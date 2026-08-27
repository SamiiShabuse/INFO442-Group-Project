"""Train and export a Random Forest volatility model.

TLDR: replica of the notebook training flow, but in a repeatable script that exports a model artifact.

This script turns the notebook training flow into a repeatable artifact export:

    python scripts/train_rf_model.py \
        --features data/processed/features/feature_engineered_dataset.csv \
        --selected-features data/processed/features/selected_features.csv \
        --model-out data/processed/modeling/random_forest/rf_model.pkl

The exported model is refit on all labeled rows after hyperparameter tuning so
it can use the most recent rows that have a known 20-day future-volatility
target.
"""

import argparse
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from portfolio_risk.training import (  # noqa: E402
    DEFAULT_MAX_DEPTH,
    DEFAULT_MIN_SAMPLES_LEAF,
    DEFAULT_SPLIT_DATE,
    run_random_forest_training,
)


def main(
    features_path: str,
    selected_features_path: str,
    model_out: str,
    metadata_out: str | None,
    metrics_out: str | None,
    predictions_out: str | None,
    comparison_metrics_out: str | None,
    split_date: str,
    n_jobs: int,
    tune: bool,
    max_depth: int | None,
    min_samples_leaf: int,
) -> None:
    result = run_random_forest_training(
        features_path=features_path,
        selected_features_path=selected_features_path,
        model_out=model_out,
        metadata_out=metadata_out,
        metrics_out=metrics_out,
        predictions_out=predictions_out,
        comparison_metrics_out=comparison_metrics_out,
        split_date=split_date,
        n_jobs=n_jobs,
        tune=tune,
        max_depth=max_depth,
        min_samples_leaf=min_samples_leaf,
        verbose=True,
    )

    print("Wrote model to:", result.model_out)
    print("Wrote metrics to:", result.metrics_out_path)
    print("Wrote metadata to:", result.metadata_out_path)
    if result.predictions_out_path:
        print("Wrote holdout predictions to:", result.predictions_out_path)
    if result.comparison_metrics_out_path:
        print("Wrote notebook metrics to:", result.comparison_metrics_out_path)
    print(result.training.metrics)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train and export the RF volatility model.")
    parser.add_argument(
        "--features",
        default="data/processed/features/feature_engineered_dataset.csv",
        help="Path to the labeled feature-engineered dataset",
    )
    parser.add_argument(
        "--selected-features",
        default="data/processed/features/selected_features.csv",
        help="Path to selected_features.csv",
    )
    parser.add_argument(
        "--model-out",
        default="data/processed/modeling/random_forest/rf_model.pkl",
        help="Path where the trained model should be written",
    )
    parser.add_argument("--metadata-out", default=None, help="Optional metadata JSON path")
    parser.add_argument("--metrics-out", default=None, help="Optional metrics CSV path")
    parser.add_argument(
        "--predictions-out",
        default="data/processed/modeling/random_forest/test_predictions.csv",
        help="Optional notebook-facing holdout predictions CSV path",
    )
    parser.add_argument(
        "--comparison-metrics-out",
        default="data/processed/modeling/random_forest/metrics.csv",
        help="Optional notebook-facing model-comparison metrics CSV path",
    )
    parser.add_argument(
        "--split-date",
        default=DEFAULT_SPLIT_DATE,
        help="Holdout split date used for reporting metrics",
    )
    parser.add_argument(
        "--n-jobs",
        type=int,
        default=1,
        help="Parallel workers for RandomForestRegressor; default 1 for Windows sandbox reliability",
    )
    parser.add_argument(
        "--tune",
        action="store_true",
        help="Run the full notebook-style GridSearchCV before exporting",
    )
    parser.add_argument(
        "--max-depth",
        type=int,
        default=DEFAULT_MAX_DEPTH,
        help="RF max_depth used when --tune is not set",
    )
    parser.add_argument(
        "--min-samples-leaf",
        type=int,
        default=DEFAULT_MIN_SAMPLES_LEAF,
        help="RF min_samples_leaf used when --tune is not set",
    )

    args = parser.parse_args()
    main(
        features_path=args.features,
        selected_features_path=args.selected_features,
        model_out=args.model_out,
        metadata_out=args.metadata_out,
        metrics_out=args.metrics_out,
        predictions_out=args.predictions_out,
        comparison_metrics_out=args.comparison_metrics_out,
        split_date=args.split_date,
        n_jobs=args.n_jobs,
        tune=args.tune,
        max_depth=args.max_depth,
        min_samples_leaf=args.min_samples_leaf,
    )
