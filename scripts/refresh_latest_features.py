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
from pathlib import Path
from urllib.parse import quote

import pandas as pd
import requests

try:
    from pandas_datareader import data as pdr
except Exception:  # pragma: no cover - allows market-only refreshes
    pdr = None


LOOKBACK_DAYS = 120
FRED_SERIES = {
    "risk_free_rate_pct": "DGS3MO",
    "fed_funds_rate_pct": "FEDFUNDS",
    "unemployment_rate_pct": "UNRATE",
    "recession_flag": "USREC",
    "cpi_index": "CPIAUCSL",
}


def read_tickers(asset_metadata_path: Path) -> list[str]:
    metadata = pd.read_csv(asset_metadata_path)
    if "ticker" not in metadata.columns:
        raise SystemExit("asset metadata CSV must contain a 'ticker' column")
    return metadata["ticker"].dropna().astype(str).sort_values().tolist()


def read_selected_features(selected_features_path: Path) -> list[str]:
    selected_features = pd.read_csv(selected_features_path)
    if "feature" not in selected_features.columns:
        raise SystemExit("selected features CSV must contain a 'feature' column")
    return selected_features["feature"].dropna().astype(str).tolist()


def flatten_download_column(download: pd.DataFrame, field: str) -> pd.DataFrame:
    if download.empty:
        return pd.DataFrame()

    if isinstance(download.columns, pd.MultiIndex):
        if field in download.columns.get_level_values(0):
            return download[field]
        fallback = "Close" if field == "Adj Close" else field
        if fallback in download.columns.get_level_values(0):
            return download[fallback]
        raise SystemExit(f"Downloaded data did not include '{field}' or fallback columns")

    if field in download.columns:
        return download[[field]]
    if field == "Adj Close" and "Close" in download.columns:
        return download[["Close"]].rename(columns={"Close": "Adj Close"})
    raise SystemExit(f"Downloaded data did not include '{field}'")


def download_yahoo_chart(
    symbol: str,
    start_date: pd.Timestamp,
    end_date: pd.Timestamp,
    adjusted: bool,
) -> pd.DataFrame:
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
            "Date": pd.to_datetime(timestamps, unit="s", utc=True).tz_convert(None).normalize(),
            symbol: values,
        }
    )
    return frame.dropna(subset=[symbol])


def download_adjusted_close(tickers: list[str], start_date: pd.Timestamp, end_date: pd.Timestamp) -> pd.DataFrame:
    print(f"Downloading prices for {len(tickers)} tickers from {start_date.date()} through {end_date.date()}")
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


def download_single_series(symbol: str, column_name: str, start_date: pd.Timestamp, end_date: pd.Timestamp) -> pd.DataFrame:
    try:
        download = download_yahoo_chart(symbol, start_date, end_date, adjusted=False)
    except Exception as exc:
        print(f"Could not download {symbol}: {exc}")
        return pd.DataFrame(columns=["Date", column_name])

    return download.rename(columns={symbol: column_name})


def fetch_fred_context(start_date: pd.Timestamp, end_date: pd.Timestamp) -> pd.DataFrame:
    if pdr is None:
        print("pandas_datareader unavailable; falling back to existing macro values only")
        return pd.DataFrame()

    fred_frames = []
    for output_column, series_id in FRED_SERIES.items():
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


def build_macro_context(
    existing_market: pd.DataFrame,
    start_date: pd.Timestamp,
    end_date: pd.Timestamp,
) -> pd.DataFrame:
    calendar = pd.DataFrame({"Date": pd.date_range(start_date, end_date, freq="D")})

    vix = download_single_series("^VIX", "vix", start_date, end_date)
    treasury = download_single_series("^TNX", "treasury_10yr_pct", start_date, end_date)
    if not treasury.empty and treasury["treasury_10yr_pct"].median() > 20:
        treasury["treasury_10yr_pct"] = treasury["treasury_10yr_pct"] / 10.0

    fred = fetch_fred_context(start_date, end_date)

    macro = calendar.merge(vix, on="Date", how="left").merge(treasury, on="Date", how="left")
    if not fred.empty:
        macro = macro.merge(fred, on="Date", how="left")

    existing_macro_columns = [
        "Date",
        "risk_free_rate_pct",
        "vix",
        "treasury_10yr_pct",
        "yield_curve_spread",
        "is_inverted",
        "fed_funds_rate_pct",
        "unemployment_rate_pct",
        "recession_flag",
        "cpi_index",
        "cpi_pct_change",
    ]
    existing_macro = (
        existing_market[[column for column in existing_macro_columns if column in existing_market.columns]]
        .drop_duplicates("Date")
        .copy()
    )
    existing_macro["Date"] = pd.to_datetime(existing_macro["Date"]).dt.normalize()

    macro = pd.concat([existing_macro, macro], ignore_index=True)
    macro = macro.sort_values("Date").drop_duplicates("Date", keep="last")

    macro["risk_free_rate_pct"] = pd.to_numeric(macro.get("risk_free_rate_pct"), errors="coerce")
    macro["vix"] = pd.to_numeric(macro.get("vix"), errors="coerce")
    macro["treasury_10yr_pct"] = pd.to_numeric(macro.get("treasury_10yr_pct"), errors="coerce")
    macro["fed_funds_rate_pct"] = pd.to_numeric(macro.get("fed_funds_rate_pct"), errors="coerce")
    macro["unemployment_rate_pct"] = pd.to_numeric(macro.get("unemployment_rate_pct"), errors="coerce")
    macro["recession_flag"] = pd.to_numeric(macro.get("recession_flag"), errors="coerce")
    macro["cpi_index"] = pd.to_numeric(macro.get("cpi_index"), errors="coerce")

    macro["cpi_pct_change"] = macro["cpi_index"].pct_change()
    if "cpi_pct_change" in existing_market.columns:
        old_cpi_pct = existing_macro.set_index("Date")["cpi_pct_change"]
        macro = macro.set_index("Date")
        macro["cpi_pct_change"] = macro["cpi_pct_change"].combine_first(pd.to_numeric(old_cpi_pct, errors="coerce"))
        macro = macro.reset_index()

    macro = macro.sort_values("Date")
    fill_columns = [
        "risk_free_rate_pct",
        "vix",
        "treasury_10yr_pct",
        "fed_funds_rate_pct",
        "unemployment_rate_pct",
        "recession_flag",
        "cpi_index",
        "cpi_pct_change",
    ]
    macro[fill_columns] = macro[fill_columns].ffill()

    macro["yield_curve_spread"] = macro["treasury_10yr_pct"] - macro["risk_free_rate_pct"]
    macro["is_inverted"] = (macro["yield_curve_spread"] < 0).astype(int)
    macro["risk_free_rate_decimal"] = macro["risk_free_rate_pct"] / 100.0

    return macro


def engineer_features(market: pd.DataFrame) -> pd.DataFrame:
    market = market.sort_values(["ticker", "Date"]).copy()

    market["daily_return"] = market.groupby("ticker")["adjusted_close"].pct_change()
    market["return_lag_1"] = market.groupby("ticker")["daily_return"].shift(1)
    market["return_lag_5"] = market.groupby("ticker")["daily_return"].shift(5)
    market["rolling_return_5d"] = (
        market.groupby("ticker")["daily_return"]
        .rolling(window=5)
        .mean()
        .reset_index(level=0, drop=True)
    )
    market["rolling_return_20d"] = (
        market.groupby("ticker")["daily_return"]
        .rolling(window=20)
        .mean()
        .reset_index(level=0, drop=True)
    )
    market["abs_return"] = market["daily_return"].abs()
    market["squared_return"] = market["daily_return"] ** 2
    market["rolling_abs_return_20d"] = (
        market.groupby("ticker")["abs_return"]
        .rolling(window=20)
        .mean()
        .reset_index(level=0, drop=True)
    )
    market["rolling_squared_return_20d"] = (
        market.groupby("ticker")["squared_return"]
        .rolling(window=20)
        .mean()
        .reset_index(level=0, drop=True)
    )
    market["rolling_volatility_5d"] = (
        market.groupby("ticker")["daily_return"]
        .rolling(window=5)
        .std()
        .reset_index(level=0, drop=True)
    )
    market["rolling_volatility_20d"] = (
        market.groupby("ticker")["daily_return"]
        .rolling(window=20)
        .std()
        .reset_index(level=0, drop=True)
    )
    market["moving_avg_20d"] = (
        market.groupby("ticker")["adjusted_close"]
        .rolling(window=20)
        .mean()
        .reset_index(level=0, drop=True)
    )
    market["price_to_moving_avg_20d"] = market["adjusted_close"] / market["moving_avg_20d"]

    return market


def main(
    integrated_market_path: str,
    asset_metadata_path: str,
    selected_features_path: str,
    out_path: str,
    start_date: str | None,
    end_date: str,
) -> None:
    integrated_market_path = Path(integrated_market_path)
    asset_metadata_path = Path(asset_metadata_path)
    selected_features_path = Path(selected_features_path)
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    tickers = read_tickers(asset_metadata_path)
    selected_features = read_selected_features(selected_features_path)
    existing_market = pd.read_csv(integrated_market_path, parse_dates=["Date"], low_memory=False)
    existing_market["Date"] = pd.to_datetime(existing_market["Date"]).dt.normalize()

    end_timestamp = pd.Timestamp(end_date or pd.Timestamp.today().date()).normalize()
    if start_date:
        start_timestamp = pd.Timestamp(start_date).normalize()
    else:
        latest_existing_date = existing_market["Date"].max()
        start_timestamp = min(latest_existing_date - pd.Timedelta(days=LOOKBACK_DAYS), end_timestamp - pd.Timedelta(days=LOOKBACK_DAYS))

    downloaded_prices = download_adjusted_close(tickers, start_timestamp, end_timestamp)
    if downloaded_prices.empty:
        raise SystemExit("No market prices were downloaded")

    macro = build_macro_context(existing_market, start_timestamp, end_timestamp)
    downloaded_market = downloaded_prices.merge(macro, on="Date", how="left")

    metadata = pd.read_csv(asset_metadata_path)
    downloaded_market = downloaded_market.merge(metadata, on="ticker", how="left")

    keep_existing = existing_market[existing_market["Date"] < downloaded_market["Date"].min()].copy()
    combined_market = pd.concat([keep_existing, downloaded_market], ignore_index=True, sort=False)
    combined_market = combined_market.sort_values(["ticker", "Date"])

    engineered = engineer_features(combined_market)

    missing_selected = [feature for feature in selected_features if feature not in engineered.columns]
    if missing_selected:
        raise SystemExit(f"Engineered dataset is missing selected features: {missing_selected}")

    output_columns = [
        "Date",
        "ticker",
        "adjusted_close",
        "daily_return",
        "risk_free_rate_decimal",
        "vix",
        "treasury_10yr_pct",
        "yield_curve_spread",
        "is_inverted",
        "fed_funds_rate_pct",
        "unemployment_rate_pct",
        "recession_flag",
        "cpi_index",
        "cpi_pct_change",
        "company_name",
        "gics_sector",
        "asset_type",
        "return_lag_1",
        "return_lag_5",
        "rolling_return_5d",
        "rolling_return_20d",
        "abs_return",
        "squared_return",
        "rolling_abs_return_20d",
        "rolling_squared_return_20d",
        "rolling_volatility_5d",
        "rolling_volatility_20d",
        "moving_avg_20d",
        "price_to_moving_avg_20d",
    ]
    output_columns = [column for column in output_columns if column in engineered.columns]
    engineered[output_columns].to_csv(out_path, index=False)

    latest_date = engineered["Date"].max()
    latest_rows = engineered[engineered["Date"] == latest_date]
    complete_latest_rows = latest_rows.dropna(subset=selected_features)

    print("Wrote latest feature snapshot to:", out_path)
    print("Latest available market date:", latest_date.date())
    print(f"Latest rows with complete selected features: {len(complete_latest_rows)} / {len(tickers)}")
    if len(complete_latest_rows) < len(tickers):
        missing_tickers = sorted(set(tickers) - set(complete_latest_rows["ticker"].astype(str)))
        print("Tickers missing complete latest features:", missing_tickers)


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
