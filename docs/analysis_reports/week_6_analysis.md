# Week 6 Analysis: Training Time Tracking and Feature Selection

**Project:** Stock Market Analysis & Portfolio Optimization
**Date:** July 25, 2026

## Main Question

After the professor's feedback, we wanted to make the modeling work more complete and easier to explain.

The main goals were:

- Add training time periods and training run timestamps to the modeling outputs.
- Add feature importance and feature selection before deciding which columns should stay in the models.
- Test whether the expanded FRED macro data helps when all columns are included, or whether only selected columns are useful.

## What Changed

The modeling notebooks now track more information about when and how each model was trained.

The model outputs now include:

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

This makes the modeling results easier to audit because we can explain what time period each model learned from, what time period it was tested on, and how long each training run took.

## Feature Selection Notebook

We added a new notebook:

- `notebooks/04_modeling/06_feature_selection_experiments.ipynb`

This notebook compares different feature groups across multiple models:

- Market-only features
- Full macro features
- Selected macro features
- SelectKBest features
- Mutual information top features
- Lasso-selected features
- Random Forest top features

The models tested were:

- Linear Regression
- Ridge Regression
- Random Forest
- Gradient Boosting

## Feature Selection Results

The best results came from using the market features plus a smaller selected set of FRED macro features.

| Model | Feature Set | Main Takeaway |
| --- | --- | --- |
| Linear Regression | Selected macro | Best overall result in this experiment. |
| Ridge Regression | Selected macro | Performed almost the same as Linear Regression. |
| Linear Regression | SelectKBest | Strong result with fewer features. |
| Ridge Regression | SelectKBest | Similar to Linear Regression with SelectKBest. |
| Random Forest | SelectKBest | Best Random Forest result in this notebook. |
| Gradient Boosting | Full macro | Best Gradient Boosting result, but not the best overall result. |

The selected macro feature set kept:

- `vix`
- `yield_curve_spread`
- `is_inverted`
- `unemployment_rate_pct`
- `cpi_pct_change`

## Feature Importance Findings

The feature importance results showed that recent volatility-related market features are still very important.

Important market features included:

- `rolling_volatility_20d`
- `rolling_squared_return_20d`
- `rolling_abs_return_20d`
- `rolling_volatility_5d`

Important macro features included:

- `vix`
- `risk_free_rate_decimal`
- `cpi_pct_change`
- `yield_curve_spread`
- `fed_funds_rate_pct`
- `unemployment_rate_pct`

This means the FRED data does help, but it works best when we choose the most useful macro signals instead of automatically keeping every macro column.

## Interpretation

The main finding is that more columns do not always mean a better model.

The expanded FRED data is useful because it gives the models extra economic context, such as market fear, interest rates, inflation, unemployment, and recession signals. However, adding every macro column at once can also add noise or repeated information.

Some macro variables are related to each other, especially the interest-rate features. If the model receives too many similar macro columns, it may become harder for the model to separate useful signal from redundant information.

The tradeoff is:

- Full macro features give the model the most information, but they can increase noise and complexity.
- Selected macro features give the model less information, but the information is cleaner and more focused.
- Market-only features are simpler and still strong, but they miss useful economic context.

Based on the Week 6 experiments, the best direction is to keep the selected macro features instead of using every FRED column in the final model.

## Decision / Next Step

The next step should be to update the main modeling notebooks so they use the selected macro feature set consistently.

Recommended final feature direction:

- Keep the original market volatility and return features.
- Keep selected macro indicators like `vix`, `yield_curve_spread`, `is_inverted`, `unemployment_rate_pct`, and `cpi_pct_change`.
- Be careful with using every interest-rate column together because some of them may be redundant.
- Continue reporting training periods, timestamps, and training duration in the model result files.

This gives us a stronger project story: the FRED data helped, but feature selection was needed to decide which macro columns actually improved the models.

## Numbers to Show Professor

The feature selection notebook used the same time-based split as the main modeling notebooks.

| Item | Value |
| --- | --- |
| Split date | 2024-01-01 |
| Training period | 2018-01-31 to 2023-12-29 |
| Test period | 2024-01-02 to 2025-12-01 |
| Training rows | 31,269 |
| Test rows | 10,101 |

The strongest model results from the feature selection notebook were:

| Model | Feature Set | Number of Features | RMSE | R2 |
| --- | --- | ---: | ---: | ---: |
| Linear Regression | Selected macro | 17 | 0.005929 | 0.3096 |
| Ridge Regression | Selected macro | 17 | 0.005930 | 0.3095 |
| Linear Regression | SelectKBest | 10 | 0.005971 | 0.2999 |
| Ridge Regression | SelectKBest | 10 | 0.005971 | 0.2998 |
| Random Forest | SelectKBest | 10 | 0.005971 | 0.2998 |
| Linear Regression | Market only | 12 | 0.005985 | 0.2965 |
| Gradient Boosting | Full macro | 21 | 0.006058 | 0.2791 |

The clearest comparison is that selected macro features performed better than using every macro feature.

| Model | Feature Set | RMSE | R2 |
| --- | --- | ---: | ---: |
| Linear Regression | Selected macro | 0.005929 | 0.3096 |
| Linear Regression | Full macro | 0.007466 | -0.0948 |
| Ridge Regression | Selected macro | 0.005930 | 0.3095 |
| Ridge Regression | Full macro | 0.007457 | -0.0922 |
| Random Forest | SelectKBest | 0.005971 | 0.2998 |
| Random Forest | Full macro | 0.006912 | 0.0617 |

Top feature ranking examples:

| Method | Top Features |
| --- | --- |
| Mutual information | `rolling_volatility_20d`, `rolling_squared_return_20d`, `rolling_abs_return_20d`, `cpi_pct_change`, `fed_funds_rate_pct` |
| Random Forest importance | `rolling_abs_return_20d`, `risk_free_rate_decimal`, `cpi_pct_change`, `vix`, `yield_curve_spread` |

These numbers support the conclusion that the FRED data helps, but the full macro feature set is not the best final choice. The selected macro features keep the useful economic context while avoiding some of the noise and redundancy from using every macro column.
