# Week 3 Summary — [7/6 - 7/12]

**Project:** Stock Market Analysis & Portfolio Optimization   
**Team Members:** Danny Eapen, Jeffrey Cheung, Joel Thomas, Samii Shabuse  
## What Each of Us Worked On

**Danny**
- 

**Jeffrey**
- Built the Random Forest modeling notebook (06_rf_modeling.ipynb): trained a pooled model across all 21 tickers to predict future 20-day realized volatility, tuned max_depth and min_samples_leaf with GridSearchCV + TimeSeriesSplit (time-based CV to avoid look-ahead bias), and evaluated on a held-out 2024+ test set.
- Established a persistence baseline (predict future volatility = current volatility) and showed the tuned Random Forest clearly beats it (test R² 0.34 vs ~0.00, MAE 19% lower), setting up a fair side-by-side comparison with the linear regression model — same dataset, split date, and metrics.

**Joel**
- 

**Samii**
- 

## Decisions Made (as a team)
- 
## Blockers / Open Questions
- 
## Next Steps
- 