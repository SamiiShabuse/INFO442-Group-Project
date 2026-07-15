# Data Acquisition & Preprocessing

This document summarizes how our team acquired and cleaned the data used in this project. Full implementation details, code, and comments are in the corresponding Jupyter notebooks under `notebooks/`.

## Overview

**Team Members:** Danny Eapen, Jeffrey Cheung, Joel Thomas, Samii Shabuse

Our project pulls data from three sources:

| Data Source | Notebooks Location |
|---|---|
| S&P 500 constituents (Wikipedia) | `notebooks/s&p500_wikipedia_dataset/` |
| Historical stock prices (Yahoo Finance) | `notebooks/yfinance_dataset/` |
| Macroeconomic & risk-free rate data (FRED) | `notebooks/fred_dataset/` |

All three pipelines follow the same structure: **01 - Acquisition → 02 - Preprocessing → 03 - EDA**. Outputs are then combined into an integrated modeling dataset (`notebooks/04_data_integration.ipynb`) and engineered into model-ready features (`notebooks/05_feature_engineer.ipynb`).

---

## 1. S&P 500 Constituents (Wikipedia)

**What it is:** The current list of S&P 500 companies with ticker, company name, and GICS sector, used to map our asset universe to sector categories.

**Acquisition:**
- Pulled directly from the [Wikipedia S&P 500 companies page](https://en.wikipedia.org/wiki/List_of_S%26P_500_companies) using `requests` + `pandas.read_html`
- Narrowed the full table down to the three columns needed: `ticker`, `company_name`, `gics_sector`
- Note: some tickers in our asset universe (SPY, QQQ, AGG, GLD, VNQ, VXUS) are ETFs, not individual companies, so they don't appear in this Wikipedia table and are handled separately during integration

**Preprocessing:**
- Checked for missing values and duplicate tickers (found none — table was clean structurally)
- Fixed ticker formatting inconsistencies: Wikipedia uses periods (e.g. `BRK.B`) while Yahoo Finance uses dashes (e.g. `BRK-B`) — converted periods to dashes so tickers would match correctly when merged with price data
- Stripped extraneous whitespace from ticker, company name, and sector fields as a safety check against silent merge mismatches
- Verified the number of unique sectors as a final consistency check

**Outputs:**
- Raw: `data/raw/wikipedia/wikipedia_sp500_constituents.csv`
- Processed: `data/processed/source_data/wikipedia/wikipedia_sp500_constituents_clean.csv`

---

## 2. Historical Stock Prices (Yahoo Finance)

**What it is:** Historical daily price data (2018–2025) for a diversified ~20-asset universe (stocks, ETFs, bonds, gold/commodities, international exposure) plus SPY as a benchmark, used to compute returns, volatility, and correlations for portfolio optimization.

**Acquisition:**
- Pulled via the `yfinance` package for a fixed list of tickers (e.g. AAPL, MSFT, LLY, UNH, JPM, V, XOM, PG, KO, CAT, LMT, plus ETFs QQQ, VNQ, VXUS, TLT, AGG, GLD) over 2018-01-01 to 2025-12-31
- Verified no tickers were missing adjusted close data after download
- Computed normalized price growth (indexed to $1 invested) and daily returns (`pct_change()`) to make assets comparable despite different price levels
- Generated an initial correlation heatmap and annualized return/volatility summary as a first look at the risk-return tradeoff across assets

**Preprocessing:**
- Reloaded raw price data with a proper datetime index for time-series work
- Checked for missing values (found none) and dropped any rows with missing adjusted close prices to keep all assets aligned on the same trading dates
- Recomputed daily returns from the cleaned price data and checked for infinite/invalid values
- Calculated a final processed summary (mean daily return, daily volatility, annualized return, annualized volatility) per asset

**Outputs:**
- Raw: `data/raw/yfinance/` — `yfinance_market_data.csv`, `yfinance_adjusted_close_prices.csv`, `yfinance_daily_returns_initial.csv`, initial summary stats
- Processed: `data/processed/source_data/yfinance/` — `yfinance_adjusted_close_clean.csv`, `yfinance_daily_returns_clean.csv`, `yfinance_processed_summary_stats.csv`

---

## 3. Macroeconomic & Risk-Free Rate Data (FRED)

**What it is:** Risk-free rate and macro context data needed for Sharpe ratio calculations and risk regime analysis.

**Acquisition:** Pulled directly from the FRED API using the `fredapi` Python package. Seven series were retrieved:

| Series ID | Description |
|---|---|
| DGS3MO | 3-Month Treasury Yield (risk-free rate) |
| CPIAUCSL | Consumer Price Index |
| VIXCLS | CBOE Volatility Index (VIX) |
| DGS10 | 10-Year Treasury Yield |
| FEDFUNDS | Federal Funds Rate |
| UNRATE | Unemployment Rate |
| USREC | NBER Recession Indicator |

**Preprocessing:**
- Forward-filled gaps in daily series (FRED doesn't publish rates on weekends/holidays)
- Converted the risk-free rate to decimal form for Sharpe ratio calculations
- Computed the yield curve spread (10-year minus 3-month yield) and an inversion flag
- Forward-filled monthly series (CPI, Fed funds, unemployment, recession flag) to daily frequency
- Aligned all series to a common trading-date index

**Key EDA findings:**
- The risk-free rate and Fed funds rate are almost perfectly correlated (0.99) — only one should be used as a model feature to avoid redundancy
- The yield curve inverted 11.1% of the time historically, and every recession in the dataset was preceded by an inversion — a potentially useful leading indicator
- VIX correlates weakly with all rate-based series, meaning it captures distinct risk information rather than duplicating what's already in the rate data
- During our backtest window, the risk-free rate swung from ~0% (2015–2021) to ~5.3% (2023–2024), so we use the daily time-varying rate rather than a flat average in Sharpe ratio calculations

**Outputs:**
- Raw: `data/raw/fred/` (one CSV per series)
- Processed: `data/processed/fred/` (cleaned individual series + `fred_all_series_combined.csv`)

---

## 4. Data Integration & Feature Engineering

Once all three sources were cleaned, they were combined and prepared for modeling:

- **`notebooks/04_data_integration.ipynb`** — merges Wikipedia sector data, yfinance price/return data, and FRED macro data into unified datasets: `daily_market_data.csv`, `asset_metadata.csv`, and `modeling_base_dataset.csv` (in `data/processed/integrated/`), and checks for alignment issues, missing values, and sector/category coverage
- **`notebooks/05_feature_engineer.ipynb`** — builds model-ready features from the integrated dataset, saved to `data/processed/features/feature_engineered_dataset.csv`


