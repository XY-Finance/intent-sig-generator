.PHONY: automl collect_raw_data feature_engineering kmeans_pipeline

automl: collect_raw_data feature_engineering kmeans_pipeline

collect_raw_data:
	python3 -m ml.src.preprocessing.collect_raw_data

feature_engineering:
	python3 -m ml.src.preprocessing.features_engineering

kmeans_pipeline:
	python3 -m ml.src.models.kmeans.kmeans_pipeline

agent:
	python3 -m ml.src.agent.main

update_price:
	python3 -m ml.src.utils.update_price

lint:
	black --check ml
	isort --check-only --profile black ml

format:
	black ml
	isort --profile black ml

venv:
	python3 -m venv .venv
	. .venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt

activate:
	@echo "Run this in your shell to activate the venv:"
	@echo "source .venv/bin/activate"