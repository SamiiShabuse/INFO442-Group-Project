# Feature Engineering Notebooks

This folder contains notebooks that turn integrated data into model-ready features, and select the final feature set.

## Current Notebooks

- `01_feature_engineering.ipynb`

This notebook reads from:

- `data/processed/integrated/modeling_base_dataset.csv`

It writes to:

- `data/processed/features/feature_engineered_dataset.csv`

- `02_feature_selection.ipynb`

This notebook reads from:

- `data/processed/features/feature_engineered_dataset.csv`

It writes to:

- `data/processed/features/selected_features.csv`
- `data/processed/features/feature_selection_summary.csv`

It ranks candidate features by correlation with the target, feature-to-feature redundancy, Random Forest importance, and mutual information, then saves the final selected feature list.

Run `01_feature_engineering.ipynb` after integration, then `02_feature_selection.ipynb`, then modeling.
