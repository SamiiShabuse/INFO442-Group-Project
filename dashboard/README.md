# Dashboard

This folder contains the Streamlit dashboard for the project.

Run it from the project root with:

```bash
streamlit run dashboard/app.py
```

The dashboard uses cleaned project outputs from `data/processed/`, especially:

- `data/processed/integrated/`
- `data/processed/features/`
- `data/processed/modeling/`
- `data/processed/model_comparison/`
- `data/processed/portfolio_optimization/`

## Current Pages

- Overview
- Model Comparison
- Prediction Explorer
- Portfolio Strategies

## Notes

Install dashboard dependencies with `pip install -r dashboard/requirements.txt` if Streamlit or Plotly is missing.

The dashboard should stay focused on presentation and interaction. Data cleaning, feature engineering, modeling, and portfolio optimization should continue to live in the notebooks and processed output files.
