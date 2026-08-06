from pathlib import Path

import numpy as np
import pandas as pd

def load_latest_prices(integrated_path: Path, tickers: list[str], as_of_date=None) -> pd.Series:
    market = pd.read_csv(integrated_path / "daily_market_data.csv", parse_dates=["Date"])

    if as_of_date is not None:
        market = market[market["Date"] < pd.Timestamp(as_of_date)]

    latest_prices = (
        market[market['ticker'].isin(tickers)]
        .sort_values(['ticker', 'Date'])
        .groupby('ticker')
        .tail(1)
        .set_index('ticker')['adjusted_close']
        .astype(float)
    )

    missing = sorted(set(tickers) - set(latest_prices.index))
    if missing:
        raise ValueError(f"Missing latest prices for: {missing}")

    return latest_prices.reindex(tickers)

def load_current_positions(path: str | None) -> pd.DataFrame:
    if path is None:
        return pd.DataFrame(columsn=['ticker', 'quantity'])

    positions = pd.read_csv(path)
    if 'qty' in positions.columns and 'quantity' not in positions.columns:
        positions = positions.rename(columns={'qty': 'quantity'})

    required = {'tickers', 'quantity'}
    missing = required - set(positions.columns)

    if missing:
        raise ValueError(f"Current position CSV is missing columns: {missing}")

    positions['ticker'] = positions['ticker'].astype(str)
    positions['quantity'] = pd.to_numeric(positions['quantity'], errors="coerce").fillna(0)
    return positions[['ticker', 'quantity']]

def generate_rebalance_orders(
    target_weights: pd.Series,
    prices: pd.Series,
    portfolio_value: float,
    current_positions: pd.DataFrame | None = None,
    min_trade_dollars: float = 25.0,
    max_order_dollars: float | None = None,
    allow_fractional: bool = False,
    trade_date=None,
) -> pd.DataFrame:
    target_weights = target_weights.astype(float).clip(lower=0)
    target_weights = target_weights / target_weights.sum()

    current_positions = current_positions if current_positions is not None else load_current_positions(None)
    current_qty = current_positions.set_index('ticker')['quantity'] if not current_positions.empty else pd.Series(dtype=float)

    tickers = sorted(set(target_weights.index) | set(current_qty.index))
    prices = prices.reindex(tickers)

    rows = []
    for ticker in tickers:
        pass