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

from portfolio_risk.evaluation import (  # noqa: E402
    largest_trailing_difference_table,
    run_trailing_volatility_comparison,
)


def main(
    features_path: str,
    predictions_path: str,
    feature_date: str,
    out_path: str,
    summary_out_path: str | None,
) -> None:
    result = run_trailing_volatility_comparison(
        features_path=features_path,
        predictions_path=predictions_path,
        feature_date=feature_date,
        out_path=out_path,
        summary_out_path=summary_out_path,
    )

    print("Wrote comparison to:", result.out_path)
    print("Wrote summary to:", result.summary_out_path)
    print(pd.DataFrame([result.summary]).T)
    print("\nLargest differences:")
    print(largest_trailing_difference_table(result.comparison).to_string(index=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Compare RF prediction with trailing 20-day volatility."
    )
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
