from io import StringIO

import pandas as pd
import pytest

from portfolio_risk.config import TARGET_COLUMN
from portfolio_risk.training import (
    BASELINE_MODEL_LABEL,
    DEFAULT_MAX_DEPTH,
    RF_MODEL_LABEL,
    build_metrics_frame,
    build_training_metadata,
    load_modeling_data,
    resolve_training_output_paths,
    split_modeling_data,
    train_random_forest_model,
)


def make_modeling_frame() -> pd.DataFrame:
    dates = pd.date_range("2023-12-20", periods=8, freq="B")
    return pd.DataFrame(
        {
            "Date": dates,
            "ticker": ["AAPL", "MSFT"] * 4,
            "signal_a": [0.10, 0.20, 0.15, 0.25, 0.30, 0.35, 0.40, 0.45],
            "signal_b": [1.0, 1.2, 1.1, 1.3, 1.4, 1.5, 1.6, 1.7],
            "rolling_volatility_20d": [0.08, 0.09, 0.10, 0.11, 0.12, 0.13, 0.14, 0.15],
            TARGET_COLUMN: [0.09, 0.11, 0.12, 0.13, 0.16, 0.17, 0.18, 0.19],
        }
    )


def test_load_modeling_data_coerces_numeric_sorts_and_drops_missing_rows():
    features_csv = StringIO(
        "Date,ticker,signal_a,signal_b,future_volatility_20d\n"
        "2026-01-02,MSFT,2,4,0.20\n"
        "2026-01-01,AAPL,1,3,0.10\n"
        "2026-01-03,GLD,bad,5,0.30\n"
    )

    model_df = load_modeling_data(features_csv, ["signal_a", "signal_b"])

    assert list(model_df["ticker"]) == ["AAPL", "MSFT"]
    assert model_df["signal_a"].tolist() == [1.0, 2.0]
    assert model_df[TARGET_COLUMN].tolist() == [0.10, 0.20]


def test_load_modeling_data_rejects_missing_required_columns():
    features_csv = StringIO("Date,ticker,signal_a\n2026-01-01,AAPL,1\n")

    with pytest.raises(SystemExit, match="missing columns"):
        load_modeling_data(features_csv, ["signal_a", "signal_b"])


def test_split_modeling_data_uses_chronological_holdout():
    model_df = make_modeling_frame()

    split = split_modeling_data(model_df, "2023-12-26")

    assert len(split.train_df) == 4
    assert len(split.test_df) == 4
    assert split.train_df["Date"].max() < pd.Timestamp("2023-12-26")
    assert split.test_df["Date"].min() >= pd.Timestamp("2023-12-26")

    with pytest.raises(SystemExit, match="produced train_rows"):
        split_modeling_data(model_df, "2023-12-01")


def test_resolve_training_output_paths_defaults_and_accepts_overrides():
    model_out, metadata_out, metrics_out = resolve_training_output_paths(
        "models/rf_model.pkl",
        None,
        None,
    )

    assert model_out.name == "rf_model.pkl"
    assert metadata_out.name == "rf_model.metadata.json"
    assert metrics_out.name == "rf_model.metrics.csv"

    _, metadata_out, metrics_out = resolve_training_output_paths(
        "models/rf_model.pkl",
        "custom_metadata.json",
        "custom_metrics.csv",
    )

    assert metadata_out.name == "custom_metadata.json"
    assert metrics_out.name == "custom_metrics.csv"


def test_build_metrics_frame_includes_baseline_when_available():
    metrics = build_metrics_frame(
        holdout_metrics={"MAE": 0.2, "RMSE": 0.3, "R2": 0.4},
        baseline_metrics={"MAE": 0.5, "RMSE": 0.6, "R2": 0.7},
    )

    assert list(metrics["model"]) == [BASELINE_MODEL_LABEL, RF_MODEL_LABEL]


def test_train_random_forest_model_reports_metrics_and_refits_all_rows():
    selected_features = ["signal_a", "signal_b"]
    model_df = make_modeling_frame()

    result = train_random_forest_model(
        model_df,
        selected_features,
        split_date="2023-12-26",
        n_jobs=1,
        tune=False,
        max_depth=DEFAULT_MAX_DEPTH,
        min_samples_leaf=1,
        n_estimators=5,
    )

    assert result.best_params == {"max_depth": DEFAULT_MAX_DEPTH, "min_samples_leaf": 1}
    assert list(result.metrics["model"]) == [BASELINE_MODEL_LABEL, RF_MODEL_LABEL]
    assert result.baseline_metrics is not None
    assert result.final_fit_rows == len(model_df)
    assert list(result.final_model.feature_names_in_) == selected_features


def test_build_training_metadata_records_reproducibility_fields():
    selected_features = ["signal_a", "signal_b"]
    result = train_random_forest_model(
        make_modeling_frame(),
        selected_features,
        split_date="2023-12-26",
        n_jobs=1,
        tune=False,
        max_depth=DEFAULT_MAX_DEPTH,
        min_samples_leaf=1,
        n_estimators=5,
    )

    metadata = build_training_metadata(
        training=result,
        model_out="models/rf_model.pkl",
        features_path="data/features.csv",
        selected_features_path="data/selected_features.csv",
        selected_features=selected_features,
        n_jobs=1,
        tune=False,
    )

    assert metadata["model_type"] == "RandomForestRegressor"
    assert metadata["selected_features"] == selected_features
    assert metadata["target_column"] == TARGET_COLUMN
    assert metadata["train_rows"] == 4
    assert metadata["test_rows"] == 4
    assert metadata["final_fit_rows"] == 8
    assert metadata["baseline_metrics"] is not None
