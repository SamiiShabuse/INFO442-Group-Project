# Predictive vs Historical Volatility

This folder holds the notebook that answers the project's central research question directly:
**does using predicted volatility in portfolio optimization actually produce a better portfolio than
using historical volatility, or than not optimizing at all?**

## Notebook

- `01_rf_vs_baseline_portfolio_impact.ipynb`

It runs in four parts:

1. **Forecast accuracy** — Random Forest vs a historical-volatility baseline (an asset's trailing
   20-day volatility used as the forecast for the next 20 days), including a per-ticker breakdown,
   a significance test that accounts for overlapping windows, and a decomposition of where the
   model's skill actually comes from.
2. **Portfolio impact** — a walk-forward backtest that rebalances every 20 trading days and compares
   equal-weight, two historical minimum-volatility baselines, the Random Forest predictive
   minimum-volatility portfolio, and the SPY benchmark.
3. **Robustness** — the same backtest across six rebalancing frequencies, to check which conclusions
   survive and which do not.
4. **Risk model calibration** — whether each risk model's predicted portfolio volatility matched the
   volatility that portfolio went on to realize.

Outputs are written to `data/processed/predictive_vs_historical/`.

## Why this notebook exists separately from `06_portfolio_optimization`

Notebook 06 builds its Random Forest portfolio from a **single prediction date** and holds those
weights for the entire test period. Because the model forecasts volatility 20 trading days ahead,
that design asks one forecast to carry a portfolio for roughly 500 trading days, so its comparison
cannot isolate whether the model adds value.

This notebook rebalances at the model's native 20-day horizon and treats rebalancing frequency as an
experimental variable rather than a fixed assumption. Notebook 06 is left unchanged as the original
strategy-comparison work.

## How the comparison is kept controlled

The `Historical Min Vol (matched)` strategy uses the **identical** covariance construction as the
Random Forest strategy — same trailing 252-day correlation matrix, same optimizer, same constraints.
Only the volatility input differs. That isolates the model's contribution.

A second baseline, `Historical Min Vol (252d cov)`, uses a trailing 252-day sample covariance matrix.
It is included because it is the estimator a practitioner would actually reach for, and it is a
tougher opponent than the matched baseline.

All inputs at a rebalance date use only data available on that date. The notebook includes an
explicit look-ahead check confirming the baseline volatility feature is trailing.

## Main findings

- The Random Forest is a clearly better volatility forecaster than the baseline: about 19% lower MAE
  and RMSE, better on 20 of 21 tickers, significant after clustering by date.
- Most of that advantage is **cross-sectional** (knowing which assets are risky) rather than
  **time-series** (knowing when a given asset's volatility will change).
- The Random Forest risk model produced **lower realized portfolio volatility at every rebalancing
  frequency tested**, with better-calibrated risk forecasts and lower turnover.
- It did **not** reliably improve the Sharpe ratio — that advantage flips sign across rebalancing
  frequencies, so it is not a claim the report should make.
- **Equal-weight had the highest Sharpe ratio of any strategy** over this test period.

## Reproducing

Run after `04_modeling/02_random_forest.ipynb`, since it reads that notebook's saved test predictions.

```bash
jupyter nbconvert --to notebook --execute --inplace \
  notebooks/09_predictive_vs_historical/01_rf_vs_baseline_portfolio_impact.ipynb
```

Runtime is roughly 20 seconds.

## Inputs

- `data/processed/modeling/random_forest/test_predictions.csv`
- `data/processed/features/feature_engineered_dataset.csv`
- `data/processed/integrated/daily_market_data.csv`
