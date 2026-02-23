import pandas as pd
from datetime import timedelta
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
        # Load the CSV with utf-8-sig encoding to handle BOM
        df = pd.read_csv(path, encoding="utf-8-sig")
        return df
    except FileNotFoundError:
        # Fallback logic if specific file not found is handled in load_data usually, 
        # but for _load_csv we raise
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
        2.  **Market Year**: Extracts the year from `proj_date_lmic_20_uptake` to drive timeline charts.
        3.  **Numeric Conversion**: Coerces key metrics (scores, DALYs, costs) to numeric types, filling NaNs with 0 to ensure downstream calculations don't fail.
        4.  **Category Cleanup**: Strips whitespace from category names to ensure grouping consistency.

    Args:
        df (pd.DataFrame): Raw dataframe.

    Returns:
        pd.DataFrame: Processed dataframe ready for analysis.
    """
    # Map 'WHO' to 'Overall' to match the app's expected aggregate identifier

    #  Date Conversions
    date_cols = [
        "eml_date",
        "nra_date",
        "gra_date",
        "phase_1_date",
        "phase_2_date",
        "phase_3_date",
        "phase_4_date",
        "date_trial_status",
        "date_market",
        "date_proof_of_concept",
        "date_first_regulatory",
        "date_first_launch",
        "proj_date_first_regulatory",
        "proj_date_first_launch",
        "proj_date_lmic_20_uptake"
    ]

    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(
                df[col], dayfirst=True, format="mixed", errors="coerce"
            ).dt.normalize()  # <- sets time to 00:00:00\

    # Market Year Generation
    # Used for the "Forecast of products" trend chart in Overview
    if "proj_date_lmic_20_uptake" in df.columns:
        df["market_year"] = df["proj_date_lmic_20_uptake"].dt.year

    #  Numeric Conversions
    # Ensures all metric columns are actual numbers for plotting/calculations
    numeric_cols = [
        # "prob_success",
        "readiness",
        "financing",
        # "dalys",
        "dalys_averted",
        "deaths_averted",
        "yll",
        # "hs_costs",
        "dalys_monetized",
        # "time_to_regulatory_approval",
        # "time_approval_to_first_launch",
        # "time_launch_to_20lmic",
        "impact_potential",
        "introduction_readiness"
    ]

    # for col in numeric_cols:
    #     if col in df.columns:
    #         df[col] = pd.to_numeric(df[col], errors="coerce")
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
    min_year = 2025 #?
    max_year = (
        int(pipeline_raw.index.max())
        if not pipeline_raw.empty and not pd.isna(pipeline_raw.index.max())
        else 2035 #?
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
        1.  Counts occurrences of each `trial_status` (which is already recoded).
        2.  Calculates percentage of total.
        3.  Assigns consistent colors from `COLORS` config.

    Args:
        df (pd.DataFrame): Preprocessed horizon dataframe.

    Returns:
        pd.DataFrame: Columns ['status', 'count', 'pct', 'colors'].
    """
    if "trial_status" not in df.columns:
        return pd.DataFrame(columns=["status", "pct", "colors"])

    # Define standard categories for color mapping
    categories = [
        "Preclinical",
        "Phase 1",
        "Phase 2",
        "Phase 3",
        "Phase 4",
        "Observational",
        "Implementation/Pilot",
        "Not in trials",
        "Unknown",
    ]
    
    base_colors = [
        "#94a3b8", # Preclinical (Grey)
        "#60a5fa", # Phase 1 (Blue)
        "#3b82f6", # Phase 2 (Darker Blue)
        "#2563eb", # Phase 3 (Even Darker Blue)
        "#1d4ed8", # Phase 4 (Deep Blue)
        "#a78bfa", # Observational (Purple)
        "#10b981", # Implementation/Pilot (Green)
        "#f43f5e", # Not in trials (Red)
        "#cbd5e1"  # Unknown (Light Grey)
    ]
    color_map = dict(zip(categories, base_colors))

    stage_counts = df["trial_status"].value_counts().reset_index()
    stage_counts.columns = ["status", "count"]
    total_innovations = len(df)
    stage_counts["pct"] = (stage_counts["count"] / total_innovations * 100).round(1)

    stage_counts["colors"] = stage_counts["status"].map(color_map).fillna("#cbd5e1")

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
            - "innovation_df": DataFrame with distinct innovations (Overall country).
            - "country_regulatory_df": DataFrame with country-specific rows.
    """
    
    try:
        raw_df = _load_csv(DATA_PATH)
    except Exception as e:
        print(f"Warning: Could not load data from {DATA_PATH}: {e}")
        raw_df = pd.DataFrame()

    df = _preprocess_data(raw_df)

    # --- 3. Organize DataFrames ---
    # The input CSV is already in long format.
    # horizon_df is the master dataframe.
    horizon_df = df.copy()

    # innovation_df: The aggregate/global view (country="Overall")
    if "scope" in horizon_df.columns:
        innovation_df = horizon_df[horizon_df["scope"] == "WHO"].copy()
        # country_regulatory_df: The specific country rows
        country_regulatory_df = horizon_df[horizon_df["scope"] != "WHO"].copy()
    else:
        innovation_df = pd.DataFrame()
        country_regulatory_df = pd.DataFrame()

    # --- 5. Population Data Integration ---
    try:
        # Load population data with standard utf-8
        pop_df = pd.read_csv(POP_DATA_PATH)
        # Merge population data based on country and disease
        horizon_df = pd.merge(
            horizon_df,
            pop_df[["scope", "disease", "targeted_population", "pop_description"]],
            on=["scope", "disease"],
            how="left",
        )

        # Rename the merged 'targeted_population' column to 'people_at_risk' for internal consistency
        horizon_df = horizon_df.rename(columns={"targeted_population": "people_at_risk"})

        # Priority Logic:
        # 1. 'people_at_risk' (from PopulationData.csv) is the default.
        # 2. If that is NaN (merge failed/no match), fill it with 'target_population' from the original data if available.
        # Note: Original CSV has 'target_population' column, not 'targeted_population' (checked from header).
        if "target_population" in horizon_df.columns:
             horizon_df["people_at_risk"] = horizon_df["people_at_risk"].fillna(horizon_df["target_population"])

    except Exception as e:
        print(f"Warning: Could not load or merge population data: {e}")
        # Fallback
        if "target_population" in horizon_df.columns:
            horizon_df["people_at_risk"] = horizon_df["target_population"]
        else:
            horizon_df["people_at_risk"] = 0

    #  Aggregation
    pipeline = _process_pipeline(horizon_df)
    readiness = _process_readiness(horizon_df)

    return {
        "pipeline": pipeline,
        "readiness": readiness,
        "horizon": horizon_df,
        "innovation_df": innovation_df,
        "country_regulatory_df": country_regulatory_df,
    }
