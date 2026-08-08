"""Central project paths used by scripts, notebooks, and the dashboard."""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

FEATURES_DIR = PROCESSED_DATA_DIR / "features"
INTEGRATED_DATA_DIR = PROCESSED_DATA_DIR / "integrated"
MODELING_DIR = PROCESSED_DATA_DIR / "modeling"
MODEL_COMPARISON_DIR = PROCESSED_DATA_DIR / "model_comparison"
PORTFOLIO_OPTIMIZATION_DIR = PROCESSED_DATA_DIR / "portfolio_optimization"

RANDOM_FOREST_DIR = MODELING_DIR / "random_forest"
RF_LIVE_PREDICTIONS_DIR = RANDOM_FOREST_DIR / "live_predictions"
RF_LIVE_EVALUATION_DIR = RANDOM_FOREST_DIR / "live_evaluation"

LIVE_WEIGHTS_DIR = PORTFOLIO_OPTIMIZATION_DIR / "live_weights"
PAPER_ORDERS_DIR = PORTFOLIO_OPTIMIZATION_DIR / "paper_orders"

DOCS_DIR = PROJECT_ROOT / "docs"
NOTEBOOKS_DIR = PROJECT_ROOT / "notebooks"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
DASHBOARD_DIR = PROJECT_ROOT / "dashboard"
