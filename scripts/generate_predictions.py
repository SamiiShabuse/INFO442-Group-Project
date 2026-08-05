"""Generate latest per-ticker volatility predictions from a saved RF model.

Example:
    python scripts/generate_predictions.py \
        --model models/rf_model.pkl \
        --features data/processed/features/feature_engineered_dataset.csv \
        --selected-features data/processed/features/selected_features.csv \
        --out predictions/latest_preds.csv

The output is a wide CSV with one row and ticker symbols as columns, which is
the shape expected by scripts/paper_trade.py.
"""

import argparse
from pathlib import Path

import joblib
import pandas as pd
from pandas.tseries.offsets import BDay


TARGET_COLUMN = "future_volatility_20d"


def load_selected_features(path: Path) -> list[str]:
    """Load the model feature list in the exact order used for prediction."""
    selected_features = pd.read_csv(path)

    if "feature" not in selected_features.columns:
        raise SystemExit("selected features CSV must contain a 'feature' column")

    features = selected_features["feature"].dropna().astype(str).tolist()

    if not features:
        raise SystemExit("selected features CSV did not contain any features")

    if TARGET_COLUMN in features:
        raise SystemExit(f"selected features must not include target column '{TARGET_COLUMN}'")

    return features


def find_date_column(df: pd.DataFrame) -> str:
    if "Date" in df.columns:
        return "Date"
    if "date" in df.columns:
        return "date"
    raise SystemExit("features CSV must contain a 'Date' or 'date' column")


def build_latest_feature_matrix(
    df: pd.DataFrame,
    date_col: str,
    selected_features: list[str],
) -> tuple[pd.Timestamp, list[str], pd.DataFrame]:
    if "ticker" not in df.columns:
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

    latest_rows = latest_rows.sort_values("ticker")
    tickers = latest_rows["ticker"].astype(str).tolist()

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


def validate_model_features(model, selected_features: list[str]) -> None:
    """Catch mismatches when the saved sklearn model remembers its fit columns."""
    model_features = getattr(model, "feature_names_in_", None)
    if model_features is None:
        return

    model_features = list(model_features)
    if model_features != selected_features:
        raise SystemExit(
            "Selected features do not match the model's fitted feature order. "
            f"Model expects {model_features}, but selected CSV provides {selected_features}."
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
    model = joblib.load(model_path)

    if not hasattr(model, "predict"):
        raise SystemExit("Loaded model object does not have a predict method")

    validate_model_features(model, selected_features)

    predictions = pd.Series(
        model.predict(X),
        index=tickers,
        name="predicted_future_volatility_20d",
    )

    target_date = latest_date + BDay(1)
    predictions_df = predictions.to_frame().T
    predictions_df.index = [target_date]
    predictions_df.index.name = "Date"

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
