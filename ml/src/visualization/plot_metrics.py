import math

import matplotlib.pyplot as plt


def plot_hierarchical_metrics(
    hierarchical_metrics, category, base_path, range_color_map, logger
):
    """Plot transaction activity metrics per cluster and save the plot."""
    hierarchical_metrics_data = {}
    types = ["min", "max", "median", "mean"]

    for cluster, metrics in hierarchical_metrics.items():
        hierarchical_metrics_data[cluster] = {}
        for key in metrics.get(category, {}):
            hierarchical_metrics_data[cluster][key] = {}
            for t in types:
                try:
                    hierarchical_metrics_data[cluster][key][t] = metrics[category][key][
                        t
                    ]
                except KeyError:
                    hierarchical_metrics_data[cluster][key][t] = None

    first_cluster = next(iter(hierarchical_metrics))
    if category in hierarchical_metrics[first_cluster]:
        metrics_to_plot = list(hierarchical_metrics[first_cluster][category].keys())
    else:
        return

    n_metrics = len(metrics_to_plot)
    n_cols = math.ceil(math.sqrt(n_metrics))
    n_rows = math.ceil(n_metrics / n_cols)

    _, axes = plt.subplots(n_rows, n_cols, figsize=(6 * n_cols, 5 * n_rows))
    if n_rows * n_cols == 1:
        axes = [axes]
    else:
        axes = axes.flatten()

    for ax, metric in zip(axes, metrics_to_plot):
        for stat_type, color in range_color_map.items():
            values = [
                hierarchical_metrics_data[cluster][metric][stat_type]
                for cluster in hierarchical_metrics_data
            ]
            x_values = range(len(values))

            if stat_type == "min" or stat_type == "max":
                ax.plot(
                    x_values,
                    values,
                    marker="o",
                    linestyle="-",
                    color=color,
                    label=stat_type,
                )
            else:
                ax.plot(
                    x_values,
                    values,
                    marker="o",
                    linestyle="--",
                    color=color,
                    label=stat_type,
                )

            for i, value in enumerate(values):
                if value == 0:
                    ax.plot(i, 0, marker="o", color="silver")

        ax.set_xlabel("Clusters")
        ax.set_ylabel("Value (symlog scale)")
        ax.set_yscale("symlog", linthresh=0.1)
        ax.set_xticks(x_values)
        ax.set_title(metric.replace("_", " ").title() + " per cluster")
        ax.legend(title="Metrics")
        ax.grid(True, axis="x")
        # ax.grid(True, axis='y')

    for ax in axes[n_metrics:]:
        ax.axis("off")

    plt.tight_layout()
    try:
        plt.savefig(f"{base_path}/plot_metrics_{category}.png")
        logger.info(f" - plot_metrics_{category} saved.")
    except FileNotFoundError as exc:
        raise FileNotFoundError("Error: The path does not exist") from exc
