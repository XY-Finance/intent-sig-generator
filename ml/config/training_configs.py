COLLECT_RAW_DATA_CONFIG = {
    "based_chain_id": 1,  # required
    "chain_ids": [1, 42161, 8453],  # required
    "timestamp_threshold": 1672531200,  # required, default: 2023-01-01
    "based_protocol_type": "Lending",  # required, default: Lending
    "senders_count_threshold": 30,  # required, min:10
    "senders_max_pages": 5,  # required, min:1
    "logs_max_pages": 2,  # required, min:1
    "max_workers": 3,  # optional, min:1
    "use_cache": False,  # optional
}

FEATURES_ENGINEERING_CONFIG = {
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

KMEANS_PIPELINE_CONFIG = {
    "n_components": 0.95,  # required
    "analyse": True,  # required
    "reduce_dimensions": False,  # required
    "optimization": False,  # required, and False only
}
