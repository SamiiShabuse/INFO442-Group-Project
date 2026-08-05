"""Archive the latest wide prediction CSV into dated files and a long log.

Example:
    python scripts/archive_predictions.py \
        --predictions predictions/latest_preds.csv \
        --out-dir predictions \
        --log predictions/prediction_log.csv
"""

import argparse
from pathlib import Path

import pandas as pd


def load_latest_predictions(path: Path) -> pd.DataFrame:
    predictions = pd.read_csv(path, index_col=0, parse_dates=True)
    if predictions.empty:
        raise SystemExit("prediction CSV did not contain any rows")

    latest = predictions.tail(1).copy()
    latest.index.name = "Date"
    latest.columns = latest.columns.astype(str)
    return latest


def archive_predictions(predictions_path: str, out_dir: str, log_path: str) -> None:
    predictions_path = Path(predictions_path)
    out_dir = Path(out_dir)
    log_path = Path(log_path)

    out_dir.mkdir(parents=True, exist_ok=True)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    latest = load_latest_predictions(predictions_path)
    target_date = pd.Timestamp(latest.index[0]).date().isoformat()

    dated_path = out_dir / f"preds_{target_date}.csv"
    latest.to_csv(dated_path)

    long_predictions = (
        latest.reset_index()
        .melt(
            id_vars="Date",
            var_name="ticker",
            value_name="predicted_future_volatility_20d",
        )
        .sort_values(["Date", "ticker"])
    )
    long_predictions["Date"] = pd.to_datetime(long_predictions["Date"]).dt.date.astype(str)

    if log_path.exists():
        prediction_log = pd.read_csv(log_path)
        prediction_log["Date"] = pd.to_datetime(prediction_log["Date"]).dt.date.astype(str)
        prediction_log = prediction_log[prediction_log["Date"] != target_date]
        prediction_log = pd.concat([prediction_log, long_predictions], ignore_index=True)
    else:
        prediction_log = long_predictions

    prediction_log = prediction_log.sort_values(["Date", "ticker"])
    prediction_log.to_csv(log_path, index=False)

    print("Archived latest predictions to:", dated_path)
    print("Updated prediction log:", log_path)
    print("Target date:", target_date)
    print("Tickers:", len(long_predictions))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Archive latest wide predictions by target date.")
    parser.add_argument(
        "--predictions",
        default="predictions/latest_preds.csv",
        help="Wide prediction CSV from generate_predictions.py",
    )
    parser.add_argument(
        "--out-dir",
        default="predictions",
        help="Directory for dated prediction CSVs",
    )
    parser.add_argument(
        "--log",
        default="predictions/prediction_log.csv",
        help="Long-format prediction log to create/update",
    )

    args = parser.parse_args()
    archive_predictions(
        predictions_path=args.predictions,
        out_dir=args.out_dir,
        log_path=args.log,
    )
