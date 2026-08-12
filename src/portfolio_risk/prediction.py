"""Reusable workflow for generating latest volatility predictions."""

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from portfolio_risk.modeling import (
    build_latest_feature_matrix,
    build_wide_prediction_frame,
    find_date_column,
    load_predictive_model,
    load_selected_features,
    next_business_day,
    predict_feature_matrix,
    validate_model_features,
)


@dataclass(frozen=True)
class LatestPredictionResult:
    """In-memory result of predicting from the latest feature rows."""

    latest_feature_date: pd.Timestamp
    prediction_target_date: pd.Timestamp
    tickers: list[str]
    predictions: pd.Series
    prediction_frame: pd.DataFrame


@dataclass(frozen=True)
class LatestPredictionRunResult:
    """File-backed prediction result returned by the CLI workflow."""

    result: LatestPredictionResult
    out_path: Path


def build_latest_prediction_result(
    features: pd.DataFrame,
    model,
    selected_features: list[str],
) -> LatestPredictionResult:
    """Predict future volatility from the latest complete feature date."""
    date_col = find_date_column(features)
    latest_date, tickers, X = build_latest_feature_matrix(
        features,
        date_col,
        selected_features,
    )

    validate_model_features(model, selected_features)
    predictions = predict_feature_matrix(model, X, tickers)
    target_date = next_business_day(latest_date)
    prediction_frame = build_wide_prediction_frame(predictions, target_date)

    return LatestPredictionResult(
        latest_feature_date=latest_date,
        prediction_target_date=target_date,
        tickers=tickers,
        predictions=predictions,
        prediction_frame=prediction_frame,
    )


def run_latest_prediction_generation(
    *,
    model_path: str | Path,
    features_path: str | Path,
    selected_features_path: str | Path,
    out_path: str | Path,
) -> LatestPredictionRunResult:
    """Load project files, generate latest predictions, and write the wide CSV."""
    model_path = Path(model_path)
    features_path = Path(features_path)
    selected_features_path = Path(selected_features_path)
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    features = pd.read_csv(features_path, low_memory=False)
    selected_features = load_selected_features(selected_features_path)
    model = load_predictive_model(model_path)

    result = build_latest_prediction_result(
        features=features,
        model=model,
        selected_features=selected_features,
    )
    result.prediction_frame.to_csv(out_path)

    return LatestPredictionRunResult(
        result=result,
        out_path=out_path,
    )
