"""Model evaluation utilities."""

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from portfolio_risk.config import (
    ACTUAL_VOLATILITY_COLUMN,
    DATE_COLUMN,
    PREDICTED_VOLATILITY_COLUMN,
    TICKER_COLUMN,
)
from portfolio_risk.modeling import validate_model_features


TRAILING_VOLATILITY_COLUMN = "trailing_volatility_20d"


def regression_metrics(y_true: pd.Series, y_pred) -> dict[str, float]:
    """Return common regression metrics used across model scripts."""
    r2 = float(r2_score(y_true, y_pred)) if len(y_true) > 1 else np.nan
    return {
        "MAE": float(mean_absolute_error(y_true, y_pred)),
        "RMSE": float(np.sqrt(mean_squared_error(y_true, y_pred))),
        "R2": r2,
    }


def add_future_window_actuals(df: pd.DataFrame, horizon: int) -> pd.DataFrame:
    """Add realized future-volatility columns for a completed horizon."""
    df = df.sort_values([TICKER_COLUMN, DATE_COLUMN]).copy()
    df["daily_return"] = pd.to_numeric(df["daily_return"], errors="coerce")
    df[ACTUAL_VOLATILITY_COLUMN] = (
        df.groupby(TICKER_COLUMN)["daily_return"]
        .transform(lambda returns: returns.rolling(window=horizon).std().shift(-horizon))
    )
    df["future_window_start"] = df.groupby(TICKER_COLUMN)[DATE_COLUMN].shift(-1)
    df["future_window_end"] = df.groupby(TICKER_COLUMN)[DATE_COLUMN].shift(-horizon)
    return df


def choose_evaluation_date(
    df: pd.DataFrame,
    selected_features: list[str],
    requested_date: str | None,
    min_tickers: int | None,
) -> pd.Timestamp:
    """Choose the latest feature date with a completed future window."""
    required_columns = selected_features + [ACTUAL_VOLATILITY_COLUMN]
    complete_rows = df.dropna(subset=required_columns).copy()

    if complete_rows.empty:
        raise SystemExit("No rows have both complete features and a realized future-volatility target")

    if requested_date:
        eval_date = pd.Timestamp(requested_date).normalize()
        rows_on_date = complete_rows[complete_rows[DATE_COLUMN] == eval_date]
        if rows_on_date.empty:
            raise SystemExit(f"No complete evaluation rows found for {eval_date.date()}")
        return eval_date

    ticker_count = df[TICKER_COLUMN].nunique()
    required_tickers = min_tickers or ticker_count
    complete_counts = complete_rows.groupby(DATE_COLUMN)[TICKER_COLUMN].nunique()
    eligible_dates = complete_counts[complete_counts >= required_tickers]

    if eligible_dates.empty:
        raise SystemExit(
            f"No evaluation date had at least {required_tickers} tickers with complete realized windows"
        )

    return pd.Timestamp(eligible_dates.index.max()).normalize()


def evaluate_completed_future_window(
    features: pd.DataFrame,
    model,
    selected_features: list[str],
    *,
    horizon: int,
    eval_date: str | None = None,
    min_tickers: int | None = None,
) -> tuple[pd.DataFrame, dict]:
    """Evaluate predictions on the latest completed future-volatility window."""
    df = features.copy()
    df[DATE_COLUMN] = pd.to_datetime(df[DATE_COLUMN]).dt.normalize()

    missing_columns = [
        column
        for column in selected_features + ["daily_return"]
        if column not in df.columns
    ]
    if missing_columns:
        raise SystemExit(f"Feature snapshot is missing columns: {missing_columns}")

    for column in selected_features:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    df = add_future_window_actuals(df, horizon)
    chosen_date = choose_evaluation_date(df, selected_features, eval_date, min_tickers)

    evaluation_rows = (
        df[df[DATE_COLUMN] == chosen_date]
        .dropna(subset=selected_features + [ACTUAL_VOLATILITY_COLUMN])
        .sort_values(TICKER_COLUMN)
        .copy()
    )

    if evaluation_rows.empty:
        raise SystemExit(f"No complete rows to evaluate on {chosen_date.date()}")

    validate_model_features(model, selected_features)
    evaluation_rows[PREDICTED_VOLATILITY_COLUMN] = model.predict(
        evaluation_rows[selected_features]
    )
    evaluation_rows["error"] = (
        evaluation_rows[ACTUAL_VOLATILITY_COLUMN]
        - evaluation_rows[PREDICTED_VOLATILITY_COLUMN]
    )
    evaluation_rows["absolute_error"] = evaluation_rows["error"].abs()
    evaluation_rows["squared_error"] = evaluation_rows["error"] ** 2

    metrics = regression_metrics(
        evaluation_rows[ACTUAL_VOLATILITY_COLUMN],
        evaluation_rows[PREDICTED_VOLATILITY_COLUMN],
    )
    summary = {
        "evaluation_feature_date": chosen_date.date().isoformat(),
        "horizon_trading_days": horizon,
        "tickers": int(len(evaluation_rows)),
        "latest_market_date_in_snapshot": df[DATE_COLUMN].max().date().isoformat(),
        "mean_future_window_start": evaluation_rows["future_window_start"].min().date().isoformat(),
        "mean_future_window_end": evaluation_rows["future_window_end"].max().date().isoformat(),
        **metrics,
    }

    output_columns = [
        DATE_COLUMN,
        TICKER_COLUMN,
        "future_window_start",
        "future_window_end",
        PREDICTED_VOLATILITY_COLUMN,
        ACTUAL_VOLATILITY_COLUMN,
        "error",
        "absolute_error",
        "squared_error",
    ]
    return evaluation_rows[output_columns], summary


def load_prediction_row(path) -> tuple[pd.Timestamp, pd.DataFrame]:
    """Load the latest row from a wide prediction CSV as long per-ticker rows."""
    predictions = pd.read_csv(path, index_col=0, parse_dates=True)
    if predictions.empty:
        raise SystemExit("prediction CSV did not contain any rows")

    latest_prediction = predictions.tail(1)
    target_date = pd.Timestamp(latest_prediction.index[0]).normalize()

    long_predictions = (
        latest_prediction.reset_index()
        .melt(
            id_vars=latest_prediction.index.name or DATE_COLUMN,
            var_name=TICKER_COLUMN,
            value_name=PREDICTED_VOLATILITY_COLUMN,
        )
        [[TICKER_COLUMN, PREDICTED_VOLATILITY_COLUMN]]
    )
    long_predictions[TICKER_COLUMN] = long_predictions[TICKER_COLUMN].astype(str)
    long_predictions[PREDICTED_VOLATILITY_COLUMN] = pd.to_numeric(
        long_predictions[PREDICTED_VOLATILITY_COLUMN],
        errors="coerce",
    )

    return target_date, long_predictions


def compare_prediction_to_trailing_volatility(
    features: pd.DataFrame,
    predictions: pd.DataFrame,
    prediction_target_date: pd.Timestamp,
    feature_date: str,
) -> tuple[pd.DataFrame, dict]:
    """Compare RF forecasts with trailing 20-day realized volatility."""
    feature_timestamp = pd.Timestamp(feature_date).normalize()
    features = features.copy()
    features[DATE_COLUMN] = pd.to_datetime(features[DATE_COLUMN]).dt.normalize()

    required_columns = [DATE_COLUMN, TICKER_COLUMN, "rolling_volatility_20d"]
    missing_columns = [column for column in required_columns if column not in features.columns]
    if missing_columns:
        raise SystemExit(f"Feature snapshot is missing columns: {missing_columns}")

    feature_rows = features[features[DATE_COLUMN] == feature_timestamp].copy()
    if feature_rows.empty:
        raise SystemExit(f"No feature rows found for {feature_timestamp.date()}")

    feature_rows = feature_rows[
        [DATE_COLUMN, TICKER_COLUMN, "rolling_volatility_20d", "rolling_volatility_5d", "daily_return"]
    ].copy()
    feature_rows = feature_rows.rename(
        columns={"rolling_volatility_20d": TRAILING_VOLATILITY_COLUMN}
    )
    feature_rows[TICKER_COLUMN] = feature_rows[TICKER_COLUMN].astype(str)
    feature_rows[TRAILING_VOLATILITY_COLUMN] = pd.to_numeric(
        feature_rows[TRAILING_VOLATILITY_COLUMN],
        errors="coerce",
    )

    comparison = feature_rows.merge(predictions, on=TICKER_COLUMN, how="inner")
    comparison = comparison.dropna(
        subset=[TRAILING_VOLATILITY_COLUMN, PREDICTED_VOLATILITY_COLUMN]
    ).copy()

    if comparison.empty:
        raise SystemExit("No overlapping complete ticker rows between features and predictions")

    comparison["prediction_target_date"] = prediction_target_date
    comparison["prediction_minus_trailing"] = (
        comparison[PREDICTED_VOLATILITY_COLUMN]
        - comparison[TRAILING_VOLATILITY_COLUMN]
    )
    comparison["absolute_difference"] = comparison["prediction_minus_trailing"].abs()
    comparison["ratio_predicted_to_trailing"] = np.where(
        comparison[TRAILING_VOLATILITY_COLUMN] > 0,
        comparison[PREDICTED_VOLATILITY_COLUMN] / comparison[TRAILING_VOLATILITY_COLUMN],
        np.nan,
    )

    comparison = comparison.sort_values("absolute_difference", ascending=False)
    correlation = comparison[
        [PREDICTED_VOLATILITY_COLUMN, TRAILING_VOLATILITY_COLUMN]
    ].corr().iloc[0, 1]
    summary = {
        "feature_date": feature_timestamp.date().isoformat(),
        "prediction_target_date": prediction_target_date.date().isoformat(),
        "tickers": int(len(comparison)),
        "mean_predicted_future_volatility_20d": float(
            comparison[PREDICTED_VOLATILITY_COLUMN].mean()
        ),
        "mean_trailing_volatility_20d": float(
            comparison[TRAILING_VOLATILITY_COLUMN].mean()
        ),
        "mean_prediction_minus_trailing": float(
            comparison["prediction_minus_trailing"].mean()
        ),
        "mean_absolute_difference": float(comparison["absolute_difference"].mean()),
        "correlation_predicted_vs_trailing": float(correlation),
    }

    return comparison, summary
