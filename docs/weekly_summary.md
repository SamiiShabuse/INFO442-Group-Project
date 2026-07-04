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
- Item
- Item

**Shabuse**
- Item
- Item

## Decisions Made (as a team)
- 

## Blockers / Open Questions
- 

## Next Steps
- 
