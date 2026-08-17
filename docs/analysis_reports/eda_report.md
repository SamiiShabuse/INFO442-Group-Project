# Exploratory Data Analysis Report

**Project:** Stock Market Analysis & Portfolio Optimization
**Date:** July 30, 2026

**Repo:** [GitHub Link](https://github.com/SamiiShabuse/INFO442-Group-Project)

## Introduction

This project builds a portfolio optimization and risk analytics workflow. The goal is to use historical asset returns, volatility, correlations, sector information, and macroeconomic risk indicators to compare portfolio strategies and understand risk-return tradeoffs.

The exploratory data analysis focused on three source datasets:

- Yahoo Finance market data for asset prices and daily returns.
- Wikipedia S&P 500 constituent data for sector and company metadata.
- FRED macroeconomic data for risk-free rates, volatility context, recession flags, and other market environment indicators.

EDA was used to understand the data before modeling and portfolio optimization. The main questions were: what variables are available, whether the data is clean enough to use, how individual variables behave, and how the variables relate to each other.

## EDA Code Files to Attach

The EDA work was completed in the existing Jupyter notebooks below. These should be attached with the report submission:

- `notebooks/01_source_data/yfinance/03_exploratory_data_analysis_yfinance.ipynb`
- `notebooks/01_source_data/wikipedia/03_exploratory_data_analysis_wikipedia.ipynb`
- `notebooks/01_source_data/fred/03_exploratory_data_analysis_fred.ipynb`

## General Description of the Data

The main processed datasets used for EDA and downstream modeling are summarized below.

| Dataset | File | Rows | Columns | Date Range / Scope |
| --- | --- | ---: | ---: | --- |
| Yahoo Finance adjusted close prices | `data/processed/source_data/yfinance/yfinance_adjusted_close_clean.csv` | 2,010 | 22 | 2018-01-02 to 2025-12-30 |
| Yahoo Finance daily returns | `data/processed/source_data/yfinance/yfinance_daily_returns_clean.csv` | 2,009 | 22 | 2018-01-03 to 2025-12-30 |
| Wikipedia S&P 500 constituents | `data/processed/source_data/wikipedia/wikipedia_sp500_constituents_clean.csv` | 503 | 3 | Current S&P 500 constituent table |
| FRED combined macro data | `data/processed/source_data/fred/fred_all_series_combined.csv` | 11,702 | 12 | 1981-09-01 to 2026-07-08 |
| Integrated modeling base dataset | `data/processed/integrated/modeling_base_dataset.csv` | 42,189 | 18 | 2018-01-03 to 2025-12-30 |

The Yahoo Finance datasets include one `Date` column plus 21 asset columns. The asset universe includes individual stocks, ETFs, bond funds, gold exposure, international exposure, and SPY as the benchmark.

The Wikipedia dataset contains categorical metadata:

| Column | Meaning | Type |
| --- | --- | --- |
| `ticker` | Stock ticker symbol | Categorical |
| `company_name` | Company name | Categorical |
| `gics_sector` | S&P 500 sector | Categorical |

The FRED dataset contains mostly numerical macro variables:

| Variable Group | Example Columns | Type |
| --- | --- | --- |
| Interest rates | `risk_free_rate_pct`, `risk_free_rate_decimal`, `fed_funds_rate_pct`, `treasury_10yr_pct` | Numerical |
| Risk regime | `vix`, `yield_curve_spread`, `is_inverted`, `recession_flag` | Numerical / binary |
| Inflation and labor market | `cpi_index`, `cpi_pct_change`, `unemployment_rate_pct` | Numerical |

The integrated modeling dataset combines market data, FRED macro data, and asset metadata. It includes numerical variables such as `adjusted_close`, `daily_return`, `vix`, and interest rates, plus categorical variables such as `ticker`, `company_name`, `gics_sector`, and `asset_type`.

## Data Quality Overview

The processed Yahoo Finance price and return datasets have no missing values and no duplicate rows. The data is aligned by trading date, which is important because portfolio analysis depends on comparing assets across the same dates.

The Wikipedia constituent dataset has no missing values, no duplicate rows, and no duplicate tickers. Some ETF tickers from the portfolio universe do not appear in the Wikipedia table, which is expected because ETFs are not individual S&P 500 companies.

The FRED combined dataset has 2,175 missing values in `vix`. These missing values occur before the FRED VIX series begins in 1990, so they are expected and do not affect the project backtest window from 2018 through 2025. The integrated modeling base dataset has no missing values.

## Univariate Analysis

### Yahoo Finance Market Data

The Yahoo Finance EDA examined each asset individually using cumulative returns, daily return distributions, annualized return, annualized volatility, rolling volatility, and maximum drawdown.

The assets show very different risk and return profiles. Based on average daily returns annualized by 252 trading days, the highest-return assets in the clean return data were:

| Asset | Approx. Annualized Return | Approx. Annualized Volatility |
| --- | ---: | ---: |
| LLY | 38.31% | 31.34% |
| AAPL | 28.73% | 30.80% |
| MSFT | 26.84% | 28.35% |
| CAT | 23.60% | 31.80% |
| AMZN | 23.03% | 34.42% |
| JPM | 20.72% | 29.05% |

The most volatile assets included AMZN, CAT, UNH, LLY, AAPL, and XOM. In contrast, AGG, GLD, TLT, VXUS, KO, and SPY had lower annualized volatility. This supports the idea that the portfolio universe contains a mix of higher-risk growth/equity assets and lower-volatility diversifiers.

Maximum drawdown analysis showed that average return and volatility do not fully explain downside risk. The largest drawdowns included UNH at about -61.39%, XOM at about -61.01%, AMZN at about -56.15%, and TLT at about -48.35%. Lower drawdown assets included AGG at about -18.43% and GLD at about -22.00%.

### Wikipedia Sector Data

The Wikipedia EDA focused on the distribution of S&P 500 companies across sectors. The sector counts are imbalanced:

| Sector | Count |
| --- | ---: |
| Industrials | 81 |
| Financials | 76 |
| Information Technology | 74 |
| Health Care | 59 |
| Consumer Discretionary | 47 |
| Consumer Staples | 34 |
| Utilities | 31 |
| Real Estate | 31 |
| Materials | 26 |
| Communication Services | 23 |
| Energy | 21 |

Industrials, Financials, and Information Technology have the largest number of companies. Energy and Communication Services have fewer companies. This matters because sector-level analysis can reveal whether a portfolio is concentrated in a few parts of the market.

For the project portfolio, the individual stock tickers matched successfully to Wikipedia sector labels. ETF tickers were handled separately with asset type labels such as bonds, gold/commodities, benchmark ETF, and international equity ETF.

### FRED Macro Data

The FRED EDA looked at individual macro variables over time, including rates, VIX, unemployment, CPI change, recession flags, and the yield curve spread.

Across the full FRED combined history, the risk-free rate averaged about 3.83% and ranged from 0.00% to 17.01%. VIX averaged about 19.43 and reached a maximum of 82.69, which captures extreme market stress periods such as the COVID crash. The yield curve spread averaged about 1.53 percentage points and was negative during inversion periods.

The `is_inverted` flag was active for about 11.1% of the FRED history. The recession flag was active for about 9.5% of observations. These variables are useful because they describe broader risk conditions that may affect portfolio performance and volatility.

## Multivariate Analysis

### Asset Correlations and Diversification

The Yahoo Finance correlation matrix showed that some assets move very closely together while others provide diversification. High positive correlations included:

| Pair | Correlation |
| --- | ---: |
| QQQ and SPY | 0.938 |
| MSFT and QQQ | 0.867 |
| SPY and VXUS | 0.861 |
| AGG and TLT | 0.835 |
| AAPL and QQQ | 0.817 |

These high correlations suggest that large-cap equity and broad equity ETF positions may duplicate similar market exposure.

Some correlations were low or negative, especially with long-term Treasury bonds:

| Pair | Correlation |
| --- | ---: |
| JPM and TLT | -0.292 |
| TLT and XOM | -0.235 |
| CAT and TLT | -0.227 |
| LMT and TLT | -0.159 |
| SPY and TLT | -0.151 |

These lower or negative correlations suggest that bond exposure may help reduce portfolio risk during some equity market movements.

### Sector Metadata and Portfolio Diversification

The Wikipedia sector data supports multivariate analysis by connecting tickers to sectors. This allows the project to compare asset performance not only by ticker, but also by sector group.

For example, the portfolio includes technology stocks such as AAPL and MSFT, financial stocks such as JPM and V, health care stocks such as LLY and UNH, and defensive or diversifying exposures such as bond ETFs and gold. This helps evaluate whether optimized portfolios are truly diversified or simply concentrated in a few high-performing sectors.

### FRED Macro Relationships

The FRED correlation analysis showed that several interest-rate variables are redundant. The risk-free rate and fed funds rate had a correlation of about 0.994, and the 10-year Treasury yield had a correlation of about 0.918 with the risk-free rate. This means these variables carry very similar information and should not all be used blindly in a model.

VIX behaved differently from the rate variables. Its absolute correlation with the main rate series was under about 0.12, which suggests it captures a separate form of market risk. VIX was more connected to recession periods, with a correlation of about 0.469 with the recession flag.

The yield curve spread also provided distinct information. It had a moderate positive correlation of about 0.590 with unemployment, which suggests it may help describe changing macro conditions and possible recession risk.

The source-level EDA does not use one final supervised target variable yet. Later modeling notebooks use engineered features to predict market volatility and compare model outputs for portfolio optimization. The EDA findings help decide which variables are useful before those modeling steps.

## Key EDA Findings and How They Inform Later Decisions

The main value of the EDA was identifying which patterns in the data should guide later feature engineering, model selection, and portfolio construction.

| EDA Finding | What We Learned From the Data | Later Project Decision |
| --- | --- | --- |
| Asset returns and volatility vary widely across tickers. | High-return assets such as LLY, AAPL, MSFT, CAT, and AMZN also tend to have higher volatility and drawdown risk. | Portfolio construction should not rank assets by return alone; risk-adjusted metrics and volatility forecasts are needed. |
| Some assets are highly correlated. | QQQ, SPY, MSFT, and AAPL show overlapping market exposure. | Portfolio optimization should account for covariance/correlation so the portfolio is not accidentally concentrated in similar assets. |
| Bonds and defensive assets provide diversification. | TLT and AGG have lower or negative correlations with several equity assets. | Bond ETFs and defensive assets should remain in the asset universe because they may reduce total portfolio volatility. |
| Macro variables capture different risk regimes. | VIX, recession flags, yield curve spread, and unemployment describe market stress differently from asset returns alone. | Macro indicators should be considered as context features for volatility modeling and risk analysis. |
| Some interest-rate variables are redundant. | Risk-free rate, fed funds rate, and 10-year Treasury yield are highly correlated. | Feature selection should avoid blindly including all overlapping rate variables because they may add duplicate information. |
| Sector metadata reveals possible concentration risk. | The portfolio includes assets across technology, financials, health care, energy, bonds, gold, and international exposure. | Later portfolio analysis should check whether optimized portfolios are diversified across sectors and asset types. |

## Hypotheses Generated

Based on the EDA, the team generated the following hypotheses for later modeling and portfolio testing:

- Lower-correlated assets such as bond ETFs, gold, and international ETFs may improve diversification and reduce overall portfolio volatility.
- Assets with high returns may also carry large drawdown risk, so portfolio selection should consider downside risk instead of ranking by return alone.
- Higher VIX periods may align with higher future volatility and weaker portfolio performance.
- Yield curve inversion may be useful as a risk-regime feature because it captures broader macro stress.
- Sector concentration may increase portfolio risk if too much weight is placed in highly correlated sectors.
- A daily time-varying risk-free rate should produce better Sharpe ratio calculations than using one flat average risk-free rate.
- Redundant interest-rate variables may add noise to models, so feature selection should remove or limit overlapping rate columns.

## Data Quality and Cleaning Suggestions

The EDA suggests the following preprocessing decisions:

- Keep the cleaned Yahoo Finance datasets aligned by trading date before calculating returns, correlations, volatility, or portfolio weights.
- Continue checking for missing prices and invalid return values whenever the asset universe changes.
- Use the cleaned Wikipedia ticker format, including the period-to-dash ticker standardization, to avoid merge problems with Yahoo Finance tickers.
- Treat ETF sector mismatches as expected and assign ETF-specific asset type labels instead of forcing ETF tickers into company sector categories.
- Keep FRED series forward-filled to match trading dates, but document which variables are originally monthly versus daily.
- Do not treat pre-1990 VIX missing values as a data error; they are outside the VIX availability range.
- Avoid using all rate variables at once in modeling. The risk-free rate, fed funds rate, and 10-year Treasury yield are highly correlated, so a smaller selected feature set is more defensible.
- Prefer `vix`, `yield_curve_spread`, `is_inverted`, `unemployment_rate_pct`, `recession_flag`, and `cpi_pct_change` as macro context features because they add information beyond raw rate levels.

## Conclusion

The EDA showed that the project data is clean enough for modeling after preprocessing and integration. The market data contains meaningful differences in return, volatility, correlation, and drawdown across assets. The Wikipedia metadata adds sector context for diversification analysis. The FRED data adds macro risk context, but some rate variables are highly redundant and should be handled carefully.

Overall, the EDA supports the next steps of feature engineering, model comparison, and portfolio optimization.
