FEATURES_ENGINEERING_DEFAULT_CONFIG = {
    "features": [  # required
        "whale_score",
        "active_score",
        "lending_ratio",
        "lending_focus",
    ],
    "active_days_threshold": 730,  # optional
    "assets_lookback_months": 12,  # optional
    "whale_score_settings": {  # optional
        "user_net_flow_eth_log_abs_norm": 0.10,
        "user_received_eth_norm": 0.05,
        "user_sent_eth_norm": 0.05,
        "max_received_eth_norm": 0.05,
        "max_sent_eth_norm": 0.05,
        "usdc_balance_usd_norm": 0.10,
        "usdt_balance_usd_norm": 0.10,
        "weth_balance_usd_norm": 0.10,
        "wbtc_balance_usd_norm": 0.10,
        "eth_balance_usd_norm": 0.10,
        "dai_balance_usd_norm": 0.10,
        "shib_balance_usd_norm": 0.05,
        "pepe_balance_usd_norm": 0.05,
    },
    "active_score_settings": {  # optional
        "method_diversity": 0.20,
        "total_protocol_count_norm": 0.10,
        "total_protocol_type_norm": 0.10,
        "total_tx_count_norm": 0.20,
        "txs_per_week_norm": 0.20,
        "active_days_ratio": 0.20,
    },
}
