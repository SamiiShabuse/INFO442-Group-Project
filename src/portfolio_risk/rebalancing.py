"""Reusable workflow for RF-driven portfolio rebalancing."""

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from portfolio_risk.config import BENCHMARK
from portfolio_risk.orders import (
    generate_rebalance_orders,
    load_current_positions,
    load_latest_prices,
)
from portfolio_risk.paths import PORTFOLIO_OPTIMIZATION_DIR
from portfolio_risk.portfolio import (
    build_rf_predicted_covariance_matrix,
    load_returns_matrix,
    load_risk_free_rate,
    optimize_portfolio,
)


@dataclass(frozen=True)
class RebalancePlan:
    """In-memory result of turning RF predictions into target weights and orders."""

    prediction_date: pd.Timestamp
    target_weights: pd.Series
    orders: pd.DataFrame
    missing_assets: list[str]
    used_prediction_date: pd.Timestamp

    @property
    def actionable_orders(self) -> int:
        return int((self.orders["status"] == "dry_run").sum())


@dataclass(frozen=True)
class RebalanceRunResult:
    """File-backed rebalance result returned by the CLI workflow."""

    plan: RebalancePlan
    weights_out: Path
    orders_out: Path


def load_live_predictions(
    path,
    include_benchmark: bool = False,
    benchmark: str = BENCHMARK,
) -> tuple[pd.Timestamp, pd.DataFrame, list[str]]:
    """Load the latest wide RF prediction row and choose optimized assets."""
    predictions = pd.read_csv(path, index_col=0, parse_dates=True)
    if predictions.empty:
        raise SystemExit("prediction CSV did not contain any rows")

    latest = predictions.tail(1)
    prediction_date = pd.Timestamp(latest.index[0]).normalize()

    assets = latest.columns.astype(str).tolist()
    if not include_benchmark:
        assets = [asset for asset in assets if asset != benchmark]

    if not assets:
        raise SystemExit("No assets available after applying benchmark filter")

    return prediction_date, latest[assets], assets


def target_weights_to_frame(target_weights: pd.Series, prediction_date) -> pd.DataFrame:
    """Format target weights for the project CSV output contract."""
    return (
        target_weights.reset_index()
        .rename(columns={"index": "ticker"})
        .assign(Date=pd.Timestamp(prediction_date).date().isoformat())[
            ["Date", "ticker", "target_weight"]
        ]
    )


def build_target_weights(
    prediction_date: pd.Timestamp,
    rf_vol_matrix: pd.DataFrame,
    assets: list[str],
    returns_matrix: pd.DataFrame,
    risk_free_rate: pd.Series,
    *,
    objective: str = "min_volatility",
    max_weight: float = 0.25,
    lookback_days: int | None = 252,
) -> tuple[pd.Series, pd.Timestamp, list[str]]:
    """Optimize target weights from RF volatility forecasts and historical returns."""
    known_returns = returns_matrix[returns_matrix.index < prediction_date][assets].dropna()
    if lookback_days:
        known_returns = known_returns.tail(lookback_days)

    if known_returns.empty:
        raise SystemExit("No historical return rows found before prediction date")

    mean_returns = known_returns.mean()
    correlation_matrix = known_returns.corr()
    historical_volatility = known_returns.std()
    avg_risk_free_rate = float(risk_free_rate.reindex(known_returns.index).mean())

    rf_covariance_matrix, used_prediction_date, missing_assets = (
        build_rf_predicted_covariance_matrix(
            assets,
            rf_vol_matrix,
            correlation_matrix,
            historical_volatility,
            prediction_date=prediction_date,
        )
    )

    result = optimize_portfolio(
        objective,
        mean_returns,
        rf_covariance_matrix,
        avg_risk_free_rate,
        max_weight,
    )

    if not result.success:
        raise SystemExit(f"Optimization failed: {result.message}")

    target_weights = pd.Series(result.x, index=assets, name="target_weight").sort_values(
        ascending=False
    )
    return target_weights, used_prediction_date, missing_assets


def build_rebalance_plan(
    prediction_date: pd.Timestamp,
    rf_vol_matrix: pd.DataFrame,
    assets: list[str],
    returns_matrix: pd.DataFrame,
    risk_free_rate: pd.Series,
    prices: pd.Series,
    *,
    portfolio_value: float,
    current_positions: pd.DataFrame | None = None,
    objective: str = "min_volatility",
    max_weight: float = 0.25,
    lookback_days: int | None = 252,
    min_trade_dollars: float = 25.0,
    max_order_dollars: float | None = None,
    allow_fractional: bool = False,
) -> RebalancePlan:
    """Build target weights and dry-run orders for one prediction date."""
    target_weights, used_prediction_date, missing_assets = build_target_weights(
        prediction_date=prediction_date,
        rf_vol_matrix=rf_vol_matrix,
        assets=assets,
        returns_matrix=returns_matrix,
        risk_free_rate=risk_free_rate,
        objective=objective,
        max_weight=max_weight,
        lookback_days=lookback_days,
    )

    orders = generate_rebalance_orders(
        target_weights=target_weights,
        prices=prices,
        portfolio_value=portfolio_value,
        current_positions=current_positions,
        min_trade_dollars=min_trade_dollars,
        max_order_dollars=max_order_dollars,
        allow_fractional=allow_fractional,
        trade_date=prediction_date,
    )

    return RebalancePlan(
        prediction_date=prediction_date,
        target_weights=target_weights,
        orders=orders,
        missing_assets=missing_assets,
        used_prediction_date=used_prediction_date,
    )


def default_rebalance_output_paths(
    prediction_date: pd.Timestamp,
    weights_out: str | Path | None = None,
    orders_out: str | Path | None = None,
) -> tuple[Path, Path]:
    """Return default dated output paths unless explicit paths are provided."""
    date_label = pd.Timestamp(prediction_date).date()
    weights_path = Path(weights_out) if weights_out else (
        PORTFOLIO_OPTIMIZATION_DIR / "live_weights" / f"target_weights_{date_label}.csv"
    )
    orders_path = Path(orders_out) if orders_out else (
        PORTFOLIO_OPTIMIZATION_DIR / "paper_orders" / f"rebalance_orders_{date_label}.csv"
    )
    return weights_path, orders_path


def write_rebalance_plan(
    plan: RebalancePlan,
    weights_out: str | Path,
    orders_out: str | Path,
) -> tuple[Path, Path]:
    """Write target weights and orders to CSV files."""
    weights_out = Path(weights_out)
    orders_out = Path(orders_out)
    weights_out.parent.mkdir(parents=True, exist_ok=True)
    orders_out.parent.mkdir(parents=True, exist_ok=True)

    target_weights_to_frame(plan.target_weights, plan.prediction_date).to_csv(
        weights_out,
        index=False,
    )
    plan.orders.to_csv(orders_out, index=False)
    return weights_out, orders_out


def run_rebalance_order_generation(
    *,
    predictions_path: str | Path,
    integrated_path: str | Path,
    portfolio_value: float,
    current_positions_path: str | Path | None = None,
    objective: str = "min_volatility",
    max_weight: float = 0.25,
    lookback_days: int | None = 252,
    min_trade_dollars: float = 25.0,
    max_order_dollars: float | None = None,
    allow_fractional: bool = False,
    include_benchmark: bool = False,
    weights_out: str | Path | None = None,
    orders_out: str | Path | None = None,
) -> RebalanceRunResult:
    """Load project files, generate target weights/orders, and write CSV outputs."""
    prediction_date, rf_vol_matrix, assets = load_live_predictions(
        predictions_path,
        include_benchmark=include_benchmark,
    )

    integrated_path = Path(integrated_path)
    returns_matrix = load_returns_matrix(integrated_path)
    risk_free_rate = load_risk_free_rate(integrated_path)
    prices = load_latest_prices(integrated_path, assets, as_of_date=prediction_date)
    current_positions = load_current_positions(current_positions_path)

    plan = build_rebalance_plan(
        prediction_date=prediction_date,
        rf_vol_matrix=rf_vol_matrix,
        assets=assets,
        returns_matrix=returns_matrix,
        risk_free_rate=risk_free_rate,
        prices=prices,
        portfolio_value=portfolio_value,
        current_positions=current_positions,
        objective=objective,
        max_weight=max_weight,
        lookback_days=lookback_days,
        min_trade_dollars=min_trade_dollars,
        max_order_dollars=max_order_dollars,
        allow_fractional=allow_fractional,
    )

    weights_path, orders_path = default_rebalance_output_paths(
        prediction_date,
        weights_out=weights_out,
        orders_out=orders_out,
    )
    write_rebalance_plan(plan, weights_path, orders_path)

    return RebalanceRunResult(
        plan=plan,
        weights_out=weights_path,
        orders_out=orders_path,
    )
