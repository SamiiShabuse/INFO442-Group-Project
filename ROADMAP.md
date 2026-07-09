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

## Week 2: Proposal, Data Acquisition, and Preprocessing

**Goal:** Finalize the proposal, collect the raw datasets, and clean/preprocess each source dataset.

**Status:** Complete.

| Team Member | Tasks |
|---|---|
| Data Lead | Finalized the asset universe across equities, sectors, bonds, gold/commodities, international exposure, and SPY as the benchmark. Pulled and cleaned historical price and volume data with `yfinance`. |
| EDA/Feature Lead | Defined the planned features for each asset and completed initial EDA for the `yfinance` data, including returns, cumulative returns, daily returns, and visual checks. |
| Modeling Lead | Defined the first predictive model approach and collected/cleaned FRED risk-free rate and CPI data for later Sharpe ratio and macro context. |
| Dashboard/Documentation Lead | Finalized the project proposal, research question, business value sections, and source-specific README notes. Helped document and organize the `yfinance`, Wikipedia, and FRED workflows. |

**Standup update examples:**

- We selected our first asset universe and benchmark.
- We collected raw market data, sector/category data, and FRED data.
- We cleaned and preprocessed the individual source datasets.
- We finalized the predictive modeling and portfolio comparison plan.
- We separated the data work into `yfinance`, Wikipedia, and FRED workflows.

---

## Week 3: Data Integration Validation and Data Dictionary

**Goal:** Validate the combined dataset, confirm the join logic, and document the final integrated data structure.

| Team Member | Tasks |
|---|---|
| Data Lead | Validate the integrated dataset shape, date range, ticker coverage, and missing values after combining all sources. |
| EDA/Feature Lead | Confirm that sector/category labels cover all selected assets, including ETFs and assets outside the S&P 500 table. |
| Modeling Lead | Confirm that benchmark returns, risk-free rate, and CPI are aligned correctly with trading dates and do not create duplicate columns. |
| Dashboard/Documentation Lead | Create or update the data dictionary for the integrated dataset, including column names, join keys, and known limitations. |

**Standup update examples:**

- We combined the market, sector/category, and FRED datasets.
- We checked missing values, duplicate columns, and date alignment across all sources.
- We documented the integrated dataset columns and join logic.

---

## Week 4: Feature Engineering and Exploratory Data Analysis

**Goal:** Create model-ready features and use EDA to check whether the features make sense.

| Team Member | Tasks |
|---|---|
| Data Lead | Fix any data issues discovered during feature engineering or EDA. |
| EDA/Feature Lead | Create model features such as rolling returns, rolling volatility, moving averages, volume changes, recent drawdown, and benchmark correlation. |
| Modeling Lead | Define the target variable for prediction, such as future realized volatility over a set window, and review feature patterns. |
| Dashboard/Documentation Lead | Add the strongest EDA charts and feature explanations to the report/dashboard draft. |

**Standup update examples:**

- We created the first modeling features.
- We found patterns in volatility, correlations, and sector/category exposure.
- We chose the first set of features and the prediction target.

---

## Week 5: Predictive Modeling

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

## Week 6: Portfolio Optimization and Evaluation

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

## Week 7: Dashboard Build

**Goal:** Build the first usable dashboard version for exploring model and portfolio results.

| Team Member | Tasks |
|---|---|
| Data Lead | Make sure final data files load correctly into the dashboard. |
| EDA/Feature Lead | Prepare clean charts for returns, risk, correlations, and sector/category exposure. |
| Modeling Lead | Prepare model and portfolio result tables for dashboard display. |
| Dashboard/Documentation Lead | Build dashboard sections for inputs, portfolio allocation, model results, strategy comparison, and project explanation. |

**Standup update examples:**

- We built the first working dashboard version.
- We added charts and tables for portfolio comparison.
- We connected the final data/model outputs to the dashboard.

---

## Week 8: Report and Project Polish

**Goal:** Polish the dashboard, report, README, and project narrative.

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

## Week 9: Final Presentation Preparation

**Goal:** Prepare the dashboard demo, report, slides, and final explanation for each project area.

| Team Member | Tasks |
|---|---|
| Data Lead | Prepare a short explanation of the data sources, cleaning, preprocessing, and integration decisions. |
| EDA/Feature Lead | Prepare a short explanation of the feature engineering and EDA findings. |
| Modeling Lead | Prepare a short explanation of the predictive model, portfolio optimization, evaluation metrics, and limitations. |
| Dashboard/Documentation Lead | Prepare the final dashboard demo, final report, final slides, and submission checklist. |

**Standup update examples:**

- We finalized the dashboard demo plan.
- We completed the final report and slides.
- Each person prepared their section for the final presentation.

---

## Week 10: Final Submission and Buffer

**Goal:** Finish any last fixes, rehearse the presentation, and submit the final project.

| Team Member | Tasks |
|---|---|
| Data Lead | Double-check that the final data files and notebooks are reproducible. |
| EDA/Feature Lead | Double-check final charts and make sure they match the report/dashboard narrative. |
| Modeling Lead | Double-check final model and portfolio results, assumptions, and limitations. |
| Dashboard/Documentation Lead | Submit the final dashboard, report, slides, README, and any required class materials. |

**Standup update examples:**

- We fixed final issues from review or rehearsal.
- We submitted the final project materials.
- We confirmed the repo is clean and easy to understand.

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
