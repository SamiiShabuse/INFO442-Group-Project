"""Compare RF predictions with trailing 20-day realized volatility.

This is a same-day baseline comparison, not a future accuracy score. For
example, a prediction made from the 2026-08-04 feature row can be compared with
the trailing 20-day volatility ending on 2026-08-04.

Example:
    python scripts/compare_prediction_to_trailing_vol.py \
        --features data/processed/features/latest_feature_snapshot.csv \
        --predictions data/processed/modeling/random_forest/live_predictions/preds_2026-08-05.csv \
        --feature-date 2026-08-04 \
        --out data/processed/modeling/random_forest/live_evaluation/rf_vs_trailing_20d_ending_2026-08-04.csv
"""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


PREDICTED_COLUMN = "predicted_future_volatility_20d"
TRAILING_COLUMN = "trailing_volatility_20d"


def load_prediction_row(path: Path) -> tuple[pd.Timestamp, pd.DataFrame]:
    predictions = pd.read_csv(path, index_col=0, parse_dates=True)
    if predictions.empty:
        raise SystemExit("prediction CSV did not contain any rows")

    latest_prediction = predictions.tail(1)
    target_date = pd.Timestamp(latest_prediction.index[0]).normalize()

    long_predictions = (
        latest_prediction.reset_index()
        .melt(
            id_vars=latest_prediction.index.name or "Date",
            var_name="ticker",
            value_name=PREDICTED_COLUMN,
        )
        [["ticker", PREDICTED_COLUMN]]
    )
    long_predictions["ticker"] = long_predictions["ticker"].astype(str)
    long_predictions[PREDICTED_COLUMN] = pd.to_numeric(
        long_predictions[PREDICTED_COLUMN],
        errors="coerce",
    )

    return target_date, long_predictions


def compare_to_trailing_vol(
    features_path: str,
    predictions_path: str,
    feature_date: str,
    out_path: str,
    summary_out_path: str | None,
) -> None:
    features_path = Path(features_path)
    predictions_path = Path(predictions_path)
    out_path = Path(out_path)
    summary_path = Path(summary_out_path) if summary_out_path else out_path.with_suffix(".summary.csv")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.parent.mkdir(parents=True, exist_ok=True)

    feature_timestamp = pd.Timestamp(feature_date).normalize()
    features = pd.read_csv(features_path, parse_dates=["Date"], low_memory=False)
    features["Date"] = pd.to_datetime(features["Date"]).dt.normalize()

    required_columns = ["Date", "ticker", "rolling_volatility_20d"]
    missing_columns = [column for column in required_columns if column not in features.columns]
    if missing_columns:
        raise SystemExit(f"Feature snapshot is missing columns: {missing_columns}")

    feature_rows = features[features["Date"] == feature_timestamp].copy()
    if feature_rows.empty:
        raise SystemExit(f"No feature rows found for {feature_timestamp.date()}")

    feature_rows = feature_rows[
        ["Date", "ticker", "rolling_volatility_20d", "rolling_volatility_5d", "daily_return"]
    ].copy()
    feature_rows = feature_rows.rename(columns={"rolling_volatility_20d": TRAILING_COLUMN})
    feature_rows["ticker"] = feature_rows["ticker"].astype(str)
    feature_rows[TRAILING_COLUMN] = pd.to_numeric(feature_rows[TRAILING_COLUMN], errors="coerce")

    prediction_target_date, predictions = load_prediction_row(predictions_path)

    comparison = feature_rows.merge(predictions, on="ticker", how="inner")
    comparison = comparison.dropna(subset=[TRAILING_COLUMN, PREDICTED_COLUMN]).copy()

    if comparison.empty:
        raise SystemExit("No overlapping complete ticker rows between features and predictions")

    comparison["prediction_target_date"] = prediction_target_date
    comparison["prediction_minus_trailing"] = comparison[PREDICTED_COLUMN] - comparison[TRAILING_COLUMN]
    comparison["absolute_difference"] = comparison["prediction_minus_trailing"].abs()
    comparison["ratio_predicted_to_trailing"] = np.where(
        comparison[TRAILING_COLUMN] > 0,
        comparison[PREDICTED_COLUMN] / comparison[TRAILING_COLUMN],
        np.nan,
    )

    comparison = comparison.sort_values("absolute_difference", ascending=False)
    comparison.to_csv(out_path, index=False)

    correlation = comparison[[PREDICTED_COLUMN, TRAILING_COLUMN]].corr().iloc[0, 1]
    summary = {
        "feature_date": feature_timestamp.date().isoformat(),
        "prediction_target_date": prediction_target_date.date().isoformat(),
        "tickers": int(len(comparison)),
        "mean_predicted_future_volatility_20d": float(comparison[PREDICTED_COLUMN].mean()),
        "mean_trailing_volatility_20d": float(comparison[TRAILING_COLUMN].mean()),
        "mean_prediction_minus_trailing": float(comparison["prediction_minus_trailing"].mean()),
        "mean_absolute_difference": float(comparison["absolute_difference"].mean()),
        "correlation_predicted_vs_trailing": float(correlation),
    }
    pd.DataFrame([summary]).to_csv(summary_path, index=False)

    print("Wrote comparison to:", out_path)
    print("Wrote summary to:", summary_path)
    print(pd.DataFrame([summary]).T)
    print("\nLargest differences:")
    print(
        comparison[
            [
                "ticker",
                PREDICTED_COLUMN,
                TRAILING_COLUMN,
                "prediction_minus_trailing",
                "absolute_difference",
                "ratio_predicted_to_trailing",
            ]
        ]
        .head(10)
        .to_string(index=False)
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compare RF prediction with trailing 20-day volatility.")
    parser.add_argument(
        "--features",
        default="data/processed/features/latest_feature_snapshot.csv",
        help="Feature snapshot containing rolling_volatility_20d",
    )
    parser.add_argument(
        "--predictions",
        required=True,
        help="Wide prediction CSV from generate_predictions.py/archive_predictions.py",
    )
    parser.add_argument(
        "--feature-date",
        required=True,
        help="Date whose trailing 20-day volatility should be compared",
    )
    parser.add_argument(
        "--out",
        required=True,
        help="Detailed comparison CSV path",
    )
    parser.add_argument("--summary-out", default=None, help="Optional summary CSV path")

    args = parser.parse_args()
    compare_to_trailing_vol(
        features_path=args.features,
        predictions_path=args.predictions,
        feature_date=args.feature_date,
        out_path=args.out,
        summary_out_path=args.summary_out,
    )
