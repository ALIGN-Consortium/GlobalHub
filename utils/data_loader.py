import pandas as pd
import numpy as np
import random
from pathlib import Path
from .config import DATA_PATH, POP_DATA_PATH, COLORS


def _load_csv(path: str) -> pd.DataFrame:
    """
    Loads the raw CSV data from the specified path.
    
    Usage:
        Called internally by `load_data()` to fetch the main dataset.
        
    Args:
        path (str): The file path to the CSV.
        
    Returns:
        pd.DataFrame: The loaded pandas DataFrame.
        
    Raises:
        FileNotFoundError: If the file does not exist.
        RuntimeError: If there is an error during parsing.
    """
    try:
        # Load the new HorizonData.csv with latin1 encoding to handle potential special characters
        df = pd.read_csv(path, encoding="latin1")
        return df
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Data file not found at {path}. Please check the path."
        )
    except Exception as e:
        raise RuntimeError(f"Error loading data: {e}")


def _preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans, filters, and types the raw dataframe.
    
    Usage:
        Called internally by `load_data()` immediately after loading.
    
    Key Logic:
        1.  **Date Conversion**: Parses multiple date columns using `dayfirst=True` and `format='mixed'` to handle inconsistent date formats (e.g., DD-MM-YYYY vs MM/DD/YYYY).
        2.  **Market Year**: Extracts the year from `expected_date_of_market` to drive timeline charts.
        3.  **Numeric Conversion**: Coerces key metrics (scores, DALYs, costs) to numeric types, filling NaNs with 0 to ensure downstream calculations don't fail.
        4.  **Category Cleanup**: Strips whitespace from category names to ensure grouping consistency.
        
    Args:
        df (pd.DataFrame): Raw dataframe.
        
    Returns:
        pd.DataFrame: Processed dataframe ready for analysis.
    """

    #  Date Conversions 
    date_cols = [
        "expected_date_of_market",
        "expected_date_of_regulatory_approval",
        "expected_date_of_first_launch",
        "nra_date",
        "gra_date",
        "eml_date",
        "date_trial_status",
    ]

    for col in date_cols:
        if col in df.columns:
            # Using dayfirst=True and format='mixed' to handle various formats (dd-mm-YYYY, d/m/yy)
            # errors='coerce' turns unparseable dates into NaT
            df[col] = pd.to_datetime(
                df[col], dayfirst=True, format="mixed", errors="coerce"
            )

    # Market Year Generation 
    # Used for the "Forecast of products" trend chart in Overview
    if "expected_date_of_market" in df.columns:
        df["market_year"] = df["expected_date_of_market"].dt.year
    else:
        df["market_year"] = 2025  # Default fallback if missing

    #  Numeric Conversions 
    # Ensures all metric columns are actual numbers for plotting/calculations
    numeric_cols = [
        "prob_success",
        "readiness",
        "financing",
        "efficacy",
        "dalys",
        "dalys_averted",
        "deaths_averted",
        "yll",
        "hs_costs",
        "dalys_monetized",
        "time_to_regulatory_approval",
        "time_approval_to_first_launch",
        "time_launch_to_20lmic",
    ]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    #  Category Cleanup 
    if "category" in df.columns:
        df["category"] = df["category"].str.strip()

    return df


def _process_pipeline(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregates pipeline data by year and category to create a cumulative timeline.
    
    Usage:
        Used by the `trend_chart` in `modules/overview.py`.
        
    Key Logic:
        1.  Groups data by `market_year` and `category`.
        2.  Fills missing years between min and max year (2025-2035) to ensure a continuous X-axis.
        3.  Calculates the **cumulative sum** (cumsum) of innovations over time.
        
    Args:
        df (pd.DataFrame): Preprocessed horizon dataframe.
        
    Returns:
        pd.DataFrame: A dataframe with columns ['year', 'category1', 'category2'...] representing cumulative counts.
    """
    if "market_year" not in df.columns or "category" not in df.columns:
        return pd.DataFrame()

    # Create a pivot table: Rows=Year, Cols=Category, Values=Count
    pipeline_raw = df.groupby(["market_year", "category"]).size().unstack(fill_value=0)

    # Determine timeline range
    min_year = 2025
    max_year = (
        int(pipeline_raw.index.max())
        if not pipeline_raw.empty and not pd.isna(pipeline_raw.index.max())
        else 2035
    )
    all_years = range(min_year, max_year + 1)

    # Reindex to include all years (filling 0 for years with no new products)
    if not pipeline_raw.empty:
        pipeline_raw.index = pipeline_raw.index.astype(int)

    pipeline_reindexed = pipeline_raw.reindex(all_years, fill_value=0)
    
    # Calculate cumulative sum
    pipeline = pipeline_reindexed.cumsum().reset_index()
    pipeline = pipeline.rename(columns={"index": "year", "market_year": "year"})

    # Ensure integer types for counts
    for col in pipeline.columns:
        if col != "year":
            pipeline[col] = pipeline[col].astype(int)

    return pipeline


def _process_readiness(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates the distribution of innovations across different trial statuses.
    
    Usage:
        Used by the `pie_chart` in `modules/overview.py`.
        
    Key Logic:
        1.  Counts occurrences of each `trial_status`.
        2.  Calculates percentage of total.
        3.  Assigns consistent colors from `COLORS` config.
        
    Args:
        df (pd.DataFrame): Preprocessed horizon dataframe.
        
    Returns:
        pd.DataFrame: Columns ['status', 'count', 'pct', 'colors'].
    """
    if "trial_status" not in df.columns:
        return pd.DataFrame(columns=["status", "pct", "colors"])

    stage_counts = df["trial_status"].value_counts().reset_index()
    stage_counts.columns = ["status", "count"]
    total_innovations = len(df)
    stage_counts["pct"] = (stage_counts["count"] / total_innovations * 100).round(1)

    base_colors = COLORS["status_colors"]
    stage_counts["colors"] = [
        base_colors[i % len(base_colors)] for i in range(len(stage_counts))
    ]
    return stage_counts[["status", "pct", "colors"]]


def load_data() -> dict:
    """
    Main orchestration function to load, process, and return all dashboard data structures.
    
    Usage:
        Called by every module (`overview.py`, `innovation_details.py`, `comparison.py`) to access data.
        
    Key Logic:
        1.  Loads main horizon data.
        2.  Preprocesses (dates, numerics).
        3.  **Population Merge**: Loads external `PopulationData.csv` and merges it into the main dataframe based on `country` and `disease`.
            *   *Priority*: Prefers `targeted_population` from PopulationData.csv.
            *   *Fallback*: Uses `targeted_population` from HorizonData.csv if the merge yields no result.
        4.  Generates aggregated datasets (`pipeline`, `readiness`) for charts.
        
    Returns:
        dict: A dictionary containing:
            - "pipeline": DataFrame for trend charts.
            - "readiness": DataFrame for pie charts.
            - "horizon": The fully processed and merged main DataFrame.
    """
    df = _load_csv(DATA_PATH)
    df = _preprocess_data(df)

    # --- Population Data Integration ---
    try:
        pop_df = _load_csv(POP_DATA_PATH)
        
        # Ensure consistent formatting for merge keys (strip whitespace)
        for d in [df, pop_df]:
            if "country" in d.columns:
                d["country"] = d["country"].astype(str).str.strip()
            if "disease" in d.columns:
                d["disease"] = d["disease"].astype(str).str.strip()

        # Merge population data based on country and disease
        df = pd.merge(
            df,
            pop_df[["country", "disease", "targeted_population", "pop_description"]],
            on=["country", "disease"],
            how="left",
        )
        
        # Rename the merged 'targeted_population' column to 'people_at_risk' for internal consistency
        df = df.rename(columns={"targeted_population": "people_at_risk"})
        
        # Priority Logic: 
        # 1. 'people_at_risk' (from PopulationData.csv) is the default.
        # 2. If that is NaN (merge failed/no match), fill it with 'targeted_population' from the original HorizonData.csv.
        if "targeted_population" in df.columns:
            df["people_at_risk"] = df["people_at_risk"].fillna(df["targeted_population"])
            
    except Exception as e:
        print(f"Warning: Could not load or merge population data: {e}")
        # Fallback if PopulationData.csv is missing entirely
        df["people_at_risk"] = df.get("targeted_population", 0)

    #  Aggregation 
    pipeline = _process_pipeline(df)
    readiness = _process_readiness(df)

    return {
        "pipeline": pipeline,
        "readiness": readiness,
        "horizon": df,
    }