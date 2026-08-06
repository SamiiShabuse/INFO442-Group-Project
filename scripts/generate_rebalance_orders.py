import argparse
import sys
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from order_generation import generate_rebalance_orders, load_current_positions, load_latest_prices
from portfolio_optimizer import (
    BENCHMARK,
    build_rf_predicted_covariance_matrix,
    load_returns_matrix,
    load_risk_free_rate,
    optimize_portfolio,
)

def load_live_predictions(path: Path, include_benchmark: bool) -> tuple[pd.Timestamp, pd.DataFrame, list[str]]:
    pass