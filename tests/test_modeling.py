import math
from io import StringIO

import pandas as pd
import pytest

from portfolio_risk.config import PREDICTED_VOLATILITY_COLUMN, TARGET_COLUMN
from portfolio_risk.modeling import (
    build_latest_feature_matrix,
    build_wide_prediction_frame,
    find_date_column,
    load_selected_features,
    next_business_day,
    predict_feature_matrix,
    validate_model_features,
)


class DummyPredictiveModel:
    feature_names_in_ = ["factor_a", "factor_b"]

    def predict(self, X):
        return X["factor_a"].to_numpy() + X["factor_b"].to_numpy()


def test_load_selected_features_preserves_order():
    features_csv = StringIO("feature\nfactor_b\nfactor_a\n")

    assert load_selected_features(features_csv) == ["factor_b", "factor_a"]


def test_load_selected_features_rejects_target_column():
    features_csv = StringIO(f"feature\nfactor_a\n{TARGET_COLUMN}\n")

    with pytest.raises(SystemExit, match="must not include target column"):
        load_selected_features(features_csv)


def test_find_date_column_accepts_uppercase_or_lowercase():
    assert find_date_column(pd.DataFrame({"Date": []})) == "Date"
    assert find_date_column(pd.DataFrame({"date": []})) == "date"

    with pytest.raises(SystemExit, match="must contain a 'Date' or 'date' column"):
        find_date_column(pd.DataFrame({"timestamp": []}))


def test_build_latest_feature_matrix_uses_latest_date_and_sorts_tickers():
    features = pd.DataFrame(
        {
            "Date": ["2026-01-02", "2026-01-03", "2026-01-03"],
            "ticker": ["ZZZ", "MSFT", "AAPL"],
            "factor_a": [1, "2.5", "1.5"],
            "factor_b": [2, "3.5", "2.5"],
        }
    )

    latest_date, tickers, X = build_latest_feature_matrix(
        features,
        "Date",
        ["factor_a", "factor_b"],
    )

    assert latest_date == pd.Timestamp("2026-01-03")
    assert tickers == ["AAPL", "MSFT"]
    assert list(X.index) == ["AAPL", "MSFT"]
    assert X.loc["AAPL", "factor_a"] == 1.5
    assert X.loc["MSFT", "factor_b"] == 3.5


def test_build_latest_feature_matrix_rejects_missing_selected_values():
    features = pd.DataFrame(
        {
            "Date": ["2026-01-03"],
            "ticker": ["AAPL"],
            "factor_a": [1.0],
            "factor_b": [None],
        }
    )

    with pytest.raises(SystemExit, match="missing or non-numeric"):
        build_latest_feature_matrix(features, "Date", ["factor_a", "factor_b"])


def test_validate_model_features_catches_wrong_order():
    model = DummyPredictiveModel()

    validate_model_features(model, ["factor_a", "factor_b"])
    with pytest.raises(SystemExit, match="feature order"):
        validate_model_features(model, ["factor_b", "factor_a"])


def test_prediction_helpers_create_wide_next_business_day_frame():
    model = DummyPredictiveModel()
    X = pd.DataFrame(
        {"factor_a": [0.01, 0.02], "factor_b": [0.03, 0.04]},
        index=["AAPL", "MSFT"],
    )

    predictions = predict_feature_matrix(model, X, ["AAPL", "MSFT"])
    assert predictions.name == PREDICTED_VOLATILITY_COLUMN
    assert math.isclose(predictions.loc["AAPL"], 0.04)
    assert math.isclose(predictions.loc["MSFT"], 0.06)

    target_date = next_business_day("2026-08-07")
    wide = build_wide_prediction_frame(predictions, target_date)

    assert target_date == pd.Timestamp("2026-08-10")
    assert list(wide.columns) == ["AAPL", "MSFT"]
    assert wide.index.name == "Date"
    assert math.isclose(wide.loc[pd.Timestamp("2026-08-10"), "AAPL"], 0.04)
