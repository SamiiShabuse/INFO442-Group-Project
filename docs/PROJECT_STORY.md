## **Who We Are**

We're four students with backgrounds in computer science and data science,
brought together by a shared interest in finance and a genuine passion for the
markets. None of us came into this as finance professionals; we came in as
students who noticed something frustrating: the tools that manage risk well,
the kind institutional investors and high-net-worth clients get from a
financial advisor, are often locked behind minimum account sizes, advisory
fees, and assumed expertise most people do not have.

We wanted to build something that pushes back on that. Not another
stock-picking app, but a real attempt to take a piece of what institutional
finance already knows, that risk-aware portfolio construction beats guessing,
and put a working version of it in the hands of someone who's never sat across
from a financial advisor in their life. Democratizing that kind of tooling,
instead of reserving it for institutions, is the "why" behind everything that
follows.

## **The Problem We Set Out To Solve**

Every individual investor faces the same difficult question institutions pay
quants to answer: *how much risk am I actually taking, and is it the right
amount for the world we're in right now?*

Most retail portfolio tools give you a pie chart and call it a day. They do
not tell you that a 60/40 stock-bond split means something very different in a
near-zero-rate world than it does when the Fed is aggressively hiking. They do
not warn you when the yield curve, one of the most watched recession signals in
modern financial history, is quietly inverting underneath your portfolio. We
wanted to build something smarter: a system that treats market risk and macro
risk as one connected problem, not two separate afterthoughts.

## **Building The Foundation**

Every real product starts with unglamorous infrastructure work, and ours was no
exception. We split into three data pipelines, each solving a different piece
of the puzzle:

- **Market data** (Yahoo Finance): historical prices for a diversified
  roughly 20-asset universe spanning stocks, ETFs, bonds, gold, and
  international exposure, plus SPY as the benchmark.
- **Company metadata** (Wikipedia): sector classifications, so the optimizer
  could reason about diversification, not just raw numbers.
- **Macroeconomic context** (FRED): risk-free rate, inflation, VIX, the
  10-year Treasury yield, a yield-curve spread, Federal Funds rate,
  unemployment, and a recession indicator.

Getting those pipelines to talk to each other cleanly was its own engineering
saga: matching trading calendars, handling frequency mismatches between daily
stock data and monthly macro releases, and resolving folder-structure drift as
the team worked in parallel. By the end, we had a single integrated dataset
where market behavior and macro conditions live side by side.

## **The Modeling Pivot**

Early exploratory analysis on the FRED data surfaced something useful: several
rate features were highly redundant, while indicators like VIX and the
yield-curve spread looked more directly connected to market risk. That shaped
our modeling strategy. Instead of predicting stock returns directly, which is a
notoriously noisy target, we predicted each asset's future 20-trading-day
volatility.

We trained Linear Regression, Ridge Regression, Random Forest, Gradient
Boosting, and a SPY-only GARCH baseline. When the full macro feature set was
added blindly, the simpler linear models got worse. That pushed us into a
feature-selection experiment across market-only features, the full macro set,
and a curated macro subset.

The lesson was simple: more data is not automatically better data. Knowing what
to leave out mattered as much as what we kept.

## **The Clean Result**

The Random Forest workflow now uses a leakage-safe holdout split. Training rows
whose 20-day target windows cross the January 1, 2024 split are purged before
holdout fitting, and the notebook-facing predictions are regenerated from that
same corrected workflow.

In the definitive predictive-vs-historical experiment, the refreshed Random
Forest improves pooled 20-day volatility forecast MAE from 0.00469 for a
trailing-volatility baseline to 0.00412, about 12.2% lower error. Its pooled R2
is 0.286 versus 0.0075 for the baseline, and it has lower per-ticker RMSE for
17 of 21 tickers.

The honest portfolio conclusion is more nuanced. The RF risk model is a better
volatility forecaster and is better calibrated than the matched historical risk
model, but that does not automatically translate into better portfolio returns.
In the rebalance-frequency sweep, the RF predictive risk model produced lower
realized volatility at 3 of 6 tested frequencies, and it did not reliably
improve Sharpe ratio.

## **Shipping The Product**

A model living in a Jupyter notebook is not a product, so we built a live,
interactive dashboard where the pipeline comes together. A user can walk
through model comparison results, explore predicted-versus-actual volatility
for any asset, review the predictive-vs-historical experiment, and use a Live
Optimizer that builds a portfolio from Random Forest predicted volatility and
historical correlations.

The deployed dashboard is here:

```text
https://portfolio-volatility-optimizer.streamlit.app/
```

The dashboard plots the efficient frontier, marks the optimized portfolio, and
backtests the selected allocation against historical and equal-weight versions
over real 2024-2025 market data.

## **Where We Go From Here**

If this became a larger product, the roadmap would be clear: refresh every
model under the same leakage-safe target-window rules, expand the asset
universe, add transaction costs, layer in macro-regime stress tests, and give
users more transparency into why the optimizer recommends a given allocation.

## **The Honest Part**

This project is built for learning, not for managing anyone's actual money.
Even the refreshed Random Forest leaves most volatility unexplained, which is
normal for noisy financial time-series work. Every number in this dashboard
comes from historical backtesting, and historical performance is not a promise
about the future. We built this to understand portfolio theory and machine
learning more deeply, not to replace a financial advisor.
