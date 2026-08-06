# Scripts README

This folder contains the runnable scripts for training the Random Forest model,
refreshing current market features, generating predictions, saving prediction
runs, and evaluating the model.

The short version:

```text
train_rf_model.py
    makes the model

refresh_latest_features.py
    gets recent market data and builds model inputs

generate_predictions.py
    uses the model to make volatility predictions

archive_predictions.py
    saves each prediction run so it is not overwritten

evaluate_recent_rf_predictions.py
    grades old predictions once the next 20 trading days have happened

compare_prediction_to_trailing_vol.py
    compares RF predictions to recent trailing volatility

paper_trade.py
    turns predictions into hypothetical/paper-trading orders
```

## Important Idea

The Random Forest model predicts:

```text
future_volatility_20d
```

That means the model uses information available on one date to predict how
volatile each ticker will be over the next 20 trading days.

Because of that, a prediction made today cannot be fully evaluated tomorrow.
We need to wait until the next 20 trading days have happened.

## Where Random Forest Outputs Live

Random Forest artifacts are grouped here:

```text
data/processed/modeling/random_forest/
```

That folder contains the trained model, its metrics/metadata, live prediction
runs, and live evaluation outputs. Keeping these files inside the model-specific
folder makes the project cleaner than using top-level `models/`, `predictions/`,
or generated CSVs in `reports/`.

## Script Details

### `train_rf_model.py`

Trains and exports the Random Forest model.

Inputs:

```text
data/processed/features/feature_engineered_dataset.csv
data/processed/features/selected_features.csv
```

Outputs:

```text
data/processed/modeling/random_forest/rf_model.pkl
data/processed/modeling/random_forest/rf_model.metrics.csv
data/processed/modeling/random_forest/rf_model.metadata.json
```

Run this when you need to create or retrain the model.

Example:

```powershell
python scripts\train_rf_model.py
```

### `refresh_latest_features.py`

Downloads recent market data and rebuilds the latest model-ready feature rows.

Output:

```text
data/processed/features/latest_feature_snapshot.csv
```

This file is not predictions. It is the input data that the model sees.

Run this when you want the newest available market data.

Example:

```powershell
.\.venv\Scripts\python.exe scripts\refresh_latest_features.py
```

### `generate_predictions.py`

Loads the trained model and latest features, then predicts future 20-day
volatility for each ticker.

Inputs:

```text
data/processed/modeling/random_forest/rf_model.pkl
data/processed/features/latest_feature_snapshot.csv
data/processed/features/selected_features.csv
```

Output:

```text
data/processed/modeling/random_forest/live_predictions/latest_preds.csv
```

Example:

```powershell
python scripts\generate_predictions.py `
  --model data\processed\modeling\random_forest\rf_model.pkl `
  --features data\processed\features\latest_feature_snapshot.csv `
  --selected-features data\processed\features\selected_features.csv `
  --out data\processed\modeling\random_forest\live_predictions\latest_preds.csv
```

### `archive_predictions.py`

Saves `latest_preds.csv` into a dated file and updates the long-format
prediction log.

Inputs:

```text
data/processed/modeling/random_forest/live_predictions/latest_preds.csv
```

Outputs:

```text
data/processed/modeling/random_forest/live_predictions/preds_YYYY-MM-DD.csv
data/processed/modeling/random_forest/live_predictions/prediction_log.csv
```

Run this after generating predictions so each daily run is saved.

Example:

```powershell
python scripts\archive_predictions.py
```

### `evaluate_recent_rf_predictions.py`

Evaluates the model against a completed 20-trading-day future window.

This is the most honest model evaluation script. It finds a date far enough in
the past that the next 20 trading days are already known, predicts from that
date, computes actual realized volatility, and compares predicted vs. actual.

Outputs:

```text
data/processed/modeling/random_forest/live_evaluation/latest_20d_rf_evaluation.csv
data/processed/modeling/random_forest/live_evaluation/latest_20d_rf_evaluation.summary.csv
```

Example:

```powershell
python scripts\evaluate_recent_rf_predictions.py
```

### `compare_prediction_to_trailing_vol.py`

Compares an RF prediction to trailing 20-day volatility ending on a chosen
feature date.

This is not a true accuracy score. It compares the RF forecast to a simple
recent-volatility baseline.

Example:

```powershell
python scripts\compare_prediction_to_trailing_vol.py `
  --features data\processed\features\latest_feature_snapshot.csv `
  --predictions data\processed\modeling\random_forest\live_predictions\preds_2026-08-05.csv `
  --feature-date 2026-08-04 `
  --out data\processed\modeling\random_forest\live_evaluation\rf_vs_trailing_20d_ending_2026-08-04.csv
```

### `paper_trade.py`

Turns prediction weights into hypothetical or Alpaca paper-trading orders.

This is separate from model evaluation. Use it only after the prediction
pipeline is working and you want to test portfolio/order behavior.

Example dry run:

```powershell
python scripts\paper_trade.py `
  --predictions data\processed\modeling\random_forest\live_predictions\latest_preds.csv `
  --dry-run `
  --dry-price 100
```

## Normal Daily Workflow

Use this when you want to make a new live prediction run:

```powershell
.\.venv\Scripts\python.exe scripts\refresh_latest_features.py

python scripts\generate_predictions.py `
  --model data\processed\modeling\random_forest\rf_model.pkl `
  --features data\processed\features\latest_feature_snapshot.csv `
  --selected-features data\processed\features\selected_features.csv `
  --out data\processed\modeling\random_forest\live_predictions\latest_preds.csv

python scripts\archive_predictions.py
```

Then, when enough future data exists to evaluate old predictions:

```powershell
python scripts\evaluate_recent_rf_predictions.py
```

## Which Script Answers Which Question?

```text
Do I need a model file?
    train_rf_model.py

Do I need fresh market features?
    refresh_latest_features.py

Do I need today's prediction?
    generate_predictions.py

Do I need to save today's prediction?
    archive_predictions.py

Did the model do well on a completed future window?
    evaluate_recent_rf_predictions.py

How different is RF from recent trailing volatility?
    compare_prediction_to_trailing_vol.py

What orders would these predictions create?
    paper_trade.py
```
