"""Generate dry-run rebalance orders from RF optimized target weights."""

import argparse
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from portfolio_risk.rebalancing import run_rebalance_order_generation  # noqa: E402


def main(args) -> None:
    result = run_rebalance_order_generation(
        predictions_path=args.predictions,
        integrated_path=args.integrated_path,
        portfolio_value=args.portfolio_value,
        current_positions_path=args.current_positions,
        objective=args.objective,
        max_weight=args.max_weight,
        lookback_days=args.lookback_days,
        min_trade_dollars=args.min_trade_dollars,
        max_order_dollars=args.max_order_dollars,
        allow_fractional=args.allow_fractional,
        include_benchmark=args.include_benchmark,
        weights_out=args.weights_out,
        orders_out=args.orders_out,
    )

    print("Prediction target date:", result.plan.prediction_date.date())
    print("Wrote target weights to:", result.weights_out)
    print("Wrote dry-run rebalance orders to:", result.orders_out)
    print("Actionable orders:", result.plan.actionable_orders)
    if result.plan.missing_assets:
        print("Missing RF predictions; used historical volatility for:", result.plan.missing_assets)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate dry-run rebalance orders from RF optimized weights."
    )
    parser.add_argument(
        "--predictions",
        default="data/processed/modeling/random_forest/live_predictions/latest_preds.csv",
    )
    parser.add_argument("--integrated-path", default="data/processed/integrated")
    parser.add_argument("--portfolio-value", type=float, default=100000.0)
    parser.add_argument(
        "--current-positions",
        default=None,
        help="Optional CSV with ticker,quantity columns",
    )
    parser.add_argument(
        "--objective",
        choices=["min_volatility", "max_sharpe"],
        default="min_volatility",
    )
    parser.add_argument("--max-weight", type=float, default=0.25)
    parser.add_argument("--lookback-days", type=int, default=252)
    parser.add_argument("--min-trade-dollars", type=float, default=25.0)
    parser.add_argument("--max-order-dollars", type=float, default=None)
    parser.add_argument("--allow-fractional", action="store_true")
    parser.add_argument("--include-benchmark", action="store_true")
    parser.add_argument("--weights-out", default=None)
    parser.add_argument("--orders-out", default=None)
    main(parser.parse_args())
