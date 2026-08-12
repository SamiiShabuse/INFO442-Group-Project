"""External market and macro data-fetching utilities."""

from urllib.parse import quote

import pandas as pd
import requests

try:
    from pandas_datareader import data as pdr
except Exception:  # pragma: no cover - allows market-only refreshes
    pdr = None


FRED_SERIES = {
    "risk_free_rate_pct": "DGS3MO",
    "fed_funds_rate_pct": "FEDFUNDS",
    "unemployment_rate_pct": "UNRATE",
    "recession_flag": "USREC",
    "cpi_index": "CPIAUCSL",
}


def download_yahoo_chart(
    symbol: str,
    start_date: pd.Timestamp,
    end_date: pd.Timestamp,
    adjusted: bool,
) -> pd.DataFrame:
    """Download daily Yahoo chart data for one symbol."""
    period1 = int(pd.Timestamp(start_date, tz="UTC").timestamp())
    period2 = int(pd.Timestamp(end_date + pd.Timedelta(days=1), tz="UTC").timestamp())
    encoded_symbol = quote(symbol, safe="")
    url = (
        f"https://query1.finance.yahoo.com/v8/finance/chart/{encoded_symbol}"
        f"?period1={period1}&period2={period2}&interval=1d"
        "&events=history&includeAdjustedClose=true"
    )

    response = requests.get(
        url,
        timeout=30,
        headers={"User-Agent": "Mozilla/5.0"},
    )
    response.raise_for_status()
    payload = response.json()

    chart = payload.get("chart", {})
    if chart.get("error"):
        raise RuntimeError(chart["error"])

    results = chart.get("result") or []
    if not results:
        return pd.DataFrame(columns=["Date", symbol])

    result = results[0]
    timestamps = result.get("timestamp") or []
    if not timestamps:
        return pd.DataFrame(columns=["Date", symbol])

    indicators = result.get("indicators", {})
    quote_data = (indicators.get("quote") or [{}])[0]
    adj_data = (indicators.get("adjclose") or [{}])[0]

    values = adj_data.get("adjclose") if adjusted else quote_data.get("close")
    if values is None:
        values = quote_data.get("close")

    frame = pd.DataFrame(
        {
            "Date": pd.to_datetime(timestamps, unit="s", utc=True)
            .tz_convert(None)
            .normalize(),
            symbol: values,
        }
    )
    return frame.dropna(subset=[symbol])


def download_adjusted_close(
    tickers: list[str],
    start_date: pd.Timestamp,
    end_date: pd.Timestamp,
) -> pd.DataFrame:
    """Download adjusted close prices in long Date/ticker/adjusted_close format."""
    print(
        "Downloading prices for "
        f"{len(tickers)} tickers from {start_date.date()} through {end_date.date()}"
    )
    frames = []
    for ticker in tickers:
        try:
            frame = download_yahoo_chart(ticker, start_date, end_date, adjusted=True)
        except Exception as exc:
            print(f"Could not download {ticker}: {exc}")
            continue

        if frame.empty:
            print(f"No downloaded prices for {ticker}")
            continue

        frames.append(frame.rename(columns={ticker: "adjusted_close"}).assign(ticker=ticker))

    if not frames:
        return pd.DataFrame(columns=["Date", "ticker", "adjusted_close"])

    return pd.concat(frames, ignore_index=True)


def download_single_series(
    symbol: str,
    column_name: str,
    start_date: pd.Timestamp,
    end_date: pd.Timestamp,
) -> pd.DataFrame:
    """Download one Yahoo series and rename it to a project column."""
    try:
        download = download_yahoo_chart(symbol, start_date, end_date, adjusted=False)
    except Exception as exc:
        print(f"Could not download {symbol}: {exc}")
        return pd.DataFrame(columns=["Date", column_name])

    return download.rename(columns={symbol: column_name})


def fetch_fred_context(
    start_date: pd.Timestamp,
    end_date: pd.Timestamp,
    series_map: dict[str, str] | None = None,
) -> pd.DataFrame:
    """Fetch configured FRED macro series in a Date-indexed context frame."""
    if pdr is None:
        print("pandas_datareader unavailable; falling back to existing macro values only")
        return pd.DataFrame()

    fred_frames = []
    for output_column, series_id in (series_map or FRED_SERIES).items():
        try:
            series = pdr.DataReader(series_id, "fred", start_date, end_date)
        except Exception as exc:
            print(f"Could not fetch FRED series {series_id}: {exc}")
            continue

        if series.empty:
            continue

        fred_frames.append(series.rename(columns={series_id: output_column}))

    if not fred_frames:
        return pd.DataFrame()

    fred = pd.concat(fred_frames, axis=1).reset_index().rename(columns={"DATE": "Date"})
    fred["Date"] = pd.to_datetime(fred["Date"]).dt.normalize()
    return fred
