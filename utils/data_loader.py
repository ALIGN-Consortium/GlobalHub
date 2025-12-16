import pandas as pd
import numpy as np
import random
from pathlib import Path
from .config import DATA_PATH, COUNTRY_COORDS, COLUMN_MAPPING, COLORS

def _load_csv(path: str) -> pd.DataFrame:
    """Loads and deduplicates the raw CSV data."""
    try:
        df = pd.read_csv(path, encoding="latin1")
        # Remove duplicate innovations, keeping the first occurrence
        df = df.drop_duplicates(subset=["Innovation"]).reset_index(drop=True)
        return df
    except FileNotFoundError:
        raise FileNotFoundError(f"Data file not found at {path}. Please check the path.")
    except Exception as e:
        raise RuntimeError(f"Error loading data: {e}")

def _preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    """Cleans and filters the dataframe."""
    # Ensure trial_completion_date is datetime
    df["trial_completion_date"] = pd.to_datetime(df["trial_completion_date"], errors="coerce")
    
    # Filter out products with very old trial completion dates
    df = df[
        (df["trial_completion_date"].dt.year >= 2016) | 
        (df["trial_completion_date"].isna())
    ]
    
    # Sort and ID generation
    df = df.sort_values(by=["Innovation", "Country"]).reset_index(drop=True)
    df["Innovation"] = df["Innovation"].fillna("Unknown")
    df["id"] = df["Innovation"]

    # Date and Market Year
    df["expected_date_of_market"] = pd.to_datetime(df["expected_date_of_market"], errors="coerce")
    df["market_year"] = df["expected_date_of_market"].dt.year
    df["Category"] = df["Category"].str.strip()
    
    # Forecast period filter
    df = df[df["market_year"] >= 2025]
    
    # Rename columns
    df = df.rename(columns=COLUMN_MAPPING)
    
    # Numeric conversion
    numeric_cols = ["Impact Score", "Impact Potential", "Introduction Readiness", 
                    "Cost-effectiveness", "Readiness", "Time_to_Approval", "Time_to_Market"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
    return df

def _process_pipeline(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregates pipeline data by year and category."""
    pipeline_raw = df.groupby(["market_year", "Category"]).size().unstack(fill_value=0)
    
    min_year = 2025
    max_year = int(pipeline_raw.index.max()) if not pipeline_raw.empty and not pd.isna(pipeline_raw.index.max()) else 2035
    all_years = range(min_year, max_year + 1)
    
    if not pipeline_raw.empty:
        pipeline_raw.index = pipeline_raw.index.astype(int)

    pipeline_reindexed = pipeline_raw.reindex(all_years, fill_value=0)
    pipeline = pipeline_reindexed.cumsum().reset_index()
    pipeline = pipeline.rename(columns={"index": "year", "market_year": "year"})
    
    for col in pipeline.columns:
        if col != "year":
            pipeline[col] = pipeline[col].astype(int)
            
    return pipeline

def _process_readiness(df: pd.DataFrame) -> pd.DataFrame:
    """Calculates readiness percentages and assigns colors."""
    stage_counts = df["Stage"].value_counts().reset_index()
    stage_counts.columns = ["status", "count"]
    total_innovations = len(df)
    stage_counts["pct"] = (stage_counts["count"] / total_innovations * 100).round(1)
    
    base_colors = COLORS["status_colors"]
    stage_counts["colors"] = [base_colors[i % len(base_colors)] for i in range(len(stage_counts))]
    return stage_counts[["status", "pct", "colors"]]

def _process_usage(df: pd.DataFrame) -> pd.DataFrame:
    """Maps country usage data to coordinates."""
    usage_all = df[["id", "Country", "Stage"]].copy()
    usage_all = usage_all.rename(columns={"Country": "country", "Stage": "status"})
    usage_all["lat"] = usage_all["country"].map(lambda x: COUNTRY_COORDS.get(x, {"lat": 0, "lon": 0})["lat"])
    usage_all["lon"] = usage_all["country"].map(lambda x: COUNTRY_COORDS.get(x, {"lat": 0, "lon": 0})["lon"])
    return usage_all

def _process_risks(df: pd.DataFrame) -> pd.DataFrame:
    """Generates risk data."""
    risk_cols = {
        "Probability of technical and regulatory success": "technical_risk",
        "Demand forecasting and generation": "market_risk",
        "Regulatory approvals": "regulatory_risk",
        "Financing": "financial_risk"
    }
    
    risk_data_list = []
    for cat, group in df.groupby("Category"):
        cat_risks = {"category": cat}
        random.seed(hash(cat))
        for src, target in risk_cols.items():
            if src in group.columns:
                val = pd.to_numeric(group[src], errors='coerce').mean()
                if val <= 5: 
                    score_10 = val * 4
                else:
                    score_10 = val / 10
                base_risk = 10 - score_10
                offset = random.uniform(-2, 2)
                final_risk = max(1, min(9, base_risk + offset))
                cat_risks[target] = final_risk
            else:
                cat_risks[target] = random.uniform(4, 8)
        risk_data_list.append(cat_risks)
    return pd.DataFrame(risk_data_list)

def _generate_templates_and_offsets(df: pd.DataFrame):
    """Generates static templates and random offsets."""
    impact_template = pd.DataFrame({
        "metric": [
            "Disease burden", "Epidemiological impact", "Alignment with goals",
            "Cost-effectiveness", "Budget impact", "Resource Optimization"
        ],
        "value": [72, 68, 63, 74, 58, 61],
        "passed": [True, True, False, True, False, True]
    })

    intro_template = pd.DataFrame({
        "subdomain": [
            "Financing", "Financing", "Policy", "Policy", "Policy", "Policy", "Policy",
            "Uptake/Delivery", "Uptake/Delivery", "Uptake/Delivery", "Uptake/Delivery"
        ],
        "metric": [
            "Probability of technical and regulatory success", "Procurement model",
            "Regulatory Approvals", "Policy Readiness", "Social context",
            "Guidelines and training", "Policy Implemented",
            "Advance launch and planning / timeline", "Demand Forecasting and generation",
            "Potential supply chain", "Delivery model"
        ],
        "value": [65, 60, 62, 58, 55, 57, 50, 63, 59, 61, 60],
        "passed": [True, True, True, False, False, False, False, True, True, True, True]
    })

    id_offsets = {}
    for pid in df["id"].unique():
        random.seed(hash(pid))
        id_offsets[pid] = {
            "impact": [random.randint(-20, 20) for _ in range(6)],
            "impact_passed": [random.choice([True, False]) for _ in range(6)],
            "intro_delta": [random.randint(-10, 10) for _ in range(11)],
            "intro_passed_delta": [random.choice([True, False]) for _ in range(11)]
        }
        
    return impact_template, intro_template, id_offsets

def _process_impact_and_readiness(df: pd.DataFrame):
    """Aggregates impact and readiness data by country and category."""
    # Impact Data
    impact_dat_all = df.groupby(["Country", "Category"]).agg({
        "Impact Score": "mean",
        "Cost-effectiveness": "mean"
    }).reset_index()
    impact_dat_all = impact_dat_all.rename(columns={"Impact Score": "impact", "Cost-effectiveness": "cost_eff"})
    
    overall_impact = impact_dat_all[impact_dat_all["Country"] != "Overall"].groupby("Category").agg({
        "impact": "mean",
        "cost_eff": "mean"
    }).reset_index()
    overall_impact["Country"] = "Overall"
    
    impact_dat_all = impact_dat_all[impact_dat_all["Country"] != "Overall"]
    impact_dat_all = pd.concat([impact_dat_all, overall_impact])
    impact_dat_all = impact_dat_all.rename(columns={"Country": "country", "Category": "category"})

    # Readiness Data
    def check_ready(stage):
        s = str(stage).lower()
        keywords = ["phase 2", "phase ii", "phase 3", "phase iii", "market", "ready", "stockpiled"]
        return any(k in s for k in keywords)

    df["is_ready"] = df["Stage"].apply(check_ready)
    
    readiness_cat_all = df.groupby(["Country", "Category"]).agg(
        ready=("is_ready", "sum"),
        total=("id", "count")
    ).reset_index()
    
    overall_readiness_cat = readiness_cat_all[readiness_cat_all["Country"] != "Overall"].groupby("Category").agg({
        "ready": "sum",
        "total": "sum"
    }).reset_index()
    overall_readiness_cat["Country"] = "Overall"
    
    readiness_cat_all = readiness_cat_all[readiness_cat_all["Country"] != "Overall"]
    readiness_cat_all = pd.concat([readiness_cat_all, overall_readiness_cat])
    readiness_cat_all = readiness_cat_all.rename(columns={"Country": "country", "Category": "category"})
    
    return impact_dat_all, readiness_cat_all

def _process_implementation(df: pd.DataFrame) -> pd.DataFrame:
    """Classifies implementation status."""
    def map_stage(stage):
        s = str(stage).lower()
        if "phase 1" in s or "phase 2" in s or "phase i" in s or "phase ii" in s:
            return "planned"
        elif "phase 3" in s or "phase iii" in s:
            return "in_progress"
        else:
            return "completed"
            
    df["impl_status"] = df["Stage"].apply(map_stage)
    implementation_data = df.groupby(["Category", "impl_status"]).size().unstack(fill_value=0).reset_index()
    for col in ["planned", "in_progress", "completed"]:
        if col not in implementation_data.columns:
            implementation_data[col] = 0
    return implementation_data.rename(columns={"Category": "category"})

def _process_country_readiness(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregates country readiness metrics."""
    country_readiness_data = df.groupby("Country").agg({
        "Policy readiness": "mean",
        "Potential supply chain": "mean",
        "Uptake/Delivery": "mean"
    }).reset_index()
    country_readiness_data.columns = ["country", "policy_readiness", "infra_readiness", "uptake_potential"]
    
    overall_cr = country_readiness_data.mean(numeric_only=True).to_frame().T
    overall_cr["country"] = "Overall"
    return pd.concat([country_readiness_data, overall_cr])

def load_data() -> dict:
    """
    Main function to load and process all dashboard data.
    Returns a dictionary of DataFrames and other data structures.
    """
    df = _load_csv(DATA_PATH)
    df = _preprocess_data(df)
    
    pipeline = _process_pipeline(df)
    readiness = _process_readiness(df)
    impact_dat_all, readiness_cat_all = _process_impact_and_readiness(df)
    usage_all = _process_usage(df)
    risk_data = _process_risks(df)
    implementation_data = _process_implementation(df)
    country_readiness_data = _process_country_readiness(df)
    impact_template, intro_template, id_offsets = _generate_templates_and_offsets(df)
    
    # Simple aggregations
    ce_all = df[["id", "Country", "Cost-effectiveness"]].copy()
    ce_all = ce_all.rename(columns={"Country": "country", "Cost-effectiveness": "ce_usd_per_daly"})
    ce_all["ce_usd_per_daly"] = pd.to_numeric(ce_all["ce_usd_per_daly"], errors='coerce').fillna(0)

    pop_impact_all = df[["id"]].copy()
    pop_impact_all["pop_millions"] = df["Impact Potential"].apply(lambda x: (pd.to_numeric(x, errors='coerce') or 0) * 0.8 + 5)

    df["Budget Impact"] = pd.to_numeric(df["Budget Impact"], errors='coerce').fillna(0)
    budget_data = df.groupby("Category")["Budget Impact"].sum().reset_index()
    budget_data.columns = ["category", "allocated"]
    budget_data["spent"] = budget_data["allocated"] * 0.8

    return {
        "pipeline": pipeline,
        "readiness": readiness,
        "horizon": df,
        "impact_dat_all": impact_dat_all,
        "readiness_cat_all": readiness_cat_all,
        "usage_all": usage_all,
        "ce_all": ce_all,
        "pop_impact_all": pop_impact_all,
        "budget_data": budget_data,
        "implementation_data": implementation_data,
        "risk_data": risk_data,
        "country_readiness_data": country_readiness_data,
        "impact_template": impact_template,
        "intro_template": intro_template,
        "id_offsets": id_offsets,
    }
