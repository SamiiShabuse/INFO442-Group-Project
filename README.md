# Predictive Portfolio Optimization and Risk Analytics

[![CI](https://github.com/SamiiShabuse/Predictive-Portfolio-Risk/actions/workflows/ci.yml/badge.svg)](https://github.com/SamiiShabuse/Predictive-Portfolio-Risk/actions/workflows/ci.yml)

This project is an end-to-end data science system for studying portfolio risk.
It combines historical market data, macroeconomic context, volatility
prediction, portfolio optimization, model evaluation, and an interactive
Streamlit dashboard.

Drexel INFO 442 Data Science Project.

The core idea is simple: instead of trying to predict exact stock prices, the
project predicts each asset's future 20-trading-day volatility. Those risk
forecasts are then used with historical returns and correlations to build and
compare portfolio strategies.

This project is educational and analytical. It is not financial advice, and it
does not submit real trades.

Live dashboard: https://portfolio-volatility-optimizer.streamlit.app/

## Key Results

- After correcting target-window leakage, Random Forest improved pooled
  20-day volatility forecast MAE from 0.00469 for a trailing-volatility
  baseline to 0.00412, about 12.2% lower error. Its pooled R2 was 0.286,
  compared with 0.0075 for the baseline.
- Random Forest had lower per-ticker RMSE than the trailing-volatility
  baseline for 17 of 21 tickers and better risk-model calibration MAE
  in the portfolio experiment.
- In the walk-forward portfolio robustness sweep, the RF predictive risk
  model produced lower realized volatility at 3 of 6 tested rebalance
  frequencies. It did not consistently improve Sharpe ratio, so the
  defensible conclusion is stronger volatility forecasting, not guaranteed
  portfolio outperformance.
- The exported Random Forest artifact now uses a target-window-purged holdout
  split so training rows whose 20-day target windows cross into the 2024+
  test period are excluded from holdout training.

## Project Story

Many beginner investors focus on returns without fully understanding risk,
volatility, drawdowns, or diversification. A portfolio can look strong from
return alone while still being fragile because the assets move together or
because recent risk has changed.

This project answers the question:

```text
Can historical market features and predicted future volatility improve how we
analyze and construct portfolios for different risk profiles?
```

The project handles that question through a full pipeline:

1. Collect public financial data from Yahoo Finance, FRED, and Wikipedia.
2. Clean and integrate asset prices, benchmark data, sector/category metadata,
   and macro/risk-free-rate data.
3. Engineer rolling return, volatility, volume, drawdown, benchmark, and macro
   features.
4. Train several volatility prediction models.
5. Use Random Forest as the main live model because it has a repeatable
   artifact workflow and leakage-safe holdout performance above the
   trailing-volatility baseline.
6. Use predicted volatility inside a portfolio optimizer.
7. Compare portfolio strategies using return, volatility, Sharpe ratio,
   drawdown, cumulative return, and allocation visuals.
8. Test live Random Forest predictions against new real market data as time
   passes.
9. Run the predictive-vs-historical walk-forward experiment that directly
   tests whether ML volatility forecasts improve portfolio risk outcomes.
10. Generate dry-run rebalance orders for demonstration and paper-analysis.

## What Is Built

- A cleaned, integrated financial dataset under `data/processed/`.
- Feature-engineered model inputs and selected feature lists.
- Volatility prediction models:
  - Linear Regression
  - Ridge Regression
  - Random Forest
  - Gradient Boosting
  - Neural Network MLP
  - SPY-only GARCH comparison
- A reusable Python package under `src/portfolio_risk/`.
- Command-line scripts for training, refreshing features, predicting,
  archiving, evaluating, and generating dry-run orders.
- Analysis notebooks for data acquisition, EDA, modeling, model comparison,
  portfolio optimization, predictive-vs-historical evaluation, live RF
  evaluation, and paper-trading analysis.
- A Streamlit dashboard with model, prediction, portfolio, and live optimizer
  pages, deployed at https://portfolio-volatility-optimizer.streamlit.app/.

## Repository Layout

```text
.
  dashboard/        Streamlit dashboard app
  data/             Raw, processed, feature, model, and portfolio output files
  docs/             Project documentation, weekly summaries, and analysis notes
  notebooks/        Executable analysis workflow in pipeline order
  reports/          Polished written deliverables and presentation artifacts
  scripts/          Command-line wrappers around package workflows
  src/              Reusable Python package code
  tests/            Unit tests for reusable package logic
```

## Main Workflow

### 1. Rebuild The Research Pipeline

Run the notebooks in order when rebuilding the full academic analysis:

```text
notebooks/01_source_data/
notebooks/02_integration/
notebooks/03_features/
notebooks/04_modeling/
notebooks/05_model_comparison/
notebooks/06_portfolio_optimization/
notebooks/07_live_model_evaluation/
notebooks/08_paper_trading/
notebooks/09_predictive_vs_historical/
```

The notebooks are meant for explanation, visuals, and final analysis. Reusable
logic lives in `src/portfolio_risk/`.

### 2. Review The Definitive Experiment

The project conclusion should be based on:

```text
notebooks/09_predictive_vs_historical/01_rf_vs_baseline_portfolio_impact.ipynb
data/processed/predictive_vs_historical/
```

That notebook compares RF volatility forecasts against a trailing-volatility
baseline, runs a walk-forward portfolio backtest, sweeps rebalance frequency,
and checks risk-model calibration. The older notebook 06 portfolio comparison
is still useful as an optimizer development step, but notebook 09 is the
definitive research result.

### 3. Train The Random Forest Model

The exported Random Forest model is used by the live prediction workflow:

```powershell
.\.venv\Scripts\python.exe scripts\train_rf_model.py
```

Outputs:

```text
data/processed/modeling/random_forest/rf_model.pkl
data/processed/modeling/random_forest/rf_model.metrics.csv
data/processed/modeling/random_forest/rf_model.metadata.json
data/processed/modeling/random_forest/test_predictions.csv
data/processed/modeling/random_forest/metrics.csv
```

The training workflow derives each row's `target_end_date` and purges rows
whose future 20-trading-day target window crosses the holdout split.

### 4. Make A New Live Prediction Run

Use this when a new trading day is available:

```powershell
.\.venv\Scripts\python.exe scripts\refresh_latest_features.py

.\.venv\Scripts\python.exe scripts\generate_predictions.py `
  --model data\processed\modeling\random_forest\rf_model.pkl `
  --features data\processed\features\latest_feature_snapshot.csv `
  --selected-features data\processed\features\selected_features.csv `
  --out data\processed\modeling\random_forest\live_predictions\latest_preds.csv

.\.venv\Scripts\python.exe scripts\archive_predictions.py
```

This creates a latest prediction file, a dated prediction file, and an appended
long-format prediction log.

### 5. Evaluate The Live Model

There are two evaluation ideas:

- Completed future-window evaluation: the honest accuracy test. It only works
  for a feature date whose next 20 trading days already happened.
- RF versus trailing volatility comparison: a same-day baseline comparison. It
  is useful for context, but it is not a true future accuracy score.

Run the completed-window evaluation:

```powershell
.\.venv\Scripts\python.exe scripts\evaluate_recent_rf_predictions.py
```

Run a trailing-volatility comparison:

```powershell
.\.venv\Scripts\python.exe scripts\compare_prediction_to_trailing_vol.py `
  --predictions data\processed\modeling\random_forest\live_predictions\latest_preds.csv `
  --feature-date YYYY-MM-DD `
  --out data\processed\modeling\random_forest\live_evaluation\rf_vs_trailing_20d_ending_YYYY-MM-DD.csv
```

### 6. Generate Dry-Run Rebalance Orders

The optimizer chooses target weights. Order generation turns those target
weights into buy/sell/hold instructions for a simulated portfolio.

```powershell
.\.venv\Scripts\python.exe scripts\generate_rebalance_orders.py --portfolio-value 100000
```

The generated orders are reviewable CSV outputs only. They do not connect to a
real brokerage account.

### 7. Run The Dashboard

Live app:

```text
https://portfolio-volatility-optimizer.streamlit.app/
```

Run locally:

```powershell
streamlit run dashboard/app.py
```

The dashboard reads from `data/processed/` and presents model comparison,
prediction exploration, the predictive-vs-historical experiment, and live
optimization.

## Important Concepts

### Feature Snapshot

`latest_feature_snapshot.csv` is the current model input table. It contains the
latest available engineered features for each ticker, plus enough historical
rows to support evaluation.

### Prediction Target

The Random Forest predicts:

```text
future_volatility_20d
```

That means a prediction made from today's features is trying to estimate the
realized volatility over the next 20 trading days. Because of that, the model
cannot be fully graded the next day. It needs a completed future window.

### Portfolio Optimization Versus Order Generation

Portfolio optimization answers:

```text
What should the target weights be?
```

Order generation answers:

```text
What buy/sell/hold actions would move a portfolio toward those weights?
```

Those are related, but they are not the same thing.

## Reusable Package

The main reusable code lives under `src/portfolio_risk/`:

- `training.py`: Random Forest training and artifact export.
- `features.py`: latest feature refresh and market feature engineering.
- `prediction.py`: live prediction generation.
- `prediction_archive.py`: dated prediction archival and prediction logs.
- `evaluation.py`: completed-window and trailing-volatility evaluation.
- `portfolio.py`: portfolio math, covariance construction, and optimization.
- `orders.py`: dry-run order creation from target weights.
- `rebalancing.py`: RF-driven rebalance workflow.

See `src/README.md` for the full package map.

## Developer Setup

Install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

For editable package development:

```powershell
python -m pip install -e ".[dev]"
```

Run checks:

```powershell
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m ruff check src scripts dashboard tests
.\.venv\Scripts\python.exe -m compileall -q scripts src\portfolio_risk
```

## Documentation Map

- `docs/project_workflow.md`: full end-to-end project story.
- `notebooks/README.md`: notebook run order and outputs.
- `scripts/README.md`: script-by-script usage guide.
- `src/README.md`: reusable package map.
- `data/README.md`: data folder organization.
- `dashboard/README.md`: dashboard pages and refresh instructions.
- `reports/README.md`: polished deliverable guidance.
- `docs/archive/course/`: historical course-process files preserved outside
  the public-facing project path.

## Team And Contributions

This was built as a group data science project by Danny Eapen, Jeffrey Cheung,
Joel Thomas, and Samii Shabuse.

- Danny Eapen -- data preprocessing, integration support, dashboard support,
  and project analysis/reporting contributions.
- Jeffrey Cheung -- Random Forest modeling, RF-vs-baseline analysis,
  predictive-volatility experiments, and notebook workflow contributions.
- Joel Thomas -- FRED macro data expansion, macro feature framing, project
  story documentation, and analysis writeups.
- Samii Shabuse -- package refactoring, automated testing, CLI workflows,
  dashboard development, model deployment workflow, and repository/documentation
  polish.

## Limitations

- The model predicts volatility, not stock price direction or guaranteed
  returns.
- Historical relationships can break during unusual market conditions.
- Portfolio optimization depends on estimated inputs and simplified
  constraints.
- Transaction costs, taxes, slippage, and real brokerage execution are not
  modeled.
- The dry-run order workflow is for demonstration and analysis only.

## Disclaimer

This repository is for an educational data science project. It does not provide
financial advice, investment recommendations, or instructions to buy or sell
securities. Historical performance and model predictions do not guarantee
future results.
