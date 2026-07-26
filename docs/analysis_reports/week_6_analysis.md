# Week 6 Analysis: Training Time Tracking and Feature Selection

**Project:** Stock Market Analysis & Portfolio Optimization
**Date:** July 26, 2026

## Main Question

After the professor's feedback, we focused on making the modeling pipeline easier to explain and more defensible.

The main goals were:

- Add training periods and training timestamps to the model outputs.
- Add feature selection before modeling.
- Connect the selected feature list back into the modeling notebooks.
- Rerun the models and portfolio optimization so the final outputs use the updated feature set.

## What Changed

The modeling notebooks now track the time period and runtime information for each model.

The model outputs include:

| Column | Meaning |
| --- | --- |
| `split_date` | Date used to separate training data from test data. |
| `train_start_date` | First date included in the training period. |
| `train_end_date` | Last date included in the training period. |
| `test_start_date` | First date included in the test period. |
| `test_end_date` | Last date included in the test period. |
| `train_rows` | Number of rows used for training. |
| `test_rows` | Number of rows used for testing. |
| `training_start_timestamp` | Timestamp for when model training started. |
| `training_end_timestamp` | Timestamp for when model training ended. |
| `training_duration_seconds` | How long the model took to train. |

This makes the model results easier to audit because we can explain what dates each model learned from, what dates it was tested on, and how long each training run took.

## Feature Selection Connection

The feature selection work now produces a shared selected feature file:

- `data/processed/features/selected_features.csv`

The following modeling notebooks now load that file instead of using separate hardcoded feature lists:

- Linear Regression
- Ridge Regression
- Random Forest
- Gradient Boosting

GARCH was not changed because it is a SPY-only statistical volatility model and does not use the tabular feature columns.

## Selected Features

The final selected feature list keeps 17 features.

Selected market features:

- `return_lag_1`
- `return_lag_5`
- `rolling_return_5d`
- `rolling_return_20d`
- `abs_return`
- `squared_return`
- `rolling_abs_return_20d`
- `rolling_volatility_5d`
- `price_to_moving_avg_20d`

Selected FRED macro features:

- `vix`
- `treasury_10yr_pct`
- `yield_curve_spread`
- `is_inverted`
- `fed_funds_rate_pct`
- `unemployment_rate_pct`
- `recession_flag`
- `cpi_pct_change`

Features dropped by feature selection included redundant or raw-level columns such as `rolling_volatility_20d`, `rolling_squared_return_20d`, `risk_free_rate_decimal`, `moving_avg_20d`, and `cpi_index`.

## Model Results After Connecting Selected Features

After connecting `selected_features.csv` into the modeling notebooks, we reran all models and reran the model comparison notebook.

| Model | MAE | RMSE | R2 | Training Duration |
| --- | ---: | ---: | ---: | ---: |
| Random Forest tuned | 0.003741 | 0.005802 | 0.3390 | 38.90 sec |
| Gradient Boosting | 0.004113 | 0.005946 | 0.3055 | 1.69 sec |
| Baseline: rolling volatility | 0.004647 | 0.007130 | 0.0015 | N/A |
| Ridge Regression | 0.005362 | 0.007763 | -0.1837 | 0.08 sec |
| Linear Regression | 0.005363 | 0.007764 | -0.1839 | 0.01 sec |

The current best all-ticker model is Random Forest tuned. It has the lowest RMSE and highest R2 after the selected feature list was connected.

## Training and Test Period

The updated model comparison used the same time-based split as before.

| Item | Value |
| --- | --- |
| Split date | 2024-01-01 |
| Training period | 2018-01-31 to 2023-12-29 |
| Test period | 2024-01-02 to 2025-12-01 |
| Training rows | 31,269 |
| Test rows | 10,101 |

## Portfolio Results After Model Rerun

Because the Random Forest predictions changed after feature selection, we reran the portfolio optimization notebook too.

| Strategy | Annualized Return | Annualized Volatility | Sharpe Ratio | Max Drawdown | Cumulative Return |
| --- | ---: | ---: | ---: | ---: | ---: |
| Historical Max Sharpe | 0.2669 | 0.1371 | 1.6042 | -0.1223 | 0.6682 |
| RF Predictive Max Sharpe | 0.2713 | 0.1526 | 1.4701 | -0.1539 | 0.6755 |
| Historical Min Vol | 0.1521 | 0.0764 | 1.3754 | -0.0615 | 0.3451 |
| Equal Weight | 0.1737 | 0.1054 | 1.2025 | -0.1057 | 0.3968 |
| RF Predictive Min Vol | 0.1297 | 0.0753 | 1.0989 | -0.0635 | 0.2868 |
| SPY Benchmark | 0.2109 | 0.1637 | 1.0015 | -0.1876 | 0.4811 |

The RF Predictive Max Sharpe portfolio now has the highest annualized return and cumulative return. However, Historical Max Sharpe still has the highest Sharpe ratio, meaning it had the best risk-adjusted performance.

## Interpretation

The main finding is that the expanded FRED data helps, but it should not be used blindly. Feature selection helped us avoid keeping every macro column just because it was available.

The selected feature list improved the tree-based models most clearly. Random Forest became the strongest all-ticker volatility model after using the selected feature list, and Gradient Boosting also remained stronger than the baseline.

Linear Regression and Ridge Regression still performed worse than the baseline. This suggests that the relationship between market features, macro features, and future volatility is probably not simple enough for a linear model to capture well.

The tradeoff is:

- Full macro data gives the model more information, but it can add noise and redundancy.
- Selected features reduce noise and make the model easier to explain.
- Random Forest gets the most benefit from the selected feature set, but it also takes much longer to train.
- Gradient Boosting is slightly less accurate than Random Forest, but trains much faster.

## Decision / Next Step

The selected feature list is now connected to the main tabular modeling notebooks, so feature selection is the single source of truth for Linear Regression, Ridge Regression, Random Forest, and Gradient Boosting.

Recommended next steps:

- Keep Random Forest tuned as the current best predictive model.
- Keep Gradient Boosting as a strong backup model because it is faster and still performs well.
- Keep GARCH separate because it is SPY-only and not directly comparable to the all-ticker models.
- Use the refreshed portfolio optimization results when discussing final portfolio strategy performance.
- Update the dashboard wording so it reflects Random Forest as the current best all-ticker model.

This gives us a clearer final project story: FRED macro data was useful, feature selection made it more reliable, and Random Forest became the strongest volatility model after the selected feature list was connected and the notebooks were rerun.
