"""Train and export a Random Forest volatility model.

TLDR: replica of the notebook training flow, but in a repeatable script that exports a model artifact.

This script turns the notebook training flow into a repeatable artifact export:

    python scripts/train_rf_model.py \
        --features data/processed/features/feature_engineered_dataset.csv \
        --selected-features data/processed/features/selected_features.csv \
        --model-out models/rf_model.pkl

The exported model is refit on all labeled rows after hyperparameter tuning so
it can use the most recent rows that have a known 20-day future-volatility
target.
"""

import argparse
import json
import time
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GridSearchCV, TimeSeriesSplit


TARGET_COLUMN = "future_volatility_20d"
DEFAULT_SPLIT_DATE = "2024-01-01"
DEFAULT_MAX_DEPTH = 16
DEFAULT_MIN_SAMPLES_LEAF = 100


def load_selected_features(path: Path) -> list[str]:
    selected_features = pd.read_csv(path)
    if "feature" not in selected_features.columns:
        raise SystemExit("selected features CSV must contain a 'feature' column")

    features = selected_features["feature"].dropna().astype(str).tolist()
    if not features:
        raise SystemExit("selected features CSV did not contain any features")

    if TARGET_COLUMN in features:
        raise SystemExit(f"selected features must not include target column '{TARGET_COLUMN}'")

    return features


def load_modeling_data(features_path: Path, selected_features: list[str]) -> pd.DataFrame:
    df = pd.read_csv(features_path, parse_dates=["Date"], low_memory=False)

    missing_columns = [
        column
        for column in selected_features + [TARGET_COLUMN]
        if column not in df.columns
    ]
    if missing_columns:
        raise SystemExit(f"Modeling dataset is missing columns: {missing_columns}")

    for column in selected_features + [TARGET_COLUMN]:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    model_df = df.dropna(subset=selected_features + [TARGET_COLUMN]).copy()
    model_df = model_df.sort_values(["Date", "ticker"]).reset_index(drop=True)

    if model_df.empty:
        raise SystemExit("No complete training rows found after dropping missing values")

    return model_df


def evaluate_predictions(y_true: pd.Series, y_pred: np.ndarray) -> dict[str, float]:
    return {
        "MAE": float(mean_absolute_error(y_true, y_pred)),
        "RMSE": float(np.sqrt(mean_squared_error(y_true, y_pred))),
        "R2": float(r2_score(y_true, y_pred)),
    }


def main(
    features_path: str,
    selected_features_path: str,
    model_out: str,
    metadata_out: str | None,
    metrics_out: str | None,
    split_date: str,
    n_jobs: int,
    tune: bool,
    max_depth: int | None,
    min_samples_leaf: int,
) -> None:
    features_path = Path(features_path)
    selected_features_path = Path(selected_features_path)
    model_out = Path(model_out)
    metadata_out_path = Path(metadata_out) if metadata_out else model_out.with_suffix(".metadata.json")
    metrics_out_path = Path(metrics_out) if metrics_out else model_out.with_suffix(".metrics.csv")

    model_out.parent.mkdir(parents=True, exist_ok=True)
    metadata_out_path.parent.mkdir(parents=True, exist_ok=True)
    metrics_out_path.parent.mkdir(parents=True, exist_ok=True)

    selected_features = load_selected_features(selected_features_path)
    model_df = load_modeling_data(features_path, selected_features)

    split_timestamp = pd.Timestamp(split_date)
    train_df = model_df[model_df["Date"] < split_timestamp]
    test_df = model_df[model_df["Date"] >= split_timestamp]

    if train_df.empty or test_df.empty:
        raise SystemExit(
            f"Split date {split_date} produced train_rows={len(train_df)} "
            f"and test_rows={len(test_df)}"
        )

    X_train = train_df[selected_features]
    y_train = train_df[TARGET_COLUMN]
    X_test = test_df[selected_features]
    y_test = test_df[TARGET_COLUMN]

    started = pd.Timestamp.now()
    start_time = time.perf_counter()

    if tune:
        param_grid = {
            "max_depth": [4, 8, 16, None],
            "min_samples_leaf": [1, 20, 100],
        }
        grid_search = GridSearchCV(
            RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=n_jobs),
            param_grid,
            cv=TimeSeriesSplit(n_splits=5),
            scoring="neg_mean_squared_error",
        )

        print(f"Training RF grid search on {len(X_train)} rows and {len(selected_features)} features")
        grid_search.fit(X_train, y_train)
        best_params = grid_search.best_params_
        holdout_model = grid_search.best_estimator_
    else:
        best_params = {
            "max_depth": max_depth,
            "min_samples_leaf": min_samples_leaf,
        }
        holdout_model = RandomForestRegressor(
            n_estimators=100,
            random_state=42,
            n_jobs=n_jobs,
            **best_params,
        )
        print(
            f"Training RF on {len(X_train)} rows and {len(selected_features)} features "
            f"with params {best_params}"
        )
        holdout_model.fit(X_train, y_train)

    duration_seconds = time.perf_counter() - start_time
    ended = pd.Timestamp.now()

    print("Model params:", best_params)

    test_predictions = holdout_model.predict(X_test)
    rf_metrics = evaluate_predictions(y_test, test_predictions)

    if "rolling_volatility_20d" in test_df.columns:
        baseline_metrics = evaluate_predictions(y_test, test_df["rolling_volatility_20d"])
    else:
        baseline_metrics = None

    X_all = model_df[selected_features]
    y_all = model_df[TARGET_COLUMN]

    final_model = RandomForestRegressor(
        n_estimators=100,
        random_state=42,
        n_jobs=n_jobs,
        **best_params,
    )
    print(f"Refitting final model on all {len(X_all)} labeled rows")
    final_model.fit(X_all, y_all)

    joblib.dump(final_model, model_out)

    metrics_rows = []
    if baseline_metrics:
        metrics_rows.append({"model": "Baseline: rolling_volatility_20d", **baseline_metrics})
    metrics_rows.append({"model": "Random Forest", **rf_metrics})
    metrics_df = pd.DataFrame(metrics_rows)
    metrics_df.to_csv(metrics_out_path, index=False)

    metadata = {
        "model_type": "RandomForestRegressor",
        "model_path": str(model_out),
        "features_path": str(features_path),
        "selected_features_path": str(selected_features_path),
        "selected_features": selected_features,
        "target_column": TARGET_COLUMN,
        "best_params": best_params,
        "n_jobs": n_jobs,
        "tuned_with_grid_search": tune,
        "split_date": split_timestamp.date().isoformat(),
        "train_start_date": train_df["Date"].min().date().isoformat(),
        "train_end_date": train_df["Date"].max().date().isoformat(),
        "test_start_date": test_df["Date"].min().date().isoformat(),
        "test_end_date": test_df["Date"].max().date().isoformat(),
        "final_fit_start_date": model_df["Date"].min().date().isoformat(),
        "final_fit_end_date": model_df["Date"].max().date().isoformat(),
        "train_rows": int(len(train_df)),
        "test_rows": int(len(test_df)),
        "final_fit_rows": int(len(model_df)),
        "training_start_timestamp": started.isoformat(),
        "training_end_timestamp": ended.isoformat(),
        "training_duration_seconds": duration_seconds,
        "holdout_metrics": rf_metrics,
        "baseline_metrics": baseline_metrics,
    }
    metadata_out_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    print("Wrote model to:", model_out)
    print("Wrote metrics to:", metrics_out_path)
    print("Wrote metadata to:", metadata_out_path)
    print(metrics_df)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train and export the RF volatility model.")
    parser.add_argument(
        "--features",
        default="data/processed/features/feature_engineered_dataset.csv",
        help="Path to the labeled feature-engineered dataset",
    )
    parser.add_argument(
        "--selected-features",
        default="data/processed/features/selected_features.csv",
        help="Path to selected_features.csv",
    )
    parser.add_argument(
        "--model-out",
        default="models/rf_model.pkl",
        help="Path where the trained model should be written",
    )
    parser.add_argument("--metadata-out", default=None, help="Optional metadata JSON path")
    parser.add_argument("--metrics-out", default=None, help="Optional metrics CSV path")
    parser.add_argument(
        "--split-date",
        default=DEFAULT_SPLIT_DATE,
        help="Holdout split date used for reporting metrics",
    )
    parser.add_argument(
        "--n-jobs",
        type=int,
        default=1,
        help="Parallel workers for RandomForestRegressor; default 1 for Windows sandbox reliability",
    )
    parser.add_argument(
        "--tune",
        action="store_true",
        help="Run the full notebook-style GridSearchCV before exporting",
    )
    parser.add_argument(
        "--max-depth",
        type=int,
        default=DEFAULT_MAX_DEPTH,
        help="RF max_depth used when --tune is not set",
    )
    parser.add_argument(
        "--min-samples-leaf",
        type=int,
        default=DEFAULT_MIN_SAMPLES_LEAF,
        help="RF min_samples_leaf used when --tune is not set",
    )

    args = parser.parse_args()
    main(
        features_path=args.features,
        selected_features_path=args.selected_features,
        model_out=args.model_out,
        metadata_out=args.metadata_out,
        metrics_out=args.metrics_out,
        split_date=args.split_date,
        n_jobs=args.n_jobs,
        tune=args.tune,
        max_depth=args.max_depth,
        min_samples_leaf=args.min_samples_leaf,
    )
