"""Build a latest feature snapshot from current market data.

The script downloads current prices for the repo's asset universe, fetches
market/macro context where available, computes the same selected feature columns
used by the RF model, and writes a model-ready CSV:

    python scripts/refresh_latest_features.py \
        --out data/processed/features/latest_feature_snapshot.csv

The output intentionally does not include a known future-volatility target for
the newly downloaded dates. Today can be predicted now, but scored only after
the next 20 trading days have happened.
"""

import argparse
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from portfolio_risk.features import refresh_latest_feature_snapshot  # noqa: E402


def main(
    integrated_market_path: str,
    asset_metadata_path: str,
    selected_features_path: str,
    out_path: str,
    start_date: str | None,
    end_date: str | None,
) -> None:
    result = refresh_latest_feature_snapshot(
        integrated_market_path=integrated_market_path,
        asset_metadata_path=asset_metadata_path,
        selected_features_path=selected_features_path,
        out_path=out_path,
        start_date=start_date,
        end_date=end_date,
    )

    print("Wrote latest feature snapshot to:", result.out_path)
    print("Latest available market date:", result.latest_date.date())
    print(
        "Latest rows with complete selected features: "
        f"{result.complete_latest_rows} / {result.ticker_count}"
    )
    if result.missing_tickers:
        print("Tickers missing complete latest features:", result.missing_tickers)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Refresh latest model-ready feature rows.")
    parser.add_argument(
        "--integrated-market",
        default="data/processed/integrated/daily_market_data.csv",
        help="Historical integrated market data CSV",
    )
    parser.add_argument(
        "--asset-metadata",
        default="data/processed/integrated/asset_metadata.csv",
        help="Asset metadata CSV with ticker column",
    )
    parser.add_argument(
        "--selected-features",
        default="data/processed/features/selected_features.csv",
        help="Path to selected_features.csv",
    )
    parser.add_argument(
        "--out",
        default="data/processed/features/latest_feature_snapshot.csv",
        help="Output path for the refreshed feature snapshot",
    )
    parser.add_argument("--start-date", default=None, help="Optional download start date")
    parser.add_argument(
        "--end-date",
        default=None,
        help="Inclusive end date for market downloads; defaults to today",
    )

    args = parser.parse_args()
    main(
        integrated_market_path=args.integrated_market,
        asset_metadata_path=args.asset_metadata,
        selected_features_path=args.selected_features,
        out_path=args.out,
        start_date=args.start_date,
        end_date=args.end_date,
    )
