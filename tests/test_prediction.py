import math

import pandas as pd
import pytest

from portfolio_risk.config import PREDICTED_VOLATILITY_COLUMN
from portfolio_risk.prediction import build_latest_prediction_result


class DummyPredictiveModel:
    feature_names_in_ = ["factor_a", "factor_b"]

    def predict(self, X):
        return X["factor_a"].to_numpy() + X["factor_b"].to_numpy()


def test_build_latest_prediction_result_uses_latest_features_and_next_business_day():
    features = pd.DataFrame(
        {
            "Date": ["2026-08-06", "2026-08-07", "2026-08-07"],
            "ticker": ["ZZZ", "MSFT", "AAPL"],
            "factor_a": [10.0, 0.02, 0.01],
            "factor_b": [20.0, 0.04, 0.03],
        }
    )

    result = build_latest_prediction_result(
        features=features,
        model=DummyPredictiveModel(),
        selected_features=["factor_a", "factor_b"],
    )

    assert result.latest_feature_date == pd.Timestamp("2026-08-07")
    assert result.prediction_target_date == pd.Timestamp("2026-08-10")
    assert result.tickers == ["AAPL", "MSFT"]
    assert result.predictions.name == PREDICTED_VOLATILITY_COLUMN
    assert math.isclose(result.predictions.loc["AAPL"], 0.04)
    assert math.isclose(result.predictions.loc["MSFT"], 0.06)
    assert list(result.prediction_frame.columns) == ["AAPL", "MSFT"]
    assert result.prediction_frame.index.name == "Date"
    assert math.isclose(
        result.prediction_frame.loc[pd.Timestamp("2026-08-10"), "AAPL"],
        0.04,
    )


def test_build_latest_prediction_result_rejects_model_feature_mismatch():
    features = pd.DataFrame(
        {
            "Date": ["2026-08-07"],
            "ticker": ["AAPL"],
            "factor_a": [0.01],
            "factor_b": [0.03],
        }
    )

    with pytest.raises(SystemExit, match="feature order"):
        build_latest_prediction_result(
            features=features,
            model=DummyPredictiveModel(),
            selected_features=["factor_b", "factor_a"],
        )
