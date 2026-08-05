# scripts/generate_predictions.py
"""
Load trained RF model and latest features; write per-ticker next-day predictions CSV.

Usage:
python scripts/generate_predictions.py \
    --model models/rf_model.pkl \
    --features data/processed/features/feature_engineered_dataset.csv \
    --out predictions/latest_preds.csv

How it Works:
- Loads `feature_engineered_dataset.csv and expects columns `date` and ticker`.
- Takes teh latest date's row, forms one feature row per ticker and then writes a CSV
"""
import argparse
from pathlib import Path
import pandas as pd
import numpy as np
import joblib
from pandas.tseries.offsets import BDay

def main(model_path, features_path, out_path):
    model_path = Path(model_path)
    features_path = Path(features_path)
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    print("Loading features:", features_path)
    df = pd.read_csv(features_path, parse_dates=["date"], low_memory=False)

    if not {"date", "ticker"}.issubset(df.columns):
        raise SystemExit("features CSV must contain 'date' and 'ticker' columns")

    last_date = df["date"].max()
    print("Latest feature date found:", last_date.date())

    df_latest = df[df["date"] == last_date].copy()
    if df_latest.empty:
        raise SystemExit("No rows for latest date in features file")

    # Build X: drop non-feature columns (keep only numeric columns)
    drop_cols = ["date", "ticker", "symbol", "adj_close", "close"]
    X = df_latest.drop(columns=[c for c in drop_cols if c in df_latest.columns], errors="ignore")

    # Keep only numeric features
    X = X.select_dtypes(include=[np.number])
    tickers = df_latest["ticker"].astype(str).values
    if X.shape[0] != len(tickers):
        # reorder/align if needed
        X = X.reset_index(drop=True)
    X.index = tickers

    print("Loading model:", model_path)
    model = joblib.load(model_path)

    if not hasattr(model, "predict"):
        raise SystemExit("Model does not have a predict method")

    preds_array = model.predict(X)
    preds = pd.Series(preds_array, index=tickers)

    # Name row with next business day
    next_bd = (pd.to_datetime(last_date) + BDay(1)).date()
    preds_df = preds.to_frame().T
    preds_df.index = pd.to_datetime([next_bd])

    preds_df.to_csv(out_path, index=True)
    print("Wrote predictions to:", out_path)
    print("Preview:")
    print(preds_df.iloc[0].head())

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--model", required=True, help="Path to trained model (joblib .pkl)")
    p.add_argument("--features", required=True, help="Path to feature CSV (must include date,ticker)")
    p.add_argument("--out", required=True, help="Output CSV path (predictions)")
    args = p.parse_args()
    main(args.model, args.features, args.out)