# Week 1 Summary — [6/29 - 7/5]

**Project:** Stock Market Analysis & Portfolio Optimization   
**Team Members:** Danny Eapen, Jeffrey Cheung, Joel Thomas, Samii Shabuse  
## What Each of Us Worked On

**Danny**
- Built the data acquisition pipeline pulling S&P 500 company data from Wikipedia, including tickers, sector, and sub industry info
- Aligned the asset list with Jeffrey's finalized universe so our datasets matched up
- Cleaned and preprocessed the data (missing values, date formatting) and ran EDA to check quality before passing it along

**Jeffrey**
- Finalized project architecture: a three-layer system — (1) regression model to predict per-asset volatility, (2) portfolio optimization across risk profiles using PyPortfolioOpt, (3) backtesting against SPY, equal-weight, min-vol, and max-Sharpe benchmarks
- Researched and finalized asset universe (~20 stocks/ETFs + SPY as benchmark), revising for better sector balance — trimmed Mag7 concentration (kept AAPL/MSFT only), reclassified AMZN under consumer discretionary, added V, KO, VZ for financials/staples/communications coverage
- Considered a crash/dip classification model as an alternative framing; deprioritized as a stretch goal due to deadline risk and added complexity (class imbalance, look-ahead bias)

**Joel**
- Built the FRED data acquisition workflow for macroeconomic data, including CPI and risk-free rate data
- Created preprocessing notebooks and processed output files for the FRED datasets so they can be used with the market data
- Added FRED EDA work to inspect the data, understand trends, and identify how the macro data should be aligned with trading dates

**Samii**
- Built the yfinance workflow, including data acquisition, preprocessing, and exploratory analysis for the selected stocks/ETFs and SPY benchmark
- Generated and organized the yfinance raw and processed files, including adjusted close prices, daily returns, summary statistics, correlation outputs, and drawdown outputs
- Combined the yfinance, Wikipedia, and FRED datasets into integrated output files and checked alignment, missing values, sector/category coverage, and final dataset structure

## Decisions Made (as a team)
- We finalized a diversified asset universe using stocks, ETFs, bonds, gold/commodities, international exposure, and SPY as the benchmark
- We decided to use three main data sources: yfinance for market data, Wikipedia for S&P 500 sector/company metadata, and FRED for CPI/risk-free rate data
- We organized the project into source-specific notebook folders and data folders so each dataset can be developed separately and then combined into one integrated dataset

## Blockers / Open Questions
- Need to finish reviewing the integrated dataset to confirm there are no duplicate CPI/risk-free columns or unexpected missing values
- Need to confirm final sector/category labels for ETFs and assets that do not map directly to the Wikipedia S&P 500 table
- Need to decide the exact target variable and feature windows for the first volatility prediction model

## Next Steps
- Finalize the integrated dataset and data dictionary so everyone understands the columns, joins, and assumptions
- Start feature engineering for rolling returns, rolling volatility, moving averages, drawdowns, benchmark correlation, and other modeling features
- Prepare the first modeling dataset and begin defining the train/test split for volatility prediction
