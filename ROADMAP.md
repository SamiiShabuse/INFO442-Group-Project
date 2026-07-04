# Project Roadmap

## Format

This is supposed to mimic a real-world project roadmap. To help everyone on the team this is the format
for the Senior Project roadmap. Each week has a goal, a table of tasks for each team member, and examples of what to report during the weekly standup.

## Team Structure

This roadmap is designed so all 4 team members have something to work on each week and something clear to report during weekly standups.

This is going to mimic how Senior Project will be done in the real world, where each person has a main area of responsibility but can help others as needed.

Team Roles:

- **Team Member 1: Data Lead** - data collection, cleaning, preprocessing, and data files
- **Team Member 2: EDA/Feature Lead** - exploratory analysis, feature engineering, and visual findings
- **Team Member 3: Modeling Lead** - volatility prediction, portfolio optimization, and evaluation metrics
- **Team Member 4: Dashboard/Documentation Lead** - dashboard, README, report, slides, and project organization

---

## Week 1: Project Setup and Scope

**Goal:** Agree on the updated project idea and make sure everyone understands the predictive portfolio scope.

**Status:** Complete.

| Team Member | Tasks |
|---|---|
| Data Lead | Researched possible data sources: `yfinance`, Wikipedia S&P 500 table, and FRED. Drafted the first list of possible stocks/ETFs. |
| EDA/Feature Lead | Researched useful features for volatility prediction, such as rolling returns, rolling volatility, moving averages, volume changes, and benchmark correlation. |
| Modeling Lead | Researched basic volatility prediction methods and portfolio strategies: equal-weight, minimum volatility, maximum Sharpe, and risk-profile portfolios. |
| Dashboard/Documentation Lead | Updated the README/project docs so the project is clearly framed as predictive portfolio optimization, not financial advice. |

**Standup update examples:**

- We updated the project scope to include future volatility prediction.
- We identified the main data sources: Yahoo Finance, Wikipedia, and FRED.
- We started researching features, models, and portfolio strategies.
- We set up the project folder structure and notebook organization.

---

## Week 2: Proposal and Data Plan

**Goal:** Finalize the proposal and decide exactly what data will be collected.

**Status:** Complete.

| Team Member | Tasks |
|---|---|
| Data Lead | Finalized the asset universe across equities, sectors, bonds, gold/commodities, international exposure, and SPY as the benchmark. Tested pulling price data with `yfinance`. |
| EDA/Feature Lead | Defined the planned features for each asset, including returns, rolling volatility, moving averages, volume changes, benchmark comparison, and drawdowns. |
| Modeling Lead | Defined the first predictive model approach and the portfolio strategies that will be compared. |
| Dashboard/Documentation Lead | Finalized the project proposal, research question, business value sections, and source-specific README notes. |

**Standup update examples:**

- We selected our first asset universe and benchmark.
- We tested the market data source.
- We finalized the predictive modeling and portfolio comparison plan.
- We separated the data work into `yfinance`, Wikipedia, and FRED workflows.

---

## Week 3: Data Acquisition

**Goal:** Finish validating the raw data workflows and make sure each source can be rerun cleanly.

| Team Member | Tasks |
|---|---|
| Data Lead | Confirm the `yfinance` acquisition notebook, final ticker list, date range, benchmark, and raw output files. |
| EDA/Feature Lead | Confirm the Wikipedia acquisition notebook and identify which selected assets need manual sector/category labels because they are ETFs or not in the S&P 500 table. |
| Modeling Lead | Confirm the FRED acquisition notebook and make sure the risk-free rate and CPI files are saved with clear column names. |
| Dashboard/Documentation Lead | Document each data source, date range, ticker list, generated file name, and why each source is being used. |

**Standup update examples:**

- We validated the raw market dataset and benchmark.
- We added sector/category data for diversification analysis.
- We confirmed the FRED risk-free rate and CPI data sources.

---

## Week 4: Data Cleaning and Preprocessing

**Goal:** Finish cleaning each source and lock the rules for combining them.

| Team Member | Tasks |
|---|---|
| Data Lead | Confirm price data, adjusted close data, daily returns, and missing-value handling for the market data. |
| EDA/Feature Lead | Check whether the sector/category data matches the selected tickers and flag any missing labels or ETF categories. |
| Modeling Lead | Align FRED data with trading dates and decide how to forward-fill monthly or daily macro values. |
| Dashboard/Documentation Lead | Document cleaning decisions, folder structure, and a first data dictionary for raw, processed, and integrated files. |

**Standup update examples:**

- We cleaned and aligned the historical price data.
- We calculated daily returns.
- We decided how to align sector, CPI, and risk-free rate data with the market data.

---

## Week 5: Data Integration and Complete Dataset

**Goal:** Build and validate the combined dataset before adding modeling features.

| Team Member | Tasks |
|---|---|
| Data Lead | Finalize cleaned source files and make sure the source notebooks can be rerun without overwriting the wrong files. |
| EDA/Feature Lead | Validate the integrated dataset shape, ticker coverage, sector/category coverage, and missing values. |
| Modeling Lead | Confirm that benchmark returns, risk-free rate, and CPI are aligned correctly with trading dates. |
| Dashboard/Documentation Lead | Update documentation to explain the integrated dataset, columns, join keys, and remaining limitations. |

**Standup update examples:**

- We created the first integrated dataset.
- We checked missing values and date alignment across all sources.
- We documented the columns and join logic.

---

## Week 6: Feature Engineering and Exploratory Data Analysis

**Goal:** Create model-ready features and use EDA to check whether the features make sense.

| Team Member | Tasks |
|---|---|
| Data Lead | Fix any data issues discovered during EDA. |
| EDA/Feature Lead | Create model features such as rolling returns, rolling volatility, moving averages, volume changes, recent drawdown, and benchmark correlation. |
| Modeling Lead | Define the target variable for prediction, such as future realized volatility over a set window, and review feature patterns. |
| Dashboard/Documentation Lead | Add the strongest EDA charts and feature explanations to the report/dashboard draft. |

**Standup update examples:**

- We created the first modeling features.
- We found patterns in volatility, correlations, and sector/category exposure.
- We chose the first set of features and the prediction target.

---

## Week 7: Predictive Modeling

**Goal:** Build and evaluate the first future volatility prediction model.

| Team Member | Tasks |
|---|---|
| Data Lead | Prepare train/test datasets using a time-based split. |
| EDA/Feature Lead | Help inspect feature importance or model behavior, if available. |
| Modeling Lead | Train the first regression model to predict future realized volatility. Evaluate it using MAE and RMSE. |
| Dashboard/Documentation Lead | Start documenting the model method, inputs, target variable, and evaluation results. |

**Standup update examples:**

- We created a time-based train/test split.
- We trained the first volatility prediction model.
- We evaluated the model using MAE and RMSE.

---

## Week 8: Portfolio Optimization and Evaluation

**Goal:** Use predicted volatility in portfolio construction and compare against baselines.

| Team Member | Tasks |
|---|---|
| Data Lead | Verify that cleaned returns, benchmark data, sector labels, and risk-free rate data are ready for evaluation. |
| EDA/Feature Lead | Create visuals comparing portfolio allocations, sector exposure, and performance over time. |
| Modeling Lead | Build equal-weight, historical minimum-volatility, predictive minimum-volatility, maximum-Sharpe, and risk-profile portfolios. Calculate annualized return, volatility, Sharpe ratio, max drawdown, and cumulative return. |
| Dashboard/Documentation Lead | Build dashboard sections for portfolio allocation, model results, and strategy comparison tables. |

**Standup update examples:**

- We connected predicted volatility to the portfolio optimization step.
- We compared predictive portfolios against equal-weight and benchmark baselines.
- We calculated the main portfolio evaluation metrics.

---

## Week 9: Dashboard, Report, and Polish

**Goal:** Turn the analysis into a polished final product.

| Team Member | Tasks |
|---|---|
| Data Lead | Clean up data files, scripts, and folders so the project is easy to rerun. |
| EDA/Feature Lead | Finalize the strongest EDA and feature visuals for the report and presentation. |
| Modeling Lead | Finalize model results, portfolio comparison results, assumptions, and limitations. |
| Dashboard/Documentation Lead | Polish the dashboard, README, final report draft, and presentation outline. |

**Standup update examples:**

- We cleaned up the repo and data pipeline.
- We finalized the main charts, model results, and portfolio comparison.
- We polished the dashboard and report draft.

---

## Week 10: Final Presentation and Submission

**Goal:** Finish the dashboard, report, slides, and final submission.

| Team Member | Tasks |
|---|---|
| Data Lead | Prepare a short explanation of the data sources, cleaning, and preprocessing. |
| EDA/Feature Lead | Prepare a short explanation of the feature engineering and EDA findings. |
| Modeling Lead | Prepare a short explanation of the predictive model, portfolio optimization, evaluation metrics, and limitations. |
| Dashboard/Documentation Lead | Prepare the final dashboard demo, final report, final slides, and submission checklist. |

**Standup update examples:**

- We finalized the dashboard.
- We completed the final report and slides.
- Each person prepared their section for the final presentation.

---

## Final Deliverables

By the end of the project, the team should have:

- Raw and cleaned market data
- Sector data for diversification analysis
- Risk-free rate data for Sharpe ratio calculations
- Feature-engineered modeling dataset
- EDA notebook or script
- Volatility prediction model
- Portfolio optimization notebook or script
- Evaluation metrics for predictive model and portfolio strategies
- Streamlit dashboard or interactive dashboard
- Final README/documentation
- Final report
- Final presentation slides

---

## Weekly Standup Template

Each person should be able to answer:

1. What did I work on this week?
2. What did I finish or make progress on?
3. What am I working on next?
4. Am I blocked by anything?
