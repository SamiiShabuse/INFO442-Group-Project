# Week 5 Summary - [7/27 - 8/2]

**Project:** Stock Market Analysis & Portfolio Optimization   
**Team Members:** Danny Eapen, Jeffrey Cheung, Joel Thomas, Samii Shabuse  
## What Each of Us Worked On

**Danny**
- 

**Jeffrey**
- Added a Live Optimizer page to the team dashboard that builds portfolio weights on demand using the random forest model's predicted volatility combined with historical asset correlations, instead of relying only on the fixed precomputed strategies.
- Extracted the optimization math (returns/volatility/Sharpe, RF-predictive covariance matrix, min-vol/max-Sharpe solver) into a reusable src/portfolio_optimizer.py module so it's shared between the dashboard and any future notebook work.
- Verified end-to-end in the browser — asset selection, objective choice, and max-weight constraints all produce a converged portfolio with a live backtest against equal-weight, historical, and SPY — without touching any of the existing dashboard pages or data.

**Joel**
- 

**Samii**
- 

## Decisions Made (as a team)
- 

## Blockers / Open Questions
- 

## Next Steps
- Use the updated Week 6 analysis report to explain the final feature selection and model comparison results.
- Prepare presentation talking points around why selected FRED features helped more than using every macro column.
- Review the dashboard pages and make sure the model comparison, prediction explorer, and portfolio strategy charts are clear.
- Finalize the project narrative around Random Forest as the best volatility prediction model and Historical Max Sharpe / RF Predictive Max Sharpe as the key portfolio strategy comparison.
- Commit and push the completed branch once the team has reviewed the notebook outputs, dashboard, and weekly documentation.
