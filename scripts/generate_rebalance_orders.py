import argparse
import sys
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from order_generation import generate_rebalance_orders, load_current_positions, load_latest_prices
from portfolio_optimizer import (
    BENCHMARK,
    build_rf_predicted_covariance_matrix,
    load_returns_matrix,
    load_risk_free_rate,
    optimize_portfolio,
)

def load_live_predictions(path: Path, include_benchmark: bool) -> tuple[pd.Timestamp, pd.DataFrame, list[str]]:
    predictions = pd.read_csv(path, index_col=0, parse_dates=True)
    latest = predictions.tail(1)
    prediction_date = pd.Timestamp(latest.index[0]).normalize()

    assets = latest.columns.astype(str).tolist()
    if not include_benchmark:
        assets = [asset for asset in assets if asset != BENCHMARK]

    return prediction_date, latest[assets], assets

def main(args):
    prediction_date, rf_vol_matrix, assets = load_live_predictions(
        Path(args.predictions),
        args.include_benchmark,
    )

    integrated_path = Path(args.integrated_path)
    returns_matrix = load_returns_matrix(integrated_path)
    risk_free_rate = load_risk_free_rate(integrated_path)

    known_returns = returns_matrix[returns_matrix.index < prediction_date][assets].dropna()
    if args.lookback_days:
        known_returns = known_returns.tail(args.lookback_days)


    mean_returns = known_returns.mean()
    correlation_matrix = known_returns.corr()
    historical_volatility = known_returns.std()
    avg_risk_free_rate = risk_free_rate.loc[known_returns.index].mean()

    rf_covariance_matrix, used_prediction_date, missing_assets = build_rf_predicted_covariance_matrix(
        assets,
        rf_vol_matrix,
        correlation_matrix,
        historical_volatility,
        prediction_date=prediction_date,
    )

    result = optimize_portfolio(
        args.objective,
        mean_returns,
        rf_covariance_matrix,
        avg_risk_free_rate,
        args.max_weight,
    )

    if not result.success:
        raise SystemExit(f"Optimization failed: {result.message}")

    target_weights = pd.Series(result.x, index=assets, name="target_weight").sort_values(ascending=False)

    portfolio_path = PROJECT_ROOT / "data" / "processed" / "portfolio_optimization"

    weights_out = Path(args.weights_out) if args.weights_out else (
        portfolio_path / "live_weights" / f"target_weights_{prediction_date.date()}.csv"
    )
    orders_out = Path(args.orders_out) if args.orders_out else (
        portfolio_path / "paper_orders" / f"rebalance_orders_{prediction_date.date()}.csv"
    )

    weights_out.parent.mkdir(parents=True, exist_ok=True)
    orders_out.parent.mkdir(parents=True, exist_ok=True)

    target_weights.reset_index().rename(columns={"index": "ticker"}).assign(
        Date=prediction_date.date().isoformat()
    )[["Date", "ticker", "target_weight"]].to_csv(weights_out, index=False)

    prices = load_latest_prices(integrated_path, assets, as_of_date=prediction_date)
    current_positions = load_current_positions(args.current_positions)

    orders = generate_rebalance_orders(
        target_weights=target_weights,
        prices=prices,
        portfolio_value=args.portfolio_value,
        current_positions=current_positions,
        min_trade_dollars=args.min_trade_dollars,
        max_order_dollars=args.max_order_dollars,
        allow_fractional=args.allow_fractional,
        trade_date=prediction_date,
    )
    orders.to_csv(orders_out, index=False)

    print("Prediction target date:", prediction_date.date())
    print("Wrote target weights to:", weights_out)
    print("Wrote dry-run rebalance orders to:", orders_out)
    print("Actionable orders:", int((orders["status"] == "dry_run").sum()))
    if missing_assets:
        print("Missing RF predictions; used historical volatility for:", missing_assets)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate dry-run rebalance orders from RF optimized weights.")
    parser.add_argument("--predictions", default="data/processed/modeling/random_forest/live_predictions/latest_preds.csv")
    parser.add_argument("--integrated-path", default="data/processed/integrated")
    parser.add_argument("--portfolio-value", type=float, default=100000.0)
    parser.add_argument("--current-positions", default=None, help="Optional CSV with ticker,quantity columns")
    parser.add_argument("--objective", choices=["min_volatility", "max_sharpe"], default="min_volatility")
    parser.add_argument("--max-weight", type=float, default=0.25)
    parser.add_argument("--lookback-days", type=int, default=252)
    parser.add_argument("--min-trade-dollars", type=float, default=25.0)
    parser.add_argument("--max-order-dollars", type=float, default=None)
    parser.add_argument("--allow-fractional", action="store_true")
    parser.add_argument("--include-benchmark", action="store_true")
    parser.add_argument("--weights-out", default=None)
    parser.add_argument("--orders-out", default=None)
    main(parser.parse_args())