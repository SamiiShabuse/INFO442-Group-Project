"""
Portfolio Optimization & Risk Analytics Dashboard
INFO 442 Group Project

Run with: streamlit run app.py
(from the notebooks/04_modeling/ folder, or adjust DATA_ROOT below to match
wherever this file lives relative to data/processed/)
"""

import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go

# ============================================================
# PATHS - adjust DATA_ROOT if you place this file somewhere
# other than notebooks/04_modeling/ or notebooks/dashboard/
# ============================================================
DATA_ROOT = Path("../data/processed")
MODEL_COMPARISON_PATH = DATA_ROOT / "model_comparison"
MODELING_PATH = DATA_ROOT / "modeling"
PORTFOLIO_PATH = DATA_ROOT / "portfolio"  # placeholder - adjust once Samii confirms actual folder name

st.set_page_config(
    page_title="Portfolio Optimization Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# DATA LOADING (cached so the app doesn't re-read CSVs on every click)
# ============================================================

@st.cache_data
def load_model_comparison():
    all_ticker = pd.read_csv(MODEL_COMPARISON_PATH / "all_ticker_model_comparison_metrics.csv")
    garch = pd.read_csv(MODEL_COMPARISON_PATH / "garch_spy_comparison_metrics.csv")
    return all_ticker, garch


@st.cache_data
def load_predictions(model_folder):
    path = MODELING_PATH / model_folder / "test_predictions.csv"
    df = pd.read_csv(path, parse_dates=["Date"])
    return df


@st.cache_data
def load_portfolio_data():
    """
    Placeholder loader - update the filename(s) below once you have
    Samii's actual saved portfolio output file(s). Expected shape based
    on the weekly summary: one row per strategy with columns like
    strategy, annualized_return, annualized_volatility, sharpe_ratio,
    max_drawdown, cumulative_return.
    """
    try:
        return pd.read_csv(PORTFOLIO_PATH / "portfolio_strategy_metrics.csv")
    except FileNotFoundError:
        return None


# ============================================================
# SIDEBAR NAVIGATION
# ============================================================

st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Go to",
    ["Overview", "Model Comparison", "Prediction Explorer", "Portfolio Strategies"],
)

MODEL_FOLDERS = {
    "Linear Regression": "linear_regression",
    "Ridge Regression": "ridge_regression",
    "Random Forest": "random_forest",
    "Gradient Boosting": "gradient_boosting",
}

# ============================================================
# PAGE: OVERVIEW
# ============================================================

if page == "Overview":
    st.title("Portfolio Optimization & Risk Analytics")
    st.markdown(
        """
        This dashboard summarizes our volatility prediction models and portfolio
        optimization strategies, built on integrated market (Yahoo Finance),
        sector (Wikipedia), and macroeconomic (FRED) data.

        **Use the sidebar to navigate:**
        - **Model Comparison** — how our 4 volatility prediction models (+ GARCH baseline) stack up
        - **Prediction Explorer** — see predicted vs. actual volatility for any model/ticker
        - **Portfolio Strategies** — compare portfolio construction approaches on the 2024+ test period
        """
    )

    try:
        all_ticker, garch = load_model_comparison()
        col1, col2, col3 = st.columns(3)
        best_model_row = all_ticker.sort_values("RMSE").iloc[0]
        col1.metric("Best Model (by RMSE)", best_model_row["model"])
        col2.metric("Best RMSE", f"{best_model_row['RMSE']:.5f}")
        col3.metric("Best R²", f"{best_model_row['R2']:.3f}")
    except FileNotFoundError:
        st.warning(
            "Model comparison files not found. Make sure this app runs from a location "
            "where `../../data/processed/model_comparison/` resolves correctly, or update "
            "DATA_ROOT at the top of app.py."
        )

# ============================================================
# PAGE: MODEL COMPARISON
# ============================================================

elif page == "Model Comparison":
    st.title("Model Comparison")

    try:
        all_ticker, garch = load_model_comparison()
    except FileNotFoundError:
        st.error(
            "Could not find model_comparison CSVs. Check that DATA_ROOT at the top "
            "of app.py points to the right data/processed folder."
        )
        st.stop()

    st.subheader("All-Ticker Volatility Prediction Models")
    st.dataframe(all_ticker, use_container_width=True)

    metric_choice = st.radio("Metric to compare", ["RMSE", "MAE", "R2"], horizontal=True)

    fig = px.bar(
        all_ticker.sort_values(metric_choice, ascending=(metric_choice != "R2")),
        x="model",
        y=metric_choice,
        color="model",
        title=f"{metric_choice} by Model (lower is better, except R2 - higher is better)",
    )
    st.plotly_chart(fig, use_container_width=True)

    st.caption(
        "Gradient Boosting currently has the lowest RMSE and highest R2 among the "
        "all-ticker models, making it the strongest predictive model after adding "
        "the expanded FRED macro features."
    )

    st.subheader("GARCH (SPY-Only Statistical Model)")
    st.markdown(
        "GARCH is shown separately since it was only built for SPY, not every ticker "
        "in the universe, so it isn't directly comparable to the all-ticker models above."
    )
    st.dataframe(garch, use_container_width=True)

# ============================================================
# PAGE: PREDICTION EXPLORER
# ============================================================

elif page == "Prediction Explorer":
    st.title("Prediction Explorer")

    model_name = st.selectbox("Choose a model", list(MODEL_FOLDERS.keys()))
    model_folder = MODEL_FOLDERS[model_name]

    try:
        preds = load_predictions(model_folder)
    except FileNotFoundError:
        st.error(
            f"Could not find test_predictions.csv for {model_name}. "
            f"Expected at data/processed/modeling/{model_folder}/test_predictions.csv"
        )
        st.stop()

    tickers = sorted(preds["ticker"].unique())
    ticker = st.selectbox("Choose a ticker", tickers)

    pred_col = [c for c in preds.columns if c.endswith("_prediction")][0]
    ticker_df = preds[preds["ticker"] == ticker].sort_values("Date")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=ticker_df["Date"], y=ticker_df["future_volatility_20d"],
        name="Actual (20-day future volatility)", line=dict(color="black"),
    ))
    fig.add_trace(go.Scatter(
        x=ticker_df["Date"], y=ticker_df[pred_col],
        name=f"{model_name} Prediction", line=dict(color="crimson", dash="dash"),
    ))
    fig.update_layout(
        title=f"{model_name} — Predicted vs. Actual Volatility ({ticker})",
        xaxis_title="Date", yaxis_title="20-Day Volatility",
    )
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    col1.metric("Mean Absolute Error (this ticker)", f"{ticker_df['absolute_error'].mean():.5f}")
    col2.metric("Rows shown", len(ticker_df))

# ============================================================
# PAGE: PORTFOLIO STRATEGIES
# ============================================================

elif page == "Portfolio Strategies":
    st.title("Portfolio Strategies")

    portfolio_df = load_portfolio_data()

    if portfolio_df is None:
        st.warning(
            "Portfolio output file not found yet. This page is a placeholder built to match "
            "the strategies mentioned in the Week 4 summary: Equal-Weight, Historical Min-Vol, "
            "Historical Max-Sharpe, RF-Predictive Min-Vol, and RF-Predictive Max-Sharpe.\n\n"
            "Once Samii's portfolio optimization notebook output is available, update "
            "PORTFOLIO_PATH and the filename in `load_portfolio_data()` at the top of this file "
            "to point to the real CSV (expected columns: strategy, annualized_return, "
            "annualized_volatility, sharpe_ratio, max_drawdown, cumulative_return)."
        )
    else:
        st.dataframe(portfolio_df, use_container_width=True)

        fig = px.scatter(
            portfolio_df,
            x="annualized_volatility",
            y="annualized_return",
            size="sharpe_ratio",
            color="strategy",
            hover_data=["max_drawdown"],
            title="Risk-Return Tradeoff by Strategy",
        )
        st.plotly_chart(fig, use_container_width=True)

        fig2 = px.bar(
            portfolio_df.sort_values("sharpe_ratio", ascending=False),
            x="strategy", y="sharpe_ratio", color="strategy",
            title="Sharpe Ratio by Strategy",
        )
        st.plotly_chart(fig2, use_container_width=True)
