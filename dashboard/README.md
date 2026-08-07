# Dashboard

This folder contains the Streamlit dashboard for the project.

Run it from the project root with:

```bash
streamlit run dashboard/app.py
```

Install dashboard dependencies from the project root with:

```bash
pip install -r dashboard/requirements.txt
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

The Portfolio Strategies page reads the saved outputs from `data/processed/portfolio_optimization/`.

## Refreshing Outputs

If feature engineering or model notebooks are rerun, rerun the downstream notebooks in order before launching the dashboard:

1. `notebooks/05_model_comparison/01_model_comparison.ipynb`
2. `notebooks/06_portfolio_optimization/01_portfolio_optimization.ipynb`

This keeps the dashboard tables and charts aligned with the newest model outputs.

## Notes

The dashboard should stay focused on presentation and interaction. Data cleaning, feature engineering, modeling, and portfolio optimization should continue to live in the notebooks and processed output files.
