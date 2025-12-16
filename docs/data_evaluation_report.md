# Data Dictionary Revision & Dashboard Critical Evaluation Report

**Date:** December 4, 2025
**Project:** Dashboard Template (Python Migration)

## 1. Executive Summary
The `data_dictionary.xlsx` file has been revised to strictly reflect the data structures currently used in the active Python dashboard codebase (`data_loader.py`). A critical evaluation reveals that the application relies heavily on hardcoded data structures that have diverged significantly from the original documentation, leading to maintenance risks.

## 2. Revisions to Data Dictionary
The following actions were taken to ensure `data_dictionary.xlsx` accurately represents the dashboard's data model:

*   **Synchronization**: The dictionary was regenerated using the actual column names and object keys from `data_loader.py`.
*   **Variable Renaming**: Variables were renamed to match the Python DataFrame columns exactly (e.g., `vaccines_count` -> `Vaccines`, `impact` -> `impact_index` mappings were resolved where identifiable, otherwise the exact code name was used).
*   **Form Name Alignment**: "Form Names" in the dictionary now match the Python DataFrame names (e.g., `impact_dat_all` instead of `impact_data`).
*   **Metadata Preservation**: Where possible, existing "Field Labels" and "Field Types" were preserved by mapping old variable names to the new ones. New variables were initialized with inferred types and default labels.

## 3. Critical Evaluation

### 3.1 Data Architecture
*   **Hardcoded Data**: The majority of the application's data (e.g., `pipeline`, `readiness`, `impact_dat_all`) is hardcoded directly into the `data_loader.py` Python script. This makes the application difficult to update without developer intervention and prone to version control conflicts.
    *   *Recommendation*: Move all static data into external files (CSV, JSON, or SQLite) similar to `horizon.csv`.
*   **Data Silos**: The `data_dictionary.xlsx` was previously an "orphan" file, unused by the application. This lack of runtime validation allows code and documentation to drift apart easily.

### 3.2 Naming Conventions & Consistency
*   **Inconsistent Naming**: The codebase uses a mix of naming conventions for dataframe columns:
    *   **Title Case**: `Vaccines`, `Drugs` (in `pipeline`)
    *   **Spaces**: `Impact Score`, `Time_to_Approval` (in `horizon`)
    *   **Snake Case**: `cost_eff`, `policy_readiness`
*   **Impact**: This inconsistency requires developers to constantly check the schema to know if they need `df['Impact Score']` or `df['impact_score']`, increasing cognitive load and bug probability.

### 3.3 Data Model Integrity
*   **Missing Identifiers**: Several datasets (e.g., `budget_data`, `risk_data`) lack clear join keys (like `country_id` or `innovation_id`) if they are meant to be relational, though they seem to be aggregated summaries.
*   **Implicit Relationships**: The relationship between `horizon_df` (the master list) and the "details" templates (`impact_template`, `intro_template`) is managed via complex dictionaries (`id_offsets`) rather than a standard relational model. This makes adding new metrics or innovations complex.

## 4. Recommendations
1.  **Externalize Data**: Refactor `data_loader.py` to load all data from the `data/` or `www/` directory.
2.  **Standardize Naming**: Adopt `snake_case` for all internal DataFrame column names. Rename `Vaccines` to `vaccines`, `Impact Score` to `impact_score` during the loading phase.
3.  **Active Data Dictionary**: Implement a test or build step that validates the loaded data against `data_dictionary.xlsx` to prevent future regression.
