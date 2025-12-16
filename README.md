# Global Hub Dashboard (ALIGN)

This is a Python-based Shiny application for the Global Hub Dashboard. It visualizes innovation pipeline data, readiness assessments, and impact analysis.

## Prerequisites

- **Python 3.11+**
- **pip** (Python package installer)

## Setup Instructions

1.  **Clone or Download the Repository**
    Ensure you have all the files in a local directory.

2.  **Create a Virtual Environment**
    It is recommended to use a virtual environment to manage dependencies.
    
    ```bash
    # macOS/Linux
    python3 -m venv .venv
    source .venv/bin/activate

    # Windows
    python -m venv .venv
    .venv\Scripts\activate
    ```

3.  **Install Dependencies**
    Install the required Python packages using `pip`.

    ```bash
    pip install -r requirements.txt
    ```

## Running the Application

To start the dashboard locally:

```bash
shiny run app.py
```

The application will start, and you should see a URL (typically `http://127.0.0.1:8000`) in the terminal. Open this URL in your web browser.

## Project Structure

- **`app.py`**: The main application entry point (Python Shiny).
- **`data_loader.py`**: Data processing logic and loading routines.
- **`overview.py`, `innovation_details.py`, `comparison.py`**: UI and Server logic for specific dashboard tabs.
- **`www/`**: Static assets and data files (e.g., `HorizonScanCombined.csv`).
- **`requirements.txt`**: List of Python dependencies.
