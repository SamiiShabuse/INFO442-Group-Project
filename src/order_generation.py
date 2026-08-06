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