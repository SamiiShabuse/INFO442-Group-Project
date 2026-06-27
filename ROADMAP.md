# Project Roadmap

## Format

This is suppose to mimic a real-world project roadmap. To help everyone on the team this is the format
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

| Team Member | Tasks |
|---|---|
| Data Lead | Research possible data sources: `yfinance`, Wikipedia S&P 500 table, and FRED. Draft a first list of possible stocks/ETFs. |
| EDA/Feature Lead | Research useful features for volatility prediction, such as rolling returns, rolling volatility, moving averages, volume changes, and benchmark correlation. |
| Modeling Lead | Research basic volatility prediction methods and portfolio strategies: equal-weight, minimum volatility, maximum Sharpe, and risk-profile portfolios. |
| Dashboard/Documentation Lead | Update the README/project docs so the project is clearly framed as predictive portfolio optimization, not financial advice. |

**Standup update examples:**

- We updated the project scope to include future volatility prediction.
- We identified the main data sources: Yahoo Finance, Wikipedia, and FRED.
- We started researching features, models, and portfolio strategies.

---

## Week 2: Proposal and Data Plan

**Goal:** Finalize the proposal and decide exactly what data will be collected.

| Team Member | Tasks |
|---|---|
| Data Lead | Finalize the asset universe, likely 10-15 stocks/ETFs plus a benchmark such as SPY. Test pulling sample price data with `yfinance`. |
| EDA/Feature Lead | Define the planned features for each asset, including returns, rolling volatility, moving averages, volume changes, and drawdowns. |
| Modeling Lead | Define the first predictive model approach and the portfolio strategies that will be compared. |
| Dashboard/Documentation Lead | Finalize the project proposal, research question, and business value sections. |

**Standup update examples:**

- We selected our first asset universe and benchmark.
- We tested the market data source.
- We finalized the predictive modeling and portfolio comparison plan.

---

## Week 3: Data Acquisition

**Goal:** Collect the raw data needed for prices, sectors, benchmark comparison, and risk-free rate.

| Team Member | Tasks |
|---|---|
| Data Lead | Pull historical daily price and volume data for selected assets and SPY. Start saving raw data files. |
| EDA/Feature Lead | Pull or prepare sector labels from Wikipedia/S&P 500 data for diversification analysis. |
| Modeling Lead | Pull or identify FRED risk-free rate data, such as 3-month Treasury yield, for Sharpe ratio calculations. |
| Dashboard/Documentation Lead | Document each data source, date range, ticker list, and why each source is being used. |

**Standup update examples:**

- We collected the first raw market dataset.
- We added sector data for diversification analysis.
- We identified the risk-free rate source for Sharpe ratio calculations.

---

## Week 4: Data Cleaning and Preprocessing

**Goal:** Clean the raw data and prepare it for feature engineering.

| Team Member | Tasks |
|---|---|
| Data Lead | Clean price data, align trading dates, handle missing values, and calculate daily returns. |
| EDA/Feature Lead | Check whether the sector data matches the selected tickers and flag any missing labels. |
| Modeling Lead | Align risk-free rate data with trading dates and decide how to handle different data frequencies. |
| Dashboard/Documentation Lead | Document cleaning decisions and create a simple data dictionary draft. |

**Standup update examples:**

- We cleaned and aligned the historical price data.
- We calculated daily returns.
- We started aligning sector and risk-free rate data with the market data.

---

## Week 5: Feature Engineering and Complete Dataset

**Goal:** Build the modeling-ready dataset.

| Team Member | Tasks |
|---|---|
| Data Lead | Finalize cleaned data files and make sure the data pipeline can be rerun. |
| EDA/Feature Lead | Create model features such as rolling returns, rolling volatility, moving averages, volume changes, recent drawdown, and benchmark correlation. |
| Modeling Lead | Define the target variable for prediction, such as future realized volatility over a set window. |
| Dashboard/Documentation Lead | Update documentation to explain the final dataset, columns, features, and target variable. |

**Standup update examples:**

- We created the modeling-ready dataset.
- We engineered features for volatility prediction.
- We defined the future volatility target variable.

---

## Week 6: Exploratory Data Analysis

**Goal:** Understand the assets, features, and relationships before modeling.

| Team Member | Tasks |
|---|---|
| Data Lead | Fix any data issues discovered during EDA. |
| EDA/Feature Lead | Create EDA visuals: cumulative returns, volatility comparison, correlation heatmap, sector breakdown, and risk-return scatterplot. |
| Modeling Lead | Review feature patterns and decide which features should be used in the first predictive model. |
| Dashboard/Documentation Lead | Add the strongest EDA charts and findings to the report/dashboard draft. |

**Standup update examples:**

- We created the main EDA visuals.
- We found patterns in volatility, correlations, and sector exposure.
- We chose the first set of features for prediction.

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

