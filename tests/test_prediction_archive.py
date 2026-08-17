from io import StringIO

import pandas as pd
import pytest

from portfolio_risk.config import DATE_COLUMN, PREDICTED_VOLATILITY_COLUMN, TICKER_COLUMN
from portfolio_risk.prediction_archive import (
    load_latest_predictions,
    merge_prediction_log,
    wide_predictions_to_long,
)


def test_load_latest_predictions_keeps_latest_wide_row():
    predictions_csv = StringIO(
        "Date,MSFT,AAPL\n"
        "2026-01-05,0.20,0.10\n"
        "2026-01-06,0.22,0.12\n"
    )

    latest = load_latest_predictions(predictions_csv)

    assert latest.index.name == DATE_COLUMN
    assert list(latest.columns) == ["MSFT", "AAPL"]
    assert latest.index.tolist() == [pd.Timestamp("2026-01-06")]
    assert latest.loc[pd.Timestamp("2026-01-06"), "AAPL"] == 0.12


def test_load_latest_predictions_rejects_empty_csv():
    with pytest.raises(SystemExit, match="did not contain any rows"):
        load_latest_predictions(StringIO("Date,AAPL\n"))


def test_wide_predictions_to_long_uses_project_log_shape_and_sorting():
    latest = pd.DataFrame(
        {"MSFT": [0.22], "AAPL": [0.12]},
        index=[pd.Timestamp("2026-01-06")],
    )
    latest.index.name = DATE_COLUMN

    target_date, long_predictions = wide_predictions_to_long(latest)

    assert target_date == "2026-01-06"
    assert list(long_predictions.columns) == [
        DATE_COLUMN,
        TICKER_COLUMN,
        PREDICTED_VOLATILITY_COLUMN,
    ]
    assert long_predictions.to_dict("records") == [
        {
            DATE_COLUMN: "2026-01-06",
            TICKER_COLUMN: "AAPL",
            PREDICTED_VOLATILITY_COLUMN: 0.12,
        },
        {
            DATE_COLUMN: "2026-01-06",
            TICKER_COLUMN: "MSFT",
            PREDICTED_VOLATILITY_COLUMN: 0.22,
        },
    ]


def test_merge_prediction_log_replaces_existing_rows_for_same_date():
    existing_log = pd.DataFrame(
        {
            DATE_COLUMN: ["2026-01-05", "2026-01-06", "2026-01-06"],
            TICKER_COLUMN: ["AAPL", "AAPL", "MSFT"],
            PREDICTED_VOLATILITY_COLUMN: [0.10, 9.99, 8.88],
        }
    )
    long_predictions = pd.DataFrame(
        {
            DATE_COLUMN: ["2026-01-06", "2026-01-06"],
            TICKER_COLUMN: ["AAPL", "MSFT"],
            PREDICTED_VOLATILITY_COLUMN: [0.12, 0.22],
        }
    )

    merged = merge_prediction_log(existing_log, long_predictions, "2026-01-06")

    assert merged.to_dict("records") == [
        {
            DATE_COLUMN: "2026-01-05",
            TICKER_COLUMN: "AAPL",
            PREDICTED_VOLATILITY_COLUMN: 0.10,
        },
        {
            DATE_COLUMN: "2026-01-06",
            TICKER_COLUMN: "AAPL",
            PREDICTED_VOLATILITY_COLUMN: 0.12,
        },
        {
            DATE_COLUMN: "2026-01-06",
            TICKER_COLUMN: "MSFT",
            PREDICTED_VOLATILITY_COLUMN: 0.22,
        },
    ]
