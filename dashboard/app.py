"""
Portfolio Optimization & Risk Analytics Dashboard

Run with: streamlit run dashboard/app.py
"""

import sys
from math import ceil

import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go
from scipy.optimize import minimize

# ============================================================
# PATHS
# ============================================================
APP_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = APP_DIR.parent
DATA_ROOT = PROJECT_ROOT / "data" / "processed"
MODEL_COMPARISON_PATH = DATA_ROOT / "model_comparison"
MODELING_PATH = DATA_ROOT / "modeling"
INTEGRATED_PATH = DATA_ROOT / "integrated"
PREDICTIVE_VS_HISTORICAL_PATH = DATA_ROOT / "predictive_vs_historical"

sys.path.insert(0, str(PROJECT_ROOT / "src"))
from portfolio_risk.portfolio import (  # noqa: E402
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
def load_predictive_vs_historical_data():
    accuracy = pd.read_csv(PREDICTIVE_VS_HISTORICAL_PATH / "forecast_accuracy_vs_baseline.csv")
    ticker_accuracy = pd.read_csv(
        PREDICTIVE_VS_HISTORICAL_PATH / "forecast_accuracy_by_ticker.csv"
    )
    performance = pd.read_csv(
        PREDICTIVE_VS_HISTORICAL_PATH / "rebalanced_strategy_performance.csv"
    )
    cumulative = pd.read_csv(
        PREDICTIVE_VS_HISTORICAL_PATH / "rebalanced_cumulative_returns.csv",
        parse_dates=["Date"],
    )
    sweep = pd.read_csv(PREDICTIVE_VS_HISTORICAL_PATH / "rebalance_frequency_sweep.csv")
    calibration = pd.read_csv(PREDICTIVE_VS_HISTORICAL_PATH / "risk_model_calibration.csv")
    return accuracy, ticker_accuracy, performance, cumulative, sweep, calibration


@st.cache_data
def load_optimizer_inputs():
    returns_matrix = load_returns_matrix(INTEGRATED_PATH)
    risk_free_rate = load_risk_free_rate(INTEGRATED_PATH)
    rf_predicted_vol_matrix = load_rf_predicted_volatility(MODELING_PATH)
    return returns_matrix, risk_free_rate, rf_predicted_vol_matrix


def compute_efficient_frontier(mean_returns, covariance_matrix, max_weight, n_points=25):
    """
    Builds the efficient frontier by minimizing portfolio volatility for a
    range of target returns, reusing the same portfolio_return/portfolio_volatility
    helpers as the rest of the app so units stay consistent with the metrics
    already shown (e.g. annualized return/volatility).
    """
    n_assets = len(mean_returns)
    bounds = tuple((0, max_weight) for _ in range(n_assets))

    single_asset_returns = [
        portfolio_return(np.eye(n_assets)[i], mean_returns) for i in range(n_assets)
    ]
    target_returns = np.linspace(min(single_asset_returns), max(single_asset_returns), n_points)

    frontier_points = []
    for target in target_returns:
        constraints = (
            {"type": "eq", "fun": lambda w: np.sum(w) - 1},
            {"type": "eq", "fun": lambda w, target=target: portfolio_return(w, mean_returns) - target},
        )
        result = minimize(
            lambda w: portfolio_volatility(w, covariance_matrix),
            np.repeat(1 / n_assets, n_assets),
            method="SLSQP",
            bounds=bounds,
            constraints=constraints,
        )
        if result.success:
            frontier_points.append(
                {"volatility": portfolio_volatility(result.x, covariance_matrix), "return": target}
            )

    return pd.DataFrame(frontier_points)


# ============================================================
# SIDEBAR NAVIGATION
# ============================================================

st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Go to",
    [
        "Overview",
        "Model Comparison",
        "Prediction Explorer",
        "Predictive vs Historical",
        "Live Optimizer",
    ],
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
        - **Predictive vs Historical** - the definitive walk-forward portfolio experiment
        - **Live Optimizer** - build and backtest your own portfolio using random forest predicted volatility
        """
    )

    try:
        all_ticker, garch = load_model_comparison()
        accuracy, _, _, _, sweep, _ = load_predictive_vs_historical_data()
        col1, col2, col3 = st.columns(3)
        best_model_row = all_ticker.sort_values("RMSE").iloc[0]
        rf_mae = accuracy.loc[accuracy["forecast"] == "Random Forest", "MAE"].iloc[0]
        baseline_mae = accuracy.loc[
            accuracy["forecast"] == "Historical baseline (trailing 20d vol)", "MAE"
        ].iloc[0]
        mae_improvement = (baseline_mae - rf_mae) / baseline_mae
        col1.metric("Best Model (by RMSE)", best_model_row["model"])
        col2.metric("Forecast MAE Improvement", f"{mae_improvement:.1%}")
        col3.metric(
            "Lower Volatility Frequencies",
            f"{int((sweep['volatility_advantage'] > 0).sum())}/{len(sweep)}",
        )
    except FileNotFoundError:
        st.warning(
            "Model comparison files were not found. Expected "
            "`data/processed/model_comparison/` and "
            "`data/processed/predictive_vs_historical/` under the project root."
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
# PAGE: PREDICTIVE VS HISTORICAL
# ============================================================

elif page == "Predictive vs Historical":
    st.title("Predictive vs Historical")

    try:
        (
            accuracy,
            ticker_accuracy,
            performance,
            cumulative,
            sweep,
            calibration,
        ) = load_predictive_vs_historical_data()
    except FileNotFoundError:
        st.error(
            "Predictive-vs-historical outputs were not found. Expected "
            "`data/processed/predictive_vs_historical/` under the project root."
        )
        st.stop()

    rf_accuracy = accuracy.loc[accuracy["forecast"] == "Random Forest"].iloc[0]
    baseline_accuracy = accuracy.loc[
        accuracy["forecast"] == "Historical baseline (trailing 20d vol)"
    ].iloc[0]
    mae_improvement = (
        (baseline_accuracy["MAE"] - rf_accuracy["MAE"]) / baseline_accuracy["MAE"]
    )
    volatility_wins = int((sweep["volatility_advantage"] > 0).sum())
    sharpe_wins = int((sweep["sharpe_advantage"] > 0).sum())

    st.markdown(
        "Machine-learned volatility forecasts improved forecast accuracy and "
        "consistently lowered realized portfolio volatility, while Sharpe-ratio "
        "improvement was not robust across rebalance frequencies."
    )

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("RF MAE", f"{rf_accuracy['MAE']:.5f}")
    col2.metric("Trailing Baseline MAE", f"{baseline_accuracy['MAE']:.5f}")
    col3.metric("MAE Improvement", f"{mae_improvement:.1%}")
    col4.metric("Lower Volatility", f"{volatility_wins}/{len(sweep)} frequencies")

    metric_choice = st.radio("Forecast metric", ["MAE", "RMSE", "R2"], horizontal=True)
    fig = px.bar(
        accuracy,
        x="forecast",
        y=metric_choice,
        color="forecast",
        title=f"Random Forest vs Trailing Historical Volatility ({metric_choice})",
    )
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        ticker_fig = px.scatter(
            ticker_accuracy,
            x="rmse_baseline",
            y="rmse_rf",
            color="rf_wins",
            hover_name="ticker",
            title="Per-Ticker Forecast Accuracy",
        )
        max_rmse = max(
            ticker_accuracy["rmse_baseline"].max(),
            ticker_accuracy["rmse_rf"].max(),
        )
        ticker_fig.add_trace(
            go.Scatter(
                x=[0, max_rmse],
                y=[0, max_rmse],
                mode="lines",
                name="Equal RMSE",
                line=dict(color="gray", dash="dash"),
            )
        )
        ticker_fig.update_layout(xaxis_title="Baseline RMSE", yaxis_title="RF RMSE")
        st.plotly_chart(ticker_fig, use_container_width=True)

    with col2:
        calibration_long = calibration.melt(
            id_vars="risk_model",
            value_vars=["mean_predicted", "mean_realized"],
            var_name="volatility_type",
            value_name="volatility",
        )
        calibration_fig = px.bar(
            calibration_long,
            x="risk_model",
            y="volatility",
            color="volatility_type",
            barmode="group",
            title="Risk Model Calibration",
        )
        st.plotly_chart(calibration_fig, use_container_width=True)

    st.subheader("Walk-Forward Portfolio Backtest")
    st.dataframe(
        performance.style.format(
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

    cumulative_plot = cumulative.set_index("Date")
    cumulative_fig = px.line(cumulative_plot, title="Walk-Forward Growth of $1")
    cumulative_fig.update_layout(yaxis_tickformat=".0%", legend_title_text="")
    st.plotly_chart(cumulative_fig, use_container_width=True)

    sweep_long = sweep.melt(
        id_vars="rebalance_days",
        value_vars=["rf_volatility", "matched_volatility"],
        var_name="risk_model",
        value_name="annualized_volatility",
    )
    sweep_fig = px.line(
        sweep_long,
        x="rebalance_days",
        y="annualized_volatility",
        color="risk_model",
        markers=True,
        title="Realized Volatility by Rebalance Frequency",
    )
    sweep_fig.update_layout(yaxis_tickformat=".0%")
    st.plotly_chart(sweep_fig, use_container_width=True)

    st.caption(
        f"RF volatility was lower at {volatility_wins} of {len(sweep)} tested "
        f"frequencies. RF Sharpe was higher at {sharpe_wins} of {len(sweep)}, "
        "so the defensible conclusion is stronger risk control rather than "
        "consistently higher risk-adjusted returns."
    )

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

    st.subheader("Risk Profile")
    RISK_PRESETS = {
        "Conservative": {"objective_label": "Minimize Volatility", "max_weight": 0.15},
        "Balanced": {"objective_label": "Maximize Sharpe Ratio", "max_weight": 0.25},
        "Aggressive": {"objective_label": "Maximize Sharpe Ratio", "max_weight": 0.50},
    }
    risk_profile = st.radio(
        "Choose a preset or customize your own",
        ["Conservative", "Balanced", "Aggressive", "Custom"],
        horizontal=True,
        index=1,
    )

    col1, col2 = st.columns(2)
    if risk_profile == "Custom":
        objective_label = col1.radio("Optimization objective", ["Minimize Volatility", "Maximize Sharpe Ratio"])
        max_weight = col2.slider("Maximum weight per asset", min_value=0.10, max_value=1.0, value=0.25, step=0.05)
    else:
        preset = RISK_PRESETS[risk_profile]
        objective_label = preset["objective_label"]
        max_weight = preset["max_weight"]
        col1.info(f"Objective: **{objective_label}**")
        col2.info(f"Max weight per asset: **{max_weight:.0%}**")

    objective = "min_volatility" if objective_label == "Minimize Volatility" else "max_sharpe"

    if st.button("Optimize Portfolio", type="primary"):
        if len(selected_assets) < 2:
            st.warning("Select at least 2 assets to optimize a portfolio.")
            st.stop()
        if len(selected_assets) * max_weight < 1:
            st.warning(
                f"The {max_weight:.0%} maximum weight cap is infeasible for "
                f"{len(selected_assets)} selected assets. Select at least "
                f"{ceil(1 / max_weight)} assets or choose a higher cap."
            )
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
        if not historical_result.success:
            st.error(f"Historical optimization did not converge: {historical_result.message}")
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

        st.subheader("Efficient Frontier")
        st.markdown(
            "Each point on the curve is the lowest-volatility portfolio achievable for "
            "a given target return, using the same RF-predicted risk model as your "
            "optimized portfolio above. Your portfolio (star) should sit on or very "
            "near the curve if the optimizer converged well."
        )

        with st.spinner("Building efficient frontier..."):
            frontier_df = compute_efficient_frontier(mean_returns, rf_covariance_matrix, max_weight)

        fig_frontier = go.Figure()

        if not frontier_df.empty:
            fig_frontier.add_trace(go.Scatter(
                x=frontier_df["volatility"], y=frontier_df["return"],
                mode="lines", name="Efficient Frontier", line=dict(color="steelblue", width=3),
            ))

        fig_frontier.add_trace(go.Scatter(
            x=[portfolio_volatility(rf_weights, rf_covariance_matrix)],
            y=[portfolio_return(rf_weights, mean_returns)],
            mode="markers", name="Your Optimized Portfolio",
            marker=dict(color="crimson", size=16, symbol="star"),
        ))

        individual_asset_points = pd.DataFrame({
            "Asset": selected_assets,
            "volatility": [
                portfolio_volatility(np.eye(len(selected_assets))[i], rf_covariance_matrix)
                for i in range(len(selected_assets))
            ],
            "return": [
                portfolio_return(np.eye(len(selected_assets))[i], mean_returns)
                for i in range(len(selected_assets))
            ],
        })
        fig_frontier.add_trace(go.Scatter(
            x=individual_asset_points["volatility"], y=individual_asset_points["return"],
            mode="markers+text", name="Individual Assets",
            text=individual_asset_points["Asset"], textposition="top center",
            marker=dict(color="gray", size=8),
        ))

        fig_frontier.update_layout(
            title="Efficient Frontier (RF-Predicted Risk Model)",
            xaxis_title="Annualized Volatility", yaxis_title="Annualized Return",
            xaxis_tickformat=".0%", yaxis_tickformat=".0%",
        )
        st.plotly_chart(fig_frontier, use_container_width=True)

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
