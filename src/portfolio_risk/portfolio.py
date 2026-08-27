"""Portfolio optimization helpers built on random forest predicted volatility.

These functions generalize the workflow in
notebooks/06_portfolio_optimization/01_portfolio_optimization.ipynb so it can
be reused for an arbitrary asset subset, such as from the dashboard or a CLI.
"""

from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import minimize

from portfolio_risk.config import BENCHMARK as BENCHMARK
from portfolio_risk.config import TRADING_DAYS


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


def portfolio_return(weights: np.ndarray, mean_returns: pd.Series) -> float:
    return np.dot(weights, mean_returns) * TRADING_DAYS


def portfolio_volatility(weights: np.ndarray, covariance_matrix: pd.DataFrame) -> float:
    return (
        np.sqrt(np.dot(weights.T, np.dot(covariance_matrix, weights)))
        * np.sqrt(TRADING_DAYS)
    )


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
    sharpe_ratio = (
        0 if annual_volatility == 0 else (annual_return - risk_free_rate) / annual_volatility
    )
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


def build_rf_predicted_covariance_matrix(
    assets: list,
    rf_predicted_vol_matrix: pd.DataFrame,
    correlation_matrix: pd.DataFrame,
    historical_volatility: pd.Series,
    prediction_date=None,
) -> tuple:
    """Combine RF predicted volatility with historical correlation into a covariance matrix.

    Assets with no RF prediction on the chosen date fall back to their
    historical volatility so optimization can still run over the full requested
    asset list.

    Returns (covariance_matrix, prediction_date_used, assets_missing_predictions).
    """
    vol_matrix = rf_predicted_vol_matrix.reindex(columns=assets)

    if prediction_date is None:
        covered_assets = vol_matrix.columns[~vol_matrix.isna().all()].tolist()
        if not covered_assets:
            raise ValueError("No RF predictions are available for the requested assets")

        complete_prediction_rows = vol_matrix[covered_assets].dropna()
        if complete_prediction_rows.empty:
            candidate_rows = vol_matrix[covered_assets].dropna(how="all")
            if candidate_rows.empty:
                raise ValueError("No RF predictions are available for the requested assets")
            prediction_date = candidate_rows.index.min()
        else:
            prediction_date = complete_prediction_rows.index.min()
    elif prediction_date not in vol_matrix.index:
        raise ValueError(f"No RF prediction row found for {pd.Timestamp(prediction_date).date()}")

    rf_predicted_vol_by_asset = vol_matrix.loc[prediction_date].reindex(assets)
    missing_assets = rf_predicted_vol_by_asset.index[
        rf_predicted_vol_by_asset.isna()
    ].tolist()
    rf_predicted_vol_by_asset = rf_predicted_vol_by_asset.fillna(
        historical_volatility.reindex(assets)
    )

    unavailable_assets = rf_predicted_vol_by_asset.index[
        rf_predicted_vol_by_asset.isna()
    ].tolist()
    if unavailable_assets:
        raise ValueError(
            "Missing both RF predictions and historical volatility for: "
            + ", ".join(unavailable_assets)
        )

    covariance_matrix = pd.DataFrame(
        np.outer(rf_predicted_vol_by_asset, rf_predicted_vol_by_asset)
        * correlation_matrix.loc[assets, assets].values,
        index=assets,
        columns=assets,
    )

    return covariance_matrix, prediction_date, missing_assets


def optimize_portfolio(
    objective: str,
    mean_returns: pd.Series,
    covariance_matrix: pd.DataFrame,
    risk_free_rate: float = 0.0,
    max_weight: float = 0.25,
):
    """Solve for long-only portfolio weights.

    objective must be either "min_volatility" or "max_sharpe". Weights sum to 1
    and each individual asset weight is capped by max_weight.
    """
    n_assets = len(covariance_matrix)
    if n_assets == 0:
        raise ValueError("Cannot optimize a portfolio with no assets")
    if max_weight <= 0 or max_weight > 1:
        raise ValueError("max_weight must be greater than 0 and no more than 1")
    if n_assets * max_weight < 1:
        raise ValueError(
            f"max_weight={max_weight:.2%} is infeasible for {n_assets} assets; "
            f"select at least {int(np.ceil(1 / max_weight))} assets or raise the cap"
        )

    initial_weights = np.repeat(1 / n_assets, n_assets)
    bounds = tuple((0, max_weight) for _ in range(n_assets))
    constraints = {"type": "eq", "fun": lambda weights: np.sum(weights) - 1}

    if objective == "min_volatility":
        def objective_fn(weights):
            return portfolio_volatility(weights, covariance_matrix)
    elif objective == "max_sharpe":
        def objective_fn(weights):
            return -portfolio_sharpe(
                weights, mean_returns, covariance_matrix, risk_free_rate
            )
    else:
        raise ValueError("objective must be 'min_volatility' or 'max_sharpe'")

    return minimize(
        objective_fn,
        initial_weights,
        method="SLSQP",
        bounds=bounds,
        constraints=constraints,
    )
