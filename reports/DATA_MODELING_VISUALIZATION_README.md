# Data Modeling & Visualization

This document summarizes the modeling approach, results, and dashboard visualizations built for this project. Full implementation details, code, and comments are in the corresponding notebooks under `notebooks/04_modeling/` and the dashboard app at `dashboard/app.py`.

**Team Members:** Danny Eapen, Jeffrey Cheung, Joel Thomas, Samii Shabuse

---

## 1. Modeling

This section covers the five models built to predict future stock volatility, the feature selection work that followed, and an honest comparison of where things currently stand.

### What we're predicting

Every model targets `future_volatility_20d`, the realized volatility (standard deviation of daily returns) over the next 20 trading days for a given ticker. This is computed strictly from future data relative to each row, so there's no look-ahead leakage into the features.

### The baseline

Before training anything, we needed something simple to beat. The baseline just assumes future volatility will look like recent volatility:

- **Baseline: `rolling_volatility_20d`**
- MAE: 0.004647
- RMSE: 0.007130
- R²: 0.0015

Any model that can't beat this isn't adding real value over "assume tomorrow looks like today."

### Data and split

- 41,370 rows across 21 tickers (2018 through late 2025)
- Time-based split, not random: everything before Jan 1, 2024 is training data (31,269 rows), everything from Jan 1, 2024 onward is the held-out test set (10,101 rows)
- A random shuffled split would leak future market conditions into training, so the chronological split is what makes the test results trustworthy

### The five models

**1. Linear Regression**
The simplest model, used as an interpretable first pass. Trained on a 17-feature set: 11 market/momentum features (returns, rolling volatility, price-to-moving-average) plus all 7 available macro features from FRED (VIX, treasury yield, yield curve spread, inversion flag, fed funds rate, unemployment, CPI).

**2. Ridge Regression**
Same feature set as Linear Regression, but with L2 regularization to penalize large coefficients. Best alpha found via cross-validation: 0.0464.

**3. Random Forest**
Tuned via grid search over `max_depth` and `min_samples_leaf` using `TimeSeriesSplit` (so validation folds always come after their training data). Best params: `max_depth=16`, `min_samples_leaf=100`. Uses a broader 35-feature set that also one-hot encodes sector and asset type, so the model can tell asset classes apart (bonds, gold, and tech stocks each get their own baseline volatility level).

**4. Gradient Boosting**
`HistGradientBoostingRegressor`, same 17-feature set as Linear/Ridge. Included to test whether a non-linear model that builds trees sequentially (each one correcting the last) could do better than a single flexible model like Random Forest.

**5. GARCH(1,1)**
A statistical volatility model rather than a machine learning model, run on SPY only (GARCH models a single return series, not a pooled multi-asset dataset like the other four). Forecasts 20 days ahead directly from the variance structure of returns, with no engineered features at all.

### Honest model comparison

These are the actual current metrics from each notebook's output, not aspirational numbers:

| Model | MAE | RMSE | R² | Beats baseline? |
|---|---|---|---|---|
| Baseline (persistence) | 0.004647 | 0.007130 | 0.0015 | — |
| Linear Regression | 0.005363 | 0.007764 | -0.184 | No |
| Ridge Regression | 0.005362 | 0.007763 | -0.184 | No |
| **Random Forest (tuned)** | **0.003741** | **0.005802** | **0.339** | Yes, clearly the best |
| Gradient Boosting | 0.004113 | 0.005946 | 0.306 | Yes, close second |
| GARCH(1,1), SPY only | 0.003815 | 0.006027 | -0.174 | Yes, vs. its own SPY-only baseline (R² -0.419) |

A quick way to read this: negative R² means the model is doing worse than just guessing the average. Right now, Linear and Ridge Regression are both underperforming the simple baseline, while Random Forest and Gradient Boosting clearly beat it. GARCH can't be compared apples-to-apples to the other four since it only runs on SPY, but it does beat its own SPY-specific baseline.

**Why Linear and Ridge are underperforming:** both are currently trained on the full 17-feature set, which includes all 7 FRED macro columns. Our feature selection experiments (below) found that this exact full-macro set actively hurts linear models. The fix is known, it just hasn't been applied back into these two notebooks yet.

### Feature selection findings

We ran a dedicated experiment (`06_feature_selection_experiments.ipynb`) to test whether trimming the macro feature set would help, instead of just throwing every available FRED variable at the models.

**Feature sets tested:**
- Market-only: 12 momentum/volatility features, no macro data
- Full macro: market features + all 7 macro columns
- Selected macro: market features + 5 hand-picked macro columns (VIX, yield curve spread, inversion flag, unemployment rate, CPI % change)

**What we found:**
- The full macro set (all 7 columns) made Linear and Ridge Regression worse, not better
- The selected macro set (5 columns) was the best-performing configuration overall: Linear Regression hit RMSE 0.005929, R² 0.31, and Ridge Regression performed almost identically
- Tree-based models (Random Forest, Gradient Boosting) were largely unaffected either way. They can handle noisy or redundant features better than linear models because they can just ignore weak splits

We also ran three automated feature ranking methods to cross-check this by hand:
- **SelectKBest (statistical F-test):** top features were the volatility/momentum features plus VIX and the recession flag
- **Mutual information (captures non-linear relationships):** ranked `rolling_volatility_20d`, `rolling_squared_return_20d`, and `rolling_abs_return_20d` highest, with CPI % change also showing up strongly
- **Random Forest importance:** `rolling_abs_return_20d` dominated at 46% importance, followed by risk-free rate, CPI % change, VIX, and yield curve spread

All three methods agree on the same core idea: recent volatility-based market features carry the most signal, and a handful of macro variables (VIX, yield curve, CPI, unemployment) add real value, but only when the noisier/less useful macro columns (like the fed funds rate and raw treasury yield) are dropped.

**Bottom line:** feature selection genuinely improves the modeling process here. It's not just a "more data is always better" situation, at least not for the linear models.

### Known gap to fix before final submission

`01_linear_regression.ipynb` and `04_ridge_regression.ipynb` are still trained on the full 17-feature set. Their written conclusions describe good performance (R² ~0.30) that was true of an earlier, better feature set, but the current output cells in both notebooks show negative R² since the notebooks haven't been rerun with the selected macro feature set that `06_feature_selection_experiments.ipynb` proved works better.

Two ways to close this before final submission:
1. Rerun 01 and 04 using the 5-feature selected macro set, so the reported numbers actually reflect the best-known configuration for those models, or
2. Keep the current honest numbers as-is, and frame the writeup as: "Linear/Ridge underperformed with the full feature set, which is exactly why we ran the feature selection experiment in notebook 06."

Either is a legitimate way to write it up. Option 2 is arguably the stronger story for a report since it shows a real methodological finding (more features isn't always better), but it does mean the two "official" model notebooks won't show their best possible numbers unless they get rerun.

### Modeling key takeaways

- Random Forest is the best-performing model for predicting 20-day future volatility across all 21 tickers, clearly beating the persistence baseline (R² 0.339 vs 0.0015)
- Gradient Boosting is a close second (R² 0.306), and is the only other model besides Random Forest that reliably beats baseline right now
- Linear and Ridge Regression, in their current state, underperform the baseline. This isn't a dead end though — it's the direct motivation for the feature selection work, and both models perform competitively (R² ~0.31) once trained on the trimmed 5-macro-feature set instead
- GARCH is a useful reference point but not directly comparable to the other four, since it only models SPY on its own return series rather than the pooled 21-ticker dataset
- Feature selection matters more for linear models than tree-based ones. Adding every available macro variable actively hurt Linear/Ridge, while Random Forest and Gradient Boosting were largely indifferent to it

---

## 2. Visualization — Dashboard

Built with Streamlit (`dashboard/app.py`), the dashboard has five pages:

### Overview
Landing page summarizing the project and highlighting the best-performing model (Random Forest) by RMSE and R².

### Model Comparison
Table and bar chart comparing all four all-ticker models across RMSE, MAE, and R², with GARCH shown separately due to its SPY-only scope.

### Prediction Explorer
Lets a user pick any model and ticker to see predicted vs. actual 20-day volatility plotted over time, along with the mean absolute error for that specific ticker.

### Portfolio Strategies
Compares five precomputed portfolio strategies (equal-weight, historical min-vol, historical max-Sharpe, RF-predictive min-vol, RF-predictive max-Sharpe) on annualized return, volatility, Sharpe ratio, and max drawdown.

### Live Optimizer
The most interactive page — lets a user select assets and a risk profile, then builds and backtests a custom portfolio in real time:
- **Risk profile presets** (Conservative, Balanced, Aggressive, or Custom) auto-configure the optimization objective (minimize volatility vs. maximize Sharpe ratio) and the maximum weight allowed per asset
- **Optimization** uses the Random Forest model's predicted 20-day volatility (the best individual volatility predictor) combined with historical asset correlations as the risk model, rather than relying purely on historical volatility
- **Efficient frontier plot** shows the full risk-return tradeoff curve for the selected assets, with the optimized portfolio marked and individual assets shown for context — a direct visualization of Markowitz portfolio theory applied to this project's actual data
- **Backtest** on the 2024+ test period compares the RF-predictive portfolio against a historical-weights version, an equal-weight version, and the SPY benchmark, with a cumulative return chart

---

## 3. Key Findings & Limitations

- Random Forest is the strongest volatility predictor (R² 0.339), with Gradient Boosting a close second (R² 0.306); linear models underperform baseline with the full feature set but become competitive (R² ~0.31) once trained on the curated 5-feature macro set
- Feature selection is a genuine methodological finding of this project, not just a data-cleaning step: more macro features actively hurt linear models while barely affecting tree-based ones
- The efficient frontier and Live Optimizer backtest demonstrate that RF-predicted volatility can inform meaningfully different portfolio weightings than historical volatility alone
- **Limitations:** predictions are based on historical/backtested data and known model limitations (even our best model, Random Forest, still leaves the majority of volatility unexplained at R² 0.339); this project is for educational purposes and does not constitute financial advice

