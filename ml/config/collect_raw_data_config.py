COLLECT_RAW_DATA_DEFAULT_CONFIG = {
    "based_chain_id": 1,  # required
    "chain_ids": [1, 42161, 8453],  # required
    "timestamp_threshold": 1672531200,  # required, default: 2023-01-01
    "based_protocol_type": "Lending",  # required, default: Lending
    "senders_count_threshold": 30,  # required
    "senders_max_pages": 1,  # required
    "logs_max_pages": 2,  # required
    "max_workers": 3,  # required
    "use_cache": False,  # required
    "eoa_max_pages": 2,  # required
}
