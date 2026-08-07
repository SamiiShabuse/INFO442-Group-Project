#!/usr/bin/env python3
"""
scripts/paper_trade.py

Usage (dry run):
python scripts/paper_trade.py --predictions data/processed/modeling/random_forest/live_predictions/latest_preds.csv --dry-run

Live (paper account; set the env vars first or .env):
export ALPACA_API_KEY=...
export ALPACA_SECRET_KEY=...
python scripts/paper_trade.py --predictions data/processed/modeling/random_forest/live_predictions/latest_preds.csv
"""
import os
import argparse
from pathlib import Path
import csv 
import math
import pandas as pd
import numpy as np
from datetime import datetime
try:
    from alpaca_tradeapi.rest import REST, APIError
except Exception:
    REST = None # allow dry-run without alpaca package

EPS = 1e-8

def load_predictions(path):
    df = pd.read_csv(path, index_col=0, parse_dates=True)

    #take last row if mutilple
    row = df.iloc[-1]

    # ensure string trickers
    row.index = row.index.astype(str)
    return row

def make_weight_from_preds(preds, pred_is_vol=True, max_pos_pct=0.2):
    if pred_is_vol:
        inv = 1.0 / (preds.astype(float) + EPS) 
        w = inv.clip(lower=0)
    else:
        w = preds.astype(float).clip(lower=0)

    # drop NaN/zero columns
    w = w.replace([np.inf, -np.inf], np.nan).fillna(0)
    if w.sum() <= 0:
        raise SystemExit("All weights zero after processing predictions.")

    # intiial normalization
    w = w / w.sum()
    # apply per-ticker cap and renormalize (simple iterative cap)
    cap = max_pos_pct
    over = w > cap
    if over.any():
        w_clipped = w.clip(upper=cap)
        remainder = 1.0 - w_clipped.sum()
        if remainder <= 0:
            # evenly distributed among uncapped if non remain
            w_final = w_clipped / w_clipped.sum()
            return w_final
        # distribute remainder proprotionally among uncapped
        uncapped = (~over) & (w_clipped > 0)
        if uncapped.any():
            prop = w.loc[uncapped] / w.loc[uncapped].sum()
            w_clipped.loc[uncapped] += remainder * prop
        w = w_clipped 
    return w

def get_last_price_alpaca(api, symbol):
    # prefer last_trade; fall back to last_quote midpoint
    try:
        trade = api.get_latest_trade(symbol)
        return float(trade.price)
    except Exception:
        try:
            q = api.get_latest_quote(symbol)
            return (float(q.bidprice) + float(q.askprice)) / 2.0
        except Exception:
            return None

def safe_int(qty):
    try:
        return int(math.floor(float(qty)))
    except Exception:
        return 0

def main(args):
    preds = load_predictions(args.predictions)
    print("Loaded predictions for target date:", preds.name)

    weights = make_weight_from_preds(preds, pred_is_vol=args.pred_is_vol, max_pos_pct=args.max_pos_pct)
    weights = weights[weights > 0].sort_values(ascending=False)
    print(f"{len(weights)} tickers with nonzero target weight. Top 5:\n", weights.head())

    # Alpaca REST client (optional for dry-run)
    api = None
    if not args.dry_run:
        if REST is None:
            raise SystemExit("aplalpaca-trade-api not installed. pip install alpaca-trade-api")
        key = os.getenv("ALPACA_API_KEY")
        secret = os.getenv("ALPACA_SECRET_KEY")
        base_url = args.alpaca_base_url or os.getenv("ALPACA_BASE_URL", "https://paper-api.alpaca.markets")
        if not key or not secret:
            raise SystemExit("Set ALPACA_API_KEY and ALPACA_SECRET_KEY in your environment or run with --dry-run")
        api = REST(key, secret, base_url, api_version='v2')

    # Determine investable cash (use account equity * fraction_invest if not enough cash)
    investable_cash = None
    account_equity = None
    if api:
        acct = api.get_account()
        account_equity = float(acct.equity)
        cash = float(acct.cash)
        investable_cash = account_equity * args.fraction_invest
        # don't use more cash then avaliable
        investable_cash = min(investable_cash, cash)
        print(f"Account equity: {account_equity:.2f}, cash: {cash:.2f}, investable cash: {investable_cash:.2f}")
        print(f"Account equity: {account_equity:.2f}, cash available: {cash:.2f}, investable_cash: {investable_cash:.2f}")
        if investable_cash < args.min_cash:
            raise SystemExit(f"Investable cash {investable_cash:.2f} below min_cash {args.min_cash:.2f}")
    else:
        # dry-run: assume a virtual bankroll
        investable_cash = args.virtual_cash
        account_equity = investable_cash
        print(f"Dry-run virtual equity: {account_equity:.2f}")

    # Build desired dollar allocations
    desired_dollars = (weights * investable_cash).to_dict()
    print(f"Desired dollar allocations:\n{desired_dollars}")

    # Get current positions
    current_positions = {}
    if api:
        for symbol in weights.index:
            try:
                pos = api.get_position(symbol)
                current_positions[symbol] = {"qty": float(pos.qty), "market_value": float(pos.market_value)}
            except Exception:
                current_positions[symbol] = {"qty": 0.0, "market_value": 0.0}

    else:
        # dry-run assume zero positions
        for symbol in weights.index:
            current_positions[symbol] = {"qty": 0.0, "market_value": 0.0}

        # For each ticker create order to move to desired allocation
    orders = []
    for symbol, target_dollar in desired_dollars.items():
        price = None
        if api:
            price = get_last_price_alpaca(api, symbol)
        else:
            # try to source price from preds if available (not ideal), else skip
            price = args.dry_price or None
        if price is None or price <= 0:
            print(f"Skipping {symbol}: no price available")
            continue
        desired_qty = safe_int(target_dollar / price)
        current_qty = safe_int(current_positions.get(symbol, {}).get("qty", 0.0))
        qty_diff = desired_qty - current_qty
        if abs(qty_diff) < 1:
            continue
        side = "buy" if qty_diff > 0 else "sell"
        qty_submit = abs(qty_diff)
        orders.append({"symbol": symbol, "side": side, "qty": qty_submit, "price": price, "desired_dollar": target_dollar, "current_qty": current_qty})

    if not orders:
        print("No orders to submit (portfolio already aligned).")
        return

    # Dry-run: print planned orders
    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    log_dir = Path("logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / f"orders_{timestamp}.csv"

    if args.dry_run:
        print("--- DRY RUN: planned orders ---")
        for o in orders:
            print(f"{o['side'].upper():4} {o['qty']:5d} {o['symbol']:6s} at ~{o['price']:.2f} (target ${o['desired_dollar']:.2f})")
        # write log of dry-run
        with open(log_path, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["ts", "symbol", "side", "qty", "price", "desired_dollar", "current_qty", "status"])
            w.writeheader()
            for o in orders:
                orow = {"ts": timestamp, **o, "status": "dry-run"}
                w.writerow(orow)
        print("Wrote dry-run order log to:", log_path)
        return

    # Submit orders to Alpaca with safety checks and logging
    with open(log_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["ts", "symbol", "side", "qty", "price", "desired_dollar", "current_qty", "order_id", "status", "detail"])
        writer.writeheader()
        for o in orders:
            if o["qty"] <= 0:
                continue
            if o["qty"] > args.max_qty_per_order:
                print(f"Reducing {o['symbol']} qty from {o['qty']} to max {args.max_qty_per_order}")
                o["qty"] = args.max_qty_per_order
            try:
                resp = api.submit_order(symbol=o["symbol"], qty=o["qty"], side=o["side"], type="market", time_in_force="day")
                writer.writerow({"ts": timestamp, "symbol": o["symbol"], "side": o["side"], "qty": o["qty"], "price": o["price"], "desired_dollar": o["desired_dollar"], "current_qty": o["current_qty"], "order_id": resp.id, "status": "submitted", "detail": ""})
                print(f"Submitted {o['side']} {o['qty']} {o['symbol']} order id {resp.id}")
            except APIError as e:
                writer.writerow({"ts": timestamp, "symbol": o["symbol"], "side": o["side"], "qty": o["qty"], "price": o["price"], "desired_dollar": o["desired_dollar"], "current_qty": o["current_qty"], "order_id": "", "status": "failed", "detail": str(e)})
                print(f"FAILED submitting {o['symbol']}: {e}")

    print("Order submission complete. Log:", log_path)

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--predictions", required=True, help="Predictions CSV (single-row or multiple rows, columns=tickers)")
    p.add_argument("--dry-run", action="store_true", help="Print planned orders but do not submit")
    p.add_argument("--pred-is-vol", action="store_true", default=True, help="Treat predictions as predicted volatility (use inverse) (default: true)")
    p.add_argument("--max-pos-pct", type=float, default=0.20, help="Max fraction of portfolio per ticker")
    p.add_argument("--fraction-invest", type=float, default=0.95, help="Fraction of equity to allocate to models")
    p.add_argument("--min-cash", type=float, default=50.0, help="Minimum cash required to continue")
    p.add_argument("--virtual-cash", type=float, default=100000.0, help="Virtual cash for dry-run")
    p.add_argument("--alpaca-base-url", type=str, default=None, help="Alpaca base URL (optional, otherwise uses env ALPACA_BASE_URL)")
    p.add_argument("--max-qty-per-order", type=int, default=1000, help="Max absolute qty to submit per order")
    p.add_argument("--dry-price", type=float, default=None, help="Price to use for dry-run if Alpaca not available")
    args = p.parse_args()
    main(args)
