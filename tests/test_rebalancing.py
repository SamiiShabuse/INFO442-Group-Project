import math
from io import StringIO

import pandas as pd

from portfolio_risk.rebalancing import (
    build_rebalance_plan,
    load_live_predictions,
    target_weights_to_frame,
)


def test_load_live_predictions_uses_latest_row_and_filters_benchmark():
    predictions_csv = StringIO(
        "Date,AAPL,SPY,MSFT\n"
        "2026-01-05,0.10,0.20,0.30\n"
        "2026-01-06,0.11,0.21,0.31\n"
    )

    prediction_date, rf_vol_matrix, assets = load_live_predictions(predictions_csv)

    assert prediction_date == pd.Timestamp("2026-01-06")
    assert assets == ["AAPL", "MSFT"]
    assert list(rf_vol_matrix.columns) == ["AAPL", "MSFT"]
    assert math.isclose(rf_vol_matrix.loc[prediction_date, "AAPL"], 0.11)


def test_load_live_predictions_can_include_benchmark():
    predictions_csv = StringIO("Date,AAPL,SPY\n2026-01-05,0.10,0.20\n")

    _, _, assets = load_live_predictions(predictions_csv, include_benchmark=True)

    assert assets == ["AAPL", "SPY"]


def test_target_weights_to_frame_uses_project_output_shape():
    weights = pd.Series({"MSFT": 0.6, "AAPL": 0.4}, name="target_weight")

    frame = target_weights_to_frame(weights, "2026-01-05")

    assert list(frame.columns) == ["Date", "ticker", "target_weight"]
    assert frame.to_dict("records") == [
        {"Date": "2026-01-05", "ticker": "MSFT", "target_weight": 0.6},
        {"Date": "2026-01-05", "ticker": "AAPL", "target_weight": 0.4},
    ]


def test_build_rebalance_plan_optimizes_weights_and_creates_orders():
    dates = pd.date_range("2026-01-01", periods=8, freq="B")
    prediction_date = dates[-1]
    assets = ["AAPL", "MSFT", "GLD"]
    returns_matrix = pd.DataFrame(
        {
            "AAPL": [0.010, 0.020, -0.010, 0.015, 0.005, 0.000, 0.010, 0.020],
            "MSFT": [0.005, 0.004, 0.006, 0.003, 0.005, 0.006, 0.004, 0.005],
            "GLD": [0.002, 0.001, 0.002, 0.001, 0.003, 0.002, 0.001, 0.002],
        },
        index=dates,
    )
    risk_free_rate = pd.Series([0.01] * len(dates), index=dates)
    rf_vol_matrix = pd.DataFrame(
        {
            "AAPL": [0.20],
            "MSFT": [0.10],
        },
        index=[prediction_date],
    )
    prices = pd.Series({"AAPL": 100.0, "MSFT": 50.0, "GLD": 25.0})

    plan = build_rebalance_plan(
        prediction_date=prediction_date,
        rf_vol_matrix=rf_vol_matrix,
        assets=assets,
        returns_matrix=returns_matrix,
        risk_free_rate=risk_free_rate,
        prices=prices,
        portfolio_value=1000.0,
        current_positions=pd.DataFrame(columns=["ticker", "quantity"]),
        max_weight=0.6,
        lookback_days=None,
        min_trade_dollars=0.0,
    )

    assert plan.prediction_date == prediction_date
    assert plan.used_prediction_date == prediction_date
    assert plan.missing_assets == ["GLD"]
    assert math.isclose(plan.target_weights.sum(), 1.0, abs_tol=1e-6)
    assert (plan.target_weights <= 0.600001).all()
    assert set(plan.orders["ticker"]) == set(assets)
    assert plan.actionable_orders == 3
    assert set(plan.orders["Date"]) == {prediction_date.date().isoformat()}
