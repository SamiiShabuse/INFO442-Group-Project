# Week 5 Analysis: FRED Macro Data Integration

**Project:** Stock Market Analysis & Portfolio Optimization
**Date:** July 18, 2026

## Main Question

We wanted to confirm whether Joel's extra FRED macro data was actually connected to the shared integrated dataset and whether the modeling notebooks used those new columns.

## What Joel Added

Joel expanded the FRED data pipeline beyond the original risk-free rate and CPI data. The combined FRED output now includes:

| Column | Meaning |
| --- | --- |
| `risk_free_rate_pct` | 3-month Treasury yield from FRED, stored as a percent. |
| `risk_free_rate_decimal` | Same 3-month Treasury yield converted to decimal form for Sharpe ratio and modeling use. |
| `vix` | CBOE Volatility Index, used as a market fear / expected volatility signal. |
| `treasury_10yr_pct` | 10-year Treasury yield, stored as a percent. |
| `yield_curve_spread` | Difference between the 10-year Treasury yield and the 3-month Treasury yield. |
| `is_inverted` | Flag for whether the yield curve is inverted. |
| `cpi_index` | Consumer Price Index level. |
| `cpi_pct_change` | Monthly CPI percent change, used as an inflation signal. |
| `fed_funds_rate_pct` | Effective federal funds rate, stored as a percent. |
| `unemployment_rate_pct` | U.S. unemployment rate, stored as a percent. |
| `recession_flag` | FRED recession indicator, where 1 means recession period and 0 means not recession. |

## What Was Connected Before

Before the integration update, only part of the FRED data was connected to the main dataset:

- `risk_free_rate_pct`
- `risk_free_rate_decimal`
- `cpi_index`
- `cpi_pct_change`

The other FRED columns existed in the processed FRED file, but they were not being merged into the shared market/modeling dataset yet.

## What Changed

The integration notebook now merges the full processed FRED macro file into the daily market dataset.

Updated outputs:

- `data/processed/integrated/daily_market_data.csv`
- `data/processed/integrated/modeling_base_dataset.csv`
- `data/processed/features/feature_engineered_dataset.csv`

After rerunning the integration and feature engineering notebooks, the feature-engineered dataset now has 30 columns and includes the extra macro context.

## Model Usage After Rerun

The following models now include the added FRED columns in their feature calculations:

- Linear Regression
- Ridge Regression
- Random Forest
- Gradient Boosting

The GARCH model does not use these columns because it is a univariate volatility model based on SPY returns, not a tabular feature model.

We intentionally kept `cpi_index` out of the model feature lists because the notebooks already noted that the CPI level can behave too much like a hidden date/time indicator. We kept `cpi_pct_change` because it is a more useful inflation-change signal.

## Model Results After Adding the FRED Columns

| Model | MAE | RMSE | R2 |
| --- | ---: | ---: | ---: |
| Gradient Boosting | 0.004113 | 0.006048 | 0.2817 |
| Random Forest tuned | 0.004062 | 0.006517 | 0.1658 |
| Baseline | 0.004647 | 0.007130 | 0.0015 |
| Ridge Regression | 0.005103 | 0.007452 | -0.0905 |
| Linear Regression | 0.005107 | 0.007456 | -0.0917 |

## Interpretation

Adding the full FRED macro data did change the model calculations, but it did not automatically make every model better.

Gradient Boosting became the strongest model after the rerun. Random Forest still beat the baseline, but it performed worse than before. Linear Regression and Ridge Regression performed worse than the baseline after the extra macro columns were added.

The likely reason is that some macro columns are useful, but adding all of them at once creates extra noise and redundancy. Several interest-rate columns are closely related to each other, and macro values are shared across all tickers on the same date. That can make simple linear models especially unstable or less helpful.

## Decision / Next Step

The extra FRED data is connected correctly now, but we should probably not keep every macro column in the final model without testing.

Recommended next experiment:

- Keep likely useful macro signals such as `vix`, `yield_curve_spread`, `is_inverted`, `unemployment_rate_pct`, and `cpi_pct_change`.
- Test whether redundant rate columns such as `fed_funds_rate_pct`, `treasury_10yr_pct`, and possibly `risk_free_rate_decimal` should be dropped from the predictive model feature set.
- Compare selected macro features against the full macro feature set and the original market-only feature set.

This will help us decide whether the final model story should be "macro data improves the model" or "only selected macro indicators help, while too many macro columns add noise."
