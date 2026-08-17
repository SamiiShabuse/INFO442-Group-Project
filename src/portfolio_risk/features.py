"""Feature engineering utilities for live model snapshots."""

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from portfolio_risk.data_fetching import (
    download_adjusted_close,
    download_single_series,
    fetch_fred_context,
)
from portfolio_risk.modeling import load_selected_features


LOOKBACK_DAYS = 120

LATEST_FEATURE_OUTPUT_COLUMNS = [
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


@dataclass(frozen=True)
class LatestFeatureRefreshResult:
    """Summary returned after writing a refreshed feature snapshot."""

    out_path: Path
    latest_date: pd.Timestamp
    complete_latest_rows: int
    ticker_count: int
    missing_tickers: list[str]


def read_tickers(asset_metadata_path: str | Path) -> list[str]:
    """Read the project asset universe from asset metadata."""
    metadata = pd.read_csv(asset_metadata_path)
    if "ticker" not in metadata.columns:
        raise SystemExit("asset metadata CSV must contain a 'ticker' column")
    return metadata["ticker"].dropna().astype(str).sort_values().tolist()


def build_macro_context(
    existing_market: pd.DataFrame,
    start_date: pd.Timestamp,
    end_date: pd.Timestamp,
) -> pd.DataFrame:
    """Build daily macro context by combining fresh downloads with existing values."""
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
        existing_market[
            [column for column in existing_macro_columns if column in existing_market.columns]
        ]
        .drop_duplicates("Date")
        .copy()
    )
    existing_macro["Date"] = pd.to_datetime(existing_macro["Date"]).dt.normalize()

    macro = (
        pd.concat([existing_macro, macro], ignore_index=True)
        .sort_values("Date")
        .groupby("Date", as_index=False)
        .last()
    )

    macro["risk_free_rate_pct"] = pd.to_numeric(macro.get("risk_free_rate_pct"), errors="coerce")
    macro["vix"] = pd.to_numeric(macro.get("vix"), errors="coerce")
    macro["treasury_10yr_pct"] = pd.to_numeric(macro.get("treasury_10yr_pct"), errors="coerce")
    macro["fed_funds_rate_pct"] = pd.to_numeric(macro.get("fed_funds_rate_pct"), errors="coerce")
    macro["unemployment_rate_pct"] = pd.to_numeric(
        macro.get("unemployment_rate_pct"),
        errors="coerce",
    )
    macro["recession_flag"] = pd.to_numeric(macro.get("recession_flag"), errors="coerce")
    macro["cpi_index"] = pd.to_numeric(macro.get("cpi_index"), errors="coerce")

    macro["cpi_pct_change"] = macro["cpi_index"].pct_change()
    if "cpi_pct_change" in existing_market.columns:
        old_cpi_pct = existing_macro.set_index("Date")["cpi_pct_change"]
        macro = macro.set_index("Date")
        macro["cpi_pct_change"] = macro["cpi_pct_change"].combine_first(
            pd.to_numeric(old_cpi_pct, errors="coerce")
        )
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
    """Add rolling-return and rolling-volatility model features."""
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


def build_latest_feature_snapshot_frame(
    existing_market: pd.DataFrame,
    asset_metadata: pd.DataFrame,
    downloaded_prices: pd.DataFrame,
    macro_context: pd.DataFrame,
    selected_features: list[str],
) -> pd.DataFrame:
    """Combine existing rows, fresh downloads, metadata, macro context, and features."""
    existing_market = existing_market.copy()
    existing_market["Date"] = pd.to_datetime(existing_market["Date"]).dt.normalize()

    downloaded_prices = downloaded_prices.copy()
    downloaded_prices["Date"] = pd.to_datetime(downloaded_prices["Date"]).dt.normalize()

    macro_context = macro_context.copy()
    macro_context["Date"] = pd.to_datetime(macro_context["Date"]).dt.normalize()

    downloaded_market = downloaded_prices.merge(macro_context, on="Date", how="left")
    downloaded_market = downloaded_market.merge(asset_metadata, on="ticker", how="left")

    keep_existing = existing_market[existing_market["Date"] < downloaded_market["Date"].min()].copy()
    combined_market = pd.concat([keep_existing, downloaded_market], ignore_index=True, sort=False)
    combined_market = combined_market.sort_values(["ticker", "Date"])

    engineered = engineer_features(combined_market)

    missing_selected = [feature for feature in selected_features if feature not in engineered.columns]
    if missing_selected:
        raise SystemExit(f"Engineered dataset is missing selected features: {missing_selected}")

    output_columns = [column for column in LATEST_FEATURE_OUTPUT_COLUMNS if column in engineered.columns]
    return engineered[output_columns]


def refresh_latest_feature_snapshot(
    integrated_market_path: str | Path,
    asset_metadata_path: str | Path,
    selected_features_path: str | Path,
    out_path: str | Path,
    start_date: str | None = None,
    end_date: str | None = None,
    lookback_days: int = LOOKBACK_DAYS,
) -> LatestFeatureRefreshResult:
    """Download recent data, rebuild model features, and write the latest snapshot."""
    integrated_market_path = Path(integrated_market_path)
    asset_metadata_path = Path(asset_metadata_path)
    selected_features_path = Path(selected_features_path)
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    tickers = read_tickers(asset_metadata_path)
    selected_features = load_selected_features(selected_features_path)
    existing_market = pd.read_csv(integrated_market_path, parse_dates=["Date"], low_memory=False)
    existing_market["Date"] = pd.to_datetime(existing_market["Date"]).dt.normalize()

    end_timestamp = pd.Timestamp(end_date or pd.Timestamp.today().date()).normalize()
    if start_date:
        start_timestamp = pd.Timestamp(start_date).normalize()
    else:
        latest_existing_date = existing_market["Date"].max()
        start_timestamp = min(
            latest_existing_date - pd.Timedelta(days=lookback_days),
            end_timestamp - pd.Timedelta(days=lookback_days),
        )

    downloaded_prices = download_adjusted_close(tickers, start_timestamp, end_timestamp)
    if downloaded_prices.empty:
        raise SystemExit("No market prices were downloaded")

    macro = build_macro_context(existing_market, start_timestamp, end_timestamp)
    metadata = pd.read_csv(asset_metadata_path)

    snapshot = build_latest_feature_snapshot_frame(
        existing_market=existing_market,
        asset_metadata=metadata,
        downloaded_prices=downloaded_prices,
        macro_context=macro,
        selected_features=selected_features,
    )
    snapshot.to_csv(out_path, index=False)

    latest_date = snapshot["Date"].max()
    latest_rows = snapshot[snapshot["Date"] == latest_date]
    complete_latest_rows = latest_rows.dropna(subset=selected_features)
    missing_tickers = sorted(set(tickers) - set(complete_latest_rows["ticker"].astype(str)))

    return LatestFeatureRefreshResult(
        out_path=out_path,
        latest_date=latest_date,
        complete_latest_rows=len(complete_latest_rows),
        ticker_count=len(tickers),
        missing_tickers=missing_tickers,
    )
