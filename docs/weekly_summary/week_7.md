# Week 7 Summary - [8/3 - 8/9]

**Project:** Stock Market Analysis & Portfolio Optimization
**Team Members:** Danny Eapen, Jeffrey Cheung, Joel Thomas, Samii Shabuse

## What Each of Us Worked On

**Danny**
- Built out 5 models to predict stock volatility (Linear, Ridge, Random Forest, Gradient Boosting, GARCH) and compared them against a simple baseline, Random Forest ended up winning clearly (R² 0.339) with Gradient Boosting close behind
- Ran feature selection experiments and found something useful, throwing every macro variable (FRED data) at Linear/Ridge actually hurt them, but a trimmed 5-feature set fixed it and got them competitive too
- Wrote it all up in a clean modeling doc with the model breakdowns, honest metrics table, and flagged that 2 of the notebooks still need to be rerun with the better feature set before final submission

**Jeffrey**
- Built the 18-slide final presentation deck, pulling all numbers directly from data/processed/ so the slides can't drift from the notebook outputs


**Joel**

- Reviewed the team dashboard's Live Optimizer page and identified two gaps: no way to compare risk appetites without manual tuning, and no visual for the classic risk-return tradeoff
- Added risk profile presets (Conservative/Balanced/Aggressive/Custom) to the Live Optimizer page for one-click portfolio configuration
- Built an efficient frontier visualization on the Live Optimizer page, showing where the optimized portfolio sits relative to all achievable risk-return combinations using the RF-predicted risk model
- Resolved a merge conflict between my dashboard branch and main's portfolio optimizer integration, and verified both new features work correctly against real project data before merging
- Wrote the visualization documentation covering the dashboard's five pages (Overview, Model Comparison, Prediction Explorer, Portfolio Strategies, Live Optimizer), including the risk profile presets and efficient frontier additions, and moved it into `reports/` to match team convention

**Samii**
- Revised the EDA analysis report after professor feedback so it stays focused on what the data shows through EDA and how those findings inform later modeling and portfolio decisions.
- Cleaned up project documentation and align folder/readme descriptions with the current project workflow.
- Tested the Random Forest model against live/latest trading data, archive daily predictions, and evaluate a completed 20-trading-day volatility window.
- Documented the live RF results honestly: the model showed useful signal overall, but missed sudden volatility spikes for some assets such as AMZN and MSFT.
- Connected RF predictions and portfolio optimization to a dry-run rebalance order workflow.
- Created the sample current-positions workflow so the order generator demonstrates true rebalancing behavior with buys, sells, and holds instead of only building a portfolio from cash.

## Decisions Made (as a team)

- We decided to keep Random Forest as the main model used for portfolio optimization because it remains the strongest all-ticker volatility model.
- We decided to treat the live RF testing as an initial validation of the real-data pipeline, not as final proof that the model is always accurate.
- We decided to use the final dashboard, EDA report, modeling documentation, and presentation deck together as the main final-project narrative.

## Blockers / Open Questions

- No major blockers right now.
- The newest live RF predictions cannot be fully evaluated until the next 20 trading days have happened.
- We still need to decide how much of the dry-run order-generation workflow to show in the final presentation, since it is useful but should be framed as simulation only.
- The final deliverable needs one last consistency check so the README, dashboard, reports, notebooks, and presentation all tell the same story.

## Next Steps

- Review the final presentation deck and make sure the numbers match the latest `data/processed/` outputs.
- Continue collecting archived live RF predictions so future completed 20-day windows can be evaluated.
- Rerun or review any notebooks that feed the dashboard if final data or model outputs change.
- Do a final project polish pass on the root README, dashboard instructions, and report links before submission.
- Get feedback from professor for any last-minute adjustments to the final deliverables or project expansions.