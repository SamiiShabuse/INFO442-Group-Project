"""
Load the trained RF model and latest features; write per-ticker next-day prediction CSVs.

Usage:
python scripts/generate_predictions.py \
    --model models/rf_model.pkl \
    --features data/processed/features/feature_engineered_dataset.csv \
    --out predictions/latest_preds.csv
"""
import argparse
from pathlib import Path
import pandas as pd
import numpy as np
import joblib # helps with parallel computing
from pandas.tseries.offsets import BDay # for business days

def main(model_path, features_path, out_path):
    model_path = Path(model_path)
    features_path = Path(features_path)
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    print("Loading features:", features_path)
    df = pd.read_csv(features_path, parse_dates=["date"], low_memory=False)

    if not {"date", "ticker"}.issubset(df.columns):
        raise SystemExit("feature CSV MUST HAVE 'date' and 'ticker' columns")

    last_date = df['date'].max()
    print("Latest feature date found:", last_date.date())

    df_latest = df[df["date"] == last_date].copy()
    if df_latest.empty:
        raise SystemExit("NO rows for latest date in features file")

    # Build X: drop non-feature columns (keep only numeric columns)
    drop_cols = ["date", "ticker", "symbol", "adj_close", "close"]
    X = df_latest.drop(columns=[c for c in drop_cols if c in df_latest.columns], errors="ignore")

    # If there are non-numeric cols, drop them
    X = X.select_dtypes(include=[np.number])
    tickers = df_latest['ticker'].values
    X.index = tickers

    print("Loading model:", model_path)
    model = joblib.load(model_path)

    # Predict: model should accept rows for each ticker (one row per ticker)
    # If the model however is a classifer that provides predict_proba, use the relevent column; otherwise use predict.
    if hasattr(model, "predict"):
        preds = model.predict(X)
    else:
        raise SystemExit("Model does not have a predict method.")

    preds = pd.Series(preds, index=tickers, name=str((last_date + BDay(1).date())))  

    # Build a single-row DataFrame where columns are tickers and index is the target/prediction date
    preds_df = preds.to_frame().T
    preds_df.index = pd.to_datetime(preds_df.index)

    preds_df.to_csv(out_path, index=True)
    print("Wrote predictiosn to:", out_path)
    print("Preview:")
    print(preds_df.iloc[0].head())

if __name__ == "__main__":
    p = argparse.ArgumentParser
    p.add_argument("--model", required=True, help="Path to trained model (joblib .pkl)")
    p.add_argument("--features", required=True, help="Path to feature CSV (must include date, ticker info)")
    p.add_argument("--out", required=True, help="Output CSV path (predictions)")
    args = p.parse_args()
    main(args.model, args.feature, args.out)