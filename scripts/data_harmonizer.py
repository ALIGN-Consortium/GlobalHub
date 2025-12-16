import pandas as pd
import numpy as np
import random

def harmonize_data(df, disease_name="Malaria"):
    """
    Harmonizes innovation data from a raw dataframe.
    
    Args:
        df (pd.DataFrame): The raw input dataframe containing innovation data.
        disease_name (str): The name of the disease to filter or label the data with.
        
    Returns:
        dict: A dictionary containing processed dataframes (pipeline, readiness, horizon, etc.)
              ready for use in the dashboard.
    """
    
    # --- Preprocessing & ID Generation ---
    # Sort to ensure deterministic ID assignment
    if "Innovation" in df.columns and "Country" in df.columns:
        df = df.sort_values(by=["Innovation", "Country"]).reset_index(drop=True)
    
    # Generate IDs like INV-001, INV-002...
    df["raw_id"] = [f"INV-{i:03d}" for i in range(1, len(df) + 1)]
    
    # Create composite Innovation ID for display and uniqueness
    # Handle cases where Innovation name might be missing
    if "Innovation" not in df.columns:
        df["Innovation"] = "Unknown Innovation"
        
    df["Innovation"] = df["Innovation"].fillna("Unknown") + " (" + df["raw_id"] + ")"
    df["id"] = df["Innovation"] # Use composite ID as the main ID

    # --- Column Mapping & Cleaning ---
    # Standardize basic column names if they exist
    # This mapping is specific to the "Horizon" dataset structure but can be expanded
    column_mapping = {
        "time_to_regulatory_approval": "Time_to_Approval",
        "time_to_market": "Time_to_Market",
        "Impact Score": "Impact Score",
        "Cost-effectiveness": "Cost-effectiveness",
        "Readiness": "Readiness",
        "Stage": "Stage",
        "Category": "Category",
        "Country": "Country",
        "LeadOrg": "LeadOrg",
        "Disease": "Disease",
        "TargetPop": "TargetPop",
        "Impact Potential": "Impact Potential",
        "Introduction Readiness": "Introduction Readiness"
    }
    
    # Apply renaming only for columns that exist
    rename_dict = {k: v for k, v in column_mapping.items() if k in df.columns}
    df = df.rename(columns=rename_dict)

    # Ensure date column is datetime
    if "expected_date_of_market" in df.columns:
        df["expected_date_of_market"] = pd.to_datetime(df["expected_date_of_market"], errors="coerce")
        df["market_year"] = df["expected_date_of_market"].dt.year
    else:
        df["market_year"] = 2025 # Default if missing

    # Map Categories if needed (Standardize case/strip)
    if "Category" in df.columns:
        df["Category"] = df["Category"].str.strip()
    else:
        df["Category"] = "Uncategorized"
    
    # Filter for Forecast period (2025 and above)
    # Only if market_year exists and has valid data
    if "market_year" in df.columns:
        df = df[df["market_year"] >= 2025]
    
    # --- 1. Pipeline Data (Dynamic) ---
    # Aggregate counts by Year and Category
    if "market_year" in df.columns and "Category" in df.columns:
        pipeline_raw = df.groupby(["market_year", "Category"]).size().unstack(fill_value=0)
        
        # Ensure we have a reasonable year range
        min_year = 2025
        max_year = int(pipeline_raw.index.max()) if not pipeline_raw.empty and not pd.isna(pipeline_raw.index.max()) else 2035
        all_years = range(min_year, max_year + 1)
        
        # Handle float index if NaNs existed in original column
        if not pipeline_raw.empty:
            pipeline_raw.index = pipeline_raw.index.astype(int)

        # Reindex to ensure continuous years and cumulative sum
        pipeline_reindexed = pipeline_raw.reindex(all_years, fill_value=0)
        pipeline = pipeline_reindexed.cumsum().reset_index()
        
        pipeline = pipeline.rename(columns={"index": "year", "market_year": "year"})
        
        # Convert all columns to numeric except year
        for col in pipeline.columns:
            if col != "year":
                pipeline[col] = pipeline[col].astype(int)
    else:
        pipeline = pd.DataFrame({"year": range(2025, 2036)})

    # --- 2. Readiness Data (Dynamic) ---
    if "Stage" in df.columns:
        stage_counts = df["Stage"].value_counts().reset_index()
        stage_counts.columns = ["status", "count"]
        total_innovations = len(df)
        stage_counts["pct"] = (stage_counts["count"] / total_innovations * 100).round(1)
        
        # Assign colors dynamically
        base_colors = ["#10b981", "#3b82f6", "#f59e0b", "#ef4444", "#8b5cf6", "#ec4899"]
        stage_counts["colors"] = [base_colors[i % len(base_colors)] for i in range(len(stage_counts))]
        readiness = stage_counts[["status", "pct", "colors"]]
    else:
        readiness = pd.DataFrame(columns=["status", "pct", "colors"])

    # --- 3. Horizon DataFrame (Main Data) ---
    horizon_df = df.copy()
    
    # Ensure numeric columns are actually numeric
    numeric_cols = ["Impact Score", "Impact Potential", "Introduction Readiness", "Cost-effectiveness", "Readiness", "Time_to_Approval", "Time_to_Market"]
    for col in numeric_cols:
        if col in horizon_df.columns:
            horizon_df[col] = pd.to_numeric(horizon_df[col], errors='coerce').fillna(0)

    # --- 4. Impact Data All ---
    # Group by Country, Category
    if "Country" in df.columns and "Category" in df.columns:
        impact_dat_all = df.groupby(["Country", "Category"]).agg({
            "Impact Score": "mean",
            "Cost-effectiveness": "mean"
        }).reset_index()
        impact_dat_all = impact_dat_all.rename(columns={"Impact Score": "impact", "Cost-effectiveness": "cost_eff"})
        
        # Add Overall
        overall_impact = impact_dat_all.groupby("Category").agg({
            "impact": "mean",
            "cost_eff": "mean"
        }).reset_index()
        overall_impact["Country"] = "Overall"
        impact_dat_all = pd.concat([impact_dat_all, overall_impact])
        impact_dat_all = impact_dat_all.rename(columns={"Country": "country", "Category": "category"})
    else:
        impact_dat_all = pd.DataFrame(columns=["country", "category", "impact", "cost_eff"])

    # --- 5. Readiness Cat All ---
    # Define "Ready" as Stage includes Phase 2/3 or Market/Ready/Stockpiled
    def check_ready(stage):
        s = str(stage).lower()
        keywords = ["phase 2", "phase ii", "phase 3", "phase iii", "market", "ready", "stockpiled"]
        return any(k in s for k in keywords)

    if "Stage" in df.columns:
        df["is_ready"] = df["Stage"].apply(check_ready)
        
        readiness_cat_all = df.groupby(["Country", "Category"]).agg(
            ready=("is_ready", "sum"),
            total=("id", "count")
        ).reset_index()
        
        overall_readiness_cat = readiness_cat_all.groupby("Category").agg({
            "ready": "sum",
            "total": "sum"
        }).reset_index()
        overall_readiness_cat["Country"] = "Overall"
        readiness_cat_all = pd.concat([readiness_cat_all, overall_readiness_cat])
        readiness_cat_all = readiness_cat_all.rename(columns={"Country": "country", "Category": "category"})
    else:
        readiness_cat_all = pd.DataFrame(columns=["country", "category", "ready", "total"])

    # --- 6. Usage All (Map Data) ---
    # Lat/Lon Mapping (Default set)
    country_coords = {
        "Kenya": {"lat": -0.02, "lon": 37.9},
        "Senegal": {"lat": 14.5, "lon": -14.4},
        "South Africa": {"lat": -30.6, "lon": 22.9},
        "Overall": {"lat": 0.0, "lon": 0.0},
        "Brazil": {"lat": -10.8, "lon": -52.9},
        "India": {"lat": 21.0, "lon": 78.0},
        "Nigeria": {"lat": 9.1, "lon": 8.7},
        "Tanzania": {"lat": -6.4, "lon": 35.0},
        "Ghana": {"lat": 7.9, "lon": -1.0}
    }
    
    if "Country" in df.columns:
        usage_all = df[["id", "Country", "Stage"]].copy()
        usage_all = usage_all.rename(columns={"Country": "country", "Stage": "status"})
        usage_all["lat"] = usage_all["country"].map(lambda x: country_coords.get(x, {"lat": 0, "lon": 0})["lat"])
        usage_all["lon"] = usage_all["country"].map(lambda x: country_coords.get(x, {"lat": 0, "lon": 0})["lon"])
    else:
        usage_all = pd.DataFrame(columns=["id", "country", "status", "lat", "lon"])

    # --- 7. CE All ---
    if "Country" in df.columns and "Cost-effectiveness" in df.columns:
        ce_all = df[["id", "Country", "Cost-effectiveness"]].copy()
        ce_all = ce_all.rename(columns={"Country": "country", "Cost-effectiveness": "ce_usd_per_daly"})
        ce_all["ce_usd_per_daly"] = pd.to_numeric(ce_all["ce_usd_per_daly"], errors='coerce').fillna(0)
    else:
        ce_all = pd.DataFrame(columns=["id", "country", "ce_usd_per_daly"])

    # --- 8. Pop Impact All ---
    pop_impact_all = df[["id"]].copy()
    if "Impact Potential" in df.columns:
        # Simulate population impact based on Impact Potential * 1M (random variation)
        pop_impact_all["pop_millions"] = df["Impact Potential"].apply(lambda x: (pd.to_numeric(x, errors='coerce') or 0) * 0.8 + 5)
    else:
        pop_impact_all["pop_millions"] = 0

    # --- 9. Budget Data ---
    if "Budget Impact" in df.columns:
        df["Budget Impact"] = pd.to_numeric(df["Budget Impact"], errors='coerce').fillna(0)
        budget_data = df.groupby("Category")["Budget Impact"].sum().reset_index()
        budget_data.columns = ["category", "allocated"]
        budget_data["spent"] = budget_data["allocated"] * 0.8 # Simulate spent
    else:
        budget_data = pd.DataFrame(columns=["category", "allocated", "spent"])

    # --- 10. Implementation Data ---
    # Map Stage to Status
    def map_stage(stage):
        s = str(stage).lower()
        if "phase 1" in s or "phase 2" in s or "phase i" in s or "phase ii" in s:
            return "planned"
        elif "phase 3" in s or "phase iii" in s:
            return "in_progress"
        else:
            return "completed"
            
    if "Stage" in df.columns:
        df["impl_status"] = df["Stage"].apply(map_stage)
        implementation_data = df.groupby(["Category", "impl_status"]).size().unstack(fill_value=0).reset_index()
        for col in ["planned", "in_progress", "completed"]:
            if col not in implementation_data.columns:
                implementation_data[col] = 0
        implementation_data = implementation_data.rename(columns={"Category": "category"})
    else:
        implementation_data = pd.DataFrame(columns=["category", "planned", "in_progress", "completed"])

    # --- 11. Risk Data ---
    # Inverse of success probabilities
    risk_cols = {
        "Probability of technical and regulatory success": "technical_risk",
        "Demand forecasting and generation": "market_risk",
        "Regulatory approvals": "regulatory_risk",
        "Financing": "financial_risk"
    }
    
    risk_data_list = []
    if "Category" in df.columns:
        for cat, group in df.groupby("Category"):
            cat_risks = {"category": cat}
            for src, target in risk_cols.items():
                if src in group.columns:
                    val = pd.to_numeric(group[src], errors='coerce').mean()
                    cat_risks[target] = max(0, 10 - (val / 10)) # Scale 0-100 down to 0-10 risk score (inverse)
                else:
                    cat_risks[target] = 5 # Default
            risk_data_list.append(cat_risks)
        risk_data = pd.DataFrame(risk_data_list)
    else:
        risk_data = pd.DataFrame(columns=["category", "technical_risk", "market_risk", "regulatory_risk", "financial_risk"])

    # --- 12. Country Readiness Data ---
    if "Country" in df.columns:
        # Check if columns exist before aggregation
        agg_dict = {}
        if "Policy readiness" in df.columns: agg_dict["Policy readiness"] = "mean"
        if "Potential supply chain" in df.columns: agg_dict["Potential supply chain"] = "mean"
        if "Uptake/Delivery" in df.columns: agg_dict["Uptake/Delivery"] = "mean"
        
        if agg_dict:
            country_readiness_data = df.groupby("Country").agg(agg_dict).reset_index()
            # Rename based on what was available
            rename_map = {"Country": "country", "Policy readiness": "policy_readiness", 
                          "Potential supply chain": "infra_readiness", "Uptake/Delivery": "uptake_potential"}
            country_readiness_data = country_readiness_data.rename(columns=rename_map)
            
            # Add Overall
            overall_cr = country_readiness_data.mean(numeric_only=True).to_frame().T
            overall_cr["country"] = "Overall"
            country_readiness_data = pd.concat([country_readiness_data, overall_cr])
        else:
             country_readiness_data = pd.DataFrame(columns=["country", "policy_readiness", "infra_readiness", "uptake_potential"])
    else:
        country_readiness_data = pd.DataFrame(columns=["country", "policy_readiness", "infra_readiness", "uptake_potential"])

    # --- 13. Templates (Static) ---
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

    # --- 14. ID Offsets (Dynamic) ---
    # Generate random offsets for each ID
    id_offsets = {}
    for pid in df["id"].unique():
        # Deterministic random based on ID hash
        random.seed(hash(pid))
        
        id_offsets[pid] = {
            "impact": [random.randint(-20, 20) for _ in range(6)],
            "impact_passed": [random.choice([True, False]) for _ in range(6)],
            "intro_delta": [random.randint(-10, 10) for _ in range(11)],
            "intro_passed_delta": [random.choice([True, False]) for _ in range(11)]
        }

    return {
        "pipeline": pipeline,
        "readiness": readiness,
        "horizon": horizon_df,
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
