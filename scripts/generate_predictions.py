"""
Load the trained RF model and latest features; write per-ticker next-day prediction CSVs.

Usage:
python scripts/generate_predictions.py \
    --model models/rf_model.pkl \
    --features data/processed/features/feature_engineered_dataset.csv \
    --out predictions/latest_preds.csv
"""