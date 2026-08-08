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
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from portfolio_risk.config import PREDICTED_VOLATILITY_COLUMN  # noqa: E402
from portfolio_risk.evaluation import (  # noqa: E402
    TRAILING_VOLATILITY_COLUMN,
    compare_prediction_to_trailing_volatility,
    load_prediction_row,
)


def main(
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

    features = pd.read_csv(features_path, parse_dates=["Date"], low_memory=False)
    prediction_target_date, predictions = load_prediction_row(predictions_path)
    comparison, summary = compare_prediction_to_trailing_volatility(
        features=features,
        predictions=predictions,
        prediction_target_date=prediction_target_date,
        feature_date=feature_date,
    )

    comparison.to_csv(out_path, index=False)
    pd.DataFrame([summary]).to_csv(summary_path, index=False)

    print("Wrote comparison to:", out_path)
    print("Wrote summary to:", summary_path)
    print(pd.DataFrame([summary]).T)
    print("\nLargest differences:")
    print(
        comparison[
            [
                "ticker",
                PREDICTED_VOLATILITY_COLUMN,
                TRAILING_VOLATILITY_COLUMN,
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
    main(
        features_path=args.features,
        predictions_path=args.predictions,
        feature_date=args.feature_date,
        out_path=args.out,
        summary_out_path=args.summary_out,
    )
