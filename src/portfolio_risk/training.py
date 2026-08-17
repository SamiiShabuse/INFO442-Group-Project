"""Random Forest training workflow utilities."""

from dataclasses import dataclass
import json
from pathlib import Path
import time

import joblib
import pandas as pd
import sklearn
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import GridSearchCV, TimeSeriesSplit

from portfolio_risk.config import DATE_COLUMN, TARGET_COLUMN, TICKER_COLUMN
from portfolio_risk.evaluation import regression_metrics
from portfolio_risk.modeling import load_selected_features


DEFAULT_SPLIT_DATE = "2024-01-01"
DEFAULT_MAX_DEPTH = 16
DEFAULT_MIN_SAMPLES_LEAF = 100
DEFAULT_N_ESTIMATORS = 100
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


@dataclass(frozen=True)
class RandomForestTrainingResult:
    """In-memory result of fitting the RF holdout and final models."""

    final_model: RandomForestRegressor
    holdout_model: RandomForestRegressor
    best_params: dict
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

    numeric_columns = selected_features + [TARGET_COLUMN]
    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    model_df = df.dropna(subset=numeric_columns).copy()
    model_df = model_df.sort_values([DATE_COLUMN, TICKER_COLUMN]).reset_index(drop=True)

    if model_df.empty:
        raise SystemExit("No complete training rows found after dropping missing values")

    return model_df


def split_modeling_data(model_df: pd.DataFrame, split_date: str) -> ModelingDataSplit:
    """Split labeled modeling rows into chronological train and holdout sets."""
    split_timestamp = pd.Timestamp(split_date)
    train_df = model_df[model_df[DATE_COLUMN] < split_timestamp]
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
    )


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
            cv=TimeSeriesSplit(n_splits=cv_splits),
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
    )
    duration_seconds = time.perf_counter() - start_time
    ended = pd.Timestamp.now()

    if verbose:
        print("Model params:", best_params)

    test_predictions = holdout_model.predict(X_test)
    holdout_metrics = regression_metrics(y_test, test_predictions)

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
        "train_start_date": split.train_df[DATE_COLUMN].min().date().isoformat(),
        "train_end_date": split.train_df[DATE_COLUMN].max().date().isoformat(),
        "test_start_date": split.test_df[DATE_COLUMN].min().date().isoformat(),
        "test_end_date": split.test_df[DATE_COLUMN].max().date().isoformat(),
        "final_fit_start_date": pd.concat(
            [split.train_df[DATE_COLUMN], split.test_df[DATE_COLUMN]]
        ).min().date().isoformat(),
        "final_fit_end_date": pd.concat(
            [split.train_df[DATE_COLUMN], split.test_df[DATE_COLUMN]]
        ).max().date().isoformat(),
        "train_rows": int(len(split.train_df)),
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

    return RandomForestTrainingRunResult(
        training=training,
        metadata=metadata,
        model_out=model_out_path,
        metadata_out_path=metadata_out_path,
        metrics_out_path=metrics_out_path,
    )
