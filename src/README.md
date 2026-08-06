# Source Code Folder

This folder is for reusable Python code that supports the notebooks and dashboard.

Right now, most project logic still lives in notebooks. As the project matures, repeated or important logic should move here so it can be imported and reused.

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

Notebooks in `notebooks/` should explain and run the workflow. Shared implementation details should eventually live in `src/`, then be imported into notebooks and the dashboard.

## Current Modules

- `portfolio_optimizer.py`: reusable portfolio math, risk/return metrics, Random Forest predictive covariance construction, and optimization.
- `order_generation.py`: reusable logic for converting target weights into dry-run buy/sell/hold rebalance orders.

The order-generation module does not submit real trades. It creates structured
CSV outputs that can be reviewed, visualized, or used later by a separate paper
trading integration.
