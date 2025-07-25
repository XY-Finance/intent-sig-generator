import json
import logging
import os
import random
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List

import pandas as pd
import requests
from tqdm import tqdm

from ml.config.collect_raw_data_config import COLLECT_RAW_DATA_DEFAULT_CONFIG
from ml.config.endpoints import ENDPOINTS
from ml.config.protocols import PROTOCOLS
from ml.config.tokens import DEFAULT_TOKENS, TOKENS
from ml.config.training_configs import COLLECT_RAW_DATA_CONFIG

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def fetch_senders(contract_address: str, chain_id: str, max_pages: int = 10):
    local_senders = set()
    page = 1
    api_key = ENDPOINTS[chain_id]["api_key"]
    base_url = ENDPOINTS[chain_id]["api_url"]
    key_method = PROTOCOLS[chain_id][contract_address].get("key_method")
    while page <= max_pages:
        params = {
            "chainid": chain_id,
            "module": "account",
            "action": "txlist",
            "address": contract_address,
            "startblock": 0,
            "endblock": 99999999,
            "page": page,
            "offset": 100,
            "sort": "desc",
            "apikey": api_key,
        }
        try:
            resp = requests.get(base_url, params=params).json()
            if resp["status"] != "1" or not resp["result"]:
                break
            txs = resp["result"]
            for tx in txs:
                if tx.get("methodId") == key_method:
                    local_senders.add(tx["from"].lower())
            page += 1
            time.sleep(0.1)
        except requests.exceptions.RequestException as e:
            logging.error(
                f"API request failed on page {page} for contract {contract_address}: {e}"
            )
            break
    return local_senders


def get_contract_sender_list(
    protocol_type: str,
    chain_id: str,
    max_pages: int = 10,
    use_cache: bool = False,
    max_workers: int = 3,
) -> List[str]:
    """
    Fetches a list of unique senders who interacted with all contracts of a given type.
    """
    cache_path = f"ml/data/raw/cache/senders_{protocol_type}_{chain_id}.json"
    os.makedirs(os.path.dirname(cache_path), exist_ok=True)
    if use_cache and os.path.exists(cache_path):
        with open(cache_path, "r") as f:
            sender_list = json.load(f)
        logging.info(f"Loaded sender_list from cache: {cache_path}")

        return sender_list

    sender_list = set()
    target_contracts = [
        addr
        for addr, data in PROTOCOLS[chain_id].items()
        if data.get("type") == protocol_type
    ]
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(fetch_senders, contract, chain_id, max_pages): contract
            for contract in target_contracts
        }
        for future in tqdm(
            as_completed(futures),
            total=len(target_contracts),
            desc="Fetching senders for contracts",
        ):
            contract = futures[future]
            try:
                result = future.result()
                sender_list.update(result)
            except Exception as e:
                logging.error(f"Error fetching senders for contract {contract}: {e}")

    sender_list = list(sender_list)
    with open(cache_path, "w") as f:
        json.dump(sender_list, f)
    logging.info(f"Saved sender_list to cache: {cache_path}")

    return sender_list


def get_eoa_transactions(
    eoa_address: str, chain_id: int, max_pages: int = 10
) -> List[Dict[str, Any]]:
    """
    Fetches up to (max_pages * 100) most recent transactions for a given EOA address.
    """
    api_key = ENDPOINTS[chain_id]["api_key"]
    base_url = ENDPOINTS[chain_id]["api_url"]
    all_results = []
    for page in range(1, max_pages + 1):
        params = {
            "chainid": chain_id,
            "module": "account",
            "action": "txlist",
            "address": eoa_address,
            "startblock": 0,
            "endblock": 99999999,
            "page": page,
            "offset": 100,
            "sort": "desc",
            "apikey": api_key,
        }
        try:
            resp = requests.get(base_url, params=params).json()
            if resp["status"] == "1" and resp.get("result"):
                for tx in resp["result"]:
                    tx["address"] = eoa_address
                    tx["chain_id"] = chain_id
                all_results.extend(resp["result"])
                if len(resp["result"]) < 100:
                    break
            else:
                logging.warning(
                    f"Could not fetch txs for {eoa_address} page {page}: {resp.get('message', 'No message')}, {resp.get('result', 'No result')}"
                )
                break
        except requests.exceptions.RequestException as e:
            logging.error(
                f"API request failed for get_eoa_transactions {eoa_address} page {page}: {e}"
            )
            break
    return all_results


def fetch_transactions_concurrently(
    sender_list: List[str],
    chain_id: int,
    use_cache: bool = False,
    max_workers: int = 3,
    eoa_max_pages: int = 2,
) -> List[Dict[str, Any]]:
    """
    Fetches transactions for a list of addresses concurrently using a thread pool.
    """
    single_chain_txs = []
    if use_cache:
        with open(f"ml/data/raw/cache/single_chain_txs_{chain_id}.json", "r") as f:
            single_chain_txs = json.load(f)
        logging.info(f"Loaded single_chain_txs_{chain_id} from cache.")

        return single_chain_txs
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_sender = {
            executor.submit(
                get_eoa_transactions, sender, chain_id, eoa_max_pages
            ): sender
            for sender in sender_list
        }

        for future in tqdm(
            as_completed(future_to_sender),
            total=len(sender_list),
            desc="Fetching transactions",
        ):
            sender = future_to_sender[future]
            try:
                txs = future.result(timeout=5)
                if txs:
                    single_chain_txs.extend(txs)
            except Exception as exc:
                logging.error(f"Sender {sender} generated an exception: {exc}")

    with open(f"ml/data/raw/cache/single_chain_txs_{chain_id}.json", "w") as f:
        json.dump(single_chain_txs, f)
    logging.info(f"Saved single_chain_txs_{chain_id} to cache.")

    return single_chain_txs


def get_token_balance(token_contract, user_address, chain_id):
    """
    Fetches the balance of a specific token for a given user address.
    """
    api_key = ENDPOINTS[chain_id]["api_key"]
    base_url = ENDPOINTS[chain_id]["api_url"]
    if token_contract == "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE":
        params = {
            "chainid": chain_id,
            "module": "account",
            "action": "balance",
            "address": user_address,
            "tag": "latest",
            "apikey": api_key,
        }
    else:
        params = {
            "chainid": chain_id,
            "module": "account",
            "action": "tokenbalance",
            "contractaddress": token_contract,
            "address": user_address,
            "tag": "latest",
            "apikey": api_key,
        }
    try:
        resp = requests.get(base_url, params=params, timeout=10).json()
        if resp.get("status") != "1":
            raise Exception(f"API error: {resp.get('message')}, {resp.get('result')}")
        return int(resp["result"])
    except Exception as e:
        logging.warning(
            f"get_token_balance failed for {user_address} on {token_contract}: {e}"
        )
        return 0


def get_balances(user_address, chain_id):
    if chain_id not in TOKENS:
        raise ValueError(f"No token config for chain ID {chain_id}")

    balances = {}
    tokens = TOKENS[chain_id]
    token_symbols = set(tokens.keys())

    for symbol, info in tokens.items():
        raw_balance = get_token_balance(info["address"], user_address, chain_id)
        price = float(info["price"])
        balance = float(raw_balance) / (10 ** int(info["decimals"]))
        balances[f"{symbol.lower()}_balance"] = round(balance, 4)
        balances[f"{symbol.lower()}_balance_usd"] = round(balance * price, 4)

    for symbol in DEFAULT_TOKENS:
        if symbol not in token_symbols:
            balances[f"{symbol.lower()}_balance"] = 0.0
            balances[f"{symbol.lower()}_balance_usd"] = 0.0

    return balances


def convert_txs_to_raw_data(
    transactions: List[Dict[str, Any]],
    chain_id: int,
    timestamp_threshold: int = 1672531200,
) -> pd.DataFrame:
    """
    Converts a list of transaction data into a pandas DataFrame,
    and saves it to a CSV file.
    """
    output_filename = f"ml/data/raw/collected_txs_{chain_id}.csv"
    if not transactions:
        logging.warning("No transactions to convert.")
        return

    logging.info(f"Converting {len(transactions)} transactions...")
    df = pd.DataFrame(transactions)

    df = df[pd.to_numeric(df["timeStamp"], errors="coerce") >= timestamp_threshold]
    logging.info(f"Filtered {len(df)} transactions...")

    numeric_cols = [
        "value",
        "gas",
        "gasPrice",
        "gasUsed",
        "cumulativeGasUsed",
        "blockNumber",
        "timeStamp",
        "nonce",
        "transactionIndex",
        "confirmations",
    ]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["timestamp_dt"] = pd.to_datetime(df["timeStamp"], unit="s")
    df["isError"] = df["isError"].astype(int)

    unique_addresses = df["address"].unique()

    logging.info(f"Fetching balances for {len(unique_addresses)} addresses...")
    address_to_balance = {}
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [
            executor.submit(get_balances, addr, chain_id) for addr in unique_addresses
        ]
        for addr, future in zip(
            unique_addresses,
            tqdm(futures, total=len(unique_addresses), desc="Fetching balances"),
        ):
            balance = future.result()
            address_to_balance[addr] = balance

    balances_df = pd.DataFrame.from_dict(address_to_balance, orient="index")
    print(balances_df.head())
    balances_df.index.name = "address"
    balances_df.reset_index(inplace=True)
    df = df.merge(balances_df, on="address", how="left")

    df.to_csv(output_filename, index=False)
    logging.info(f"All collected transactions saved to '{output_filename}'")

    return df


def merge_collected_txs(chain_ids: list) -> pd.DataFrame:
    dfs = []
    for chain_id in chain_ids:
        csv_path = f"ml/data/raw/collected_txs_{chain_id}.csv"
        if not os.path.exists(csv_path):
            logging.warning(f"{csv_path} does not exist, skipping.")
            continue
        try:
            df = pd.read_csv(csv_path)
        except pd.errors.EmptyDataError:
            logging.warning(f"{csv_path} is empty, skipping.")
            df = pd.DataFrame()
        dfs.append(df)
    if not dfs:
        logging.warning("No csv files were read, returning empty DataFrame.")
        return pd.DataFrame()
    merged_df = pd.concat(dfs, ignore_index=True)
    logging.info(f"Merged {len(dfs)} chains, {len(merged_df)} transactions in total.")
    return merged_df


def merge_event_logs(chain_ids: list) -> pd.DataFrame:
    dfs = []
    for chain_id in chain_ids:
        csv_path = f"ml/data/raw/event_logs_{str(chain_id)}.csv"
        if not os.path.exists(csv_path):
            logging.warning(f"{csv_path} does not exist, skipping.")
            continue
        try:
            df = pd.read_csv(csv_path)
        except pd.errors.EmptyDataError:
            logging.warning(f"{csv_path} is empty, skipping.")
            df = pd.DataFrame()
        dfs.append(df)
    if not dfs:
        logging.warning("No csv files were read, returning empty DataFrame.")
        return pd.DataFrame()
    merged_df = pd.concat(dfs, ignore_index=True)
    logging.info(f"Merged {len(dfs)} chains, {len(merged_df)} event logs in total.")
    return merged_df


def get_transfer_event_logs_from(
    chain_id: int, contract_address: str, target_address: str, max_pages: int = 10
) -> List[Dict[str, Any]]:
    logs = get_transfer_event_logs(
        chain_id,
        contract_address,
        target_address,
        topic1=True,
        topic2=False,
        max_pages=max_pages,
    )
    results = []
    for log in logs:
        amount = parse_amount(log["data"])
        results.append(
            {
                "address": target_address,
                "chain_id": chain_id,
                "contract": contract_address,
                "from": bytes32_to_address(log.get("topics")[1]),
                "to": bytes32_to_address(log.get("topics")[2]),
                "amount": -amount,  # from address, amount is negative
                "tx_hash": log.get("transactionHash"),
                "block_number": log.get("blockNumber"),
                "timestamp": hex_to_decimal(log.get("timeStamp")),
            }
        )
    return results


def get_transfer_event_logs_to(
    chain_id: int, contract_address: str, target_address: str, max_pages: int = 10
) -> List[Dict[str, Any]]:
    logs = get_transfer_event_logs(
        chain_id,
        contract_address,
        target_address,
        topic1=False,
        topic2=True,
        max_pages=max_pages,
    )
    results = []
    for log in logs:
        amount = parse_amount(log["data"])
        results.append(
            {
                "address": target_address,
                "chain_id": chain_id,
                "contract": contract_address,
                "from": bytes32_to_address(log.get("topics")[1]),
                "to": bytes32_to_address(log.get("topics")[2]),
                "amount": amount,
                "tx_hash": log.get("transactionHash"),
                "block_number": log.get("blockNumber"),
                "timestamp": hex_to_decimal(log.get("timeStamp")),
            }
        )
    return results


def get_transfer_event_logs(
    chain_id: int,
    contract_address: str,
    target_address: str,
    topic1: bool = False,
    topic2: bool = False,
    max_pages: int = 10,
) -> List[Dict[str, Any]]:
    transactions = []
    page = 0
    api_key = ENDPOINTS[chain_id]["api_key"]
    base_url = ENDPOINTS[chain_id]["api_url"]
    while page <= max_pages:
        if topic1:
            params = {
                "chainid": chain_id,
                "module": "logs",
                "action": "getLogs",
                "fromBlock": 0,
                "toBlock": 99999999,
                "address": contract_address,
                "topic0": "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef",
                "topic0_1_opr": "and",
                "topic1": address_to_bytes32(target_address),
                "page": page,
                "offset": 1000,
                "apikey": api_key,
            }
        elif topic2:
            params = {
                "chainid": chain_id,
                "module": "logs",
                "action": "getLogs",
                "fromBlock": 0,
                "toBlock": 99999999,
                "address": contract_address,
                "topic0": "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef",
                "topic0_2_opr": "and",
                "topic2": address_to_bytes32(target_address),
                "page": page,
                "offset": 1000,
                "apikey": api_key,
            }
        else:
            raise ValueError("Invalid topic")
        try:
            page += 1
            resp = requests.get(base_url, params=params).json()
            if resp.get("status") != "1":
                if resp.get("message") == "No records found":
                    break
                raise Exception(
                    f"API error: {resp.get('message')}, {resp.get('result')}"
                )
            transactions.extend(resp.get("result"))
            time.sleep(0.1)
        except Exception as e:
            logging.error(
                f"EOA {target_address} transfer logs not found on page {page}: {e}"
            )
            break
    return transactions


def get_decimals(row):
    chain_id = row["chain_id"]
    contract = row["contract"].lower()
    for _, info in TOKENS.get(chain_id, {}).items():
        if info["address"].lower() == contract:
            return info["decimals"]
    return None


def get_price(row):
    chain_id = row["chain_id"]
    contract = row["contract"].lower()
    for _, info in TOKENS.get(chain_id, {}).items():
        if info["address"].lower() == contract:
            return info["price"]


def get_event_logs_combined(
    chain_id: int, contract_address: str, target_address: str, max_pages: int = 10
) -> pd.DataFrame:
    from_logs = get_transfer_event_logs_from(
        chain_id, contract_address, target_address, max_pages
    )
    to_logs = get_transfer_event_logs_to(
        chain_id, contract_address, target_address, max_pages
    )
    all_logs = from_logs + to_logs
    if len(all_logs) == 0:
        logging.warning(
            f"No transfer logs found for {target_address} on chain {chain_id}."
        )
        return pd.DataFrame()

    logging.info(
        f"Found {len(all_logs)} transfer logs for {target_address} on chain {chain_id}."
    )
    df = pd.DataFrame(all_logs)
    df["raw_amount"] = df["amount"].astype(float)
    df["decimals"] = df.apply(get_decimals, axis=1)
    df["amount"] = df.apply(
        lambda row: (
            row["raw_amount"] / (10 ** row["decimals"])
            if pd.notnull(row["decimals"])
            else None
        ),
        axis=1,
    )
    df["price"] = df.apply(get_price, axis=1)
    df["amount_usd"] = df["amount"] * df["price"]
    df["contract"] = df["contract"].str.lower()
    df["chain_id"] = df["chain_id"].astype(int)
    return df


def parse_amount(data_hex: str) -> int:
    return int(data_hex, 16)


def address_to_bytes32(address: str) -> str:
    addr_hex = address.lower().replace("0x", "")
    return "0x" + addr_hex.zfill(64)


def bytes32_to_address(bytes32_str: str) -> str:
    if bytes32_str.startswith("0x"):
        hex_str = bytes32_str[2:]
    else:
        hex_str = bytes32_str
    addr = "0x" + hex_str[-40:]
    return addr


def hex_to_decimal(hex_str: str) -> int:
    if hex_str.startswith("0x"):
        hex_str = hex_str[2:]
    return int(hex_str, 16)


def get_config_value(key):
    return COLLECT_RAW_DATA_CONFIG.get(key, COLLECT_RAW_DATA_DEFAULT_CONFIG.get(key))


if __name__ == "__main__":

    based_chain_id = get_config_value("based_chain_id")
    chain_ids = get_config_value("chain_ids")
    use_cache = get_config_value("use_cache")
    max_workers = get_config_value("max_workers")
    timestamp_threshold = get_config_value("timestamp_threshold")
    based_protocol_type = get_config_value("based_protocol_type")
    senders_max_pages = get_config_value("senders_max_pages")
    logs_max_pages = get_config_value("logs_max_pages")
    senders_count_threshold = get_config_value("senders_count_threshold")
    eoa_max_pages = get_config_value("eoa_max_pages")

    logging.info(
        f"Step 1: Fetching list of senders who interacted with the target contracts on based CHAIN_ID: {based_chain_id}..."
    )
    sender_list = get_contract_sender_list(
        based_protocol_type, based_chain_id, senders_max_pages, use_cache, max_workers
    )

    if not sender_list:
        logging.info(f"No senders found on chain {based_chain_id}.")
    else:
        if len(sender_list) > senders_count_threshold:
            sender_list = random.sample(sender_list, senders_count_threshold)
            logging.info(
                f"Randomly sampled {len(sender_list)} unique senders on CHAIN_ID: {based_chain_id}."
            )
        else:
            logging.info(
                f"Found {len(sender_list)} unique senders on CHAIN_ID: {based_chain_id}."
            )

    for chain_id in chain_ids:
        logging.info(f"Step 2: Fetching event logs on CHAIN_ID: {chain_id}...")
        event_logs_list = []
        for sender in tqdm(sender_list, desc="Fetching event logs"):
            weth_address = TOKENS[chain_id]["WETH"]["address"]
            event_logs = get_event_logs_combined(
                chain_id, weth_address, sender, logs_max_pages
            )
            event_logs_list.append(event_logs)
            wbtc_address = TOKENS[chain_id]["WBTC"]["address"]
            event_logs = get_event_logs_combined(
                chain_id, wbtc_address, sender, logs_max_pages
            )
            event_logs_list.append(event_logs)
        event_logs_df = pd.concat(event_logs_list, ignore_index=True)
        event_logs_df.to_csv(f"ml/data/raw/event_logs_{chain_id}.csv", index=False)

        logging.info(
            f"Step 3: Fetching recent transactions for each sender concurrently on CHAIN_ID: {chain_id}..."
        )
        txs_by_chain = fetch_transactions_concurrently(
            sender_list, chain_id, use_cache, max_workers, eoa_max_pages
        )

        logging.info(
            f"Step 4: Saving {len(txs_by_chain)} transactions on CHAIN_ID: {chain_id}..."
        )
        df = convert_txs_to_raw_data(txs_by_chain, chain_id, timestamp_threshold)

        logging.info(f"Workflow finished on CHAIN_ID: {chain_id}.")

    merged_txs_df = merge_collected_txs(chain_ids)
    merged_txs_df.to_csv("ml/data/raw/collected_txs_all.csv", index=False)
    logging.info(
        f"All collected transactions saved to 'ml/data/raw/collected_txs_all.csv'"
    )

    merged_event_logs_df = merge_event_logs(chain_ids)
    merged_event_logs_df.to_csv("ml/data/raw/event_logs_all.csv", index=False)
    logging.info(f"All event logs saved to 'ml/data/raw/event_logs_all.csv'")
