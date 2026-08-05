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
    """
    Load trained RF model and latest features; write per-ticker next-day predictions CSV.

    Usage:
      python scripts/generate_predictions.py \
        --model models/rf_model.pkl \
        --features data/processed/features/feature_engineered_dataset.csv \
        --out predictions/latest_preds.csv

    Notes:
    - Accepts feature CSVs with a date column named either `date` or `Date`.
    - Writes a single-row CSV where columns are tickers and the row index is the prediction target date (next business day).
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
        # Read without forcing parse_dates so we can accept either 'date' or 'Date'
        df = pd.read_csv(features_path, low_memory=False)

        # Accept either lowercase or capitalized date column
        if "date" in df.columns:
            date_col = "date"
        elif "Date" in df.columns:
            date_col = "Date"
        else:
            raise SystemExit("features CSV must contain a 'date' or 'Date' column")

        if "ticker" not in df.columns:
            raise SystemExit("features CSV must contain a 'ticker' column")

        # Ensure date column is parsed as datetime
        df[date_col] = pd.to_datetime(df[date_col])

        last_date = df[date_col].max()
        print("Latest feature date found:", last_date.date())

        df_latest = df[df[date_col] == last_date].copy()
        if df_latest.empty:
            raise SystemExit("No rows for latest date in features file")

        # Build X: drop common non-feature columns and keep numeric columns only
        drop_cols = [date_col, "ticker", "symbol", "adj_close", "close"]
        X = df_latest.drop(columns=[c for c in drop_cols if c in df_latest.columns], errors="ignore")
        X = X.select_dtypes(include=[np.number])

        tickers = df_latest["ticker"].astype(str).values
        X.index = tickers

        print("Loading model:", model_path)
        model = joblib.load(model_path)

        if not hasattr(model, "predict"):
            raise SystemExit("Model does not have a predict method")

        preds_array = model.predict(X)
        preds = pd.Series(preds_array, index=tickers)

        # Name the prediction row with next business day
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