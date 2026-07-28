"""Portfolio optimization helpers built on random forest predicted volatility.

These functions generalize the workflow in
notebooks/06_portfolio_optimization/01_portfolio_optimization.ipynb so it can
be reused for an arbitrary asset subset (e.g. from the dashboard), not just
the full asset universe.
"""

from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import minimize

TRADING_DAYS = 252
BENCHMARK = "SPY"


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_returns_matrix(integrated_path: Path) -> pd.DataFrame:
    """Pivot daily market data into a Date x ticker matrix of daily returns."""
    daily_market_data = pd.read_csv(
        integrated_path / "daily_market_data.csv", parse_dates=["Date"]
    )
    returns_matrix = daily_market_data.pivot(
        index="Date", columns="ticker", values="daily_return"
    ).sort_index()
    return returns_matrix.dropna()


def load_risk_free_rate(integrated_path: Path) -> pd.Series:
    daily_market_data = pd.read_csv(
        integrated_path / "daily_market_data.csv", parse_dates=["Date"]
    )
    return (
        daily_market_data[["Date", "risk_free_rate_decimal"]]
        .drop_duplicates("Date")
        .set_index("Date")
        .sort_index()["risk_free_rate_decimal"]
    )


def load_rf_predicted_volatility(modeling_path: Path) -> pd.DataFrame:
    """Pivot random forest predictions into a Date x ticker matrix."""
    rf_predictions = pd.read_csv(
        modeling_path / "random_forest" / "test_predictions.csv", parse_dates=["Date"]
    )
    return rf_predictions.pivot(
        index="Date", columns="ticker", values="predicted_future_volatility_20d"
    ).sort_index()


# ---------------------------------------------------------------------------
# Portfolio math
# ---------------------------------------------------------------------------

def portfolio_return(weights: np.ndarray, mean_returns: pd.Series) -> float:
    return np.dot(weights, mean_returns) * TRADING_DAYS


def portfolio_volatility(weights: np.ndarray, covariance_matrix: pd.DataFrame) -> float:
    return np.sqrt(np.dot(weights.T, np.dot(covariance_matrix, weights))) * np.sqrt(TRADING_DAYS)


def portfolio_sharpe(
    weights: np.ndarray,
    mean_returns: pd.Series,
    covariance_matrix: pd.DataFrame,
    risk_free_rate: float = 0.0,
) -> float:
    port_return = portfolio_return(weights, mean_returns)
    port_vol = portfolio_volatility(weights, covariance_matrix)

    if port_vol == 0:
        return 0

    return (port_return - risk_free_rate) / port_vol


def max_drawdown(portfolio_returns: pd.Series) -> float:
    cumulative = (1 + portfolio_returns).cumprod()
    running_max = cumulative.cummax()
    drawdown = (cumulative - running_max) / running_max
    return drawdown.min()


def evaluate_portfolio(
    strategy_name: str,
    weights: np.ndarray,
    returns_data: pd.DataFrame,
    risk_free_rate: float = 0.0,
) -> dict:
    daily_portfolio_returns = returns_data.dot(weights)

    annual_return = daily_portfolio_returns.mean() * TRADING_DAYS
    annual_volatility = daily_portfolio_returns.std() * np.sqrt(TRADING_DAYS)
    sharpe_ratio = 0 if annual_volatility == 0 else (annual_return - risk_free_rate) / annual_volatility
    cumulative_return = (1 + daily_portfolio_returns).prod() - 1
    drawdown = max_drawdown(daily_portfolio_returns)

    return {
        "strategy": strategy_name,
        "annualized_return": annual_return,
        "annualized_volatility": annual_volatility,
        "sharpe_ratio": sharpe_ratio,
        "max_drawdown": drawdown,
        "cumulative_return": cumulative_return,
    }


# ---------------------------------------------------------------------------
# Predictive covariance matrix (random forest volatility x historical correlation)
# ---------------------------------------------------------------------------

def build_rf_predicted_covariance_matrix(
    assets: list,
    rf_predicted_vol_matrix: pd.DataFrame,
    correlation_matrix: pd.DataFrame,
    historical_volatility: pd.Series,
    prediction_date=None,
) -> tuple:
    """Combine RF predicted volatility with historical correlation into a covariance matrix.

    Assets with no RF prediction on the chosen date fall back to their
    historical (annualized) volatility so optimization can still run over the
    full requested asset list.

    Returns (covariance_matrix, prediction_date_used, assets_missing_predictions).
    """
    vol_matrix = rf_predicted_vol_matrix.reindex(columns=assets)

    missing_assets = vol_matrix.columns[vol_matrix.isna().all()].tolist()

    if prediction_date is None:
        prediction_date = vol_matrix.dropna().index.min()

    rf_predicted_vol_by_asset = vol_matrix.loc[prediction_date].reindex(assets)
    rf_predicted_vol_by_asset = rf_predicted_vol_by_asset.fillna(historical_volatility.reindex(assets))

    covariance_matrix = pd.DataFrame(
        np.outer(rf_predicted_vol_by_asset, rf_predicted_vol_by_asset)
        * correlation_matrix.loc[assets, assets].values,
        index=assets,
        columns=assets,
    )

    return covariance_matrix, prediction_date, missing_assets


# ---------------------------------------------------------------------------
# Optimization
# ---------------------------------------------------------------------------

def optimize_portfolio(
    objective: str,
    mean_returns: pd.Series,
    covariance_matrix: pd.DataFrame,
    risk_free_rate: float = 0.0,
    max_weight: float = 0.25,
):
    """Solve for portfolio weights. objective is 'min_volatility' or 'max_sharpe'.

    Long-only, weights sum to 1, each weight capped at max_weight.
    """
    n_assets = len(covariance_matrix)
    initial_weights = np.repeat(1 / n_assets, n_assets)
    bounds = tuple((0, max_weight) for _ in range(n_assets))
    constraints = {"type": "eq", "fun": lambda weights: np.sum(weights) - 1}

    if objective == "min_volatility":
        objective_fn = lambda weights: portfolio_volatility(weights, covariance_matrix)
    elif objective == "max_sharpe":
        objective_fn = lambda weights: -portfolio_sharpe(
            weights, mean_returns, covariance_matrix, risk_free_rate
        )
    else:
        raise ValueError("objective must be 'min_volatility' or 'max_sharpe'")

    result = minimize(
        objective_fn,
        initial_weights,
        method="SLSQP",
        bounds=bounds,
        constraints=constraints,
    )

    return result
