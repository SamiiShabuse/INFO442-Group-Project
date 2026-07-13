# Week 3 Summary — [7/6 - 7/12]

**Project:** Stock Market Analysis & Portfolio Optimization   
**Team Members:** Danny Eapen, Jeffrey Cheung, Joel Thomas, Samii Shabuse  
## What Each of Us Worked On

**Danny**
- Helped reorganize the model and project structure so the work is easier to follow across the team: source data, integrated data, feature data, and model results now have clearer folders and documentation.
- Helped align the integrated dataset structure with the modeling workflow, making sure the cleaned Yahoo Finance, Wikipedia, and FRED data could move cleanly into feature engineering and model output folders.
- Supported the team in organizing the data properly so future dashboard, reporting, and portfolio optimization work can use the same shared files instead of each person relying on separate notebook outputs.

**Jeffrey**
- Built the Random Forest modeling notebook (`02_random_forest.ipynb`): trained a pooled model across all 21 tickers to predict future 20-day realized volatility, tuned max_depth and min_samples_leaf with GridSearchCV + TimeSeriesSplit (time-based CV to avoid look-ahead bias), and evaluated on a held-out 2024+ test set.
- Established a persistence baseline (predict future volatility = current volatility) and showed the tuned Random Forest clearly beats it (test R2 0.34 vs ~0.00, MAE 19% lower), setting up a fair side-by-side comparison with the linear regression model — same dataset, split date, and metrics.

**Joel**
- Expanded the FRED data pipeline beyond the initial CPI and risk-free rate work by adding macro/risk indicators such as VIX, the 10-year Treasury yield, yield curve spread, recession flag, Fed funds rate, and unemployment rate.
- Finalized the FRED acquisition, preprocessing, and EDA workflow so the team has raw files, processed files, and exploratory checks for how macro conditions relate to market risk and volatility.
- Reorganized the FRED notebooks and data outputs to better match the team folder conventions, making it easier to connect the macro data with the shared integration and modeling pipeline.

**Samii**
- Built three volatility modeling notebooks: Linear Regression, Gradient Boosting, and Ridge Regression. Each model used the shared feature-engineered dataset to predict future 20-day realized volatility and saved comparable metrics/predictions to the modeling output folders.
- Established a baseline comparison using current rolling volatility and showed the Linear Regression and Ridge Regression models performed similarly and beat the baseline (R2 about 0.297, MAE about 0.00394 vs baseline MAE about 0.00465).
- Added Gradient Boosting as a non-linear comparison model and documented the results, giving the team a broader model set to compare against Jeffrey's Random Forest before deciding which approach is best for the dashboard and portfolio work.

## Decisions Made (as a team)
- We pivoted more clearly toward volatility prediction as the main modeling task, using future 20-day realized volatility as the target instead of trying to directly predict stock prices or short-term returns.
- We decided to keep a shared modeling structure where all models read from `data/processed/features/feature_engineered_dataset.csv` and write metrics/predictions to `data/processed/modeling/<model_name>/`.
- We agreed that model comparison should use the same baseline, train/test setup, and metrics so Linear Regression, Ridge, Gradient Boosting, and Random Forest can be evaluated fairly.

## Blockers / Open Questions
- No major blockers right now.
- We still need to choose the final model or model comparison story for the dashboard and final report.
- We need to confirm which macro/FRED features should stay in the final model so the model is useful without adding unnecessary complexity (maybe).

## Next Steps
- Compare all model results side by side and decide which model should drive the portfolio optimization workflow.
- Connect model outputs to the next portfolio construction step, especially minimum-volatility and risk-profile portfolios.
- Start preparing dashboard-ready tables and visuals for model performance, volatility predictions, and portfolio results.
