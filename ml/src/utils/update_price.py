import pprint

import requests

from ml.config.tokens import TOKENS


def update_token_prices():
    for chain_id, chain_tokens in TOKENS.items():
        for symbol, info in chain_tokens.items():
            addr = (
                info["address"]
                if info["address"] == "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"
                else info["address"].lower()
            )
            url = f"https://prod-price-server-z5c7fs3wka-de.a.run.app/tokens/{chain_id}"
            params = {"addresses": addr}
            resp = requests.get(url, params=params).json()
            print(f"chain_id: {chain_id} symbol: {symbol} price: {resp[addr]}")
            TOKENS[chain_id][symbol]["price"] = float(resp[addr])
    save_tokens_to_py(TOKENS)


def save_tokens_to_py(tokens, path="ml/config/tokens.py"):
    with open(path, "w") as f:
        f.write("TOKENS = ")
        pprint.pprint(tokens, stream=f, indent=4, width=40, sort_dicts=False)
        f.write(
            '\n\nDEFAULT_TOKENS = [\n    "USDC",\n    "USDT",\n    "WETH",\n    "WBTC",\n    "DAI",\n    "ETH",\n]\n'
        )
    print(f"Successfully updated token prices to {path}")


if __name__ == "__main__":
    update_token_prices()
