# Migration Plan: R Shiny to Python Shiny Dashboard

This document outlines the step-by-step plan for migrating the existing R Shiny dashboard to a Python Shiny application. The goal is to reproduce the core sections, interactivity, and reactivity of the original dashboard, adapting as necessary for the Python Shiny framework.

## Phase 0: Cleanup and Setup

1.  **Delete old Python files and directories:** Remove `app.py`, `overview.py`, `innovation_details.py`, `data_loader.py`, `main.py`, `MIGRATION_NOTES.md`, `plan.md`, `__pycache__`, and `.venv`. (Completed)
2.  **Verify `requirements.txt`:** Ensure it contains `shiny`, `pandas`, `plotly`, `pyecharts`, `shinyswatch`.
3.  **Verify `www/styles.css`:** Ensure it contains the custom CSS from the original R application.
4.  **Install dependencies:** Install all packages listed in `requirements.txt`.

## Phase 1: Project Scaffolding and Core Setup

*   **Goal:** Create the basic structure of the Python Shiny application and set up the environment.
*   **Actions:**
    1.  **Create `app.py`:** Define the overall UI layout (`ui.page_navbar`) and integrate the different modules.
    2.  **Create placeholder modules:**
        *   `overview.py`: For the "Overview" page UI and server logic.
        *   `innovation_details.py`: For the "Innovation Details" module UI and server logic.
        *   `data_loader.py`: For loading and preparing all data.
    3.  **Create `main.py`:** To serve as the entry point for running the application.

## Phase 2: Data Loading and Preparation (`data_loader.py`)

*   **Goal:** Translate all R `tibble`/`tribble` objects and CSV loading into pandas DataFrames.
*   **Actions:**
    1.  **Implement `load_data()`:** Create a function that returns a dictionary of pandas DataFrames.
    2.  **Convert `pipeline`:** Translate the R `pipeline` tibble into a pandas DataFrame.
    3.  **Convert `readiness`:** Translate the R `readiness` tibble into a pandas DataFrame.
    4.  **Load `horizon.csv`:** Read `www/horizon.csv` into a pandas DataFrame.
    5.  **Convert `impact_dat_all`:** Translate the R `impact_dat_all` tribble into a pandas DataFrame.
    6.  **Convert `readiness_cat_all`:** Translate the R `readiness_cat_all` tribble into a pandas DataFrame.
    7.  **Convert `usage_all`:** Translate the R `usage_all` tribble into a pandas DataFrame.
    8.  **Convert `ce_all`:** Translate the R `ce_all` tribble into a pandas DataFrame.
    9.  **Convert `pop_impact_all`:** Translate the R `pop_impact_all` tribble into a pandas DataFrame.

## Phase 3: "Overview" Page Migration (`overview.py`)

*   **Goal:** Migrate the main dashboard page, including all charts and the interactive data table.
*   **Actions:**
    1.  **UI (`overview_ui` function):**
        *   Implement the Hero section (title, description, progress card).
        *   Implement KPI cards (Active Innovations, Implementation Ready, Maternal Health Focus, Impact Score).
        *   Implement Overview charts placeholders (`ui.output_plotly` for trend and pie charts).
        *   Implement High-level value boxes (Total Budget Impact, Implementation Readiness, Population Coverage, Risk Level).
        *   Implement Analytics tabs section (`ui.navset_pill`) with chart placeholders (`ui.output_ui` for pyecharts).
        *   Implement Innovation Explorer table placeholder (`ui.output_data_frame`).
    2.  **Server (`overview_server` function):**
        *   Implement `trend_chart` using Plotly.
        *   Implement `pie_chart` using Plotly.
        *   Implement `impact_combo` using pyecharts (rendered to HTML).
        *   Implement `readiness_bar` using pyecharts (rendered to HTML).
        *   Implement `pipeline_tbl` using `render.data_frame` with country filtering.
        *   Implement reactivity for `impact_country` and `impact_country_table` inputs.
        *   Implement `selected_innovation` (a `reactive.Value`) to store the ID of the selected row in `pipeline_tbl`.
        *   Implement `reactive.Effect` to navigate to "Innovation Details" tab on row selection.

## Phase 4: "Innovation Details" Module Migration (`innovation_details.py`)

*   **Goal:** Build a new, comprehensive module in `innovation_details.py` by merging the best of both R files.
*   **Actions:**
    1.  **UI (`innovation_details_ui` function):**
        *   Implement Header card (title + summary).
        *   Implement two-column layout for domain readiness summary and detailed scores.
        *   Implement "Key Indicators" section with `ui.value_box` components.
    2.  **Server (`innovation_details_server` function):**
        *   Define `impact_template`, `intro_template`, and `id_offsets` as pandas DataFrames/dictionaries.
        *   Implement `get_selected_id` reactive to receive the selected innovation ID.
        *   Implement `detail_row` reactive to filter `horizon_df` based on `selected_id`.
        *   Implement `scores_for_id` reactive to calculate scores based on templates and offsets.
        *   Implement `detail_title` and `detail_summary` rendering.
        *   Implement helper functions: `progress_row_with_icon`, `mini_bar`, `indicator_row`, `indicator_list`, `intro_subdomain_section`.
        *   Implement `domain_summary_bars` rendering.
        *   Implement `domain_bars` rendering with tab selection logic.
        *   Implement `rd_score_from_stage`, `delivery_scale_score`, `impl_readiness_avg`, `sel_ce`, `sel_pop` reactive calculations.
        *   Implement `kpi_box` rendering.
        *   Implement `usage_map` using Plotly.
        *   Implement `ce_by_country` using Plotly.

## Phase 5: Integration and Finalization

*   **Goal:** Connect all modules, ensure seamless navigation, and apply final styling.
*   **Actions:**
    1.  **`app.py`:**
        *   Pass `selected_innovation` from `overview_server` to `innovation_details_server`.
        *   Apply custom theme using `ui.Theme().add_defaults().add_rules()`.
    2.  **`overview.py`:**
        *   Implement `ui.nav_select` to switch to "Innovation Details" tab when a row is selected in `pipeline_tbl`.
    3.  **Review:** Conduct a final review to ensure all components are working together as expected and all features from the original application have been successfully migrated and combined.
