# Global Hub Dashboard (ALIGN)

A Python Shiny application for the Global Hub Dashboard. It visualizes innovation pipeline data, readiness assessments, and impact analysis from curated CSV inputs.

## What this app expects (data flow)

The dashboard reads one or more CSV files from the repository (or a configured data path), loads them into **Pandas**, applies lightweight cleaning and recoding, and drives all UI tabs (overview, innovation details, comparisons) from the processed dataset.

## Data sources and location

By default, data files live under:

```
www/
```

Example:
```
www/HorizonScanCombined.csv
```

If your project uses a different data directory, update both this documentation and the data loader accordingly.

## Required data structure (high level)

Each row represents an innovation (or an innovation–timepoint record). Columns include identifiers and metrics used across the dashboard, such as:

- Innovation name or ID  
- Category / domain  
- Stage or maturity  
- Readiness indicators  
- Impact-related fields  

If the app fails at startup, verify:

1. The CSV exists at the expected path  
2. Column names match what the UI modules reference  

## Updating or refreshing data

1. Replace or update the CSV file(s) in the `www/` directory  
2. Re-run the application  
3. If column names or fields change, update the data loader and any UI modules that reference those fields  

## Dependency management (uv-first)

This repository uses **uv** with:

- `pyproject.toml` — dependency declarations  
- `uv.lock` — resolved dependency lockfile (**source of truth**)  
- `requirements.txt` — exported artifact for compatibility or deployment  

## Prerequisites

- **Python 3.11+**
- **uv** installed (`uv --version`)

## Setup instructions

Create and sync the virtual environment:

```bash
uv venv
uv sync
```

## Running the application

Activate the environment if needed:

**macOS / Linux**
```bash
source .venv/bin/activate
```

**Windows**
```bash
.venv\Scripts\activate
```

Run the app locally:

```bash
shiny run app.py
```

The application will start at a local URL, typically  
`http://127.0.0.1:8000`

## Project structure

- `app.py` — main Shiny application entry point  
- `utils/data_loader.py` — data loading and processing logic  
- `overview.py`, `innovation_details.py`, `comparison.py` — tab-specific UI/server logic  
- `www/` — static assets and CSV data files  
- `pyproject.toml` — dependency declarations  
- `uv.lock` — locked dependency resolution  
- `requirements.txt` — exported dependencies for deployment  

