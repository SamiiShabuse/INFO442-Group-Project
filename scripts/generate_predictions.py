"""Generate latest per-ticker volatility predictions from a saved RF model.

Example:
    python scripts/generate_predictions.py \
        --model data/processed/modeling/random_forest/rf_model.pkl \
        --features data/processed/features/feature_engineered_dataset.csv \
        --selected-features data/processed/features/selected_features.csv \
        --out data/processed/modeling/random_forest/live_predictions/latest_preds.csv

The output is a wide CSV with one row and ticker symbols as columns, which is
the shape expected by scripts/paper_trade.py.
"""

import argparse
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from portfolio_risk.modeling import (  # noqa: E402
    build_latest_feature_matrix,
    build_wide_prediction_frame,
    find_date_column,
    load_predictive_model,
    load_selected_features,
    next_business_day,
    predict_feature_matrix,
    validate_model_features,
)


def main(
    model_path: str,
    features_path: str,
    selected_features_path: str,
    out_path: str,
) -> None:
    model_path = Path(model_path)
    features_path = Path(features_path)
    selected_features_path = Path(selected_features_path)
    out_path = Path(out_path)

    out_path.parent.mkdir(parents=True, exist_ok=True)

    print("Loading features:", features_path)
    df = pd.read_csv(features_path, low_memory=False)
    date_col = find_date_column(df)

    print("Loading selected features:", selected_features_path)
    selected_features = load_selected_features(selected_features_path)

    latest_date, tickers, X = build_latest_feature_matrix(df, date_col, selected_features)

    print("Latest feature date:", latest_date.date())
    print("Predicting tickers:", len(tickers))
    print("Loading model:", model_path)
    model = load_predictive_model(model_path)
    validate_model_features(model, selected_features)

    predictions = predict_feature_matrix(model, X, tickers)
    predictions_df = build_wide_prediction_frame(
        predictions,
        target_date=next_business_day(latest_date),
    )

    predictions_df.to_csv(out_path)

    print("Wrote predictions to:", out_path)
    print("Preview:")
    print(predictions_df.iloc[:, :5])


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
