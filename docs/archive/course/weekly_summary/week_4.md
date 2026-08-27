# Week 4 Summary — [7/13 - 7/19]

**Project:** Stock Market Analysis & Portfolio Optimization   
**Team Members:** Danny Eapen, Jeffrey Cheung, Joel Thomas, Samii Shabuse  
## What Each of Us Worked On

**Danny**
- Updated the Linear Regression and Ridge Regression modeling notebooks so they use the expanded FRED macro columns from the shared feature-engineered dataset.
- Reran the linear-model outputs after the new macro data was added, making sure the saved metrics and predictions still followed the same modeling output structure.
- Helped compare how the added macro indicators affected simpler linear models, including noting that adding all FRED columns at once made Linear Regression and Ridge Regression perform worse than the baseline.

**Jeffrey**
- Updated the Random Forest modeling workflow so it uses the new FRED macro features along with the existing market and volatility features.
- Reran the Random Forest model and saved updated metrics/predictions so it could still be compared fairly against the other models.
- Helped keep the Random Forest results connected to the next portfolio step by using its predicted future volatility as one predictive input for portfolio optimization.

**Joel**
- Connected the expanded FRED macro data back into the integrated dataset instead of leaving the extra FRED columns only in the processed source-data folder.
- Added macro/risk indicators such as VIX, 10-year Treasury yield, yield curve spread, inversion flag, Fed funds rate, unemployment rate, and recession flag into the shared daily market/modeling data.
- Helped validate that the integrated and feature-engineered datasets now include the extra FRED columns with clean alignment by date.

**Samii**
- Built out the portfolio optimization notebook so the project can compare portfolio strategies using the model and market outputs.
- Created equal-weight, historical minimum-volatility, historical maximum-Sharpe, Random Forest predictive minimum-volatility, and Random Forest predictive maximum-Sharpe portfolios.
- Evaluated the portfolio strategies on the 2024+ test period using annualized return, annualized volatility, Sharpe ratio, maximum drawdown, and cumulative return, then saved dashboard-ready portfolio output files.

## Decisions Made (as a team)
- We decided to connect Joel's expanded FRED macro indicators into the shared integrated dataset so all modeling notebooks could use the same updated data source.
- We decided to include the new macro columns in the supervised volatility models, while keeping `cpi_index` out of the feature lists because it can behave too much like a hidden date/time indicator.
- We confirmed that Gradient Boosting is currently the strongest model in the model comparison results, but kept Random Forest predictions in the first portfolio optimization workflow as a clear predictive-volatility input.
- We decided to treat SPY as the benchmark instead of allowing it to be included as an optimized portfolio holding.
- We used a time-based evaluation setup where portfolios are built using data before 2024 and evaluated on 2024 and later.

## Blockers / Open Questions
- No major blockers right now.
- We still need to decide whether the final dashboard should use Gradient Boosting predictions, Random Forest predictions, or show both for comparison.
- We still need to test whether all FRED macro features should stay in the final model, since adding every macro column helped some models less than expected and made the linear models worse.
- We need to map the portfolio strategies into simple risk-profile labels such as conservative, balanced, and aggressive for the dashboard/report.

## Next Steps
- Finish the written interpretation for the portfolio optimization notebook.
- Add portfolio visuals, such as strategy weights, cumulative returns, drawdowns, and risk-return comparison charts.
- Prepare the dashboard inputs from the saved model comparison and portfolio optimization output files.
- Begin building the dashboard sections for model results, portfolio allocations, portfolio performance metrics, and benchmark comparison.
- Start drafting the report narrative around the final model results, portfolio results, assumptions, limitations, and educational/non-financial-advice framing.
