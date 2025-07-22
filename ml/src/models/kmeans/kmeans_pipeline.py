import json
import logging
import os
from datetime import datetime

import joblib
import pandas as pd
import pyarrow as pa
import pyarrow.feather as feather
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

from ml.config.kmeans_pipeline_config import KMEANS_PIPELINE_DEFAULT_CONFIG
from ml.config.training_configs import (
    COLLECT_RAW_DATA_CONFIG,
    FEATURES_ENGINEERING_CONFIG,
    KMEANS_PIPELINE_CONFIG,
)
from ml.src.models.kmeans.kmeans_analysis import (
    analyze_kmeans,
    measure_performances,
    optimize_hyperparams,
)
from ml.src.utils.comparison import clusters_analysis
from ml.src.utils.logger import get_logger_with_timestamp
from ml.src.utils.splitting import splitting
from ml.src.visualization.plotter import analyze_clusters


class KMeansPipeline:
    def __init__(
        self,
        n_components=0.95,
        analyse=True,
        reduce_dimensions=True,
        optimization=False,
        no_graph=False,
    ):
        self.n_components = n_components
        self.analyse = analyse
        self.reduce_dimensions = reduce_dimensions
        self.optimization = optimization
        self.no_graph = no_graph
        self.dataset = None
        self.x_all = None
        self.y_all = None
        self.best_k = 4
        self.model = None
        self.clusters = None
        self.pca = None
        self.metrics = None
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.logger = get_logger_with_timestamp(self.timestamp, "kmeans_pipeline")
        self.pkl_path = "ml/src/models/kmeans/pkl/"
        self.model_path = f"ml/src/models/kmeans/pkl/kmeans_model_{self.timestamp}.pkl"
        self.features_path = "ml/data/features/user_features.arrow"
        self.raw_features_path = "ml/data/features/raw_user_features.arrow"
        self.predictions_path = "ml/data/models/kmeans/kmeans_predictions.arrow"
        self.optuna_results_path = (
            "ml/data/models/kmeans/optuna/optuna_study_results.json"
        )
        self.performance_path = "ml/data/models/kmeans/kmeans_performance.json"
        self.scoring_path = "ml/data/models/kmeans/kmeans_user_scores.csv"
        self.results_path = f"ml/src/results/{self.timestamp}/"

    def run(self):
        logging.info("=== Running KMeans pipeline ===")
        self.load_data()
        self.reduce()
        self.load_hyperparameters()
        if self.optimization:
            self.optimize_hyperparameters()
        self.analyze()
        self.train_model()
        self.predict()
        self.analyse_results()
        self.compute_graphics()
        self.save()
        self.logger.info("=== KMeans pipeline completed ===")

    def load_data(self):
        self.logger.info("1. Loading and splitting data")
        self.dataset = splitting()
        self.x_all = self.dataset["all"][0]  # features
        self.y_all = self.dataset["all"][1]  # address

    def reduce(self):
        if self.reduce_dimensions:
            self.logger.info("2. Reducing dimensions via PCA (95% variance retained)")
            self.pca = PCA(n_components=self.n_components)
            self.logger.info(f"Before dimensions reduction: {self.x_all.shape}")
            feature_names = self.x_all.columns
            self.logger.info(feature_names)
            self.x_all = self.pca.fit_transform(self.x_all)
            self.logger.info(f"After dimensions reduction: {self.x_all.shape}")
            self.logger.info(self.x_all)
            for i, component in enumerate(self.pca.components_):
                self.logger.info(f"PC{i+1}:")
                for name, coef in sorted(
                    zip(feature_names, component), key=lambda x: abs(x[1]), reverse=True
                ):
                    self.logger.info(f"  {name}: {coef:.3f}")
            # self.logger.info(f"PCA components: {self.pca.components_}")
        else:
            self.logger.info("2. Skipping dimensionality reduction")

    def analyze(self):
        if self.analyse:
            self.logger.info("4. Analyzing to find best cluster count")
            self.best_k = analyze_kmeans(self.x_all, "train", self.timestamp)
            self.logger.info(f"Best k from analysis (train) : {self.best_k}")
        else:
            self.logger.info("4. Skipping analysis")

    def load_hyperparameters(self):
        if os.path.exists(self.optuna_results_path):
            self.logger.info("3. Loading saved hyperparameters")
            try:
                with open(self.optuna_results_path, "r") as f:
                    results = json.load(f)
                    best_params = results.get("best_params", {})
                    self.best_k = best_params.get("n_clusters", self.best_k)
                    self.logger.info(f"Loaded best params: {best_params}")
            except Exception as e:
                self.logger.exception(f"Failed loading hyperparams: {e}")
        else:
            self.logger.info("3. No precomputed hyperparameters found")

    def optimize_hyperparameters(self):
        self.logger.info("5. Optimizing hyperparameters with Optuna")
        results = optimize_hyperparams(
            self.x_all, n_trials=300, save_path=self.optuna_results_path
        )
        self.best_k = results["best_params"]["n_clusters"]
        self.logger.info(f"Optimal k after tuning: {self.best_k}")

    def train_model(self):
        self.logger.info("6. Training model")
        self.model = KMeans(n_clusters=self.best_k, random_state=42, n_init=10)
        self.model.fit(self.x_all)

    def predict(self):
        self.logger.info("7. Predicting clusters")
        self.clusters = self.model.predict(self.x_all)
        results = pd.DataFrame({"address": self.y_all, "cluster": self.clusters})
        self.logger.info(f"Clustered {len(results)} addresses")

        table = pa.Table.from_pandas(results)
        feather.write_feather(table, self.predictions_path)
        self.logger.info(f"Saved predictions to {self.predictions_path}")

        csv_path = self.predictions_path.replace(".arrow", ".csv")
        results.to_csv(csv_path, index=False)
        self.logger.info(f"Saved predictions to {csv_path}")

        results_path = os.path.join(self.results_path, "predictions")
        os.makedirs(results_path, exist_ok=True)
        results.to_csv(f"{results_path}/kmeans_predictions.csv", index=False)
        self.logger.info(f"Saved predictions to {results_path}")

    def analyse_results(self):
        self.logger.info("8. Evaluating clustering performance")
        db_index, ch_index, silhouette_avg = measure_performances(
            self.x_all, self.clusters
        )
        self.metrics = {
            "Davies-Bouldin Index": db_index,
            "Calinski-Harabasz Index": ch_index,
            "Silhouette Avg": silhouette_avg,
        }

        with open(self.performance_path, "w") as f:
            json.dump(self.metrics, f, indent=4)

        save_path = os.path.join(
            self.results_path, "kmeans_evaluation/kmeans_performance.json"
        )
        with open(save_path, "w") as f:
            json.dump(self.metrics, f, indent=4)

        self.logger.info("Cluster metrics computed")
        clusters = clusters_analysis(
            self.features_path,
            self.raw_features_path,
            self.predictions_path,
            self.timestamp,
        )
        for k, data in clusters.items():
            self.logger.info(
                f"Cluster {k}: {data['address']} users, rate: {data['repartition_rate']:.2%}"
            )

    def compute_graphics(self):
        if self.no_graph:
            self.logger.info("9. Skipping graphic generation")
            return
        self.logger.info("9. Generating cluster visualizations")
        analyze_clusters(self.timestamp)

    def save(self):
        self.logger.info(f"10. Saving model to {self.model_path}")
        os.makedirs(os.path.dirname(self.pkl_path), exist_ok=True)
        joblib.dump(self.model, self.model_path)
        save_dir = os.path.join("ml/src/results/", self.timestamp, "configs")
        os.makedirs(save_dir, exist_ok=True)
        save_path = os.path.join(save_dir, "configs.json")
        with open(save_path, "w") as f:
            json.dump(
                {
                    "results": {
                        "timestamp": self.timestamp,
                        "best_k": self.best_k,
                        "metrics": self.metrics,
                    },
                    "configs": {
                        "collect_raw_data_config": COLLECT_RAW_DATA_CONFIG,
                        "features_engineering_config": FEATURES_ENGINEERING_CONFIG,
                        "kmeans_pipeline_config": KMEANS_PIPELINE_CONFIG,
                    },
                },
                f,
                indent=4,
            )


def get_config_value(key):
    return KMEANS_PIPELINE_CONFIG.get(key, KMEANS_PIPELINE_DEFAULT_CONFIG.get(key))


if __name__ == "__main__":
    pipeline = KMeansPipeline(
        n_components=get_config_value("n_components"),
        analyse=get_config_value("analyse"),
        reduce_dimensions=get_config_value("reduce_dimensions"),
        optimization=get_config_value("optimization"),
    )
    pipeline.run()
