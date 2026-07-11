# Dashboard Folder

This folder is reserved for the interactive dashboard, likely built with Streamlit.

The dashboard should use the cleaned project outputs from `data/processed/`, especially:

- `data/processed/integrated/`
- `data/processed/features/`
- `data/processed/modeling/`

## What Belongs Here

- Main Streamlit app file
- Dashboard pages or components
- Dashboard-specific chart code
- Dashboard-specific helper files

## What Does Not Belong Here

- Raw source data
- Notebook experiments
- General-purpose modeling or cleaning logic
- Final written reports or slides

Reusable logic should go in `src/` when possible, then be imported by the dashboard. This keeps the dashboard focused on interaction and presentation.
