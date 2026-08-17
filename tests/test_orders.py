import math
from io import StringIO

import pandas as pd
import pytest

from portfolio_risk.orders import generate_rebalance_orders, load_current_positions


def test_load_current_positions_accepts_qty_alias():
    positions_csv = StringIO("ticker,qty\nAAPL,2\nMSFT,\n")

    positions = load_current_positions(positions_csv)

    assert list(positions.columns) == ["ticker", "quantity"]
    assert positions.loc[positions["ticker"] == "AAPL", "quantity"].iloc[0] == 2
    assert positions.loc[positions["ticker"] == "MSFT", "quantity"].iloc[0] == 0


def test_load_current_positions_requires_ticker_and_quantity():
    positions_csv = StringIO("ticker,shares\nAAPL,1\n")

    with pytest.raises(ValueError, match="missing columns"):
        load_current_positions(positions_csv)


def test_generate_rebalance_orders_creates_buy_sell_and_hold_rows():
    target_weights = pd.Series({"AAPL": 0.5, "MSFT": 0.5})
    prices = pd.Series({"AAPL": 100.0, "MSFT": 50.0, "CASHLIKE": 10.0})
    current_positions = pd.DataFrame(
        {
            "ticker": ["AAPL", "CASHLIKE"],
            "quantity": [7, 1],
        }
    )

    orders = generate_rebalance_orders(
        target_weights=target_weights,
        prices=prices,
        portfolio_value=1000.0,
        current_positions=current_positions,
        min_trade_dollars=25.0,
        trade_date="2026-01-05",
    ).set_index("ticker")

    assert orders.loc["AAPL", "side"] == "sell"
    assert orders.loc["AAPL", "quantity"] == 2
    assert orders.loc["AAPL", "status"] == "dry_run"

    assert orders.loc["MSFT", "side"] == "buy"
    assert orders.loc["MSFT", "quantity"] == 10
    assert orders.loc["MSFT", "status"] == "dry_run"

    assert orders.loc["CASHLIKE", "side"] == "hold"
    assert orders.loc["CASHLIKE", "status"] == "skipped_small_trade"
    assert orders.loc["CASHLIKE", "Date"] == "2026-01-05"


def test_generate_rebalance_orders_normalizes_weights_and_supports_fractional_orders():
    target_weights = pd.Series({"AAPL": 2.0, "MSFT": 1.0})
    prices = pd.Series({"AAPL": 100.0, "MSFT": 50.0})

    orders = generate_rebalance_orders(
        target_weights=target_weights,
        prices=prices,
        portfolio_value=300.0,
        allow_fractional=True,
        min_trade_dollars=0.0,
    ).set_index("ticker")

    assert math.isclose(orders.loc["AAPL", "target_weight"], 2 / 3)
    assert math.isclose(orders.loc["MSFT", "target_weight"], 1 / 3)
    assert math.isclose(orders.loc["AAPL", "quantity"], 2.0)
    assert math.isclose(orders.loc["MSFT", "quantity"], 2.0)


def test_generate_rebalance_orders_rejects_all_zero_weights():
    with pytest.raises(ValueError, match="at least one positive weight"):
        generate_rebalance_orders(
            target_weights=pd.Series({"AAPL": 0.0}),
            prices=pd.Series({"AAPL": 100.0}),
            portfolio_value=1000.0,
        )
