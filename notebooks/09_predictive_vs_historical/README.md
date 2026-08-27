# Predictive vs Historical Volatility

This folder holds the notebook that answers the project's central research
question directly: **does using predicted volatility in portfolio optimization
actually produce a better portfolio than using historical volatility, or than
not optimizing at all?**

## Notebook

- `01_rf_vs_baseline_portfolio_impact.ipynb`

It runs in four parts:

1. **Forecast accuracy** - Random Forest vs a historical-volatility baseline
   (an asset's trailing 20-day volatility used as the forecast for the next
   20 days), including a per-ticker breakdown, a significance test that accounts
   for overlapping windows, and a decomposition of where the model's skill
   actually comes from.
2. **Portfolio impact** - a walk-forward backtest that rebalances every
   20 trading days and compares equal-weight, two historical minimum-volatility
   baselines, the Random Forest predictive minimum-volatility portfolio, and
   the SPY benchmark.
3. **Robustness** - the same backtest across six rebalancing frequencies, to
   check which conclusions survive and which do not.
4. **Risk model calibration** - whether each risk model's predicted portfolio
   volatility matched the volatility that portfolio went on to realize.

Outputs are written to `data/processed/predictive_vs_historical/`.

## Why This Notebook Exists Separately From `06_portfolio_optimization`

Notebook 06 builds its Random Forest portfolio from a **single prediction
date** and holds those weights for the entire test period. Because the model
forecasts volatility 20 trading days ahead, that design asks one forecast to
carry a portfolio for roughly 500 trading days, so its comparison cannot
isolate whether the model adds value.

This notebook rebalances at the model's native 20-day horizon and treats
rebalancing frequency as an experimental variable rather than a fixed
assumption. Notebook 06 is left unchanged as the original strategy-comparison
work.

## How The Comparison Is Kept Controlled

The `Historical Min Vol (matched)` strategy uses the **identical** covariance
construction as the Random Forest strategy: same trailing 252-day correlation
matrix, same optimizer, same constraints. Only the volatility input differs.
That isolates the model's contribution.

A second baseline, `Historical Min Vol (252d cov)`, uses a trailing 252-day
sample covariance matrix. It is included because it is the estimator a
practitioner would actually reach for, and it is a tougher opponent than the
matched baseline.

All inputs at a rebalance date use only data available on that date. The
notebook includes an explicit look-ahead check confirming the baseline
volatility feature is trailing.

## Main Findings

- The leakage-safe Random Forest is a better volatility forecaster than the
  trailing-volatility baseline: MAE improves from 0.00469 to 0.00412
  (about 12.2% lower error), RMSE improves from 0.00719 to 0.00610, and pooled
  R2 improves from 0.0075 to 0.286.
- Random Forest has lower per-ticker RMSE for 17 of 21 tickers.
- The RF risk model is better calibrated than the matched historical risk
  model, but its portfolio advantage is frequency-sensitive: it produces lower
  realized volatility at 3 of 6 tested rebalance frequencies.
- It does **not** reliably improve Sharpe ratio, so it is not a claim the
  report should make.
- **Equal-weight had the highest Sharpe ratio of any strategy** over this test
  period.

## Reproducing

Run after regenerating the leakage-safe Random Forest predictions:

```bash
python scripts/train_rf_model.py
```

Then execute this notebook:

```bash
jupyter nbconvert --to notebook --execute --inplace \
  notebooks/09_predictive_vs_historical/01_rf_vs_baseline_portfolio_impact.ipynb
```

Runtime is roughly 20 seconds.

## Inputs

- `data/processed/modeling/random_forest/test_predictions.csv`
- `data/processed/features/feature_engineered_dataset.csv`
- `data/processed/integrated/daily_market_data.csv`
