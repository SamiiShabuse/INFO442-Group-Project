"""Model training and prediction utilities."""

from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from pandas.tseries.offsets import BDay

from portfolio_risk.config import (
    DATE_COLUMN,
    PREDICTED_VOLATILITY_COLUMN,
    TARGET_COLUMN,
    TICKER_COLUMN,
)


def load_selected_features(
    path: str | Path,
    *,
    target_column: str = TARGET_COLUMN,
    allow_target: bool = False,
) -> list[str]:
    """Load model features in the exact order used for training/prediction."""
    selected_features = pd.read_csv(path)

    if "feature" not in selected_features.columns:
        raise SystemExit("selected features CSV must contain a 'feature' column")

    features = selected_features["feature"].dropna().astype(str).tolist()

    if not features:
        raise SystemExit("selected features CSV did not contain any features")

    if not allow_target and target_column in features:
        raise SystemExit(f"selected features must not include target column '{target_column}'")

    return features


def find_date_column(df: pd.DataFrame) -> str:
    """Return the date column name accepted by project feature CSVs."""
    if DATE_COLUMN in df.columns:
        return DATE_COLUMN
    if "date" in df.columns:
        return "date"
    raise SystemExit("features CSV must contain a 'Date' or 'date' column")


def validate_model_features(model: Any, selected_features: list[str]) -> None:
    """Catch mismatches when a saved sklearn model remembers its fit columns."""
    model_features = getattr(model, "feature_names_in_", None)
    if model_features is None:
        return

    model_features = list(model_features)
    if model_features != selected_features:
        raise SystemExit(
            "Selected features do not match the model's fitted feature order. "
            f"Model expects {model_features}, but selected CSV provides {selected_features}."
        )


def load_predictive_model(path: str | Path):
    """Load a saved model artifact and verify it exposes predict()."""
    model = joblib.load(path)
    if not hasattr(model, "predict"):
        raise SystemExit("Loaded model object does not have a predict method")
    return model


def build_latest_feature_matrix(
    df: pd.DataFrame,
    date_col: str,
    selected_features: list[str],
) -> tuple[pd.Timestamp, list[str], pd.DataFrame]:
    """Build the latest complete model input matrix from a feature snapshot."""
    if TICKER_COLUMN not in df.columns:
        raise SystemExit("features CSV must contain a 'ticker' column")

    missing_features = [feature for feature in selected_features if feature not in df.columns]
    if missing_features:
        raise SystemExit(f"Missing selected feature columns: {missing_features}")

    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col])

    latest_date = df[date_col].max()
    latest_rows = df[df[date_col] == latest_date].copy()

    if latest_rows.empty:
        raise SystemExit("No rows found for the latest feature date")

    latest_rows = latest_rows.sort_values(TICKER_COLUMN)
    tickers = latest_rows[TICKER_COLUMN].astype(str).tolist()

    X = latest_rows[selected_features].apply(pd.to_numeric, errors="coerce")
    X.index = tickers

    rows_with_missing = X.isna().any(axis=1)
    if rows_with_missing.any():
        bad_tickers = X.index[rows_with_missing].tolist()
        raise SystemExit(
            "Latest feature rows contain missing or non-numeric selected features "
            f"for tickers: {bad_tickers}"
        )

    return latest_date, tickers, X


def predict_feature_matrix(
    model,
    X: pd.DataFrame,
    tickers: list[str],
) -> pd.Series:
    """Run a predictive model against a model-ready feature matrix."""
    if not hasattr(model, "predict"):
        raise SystemExit("Loaded model object does not have a predict method")

    return pd.Series(
        model.predict(X),
        index=tickers,
        name=PREDICTED_VOLATILITY_COLUMN,
    )


def next_business_day(date) -> pd.Timestamp:
    """Return the next business day after a feature date."""
    return pd.Timestamp(date) + BDay(1)


def build_wide_prediction_frame(
    predictions: pd.Series,
    target_date,
) -> pd.DataFrame:
    """Convert per-ticker predictions into the wide CSV shape used downstream."""
    predictions_df = predictions.to_frame().T
    predictions_df.index = [pd.Timestamp(target_date)]
    predictions_df.index.name = DATE_COLUMN
    return predictions_df
