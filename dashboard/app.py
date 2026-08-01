"""
Portfolio Optimization & Risk Analytics Dashboard
INFO 442 Group Project

Run with: streamlit run dashboard/app.py
"""

import sys

import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go

# ============================================================
# PATHS
# ============================================================
APP_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = APP_DIR.parent
DATA_ROOT = PROJECT_ROOT / "data" / "processed"
MODEL_COMPARISON_PATH = DATA_ROOT / "model_comparison"
MODELING_PATH = DATA_ROOT / "modeling"
PORTFOLIO_PATH = DATA_ROOT / "portfolio_optimization"
INTEGRATED_PATH = DATA_ROOT / "integrated"

sys.path.insert(0, str(PROJECT_ROOT / "src"))
from portfolio_optimizer import (  # noqa: E402
    BENCHMARK,
    build_rf_predicted_covariance_matrix,
    evaluate_portfolio,
    load_returns_matrix,
    load_risk_free_rate,
    load_rf_predicted_volatility,
    optimize_portfolio,
    portfolio_return,
    portfolio_sharpe,
    portfolio_volatility,
)

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


def get_prediction_column(predictions):
    prediction_columns = [c for c in predictions.columns if c.endswith("_prediction")]
    if prediction_columns:
        return prediction_columns[0]

    if "predicted_future_volatility_20d" in predictions.columns:
        return "predicted_future_volatility_20d"

    raise ValueError("No prediction column found in test_predictions.csv")


@st.cache_data
def load_portfolio_data():
    try:
        return pd.read_csv(PORTFOLIO_PATH / "portfolio_performance_metrics.csv")
    except FileNotFoundError:
        return None


@st.cache_data
def load_optimizer_inputs():
    returns_matrix = load_returns_matrix(INTEGRATED_PATH)
    risk_free_rate = load_risk_free_rate(INTEGRATED_PATH)
    rf_predicted_vol_matrix = load_rf_predicted_volatility(MODELING_PATH)
    return returns_matrix, risk_free_rate, rf_predicted_vol_matrix


# ============================================================
# SIDEBAR NAVIGATION
# ============================================================

st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Go to",
    ["Overview", "Model Comparison", "Prediction Explorer", "Portfolio Strategies", "Live Optimizer"],
)

MODEL_FOLDERS = {
    "Linear Regression": "linear_regression",
    "Ridge Regression": "ridge_regression",
    "Random Forest": "random_forest",
    "Gradient Boosting": "gradient_boosting",
    "Neural Network MLP": "neural_network_mlp",
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
        - **Model Comparison** - how our 4 volatility prediction models (+ GARCH baseline) stack up
        - **Prediction Explorer** - see predicted vs. actual volatility for any model/ticker
        - **Portfolio Strategies** - compare portfolio construction approaches on the 2024+ test period
        - **Live Optimizer** - build and backtest your own portfolio using random forest predicted volatility
        """
    )

    try:
        all_ticker, garch = load_model_comparison()
        col1, col2, col3 = st.columns(3)
        best_model_row = all_ticker.sort_values("RMSE").iloc[0]
        col1.metric("Best Model (by RMSE)", best_model_row["model"])
        col2.metric("Best RMSE", f"{best_model_row['RMSE']:.5f}")
        col3.metric("Best R2", f"{best_model_row['R2']:.3f}")
    except FileNotFoundError:
        st.warning(
            "Model comparison files were not found. Expected "
            "`data/processed/model_comparison/` under the project root."
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
            "Model comparison files were not found. Expected "
            "`data/processed/model_comparison/` under the project root."
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

    best_model_row = all_ticker.sort_values("RMSE").iloc[0]
    st.caption(
        f"{best_model_row['model']} currently has the lowest RMSE and highest R2 "
        "among the all-ticker models, making it the strongest predictive model "
        "after feature selection."
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

    try:
        pred_col = get_prediction_column(preds)
    except ValueError as error:
        st.error(str(error))
        st.stop()

    if "absolute_error" not in preds.columns:
        preds["absolute_error"] = (
            preds["future_volatility_20d"] - preds[pred_col]
        ).abs()

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
        title=f"{model_name} - Predicted vs. Actual Volatility ({ticker})",
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
            "Portfolio performance metrics were not found. Expected "
            "`data/processed/portfolio_optimization/portfolio_performance_metrics.csv`."
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

# ============================================================
# PAGE: LIVE OPTIMIZER
# ============================================================

elif page == "Live Optimizer":
    st.title("Live Optimizer")
    st.markdown(
        "Pick assets and an objective, and this solves for portfolio weights "
        "using the **random forest** model's predicted 20-day volatility "
        "(our best-performing volatility model) combined with historical asset "
        "correlations as the risk model, instead of purely historical volatility."
    )

    try:
        returns_matrix, risk_free_rate, rf_predicted_vol_matrix = load_optimizer_inputs()
    except FileNotFoundError:
        st.error(
            "Could not load return or prediction data. Expected "
            "`data/processed/integrated/daily_market_data.csv` and "
            "`data/processed/modeling/random_forest/test_predictions.csv`."
        )
        st.stop()

    all_assets = [ticker for ticker in returns_matrix.columns if ticker != BENCHMARK]

    train_returns = returns_matrix[returns_matrix.index < "2024-01-01"]
    test_returns = returns_matrix[returns_matrix.index >= "2024-01-01"]
    train_risk_free_rate = risk_free_rate.loc[train_returns.index].mean()
    test_risk_free_rate = risk_free_rate.loc[test_returns.index].mean()

    selected_assets = st.multiselect("Assets to include", options=all_assets, default=all_assets)

    col1, col2 = st.columns(2)
    objective_label = col1.radio("Optimization objective", ["Minimize Volatility", "Maximize Sharpe Ratio"])
    objective = "min_volatility" if objective_label == "Minimize Volatility" else "max_sharpe"
    max_weight = col2.slider("Maximum weight per asset", min_value=0.10, max_value=1.0, value=0.25, step=0.05)

    if st.button("Optimize Portfolio", type="primary"):
        if len(selected_assets) < 2:
            st.warning("Select at least 2 assets to optimize a portfolio.")
            st.stop()

        train_asset_returns = train_returns[selected_assets]
        test_asset_returns = test_returns[selected_assets]

        mean_returns = train_asset_returns.mean()
        correlation_matrix = train_asset_returns.corr()
        historical_volatility = train_asset_returns.std()
        historical_covariance_matrix = train_asset_returns.cov()

        rf_covariance_matrix, prediction_date, missing_assets = build_rf_predicted_covariance_matrix(
            selected_assets, rf_predicted_vol_matrix, correlation_matrix, historical_volatility
        )

        if missing_assets:
            st.info(
                f"No random forest prediction available for {', '.join(missing_assets)}; "
                "falling back to historical volatility for those assets."
            )

        rf_result = optimize_portfolio(
            objective, mean_returns, rf_covariance_matrix, train_risk_free_rate, max_weight
        )
        historical_result = optimize_portfolio(
            objective, mean_returns, historical_covariance_matrix, train_risk_free_rate, max_weight
        )
        equal_weights = np.repeat(1 / len(selected_assets), len(selected_assets))

        if not rf_result.success:
            st.error(f"Optimization did not converge: {rf_result.message}")
            st.stop()

        rf_weights = rf_result.x
        historical_weights = historical_result.x

        col1, col2 = st.columns([2, 1])

        with col1:
            weights_df = pd.DataFrame(
                {"Asset": selected_assets, "Weight": rf_weights}
            ).sort_values("Weight", ascending=False)
            fig = px.bar(weights_df, x="Asset", y="Weight", title="Optimized Weights (RF Predictive)")
            fig.update_layout(yaxis_tickformat=".0%")
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("Expected Metrics (train period)")
            st.metric("Expected Annual Return", f"{portfolio_return(rf_weights, mean_returns):.2%}")
            st.metric("Expected Annual Volatility", f"{portfolio_volatility(rf_weights, rf_covariance_matrix):.2%}")
            st.metric(
                "Expected Sharpe Ratio",
                f"{portfolio_sharpe(rf_weights, mean_returns, rf_covariance_matrix, train_risk_free_rate):.2f}",
            )
            st.caption(f"Risk model uses RF volatility predictions as of {prediction_date.date()}.")

        st.subheader("Backtest on 2024+ Test Period")
        backtest_rows = [
            evaluate_portfolio("RF Predictive", rf_weights, test_asset_returns, test_risk_free_rate),
            evaluate_portfolio("Historical (same assets)", historical_weights, test_asset_returns, test_risk_free_rate),
            evaluate_portfolio("Equal Weight (same assets)", equal_weights, test_asset_returns, test_risk_free_rate),
        ]
        backtest_df = pd.DataFrame(backtest_rows).set_index("strategy")
        st.dataframe(
            backtest_df.style.format(
                {
                    "annualized_return": "{:.2%}",
                    "annualized_volatility": "{:.2%}",
                    "sharpe_ratio": "{:.2f}",
                    "max_drawdown": "{:.2%}",
                    "cumulative_return": "{:.2%}",
                }
            ),
            use_container_width=True,
        )

        cumulative = pd.DataFrame(index=test_asset_returns.index)
        cumulative["RF Predictive"] = (1 + test_asset_returns.dot(rf_weights)).cumprod() - 1
        cumulative["Historical"] = (1 + test_asset_returns.dot(historical_weights)).cumprod() - 1
        cumulative["Equal Weight"] = (1 + test_asset_returns.dot(equal_weights)).cumprod() - 1
        cumulative["SPY Benchmark"] = (1 + test_returns[BENCHMARK]).cumprod() - 1

        fig2 = px.line(cumulative, title="Backtested Cumulative Return")
        fig2.update_layout(yaxis_tickformat=".0%", legend_title_text="")
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Choose assets and an objective above, then click **Optimize Portfolio**.")
