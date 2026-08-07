"""Create a sample current-positions CSV for rebalance-order testing.

Example:
    python scripts/create_sample_current_positions.py

This file is only for simulation. It gives generate_rebalance_orders.py an
example existing portfolio so the output can include true rebalance behavior
instead of assuming the account starts from cash.
"""

import argparse
from pathlib import Path

import pandas as pd


DEFAULT_OUTPUT = "data/processed/portfolio_optimization/sample_current_positions.csv"

SAMPLE_POSITIONS = [
    {"ticker": "AAPL", "quantity": 20},
    {"ticker": "MSFT", "quantity": 8},
    {"ticker": "GLD", "quantity": 5},
    {"ticker": "TLT", "quantity": 50},
    {"ticker": "AGG", "quantity": 100},
    {"ticker": "AMZN", "quantity": 4},
    {"ticker": "KO", "quantity": 25},
    {"ticker": "V", "quantity": 6},
]


def create_sample_positions(output_path: str, force: bool) -> None:
    output_path = Path(output_path)

    if output_path.exists() and not force:
        raise SystemExit(
            f"{output_path} already exists. Use --force to overwrite it."
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    positions = pd.DataFrame(SAMPLE_POSITIONS)
    positions.to_csv(output_path, index=False)

    print("Wrote sample current positions to:", output_path)
    print(positions)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Create a sample current-positions CSV for rebalance testing."
    )
    parser.add_argument(
        "--out",
        default=DEFAULT_OUTPUT,
        help="Output CSV path with ticker,quantity columns",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite the output file if it already exists",
    )

    args = parser.parse_args()
    create_sample_positions(args.out, args.force)
