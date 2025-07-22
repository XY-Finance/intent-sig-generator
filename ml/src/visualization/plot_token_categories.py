import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns


def plot_token_categories(hierarchical_metrics, base_path, qualitative_cmap, logger):
    """Plot token categories metrics per cluster and save the plot with a heatmap of percentage values."""
    token_categories_data = {}
    for cluster, metrics in hierarchical_metrics.items():
        token_categories_data[cluster] = {
            token_category: float(metrics["token_categories"][token_category]["mean"])
            for token_category in metrics["token_categories"]
        }

    clusters = list(token_categories_data.keys())
    token_categories = list(token_categories_data[clusters[0]].keys())
    data = np.array(
        [
            [
                float(token_categories_data[cluster][token_category])
                for token_category in token_categories
            ]
            for cluster in clusters
        ]
    )

    # Normalize data to percentages
    data_percentage = data / data.sum(axis=1, keepdims=True) * 100

    _, ax = plt.subplots(2, 1, figsize=(10, 10), gridspec_kw={"height_ratios": [3, 1]})

    cmap = plt.cm.get_cmap(qualitative_cmap)
    colors = cmap.colors[: len(token_categories)]
    clusters = [int(v) for v in clusters]
    bottom_values = np.zeros(len(clusters))
    for i, token_category in enumerate(token_categories):
        ax[0].bar(
            clusters,
            data[:, i],
            bottom=bottom_values,
            label=token_category,
            color=colors[i],
        )
        bottom_values += data[:, i]

    ax[0].set_ylabel("Mean Interaction")
    ax[0].set_xlabel("Cluster")
    ax[0].set_title("Stacked Bar Plot of Token Categories by Cluster")
    ax[0].legend(title="Token Categories")

    # Create the heatmap
    sns.heatmap(
        data_percentage.T,
        ax=ax[1],
        cmap="YlGnBu",
        annot=True,
        fmt=".1f",
        xticklabels=clusters,
        yticklabels=token_categories,
    )
    ax[1].set_title("Heatmap of Token Categories by Cluster (Percentage)")
    ax[1].set_xlabel("Cluster")
    ax[1].set_ylabel("Token Category")

    plt.tight_layout()

    try:
        plt.savefig(f"{base_path}/token_categories_plot.png")
        logger.info(" - token categories plot saved.")
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"Directory {base_path} does not exist.") from exc
