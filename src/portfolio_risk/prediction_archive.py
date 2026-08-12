"""Reusable workflow for archiving latest prediction runs."""

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from portfolio_risk.config import DATE_COLUMN, PREDICTED_VOLATILITY_COLUMN, TICKER_COLUMN


@dataclass(frozen=True)
class PredictionArchiveResult:
    """Result of archiving one wide latest-prediction file."""

    target_date: str
    dated_path: Path
    log_path: Path
    long_predictions: pd.DataFrame
    prediction_log: pd.DataFrame

    @property
    def ticker_count(self) -> int:
        return len(self.long_predictions)


def load_latest_predictions(path) -> pd.DataFrame:
    """Load the newest wide prediction row from a CSV or file-like object."""
    predictions = pd.read_csv(path, index_col=0, parse_dates=True)
    if predictions.empty:
        raise SystemExit("prediction CSV did not contain any rows")

    latest = predictions.tail(1).copy()
    latest.index.name = DATE_COLUMN
    latest.columns = latest.columns.astype(str)
    return latest


def wide_predictions_to_long(latest: pd.DataFrame) -> tuple[str, pd.DataFrame]:
    """Convert the latest wide prediction row into long log format."""
    if latest.empty:
        raise SystemExit("latest prediction frame did not contain any rows")

    target_date = pd.Timestamp(latest.index[0]).date().isoformat()
    long_predictions = (
        latest.reset_index()
        .melt(
            id_vars=DATE_COLUMN,
            var_name=TICKER_COLUMN,
            value_name=PREDICTED_VOLATILITY_COLUMN,
        )
        .sort_values([DATE_COLUMN, TICKER_COLUMN])
    )
    long_predictions[DATE_COLUMN] = pd.to_datetime(
        long_predictions[DATE_COLUMN]
    ).dt.date.astype(str)
    return target_date, long_predictions


def merge_prediction_log(
    existing_log: pd.DataFrame | None,
    long_predictions: pd.DataFrame,
    target_date: str,
) -> pd.DataFrame:
    """Append latest predictions, replacing any old rows for the same date."""
    if existing_log is not None and not existing_log.empty:
        prediction_log = existing_log.copy()
        prediction_log[DATE_COLUMN] = pd.to_datetime(
            prediction_log[DATE_COLUMN]
        ).dt.date.astype(str)
        prediction_log = prediction_log[prediction_log[DATE_COLUMN] != target_date]
        prediction_log = pd.concat([prediction_log, long_predictions], ignore_index=True)
    else:
        prediction_log = long_predictions.copy()

    return prediction_log.sort_values([DATE_COLUMN, TICKER_COLUMN]).reset_index(drop=True)


def archive_latest_predictions(
    predictions_path: str | Path,
    out_dir: str | Path,
    log_path: str | Path,
) -> PredictionArchiveResult:
    """Archive latest predictions into a dated wide CSV and long prediction log."""
    predictions_path = Path(predictions_path)
    out_dir = Path(out_dir)
    log_path = Path(log_path)

    out_dir.mkdir(parents=True, exist_ok=True)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    latest = load_latest_predictions(predictions_path)
    target_date, long_predictions = wide_predictions_to_long(latest)

    dated_path = out_dir / f"preds_{target_date}.csv"
    latest.to_csv(dated_path)

    existing_log = pd.read_csv(log_path) if log_path.exists() else None
    prediction_log = merge_prediction_log(existing_log, long_predictions, target_date)
    prediction_log.to_csv(log_path, index=False)

    return PredictionArchiveResult(
        target_date=target_date,
        dated_path=dated_path,
        log_path=log_path,
        long_predictions=long_predictions,
        prediction_log=prediction_log,
    )
