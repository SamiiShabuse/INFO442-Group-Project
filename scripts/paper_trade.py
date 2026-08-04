#!/usr/bin/env python3
"""
scripts/paper_trade.py

Usage (dry run):
Python scripts/paper_trade.py --predictions predicitions/latest_preds.csv --dry-run

Live (paper account; set the env vars first or .env):
export ALPACA_API_KEY=...
export ALPACA_SECRET_KEY=...
python scripts/paper_trade.py --predictions predictions/latest_preds.csv`
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
    