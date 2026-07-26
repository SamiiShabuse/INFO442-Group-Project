# Week 5 Summary - [7/20 - 7/26]

**Project:** Stock Market Analysis & Portfolio Optimization   
**Team Members:** Danny Eapen, Jeffrey Cheung, Joel Thomas, Samii Shabuse  
## What Each of Us Worked On

**Danny**
- Worked on the Streamlit dashboard setup and helped connect the dashboard to the cleaned project outputs.
- Helped make the dashboard easier to use by connecting model comparison results, prediction outputs, and portfolio strategy outputs into one interactive interface.
- Helped update dashboard wording and structure so the dashboard reflects the newest model results after feature selection.

**Jeffrey**
- Worked on feature analysis to help decide which market and FRED macro features should stay in the modeling pipeline.
- Helped evaluate feature importance and redundancy so the team could avoid keeping every macro column automatically.
- Helped connect the feature selection work back to the modeling story, especially showing that selected features improved tree-based models like Random Forest.

**Joel**
- Worked on the Streamlit dashboard prototype so the project has an interactive way to present model and portfolio results.
- Added dashboard sections for overview, model comparison, prediction exploration, and portfolio strategies.
- Helped turn the saved CSV outputs from the modeling and portfolio notebooks into dashboard-ready visuals and tables.

**Samii**
- Worked on feature analysis and helped combine the selected feature work back into the modeling pipeline.
- Connected `selected_features.csv` into the main modeling notebooks so Linear Regression, Ridge Regression, Random Forest, and Gradient Boosting use the same shared feature list.
- Reran the modeling notebooks, model comparison notebook, and portfolio optimization notebook so the saved outputs reflect the selected feature set.

## Decisions Made (as a team)
- We decided that feature selection should become the single source of truth for the main tabular modeling notebooks instead of each model keeping its own hardcoded feature list.
- We decided to keep GARCH separate because it is SPY-only and does not use the tabular selected feature columns.
- We confirmed that Random Forest is now the strongest all-ticker volatility model after using the selected feature list.
- We decided to rerun portfolio optimization after updating Random Forest predictions so the portfolio results match the newest model outputs.
- We connected the Streamlit dashboard to the real model comparison, prediction, and portfolio output files so it can be used for presentation.

## Blockers / Open Questions
- No major blockers right now.
- We still need to do a final visual walkthrough of the Streamlit dashboard before presenting it.
- We may still want to explain clearly why Random Forest is the best predictive model but Historical Max Sharpe is still the best risk-adjusted portfolio strategy.
- We need to decide how much technical feature-selection detail should go into the final presentation versus the written report.

## Next Steps
- Use the updated Week 6 analysis report to explain the final feature selection and model comparison results.
- Prepare presentation talking points around why selected FRED features helped more than using every macro column.
- Review the dashboard pages and make sure the model comparison, prediction explorer, and portfolio strategy charts are clear.
- Finalize the project narrative around Random Forest as the best volatility prediction model and Historical Max Sharpe / RF Predictive Max Sharpe as the key portfolio strategy comparison.
- Commit and push the completed branch once the team has reviewed the notebook outputs, dashboard, and weekly documentation.
