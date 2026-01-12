from shiny import ui, reactive
from shiny.express import render
import plotly.graph_objects as go
import pandas as pd
from utils.data_loader import load_data
from shinywidgets import output_widget, render_widget


def req(condition):
    """
    Helper to stop execution if a condition is not met (similar to R Shiny's req).
    Useful for preventing errors when data is momentarily empty during reactivity.
    """
    import pandas as pd

    if isinstance(condition, pd.DataFrame):
        if condition.empty:
            raise StopIteration
    elif not condition:
        raise StopIteration


def overview_ui(id):
    """
    Defines the User Interface for the Overview module.

    Layout:
    1. KPI Cards: Top-level metrics for Tuberculosis, HIV, Malaria, and MNCH.
    2. Market Overview:
       - Trend Chart: Cumulative forecast of products coming to market.
       - Pie Chart: Current development status breakdown.
    3. Average Timeline: Visual timeline of development stages.
    4. Innovation Explorer: Interactive table to browse and select innovations.
    """
    data = load_data()
    horizon_df = data["horizon"]

    # Get unique diseases for the filter dropdown
    diseases = ["Overall"] + sorted(horizon_df["disease"].dropna().unique().tolist())

    # Helper function to create consistent KPI cards
    def kpi_card(value, label, sub, icon):
        return ui.div(
            ui.div(
                ui.h3(value, class_="text-primary mb-1"),
                ui.p(label, class_="mb-1 fw-bold text-dark"),
                ui.tags.small(sub, class_="text-success"),
            ),
            ui.div(
                ui.tags.i(class_=f"fa-solid fa-{icon} fa-2x text-primary opacity-50")
            ),
            class_="d-flex justify-content-between align-items-center p-3",
        )

    # Calculate innovation counts for specific disease categories
    def count_innovations(diseases):
        if isinstance(diseases, str):
            diseases = [diseases]
        # Filter by Disease column
        return len(
            horizon_df[horizon_df["disease"].isin(diseases)]["innovation"].unique()
        )

    tb_count = count_innovations(["Tuberculosis"])
    hiv_count = count_innovations(["HIV"])
    malaria_count = count_innovations(["Malaria"])
    mnch_count = count_innovations(["MNCH"])

    return ui.div(
        # --- Section 1: KPI Cards ---
        ui.div(
            ui.div(
                ui.card(
                    kpi_card(
                        str(tb_count), "Tuberculosis", "Innovations", "lungs-virus"
                    )
                ),
                class_="col-md-3",
            ),
            ui.div(
                ui.card(kpi_card(str(hiv_count), "HIV/AIDS", "Innovations", "ribbon")),
                class_="col-md-3",
            ),
            ui.div(
                ui.card(
                    kpi_card(str(malaria_count), "Malaria", "Innovations", "mosquito")
                ),
                class_="col-md-3",
            ),
            ui.div(
                ui.card(
                    kpi_card(
                        str(mnch_count), "MNCH", "Innovations", "person-breastfeeding"
                    )
                ),
                class_="col-md-3",
            ),
            class_="row mb-4 g-3",
        ),
        # --- Section 2: Market Overview Charts ---
        ui.div(
            ui.div(
                ui.span("Market Overview", class_="fw-semibold"),
                ui.input_select(
                    "disease_selector",
                    None,
                    choices=diseases,
                    selected="Overall",
                    width="220px",
                ),
                class_="d-flex align-items-center justify-content-between flex-wrap gap-2 mb-2",
            ),
            class_="col-12",
        ),
        ui.div(
            ui.div(
                ui.div(
                    ui.div(
                        "Forecast of products coming to market", class_="card-header"
                    ),
                    ui.div(
                        output_widget("trend_chart", height="350px"), class_="card-body"
                    ),
                    class_="card",
                ),
                class_="col-md-7",
            ),
            ui.div(
                ui.div(
                    ui.div("Development Status", class_="card-header"),
                    ui.div(
                        output_widget("pie_chart", height="350px"), class_="card-body"
                    ),
                    class_="card",
                ),
                class_="col-md-5",
            ),
            class_="row g-3",
        ),
        # --- Section 3: Average Timeline ---
        ui.div(
            ui.div(
                ui.div(
                    ui.span(
                        "Average innovation development time", class_="fw-semibold"
                    ),
                    ui.input_select(
                        "timeline_country_selector",
                        None,
                        choices=["Overall", "Kenya", "Senegal", "South Africa"],
                        selected="Overall",
                        width="220px",
                    ),
                    class_="card-header d-flex align-items-center justify-content-between flex-wrap gap-2",
                ),
                ui.div(
                    ui.div(
                        output_widget("avg_timeline_plot", height="300px"),
                        style="width: 100%; display: block;",
                    ),
                    class_="card-body",
                ),
                class_="card col-12",
            ),
            class_="row g-3 mb-4",
        ),
        # --- Section 4: Innovation Explorer Table ---
        ui.div(
            ui.div(
                ui.div(
                    ui.span("Innovation Explorer", class_="fw-semibold"),
                    ui.input_select(
                        "impact_country_table",
                        None,
                        choices=["Overall", "Kenya", "Senegal", "South Africa"],
                        selected="Overall",
                        width="220px",
                    ),
                    class_="d-flex align-items-center justify-content-between flex-wrap gap-2",
                ),
                class_="card-header",
            ),
            ui.div(
                ui.output_data_frame("pipeline_tbl"),
                class_="card-body",
            ),
            class_="card",
            min_height="500px",
        ),
        id=id,
    )


def overview_server(id, input, output, session):
    """
    Server logic for the Overview module.

    Handles:
    - Data loading and filtering based on user inputs (disease, country).
    - Rendering of Plotly charts (trend, pie, timeline).
    - Rendering of the interactive DataGrid.
    - Navigation event when a table row is clicked.
    """
    data = load_data()
    horizon_df = data["horizon"]

    # Reactive value to store the selected innovation ID for cross-module communication
    default_innovation_id = (
        horizon_df["innovation"].iloc[0] if not horizon_df.empty else None
    )
    selected_innovation = reactive.Value(default_innovation_id)

    # --- Layout Fix: Startup Delay ---
    # Delays the initial render of complex charts to allow CSS layout to settle.
    layout_ready = reactive.Value(False)

    @reactive.Effect
    def _():
        # Trigger once on startup after 0.5s
        reactive.invalidate_later(0.5)
        layout_ready.set(True)

    @render_widget
    def trend_chart():
        """
        Renders a cumulative line chart of products coming to market over time.
        Filters by selected disease and aggregates by category.
        """
        disease = input.disease_selector()

        # 1. Filter Data
        if disease == "Overall":
            df_filtered = horizon_df
        else:
            df_filtered = horizon_df[horizon_df["disease"] == disease]

        # Filter for Forecast period (2025-2050)
        df_filtered = df_filtered[
            (df_filtered["market_year"] >= 2025) & (df_filtered["market_year"] <= 2050)
        ]

        if df_filtered.empty:
            return go.FigureWidget()

        # 2. Aggregate Data: Count per Year & Category
        pipeline_raw = (
            df_filtered.groupby(["market_year", "category"])
            .size()
            .unstack(fill_value=0)
        )

        # 3. Ensure Continuous Timeline (fill missing years)
        min_year = 2025
        max_year = (
            int(pipeline_raw.index.max())
            if not pipeline_raw.empty and not pd.isna(pipeline_raw.index.max())
            else 2035
        )
        max_year = min(max_year, 2050)
        all_years = range(min_year, max_year + 1)

        if not pipeline_raw.empty:
            pipeline_raw.index = pipeline_raw.index.astype(int)

        pipeline_reindexed = pipeline_raw.reindex(all_years, fill_value=0)

        # 4. Calculate Cumulative Sums
        pipeline = pipeline_reindexed.cumsum().reset_index()
        pipeline = pipeline.rename(columns={"index": "year", "market_year": "year"})

        df = pipeline.melt(id_vars="year", var_name="category", value_name="count")
        req(not df.empty)

        # 5. Build Plotly Figure
        fig = go.FigureWidget()
        for category in df["category"].unique():
            category_df = df[df["category"] == category]
            fig.add_trace(
                go.Scatter(
                    x=category_df["year"].astype(str),
                    y=category_df["count"],
                    name=category,
                    mode="lines+markers",
                    line=dict(width=3),
                    marker=dict(size=6),
                )
            )
        fig.update_layout(
            hovermode="x unified",
            legend=dict(orientation="h", y=1.02, yanchor="bottom"),
            margin=dict(l=0, r=0, t=0, b=0),
            yaxis_title="Cumulative Number of Products",
            xaxis=dict(showticklabels=True, dtick=1, tickangle=-45, type="category"),
            yaxis=dict(range=[0, None], fixedrange=True),
            annotations=[
                dict(
                    text="Data is cumulative",
                    xref="paper",
                    yref="paper",
                    x=0.02,
                    y=0.95,
                    showarrow=False,
                    font=dict(size=10, color="gray"),
                )
            ],
        )
        return fig

    @render_widget
    def pie_chart():
        """
        Renders a donut chart showing the breakdown of innovations by development status (Stage).
        """
        disease = input.disease_selector()

        if disease == "Overall":
            df_filtered = horizon_df
        else:
            df_filtered = horizon_df[horizon_df["disease"] == disease]

        if df_filtered.empty:
            return go.FigureWidget()

        stage_counts = df_filtered["trial_status"].value_counts().reset_index()
        stage_counts.columns = ["status", "count"]
        total_innovations = len(df_filtered)
        stage_counts["pct"] = (stage_counts["count"] / total_innovations * 100).round(1)

        base_colors = ["#10b981", "#3b82f6", "#f59e0b", "#ef4444", "#8b5cf6", "#ec4899"]
        stage_counts["colors"] = [
            base_colors[i % len(base_colors)] for i in range(len(stage_counts))
        ]
        readiness = stage_counts

        req(not readiness.empty)
        fig = go.FigureWidget(
            data=[
                go.Pie(
                    labels=readiness["status"],
                    values=readiness["pct"],
                    hole=0.4,
                    marker=dict(
                        colors=readiness["colors"], line=dict(color="#FFFFFF", width=2)
                    ),
                    textinfo="label+percent",
                    textposition="outside",
                )
            ]
        )
        fig.update_layout(
            showlegend=True,
            margin=dict(l=0, r=0, t=0, b=0),
        )
        return fig

    @render_widget
    def avg_timeline_plot():
        """
        Renders a static timeline visualization showing average years between key milestones.
        Calculates means for:
        1. Start -> Regulatory Approval
        2. Regulatory Approval -> First Launch
        3. First Launch -> 20% Market Uptake
        """
        # Wait for layout to stabilize (fixes initial width issue)
        req(layout_ready())

        disease = input.disease_selector()
        country = input.timeline_country_selector()

        df_filtered = horizon_df.copy()

        if disease != "Overall":
            df_filtered = df_filtered[df_filtered["disease"] == disease]

        if country != "Overall":
            df_filtered = df_filtered[df_filtered["country"] == country]

        # Ensure numeric columns
        cols = [
            "time_to_regulatory_approval",
            "time_approval_to_first_launch",
            "time_launch_to_20lmic",
        ]
        for c in cols:
            if c in df_filtered.columns:
                df_filtered[c] = pd.to_numeric(df_filtered[c], errors="coerce")

        # Calculate averages
        t1 = (
            df_filtered["time_to_regulatory_approval"].mean()
            if "time_to_regulatory_approval" in df_filtered.columns
            else 0
        )
        t2 = (
            df_filtered["time_approval_to_first_launch"].mean()
            if "time_approval_to_first_launch" in df_filtered.columns
            else 0
        )
        t3 = (
            df_filtered["time_launch_to_20lmic"].mean()
            if "time_launch_to_20lmic" in df_filtered.columns
            else 0
        )

        t1 = 0 if pd.isna(t1) else t1
        t2 = 0 if pd.isna(t2) else t2
        t3 = 0 if pd.isna(t3) else t3

        # Create cumulative timeline points
        x_vals = [0, t1, t1 + t2, t1 + t2 + t3]
        labels = [
            "Start",
            "Regulatory approval",
            "First country launch",
            "20% Market uptake",
        ]
        text_vals = [f"{x:.1f} yrs" for x in x_vals]

        text_positions = ["bottom center", "top center", "bottom center", "top center"]

        fig = go.FigureWidget()

        fig.add_trace(
            go.Scatter(
                x=x_vals,
                y=[0] * len(x_vals),
                mode="lines+markers+text",
                line=dict(color="red", width=3),
                marker=dict(size=14, color="red", line=dict(width=2, color="white")),
                text=[f"<b>{l}</b><br>{v}" for l, v in zip(labels, text_vals)],
                textposition=text_positions,
                hoverinfo="text",
                showlegend=False,
            )
        )

        fig.update_layout(
            height=300,
            margin=dict(l=40, r=40, t=40, b=40),
            xaxis=dict(
                showgrid=False,
                zeroline=False,
                showline=True,
                linecolor="#BFBBBB",
                title="Years from Project Start",
                dtick=1,
            ),
            yaxis=dict(visible=False, range=[-1.5, 1.5], fixedrange=True),
            plot_bgcolor="white",
            paper_bgcolor="white",
        )
        return fig

    @render.data_frame
    def pipeline_tbl():
        """
        Renders the interactive DataGrid table.
        Filters by country and selects key columns for display.
        """
        country = input.impact_country_table()
        if country == "Overall":
            df_filtered = horizon_df
        else:
            df_filtered = horizon_df[horizon_df["country"] == country]
        req(not df_filtered.empty)

        return render.DataGrid(
            df_filtered.assign(
                expected_date_of_market=lambda d: d[
                    "expected_date_of_market"
                ].dt.strftime("%Y-%m-%d")
            ).rename(
                columns={
                    "innovation": "Innovation",
                    "category": "Category",
                    "trial_status": "Status",
                    "expected_date_of_market": "Expected Market Date",
                    "disease": "Disease Area",
                }
            )[
                [
                    "Innovation",
                    "Disease Area",
                    "Category",
                    "Status",
                    "Expected Market Date",
                ]
            ],
            selection_mode="row",
            width="100%",
            filters=True,
        )

    @reactive.Effect
    @reactive.event(input.pipeline_tbl_selected_rows)
    def _():
        """
        Event Handler: Runs when a row is clicked in the pipeline_tbl.
        1. Identifies the selected innovation ID.
        2. Updates the `selected_innovation` reactive value.
        3. Switches the main navigation tab to 'Innovation Details'.
        """
        if not input.pipeline_tbl_selected_rows():
            return
        idx = input.pipeline_tbl_selected_rows()[0]

        country = input.impact_country_table()
        if country == "Overall":
            df_filtered = horizon_df
        else:
            df_filtered = horizon_df[horizon_df["country"] == country]

        selected_id = df_filtered.iloc[idx]["innovation"]
        selected_innovation.set(selected_id)
        ui.update_navset("main_nav", "Innovation Details")

    return selected_innovation
