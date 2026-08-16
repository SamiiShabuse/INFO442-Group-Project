# Week 8 Summary - [8/10 - 8/16]

**Project:** Stock Market Analysis & Portfolio Optimization
**Team Members:** Danny Eapen, Jeffrey Cheung, Joel Thomas, Samii Shabuse

## What Each of Us Worked On

**Danny**
- Reviewed the final modeling outputs and helped keep the model comparison story focused on volatility prediction instead of stock-price prediction.
- Checked that Random Forest remained the strongest all-ticker model for the live optimization workflow, while the MLP and other models stayed useful as comparison models.
- Helped clarify how model metrics such as MAE, RMSE, and R2 should be explained in the final documentation and presentation.

**Jeffrey**
- Merged PR #43, which added the predictive-vs-historical volatility notebook in `notebooks/09_predictive_vs_historical/`.
- Built a controlled comparison between Random Forest predicted volatility and a historical trailing-volatility baseline, including pooled forecast metrics, per-ticker accuracy, and skill decomposition outputs.
- Ran a walk-forward portfolio impact backtest comparing equal weight, historical minimum-volatility baselines, RF predictive minimum volatility, and the SPY benchmark.
- Added robustness outputs for multiple rebalance frequencies and risk-model calibration, showing that RF reduced realized portfolio volatility consistently while the Sharpe-ratio advantage was not stable enough to overclaim.
- Saved the generated comparison tables under `data/processed/predictive_vs_historical/` so the final report, dashboard, and slides can cite the same numbers.

**Joel**
- Reviewed the portfolio optimization and dry-run order-generation workflow so it is framed as simulation and analysis, not real trading.
- Helped connect the Live Optimizer workflow to the final explanation of target weights, risk profiles, and buy/sell/hold rebalance outputs.
- Checked that the project narrative clearly separates portfolio optimization from order generation.

**Samii**
- Refactored the live project scripts into a cleaner package structure under `src/portfolio_risk/`, including training, prediction, prediction archival, evaluation, rebalancing, and order-generation logic.
- Added and updated unit tests for features, prediction, prediction archival, evaluation, training, rebalancing, portfolio logic, and order generation.
- Polished the full documentation story across the root README, `docs/project_workflow.md`, script docs, source-code docs, data docs, dashboard docs, notebook docs, and report docs.
- Documented where live Random Forest predictions, archived prediction runs, live evaluation outputs, optimized target weights, and dry-run rebalance orders are stored.

## Decisions Made (as a team)

- We decided the project is now mostly code-complete and should move into final documentation, report, presentation, and demo polish.
- We decided to keep Random Forest as the main live volatility model because it remains the strongest all-ticker model used by the portfolio optimizer.
- We decided to present the live RF testing honestly: it proves the pipeline works on real trading data, but a prediction can only be fully judged after the next 20 trading days have happened.
- We decided that order-generation outputs should be described as dry-run simulation files only, not as real brokerage orders or financial advice.
- We decided to keep notebooks focused on explanation and visualization, scripts focused on repeatable workflow commands, and `src/portfolio_risk/` focused on reusable tested code.

## Blockers / Open Questions

- No major technical blockers right now.
- The newest live Random Forest predictions still need future trading days before they can be fully evaluated against realized 20-day volatility.
- The team still needs to choose which visuals and metrics are most important for the final presentation so the story stays concise.
- The final report and presentation should avoid overclaiming model performance and clearly state the project limitations.

## Next Steps

- Finalize the written report using the updated README and `docs/project_workflow.md` as the source of truth.
- Review the dashboard one more time and confirm all charts load from the latest `data/processed/` outputs.
- Prepare final presentation talking points around the data pipeline, EDA findings, model comparison, Random Forest live workflow, portfolio optimization, and limitations.
- Continue archiving live RF predictions if more trading days become available before final submission.
- Run the final test/lint checks before committing and submitting the completed project.
