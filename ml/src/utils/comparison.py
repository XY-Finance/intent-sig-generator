import json

import pandas as pd
from pyarrow import feather

from ml.src.utils.logger import get_logger_with_timestamp

BASE_PATH = "ml/data/models/kmeans"


def load_predictions(features_path, predictions_path):
    """Load the predictions and features dataframes and merge them"""
    users = feather.read_table(features_path).to_pandas()
    result = feather.read_table(predictions_path).to_pandas()
    df = pd.merge(users, result, on="address", how="left")

    return df


def categorize_columns(df):
    categories = {"whale": [], "activity": [], "others": []}
    exclude_cols = ["address", "cluster"]
    for col in df.columns:
        if col in exclude_cols:
            continue
        if "whale" in col or "balance" in col or "net_flow" in col:
            categories["whale"].append(col)
        elif (
            "active" in col
            or "tx_count" in col
            or "freq" in col
            or "lifetime" in col
            or "diversity" in col
        ):
            categories["activity"].append(col)
        else:
            categories["others"].append(col)
    categories = {k: v for k, v in categories.items() if v}
    return categories


def aggregate_metrics(df, timestamp, logger):
    """Aggregate metrics for each cluster per category"""
    categories = {"whale": [], "activity": [], "others": []}
    exclude_cols = ["address", "cluster"]
    for col in df.columns:
        if col in exclude_cols:
            continue
        if "whale" in col or "balance" in col or "net_flow" in col:
            categories["whale"].append(col)
        elif (
            "active" in col
            or "tx_count" in col
            or "freq" in col
            or "lifetime" in col
            or "diversity" in col
        ):
            categories["activity"].append(col)
        else:
            categories["others"].append(col)
    categories = {k: v for k, v in categories.items() if v}
    total_addresses = df["address"].nunique()
    address_counts = df.groupby("cluster")["address"].nunique()
    exclude_cols = ["address", "cluster"]
    agg_cols = [col for col in sum(categories.values(), []) if col not in exclude_cols]
    metrics_by_cluster = df.groupby("cluster")[agg_cols].agg(
        ["mean", "median", "std", "var", "max", "min"]
    )

    metrics = {
        cluster: {
            "address": int(count),
            "repartition_rate": float(count / total_addresses),
            **{
                category: {
                    col: {
                        "mean": float(metrics_by_cluster.loc[cluster, (col, "mean")]),
                        "max": float(metrics_by_cluster.loc[cluster, (col, "max")]),
                        "min": float(metrics_by_cluster.loc[cluster, (col, "min")]),
                        "std": float(metrics_by_cluster.loc[cluster, (col, "std")]),
                        "var": float(metrics_by_cluster.loc[cluster, (col, "var")]),
                        "median": float(
                            metrics_by_cluster.loc[cluster, (col, "median")]
                        ),
                    }
                    for col in cols
                }
                for category, cols in categories.items()
            },
        }
        for cluster, count in address_counts.items()
    }
    metrics_json = json.dumps(metrics, indent=4)

    with open(
        f"ml/src/results/{timestamp}/kmeans_evaluation/kmeans_clusters_metrics.json",
        "w",
    ) as json_file:
        json_file.write(metrics_json)

    logger.info("Metrics saved to kmeans_evaluation/kmeans_clusters_metrics")

    return metrics


def aggregate_raw_statistics(df, timestamp, logger):
    """Aggregate raw statistics for each cluster per category"""
    categories = {
        "interaction_types": [
            "lending_ratio",
            "dex_ratio",
            "stablecoin_ratio",
            "bridge_ratio",
            "unknown_ratio",
        ],
        "token_categories": [
            "stable_token_ratio",
            "meme_token_ratio",
            "erc20_token_ratio",
            "native_token_ratio",
        ],
    }
    # exclude_cols = ['address', 'cluster']
    # for col in df.columns:
    #     if col in exclude_cols:
    #         continue
    #     if 'whale' in col or 'balance' in col or 'net_flow' in col:
    #         categories['whale'].append(col)
    #     elif 'active' in col or 'tx_count' in col or 'freq' in col or 'lifetime' in col or 'diversity' in col:
    #         categories['activity'].append(col)
    #     else:
    #         categories['others'].append(col)

    total_addresses = df["address"].nunique()
    address_counts = df.groupby("cluster")["address"].nunique()
    exclude_cols = ["address", "cluster"]
    agg_cols = [col for col in sum(categories.values(), []) if col not in exclude_cols]
    metrics_by_cluster = df.groupby("cluster")[agg_cols].agg(
        ["mean", "median", "std", "var", "max", "min"]
    )

    metrics = {
        cluster: {
            "address": int(count),
            "repartition_rate": float(count / total_addresses),
            **{
                category: {
                    col: {
                        "mean": float(metrics_by_cluster.loc[cluster, (col, "mean")]),
                        "max": float(metrics_by_cluster.loc[cluster, (col, "max")]),
                        "min": float(metrics_by_cluster.loc[cluster, (col, "min")]),
                        "std": float(metrics_by_cluster.loc[cluster, (col, "std")]),
                        "var": float(metrics_by_cluster.loc[cluster, (col, "var")]),
                        "median": float(
                            metrics_by_cluster.loc[cluster, (col, "median")]
                        ),
                    }
                    for col in cols
                }
                for category, cols in categories.items()
            },
        }
        for cluster, count in address_counts.items()
    }
    metrics_json = json.dumps(metrics, indent=4)

    with open(
        f"ml/src/results/{timestamp}/kmeans_evaluation/kmeans_clusters_raw_statistics.json",
        "w",
    ) as json_file:
        json_file.write(metrics_json)

    logger.info(
        "Raw statistics saved to kmeans_evaluation/kmeans_clusters_raw_statistics"
    )


def clusters_analysis(features_path, raw_features_path, predictions_path, timestamp):
    logger = get_logger_with_timestamp(timestamp, "comparison")
    df = load_predictions(features_path, predictions_path)
    metrics = aggregate_metrics(df, timestamp, logger)
    raw_df = load_predictions(raw_features_path, predictions_path)
    aggregate_raw_statistics(raw_df, timestamp, logger)
    # result = identify_variance(metrics)
    return metrics
