.PHONY: automl collect_raw_data feature_engineering kmeans_pipeline

automl: collect_raw_data feature_engineering kmeans_pipeline

collect_raw_data:
	python -m ml.src.preprocessing.collect_raw_data

feature_engineering:
	python -m ml.src.preprocessing.features_engineering

kmeans_pipeline:
	python -m ml.src.models.kmeans.kmeans_pipeline

agent:
	python -m ml.src.agent.main

update_price:
	python -m ml.src.utils.update_price

lint:
	black --check ml
	isort --check-only --profile black ml

format:
	black ml
	isort --profile black ml
