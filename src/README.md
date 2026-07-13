# Source Code Folder

This folder is for reusable Python code that supports the notebooks and dashboard.

Right now, most project logic still lives in notebooks. As the project matures, repeated or important logic should move here so it can be imported and reused.

## What Belongs Here

- Data loading helpers
- Cleaning and preprocessing functions
- Feature engineering functions
- Model training and evaluation helpers
- Portfolio optimization functions
- Shared plotting or metric utilities
- Code used by both notebooks and the dashboard

## What Does Not Belong Here

- Raw or processed datasets
- Notebook-only scratch work
- Final reports or slides
- Dashboard app files that are only used by Streamlit

## Intended Relationship With Notebooks

Notebooks in `notebooks/` should explain and run the workflow. Shared implementation details should eventually live in `src/`, then be imported into notebooks and the dashboard.
