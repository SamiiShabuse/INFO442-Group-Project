# End-to-End Project Workflow

This document explains the full story of the project from raw data to model
evaluation, portfolio optimization, dashboard outputs, and dry-run orders.

## One-Sentence Summary

The project predicts each asset's next 20-trading-day volatility, uses that
forecast as a risk input for portfolio optimization, and evaluates whether the
model and resulting portfolio workflow behave better than simple baselines.

## 1. Data Sources

The project uses public financial and macroeconomic data:

- Yahoo Finance: daily open, high, low, close, adjusted close, and volume data.
- Wikipedia S&P 500 table: ticker, company, sector, and industry metadata.
- FRED: risk-free rate and macro context used for Sharpe ratio and analysis.

Raw source files live in:

```text
data/raw/
```

Cleaned source-specific files live in:

```text
data/processed/source_data/
```

## 2. Data Integration

The integration step combines market prices, returns, asset metadata, benchmark
data, and macro/risk-free-rate data into project-level datasets.

Key outputs:

```text
data/processed/integrated/daily_market_data.csv
data/processed/integrated/asset_metadata.csv
data/processed/integrated/modeling_base_dataset.csv
```

These files give the later steps a consistent date/ticker structure.

## 3. Feature Engineering

The feature engineering step creates the model-ready table. Features include
rolling return, rolling volatility, moving-average, volume, drawdown,
benchmark, and macro variables.

The main target is:

```text
future_volatility_20d
```

That target represents realized volatility over the next 20 trading days. It is
shifted forward so the model learns from information available on the feature
date and predicts future risk.

Key outputs:

```text
data/processed/features/feature_engineered_dataset.csv
data/processed/features/selected_features.csv
data/processed/features/feature_selection_summary.csv
```

## 4. Modeling

The modeling notebooks compare several volatility models:

- Linear Regression
- Ridge Regression
- Random Forest
- Gradient Boosting
- Neural Network MLP
- GARCH for SPY only

The all-ticker models use the same selected feature list. GARCH is reported
separately because it is a single-series volatility model in this project.

Random Forest is the main live model because it performed best among the
all-ticker models by the project evaluation metrics.

Key Random Forest outputs:

```text
data/processed/modeling/random_forest/metrics.csv
data/processed/modeling/random_forest/test_predictions.csv
data/processed/modeling/random_forest/rf_model.pkl
data/processed/modeling/random_forest/rf_model.metrics.csv
data/processed/modeling/random_forest/rf_model.metadata.json
```

## 5. Live Prediction Workflow

The live workflow answers:

```text
Given the newest available market data, what future volatility does the Random
Forest expect for each ticker?
```

It runs in three steps:

1. Refresh the latest feature snapshot.
2. Generate Random Forest predictions.
3. Archive the prediction run so it can be evaluated later.

Commands:

```powershell
.\.venv\Scripts\python.exe scripts\refresh_latest_features.py

.\.venv\Scripts\python.exe scripts\generate_predictions.py `
  --model data\processed\modeling\random_forest\rf_model.pkl `
  --features data\processed\features\latest_feature_snapshot.csv `
  --selected-features data\processed\features\selected_features.csv `
  --out data\processed\modeling\random_forest\live_predictions\latest_preds.csv

.\.venv\Scripts\python.exe scripts\archive_predictions.py
```

Key outputs:

```text
data/processed/features/latest_feature_snapshot.csv
data/processed/modeling/random_forest/live_predictions/latest_preds.csv
data/processed/modeling/random_forest/live_predictions/preds_YYYY-MM-DD.csv
data/processed/modeling/random_forest/live_predictions/prediction_log.csv
```

## 6. Live Evaluation

There are two different evaluation modes, and they answer different questions.

### Completed Future-Window Evaluation

This is the honest model accuracy test.

It finds a historical feature date where the next 20 trading days have already
happened, reruns the model prediction from that date, computes actual realized
future volatility, and compares predicted versus actual volatility.

Command:

```powershell
.\.venv\Scripts\python.exe scripts\evaluate_recent_rf_predictions.py
```

Outputs:

```text
data/processed/modeling/random_forest/live_evaluation/latest_20d_rf_evaluation.csv
data/processed/modeling/random_forest/live_evaluation/latest_20d_rf_evaluation.summary.csv
```

### RF Versus Trailing Volatility

This is a same-day baseline comparison. It compares the RF forecast to the
trailing 20-day volatility ending on the feature date.

It is useful context, but it is not a true future accuracy score because it
does not wait for the next 20 trading days.

Command:

```powershell
.\.venv\Scripts\python.exe scripts\compare_prediction_to_trailing_vol.py `
  --predictions data\processed\modeling\random_forest\live_predictions\latest_preds.csv `
  --feature-date YYYY-MM-DD `
  --out data\processed\modeling\random_forest\live_evaluation\rf_vs_trailing_20d_ending_YYYY-MM-DD.csv
```

## 7. Portfolio Optimization

The portfolio optimizer uses:

- Historical daily returns.
- Historical correlations.
- Risk-free-rate data.
- Random Forest predicted future volatility.

It creates portfolio strategies such as equal-weight, minimum-volatility,
maximum-Sharpe, and risk-profile portfolios. The purpose is to compare
risk/return behavior, not to recommend real trades.

Key outputs:

```text
data/processed/portfolio_optimization/portfolio_performance_metrics.csv
data/processed/portfolio_optimization/portfolio_strategy_weights.csv
data/processed/portfolio_optimization/portfolio_daily_returns.csv
data/processed/portfolio_optimization/portfolio_cumulative_returns.csv
```

## 8. Rebalance Orders

Portfolio optimization and order generation are related but different.

Portfolio optimization answers:

```text
What should the target weights be?
```

Order generation answers:

```text
What buy/sell/hold rows would move a simulated portfolio toward those weights?
```

Command:

```powershell
.\.venv\Scripts\python.exe scripts\generate_rebalance_orders.py --portfolio-value 100000
```

Outputs:

```text
data/processed/portfolio_optimization/live_weights/target_weights_YYYY-MM-DD.csv
data/processed/portfolio_optimization/paper_orders/rebalance_orders_YYYY-MM-DD.csv
```

These are dry-run outputs only. They do not submit orders.

## 9. Dashboard

The Streamlit dashboard is the presentation layer. It reads processed outputs
instead of rebuilding the whole pipeline on every page load.

Run:

```powershell
streamlit run dashboard/app.py
```

Dashboard pages:

- Overview
- Model Comparison
- Prediction Explorer
- Portfolio Strategies
- Live Optimizer

## 10. Why The Refactor Matters

The project now separates three responsibilities:

- Notebooks explain analysis and produce visuals.
- `src/portfolio_risk/` contains reusable tested logic.
- `scripts/` expose repeatable command-line workflows.

This makes the repository easier to understand, test, rerun, and present to
employers or reviewers.

## 11. Current Status

The main project pipeline is implemented:

- Data acquisition, preprocessing, integration, and feature engineering.
- Multiple volatility prediction models.
- Random Forest export and live prediction workflow.
- Live prediction archival.
- Completed-window and trailing-volatility evaluation.
- Portfolio optimization.
- Dry-run rebalance order generation.
- Dashboard presentation layer.
- Unit tests for package logic.

The remaining polish is final presentation/report work: choose the strongest
visuals, explain the main results, document limitations, and present the final
story clearly.

## 12. Responsible Use

The project predicts volatility, not guaranteed future returns. Market
relationships can change, and optimization inputs are estimates. The dashboard
and dry-run orders are for education and analysis only, not financial advice.
