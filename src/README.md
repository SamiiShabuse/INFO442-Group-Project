# Source Code Folder

This folder contains reusable Python code that supports the notebooks, scripts,
and dashboard.

The project now uses a package-style layout under `src/portfolio_risk/`. New
shared logic should go into that package instead of being copied into notebooks
or standalone scripts.

## What Belongs Here

- Data loading helpers
- Cleaning and preprocessing functions
- Feature engineering functions
- Model training and evaluation helpers
- Portfolio optimization functions
- Order-generation helpers for simulated/paper rebalancing
- Shared plotting or metric utilities
- Code used by both notebooks and the dashboard

## What Does Not Belong Here

- Raw or processed datasets
- Notebook-only scratch work
- Final reports or slides
- Dashboard app files that are only used by Streamlit

## Intended Relationship With Notebooks

Notebooks in `notebooks/` should explain and visualize the workflow. Shared
implementation details should live in `src/portfolio_risk/`, then be imported
by notebooks, command-line scripts, and the dashboard.

## Current Package Layout

```text
portfolio_risk/
    __init__.py
    config.py
    data_fetching.py
    evaluation.py
    features.py
    modeling.py
    orders.py
    paths.py
    portfolio.py
```

- `portfolio_risk.config`: shared constants for trading days, benchmark ticker,
  date/ticker columns, model target, prediction, and actual-volatility columns.
- `portfolio_risk.data_fetching`: Yahoo chart and FRED macro data fetching
  utilities used by the live feature refresh workflow.
- `portfolio_risk.evaluation`: completed-window model evaluation,
  trailing-volatility comparison, and shared regression metric utilities.
- `portfolio_risk.features`: latest feature snapshot refresh logic, macro
  context merging, ticker loading, and rolling market feature engineering.
- `portfolio_risk.modeling`: selected-feature loading, date-column detection,
  model validation, model loading, feature matrix construction, and prediction
  frame helpers.
- `portfolio_risk.orders`: reusable logic for converting target weights into
  dry-run buy/sell/hold rebalance orders.
- `portfolio_risk.paths`: shared project paths for data, notebooks, docs,
  scripts, model outputs, live predictions, and paper-order outputs.
- `portfolio_risk.portfolio`: reusable portfolio math, risk/return metrics,
  Random Forest predictive covariance construction, and optimization.

The order-generation module does not submit real trades. It creates structured
CSV outputs that can be reviewed, visualized, or used later by a separate paper
trading integration.

## Compatibility Wrappers

The older top-level modules still exist for now:

```text
portfolio_optimizer.py
order_generation.py
```

They re-export the new package modules so older notebooks or scripts do not
break immediately. New code should import from `portfolio_risk.portfolio` and
`portfolio_risk.orders` directly.
