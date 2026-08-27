"""Random Forest training workflow utilities."""

from dataclasses import dataclass
import json
from pathlib import Path
import time

import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import GridSearchCV, TimeSeriesSplit

from portfolio_risk.config import (
    DATE_COLUMN,
    PREDICTED_VOLATILITY_COLUMN,
    TARGET_COLUMN,
    TARGET_END_DATE_COLUMN,
    TICKER_COLUMN,
)
from portfolio_risk.evaluation import regression_metrics
from portfolio_risk.modeling import load_selected_features


DEFAULT_SPLIT_DATE = "2024-01-01"
DEFAULT_MAX_DEPTH = 16
DEFAULT_MIN_SAMPLES_LEAF = 100
DEFAULT_N_ESTIMATORS = 100
DEFAULT_TARGET_WINDOW_DAYS = 20
DEFAULT_RF_PARAM_GRID = {
    "max_depth": [4, 8, 16, None],
    "min_samples_leaf": [1, 20, 100],
}
BASELINE_MODEL_LABEL = "Baseline: rolling_volatility_20d"
RF_MODEL_LABEL = "Random Forest"


@dataclass(frozen=True)
class ModelingDataSplit:
    """Time-based train/test split used for model reporting."""

    split_timestamp: pd.Timestamp
    train_df: pd.DataFrame
    test_df: pd.DataFrame
    purged_train_rows: int = 0


@dataclass(frozen=True)
class RandomForestTrainingResult:
    """In-memory result of fitting the RF holdout and final models."""

    final_model: RandomForestRegressor
    holdout_model: RandomForestRegressor
    best_params: dict
    holdout_predictions: pd.DataFrame
    metrics: pd.DataFrame
    holdout_metrics: dict
    baseline_metrics: dict | None
    split: ModelingDataSplit
    started: pd.Timestamp
    ended: pd.Timestamp
    duration_seconds: float
    final_fit_rows: int


@dataclass(frozen=True)
class RandomForestTrainingRunResult:
    """File-backed training run result."""

    training: RandomForestTrainingResult
    metadata: dict
    model_out: Path
    metadata_out_path: Path
    metrics_out_path: Path
    predictions_out_path: Path | None = None
    comparison_metrics_out_path: Path | None = None


def resolve_training_output_paths(
    model_out: str | Path,
    metadata_out: str | Path | None,
    metrics_out: str | Path | None,
) -> tuple[Path, Path, Path]:
    """Use explicit artifact paths or default metadata/metrics paths beside the model."""
    model_out_path = Path(model_out)
    metadata_out_path = (
        Path(metadata_out) if metadata_out else model_out_path.with_suffix(".metadata.json")
    )
    metrics_out_path = Path(metrics_out) if metrics_out else model_out_path.with_suffix(".metrics.csv")
    return model_out_path, metadata_out_path, metrics_out_path


def load_modeling_data(features_path: str | Path, selected_features: list[str]) -> pd.DataFrame:
    """Load, validate, and clean labeled rows for Random Forest training."""
    df = pd.read_csv(features_path, low_memory=False)

    required_columns = [DATE_COLUMN, TICKER_COLUMN, *selected_features, TARGET_COLUMN]
    missing_columns = [column for column in required_columns if column not in df.columns]
    if missing_columns:
        raise SystemExit(f"Modeling dataset is missing columns: {missing_columns}")

    df[DATE_COLUMN] = pd.to_datetime(df[DATE_COLUMN])
    if TARGET_END_DATE_COLUMN in df.columns:
        df[TARGET_END_DATE_COLUMN] = pd.to_datetime(df[TARGET_END_DATE_COLUMN])
    else:
        df = add_target_end_dates(df)

    numeric_columns = selected_features + [TARGET_COLUMN]
    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    complete_columns = numeric_columns + [TARGET_END_DATE_COLUMN]
    model_df = df.dropna(subset=complete_columns).copy()
    model_df = model_df.sort_values([DATE_COLUMN, TICKER_COLUMN]).reset_index(drop=True)

    if model_df.empty:
        raise SystemExit("No complete training rows found after dropping missing values")

    return model_df


def add_target_end_dates(
    df: pd.DataFrame,
    *,
    target_window_days: int = DEFAULT_TARGET_WINDOW_DAYS,
) -> pd.DataFrame:
    """Add the date when each row's future-volatility target window ends."""
    df = df.sort_values([TICKER_COLUMN, DATE_COLUMN]).copy()
    df[TARGET_END_DATE_COLUMN] = df.groupby(TICKER_COLUMN)[DATE_COLUMN].shift(
        -target_window_days
    )
    return df


def split_modeling_data(model_df: pd.DataFrame, split_date: str) -> ModelingDataSplit:
    """Split labeled modeling rows into chronological train and holdout sets."""
    model_df = model_df.copy()
    model_df[DATE_COLUMN] = pd.to_datetime(model_df[DATE_COLUMN])
    if TARGET_END_DATE_COLUMN in model_df.columns:
        model_df[TARGET_END_DATE_COLUMN] = pd.to_datetime(model_df[TARGET_END_DATE_COLUMN])

    split_timestamp = pd.Timestamp(split_date)
    train_candidate = model_df[model_df[DATE_COLUMN] < split_timestamp]
    purged_train_rows = 0
    if TARGET_END_DATE_COLUMN in model_df.columns:
        target_end_date = pd.to_datetime(train_candidate[TARGET_END_DATE_COLUMN])
        train_df = train_candidate[
            target_end_date < split_timestamp
        ]
        purged_train_rows = len(train_candidate) - len(train_df)
    else:
        train_df = train_candidate
    test_df = model_df[model_df[DATE_COLUMN] >= split_timestamp]

    if train_df.empty or test_df.empty:
        raise SystemExit(
            f"Split date {split_date} produced train_rows={len(train_df)} "
            f"and test_rows={len(test_df)}"
        )

    return ModelingDataSplit(
        split_timestamp=split_timestamp,
        train_df=train_df,
        test_df=test_df,
        purged_train_rows=purged_train_rows,
    )


def leakage_safe_time_series_cv(
    train_df: pd.DataFrame,
    *,
    n_splits: int,
) -> list[tuple[np.ndarray, np.ndarray]]:
    """Build TimeSeriesSplit folds that purge target windows crossing validation starts."""
    if TARGET_END_DATE_COLUMN not in train_df.columns:
        return list(TimeSeriesSplit(n_splits=n_splits).split(train_df))

    date_series = pd.to_datetime(train_df[DATE_COLUMN])
    target_end_series = pd.to_datetime(train_df[TARGET_END_DATE_COLUMN])
    unique_dates = pd.Series(date_series.sort_values().unique())
    date_splits = TimeSeriesSplit(n_splits=n_splits).split(unique_dates)

    folds = []
    for train_date_idx, validation_date_idx in date_splits:
        train_dates = set(unique_dates.iloc[train_date_idx])
        validation_dates = set(unique_dates.iloc[validation_date_idx])
        validation_start = unique_dates.iloc[validation_date_idx].min()

        train_mask = date_series.isin(train_dates) & (target_end_series < validation_start)
        validation_mask = date_series.isin(validation_dates)
        train_indices = np.flatnonzero(train_mask.to_numpy())
        validation_indices = np.flatnonzero(validation_mask.to_numpy())

        if len(train_indices) and len(validation_indices):
            folds.append((train_indices, validation_indices))

    if not folds:
        raise SystemExit(
            "Time-series CV could not create leakage-safe folds. "
            "Use fewer splits or provide more training history."
        )

    return folds


def fit_holdout_random_forest(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    *,
    n_jobs: int,
    tune: bool,
    max_depth: int | None,
    min_samples_leaf: int,
    n_estimators: int = DEFAULT_N_ESTIMATORS,
    param_grid: dict | None = None,
    cv_splits: int = 5,
    cv=None,
) -> tuple[RandomForestRegressor, dict]:
    """Fit the holdout model, optionally using notebook-style grid search."""
    if tune:
        grid_search = GridSearchCV(
            RandomForestRegressor(
                n_estimators=n_estimators,
                random_state=42,
                n_jobs=n_jobs,
            ),
            param_grid or DEFAULT_RF_PARAM_GRID,
            cv=cv or TimeSeriesSplit(n_splits=cv_splits),
            scoring="neg_mean_squared_error",
        )
        grid_search.fit(X_train, y_train)
        return grid_search.best_estimator_, dict(grid_search.best_params_)

    best_params = {
        "max_depth": max_depth,
        "min_samples_leaf": min_samples_leaf,
    }
    model = RandomForestRegressor(
        n_estimators=n_estimators,
        random_state=42,
        n_jobs=n_jobs,
        **best_params,
    )
    model.fit(X_train, y_train)
    return model, best_params


def build_metrics_frame(holdout_metrics: dict, baseline_metrics: dict | None) -> pd.DataFrame:
    """Format holdout and baseline metrics for the exported metrics CSV."""
    rows = []
    if baseline_metrics:
        rows.append({"model": BASELINE_MODEL_LABEL, **baseline_metrics})
    rows.append({"model": RF_MODEL_LABEL, **holdout_metrics})
    return pd.DataFrame(rows)


def build_holdout_predictions_frame(
    split: ModelingDataSplit,
    predictions,
) -> pd.DataFrame:
    """Format holdout predictions for notebooks and dashboard data refreshes."""
    prediction_frame = split.test_df[[DATE_COLUMN, TICKER_COLUMN, TARGET_COLUMN]].copy()
    prediction_frame[PREDICTED_VOLATILITY_COLUMN] = predictions
    return prediction_frame[
        [DATE_COLUMN, TICKER_COLUMN, TARGET_COLUMN, PREDICTED_VOLATILITY_COLUMN]
    ]


def build_comparison_metrics_frame(training: RandomForestTrainingResult) -> pd.DataFrame:
    """Format RF metrics with the legacy notebook metadata columns."""
    split = training.split
    metrics = training.metrics.copy()

    metrics["model_run_timestamp"] = training.started.isoformat()
    metrics["split_date"] = split.split_timestamp.date().isoformat()
    metrics["train_start_date"] = split.train_df[DATE_COLUMN].min().date().isoformat()
    metrics["train_end_date"] = split.train_df[DATE_COLUMN].max().date().isoformat()
    metrics["test_start_date"] = split.test_df[DATE_COLUMN].min().date().isoformat()
    metrics["test_end_date"] = split.test_df[DATE_COLUMN].max().date().isoformat()
    metrics["train_rows"] = int(len(split.train_df))
    metrics["test_rows"] = int(len(split.test_df))

    metrics["training_start_timestamp"] = training.started.isoformat()
    metrics["training_end_timestamp"] = training.ended.isoformat()
    metrics["training_duration_seconds"] = training.duration_seconds

    baseline_mask = metrics["model"] == BASELINE_MODEL_LABEL
    metrics.loc[
        baseline_mask,
        [
            "training_start_timestamp",
            "training_end_timestamp",
            "training_duration_seconds",
        ],
    ] = pd.NA

    return metrics


def train_random_forest_model(
    model_df: pd.DataFrame,
    selected_features: list[str],
    *,
    split_date: str,
    n_jobs: int,
    tune: bool,
    max_depth: int | None,
    min_samples_leaf: int,
    n_estimators: int = DEFAULT_N_ESTIMATORS,
    verbose: bool = False,
) -> RandomForestTrainingResult:
    """Train the RF holdout model, evaluate it, and refit a final model on all rows."""
    split = split_modeling_data(model_df, split_date)

    X_train = split.train_df[selected_features]
    y_train = split.train_df[TARGET_COLUMN]
    X_test = split.test_df[selected_features]
    y_test = split.test_df[TARGET_COLUMN]

    if verbose:
        if tune:
            print(
                f"Training RF grid search on {len(X_train)} rows "
                f"and {len(selected_features)} features"
            )
        else:
            params = {"max_depth": max_depth, "min_samples_leaf": min_samples_leaf}
            print(
                f"Training RF on {len(X_train)} rows and {len(selected_features)} features "
                f"with params {params}"
            )

    started = pd.Timestamp.now()
    start_time = time.perf_counter()
    holdout_model, best_params = fit_holdout_random_forest(
        X_train,
        y_train,
        n_jobs=n_jobs,
        tune=tune,
        max_depth=max_depth,
        min_samples_leaf=min_samples_leaf,
        n_estimators=n_estimators,
        cv=leakage_safe_time_series_cv(split.train_df.reset_index(drop=True), n_splits=5)
        if tune
        else None,
    )
    duration_seconds = time.perf_counter() - start_time
    ended = pd.Timestamp.now()

    if verbose:
        print("Model params:", best_params)

    test_predictions = holdout_model.predict(X_test)
    holdout_metrics = regression_metrics(y_test, test_predictions)
    holdout_predictions = build_holdout_predictions_frame(split, test_predictions)

    baseline_metrics = None
    if "rolling_volatility_20d" in split.test_df.columns:
        baseline_metrics = regression_metrics(y_test, split.test_df["rolling_volatility_20d"])

    X_all = model_df[selected_features]
    y_all = model_df[TARGET_COLUMN]

    final_model = RandomForestRegressor(
        n_estimators=n_estimators,
        random_state=42,
        n_jobs=n_jobs,
        **best_params,
    )
    if verbose:
        print(f"Refitting final model on all {len(X_all)} labeled rows")
    final_model.fit(X_all, y_all)

    return RandomForestTrainingResult(
        final_model=final_model,
        holdout_model=holdout_model,
        best_params=best_params,
        holdout_predictions=holdout_predictions,
        metrics=build_metrics_frame(holdout_metrics, baseline_metrics),
        holdout_metrics=holdout_metrics,
        baseline_metrics=baseline_metrics,
        split=split,
        started=started,
        ended=ended,
        duration_seconds=duration_seconds,
        final_fit_rows=len(model_df),
    )


def build_training_metadata(
    *,
    training: RandomForestTrainingResult,
    model_out: str | Path,
    features_path: str | Path,
    selected_features_path: str | Path,
    selected_features: list[str],
    n_jobs: int,
    tune: bool,
) -> dict:
    """Build reproducibility metadata for a saved RF model artifact."""
    split = training.split
    model_out = Path(model_out)
    features_path = Path(features_path)
    selected_features_path = Path(selected_features_path)

    return {
        "model_type": "RandomForestRegressor",
        "model_path": str(model_out),
        "sklearn_version": sklearn.__version__,
        "joblib_version": joblib.__version__,
        "features_path": str(features_path),
        "selected_features_path": str(selected_features_path),
        "selected_features": selected_features,
        "target_column": TARGET_COLUMN,
        "best_params": training.best_params,
        "n_jobs": n_jobs,
        "tuned_with_grid_search": tune,
        "split_date": split.split_timestamp.date().isoformat(),
        "target_end_date_column": TARGET_END_DATE_COLUMN
        if TARGET_END_DATE_COLUMN in split.train_df.columns
        else None,
        "train_start_date": split.train_df[DATE_COLUMN].min().date().isoformat(),
        "train_end_date": split.train_df[DATE_COLUMN].max().date().isoformat(),
        "train_target_end_date": split.train_df[TARGET_END_DATE_COLUMN].max().date().isoformat()
        if TARGET_END_DATE_COLUMN in split.train_df.columns
        else None,
        "test_start_date": split.test_df[DATE_COLUMN].min().date().isoformat(),
        "test_end_date": split.test_df[DATE_COLUMN].max().date().isoformat(),
        "final_fit_start_date": pd.concat(
            [split.train_df[DATE_COLUMN], split.test_df[DATE_COLUMN]]
        ).min().date().isoformat(),
        "final_fit_end_date": pd.concat(
            [split.train_df[DATE_COLUMN], split.test_df[DATE_COLUMN]]
        ).max().date().isoformat(),
        "train_rows": int(len(split.train_df)),
        "purged_train_rows": int(split.purged_train_rows),
        "test_rows": int(len(split.test_df)),
        "final_fit_rows": int(training.final_fit_rows),
        "training_start_timestamp": training.started.isoformat(),
        "training_end_timestamp": training.ended.isoformat(),
        "training_duration_seconds": training.duration_seconds,
        "holdout_metrics": training.holdout_metrics,
        "baseline_metrics": training.baseline_metrics,
    }


def run_random_forest_training(
    *,
    features_path: str | Path,
    selected_features_path: str | Path,
    model_out: str | Path,
    metadata_out: str | Path | None = None,
    metrics_out: str | Path | None = None,
    predictions_out: str | Path | None = None,
    comparison_metrics_out: str | Path | None = None,
    split_date: str = DEFAULT_SPLIT_DATE,
    n_jobs: int = 1,
    tune: bool = False,
    max_depth: int | None = DEFAULT_MAX_DEPTH,
    min_samples_leaf: int = DEFAULT_MIN_SAMPLES_LEAF,
    verbose: bool = False,
) -> RandomForestTrainingRunResult:
    """Load training files, fit the RF model, and write model/metrics/metadata artifacts."""
    model_out_path, metadata_out_path, metrics_out_path = resolve_training_output_paths(
        model_out,
        metadata_out,
        metrics_out,
    )
    model_out_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_out_path.parent.mkdir(parents=True, exist_ok=True)
    metrics_out_path.parent.mkdir(parents=True, exist_ok=True)

    selected_features = load_selected_features(selected_features_path)
    model_df = load_modeling_data(features_path, selected_features)
    training = train_random_forest_model(
        model_df,
        selected_features,
        split_date=split_date,
        n_jobs=n_jobs,
        tune=tune,
        max_depth=max_depth,
        min_samples_leaf=min_samples_leaf,
        verbose=verbose,
    )

    metadata = build_training_metadata(
        training=training,
        model_out=model_out_path,
        features_path=features_path,
        selected_features_path=selected_features_path,
        selected_features=selected_features,
        n_jobs=n_jobs,
        tune=tune,
    )

    joblib.dump(training.final_model, model_out_path)
    training.metrics.to_csv(metrics_out_path, index=False)
    metadata_out_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    predictions_out_path = Path(predictions_out) if predictions_out else None
    if predictions_out_path:
        predictions_out_path.parent.mkdir(parents=True, exist_ok=True)
        training.holdout_predictions.to_csv(predictions_out_path, index=False)

    comparison_metrics_out_path = Path(comparison_metrics_out) if comparison_metrics_out else None
    if comparison_metrics_out_path:
        comparison_metrics_out_path.parent.mkdir(parents=True, exist_ok=True)
        build_comparison_metrics_frame(training).to_csv(comparison_metrics_out_path, index=False)

    return RandomForestTrainingRunResult(
        training=training,
        metadata=metadata,
        model_out=model_out_path,
        metadata_out_path=metadata_out_path,
        metrics_out_path=metrics_out_path,
        predictions_out_path=predictions_out_path,
        comparison_metrics_out_path=comparison_metrics_out_path,
    )
