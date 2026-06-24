# Project Roadmap

## Format

This is suppose to mimic a real-world project roadmap. To help everyone on the team this is the format
for the Senior Project roadmap. Each week has a goal, a table of tasks for each team member, and examples of what to report during the weekly standup.

## Team Structure

This roadmap is designed so all 4 team members have something to work on each week and something clear to report during weekly standups.

This is going to mimic how Senior Project will be done in the real world, where each person has a main area of responsibility but can help others as needed.

Team Roles:

- **Team Member 1: Data Lead** - data collection, cleaning, and preprocessing
- **Team Member 2: EDA Lead** - exploratory analysis, charts, and findings
- **Team Member 3: Modeling Lead** - portfolio strategies and evaluation metrics
- **Team Member 4: Dashboard/Documentation Lead** - Web dashboard, README, report, and presentation materials

Roles can rotate if needed, but each person should own one main area so the work is easier to track.

---

## Week 1: Project Setup and Scope

**Goal:** Agree on the project direction and make sure everyone understands the problem.

| Team Member | Tasks |
|---|---|
| Data Lead | Research possible financial data sources such as Yahoo Finance/yfinance. Make a first draft list of possible stocks/ETFs. |
| EDA Lead | Research useful portfolio analysis charts, such as return charts, volatility charts, and correlation heatmaps. |
| Modeling Lead | Research portfolio strategies: equal-weight, minimum volatility, and maximum Sharpe ratio. |
| Dashboard/Documentation Lead | Organize the GitHub repo and make sure the README/project proposal clearly explains the project. |

**Standup update examples:**

- We decided on the main project idea.
- We identified likely data sources.
- We started researching the main analysis and modeling methods.

---

## Week 2: Proposal and Data Plan

**Goal:** Finalize the project proposal and decide what data will be used.

| Team Member | Tasks |
|---|---|
| Data Lead | Finalize the asset list, likely 10-15 stocks/ETFs. Test pulling sample historical data. |
| EDA Lead | Define the key EDA questions, such as which assets are most volatile or most correlated. |
| Modeling Lead | Define which portfolio models will be included in the first version. |
| Dashboard/Documentation Lead | Finalize the proposal document and update the README with the project scope. |

**Standup update examples:**

- We selected our first asset universe.
- We tested that the data source works.
- We finalized the main research question and project scope.

---

## Week 3: Data Acquisition

**Goal:** Collect the raw historical price data.

| Team Member | Tasks |
|---|---|
| Data Lead | Pull historical price data for all selected assets and the benchmark, such as SPY. Save raw data files. |
| EDA Lead | Inspect the raw data for missing values, date ranges, and obvious data issues. |
| Modeling Lead | Decide what return and risk metrics the models will need. |
| Dashboard/Documentation Lead | Start documenting the data source, asset list, date range, and benchmark choice. |

**Standup update examples:**

- We collected the first raw dataset.
- We checked for missing or incomplete data.
- We documented where the data came from.

---

## Week 4: Data Cleaning and Preprocessing

**Goal:** Turn raw price data into clean data that can be used for analysis.

| Team Member | Tasks |
|---|---|
| Data Lead | Clean and align the data by trading date. Calculate daily returns. |
| EDA Lead | Create initial summary statistics for each asset. |
| Modeling Lead | Check that the return data is usable for portfolio calculations. |
| Dashboard/Documentation Lead | Document the preprocessing steps and cleaning decisions. |

**Standup update examples:**

- We cleaned the historical price data.
- We calculated daily returns.
- We created the first summary statistics.

---

## Week 5: Complete Dataset and Feature Engineering

**Goal:** Finalize the dataset for EDA and modeling.

| Team Member | Tasks |
|---|---|
| Data Lead | Finalize the cleaned dataset and save it in the project folder. |
| EDA Lead | Calculate asset-level metrics such as annualized return and volatility. |
| Modeling Lead | Create covariance and correlation matrices needed for optimization. |
| Dashboard/Documentation Lead | Create a simple data dictionary explaining each file and column. |

**Standup update examples:**

- We finalized the modeling-ready dataset.
- We created annualized return and volatility features.
- We created the covariance and correlation matrices.

---

## Week 6: Exploratory Data Analysis

**Goal:** Understand the assets and find patterns in the data.

| Team Member | Tasks |
|---|---|
| Data Lead | Support any data fixes discovered during EDA. |
| EDA Lead | Create EDA visuals: cumulative return chart, volatility comparison, correlation heatmap, and risk-return scatterplot. |
| Modeling Lead | Review EDA findings and identify how they affect portfolio construction. |
| Dashboard/Documentation Lead | Add EDA charts and findings to the report/dashboard draft. |

**Standup update examples:**

- We created the main EDA charts.
- We found which assets were most volatile and most correlated.
- We started connecting EDA findings to portfolio strategy.

---

## Week 7: Portfolio Modeling

**Goal:** Build the first working portfolio strategies.

| Team Member | Tasks |
|---|---|
| Data Lead | Make sure the model input data is clean and reusable. |
| EDA Lead | Help interpret how the portfolio allocations relate to the data patterns. |
| Modeling Lead | Build equal-weight, minimum-volatility, maximum-Sharpe, and risk-profile portfolios. |
| Dashboard/Documentation Lead | Start adding portfolio allocation outputs to the dashboard. |

**Standup update examples:**

- We built the equal-weight portfolio.
- We built the first optimized portfolio models.
- We started showing portfolio allocations in the dashboard.

---

## Week 8: Evaluation and Visualization

**Goal:** Compare portfolio strategies and make the results understandable.

| Team Member | Tasks |
|---|---|
| Data Lead | Verify that benchmark data is included correctly. |
| EDA Lead | Create comparison visuals for portfolio performance over time. |
| Modeling Lead | Calculate evaluation metrics: annualized return, volatility, Sharpe ratio, max drawdown, and cumulative return. |
| Dashboard/Documentation Lead | Build dashboard sections for strategy comparison and metric tables. |

**Standup update examples:**

- We compared the portfolio strategies against a benchmark.
- We calculated the main performance metrics.
- We added comparison visuals to the dashboard.

---

## Week 9: Dashboard, Report, and Polish

**Goal:** Turn the analysis into a polished final product.

| Team Member | Tasks |
|---|---|
| Data Lead | Clean up data files and make sure the project can be rerun. |
| EDA Lead | Finalize EDA findings and choose the strongest charts for the report. |
| Modeling Lead | Finalize model explanations, assumptions, and limitations. |
| Dashboard/Documentation Lead | Polish the Streamlit dashboard, README, and final report draft. |

**Standup update examples:**

- We cleaned up the repo and data files.
- We finalized the main charts and model results.
- We polished the dashboard and report draft.

---

## Week 10: Final Presentation and Submission

**Goal:** Finish the dashboard, report, and presentation.

| Team Member | Tasks |
|---|---|
| Data Lead | Prepare a short explanation of the dataset and preprocessing. |
| EDA Lead | Prepare a short explanation of the main EDA findings. |
| Modeling Lead | Prepare a short explanation of the portfolio models and evaluation results. |
| Dashboard/Documentation Lead | Prepare the final dashboard demo and organize final submission materials. |

**Standup update examples:**

- We finalized the dashboard.
- We completed the report and slides.
- Each person prepared their section for the final presentation.

---

## Final Deliverables

By the end of the project, the team should have:

- Cleaned historical asset price dataset
- EDA notebook or script
- Portfolio modeling notebook or script
- Evaluation metrics and comparison results
- Streamlit dashboard
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

