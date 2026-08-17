"""Archive the latest wide prediction CSV into dated files and a long log.

Example:
    python scripts/archive_predictions.py \
        --predictions data/processed/modeling/random_forest/live_predictions/latest_preds.csv \
        --out-dir data/processed/modeling/random_forest/live_predictions \
        --log data/processed/modeling/random_forest/live_predictions/prediction_log.csv
"""

import argparse
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from portfolio_risk.prediction_archive import archive_latest_predictions  # noqa: E402


def main(predictions_path: str, out_dir: str, log_path: str) -> None:
    result = archive_latest_predictions(
        predictions_path=predictions_path,
        out_dir=out_dir,
        log_path=log_path,
    )

    print("Archived latest predictions to:", result.dated_path)
    print("Updated prediction log:", result.log_path)
    print("Target date:", result.target_date)
    print("Tickers:", result.ticker_count)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Archive latest wide predictions by target date.")
    parser.add_argument(
        "--predictions",
        default="data/processed/modeling/random_forest/live_predictions/latest_preds.csv",
        help="Wide prediction CSV from generate_predictions.py",
    )
    parser.add_argument(
        "--out-dir",
        default="data/processed/modeling/random_forest/live_predictions",
        help="Directory for dated prediction CSVs",
    )
    parser.add_argument(
        "--log",
        default="data/processed/modeling/random_forest/live_predictions/prediction_log.csv",
        help="Long-format prediction log to create/update",
    )

    args = parser.parse_args()
    main(
        predictions_path=args.predictions,
        out_dir=args.out_dir,
        log_path=args.log,
    )
