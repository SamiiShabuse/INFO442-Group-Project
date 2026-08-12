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
import sys
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from portfolio_risk.evaluation import (  # noqa: E402
    largest_absolute_error_table,
    run_completed_future_window_evaluation,
)


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
    result = run_completed_future_window_evaluation(
        model_path=model_path,
        features_path=features_path,
        selected_features_path=selected_features_path,
        out_path=out_path,
        summary_out=summary_out,
        horizon=horizon,
        eval_date=eval_date,
        min_tickers=min_tickers,
    )

    print("Wrote detailed evaluation to:", result.out_path)
    print("Wrote summary to:", result.summary_out_path)
    print(pd.DataFrame([result.summary]).T)
    print("\nLargest absolute errors:")
    print(largest_absolute_error_table(result.evaluation_rows).to_string(index=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Evaluate recent RF predictions against realized 20d volatility."
    )
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
