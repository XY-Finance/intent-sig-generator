import json

from ml.src.utils.logger import get_logger_with_timestamp

from .plot_clustering_rate import plot_cluster_metrics
from .plot_interaction_types import plot_interaction_types
from .plot_metrics import plot_hierarchical_metrics
from .plot_token_categories import plot_token_categories


def analyze_clusters(timestamp):
    """Main function to plot all the clusters metrics and analysis"""
    logger = get_logger_with_timestamp(timestamp, "plotter")
    logger.info("Plotting clusters metrics")

    with open(
        f"ml/src/results/{timestamp}/kmeans_evaluation/kmeans_clusters_metrics.json",
        "r",
        encoding="utf-8",
    ) as file:
        metrics = json.load(file)
    with open(
        f"ml/src/results/{timestamp}/kmeans_evaluation/kmeans_clusters_raw_statistics.json",
        "r",
        encoding="utf-8",
    ) as file:
        raw_statistics = json.load(file)
    base_path = f"ml/src/results/{timestamp}/kmeans_evaluation"

    qualitative_cmap = "Pastel1"
    range_color_map = {
        "min": "red",
        "max": "green",
        "median": "navy",
        "mean": "lightseagreen",
    }

    for category in ["activity", "whale", "others"]:
        plot_hierarchical_metrics(metrics, category, base_path, range_color_map, logger)

    plot_cluster_metrics(metrics, base_path, qualitative_cmap, logger)
    plot_interaction_types(raw_statistics, base_path, qualitative_cmap, logger)
    plot_token_categories(raw_statistics, base_path, qualitative_cmap, logger)
