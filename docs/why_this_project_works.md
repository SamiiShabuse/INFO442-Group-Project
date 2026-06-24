# Project Alignment with INFO 442 Requirements

## Project Name

**Portfolio Optimization & Risk Analytics Dashboard**

## Overview

This project aligns with the INFO 442 final project requirements because it applies a full data science workflow to a real-world finance problem: portfolio construction and risk analysis.

The project is not designed to predict which individual stocks will increase in price. Instead, it uses historical asset data to analyze risk, return, volatility, correlation, and diversification. The final product will be an interactive dashboard that helps users compare portfolio strategies and understand risk-return tradeoffs.

---

## Why This Project Fits the Course Requirements

The course expects teams to choose a real-world domain problem, select a dataset, develop a scientific question with business value, perform exploratory data analysis, build a data science model, evaluate the results, and communicate the findings.

Our project satisfies these requirements in the following ways:

| Course Requirement            | How This Project Fits                                                                                                                         |
| ----------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| **Real-world domain problem** | The project focuses on finance and investment portfolio construction, a practical real-world decision-making problem.                         |
| **Dataset**                   | We will use historical stock and ETF price data from public financial data sources such as Yahoo Finance/yfinance.                            |
| **Scientific question**       | How can historical asset returns, volatility, and correlations be used to construct portfolios that match different investor risk profiles?   |
| **Business value**            | The dashboard helps users understand portfolio risk, diversification, and performance tradeoffs before making allocation decisions.           |
| **Exploratory Data Analysis** | We will analyze return distributions, volatility, correlations, cumulative returns, and drawdowns.                                            |
| **Data science model**        | We will build portfolio optimization models such as equal-weight, minimum-volatility, maximum-Sharpe, and risk-profile-based portfolios.      |
| **Evaluation**                | We will evaluate portfolios using annualized return, volatility, Sharpe ratio, maximum drawdown, cumulative return, and benchmark comparison. |
| **Visualization**             | The project will include charts such as allocation plots, correlation heatmaps, risk-return scatterplots, and backtest performance graphs.    |
| **Deployment / Presentation** | The final product will be presented as an interactive dashboard, likely built with Streamlit, along with a final report and presentation.     |

---

## Main Research Question

**How can historical asset returns, volatility, and correlations be used to construct portfolios that match different investor risk profiles?**

---

## Business Value

Many beginner investors and individual investors struggle to understand portfolio risk. A portfolio can appear attractive based on return alone, but it may also have high volatility, poor diversification, or large drawdowns.

This project provides value by helping users:

* Compare different portfolio strategies
* Understand the tradeoff between risk and return
* See how diversification affects portfolio behavior
* Evaluate portfolios using objective financial metrics
* Learn why historical performance should not be treated as guaranteed future performance

---

## Why This Is a Data Science Project

This project includes the full data science pipeline:

1. **Data Acquisition**
   Collect historical price data for selected stocks and/or ETFs.

2. **Data Preprocessing**
   Clean the data, align trading dates, calculate daily returns, and prepare a complete dataset.

3. **Exploratory Data Analysis**
   Analyze asset behavior using volatility, return distributions, correlations, cumulative returns, and drawdowns.

4. **Modeling**
   Build portfolio construction models, including equal-weight, minimum-volatility, maximum-Sharpe, and risk-profile-based portfolios.

5. **Evaluation**
   Compare portfolio strategies against benchmarks and baselines using financial performance metrics.

6. **Visualization**
   Create an interactive dashboard to communicate portfolio performance, allocation, risk, and diversification.

7. **Deployment and Communication**
   Present the final dashboard, report, and findings to an audience.

---

# Alignment with the 10-Week Course Timeline

## Week 1: Define Goals and Scope

**Course focus:** Define the goals and scope of the data science project and form teams.

**Our project work:**

* Finalize the project idea.
* Define the project scope.
* Decide that the project is a portfolio optimization and risk analytics dashboard.
* Choose the finance domain.
* Decide what the dashboard should help users understand.

**Expected output:**

* Project name
* Problem statement
* Initial research question
* Team roles
* Initial project scope

---

## Week 2: Project Proposal and Data Acquisition

**Course focus:** Select data science questions and hypotheses, begin data acquisition, and submit the project proposal.

**Our project work:**

* Write the formal project proposal.
* Define the main scientific/business question.
* Choose the asset universe, such as 10-20 stocks and/or ETFs.
* Identify data sources such as yfinance/Yahoo Finance.
* Pull sample historical price data.

**Expected output:**

* Project proposal
* Research question
* Hypotheses
* Data source plan
* Initial sample dataset

---

## Week 3: Data Acquisition

**Course focus:** Continue data acquisition.

**Our project work:**

* Collect historical price data for selected assets.
* Collect benchmark data, such as SPY or another market index/ETF.
* Store raw data in CSV files or project data folders.
* Document the data source, time range, and asset list.

**Expected output:**

* Raw historical price dataset
* Benchmark dataset
* Data source documentation

---

## Week 4: Data Preprocessing

**Course focus:** Select data preprocessing and transformations.

**Our project work:**

* Clean missing values.
* Align assets by trading date.
* Calculate daily returns.
* Calculate cumulative returns.
* Prepare data for portfolio modeling.
* Create reusable preprocessing scripts or notebooks.

**Expected output:**

* Cleaned dataset
* Preprocessing notebook/script
* Data dictionary
* Summary of cleaning decisions

---

## Week 5: Data Formatting and Complete Dataset

**Course focus:** Format the data and complete the dataset.

**Our project work:**

* Finalize the complete dataset.
* Calculate features such as annualized return, annualized volatility, covariance, and correlation.
* Build data tables needed for EDA and modeling.
* Confirm the asset universe and time range will not change unless necessary.

**Expected output:**

* Complete modeling-ready dataset
* Feature-engineered dataset
* Correlation/covariance matrices
* Final asset list

---

## Week 6: Exploratory Data Analysis

**Course focus:** Perform exploratory data analysis.

**Our project work:**

* Analyze individual asset performance.
* Create return distribution charts.
* Create volatility comparison charts.
* Create cumulative return charts.
* Create correlation heatmaps.
* Identify diversification patterns and asset relationships.

**Expected output:**

* EDA notebook
* EDA charts
* Key findings from the data
* Initial insights for portfolio construction

---

## Week 7: Build Data Science Models

**Course focus:** Build data science models.

**Our project work:**

* Build baseline equal-weight portfolio.
* Build minimum-volatility portfolio.
* Build maximum-Sharpe portfolio.
* Build risk-profile-based portfolios, such as conservative, balanced, and aggressive.
* Apply allocation constraints to keep results realistic.

**Expected output:**

* Portfolio optimization models
* Baseline portfolio
* Risk-profile portfolios
* Model implementation notebook/script

---

## Week 8: Visualization and Evaluation

**Course focus:** Visualize and evaluate data science models, and practice storytelling with data.

**Our project work:**

* Evaluate each portfolio strategy.
* Compare optimized portfolios against baselines.
* Calculate annualized return, annualized volatility, Sharpe ratio, maximum drawdown, and cumulative return.
* Build visuals showing portfolio performance over time.
* Start turning technical results into a clear story.

**Expected output:**

* Backtesting results
* Performance comparison table
* Portfolio evaluation charts
* Draft dashboard visuals

---

## Week 9: Documentation and Curation

**Course focus:** Document and curate the data science project.

**Our project work:**

* Polish the GitHub repository.
* Write the README.
* Document the data pipeline.
* Document modeling choices and limitations.
* Build and polish the Streamlit dashboard.
* Prepare final report sections.

**Expected output:**

* Updated README
* Project documentation
* Dashboard draft
* Final report draft
* Clean repository structure

---

## Week 10: Final Presentation, Deployment, Report

**Course focus:** Present the project and submit deployment, report, and presentation.

**Our project work:**

* Finalize the interactive dashboard.
* Finalize the report.
* Prepare the final presentation.
* Present the problem, data, EDA, models, evaluation, dashboard, limitations, and future work.

**Expected output:**

* Final dashboard
* Final report
* Final presentation
* Final GitHub repository

---

# Final Project Scope

To keep the project realistic for a 10-week class, the project will focus on:

* 10-20 stocks and/or ETFs
* 5-10 years of historical price data
* Daily returns and portfolio metrics
* Equal-weight, minimum-volatility, maximum-Sharpe, and risk-profile portfolios
* Benchmark comparison
* Interactive Streamlit dashboard
* Clear educational disclaimer

---

# What We Will Not Do

To keep the project manageable and academically responsible, we will not focus on:

* Predicting exact future stock prices
* Giving real investment advice
* Building a live trading bot
* Managing real money
* Using personal financial data
* Guaranteeing future portfolio performance
* Overcomplicating the model with unnecessary deep learning

---

# Final Verdict

This project fits the INFO 442 final project requirements because it uses a real-world finance problem, public data, exploratory analysis, modeling, evaluation, visualization, and deployment.

It also fits the 10-week timeline because each course deliverable maps naturally to a stage of the project:

**proposal → data acquisition → preprocessing → complete dataset → EDA → modeling → visualization/evaluation → documentation → deployment/presentation**

The project should be framed as a **portfolio optimization and risk analytics dashboard**, not as a stock-picking or investment advice tool.
