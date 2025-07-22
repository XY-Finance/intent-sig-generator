import logging

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.feather as feather

from ml.config.features_engineering_config import FEATURES_ENGINEERING_DEFAULT_CONFIG
from ml.config.method_weights import METHOD_WEIGHTS
from ml.config.protocols import PROTOCOLS
from ml.config.tokens import TOKENS
from ml.config.training_configs import FEATURES_ENGINEERING_CONFIG

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def get_config_value(key):
    return FEATURES_ENGINEERING_CONFIG.get(
        key, FEATURES_ENGINEERING_DEFAULT_CONFIG.get(key)
    )


def parse_transaction_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["timeStamp"] = pd.to_numeric(df["timeStamp"], errors="coerce")
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df["timestamp_dt"] = pd.to_datetime(df["timeStamp"], unit="s")

    return df


def get_method_name(function_name):
    for key in METHOD_WEIGHTS:
        if key in str(function_name).lower():
            return key
    return None


def get_method_weight(function_name):
    for key, value in METHOD_WEIGHTS.items():
        if key in str(function_name).lower():
            return value
    return 0


def get_user_sent_eth(subdf):
    address = subdf.name[0]
    return (subdf.loc[subdf["from"] == address, "value"].sum() / 1e18).round(2)


def get_user_received_eth(subdf):
    address = subdf.name[0]
    return (subdf.loc[subdf["to"] == address, "value"].sum() / 1e18).round(2)


def get_max_received_eth(subdf):
    address = subdf.name[0]
    vals = subdf.loc[subdf["to"] == address, "value"]
    return (vals.max() / 1e18).round(2) if not vals.empty else 0


def get_max_sent_eth(subdf):
    address = subdf.name[0]
    vals = subdf.loc[subdf["from"] == address, "value"]
    return (vals.max() / 1e18).round(2) if not vals.empty else 0


def calc_minmax_norm(features, col, round_to=2):
    # log(x+1)
    log_col = f"{col}_log"
    features[log_col] = np.log1p(features[col])
    min_val, max_val = features[log_col].min(), features[log_col].max()
    # MinMaxScaler
    norm_col = f"{col}_norm"
    features[norm_col] = (
        ((features[log_col] - min_val) / (max_val - min_val)).round(round_to)
        if max_val != min_val
        else 0
    )
    # drop log_col
    features = features.drop(columns=[log_col], errors="ignore")
    return features


def calc_weighted_method_entropy(subdf):
    method_counts = subdf.groupby("functionName")["method_weight"].sum()
    total = method_counts.sum()
    if total == 0:
        return 0
    probs = method_counts / total
    probs = probs[probs > 0]
    entropy = -np.sum(probs * np.log(probs))
    # normalize to 0~1
    max_entropy = np.log(len(method_counts)) if len(method_counts) > 1 else 1
    return round(entropy / max_entropy, 2) if max_entropy > 0 else 0


def calc_hhi(ratios):
    return round((ratios**2).sum(), 2)


def calc_protocol_type_ratio(group, protocol_type):
    count = group["protocol_type"].apply(lambda x: (x == protocol_type).sum())
    total_count = group["protocol_type"].count()
    ratio = (count * 100 / total_count).where(total_count > 0, 0)
    return ratio.fillna(0).round(2)


def calc_protocol_focus(
    df: pd.DataFrame, unknown_type: str = "unknown", fillna_focus: float = 0
) -> pd.DataFrame:
    grouped = (
        df.groupby(["address", "protocol_type", "protocol_name"])
        .size()
        .reset_index(name="count")
    )
    total = (
        grouped.groupby(["address", "protocol_type"])["count"]
        .sum()
        .reset_index(name="total_count")
    )
    merged = pd.merge(grouped, total, on=["address", "protocol_type"])
    merged["ratio"] = merged["count"] / merged["total_count"]
    protocol_type_focus = (
        merged.groupby(["address", "protocol_type"])["ratio"]
        .apply(calc_hhi)
        .reset_index(name="protocol_type_focus")
    )
    focus_pivot = protocol_type_focus.pivot(
        index="address", columns="protocol_type", values="protocol_type_focus"
    )
    focus_pivot = focus_pivot.add_suffix("_focus").reset_index()
    focus_pivot.columns = [col.lower() for col in focus_pivot.columns]

    if f"{unknown_type}_focus" in focus_pivot.columns:
        focus_pivot = focus_pivot.drop(columns=[f"{unknown_type}_focus"])

    return focus_pivot.fillna(fillna_focus)


def calc_most_used_protocols(
    df: pd.DataFrame, unknown_type: str = "unknown", fillna_protocol: str = "unknown"
) -> pd.DataFrame:
    grouped = (
        df.groupby(["address", "protocol_type", "protocol_name"])
        .size()
        .reset_index(name="count")
    )
    df_with_counts = df.merge(
        grouped, on=["address", "protocol_type", "protocol_name"], how="left"
    )
    idx = df_with_counts.groupby(["address", "protocol_type"])["count"].idxmax()
    most_used_protocol = df_with_counts.loc[
        idx, ["address", "protocol_type", "protocol_name", "chain_id"]
    ]
    most_used_protocol["most_used_protocol_name"] = (
        most_used_protocol["protocol_name"].astype(str)
        + "_"
        + most_used_protocol["chain_id"].astype(str)
    )
    most_used_protocol = most_used_protocol[
        ["address", "protocol_type", "most_used_protocol_name"]
    ]
    merged_pivot = most_used_protocol.pivot(
        index="address", columns="protocol_type", values="most_used_protocol_name"
    )
    merged_pivot = merged_pivot.add_prefix("most_used_").reset_index()
    merged_pivot.columns = [col.lower() for col in merged_pivot.columns]

    if f"most_used_{unknown_type}" in merged_pivot.columns:
        merged_pivot = merged_pivot.drop(columns=[f"most_used_{unknown_type}"])

    return merged_pivot.fillna(fillna_protocol)


def calc_protocol_type_ratios(df: pd.DataFrame) -> pd.DataFrame:
    type_count = (
        df.groupby(["address", "protocol_type"]).size().reset_index(name="type_count")
    )
    total_type_count = (
        type_count.groupby("address")["type_count"]
        .sum()
        .reset_index(name="total_type_count")
    )
    type_count_df = pd.merge(type_count, total_type_count, on="address", how="left")
    type_count_df["protocol_type_ratio"] = (
        type_count_df["type_count"] / type_count_df["total_type_count"]
    )
    type_ratios = type_count_df.pivot(
        index="address", columns="protocol_type", values="protocol_type_ratio"
    ).fillna(0)
    type_ratios.columns = [f"{col.lower()}_ratio" for col in type_ratios.columns]
    type_ratios = type_ratios.reset_index()
    num_cols = type_ratios.select_dtypes(include="number").columns
    type_ratios[num_cols] = np.floor(type_ratios[num_cols] * 100) / 100

    return type_ratios


def add_time_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["weekday"] = df["timestamp_dt"].dt.day_name()  # eg. Monday, Tuesday
    df["hour"] = df["timestamp_dt"].dt.hour
    df["4h_interval"] = (df["hour"] // 4) * 4  # eg. 0, 4, 8, 12, 16, 20
    return df


def calc_most_active_time_features(df: pd.DataFrame) -> tuple:
    counts_1h_interval = (
        df.groupby(["address", "hour"]).size().reset_index(name="count")
    )
    idx = counts_1h_interval.groupby("address")["count"].idxmax()
    most_active_1h_interval = counts_1h_interval.loc[idx, ["address", "hour"]]
    most_active_1h_interval = most_active_1h_interval.rename(
        columns={"hour": "most_active_1h_interval"}
    )

    counts_4h_interval = (
        df.groupby(["address", "4h_interval"]).size().reset_index(name="count")
    )
    idx = counts_4h_interval.groupby("address")["count"].idxmax()
    most_active_4h_interval = counts_4h_interval.loc[idx, ["address", "4h_interval"]]
    most_active_4h_interval = most_active_4h_interval.rename(
        columns={"4h_interval": "most_active_4h_interval"}
    )

    weekday_counts = df.groupby(["address", "weekday"]).size().reset_index(name="count")
    idx = weekday_counts.groupby("address")["count"].idxmax()
    most_active_weekday = weekday_counts.loc[idx, ["address", "weekday"]]
    most_active_weekday = most_active_weekday.rename(
        columns={"weekday": "most_active_weekday"}
    )

    return most_active_1h_interval, most_active_4h_interval, most_active_weekday


def calc_most_active_chain(df: pd.DataFrame) -> pd.DataFrame:
    chain_counts = df.groupby(["address", "chain_id"]).size().reset_index(name="count")
    idx = chain_counts.groupby("address")["count"].idxmax()
    most_active_chain = chain_counts.loc[idx, ["address", "chain_id"]]
    most_active_chain = most_active_chain.rename(
        columns={"chain_id": "most_active_chain"}
    )
    return most_active_chain


def calc_protocol_type_focus(
    df: pd.DataFrame,
    unknown_type: str = "unknown",
    fillna_focus: float = 0,
    fillna_protocol: str = "unknown",
) -> pd.DataFrame:
    df_with_time = add_time_features(df)
    protocol_focus = calc_protocol_focus(df_with_time, unknown_type, fillna_focus)
    most_used_protocols = calc_most_used_protocols(
        df_with_time, unknown_type, fillna_protocol
    )
    protocol_type_ratios = calc_protocol_type_ratios(df_with_time)
    most_active_1h, most_active_4h, most_active_weekday = (
        calc_most_active_time_features(df_with_time)
    )
    most_active_chain = calc_most_active_chain(df_with_time)
    result = protocol_type_ratios.merge(protocol_focus, on="address", how="left")
    result = result.merge(most_used_protocols, on="address", how="left")
    result = result.merge(most_active_weekday, on="address", how="left")
    result = result.merge(most_active_1h, on="address", how="left")
    result = result.merge(most_active_4h, on="address", how="left")
    result = result.merge(most_active_chain, on="address", how="left")

    return result


def calc_shannon_entropy(x):
    x = x[x > 0]
    entropy = -(x * np.log2(x)).sum() if len(x) > 0 else 0
    entropy = abs(entropy)
    return round(entropy, 2)


def calc_chain_focus_and_ratios(df):
    chain_counts = df.groupby(["address", "chain_id"]).size().reset_index(name="count")
    total_counts = (
        chain_counts.groupby("address")["count"].sum().reset_index(name="total_count")
    )
    n_chains_used = (
        chain_counts.groupby("address")["chain_id"]
        .nunique()
        .reset_index(name="n_chains_used")
    )

    merged = pd.merge(chain_counts, total_counts, on="address")
    merged["chain_ratio"] = merged["count"] / merged["total_count"]
    chain_focus = (
        merged.groupby("address")["chain_ratio"]
        .apply(calc_hhi)
        .reset_index(name="chain_focus")
    )
    chain_entropy = (
        merged.groupby("address")["chain_ratio"]
        .apply(calc_shannon_entropy)
        .reset_index(name="chain_entropy")
    )

    chain_ratios = merged.pivot(
        index="address", columns="chain_id", values="chain_ratio"
    ).fillna(0)
    chain_ratios.columns = [f"chain_{col}_ratio" for col in chain_ratios.columns]
    chain_ratios = chain_ratios.reset_index()
    num_cols = chain_ratios.select_dtypes(include="number").columns
    chain_ratios[num_cols] = chain_ratios[num_cols].round(2)

    result = (
        n_chains_used.merge(chain_focus, on="address")
        .merge(chain_entropy, on="address")
        .merge(chain_ratios, on="address")
    )
    result["chain_entropy"] = result.apply(
        lambda row: (
            round(row["chain_entropy"] / np.log2(row["n_chains_used"]), 2)
            if row["n_chains_used"] > 1
            else 0
        ),
        axis=1,
    )

    return result


def abs_minmax(series):
    result = pd.Series(0, index=series.index, dtype=float)
    pos = series[series > 0]
    neg = series[series < 0]
    if not pos.empty and pos.max() != 0:
        result[pos.index] = pos / pos.max()
    if not neg.empty and neg.min() != 0:
        result[neg.index] = neg / neg.min()
    # Zero stays 0
    return result.abs()


def calc_positive_inflow_months(df, token_symbol):
    to_in = (
        df.groupby(["to", "year_month"])["amount"].sum().reset_index(name="in_amount")
    )
    from_out = (
        df.groupby(["from", "year_month"])["amount"]
        .sum()
        .reset_index(name="out_amount")
    )
    merged = pd.merge(
        to_in,
        from_out,
        left_on=["to", "year_month"],
        right_on=["from", "year_month"],
        how="outer",
    )
    merged["address"] = merged["to"].combine_first(merged["from"])
    for col in ["in_amount", "out_amount"]:
        merged[col] = merged[col].fillna(0)
        merged[col] = merged[col].astype(float)
    merged["net_inflow"] = merged["in_amount"] - merged["out_amount"]
    result = (
        merged.groupby("address")
        .apply(lambda x: (x["net_inflow"] > 0).sum(), include_groups=False)
        .reset_index(name=f"{token_symbol}_positive_inflow_months")
    )
    result[f"{token_symbol}_positive_inflow_months"] = (
        result[f"{token_symbol}_positive_inflow_months"].fillna(0).astype(int)
    )

    return result


def merge_and_save_features(
    assets_distribution_df,
    tx_behavior_df,
    columns_to_features=None,
    output_path="ml/data/processed",
):
    logging.info("Merging features...")
    features = pd.merge(
        assets_distribution_df, tx_behavior_df, on="address", how="left"
    )
    features.to_csv(f"{output_path}/raw_user_features.csv")
    logging.info(f"Raw user features saved to {output_path}/raw_user_features.csv")
    table = pa.Table.from_pandas(features)
    feather.write_feather(table, "ml/data/features/raw_user_features.arrow")
    logging.info("Raw user features saved to ml/data/features/raw_user_features.arrow")

    if columns_to_features:
        columns_to_features.append("address")
        features = features.reset_index()
        features = features[columns_to_features]
        features = features.set_index("address")
        features.to_csv(f"{output_path}/user_features.csv")
        logging.info(f"User features saved to {output_path}/user_features.csv")
        table = pa.Table.from_pandas(features)
        feather.write_feather(table, "ml/data/features/user_features.arrow")
        logging.info("User features saved to ml/data/features/user_features.arrow")


def get_token_contracts(token_symbol, tokens_config):
    return {
        chain_id: token_info[token_symbol]["address"]
        for chain_id, token_info in tokens_config.items()
        if token_symbol in token_info
    }


def filter_token_df(df, token_symbol, tokens_config):
    df = df.copy()
    contracts = get_token_contracts(token_symbol, tokens_config)
    df["contract"] = df["contract"].str.lower()
    df["chain_id"] = df["chain_id"].astype(int)
    df["chain_contract"] = list(zip(df["chain_id"], df["contract"]))
    contract_set = set((int(cid), addr.lower()) for cid, addr in contracts.items())
    return df[df["chain_contract"].isin(contract_set)].copy()


def preprocess_assets_distribution(
    df: pd.DataFrame,
    event_logs_df: pd.DataFrame,
    lookback_months: int = 12,
    whale_score_settings: dict = None,
) -> pd.DataFrame:
    group = df.groupby(["address", "chain_id"])
    features_address = pd.DataFrame()  # features_address: index=['address']
    features_chain = pd.DataFrame()  # features_chain: index=['address', 'chain_id']
    balance_usd_columns = [col for col in df.columns if col.endswith("balance_usd")]

    for col in balance_usd_columns:
        features_chain[col] = group[col].mean()
        features_address[col] = features_chain.groupby("address")[col].sum()

    user_sent = group.apply(get_user_sent_eth, include_groups=False).rename(
        "user_sent_eth"
    )
    user_received = group.apply(get_user_received_eth, include_groups=False).rename(
        "user_received_eth"
    )
    max_sent = group.apply(get_max_sent_eth, include_groups=False).rename(
        "max_sent_eth"
    )
    max_received = group.apply(get_max_received_eth, include_groups=False).rename(
        "max_received_eth"
    )

    eth_features = pd.concat(
        [user_received, user_sent, max_received, max_sent], axis=1
    ).fillna(0)
    eth_features["user_net_flow_eth"] = (
        eth_features["user_received_eth"] - eth_features["user_sent_eth"]
    ).round(2)
    eth_features["user_net_flow_eth_log"] = eth_features["user_net_flow_eth"].apply(
        lambda x: np.sign(x) * np.log1p(abs(x)) if abs(x) >= 1 else 0
    )
    eth_features["user_net_flow_eth_log_abs_norm"] = abs_minmax(
        eth_features["user_net_flow_eth_log"]
    ).round(2)

    eth_features_address = (
        eth_features.groupby("address")
        .agg(
            {
                "user_received_eth": "sum",
                "user_sent_eth": "sum",
                "max_received_eth": "max",
                "max_sent_eth": "max",
                "user_net_flow_eth_log_abs_norm": "max",
            }
        )
        .round(2)
    )

    features_address = features_address.merge(
        eth_features_address, left_index=True, right_index=True, how="left"
    )

    balance_norm_columns = []
    for col in balance_usd_columns:
        norm_col = f"{col}_norm"
        features_address[norm_col] = (
            features_address[col] - features_address[col].min()
        ) / (features_address[col].max() - features_address[col].min())
        features_address[norm_col] = features_address[norm_col].fillna(0).round(2)
        balance_norm_columns.append(norm_col)

    eth_norm_columns = []
    for col in [
        "user_received_eth",
        "user_sent_eth",
        "max_received_eth",
        "max_sent_eth",
    ]:
        norm_col = f"{col}_norm"
        features_address[norm_col] = (
            features_address[col] - features_address[col].min()
        ) / (features_address[col].max() - features_address[col].min())
        features_address[norm_col] = features_address[norm_col].fillna(0).round(2)
        eth_norm_columns.append(norm_col)

    features_address["whale_score"] = sum(
        whale_score_settings.get(col, 0) * features_address.get(col, 0)
        for col in whale_score_settings
    )
    features_address["whale_score"] = (features_address["whale_score"] * 100).round(2)
    features_chain["has_1000usd"] = (
        features_chain[balance_usd_columns].sum(axis=1) > 1000
    )
    features_address["n_chains_with_asset"] = features_chain.groupby("address")[
        "has_1000usd"
    ].sum()
    features_address["total_assets_usd"] = features_address[
        [
            "usdc_balance_usd",
            "usdt_balance_usd",
            "weth_balance_usd",
            "wbtc_balance_usd",
            "eth_balance_usd",
            "dai_balance_usd",
            "shib_balance_usd",
            "pepe_balance_usd",
        ]
    ].sum(axis=1)
    features_address["usdc_balance_ratio"] = round(
        features_address["usdc_balance_usd"] / features_address["total_assets_usd"], 2
    )
    features_address["usdt_balance_ratio"] = round(
        features_address["usdt_balance_usd"] / features_address["total_assets_usd"], 2
    )
    features_address["weth_balance_ratio"] = round(
        features_address["weth_balance_usd"] / features_address["total_assets_usd"], 2
    )
    features_address["wbtc_balance_ratio"] = round(
        features_address["wbtc_balance_usd"] / features_address["total_assets_usd"], 2
    )
    features_address["eth_balance_ratio"] = round(
        features_address["eth_balance_usd"] / features_address["total_assets_usd"], 2
    )
    features_address["dai_balance_ratio"] = round(
        features_address["dai_balance_usd"] / features_address["total_assets_usd"], 2
    )
    features_address["stable_token_ratio"] = round(
        (
            features_address["usdc_balance_usd"]
            + features_address["usdt_balance_usd"]
            + features_address["dai_balance_usd"]
        )
        / features_address["total_assets_usd"],
        2,
    )
    features_address["meme_token_ratio"] = round(
        (features_address["shib_balance_usd"] + features_address["pepe_balance_usd"])
        / features_address["total_assets_usd"],
        2,
    )
    features_address["erc20_token_ratio"] = round(
        (features_address["weth_balance_usd"] + features_address["wbtc_balance_usd"])
        / features_address["total_assets_usd"],
        2,
    )
    features_address["native_token_ratio"] = round(
        features_address["eth_balance_usd"] / features_address["total_assets_usd"], 2
    )

    # at least 1 tx in the last 30 days
    timestamp_threshold = pd.Timestamp.now() - pd.Timedelta(days=30)
    tx_count_threshold = 1
    df_recent = df[df["timestamp_dt"] > timestamp_threshold]
    group_tx_counts = (
        df_recent.groupby(["address", "chain_id"]).size().reset_index(name="tx_count")
    )
    group_tx_counts["is_active"] = group_tx_counts["tx_count"] > tx_count_threshold
    features_chain = features_chain.merge(
        group_tx_counts[["address", "chain_id", "is_active"]],
        on=["address", "chain_id"],
        how="left",
    )
    features_chain["is_active"] = (
        features_chain["is_active"].fillna(False).infer_objects(copy=False)
    )
    features_address["n_chains_with_activity"] = features_chain.groupby("address")[
        "is_active"
    ].sum()

    event_logs_df = event_logs_df.copy()
    event_logs_df["timestamp_dt"] = pd.to_datetime(event_logs_df["timestamp"], unit="s")
    cutoff = pd.Timestamp.now() - pd.DateOffset(months=lookback_months)
    event_logs_df = event_logs_df[event_logs_df["timestamp_dt"] >= cutoff]
    event_logs_df["year_month"] = event_logs_df["timestamp_dt"].dt.to_period("M")

    for token in ["WBTC", "WETH"]:
        token_df = filter_token_df(event_logs_df, token, TOKENS)
        positive_inflow = calc_positive_inflow_months(token_df, token.lower())
        features_address = features_address.merge(
            positive_inflow, on="address", how="left"
        )
        col = f"{token.lower()}_positive_inflow_months"
        features_address[col] = features_address[col].fillna(0).astype(int)

    features_address.to_csv("ml/data/processed/assets_distribution.csv")

    return features_address


def calc_avg_tx_usd_value(group, flow_type="inflow"):
    address = group.name[0]
    chain_id = group.name[1]
    if flow_type == "inflow":
        filtered_txs = group[group["to"] == address]
    elif flow_type == "outflow":
        filtered_txs = group[group["from"] == address]
    else:
        raise ValueError("flow_type only allows 'inflow' or 'outflow'")
    if len(filtered_txs) == 0:
        return 0

    total_usd_value = 0
    for _, tx in filtered_txs.iterrows():
        eth_price = TOKENS.get(chain_id, {}).get("ETH", {}).get("price", 0)
        if eth_price > 0:
            eth_value = tx["value"] / 1e18
            usd_value = eth_value * eth_price
            total_usd_value += usd_value

    avg_usd_value = total_usd_value / len(filtered_txs)
    return round(avg_usd_value, 2)


def calc_total_tx_usd_value(group, flow_type="inflow"):
    address = group.name[0]
    chain_id = group.name[1]
    if flow_type == "inflow":
        filtered_txs = group[group["to"] == address]
    elif flow_type == "outflow":
        filtered_txs = group[group["from"] == address]
    else:
        raise ValueError("flow_type only allows 'inflow' or 'outflow'")

    if len(filtered_txs) == 0:
        return 0

    total_usd_value = 0
    for _, tx in filtered_txs.iterrows():
        eth_price = TOKENS.get(chain_id, {}).get("ETH", {}).get("price", 0)
        if eth_price > 0:
            eth_value = tx["value"] / 1e18
            usd_value = eth_value * eth_price
            total_usd_value += usd_value

    return round(total_usd_value, 2)


def calc_tx_timing_features(group):
    min_time = group["timestamp_dt"].min()
    max_time = group["timestamp_dt"].max()
    lifetime_days = (max_time - min_time).days + 1
    if lifetime_days <= 0:
        return pd.Series(
            {
                "first_timestamp_dt": min_time,
                "last_timestamp_dt": max_time,
                "lifetime_days": 0,
                "txs_per_day": 0,
                "txs_per_week": 0,
                "txs_per_month": 0,
            }
        )
    tx_count = len(group)
    min_week_days = max(lifetime_days, 7)
    min_month_days = max(lifetime_days, 30)
    return pd.Series(
        {
            "first_timestamp_dt": min_time,
            "last_timestamp_dt": max_time,
            "lifetime_days": lifetime_days,
            "txs_per_day": round(tx_count / lifetime_days, 2),
            "txs_per_week": round(tx_count / (min_week_days / 7), 2),
            "txs_per_month": round(tx_count / (min_month_days / 30), 2),
        }
    )


def preprocess_tx_behavior(
    df: pd.DataFrame,
    active_days_threshold: int = 730,
    active_score_settings: dict = None,
) -> pd.DataFrame:
    pd.set_option("display.max_rows", None)
    pd.set_option("display.max_columns", None)

    features_address = pd.DataFrame()  # features_address: index=['address']
    features_chain = pd.DataFrame()  # features_chain: index=['address', 'chain_id']
    flat_name_map = {
        (chain_id, address): meta["name"]
        for chain_id, addr_map in PROTOCOLS.items()
        for address, meta in addr_map.items()
    }
    flat_type_map = {
        (chain_id, address): meta["type"]
        for chain_id, addr_map in PROTOCOLS.items()
        for address, meta in addr_map.items()
    }
    keys = list(zip(df["chain_id"], df["to"]))

    df["protocol_name"] = list(map(lambda k: flat_name_map.get(k, "Unknown"), keys))
    df["protocol_type"] = list(map(lambda k: flat_type_map.get(k, "Unknown"), keys))
    df["method_weight"] = df["functionName"].apply(get_method_weight)
    df["method_name"] = df["functionName"].apply(get_method_name)
    df["n_methods"] = df["functionName"].nunique()

    group = df.groupby(["address", "chain_id"])
    features_chain["n_protocol_names"] = group["protocol_name"].nunique()
    features_chain["n_protocol_types"] = group["protocol_type"].nunique()
    features_chain["n_methods"] = group["n_methods"].nunique()
    features_chain["tx_count"] = group["hash"].nunique()
    features_chain["method_diversity"] = group.apply(
        calc_weighted_method_entropy, include_groups=False
    )
    features_chain["avg_tx_usd_value_inflow"] = group.apply(
        calc_avg_tx_usd_value, flow_type="inflow", include_groups=False
    )
    features_chain["avg_tx_usd_value_outflow"] = group.apply(
        calc_avg_tx_usd_value, flow_type="outflow", include_groups=False
    )
    features_chain["total_tx_usd_value_inflow"] = group.apply(
        calc_total_tx_usd_value, flow_type="inflow", include_groups=False
    )
    features_chain["total_tx_usd_value_outflow"] = group.apply(
        calc_total_tx_usd_value, flow_type="outflow", include_groups=False
    )
    features_address["total_protocol_count"] = features_chain.groupby("address")[
        "n_protocol_names"
    ].sum()
    features_address["total_protocol_type"] = features_chain.groupby("address")[
        "n_protocol_types"
    ].sum()
    features_address["total_methods"] = features_chain.groupby("address")[
        "n_methods"
    ].sum()
    features_address["total_tx_count"] = features_chain.groupby("address")[
        "tx_count"
    ].sum()
    features_address["method_diversity"] = features_chain.groupby("address")[
        "method_diversity"
    ].max()
    features_address["avg_tx_usd_value_inflow"] = (
        features_chain.groupby("address")["avg_tx_usd_value_inflow"].mean().round(2)
    )
    features_address["avg_tx_usd_value_outflow"] = (
        features_chain.groupby("address")["avg_tx_usd_value_outflow"].mean().round(2)
    )
    features_address["total_tx_usd_value_inflow"] = (
        features_chain.groupby("address")["total_tx_usd_value_inflow"].sum().round(2)
    )
    features_address["total_tx_usd_value_outflow"] = (
        features_chain.groupby("address")["total_tx_usd_value_outflow"].sum().round(2)
    )

    active_days_dt = pd.Timestamp.now() - pd.Timedelta(days=active_days_threshold)
    df_recent = df[df["timestamp_dt"] >= active_days_dt].copy()
    df_recent["date"] = df_recent["timestamp_dt"].dt.date
    active_days = (
        df_recent.groupby("address")["date"].nunique().reset_index(name="active_days")
    )
    features_address = features_address.merge(active_days, on="address", how="left")
    features_address["active_days"] = (
        features_address["active_days"].fillna(0).astype(int)
    )
    features_address["active_days_ratio"] = round(
        features_address["active_days"] / active_days_threshold, 2
    )
    features_address["tx_avg_burst"] = features_address.apply(
        lambda row: (
            round(row["total_tx_count"] / row["active_days"], 2)
            if row["active_days"] > 0
            else 0
        ),
        axis=1,
    )

    protocol_focus_df = calc_protocol_type_focus(df)
    features_address = features_address.merge(
        protocol_focus_df, on="address", how="left"
    )
    chain_focus_df = calc_chain_focus_and_ratios(df)
    features_address = features_address.merge(chain_focus_df, on="address", how="left")
    tx_timing = (
        df.groupby("address")
        .apply(calc_tx_timing_features, include_groups=False)
        .reset_index()
    )
    features_address = features_address.merge(tx_timing, on="address", how="left")

    features_address["first_timestamp_dt"] = pd.to_datetime(
        features_address["first_timestamp_dt"]
    )
    features_address["last_timestamp_dt"] = pd.to_datetime(
        features_address["last_timestamp_dt"]
    )

    for col in [
        "total_protocol_count",
        "total_protocol_type",
        "total_methods",
        "total_tx_count",
        "txs_per_week",
    ]:
        features_address = calc_minmax_norm(features_address, col)

    features_address["active_score"] = sum(
        active_score_settings.get(col, 0) * features_address.get(col, 0)
        for col in active_score_settings
    )
    features_address["active_score"] = (features_address["active_score"] * 100).round(2)
    features_address.to_csv("ml/data/processed/tx_behavior.csv")

    return features_address


if __name__ == "__main__":
    logging.info("Loading raw transaction data...")
    df = pd.read_csv("ml/data/raw/collected_txs_all.csv", low_memory=False)
    event_logs_df = pd.read_csv("ml/data/raw/event_logs_all.csv", low_memory=False)

    logging.info("Loading features engineering config...")
    columns_to_features = get_config_value("features")
    active_days_threshold = get_config_value("active_days_threshold")
    assets_lookback_months = get_config_value("assets_lookback_months")
    whale_score_settings = get_config_value("whale_score_settings")
    active_score_settings = get_config_value("active_score_settings")

    logging.info("Preprocessing transaction data...")
    df = parse_transaction_columns(df)

    logging.info("Preprocessing assets distribution...")
    assets_distribution_df = preprocess_assets_distribution(
        df, event_logs_df, assets_lookback_months, whale_score_settings
    )

    logging.info("Preprocessing tx behavior...")
    tx_behavior_df = preprocess_tx_behavior(
        df, active_days_threshold, active_score_settings
    )

    logging.info("Merging and saving features...")
    merge_and_save_features(assets_distribution_df, tx_behavior_df, columns_to_features)
