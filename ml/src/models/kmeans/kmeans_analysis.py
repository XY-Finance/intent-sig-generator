import json
import os
from datetime import datetime

import numpy as np
import optuna
import pandas as pd
from joblib import Parallel, delayed
from matplotlib import pyplot as plt
from sklearn.cluster import KMeans, MiniBatchKMeans
from sklearn.metrics import (
    calinski_harabasz_score,
    davies_bouldin_score,
    silhouette_score,
)
from sklearn.utils import resample
from tqdm import tqdm

from ml.src.utils.logger import get_logger_with_timestamp


def compute_inertia(k, x_train):
    """
    Computes the inertia (sum of squared distances to the nearest centroid) for a given number of clusters.
    :param:
        k (int): Number of clusters.
        x_train (ndarray): Training data.
    :return:
        float: Inertia value.
    """
    kmeans = MiniBatchKMeans(n_clusters=k, random_state=42, batch_size=100)
    kmeans.fit(x_train)
    return kmeans.inertia_


def compute_silhouette_score_subsampling(k, x_train, logger):
    """
    Computes the silhouette score for a given number of clusters with subsampling.
    :param:
        k (int): Number of clusters.
        x_train (ndarray): Training data.
    :return:
        float: Silhouette score (0 if insufficient clusters are found).
    """
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    kmeans.fit(x_train)

    sample_size = min(10000, x_train.shape[0])
    sample_indices = np.random.choice(x_train.shape[0], sample_size, replace=False)

    x_sample = x_train.iloc[sample_indices]
    labels_sample = kmeans.labels_[sample_indices]

    if len(np.unique(labels_sample)) < 2:
        logger.info(
            f"Warning: only {len(np.unique(labels_sample))} clusters found for k={k}"
        )
        return 0

    return silhouette_score(x_sample, labels_sample)


def compute_silhouette_score_full(k, x_train, timestamp, logger):
    """
    Computes the silhouette score for a given number of clusters using all data (no subsampling).
    :param:
        k (int): Number of clusters.
        x_train (ndarray or DataFrame): Training data.
    :return:
        float: Silhouette score (0 if insufficient clusters are found).
    """
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = kmeans.fit_predict(x_train)

    if len(np.unique(labels)) < 2:
        logger.info(
            f"Warning: only {len(np.unique(labels))} cluster(s) found for k={k}"
        )
        return 0

    auto_pca_scatter_plot(x_train, k, labels, timestamp, logger)

    return silhouette_score(x_train, labels)


def analyze_kmeans(x_train, dataset_name, timestamp):
    """
    Analyzes K-Means clustering for different values of k and visualizes the results.
    :param:
        x_train (ndarray): Training data.
        dataset_name (str): Identifier for the dataset (used in output file naming).
    :return:
        int: Optimal number of clusters based on silhouette score.
    """
    logger = get_logger_with_timestamp(timestamp, "kmeans_analysis")
    k_range = range(2, 10)

    logger.info("Dataset statistics:")
    logger.info(f"- Shape: {x_train.shape}")
    logger.info(
        f"- Unique values: {np.unique(x_train, axis=0).shape[0]} / {x_train.shape[0]}"
    )
    logger.info(f"- Feature variance: {np.var(x_train, axis=0)}")
    logger.info(f"- NaN values present: {np.any(np.isnan(x_train))}")
    logger.info(f"- Inf values present: {np.any(np.isinf(x_train))}")

    inertia = Parallel(n_jobs=-1)(
        delayed(compute_inertia)(k, x_train)
        for k in tqdm(k_range, desc="Calculating inertia")
    )

    try:
        silhouette_scores = Parallel(n_jobs=-1)(
            delayed(compute_silhouette_score_full)(k, x_train, timestamp, logger)
            for k in tqdm(k_range, desc="Calculating silhouette scores")
        )
    except (ValueError, IndexError, RuntimeError) as e:
        logger.exception(f"Error during silhouette score calculation: {e}")
        silhouette_scores = [0] * len(k_range)

    best_k = k_range[np.argmax(silhouette_scores)]

    fig, ax = plt.subplots(1, 2, figsize=(12, 5))

    ax[0].plot(k_range, inertia, marker="o")
    ax[0].set_title("Elbow Method")
    ax[0].set_xlabel("Number of clusters (k)")
    ax[0].set_ylabel("Inertia")

    ax[1].plot(k_range, silhouette_scores, marker="o")
    ax[1].set_title("Silhouette Scores")
    ax[1].set_xlabel("Number of clusters (k)")
    ax[1].set_ylabel("Silhouette Score")

    ax[1].axvline(best_k, linestyle="--", color="red", label=f"Best k = {best_k}")
    ax[1].legend()

    save_dir = os.path.join("ml/src/results/", timestamp, "kmeans_evaluation")
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, f"kmeans_{dataset_name}_scores.png")
    fig.savefig(
        save_path,
        dpi=300,
        bbox_inches="tight",
    )
    plt.show()

    return best_k


def measure_performances(data, labels):
    """Measure the performances of clustering algorithms"""

    db_index = davies_bouldin_score(data, labels)
    ch_index = calinski_harabasz_score(data, labels)

    data_sample, labels_sample = resample(
        data, labels, n_samples=10000, random_state=42
    )
    silhouette_avg = silhouette_score(data_sample, labels_sample)

    return db_index, ch_index, silhouette_avg


def objective(x, trial):
    """
    Objective function for Optuna hyperparameter optimization of MiniBatchKMeans.
    :param:
        x (ndarray): Training data.
        trial (optuna.Trial): Optuna trial instance.
    :return:
        float: performance score of the clustering result.
    """
    # Define the search space
    n_clusters = trial.suggest_int("n_clusters", 2, 10)
    init = trial.suggest_categorical("init", ["k-means++", "random"])
    batch_size = trial.suggest_int("batch_size", 50, 500, step=50)
    max_iter = trial.suggest_int("max_iter", 100, 500)
    tol = trial.suggest_float("tol", 1e-6, 1e-2, log=True)

    # Define the model with the hyperparameters
    kmeans = MiniBatchKMeans(
        n_clusters=n_clusters,
        init=init,
        batch_size=batch_size,
        max_iter=max_iter,
        tol=tol,
        random_state=42,
    )
    # Measure the performances
    labels = kmeans.fit_predict(x)
    db_index, ch_index, silhouette_avg = measure_performances(data=x, labels=labels)

    # Define the weights
    x = trial.suggest_float("silhouette_weight", 0.1, 1.0)
    y = trial.suggest_float("ch_weight", 0.1, 1.0)
    z = trial.suggest_float("db_weight", 0.1, 1.0)

    # Return the weighted sum of the performances with the trial parameters
    return (x * silhouette_avg) + (y * ch_index) - (z * db_index)


def optimize_hyperparams(
    x,
    n_trials=50,
    save_path="ml/data/models/kmeans/optuna/optuna_kmeans_results.json",
    timestamp=None,
):
    """
    Optimizes MiniBatchKMeans hyperparameters using Optuna and saves the results.
    :param:
        x (ndarray): Training data.
        n_trials (int, optional): Number of optimization trials. Defaults to 50.
        save_path (str, optional): Path to save optimization results. Defaults to "ml/data/models/kmeans/optuna/optuna_kmeans_results.json".
    :return:
        dict: Best parameters and corresponding silhouette score.
    """
    logger = get_logger_with_timestamp(
        timestamp or datetime.now().strftime("%Y%m%d_%H%M%S")
    )
    best_params, best_value = {}, float("-inf")

    if os.path.exists(save_path):
        try:
            with open(save_path, "r") as f:
                saved_results = json.load(f)
                best_params = saved_results.get("best_params", {})
                best_value = saved_results.get("best_value", float("-inf"))
                logger.info("Loaded previous optimization results...")
        except Exception as e:
            logger.exception(f"Error loading results: {e}")

    study = optuna.create_study(
        direction="maximize", study_name="minibatch_kmeans_optimization"
    )

    if best_params:
        study.enqueue_trial(best_params)

    try:
        study.optimize(lambda trial: objective(x, trial), n_trials=n_trials)
        best_params = study.best_params
        best_value = study.best_value
    except Exception as e:
        logger.exception(f"Optimization error: {e}")

    results = {"best_params": best_params, "best_value": best_value}

    try:
        with open(save_path, "w") as f:
            json.dump(results, f, indent=4)
        logger.info(f"Results saved to {save_path}")
    except Exception as e:
        logger.exception(f"Error saving results: {e}")

    return results


def auto_pca_scatter_plot(X_pca, k, labels, timestamp, logger):
    save_dir = os.path.join("ml/src/results/", timestamp, "scatter_plots")
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, f"pca_scatter_plot_k{str(k)}.png")
    n_components = X_pca.shape[1]
    if n_components < 2:
        logger.info("主成分數量小於2，無法畫 scatter plot。")
        return
    elif n_components == 2:
        plt.figure(figsize=(8, 6))
        plt.scatter(
            X_pca[:, 0], X_pca[:, 1], c=labels, cmap="tab10", alpha=0.7, edgecolor="k"
        )
        plt.xlabel("PC1")
        plt.ylabel("PC2")
        plt.title(f"PCA Scatter Plot (2D) for k={k}")
        plt.savefig(save_path)
        plt.close()
    else:
        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection="3d")
        if isinstance(X_pca, pd.DataFrame):
            ax.scatter(
                X_pca.iloc[:, 0],
                X_pca.iloc[:, 1],
                X_pca.iloc[:, 2],
                c=labels,
                cmap="tab10",
                alpha=0.7,
                edgecolor="k",
            )
        else:
            ax.scatter(
                X_pca[:, 0],
                X_pca[:, 1],
                X_pca[:, 2],
                c=labels,
                cmap="tab10",
                alpha=0.7,
                edgecolor="k",
            )
        ax.set_xlabel("PC1")
        ax.set_ylabel("PC2")
        ax.set_zlabel("PC3")
        plt.title(f"PCA Scatter Plot (3D) for k={k}")
        plt.savefig(save_path)
        plt.close()
