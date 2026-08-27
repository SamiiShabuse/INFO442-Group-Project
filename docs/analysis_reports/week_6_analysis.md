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

After connecting `selected_features.csv` into the modeling notebooks, we reran
all models and reran the model comparison notebook. The Random Forest row below
has since been refreshed with the leakage-safe target-window split used by the
exported model workflow.

| Model | MAE | RMSE | R2 | Training Duration |
| --- | ---: | ---: | ---: | ---: |
| Random Forest | 0.004119 | 0.006101 | 0.2855 | 12.77 sec |
| Gradient Boosting | 0.004113 | 0.005946 | 0.3055 | 1.69 sec |
| Baseline: rolling volatility | 0.004693 | 0.007191 | 0.0075 | N/A |
| Ridge Regression | 0.005362 | 0.007763 | -0.1837 | 0.08 sec |
| Linear Regression | 0.005363 | 0.007764 | -0.1839 | 0.01 sec |

The leakage-safe Random Forest remains the exported live model because it has a
repeatable artifact workflow and beats the trailing-volatility baseline. In the
archived all-model comparison, Gradient Boosting remains a strong comparison
model with slightly lower RMSE.

## Training and Test Period

The refreshed Random Forest uses the same split date, but purges training rows
whose 20-trading-day target window crosses into the test period.

| Item | Value |
| --- | --- |
| Split date | 2024-01-01 |
| Training period | 2018-01-31 to 2023-11-30 |
| Training target-window end | 2023-12-29 |
| Test period | 2024-01-02 to 2025-10-31 |
| Training rows | 30,849 |
| Purged training rows | 420 |
| Test rows | 9,681 |

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

The selected feature list improved the tree-based models most clearly. After the
leakage-safe refresh, both Random Forest and Gradient Boosting remain stronger
than the trailing-volatility baseline.

Linear Regression and Ridge Regression still performed worse than the baseline. This suggests that the relationship between market features, macro features, and future volatility is probably not simple enough for a linear model to capture well.

The tradeoff is:

- Full macro data gives the model more information, but it can add noise and redundancy.
- Selected features reduce noise and make the model easier to explain.
- Random Forest has the repeatable live artifact workflow and a leakage-safe
  holdout improvement over the trailing-volatility baseline.
- Gradient Boosting remains a strong comparison model in the archived
  all-model table.

## Final Decision

The selected feature list is now connected to the main tabular modeling notebooks, so feature selection is the single source of truth for Linear Regression, Ridge Regression, Random Forest, and Gradient Boosting.

Final modeling direction:

- Keep Random Forest as the exported live predictive model.
- Keep Gradient Boosting as a strong comparison model because it is fast and
  still performs well in the archived model comparison.
- Keep GARCH separate because it is SPY-only and not directly comparable to the all-ticker models.
- Use the refreshed portfolio optimization results when discussing final portfolio strategy performance.
- Use the updated dashboard to show model comparison, prediction explorer charts, and portfolio strategy results.

This gives us a clearer final project story: FRED macro data was useful,
feature selection made it more reliable, and the exported Random Forest
workflow provides a leakage-safe volatility model for the dashboard and live
prediction scripts.
