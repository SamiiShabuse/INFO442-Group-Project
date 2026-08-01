# Dashboard

This folder contains the Streamlit dashboard for the project.

Run it from the project root with:

```bash
streamlit run dashboard/app.py
```

The dashboard uses cleaned project outputs from `data/processed/`, especially:

- `data/processed/integrated/`
- `data/processed/features/`
- `data/processed/modeling/`
- `data/processed/model_comparison/`
- `data/processed/portfolio_optimization/`

## Current Pages

- Overview
- Model Comparison
- Prediction Explorer
- Portfolio Strategies
- Live Optimizer

## Model Connections

The Model Comparison page reads the refreshed comparison tables from
`data/processed/model_comparison/`. It includes Linear Regression, Ridge
Regression, Random Forest, Gradient Boosting, and Neural Network MLP. GARCH is
displayed separately because it was evaluated only on SPY.

The Prediction Explorer reads each model's `test_predictions.csv` file and
supports all five all-ticker models, including the MLP.

The Live Optimizer intentionally uses Random Forest predicted volatility
combined with historical correlations. Random Forest remains the best
all-ticker volatility model by MAE, RMSE, and R2; the MLP is included as a
comparison model but is not used for portfolio construction.

## Notes

Install dashboard dependencies from the project root with:

```bash
pip install -r dashboard/requirements.txt
```

If a modeling notebook is rerun, rerun the model-comparison notebook before
launching the dashboard so its saved comparison tables contain the newest
metrics.

The dashboard should stay focused on presentation and interaction. Data cleaning, feature engineering, modeling, and portfolio optimization should continue to live in the notebooks and processed output files.
