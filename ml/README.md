# ML Project Overview

This directory provides a complete pipeline for blockchain user data analysis, including multi-chain data collection, feature engineering, clustering (AutoML), and result visualization. All modules and configurations are designed for flexible, reproducible research and actionable business insights into user behavior and segmentation.

---

## 📦 Folder Structure

- `ml/config/`  
  Configuration files for data collection, feature engineering, and pipeline settings.
- `ml/data/`  
  - `raw/` - Raw collected blockchain data  
  - `processed/` - Processed features and analysis results  
  - `features/` - Feature files for modeling  
  - `models/` - Saved models and predictions
- `ml/src/preprocessing/`  
  Data collection and feature engineering scripts.
- `ml/src/models/kmeans/`  
  KMeans clustering pipeline and analysis scripts.
- `ml/src/visualization/`  
  Visualization utilities for analysis results.

---

## 🧬 Data Feature Description

- **Raw Data** (`ml/data/raw/`)
  - Blockchain transaction logs, event logs, token balances, etc.
- **Processed Features** (`ml/data/processed/`)
  - `assets_distribution.csv`  
    - User asset distribution across chains and tokens (e.g., USDC, ETH, WBTC)
    - Features: token balances, ratios, total assets, **whale score**, etc.
  - `tx_behavior.csv`  
    - User transaction behavior features
    - Features: protocol diversity, tx count, active days, burstiness, inflow/outflow stats, **active score**, etc.
  - `raw_user_features.csv`  
    - All raw features before feature selection, cleaning, or aggregation
    - [Refer to this sheet](https://docs.google.com/spreadsheets/d/19LlNmWYfyDzuZncPNWM_FUSxIjMAJ7ZbU2_jGUsIkd4/edit?gid=535598059#gid=535598059)
  - `user_features.csv`  
    - Final merged features for modeling and clustering

**Key Features:**
- `whale_score`: Comprehensive asset and liquidity indicator for whale detection
- `active_score`: Activity indicator combining protocol diversity, tx frequency, etc.
- `*_balance_usd`: Token balances in USD
- `*_ratio`: Asset composition ratios
- `avg_tx_usd_value_inflow/outflow`: Average inflow/outflow per transaction
- `total_tx_usd_value_inflow/outflow`: Total inflow/outflow in USD
- `method_diversity`: Entropy of contract interaction diversity
- `chain_focus`, `protocol_type_focus`: Chain/protocol concentration indices

**Note:** All features described above are aggregated across multi-chain, including Ethereum, Arbitrum, and Base, not just single-chain features

---

## 🚀 How to Start AutoML Pipeline

**Step 1 and 2 are for first-time setup. Steps 3–6 can be run independently for further optimization or re-analysis.**

1. **Install dependencies** 
   ```bash
   pip install -r requirements.txt
   ```

2. **Run AutoML pipeline**
   ```bash
   make automl
   ```

3. **Collect raw data**
   ```bash
   make collect_raw_data
   ```

4. **Feature engineering**
   ```bash
   make feature_engineering
   ```

5. **Run KMeans pipeline**
   ```bash
   make kmeans_pipeline
   ```

6. **Check results**
   - Check processed features: `ml/data/processed/`
   - Check clustering results: `ml/src/results/<timestamp>/`

7. **Update token price**  (*Run once before collect raw data)
   ```bash
   make update_price
   ```

---

## 🛠️ How configs work?

All pipeline and feature engineering parameters are managed via config files in `ml/config/training_configs.py`.
You can customize these configs to control data collection, feature engineering, and modeling behavior without changing code.
Below are the main configs and their key parameters:

### COLLECT_RAW_DATA_CONFIG
- **based_chain_id**: The main chain for sender sampling (e.g., 1 for Ethereum)
- **chain_ids**: List of chain IDs to collect data from (e.g., [1, 42161, 8453] for Ethereum, Arbitrum, Base)
- **timestamp_threshold**: Only collect data after this Unix timestamp (default: 2023-01-01)
- **based_protocol_type**: Protocol type for sender sampling (e.g., 'Lending')
- **senders_count_threshold**: Number of unique addresses to sample (min: 10, default: 30)
- **senders_max_pages**: Max pages to fetch for senders (min: 1, default: 5)
- **logs_max_pages**: Max pages to fetch for event logs (min: 1, default: 2)
- **max_workers**: Number of threads for concurrent fetching (default: 3)
- **use_cache**: Whether to use cached data (default: False)

### FEATURES_ENGINEERING_CONFIG
- **features**: List of features to include in the final dataset (e.g., whale_score, active_score)
- **active_days_threshold**: Number of days to consider for active user calculation (default: 730)
- **assets_lookback_months**: How many months of asset history to consider (default: 12)
- **whale_score_settings**: Dict of weights for each feature in whale_score calculation
- **active_score_settings**: Dict of weights for each feature in active_score calculation

### KMEANS_PIPELINE_CONFIG
- **n_components**: Number of PCA components to keep; use a float (e.g., 0.95) to retain that proportion of variance, or an integer (e.g., 5) to keep a fixed number of components
- **analyse**: Whether to run analysis and visualization steps
- **reduce_dimensions**: Whether to apply PCA before clustering
- **optimization**: Whether to run hyperparameter optimization (usually False for production)

---

## ⚠️ Analysis Process Notes

- **Configurable Parameters**
  - All pipeline, feature, and data collection default parameters are in `ml/config/` (e.g., `features_engineering_config.py`, `kmeans_pipeline_config.py`)
  - You can override any default parameters by editing the `training_configs.py` config file 
- **Data Quality**
  - Ensure raw data is complete and up-to-date before running feature engineering
  - For example, you should run `make update_price` at least once per day to ensure token prices are up-to-date
- **Reproducibility**
  - All configs, visualizations and model performance are saved in `ml/src/results/` for reproducibility
- **Resource Usage**
  - Large datasets may require more time/memory/CPU; consider sampling small size for quick tests (e.g., `senders_count_threshold ~= 30`)

---

## 📊 How to Evaluate Analysis Results

- **Clustering Quality**
  - Check metrics: Silhouette Score, Davies-Bouldin Index, Calinski-Harabasz Index (see `ml/src/results/<timestamp>/kmeans_evaluation/`)
  - You can refer to the [Clustering Metric Reference Table](#clustering-metric-reference-table) below.
- **User Segmentation**
  - Inspect cluster composition: Are whales/active users correctly grouped?
  - You can also look up addresses on-chain, or use third-party tools such as [Arkham](https://platform.arkhamintelligence.com/) and [Nansen](https://app.nansen.ai/) to further investigate user profiles and behaviors.
- **Visualization**
  - Use provided visualization results to check cluster distributions, feature histograms, etc.
- **Business Metrics**
  - Validate clusters/labels against business logic (e.g., known whales, protocol usage patterns)

### Clustering Metric Reference Table

| Metric                  | Range      | Good Value      | Interpretation                                  |
|-------------------------|------------|-----------------|-------------------------------------------------|
| Silhouette Score        | -1 to 1    | > 0.5 (good)    | Higher is better; >0.5 is strong clustering     |
| Davies-Bouldin Index    | 0 to ∞     | < 1 (good)      | Lower is better; <1 is strong separation        |
| Calinski-Harabasz Index | 0 to ∞     | Higher is better| Higher is better; compare across experiments    |

- **Silhouette Score:** Measures how well samples are clustered; higher means better separation and cohesion.
- **Davies-Bouldin Index:** Measures average similarity between clusters; lower means better separation.
- **Calinski-Harabasz Index:** Ratio of between-cluster to within-cluster dispersion; higher means better defined clusters.

---

## ✅ What You Should / Should Not Do

### You SHOULD:
1. **Decide on your target audience and relevant raw data.**  
   Before starting any analysis, clarify which user segments or behaviors you are interested in (e.g., whales, active DeFi users) and ensure your raw data covers these groups.
2. **Select features that are valuable and insightful based on your domain knowledge.**  
   Use your understanding of blockchain, DeFi, or user behavior to identify which columns/metrics are likely to provide meaningful insights for modeling.
3. **Request new features if needed.**  
   If you identify important behavioral or financial signals that are not present in the current dataset, please communicate with Tanner to add these features to the pipeline.
4. **Pay attention to feature size and scaling.**  
   KMeans is sensitive to the scale of features. Always check for features with much larger or smaller values than others, and apply appropriate scaling (e.g., normalization or standardization) to ensure fair clustering.

### You SHOULD NOT:
1. **Repeatedly run `make collect_raw_data` without necessity.**  
   Data collection is resource-intensive and should only be performed when you need new or updated data. Frequent unnecessary runs only waste time and compute resources.
2. **Use all available columns as features for model training.**  
   Including irrelevant or redundant features (including highly collinear features) can degrade model performance and make interpretation harder. Always perform feature selection, even if it is manual selection.
3. **Use too few features for model training.**  
   Using too few features (e.g., only 2 features) limits the model's ability to capture complex user behaviors and often results in poor clustering or classification performance.
4. **Ignore clustering or model evaluation metrics.**  
   Always check metrics like silhouette score, Davies-Bouldin index, and cluster interpretability.

---

## 💡 Professional Data Analyst Tips From Cursor

- **Feature Engineering is Key:**  
  The quality of your features determines the quality of your insights and models. Invest time in understanding the data, creating new features, and iteratively refining them.
- **Document Your Process:**  
  Keep track of which features you tried, which worked, and which didn’t. This helps with reproducibility and knowledge sharing within your team.
- **Validate with Business Logic:**  
  Always cross-check your findings with domain experts or business logic. A cluster that looks good statistically may not make sense in the real world.
- **Automate, but Don’t Blindly Trust Automation:**  
  AutoML and pipelines are powerful, but human judgment is irreplaceable. Use automation to speed up routine tasks, but always review and interpret the results yourself.
- **Communicate with Developers:**  
  If you need new data or features, provide clear requirements and rationale to the dev team. Collaboration leads to better data and better results.
- **Monitor Data Drift:**  
  Blockchain and DeFi evolve rapidly. Regularly check if your features and models remain relevant as user behavior and protocols change.

---

**Remember:**  
**The best data analysis is not just about technical execution, but about asking the right questions, selecting the right data, and critically interpreting the results in context.**
