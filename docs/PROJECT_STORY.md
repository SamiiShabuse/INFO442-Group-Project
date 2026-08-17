## **Who We Are**

We're four students with backgrounds in computer science and data science, brought together by a shared interest in finance and a genuine passion for the markets. None of us came into this as finance professionals; we came in as students who noticed something frustrating: the tools that actually manage risk well, the kind institutional investors and high-net-worth clients get from a financial advisor, are locked behind minimum account sizes, advisory fees, and assumed expertise most people don't have.

We wanted to build something that pushes back on that. Not another stock-picking app, but a real attempt to take a piece of what institutional finance already knows; that risk-adjusted, macro-aware portfolio construction beats guessing; and put a working version of it in the hands of someone who's never sat across from a financial advisor in their life. Democratizing that kind of tooling, instead of reserving it for institutions, is the "why" behind everything that follows.

## **The Problem We Set Out to Solve**

Every individual investor faces the same unsolved question institutions pay quants millions to answer: *how much risk am I actually taking, and is it the right amount for the world we're in right now?*

Most retail portfolio tools give you a pie chart and call it a day. They don't tell you that a 60/40 stock-bond split means something completely different in a near-zero-rate world than it does when the Fed is aggressively hiking. They don't warn you when the yield curve; one of the most reliable recession signals in modern financial history; is quietly inverting underneath your portfolio. We wanted to build something smarter: a system that doesn't just optimize a portfolio once, but understands the macroeconomic weather it's optimizing *in*.

That became our founding thesis: build a pipeline that treats market risk and macro risk as one connected problem, not two separate afterthoughts.

## **Building the Foundation**

Every real product starts with unglamorous infrastructure work, and ours was no exception. We split into three data pipelines, each solving a different piece of the puzzle:

* **Market data** (Yahoo Finance): historical prices for a deliberately diversified \~20-asset universe spanning stocks, ETFs, bonds, gold, and international exposure, plus SPY as our north-star benchmark  
* **Company metadata** (Wikipedia): sector classifications, so our optimizer could reason about diversification, not just raw numbers  
* **Macroeconomic context** (FRED): starting with just the risk-free rate and CPI, this pipeline grew into seven full series: the risk-free rate, inflation, market volatility (VIX), the 10-year Treasury yield, a derived yield curve spread, the Federal Funds rate, unemployment, and an official NBER recession flag

Getting these three pipelines talking to each other cleanly; matching trading calendars, handling frequency mismatches between daily stock data and monthly macro releases, resolving real merge conflicts as the team's folder structure evolved; was its own small engineering saga. But by the end, we had something most retail tools don't: a single integrated dataset where market behavior and macro conditions live side by side, ready to be modeled together.

## **The Insight Nobody Expected**

Early exploratory analysis on the FRED data surfaced something we didn't anticipate: the risk-free rate and the Federal Funds rate were correlated at 0.994; essentially redundant. More interestingly, the yield curve had inverted before *every single recession* in our dataset's history. We weren't just collecting macro data anymore; we were finding signal in it.

That signal became the seed of our modeling strategy: instead of predicting stock returns directly (a notoriously hard, near-random problem), we'd predict volatility, a much more tractable target, and feed macro context in as features, hypothesizing that a model aware of the yield curve, VIX, and recession risk could out-predict one that only looked at price history.

## **The Pivot**

Here's where the story gets honest, because real building involves real setbacks.

We trained five models; Linear Regression, Ridge Regression, Random Forest, Gradient Boosting, and a GARCH statistical baseline; to predict each asset's 20-day forward volatility. When we threw the full macro feature set at every model, something surprising happened: our simplest models, Linear and Ridge Regression, got *worse* than doing nothing at all. Their R² dropped to \-0.184, actively underperforming a naive "assume tomorrow looks like today" baseline.

This could have been a dead end. Instead, it became our pivot moment. We ran a dedicated feature selection experiment, testing market-only features, the full macro set, and a curated 5-variable macro subset against each other; cross-validated with three independent statistical ranking methods. The result: trimming the macro feature set down to the variables that actually mattered (VIX, the yield curve spread, the inversion flag, unemployment, and inflation) rescued the linear models, pushing their R² back up to roughly 0.31. Meanwhile, our tree-based models, Random Forest and Gradient Boosting, had barely noticed the extra noise in the first place, and Random Forest emerged as our strongest predictor overall, with an R² of 0.339.

The lesson we shipped with: more data isn't automatically better data. Knowing what to leave out turned out to be as important as what we put in.

## **Shipping the Product**

A model living in a Jupyter notebook isn't a product, it's a proof of concept. So we built one: a live, interactive dashboard where the whole pipeline comes together, designed to be usable by someone with zero background in quantitative finance.

A user can walk through our model comparison results, explore predicted-versus-actual volatility for any asset, and then step into the centerpiece: the Live Optimizer. Pick a risk profile, Conservative, Balanced, Aggressive, or fully custom, and the system builds a real portfolio in real time, using Random Forest's predicted volatility (not just historical volatility) as its risk model. It then plots the full efficient frontier, the exact curve Harry Markowitz described in 1952, with your optimized portfolio marked as a star against every asset in the universe. Finally, it backtests that portfolio against a historical-weights version, an equal-weight version, and SPY itself, over real 2024-2025 market data.

This is the moment the whole pipeline, three data sources, five models, one pivot, and a lot of git merge conflicts, became something a person could actually use. No account minimum, no advisory fee, no assumed background in finance required to click through it and understand what it's telling you.

## **Where We Go From Here**

If this were a real company, the roadmap writes itself: rerun the linear models on their best-known feature set so every notebook tells the same honest story, expand the asset universe, layer in the recession flag as a portfolio regime-switcher rather than just a chart annotation, and eventually let users stress-test their portfolio against specific historical macro regimes, 2008, 2020, 2022, on demand.

The bigger version of this project is one where the barrier to entry keeps shrinking: more asset classes, more transparency into *why* the model recommends what it recommends, and eventually, a tool that genuinely competes with what a paid advisor offers — just without the account minimum standing in the way.

## **The Honest Part**

This project is built for learning, not for managing anyone's actual money. Our best model still leaves the majority of volatility unexplained (R² 0.339 means roughly two-thirds of what drives future volatility is outside what we can currently predict). Every number in this dashboard comes from historical backtesting, and historical performance is not a promise about the future. We built this to understand portfolio theory and machine learning more deeply, and to prove to ourselves that institutional-grade portfolio tooling doesn't have to stay institutional; not to replace a financial advisor.

