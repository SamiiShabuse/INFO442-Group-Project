import math
from io import StringIO

import pandas as pd
import pytest

from portfolio_risk.features import (
    build_latest_feature_snapshot_frame,
    build_macro_context,
    engineer_features,
    read_tickers,
)


def test_read_tickers_sorts_and_requires_ticker_column():
    metadata_csv = StringIO("ticker\nMSFT\nAAPL\n\n")

    assert read_tickers(metadata_csv) == ["AAPL", "MSFT"]

    with pytest.raises(SystemExit, match="ticker"):
        read_tickers(StringIO("symbol\nAAPL\n"))


def test_engineer_features_adds_rolling_columns():
    dates = pd.date_range("2026-01-01", periods=25, freq="B")
    market = pd.DataFrame(
        {
            "Date": dates,
            "ticker": ["AAPL"] * len(dates),
            "adjusted_close": [100 + i for i in range(len(dates))],
        }
    )

    engineered = engineer_features(market)
    latest = engineered.iloc[-1]

    assert "daily_return" in engineered.columns
    assert "rolling_volatility_20d" in engineered.columns
    assert "price_to_moving_avg_20d" in engineered.columns
    assert not math.isnan(latest["rolling_volatility_20d"])
    assert latest["price_to_moving_avg_20d"] > 1


def test_build_macro_context_reuses_existing_values_when_downloads_are_empty(monkeypatch):
    existing_market = pd.DataFrame(
        {
            "Date": pd.to_datetime(["2026-01-01", "2026-01-02"]),
            "risk_free_rate_pct": [4.0, 4.1],
            "vix": [15.0, 16.0],
            "treasury_10yr_pct": [4.5, 4.6],
            "fed_funds_rate_pct": [4.25, 4.25],
            "unemployment_rate_pct": [4.0, 4.0],
            "recession_flag": [0, 0],
            "cpi_index": [300.0, 301.0],
            "cpi_pct_change": [0.0, 0.0033],
        }
    )

    monkeypatch.setattr(
        "portfolio_risk.features.download_single_series",
        lambda _symbol, column_name, *_args, **_kwargs: pd.DataFrame(
            columns=["Date", column_name]
        ),
    )
    monkeypatch.setattr(
        "portfolio_risk.features.fetch_fred_context",
        lambda *_args, **_kwargs: pd.DataFrame(),
    )

    macro = build_macro_context(
        existing_market,
        pd.Timestamp("2026-01-01"),
        pd.Timestamp("2026-01-03"),
    ).set_index("Date")

    assert math.isclose(macro.loc[pd.Timestamp("2026-01-03"), "risk_free_rate_pct"], 4.1)
    assert math.isclose(macro.loc[pd.Timestamp("2026-01-03"), "risk_free_rate_decimal"], 0.041)
    assert math.isclose(macro.loc[pd.Timestamp("2026-01-03"), "yield_curve_spread"], 0.5)
    assert macro.loc[pd.Timestamp("2026-01-03"), "is_inverted"] == 0


def test_build_latest_feature_snapshot_frame_returns_model_ready_rows():
    dates = pd.date_range("2026-01-01", periods=30, freq="B")
    integrated_rows = []
    price_rows = []
    for ticker, base in [("AAPL", 100), ("MSFT", 200)]:
        for i, date in enumerate(dates):
            integrated_rows.append(
                {
                    "Date": date,
                    "ticker": ticker,
                    "adjusted_close": base + i,
                    "risk_free_rate_pct": 4.0,
                    "vix": 15.0,
                    "treasury_10yr_pct": 4.5,
                    "fed_funds_rate_pct": 4.25,
                    "unemployment_rate_pct": 4.0,
                    "recession_flag": 0,
                    "cpi_index": 300.0 + i * 0.1,
                    "cpi_pct_change": 0.001,
                }
            )
            price_rows.append(
                {
                    "Date": date,
                    "ticker": ticker,
                    "adjusted_close": base + i,
                }
            )

    selected_features = [
        "return_lag_1",
        "rolling_volatility_20d",
        "price_to_moving_avg_20d",
    ]
    snapshot = build_latest_feature_snapshot_frame(
        existing_market=pd.DataFrame(integrated_rows),
        asset_metadata=pd.DataFrame(
            {
                "ticker": ["AAPL", "MSFT"],
                "company_name": ["Apple", "Microsoft"],
                "gics_sector": ["Technology", "Technology"],
                "asset_type": ["Equity", "Equity"],
            }
        ),
        downloaded_prices=pd.DataFrame(price_rows),
        macro_context=pd.DataFrame(
            {
                "Date": dates,
                "risk_free_rate_pct": [4.0] * len(dates),
                "risk_free_rate_decimal": [0.04] * len(dates),
                "vix": [15.0] * len(dates),
                "treasury_10yr_pct": [4.5] * len(dates),
                "yield_curve_spread": [0.5] * len(dates),
                "is_inverted": [0] * len(dates),
                "fed_funds_rate_pct": [4.25] * len(dates),
                "unemployment_rate_pct": [4.0] * len(dates),
                "recession_flag": [0] * len(dates),
                "cpi_index": [300.0 + i * 0.1 for i in range(len(dates))],
                "cpi_pct_change": [0.001] * len(dates),
            }
        ),
        selected_features=selected_features,
    )

    latest_rows = snapshot[snapshot["Date"] == snapshot["Date"].max()]

    assert snapshot["Date"].max() == pd.Timestamp("2026-02-11")
    assert latest_rows.dropna(subset=selected_features).shape[0] == 2
    assert set(latest_rows["ticker"]) == {"AAPL", "MSFT"}
    assert {"company_name", "rolling_volatility_20d", "price_to_moving_avg_20d"}.issubset(
        snapshot.columns
    )


def test_build_latest_feature_snapshot_frame_rejects_missing_selected_feature():
    dates = pd.date_range("2026-01-01", periods=5, freq="B")

    with pytest.raises(SystemExit, match="missing selected features"):
        build_latest_feature_snapshot_frame(
            existing_market=pd.DataFrame(
                {
                    "Date": dates,
                    "ticker": ["AAPL"] * len(dates),
                    "adjusted_close": [100 + i for i in range(len(dates))],
                }
            ),
            asset_metadata=pd.DataFrame(
                {
                    "ticker": ["AAPL"],
                    "company_name": ["Apple"],
                }
            ),
            downloaded_prices=pd.DataFrame(
                {
                    "Date": dates,
                    "ticker": ["AAPL"] * len(dates),
                    "adjusted_close": [100 + i for i in range(len(dates))],
                }
            ),
            macro_context=pd.DataFrame({"Date": dates}),
            selected_features=["not_a_feature"],
        )
