# Visualization — Dashboard

**Team Members:** Danny Eapen, Jeffrey Cheung, Joel Thomas, Samii Shabuse

## Synopsis

We built a five-page Streamlit dashboard (`dashboard/app.py`) that lets a user explore model performance, compare portfolio strategies, and build a custom portfolio in real time. The centerpiece is the Live Optimizer, which uses the project's best-performing volatility model to construct and backtest a risk-adjusted portfolio interactively, including an efficient frontier plot grounded in Markowitz portfolio theory.

---

## Overview page
Landing page summarizing the project and highlighting the best-performing model by RMSE and R².

## Model Comparison page
Table and bar chart comparing all four all-ticker models across RMSE, MAE, and R², with the SPY-only model shown separately due to its narrower scope.

## Prediction Explorer page
Lets a user pick any model and ticker to see predicted vs. actual 20-day volatility plotted over time, along with the mean absolute error for that specific ticker.

## Portfolio Strategies page
Compares five precomputed portfolio strategies (equal-weight, historical min-vol, historical max-Sharpe, model-predictive min-vol, model-predictive max-Sharpe) on annualized return, volatility, Sharpe ratio, and max drawdown.

## Live Optimizer page
The most interactive page, lets a user select assets and a risk profile, then builds and backtests a custom portfolio in real time:

- **Risk profile presets** (Conservative, Balanced, Aggressive, or Custom) auto-configure the optimization objective (minimize volatility vs. maximize Sharpe ratio) and the maximum weight allowed per asset
- **Optimization** uses the best individual volatility predictor's forecasts combined with historical asset correlations as the risk model, rather than relying purely on historical volatility
- **Efficient frontier plot** shows the full risk-return tradeoff curve for the selected assets, with the optimized portfolio marked and individual assets shown for context, a direct visualization of Markowitz portfolio theory applied to this project's actual data
- **Backtest** on the 2024+ test period compares the model-predictive portfolio against a historical-weights version, an equal-weight version, and the SPY benchmark, with a cumulative return chart

## Visualization key takeaways

- The efficient frontier and Live Optimizer backtest demonstrate that model-predicted volatility can inform meaningfully different portfolio weightings than historical volatility alone
- The dashboard is built to let a user explore results interactively rather than only reading static tables, particularly through the Prediction Explorer and Live Optimizer pages
- **Limitations:** predictions are based on historical/backtested data and known model limitations; this project is for educational purposes and does not constitute financial advice
