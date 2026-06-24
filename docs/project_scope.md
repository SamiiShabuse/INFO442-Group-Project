# Data Science Project Scoping Worksheet

## 1. Project Name

**Portfolio Optimization & Risk Analytics Dashboard**

---

## 2. Organization Name

**INFO 442 Project Team**

Optional project organization name: **FinSight Analytics**

---

## 3. Problem Description

### 3.1 What is the problem you are facing?

Many individual investors struggle to build portfolios that match their risk tolerance. Investors often focus only on high-return assets without understanding volatility, drawdowns, diversification, or how assets move together. This can lead to portfolios that are too risky, poorly diversified, or not aligned with the investor’s goals.

Our project addresses this problem by building a data-driven portfolio optimization and risk analytics dashboard. The dashboard will use historical asset price data to construct and compare different portfolio strategies, including equal-weight portfolios, minimum-volatility portfolios, maximum-Sharpe portfolios, and risk-profile-based portfolios.

### 3.2 Who/what is affected by this problem?

This problem affects individual investors, beginner investors, students, and small financial advisory teams who need better tools to understand portfolio risk and return. It also affects anyone trying to make investment allocation decisions without access to professional portfolio analytics tools.

### 3.3 How many people/organizations/places/etc. and how much are they affected?

Millions of individual investors participate in financial markets through retirement accounts, brokerage accounts, and investment apps. Poor portfolio allocation can lead to unnecessary losses, excessive volatility, and portfolios that do not match the investor’s risk tolerance.

For this project, we will measure the impact using portfolio-level metrics such as annualized return, annualized volatility, Sharpe ratio, maximum drawdown, and cumulative return. These metrics will show how different portfolio strategies perform compared to simple baselines.

### 3.4 Why is solving this problem a priority for your organization?

This is a priority because portfolio construction is a real-world financial decision-making problem. A data-driven dashboard can help users understand the tradeoff between risk and return before making investment decisions. For our team, this project is valuable because it applies data science techniques to a practical finance problem involving data acquisition, preprocessing, exploratory analysis, optimization, evaluation, visualization, and deployment.

---

## 4. Goals

| # | Goal                                                                                                             | Constraints                                                                                                                    |
| - | ---------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| 1 | Help users understand portfolio risk and return tradeoffs using historical data.                                 | Historical data does not guarantee future performance. The project must avoid presenting outputs as financial advice.          |
| 2 | Build portfolio strategies for different investor risk profiles, such as conservative, balanced, and aggressive. | Risk profiles must be simplified for the class project and based on measurable portfolio metrics like volatility and drawdown. |
| 3 | Compare optimized portfolios against simple baselines such as equal-weight and benchmark portfolios.             | The analysis depends on available historical price data, selected assets, and chosen time period.                              |

---

## 5. Actions

### Action 1: Generate a Portfolio Allocation

| Field                                                   | Response                                                                                                                                                        |
| ------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Action**                                              | Generate a portfolio allocation based on a user-selected risk profile.                                                                                          |
| **Who is executing the action?**                        | The dashboard/system, used by an investor, student, or analyst.                                                                                                 |
| **Who/what is the action being taken on?**              | A selected universe of stocks and/or ETFs.                                                                                                                      |
| **How often is the decision to take this action made?** | Whenever a user wants to create or compare portfolio allocations.                                                                                               |
| **What channels are/can be used to take this action?**  | Interactive web dashboard, likely built with Streamlit.                                                                                                         |
| **Other useful information about the action**           | The allocation will be based on historical return, volatility, and correlation data. It is for educational purposes only and does not provide financial advice. |

### Action 2: Compare Portfolio Strategies

| Field                                                   | Response                                                                                                                          |
| ------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| **Action**                                              | Compare multiple portfolio strategies using risk and return metrics.                                                              |
| **Who is executing the action?**                        | The project dashboard/system and project team.                                                                                    |
| **Who/what is the action being taken on?**              | Portfolio strategies such as equal-weight, minimum-volatility, maximum-Sharpe, conservative, balanced, and aggressive portfolios. |
| **How often is the decision to take this action made?** | Whenever new assets, time periods, or risk profiles are selected.                                                                 |
| **What channels are/can be used to take this action?**  | Dashboard visualizations, final report, and final presentation.                                                                   |
| **Other useful information about the action**           | Comparison metrics will include annualized return, annualized volatility, Sharpe ratio, maximum drawdown, and cumulative return.  |

### Action 3: Identify Diversification Opportunities

| Field                                                   | Response                                                                                                         |
| ------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| **Action**                                              | Identify diversification opportunities using asset correlation and risk analysis.                                |
| **Who is executing the action?**                        | The dashboard/system and users reviewing the analysis.                                                           |
| **Who/what is the action being taken on?**              | Assets in the selected portfolio universe.                                                                       |
| **How often is the decision to take this action made?** | During portfolio construction or portfolio review.                                                               |
| **What channels are/can be used to take this action?**  | Correlation heatmaps, risk-return scatterplots, and dashboard charts.                                            |
| **Other useful information about the action**           | This action helps users understand whether their portfolio is overly concentrated in assets that move similarly. |

---

## 6. Data

### 6A. What data sources do you have internally?

Since this is a class project, we likely do not have private/internal organizational data. We will mainly use external/public financial data.

| Field                                       | Data Source 1                                                                         | Data Source 2                                                                           | Data Source 3                                                                            |
| ------------------------------------------- | ------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| **Name**                                    | Project-generated portfolio dataset                                                   | User-selected risk profile inputs                                                       | Portfolio performance results                                                            |
| **What does it contain?**                   | Cleaned historical asset prices, returns, volatility, correlations, covariance matrix | Conservative/balanced/aggressive risk profile selections and optional asset preferences | Generated allocations, returns, volatility, Sharpe ratio, drawdown, benchmark comparison |
| **What level of granularity?**              | Daily asset-level data                                                                | User/session-level input                                                                | Portfolio-level output                                                                   |
| **How frequently is it collected/updated?** | Once during project development or refreshed when data is pulled                      | Whenever user interacts with dashboard                                                  | Whenever portfolio is generated                                                          |
| **Does it have reliable identifiers?**      | Yes, ticker symbols and dates                                                         | No personal identifiers needed                                                          | Portfolio strategy names and timestamps                                                  |
| **Who’s the internal owner of the data?**   | INFO 442 project team                                                                 | INFO 442 project team                                                                   | INFO 442 project team                                                                    |
| **How is it stored?**                       | CSV files, pandas DataFrames, or local project files                                  | Dashboard/session variables                                                             | CSV files, dashboard output, or generated reports                                        |
| **Additional comments**                     | No sensitive personal data should be collected.                                       | Risk profile inputs are simplified and educational.                                     | Results are analytical, not investment advice.                                           |

---

### 6B. What data can you get from external, private, or public sources?

| Field                                       | Data Source 1                                                                     | Data Source 2                                                   | Data Source 3                                                                                   |
| ------------------------------------------- | --------------------------------------------------------------------------------- | --------------------------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| **Name**                                    | Yahoo Finance historical market data via yfinance                                 | Benchmark index data                                            | Asset category/sector data                                                                      |
| **Link**                                    | https://ranaroussi.github.io/yfinance/                                            | https://finance.yahoo.com/quote/SPY/history/                    | Manually created mapping table or financial API metadata                                        |
| **What does it contain?**                   | Daily open, high, low, close, adjusted close, and volume for selected ETFs/stocks | Historical benchmark prices such as S&P 500 or total market ETF | Asset class or sector labels such as equity, bond, technology, real estate, gold, international |
| **What level of granularity?**              | Daily asset-level time series                                                     | Daily benchmark-level time series                               | Asset-level metadata                                                                            |
| **How frequently is it collected/updated?** | Daily in real markets; for class project, pulled once or periodically             | Daily in real markets; pulled once or periodically              | Static or occasionally updated                                                                  |
| **Does it have unique identifiers?**        | Yes, ticker symbol and date                                                       | Yes, benchmark ticker and date                                  | Yes, ticker symbol                                                                              |
| **Who’s the internal owner of the data?**   | External financial data provider/API                                              | External financial data provider/API                            | External financial data provider/API or manually created by team                                |
| **How is it stored?**                       | API endpoint, CSV, or pandas DataFrame                                            | API endpoint, CSV, or pandas DataFrame                          | CSV or manually created mapping table                                                           |
| **Additional comments**                     | We may use yfinance or another public financial data source.                      | Benchmark comparison helps evaluate portfolio strategies.       | Sector/category data helps explain diversification.                                             |

---

### 6C. In an ideal world, is there additional data you would want to get/gather?

In an ideal world, we would want access to investor-specific data such as age, income, investment horizon, financial goals, risk tolerance surveys, current portfolio holdings, and liquidity needs. We would also want macroeconomic indicators such as inflation, interest rates, unemployment, and market regime data to improve portfolio recommendations.

However, for this class project, we will avoid collecting personal financial information and focus on historical asset behavior.

---

### 6D. What analysis will the existing data not support?

The existing data will not support guaranteed future performance predictions. Historical prices can show past returns, volatility, correlations, and drawdowns, but they cannot prove how a portfolio will perform in the future.

The data also will not support personalized financial advice because we are not collecting detailed personal financial information from users. The project can support educational portfolio simulation and risk analysis, but not real investment recommendations.

---

## 7. Analysis

| Field                                         | Analysis 1                                                                                                                                  | Analysis 2                                                                                                                                | Analysis 3                                                                                                                                |
| --------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| **Analysis type**                             | Description / Exploratory Data Analysis                                                                                                     | Optimization                                                                                                                              | Evaluation / Backtesting                                                                                                                  |
| **Purpose of the analysis**                   | Understand historical asset behavior, including returns, volatility, correlations, and drawdowns.                                           | Construct portfolios based on different objectives such as minimum volatility, maximum Sharpe ratio, and risk profiles.                   | Compare portfolio strategies against baselines and benchmarks using performance metrics.                                                  |
| **Which action will this analysis inform?**   | Helps users understand which assets are risky, diversified, or highly correlated.                                                           | Informs portfolio allocation generation.                                                                                                  | Informs whether optimized portfolios perform better than simple baselines.                                                                |
| **How will you validate this analysis?**      | Validate calculations by checking return formulas, missing data, and summary statistics. Compare visual patterns with known asset behavior. | Compare optimized portfolios against equal-weight and benchmark portfolios. Apply realistic constraints such as max allocation per asset. | Use historical backtesting. Metrics include annualized return, annualized volatility, Sharpe ratio, max drawdown, and cumulative return.  |
| **What limitations will this analysis have?** | EDA is descriptive and does not prove causation.                                                                                            | Optimization may overfit historical data and may be sensitive to the selected time period.                                                | Backtesting is based on historical data and does not guarantee future results. Transaction costs and taxes may be simplified or excluded. |

---

## 8. Ethical Considerations

### Privacy

This project will not use personally identifiable information. We will not collect names, addresses, account balances, brokerage information, income, or real investor holdings. User inputs will be limited to general risk profile selections such as conservative, balanced, or aggressive.

### Transparency

Users and stakeholders should know that this project is educational and analytical. The dashboard should clearly explain what data is used, what assumptions are made, how portfolios are constructed, and what limitations exist. The final dashboard should include a disclaimer that the project does not provide financial advice.

### Discrimination/Equity

Because the project does not use personal demographic data, direct demographic discrimination risk is low. However, simplified risk profiles may not represent all investor circumstances equally. Different people may have different financial goals, time horizons, obligations, and risk capacities. The project should avoid implying that one portfolio is universally best for all users.

### Social Licence

If the public found out about this project, it would likely be acceptable as long as it is clearly framed as an educational data science tool and not as financial advice. The project should be transparent about limitations and avoid misleading users into thinking the model can guarantee investment success.

### Accountability

The INFO 442 project team is responsible for data collection, analysis, dashboard development, ethical framing, and final presentation. The team should ensure that outputs are communicated responsibly and that the dashboard includes appropriate limitations and disclaimers.

### Other Considerations

The project should comply with the terms of use of any financial data source used. Since the dashboard is not a licensed investment advisor, it should not provide personalized investment advice or tell users to buy/sell specific assets. It should be presented as a simulation and educational analytics project.

---

## 9. Field Trial or Randomized Controlled Trial

A field trial could be designed with students or beginner investors as participants. Participants would be split into two groups:

### Baseline Group

Receives simple portfolio information, such as asset returns and an equal-weight portfolio.

### Treatment Group

Uses the portfolio optimization and risk analytics dashboard.

### Outcomes Measured

The trial would measure whether the dashboard improves users’ understanding of portfolio risk and diversification. Outcomes could include:

* Ability to identify high-risk portfolios
* Ability to explain diversification
* Ability to compare risk-adjusted returns
* Confidence in interpreting portfolio metrics
* Quality of selected portfolio based on stated risk tolerance

The trial could run over one class session or one week. Since this is a class project, the field trial may be proposed rather than fully executed.

---

## 10. External Organizations and Internal Departments

| Organization/Department     | Description of Desired Involvement                                                             | Name/Role of Counterpart                                |
| --------------------------- | ---------------------------------------------------------------------------------------------- | ------------------------------------------------------- |
| INFO 442 Project Team       | Responsible for data collection, preprocessing, modeling, dashboard, report, and presentation. | Project team members                                    |
| Course Instructor           | Provides project guidance, feedback, and grading.                                              | Dr. Lei Wang                                            |
| Financial Data Provider/API | Provides historical asset and benchmark data.                                                  | yfinance or similar public data source                  |
| Potential Users/Testers     | Provide feedback on dashboard usability and clarity.                                           | Students, classmates, or beginner investors             |
| IT/Deployment Platform      | Hosts or runs the dashboard.                                                                   | Streamlit Community Cloud, GitHub, or local environment |

---

## Project Disclaimer

This project is for educational and analytical purposes only. It does not provide financial advice, investment recommendations, or instructions to buy or sell specific securities. Historical performance does not guarantee future results.
