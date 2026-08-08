import math
from io import StringIO

import numpy as np
import pandas as pd
import pytest

from portfolio_risk.config import (
    ACTUAL_VOLATILITY_COLUMN,
    PREDICTED_VOLATILITY_COLUMN,
)
from portfolio_risk.evaluation import (
    TRAILING_VOLATILITY_COLUMN,
    choose_evaluation_date,
    compare_prediction_to_trailing_volatility,
    evaluate_completed_future_window,
    load_prediction_row,
    regression_metrics,
)


class ConstantModel:
    feature_names_in_ = ["signal"]

    def predict(self, X):
        return np.repeat(0.02, len(X))


def test_regression_metrics_calculates_expected_values():
    metrics = regression_metrics(pd.Series([1.0, 2.0, 3.0]), [1.0, 2.0, 4.0])

    assert math.isclose(metrics["MAE"], 1 / 3)
    assert math.isclose(metrics["RMSE"], math.sqrt(1 / 3))
    assert math.isclose(metrics["R2"], 0.5)


def test_regression_metrics_returns_nan_r2_for_one_row():
    metrics = regression_metrics(pd.Series([1.0]), [1.2])

    assert math.isclose(metrics["MAE"], 0.2)
    assert math.isnan(metrics["R2"])


def test_choose_evaluation_date_uses_latest_complete_date():
    df = pd.DataFrame(
        {
            "Date": pd.to_datetime(
                ["2026-01-01", "2026-01-01", "2026-01-02", "2026-01-02"]
            ),
            "ticker": ["AAPL", "MSFT", "AAPL", "MSFT"],
            "signal": [1.0, 2.0, 3.0, 4.0],
            ACTUAL_VOLATILITY_COLUMN: [0.1, 0.2, 0.3, np.nan],
        }
    )

    assert choose_evaluation_date(df, ["signal"], None, None) == pd.Timestamp("2026-01-01")
    assert choose_evaluation_date(df, ["signal"], None, 1) == pd.Timestamp("2026-01-02")
    assert choose_evaluation_date(df, ["signal"], "2026-01-01", None) == pd.Timestamp(
        "2026-01-01"
    )

    with pytest.raises(SystemExit, match="No complete evaluation rows"):
        choose_evaluation_date(df, ["signal"], "2026-01-03", None)


def test_evaluate_completed_future_window_returns_rows_and_summary():
    dates = pd.date_range("2026-01-01", periods=4, freq="B")
    features = pd.DataFrame(
        [
            {
                "Date": date,
                "ticker": ticker,
                "daily_return": daily_return,
                "signal": signal,
            }
            for ticker, offset in [("AAPL", 0.0), ("MSFT", 0.01)]
            for signal, date, daily_return in zip(
                [1.0, 2.0, 3.0, 4.0],
                dates,
                [0.01 + offset, 0.02 + offset, 0.03 + offset, 0.04 + offset],
            )
        ]
    )

    rows, summary = evaluate_completed_future_window(
        features,
        ConstantModel(),
        ["signal"],
        horizon=2,
    )

    assert summary["evaluation_feature_date"] == "2026-01-02"
    assert summary["horizon_trading_days"] == 2
    assert summary["tickers"] == 2
    assert list(rows["ticker"]) == ["AAPL", "MSFT"]
    assert set(rows[PREDICTED_VOLATILITY_COLUMN]) == {0.02}
    assert rows[ACTUAL_VOLATILITY_COLUMN].notna().all()
    assert {"error", "absolute_error", "squared_error"}.issubset(rows.columns)


def test_load_prediction_row_converts_wide_predictions_to_long():
    predictions_csv = StringIO("Date,AAPL,MSFT\n2026-01-05,0.1,0.2\n")

    target_date, long_predictions = load_prediction_row(predictions_csv)

    assert target_date == pd.Timestamp("2026-01-05")
    assert set(long_predictions["ticker"]) == {"AAPL", "MSFT"}
    assert set(long_predictions[PREDICTED_VOLATILITY_COLUMN]) == {0.1, 0.2}


def test_compare_prediction_to_trailing_volatility_summarizes_differences():
    features = pd.DataFrame(
        {
            "Date": ["2026-01-02", "2026-01-02"],
            "ticker": ["AAPL", "MSFT"],
            "rolling_volatility_20d": [0.10, 0.30],
            "rolling_volatility_5d": [0.08, 0.25],
            "daily_return": [0.01, -0.02],
        }
    )
    predictions = pd.DataFrame(
        {
            "ticker": ["AAPL", "MSFT"],
            PREDICTED_VOLATILITY_COLUMN: [0.20, 0.10],
        }
    )

    comparison, summary = compare_prediction_to_trailing_volatility(
        features,
        predictions,
        prediction_target_date=pd.Timestamp("2026-01-05"),
        feature_date="2026-01-02",
    )

    assert list(comparison["ticker"]) == ["MSFT", "AAPL"]
    assert math.isclose(comparison.iloc[0]["absolute_difference"], 0.20)
    assert summary["feature_date"] == "2026-01-02"
    assert summary["prediction_target_date"] == "2026-01-05"
    assert summary["tickers"] == 2
    assert math.isclose(summary["mean_absolute_difference"], 0.15)
    assert TRAILING_VOLATILITY_COLUMN in comparison.columns
