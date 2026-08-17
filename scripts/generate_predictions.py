"""Generate latest per-ticker volatility predictions from a saved RF model.

Example:
    python scripts/generate_predictions.py \
        --model data/processed/modeling/random_forest/rf_model.pkl \
        --features data/processed/features/feature_engineered_dataset.csv \
        --selected-features data/processed/features/selected_features.csv \
        --out data/processed/modeling/random_forest/live_predictions/latest_preds.csv

The output is a wide CSV with one row and ticker symbols as columns, which is
the shape expected by downstream paper-trading and rebalance scripts.
"""

import argparse
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from portfolio_risk.prediction import run_latest_prediction_generation  # noqa: E402


def main(
    model_path: str,
    features_path: str,
    selected_features_path: str,
    out_path: str,
) -> None:
    print("Loading features:", features_path)
    print("Loading selected features:", selected_features_path)
    print("Loading model:", model_path)

    run_result = run_latest_prediction_generation(
        model_path=model_path,
        features_path=features_path,
        selected_features_path=selected_features_path,
        out_path=out_path,
    )
    result = run_result.result

    print("Latest feature date:", result.latest_feature_date.date())
    print("Prediction target date:", result.prediction_target_date.date())
    print("Predicting tickers:", len(result.tickers))
    print("Wrote predictions to:", run_result.out_path)
    print("Preview:")
    print(result.prediction_frame.iloc[:, :5])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate latest RF volatility predictions from model-ready features."
    )
    parser.add_argument("--model", required=True, help="Path to trained joblib model")
    parser.add_argument(
        "--features",
        required=True,
        help="Path to feature CSV with Date/date and ticker columns",
    )
    parser.add_argument(
        "--selected-features",
        default="data/processed/features/selected_features.csv",
        help="Path to selected_features.csv",
    )
    parser.add_argument("--out", required=True, help="Output prediction CSV path")

    args = parser.parse_args()
    main(
        model_path=args.model,
        features_path=args.features,
        selected_features_path=args.selected_features,
        out_path=args.out,
    )
