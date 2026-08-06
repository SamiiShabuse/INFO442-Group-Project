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