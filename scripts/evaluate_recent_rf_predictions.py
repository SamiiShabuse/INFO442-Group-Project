"""Evaluate RF predictions over the latest completed future-volatility window.

This script predicts from a historical feature date whose next N trading days
are already present in the feature snapshot, computes realized future
volatility over those N days, and compares predicted vs actual volatility.

Example:
    python scripts/evaluate_recent_rf_predictions.py \
        --model data/processed/modeling/random_forest/rf_model.pkl \
        --features data/processed/features/latest_feature_snapshot.csv \
        --selected-features data/processed/features/selected_features.csv \
        --out data/processed/modeling/random_forest/live_evaluation/latest_20d_rf_evaluation.csv
"""

import argparse
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


ACTUAL_COLUMN = "actual_future_volatility_20d"
PREDICTED_COLUMN = "predicted_future_volatility_20d"


def load_selected_features(path: Path) -> list[str]:
    selected_features = pd.read_csv(path)
    if "feature" not in selected_features.columns:
        raise SystemExit("selected features CSV must contain a 'feature' column")

    features = selected_features["feature"].dropna().astype(str).tolist()
    if not features:
        raise SystemExit("selected features CSV did not contain any features")

    return features


def validate_model_features(model, selected_features: list[str]) -> None:
    model_features = getattr(model, "feature_names_in_", None)
    if model_features is None:
        return

    model_features = list(model_features)
    if model_features != selected_features:
        raise SystemExit(
            "Selected features do not match the model's fitted feature order. "
            f"Model expects {model_features}, but selected CSV provides {selected_features}."
        )


def add_future_window_actuals(df: pd.DataFrame, horizon: int) -> pd.DataFrame:
    df = df.sort_values(["ticker", "Date"]).copy()
    df["daily_return"] = pd.to_numeric(df["daily_return"], errors="coerce")
    df[ACTUAL_COLUMN] = (
        df.groupby("ticker")["daily_return"]
        .transform(lambda returns: returns.rolling(window=horizon).std().shift(-horizon))
    )
    df["future_window_start"] = df.groupby("ticker")["Date"].shift(-1)
    df["future_window_end"] = df.groupby("ticker")["Date"].shift(-horizon)
    return df


def choose_evaluation_date(
    df: pd.DataFrame,
    selected_features: list[str],
    requested_date: str | None,
    min_tickers: int | None,
) -> pd.Timestamp:
    required_columns = selected_features + [ACTUAL_COLUMN]
    complete_rows = df.dropna(subset=required_columns).copy()

    if complete_rows.empty:
        raise SystemExit("No rows have both complete features and a realized future-volatility target")

    if requested_date:
        eval_date = pd.Timestamp(requested_date).normalize()
        rows_on_date = complete_rows[complete_rows["Date"] == eval_date]
        if rows_on_date.empty:
            raise SystemExit(f"No complete evaluation rows found for {eval_date.date()}")
        return eval_date

    ticker_count = df["ticker"].nunique()
    required_tickers = min_tickers or ticker_count
    complete_counts = complete_rows.groupby("Date")["ticker"].nunique()
    eligible_dates = complete_counts[complete_counts >= required_tickers]

    if eligible_dates.empty:
        raise SystemExit(
            f"No evaluation date had at least {required_tickers} tickers with complete realized windows"
        )

    return pd.Timestamp(eligible_dates.index.max()).normalize()


def main(
    model_path: str,
    features_path: str,
    selected_features_path: str,
    out_path: str,
    summary_out: str | None,
    horizon: int,
    eval_date: str | None,
    min_tickers: int | None,
) -> None:
    model_path = Path(model_path)
    features_path = Path(features_path)
    selected_features_path = Path(selected_features_path)
    out_path = Path(out_path)
    summary_out_path = Path(summary_out) if summary_out else out_path.with_suffix(".summary.csv")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    summary_out_path.parent.mkdir(parents=True, exist_ok=True)

    selected_features = load_selected_features(selected_features_path)
    df = pd.read_csv(features_path, parse_dates=["Date"], low_memory=False)
    df["Date"] = pd.to_datetime(df["Date"]).dt.normalize()

    missing_columns = [column for column in selected_features + ["daily_return"] if column not in df.columns]
    if missing_columns:
        raise SystemExit(f"Feature snapshot is missing columns: {missing_columns}")

    for column in selected_features:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    df = add_future_window_actuals(df, horizon)
    chosen_date = choose_evaluation_date(df, selected_features, eval_date, min_tickers)

    evaluation_rows = (
        df[df["Date"] == chosen_date]
        .dropna(subset=selected_features + [ACTUAL_COLUMN])
        .sort_values("ticker")
        .copy()
    )

    if evaluation_rows.empty:
        raise SystemExit(f"No complete rows to evaluate on {chosen_date.date()}")

    model = joblib.load(model_path)
    if not hasattr(model, "predict"):
        raise SystemExit("Loaded model object does not have a predict method")
    validate_model_features(model, selected_features)

    X = evaluation_rows[selected_features]
    evaluation_rows[PREDICTED_COLUMN] = model.predict(X)
    evaluation_rows["error"] = evaluation_rows[ACTUAL_COLUMN] - evaluation_rows[PREDICTED_COLUMN]
    evaluation_rows["absolute_error"] = evaluation_rows["error"].abs()
    evaluation_rows["squared_error"] = evaluation_rows["error"] ** 2

    y_true = evaluation_rows[ACTUAL_COLUMN]
    y_pred = evaluation_rows[PREDICTED_COLUMN]
    summary = {
        "evaluation_feature_date": chosen_date.date().isoformat(),
        "horizon_trading_days": horizon,
        "tickers": int(len(evaluation_rows)),
        "latest_market_date_in_snapshot": df["Date"].max().date().isoformat(),
        "mean_future_window_start": evaluation_rows["future_window_start"].min().date().isoformat(),
        "mean_future_window_end": evaluation_rows["future_window_end"].max().date().isoformat(),
        "MAE": float(mean_absolute_error(y_true, y_pred)),
        "RMSE": float(np.sqrt(mean_squared_error(y_true, y_pred))),
        "R2": float(r2_score(y_true, y_pred)) if len(evaluation_rows) > 1 else np.nan,
    }

    output_columns = [
        "Date",
        "ticker",
        "future_window_start",
        "future_window_end",
        PREDICTED_COLUMN,
        ACTUAL_COLUMN,
        "error",
        "absolute_error",
        "squared_error",
    ]
    evaluation_rows[output_columns].to_csv(out_path, index=False)
    pd.DataFrame([summary]).to_csv(summary_out_path, index=False)

    print("Wrote detailed evaluation to:", out_path)
    print("Wrote summary to:", summary_out_path)
    print(pd.DataFrame([summary]).T)
    print("\nLargest absolute errors:")
    print(
        evaluation_rows[
            ["ticker", PREDICTED_COLUMN, ACTUAL_COLUMN, "absolute_error"]
        ]
        .sort_values("absolute_error", ascending=False)
        .head(8)
        .to_string(index=False)
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate recent RF predictions against realized 20d volatility.")
    parser.add_argument(
        "--model",
        default="data/processed/modeling/random_forest/rf_model.pkl",
        help="Path to trained joblib model",
    )
    parser.add_argument(
        "--features",
        default="data/processed/features/latest_feature_snapshot.csv",
        help="Feature snapshot containing enough future rows for realized-vol evaluation",
    )
    parser.add_argument(
        "--selected-features",
        default="data/processed/features/selected_features.csv",
        help="Path to selected_features.csv",
    )
    parser.add_argument(
        "--out",
        default="data/processed/modeling/random_forest/live_evaluation/latest_20d_rf_evaluation.csv",
        help="Detailed per-ticker output CSV",
    )
    parser.add_argument("--summary-out", default=None, help="Optional summary CSV path")
    parser.add_argument("--horizon", type=int, default=20, help="Future trading-day horizon")
    parser.add_argument(
        "--eval-date",
        default=None,
        help="Optional feature date to evaluate; defaults to latest date with a complete future window",
    )
    parser.add_argument(
        "--min-tickers",
        type=int,
        default=None,
        help="Minimum complete tickers required when auto-selecting eval date",
    )

    args = parser.parse_args()
    main(
        model_path=args.model,
        features_path=args.features,
        selected_features_path=args.selected_features,
        out_path=args.out,
        summary_out=args.summary_out,
        horizon=args.horizon,
        eval_date=args.eval_date,
        min_tickers=args.min_tickers,
    )
