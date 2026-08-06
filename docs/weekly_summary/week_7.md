# Week 7 Summary — [8/3 - 8/9]

**Project:** Stock Market Analysis & Portfolio Optimization
**Team Members:** Danny Eapen, Jeffrey Cheung, Joel Thomas, Samii Shabuse

## What Each of Us Worked On

**Danny**
- Built out 5 models to predict stock volatility (Linear, Ridge, Random Forest, Gradient Boosting, GARCH) and compared them against a simple baseline, Random Forest ended up winning clearly (R² 0.339) with Gradient Boosting close behind
- Ran feature selection experiments and found something useful, throwing every macro variable (FRED data) at Linear/Ridge actually hurt them, but a trimmed 5-feature set fixed it and got them competitive too
- Wrote it all up in a clean modeling doc with the model breakdowns, honest metrics table, and flagged that 2 of the notebooks still need to be rerun with the better feature set before final submission

**Jeffrey**

**Joel**

- Reviewed the team dashboard's Live Optimizer page and identified two gaps: no way to compare risk appetites without manual tuning, and no visual for the classic risk-return tradeoff
- Added risk profile presets (Conservative/Balanced/Aggressive/Custom) to the Live Optimizer page for one-click portfolio configuration
- Built an efficient frontier visualization on the Live Optimizer page, showing where the optimized portfolio sits relative to all achievable risk-return combinations using the RF-predicted risk model
- Resolved a merge conflict between my dashboard branch and main's portfolio optimizer integration, and verified both new features work correctly against real project data before merging
- Wrote the visualization documentation covering the dashboard's five pages (Overview, Model Comparison, Prediction Explorer, Portfolio Strategies, Live Optimizer), including the risk profile presets and efficient frontier additions, and moved it into `reports/` to match team convention

**Samii**

## Decisions Made (as a team)

-

## Blockers / Open Questions

-

## Next Steps

-
