import math

import numpy as np
import pandas as pd

from portfolio_risk.portfolio import (
    build_rf_predicted_covariance_matrix,
    evaluate_portfolio,
    optimize_portfolio,
)


def test_build_rf_predicted_covariance_matrix_uses_historical_vol_for_missing_asset():
    assets = ["AAPL", "MSFT", "GLD"]
    prediction_date = pd.Timestamp("2026-01-05")
    rf_vol = pd.DataFrame(
        {"AAPL": [0.10], "MSFT": [0.20]},
        index=[prediction_date],
    )
    correlation = pd.DataFrame(
        np.eye(3),
        index=assets,
        columns=assets,
    )
    historical_volatility = pd.Series({"AAPL": 0.11, "MSFT": 0.21, "GLD": 0.30})

    covariance, used_date, missing_assets = build_rf_predicted_covariance_matrix(
        assets,
        rf_vol,
        correlation,
        historical_volatility,
        prediction_date=prediction_date,
    )

    assert used_date == prediction_date
    assert missing_assets == ["GLD"]
    assert math.isclose(covariance.loc["AAPL", "AAPL"], 0.01)
    assert math.isclose(covariance.loc["MSFT", "MSFT"], 0.04)
    assert math.isclose(covariance.loc["GLD", "GLD"], 0.09)


def test_optimize_portfolio_returns_weights_that_sum_to_one_and_respect_cap():
    assets = ["AAPL", "MSFT", "GLD", "TLT"]
    mean_returns = pd.Series([0.001, 0.0012, 0.0008, 0.0005], index=assets)
    covariance = pd.DataFrame(np.eye(4) * 0.0001, index=assets, columns=assets)

    result = optimize_portfolio(
        "min_volatility",
        mean_returns,
        covariance,
        max_weight=0.4,
    )

    assert result.success
    assert math.isclose(result.x.sum(), 1.0, abs_tol=1e-6)
    assert (result.x >= -1e-8).all()
    assert (result.x <= 0.400001).all()


def test_evaluate_portfolio_returns_expected_metric_keys():
    returns = pd.DataFrame(
        {
            "AAPL": [0.01, -0.01, 0.02],
            "MSFT": [0.00, 0.01, -0.01],
        }
    )

    metrics = evaluate_portfolio(
        "test_strategy",
        np.array([0.5, 0.5]),
        returns,
        risk_free_rate=0.01,
    )

    assert set(metrics) == {
        "strategy",
        "annualized_return",
        "annualized_volatility",
        "sharpe_ratio",
        "max_drawdown",
        "cumulative_return",
    }
    assert metrics["strategy"] == "test_strategy"
