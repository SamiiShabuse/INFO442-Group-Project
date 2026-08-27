# Random Forest Modeling Outputs

This folder contains the Random Forest outputs used by both the notebook
analysis and the live prediction workflow.

Random Forest is the main live model because it has a repeatable artifact
export workflow and leakage-safe holdout performance above the
trailing-volatility baseline. It predicts:

```text
future_volatility_20d
```

That prediction is an estimate of each asset's realized volatility over the
next 20 trading days.

## Notebook Outputs

- `metrics.csv`: holdout metrics from the Random Forest modeling notebook.
- `test_predictions.csv`: holdout predictions used for model comparison.

These files now come from the same leakage-safe training script as the exported
model artifact, so notebook 09 and the dashboard use the corrected holdout
predictions.

## Exported Live Model

- `rf_model.pkl`: trained Random Forest artifact used by live scripts.
- `rf_model.metrics.csv`: metrics from the repeatable training script.
- `rf_model.metadata.json`: training metadata, selected features, split dates,
  package versions, row counts, and holdout metrics.

The exported model is created by:

```powershell
.\.venv\Scripts\python.exe scripts\train_rf_model.py
```

The repeatable training script derives a `target_end_date` for each labeled
row and purges rows whose future 20-trading-day target window would cross the
holdout split. The current exported artifact purged 420 boundary rows from
holdout training before fitting the reported Random Forest.

## Live Predictions

`live_predictions/` stores current and archived prediction runs:

- `latest_preds.csv`: most recent wide prediction file.
- `preds_YYYY-MM-DD.csv`: dated copy of a prediction run.
- `prediction_log.csv`: long-format append-only prediction history.

Generate and archive a new prediction run with:

```powershell
.\.venv\Scripts\python.exe scripts\generate_predictions.py `
  --model data\processed\modeling\random_forest\rf_model.pkl `
  --features data\processed\features\latest_feature_snapshot.csv `
  --selected-features data\processed\features\selected_features.csv `
  --out data\processed\modeling\random_forest\live_predictions\latest_preds.csv

.\.venv\Scripts\python.exe scripts\archive_predictions.py
```

## Live Evaluation

`live_evaluation/` stores CSV outputs used to understand whether live Random
Forest predictions are behaving well.

There are two evaluation styles:

- Completed future-window evaluation: compares predictions to actual realized
  future volatility after the next 20 trading days are available.
- RF versus trailing volatility comparison: compares the prediction to recent
  trailing 20-day volatility as a same-day baseline.

The completed-window evaluation is the real accuracy test. The trailing
comparison is useful context, but it is not a future accuracy score.
