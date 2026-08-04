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