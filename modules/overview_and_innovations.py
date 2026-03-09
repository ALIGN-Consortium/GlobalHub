# modules/innovation_page.py
#
# Innovation Page (single page) = Overview + Innovation Details
# - ONE pipeline / innovation explorer table (DataGrid)
# - Selecting a row updates ALL detail boxes, charts, and summaries below
# - Keeps ALL existing commented code blocks (for future implementation)
# - Preserves ALL popovers (no removals)
# - Does NOT change themes (theme is set in app.py; this module only uses existing classes)
#
# Usage in app.py:
#   from modules.innovation_page import innovation_page_ui, innovation_page_server
#   ...
#   nav_panel("Innovation Page", innovation_page_ui("innovation_page"))
#   ...
#   innovation_page_server("innovation_page")
#
# If you keep the old Overview + Innovation Details tabs at the same time,
# you should namespace their inputs/outputs too; otherwise you can remove them.

from shiny import ui, reactive, module
from shiny.express import render
from shiny.render import DataGrid
from shiny.ui import popover
import plotly.graph_objects as go
import pandas as pd
from shinywidgets import output_widget, render_widget
from utils.data_loader import load_data


def req(condition):
    """
    Helper to stop execution if a condition is not met (similar to R Shiny's req).
    Useful for preventing errors when data is momentarily empty during reactivity.
    """
    import pandas as pd

    if isinstance(condition, (pd.DataFrame, pd.Series)):
        if condition.empty:
            raise StopIteration
    elif not condition:
        raise StopIteration


def progress_row(label, value):
    """
    Helper to create a labelled progress bar component.
    """
    try:
        if pd.isna(value):
            int_val = 0
        else:
            int_val = int(value)
    except (ValueError, TypeError):
        int_val = 0

    return ui.div(
        ui.div(
            ui.span(label, class_="lbl"),
            ui.span(f"{int_val}%"),
            class_="d-flex justify-content-between",
        ),
        ui.div(
            ui.div(
                class_="progress-bar",
                role="progressbar",
                style=f"width: {int_val}%",
                aria_valuenow=str(int_val),
                aria_valuemin="0",
                aria_valuemax="100",
            ),
            class_="progress",
        ),
        class_="readiness-row",
    )


@module.ui
def innovation_page_ui():
    """
    UI for a single combined page:
      - Hero + KPIs
      - Market overview (trend + donut)
      - Product explorer table (single DataGrid)
      - Detail section (title/summary + readiness + timeline)
      - Impact potential
      - Introduction readiness (Financing + Uptake/Delivery + Policy)
    """
    return ui.div(
        ui.div(
            # =====================================================
            # HERO HEADER
            # =====================================================
            ui.div(
                ui.h1("ALIGN GlobalHub", class_="fw-bold display-5 mb-1"),
                ui.p(
                    "Market Intelligence Hub for Global Health Innovation",
                    class_="lead text-muted mb-3",
                ),
                ui.hr(class_="mb-4"),
            ),
            # =====================================================
            # KPI CARDS
            # =====================================================
            ui.div(
                ui.div(ui.output_ui("kpi_tb"), class_="col-md-3"),
                ui.div(ui.output_ui("kpi_hiv"), class_="col-md-3"),
                ui.div(ui.output_ui("kpi_malaria"), class_="col-md-3"),
                ui.div(ui.output_ui("kpi_mnch"), class_="col-md-3"),
                class_="row mb-4 g-3",
            ),
            # =====================================================
            # MARKET OVERVIEW
            # =====================================================
            ui.div(
                ui.div(
                    ui.div(
                        ui.span("Market overview", class_="fw-semibold"),
                        ui.input_select(
                            "disease_selector",
                            None,
                            choices=[
                                "Overall"
                            ],  # filled by server via ui.update_select
                            selected="Overall",
                            width="220px",
                        ),
                        class_="card-header d-flex align-items-center justify-content-between flex-wrap gap-2",
                    ),
                    ui.div(
                        ui.div(
                            ui.div(
                                ui.div(
                                    ui.div(
                                        ui.tags.span(
                                            "Products cmoing to market in the next 3 years"
                                        ),
                                        # ui.tags.span(
                                        #     "Forecast of products coming to market"
                                        # ),
                                        ui.tags.span(
                                            popover(
                                                ui.tags.i(
                                                    class_="fa-solid fa-circle-info text-muted",
                                                    style="cursor:pointer;",
                                                ),
                                                ui.div(
                                                    ui.p(
                                                        "Projected date of first country-level launch, calculated from expected market approval date based on the method by Mao, Wenhui et al. Development, launch, and scale-up of health products in low-income and middle-income countries: a retrospective analysis on 59 health products. The Lancet Global Health, Volume 13, Issue 6, e1132 - e1139"
                                                    ),
                                                    ui.tags.a(
                                                        "Learn more",
                                                        href="https://www.thelancet.com/journals/langlo/article/PIIS2214-109X(25)00062-2/fulltext",
                                                        target="_blank",
                                                        class_="fw-semibold",
                                                    ),
                                                ),
                                                title="Methodology",
                                            ),
                                            class_="ms-2",
                                        ),
                                        class_="d-flex align-items-center gap-1",
                                    ),
                                    class_="card-header d-flex align-items-center",
                                ),
                                # ui.div(
                                #     output_widget("trend_chart", height="360px"),
                                #     class_="card-body",
                                # ),
                                class_="card",
                            ),
                            class_="col-md-7",
                        ),
                        ui.div(
                            ui.div(
                                ui.div("Development status", class_="card-header"),
                                ui.div(
                                    output_widget("pie_chart", height="360px"),
                                    class_="card-body",
                                ),
                                class_="card",
                            ),
                            class_="col-md-5",
                        ),
                        class_="row g-3",
                    ),
                    class_="card mb-4",
                ),
                class_="col-12",
            ),
            # =====================================================
            # AVERAGE TIMELINE (kept commented as in your original)
            # =====================================================
            # ui.div(
            #     ui.div(
            #         ui.div(
            #             ui.span("Average innovation development time", class_="fw-semibold"),
            #             ui.input_select(
            #                 "timeline_scope_selector",
            #                 None,
            #                 choices=["Overall", "Kenya", "Senegal", "South Africa"],
            #                 selected="Overall",
            #                 width="220px",
            #             ),
            #             class_="card-header d-flex align-items-center justify-content-between flex-wrap gap-2",
            #         ),
            #         ui.div(
            #             ui.div(
            #                 output_widget("avg_timeline_plot", height="300px"),
            #                 style="width: 100%; display: block;",
            #             ),
            #             class_="card-body",
            #         ),
            #         class_="card col-12",
            #     ),
            #     class_="row g-3 mb-4",
            # ),
            # =====================================================
            # PRODUCT EXPLORER (single table)
            # =====================================================
            ui.div(
                ui.div(
                    ui.div(
                        ui.span("Product explorer", class_="fw-semibold"),
                        ui.input_action_button(
                            "clear_filters",
                            ui.tags.span(
                                ui.tags.i(class_="fa-solid fa-rotate-left me-1"),
                                "Clear filters",
                            ),
                            class_="btn btn-sm btn-outline-secondary",
                        ),
                        class_="d-flex justify-content-between align-items-center w-100",
                    ),
                    class_="card-header",
                ),
                ui.div(
                    ui.output_data_frame("pipeline_tbl"),
                    class_="card-body p-0",
                ),
                class_="card mb-4",
                min_height="500px",
            ),
            # =====================================================
            # DETAIL TITLE & SUMMARY
            # =====================================================
            ui.div(
                ui.div(ui.output_text("detail_title"), class_="card-header"),
                ui.div(ui.output_ui("detail_summary"), class_="card-body"),
                class_="card mb-4",
                min_height="400px",
            ),
            # =====================================================
            # DETAIL: readiness + timeline
            # =====================================================
            ui.div(
                # Left column
                ui.div(
                    ui.div(
                        ui.div(
                            ui.div(
                                ui.tags.span("Overall product readiness"),
                                ui.tags.span(
                                    popover(
                                        ui.tags.i(
                                            class_="fa-solid fa-circle-info text-muted",
                                            style="cursor:pointer;",
                                        ),
                                        ui.div(
                                            ui.p(ui.p("Impact potential: coming soon")),
                                            ui.p("Introduction readiness: coming soon"),
                                            ui.tags.a(
                                                "Learn more",
                                                href="https://www.thelancet.com/journals/langlo/article/PIIS2214-109X(25)00062-2/fulltext",
                                                target="_blank",
                                                class_="fw-semibold",
                                            ),
                                        ),
                                        title="Methodology",
                                    ),
                                    class_="ms-2",
                                ),
                                class_="d-flex align-items-center gap-1",
                            ),
                            class_="card-header",
                        ),
                        ui.div(ui.output_ui("domain_summary_bars"), class_="card-body"),
                        class_="card h-100",
                    ),
                    class_="col-12 col-lg-4",
                ),
                # Right column
                ui.div(
                    ui.div(
                        ui.div(
                            ui.div(
                                ui.tags.span("Forecast of products coming to market"),
                                ui.tags.span(
                                    popover(
                                        ui.tags.i(
                                            class_="fa-solid fa-circle-info text-muted",
                                            style="cursor:pointer;",
                                        ),
                                        ui.div(
                                            ui.p(
                                                "Timeline of product development. ",
                                                ui.p(
                                                    "Calculated based on the method by: ",
                                                    ui.tags.em(
                                                        "Mao, Wenhui et al. Development, launch, and scale-up of health products in low-income and middle-income countries: a retrospective analysis on 59 health products. The Lancet Global Health, Volume 13, Issue 6, e1132 - e1139"
                                                    ),
                                                ),
                                            ),
                                            ui.tags.a(
                                                "Learn more",
                                                href="https://www.thelancet.com/journals/langlo/article/PIIS2214-109X(25)00062-2/fulltext",
                                                target="_blank",
                                                class_="fw-semibold",
                                            ),
                                        ),
                                        title="Methodology",
                                    ),
                                    class_="ms-2",
                                ),
                                class_="d-flex align-items-center gap-1",
                            ),
                            class_="card-header d-flex align-items-center",
                        ),
                        ui.div(
                            output_widget("timeline_plot", height="200px"),
                            class_="card-body d-flex align-items-center justify-content-center",
                        ),
                        class_="card h-100",
                    ),
                    class_="col-12 col-lg-8",
                ),
                # IMPORTANT: class_ goes last (after positional children)
                class_="row g-4 g-3 mb-4",
            ),
            # =====================================================
            # IMPACT POTENTIAL
            # =====================================================
            ui.div(
                ui.div(
                    ui.div(
                        ui.span("Impact potential", class_="fw-semibold"),
                        class_="d-flex align-items-center justify-content-between flex-wrap gap-2",
                    ),
                    class_="card-header",
                ),
                ui.div(
                    ui.div(
                        ui.div(
                            ui.output_ui("impact_potential_box", class_="row g-3 mt-1"),
                            class_="card-body",
                        ),
                        class_="card bg-light border-0",
                    ),
                ),
                class_="card mb-4",
                min_height="600px",
            ),
            # =====================================================
            # INTRODUCTION READINESS
            # =====================================================
            ui.div(
                ui.div(
                    ui.div(
                        ui.span("Introduction readiness", class_="fw-semibold"),
                        class_="d-flex align-items-center justify-content-between flex-wrap gap-2",
                    ),
                    class_="card-header",
                ),
                ui.div(
                    ui.div(
                        ui.div(
                            ui.div(
                                ui.span("Financing", class_="fw-semibold card-header"),
                                ui.div(
                                    ui.output_ui(
                                        "financing_box", class_="row g-3 mt-1"
                                    ),
                                    class_="card-body",
                                ),
                                class_="card h-100 bg-light border-0",
                            ),
                            class_="col-md-6",
                        ),
                        ui.div(
                            ui.div(
                                ui.span(
                                    "Uptake/Delivery", class_="fw-semibold card-header"
                                ),
                                ui.div(
                                    ui.output_ui(
                                        "uptake_delivery_box", class_="row g-3 mt-1"
                                    ),
                                    class_="card-body",
                                ),
                                class_="card h-100 bg-light border-0",
                            ),
                            class_="col-md-6",
                        ),
                        class_="row g-3",
                    ),
                    ui.div(
                        ui.div(
                            ui.span("Policy", class_="fw-semibold card-header"),
                            ui.div(
                                ui.output_ui("policy_box", class_="row g-3 mt-1"),
                                class_="card-body",
                            ),
                            class_="card bg-light border-0",
                        ),
                        class_="mt-3",
                    ),
                    class_="card-body",
                ),
                class_="card",
                min_height="600px",
            ),
            class_="container-fluid px-3 py-3",
        )
    )


@module.server
def innovation_page_server(input, output, session):
    """
    Server for combined Innovation Page.
    - Single DataGrid controls the selected_innovation reactive value
    - All detail outputs use selected_innovation
    """
    clear_trigger = reactive.Value(0)
    layout_ready = reactive.Value(False)

    data = load_data()
    horizon_df = data["horizon"]
    innovation_df = data["innovation_df"]

    # ---------------------------------------------------------
    # Populate disease dropdown choices (from horizon)
    # ---------------------------------------------------------
    diseases = ["Overall"] + sorted(horizon_df["disease"].dropna().unique().tolist())

    @reactive.Effect
    def _update_disease_choices():
        ui.update_select(
            "disease_selector",
            choices=diseases,
            selected="Overall",
        )

    # ---------------------------------------------------------
    # KPI helper
    # ---------------------------------------------------------
    def kpi_card(value, label, sub, icon):
        return ui.div(
            ui.div(
                ui.h3(value, class_="text-primary mb-1"),
                ui.p(label, class_="mb-1 fw-bold text-dark"),
                ui.tags.small(sub, class_="text-success"),
            ),
            ui.div(ui.tags.i(class_=f"fa-solid fa-{icon} fa-2x text-primary opacity-50")),
            class_="d-flex justify-content-between align-items-center p-3",
        )

    def count_innovations(diseases_list):
        if isinstance(diseases_list, str):
            diseases_list = [diseases_list]
        return len(horizon_df[horizon_df["disease"].isin(diseases_list)]["innovation"].unique())

    @render.ui
    def kpi_tb():
        return ui.card(kpi_card(str(count_innovations(["Tuberculosis"])), "Tuberculosis", "Products", "lungs-virus"))

    @render.ui
    def kpi_hiv():
        return ui.card(kpi_card(str(count_innovations(["HIV"])), "HIV/AIDS", "Products", "ribbon"))

    @render.ui
    def kpi_malaria():
        return ui.card(kpi_card(str(count_innovations(["Malaria"])), "Malaria", "Products", "mosquito"))

    @render.ui
    def kpi_mnch():
        return ui.card(kpi_card(str(count_innovations(["MNCH"])), "MNCH", "Products", "person-breastfeeding"))

    # ---------------------------------------------------------
    # Data filtering used by the single table + selection mapping
    # IMPORTANT: keep consistent everywhere.
    # ---------------------------------------------------------
    def filtered_innovation_df_for_table(df: pd.DataFrame) -> pd.DataFrame:
        out = df.copy()

        # Does not show Trial Phase 1
        out = out[out["trial_status"] != "Phase 1"]

        # Removes empty time stamps or time stamps way too in the past
        out = out[
            out["proj_date_lmic_20_uptake"].notna()
            & (out["proj_date_lmic_20_uptake"] >= pd.Timestamp("2025-01-01"))
        ]

        return out

    df0 = filtered_innovation_df_for_table(innovation_df)
    default_innovation_id = df0["innovation"].iloc[0] if not df0.empty else None
    selected_innovation = reactive.Value(default_innovation_id)

    # ---------------------------------------------------------
    # Layout settle delay
    # ---------------------------------------------------------
    @reactive.Effect
    def _layout_delay():
        reactive.invalidate_later(0.5)
        layout_ready.set(True)

    # ---------------------------------------------------------
    # Trend chart
    # ---------------------------------------------------------
    @render_widget
    def trend_chart():
        disease = input.disease_selector()

        # Use only unique innovations (scope="WHO") for global counts
        df_unique = horizon_df[horizon_df["scope"] == "WHO"]

        if disease == "Overall":
            df_f = df_unique
        else:
            df_f = df_unique[df_unique["disease"] == disease]

        df_f = df_f[(df_f["market_year"] >= 2025) & (df_f["market_year"] <= 2050)]

        if df_f.empty:
            return go.FigureWidget()

        pipeline_raw = df_f.groupby(["market_year", "category"]).size().unstack(fill_value=0)

        min_year = 2025
        max_year = int(pipeline_raw.index.max()) if not pipeline_raw.empty and not pd.isna(pipeline_raw.index.max()) else 2035
        max_year = min(max_year, 2050)
        all_years = range(min_year, max_year + 1)

        if not pipeline_raw.empty:
            pipeline_raw.index = pipeline_raw.index.astype(int)

        pipeline_reindexed = pipeline_raw.reindex(all_years, fill_value=0)
        pipeline = pipeline_reindexed.cumsum().reset_index()
        pipeline = pipeline.rename(columns={"index": "year", "market_year": "year"})
        dfm = pipeline.melt(id_vars="year", var_name="category", value_name="count")
        req(not dfm.empty)

        fig = go.FigureWidget()
        for category in dfm["category"].unique():
            category_df = dfm[dfm["category"] == category]
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
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
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

    # ---------------------------------------------------------
    # Pie (donut) chart
    # ---------------------------------------------------------
    @render_widget
    def pie_chart():
        df_unique = horizon_df[horizon_df["scope"] == "WHO"][
            horizon_df["trial_status"] != "Phase 1"
        ]

        stage_counts = df_unique["trial_status"].value_counts().reset_index()
        stage_counts.columns = ["status", "count"]
        total_innovations = len(df_unique)
        stage_counts["pct"] = (stage_counts["count"] / total_innovations * 100).round(1)

        categories = [
            "Preclinical",
            "Phase 1",
            "Phase 2",
            "Phase 3",
            "Phase 4",
            "Observational",
            "Implementation/Pilot",
            "Approved / Marketed",
            "Unknown",
        ]

        base_colors = [
            "#94a3b8",
            "#60a5fa",
            "#3b82f6",
            "#2563eb",
            "#1d4ed8",
            "#a78bfa",
            "#10b981",
            "#f43f5e",
            "#cbd5e1",
        ]
        color_map = dict(zip(categories, base_colors))

        stage_counts["colors"] = stage_counts["status"].map(color_map).fillna("#cbd5e1")
        readiness = stage_counts
        req(not readiness.empty)

        fig = go.FigureWidget(
            data=[
                go.Pie(
                    labels=readiness["status"],
                    values=readiness["pct"],
                    hole=0.4,
                    marker=dict(colors=readiness["colors"], line=dict(color="#FFFFFF", width=2)),
                    textinfo="label+percent",
                    textposition="outside",
                )
            ]
        )
        fig.update_layout(showlegend=True, margin=dict(l=0, r=0, t=0, b=0))
        return fig

    # ---------------------------------------------------------
    # Average Timeline (kept here for future; UI is commented)
    # ---------------------------------------------------------
    # @render_widget
    # def avg_timeline_plot():
    #     req(layout_ready())
    #     disease = input.disease_selector()
    #     scope = input.timeline_scope_selector()
    #
    #     df_f = horizon_df.copy()
    #     if disease != "Overall":
    #         df_f = df_f[df_f["disease"] == disease]
    #     if scope != "Overall":
    #         df_f = df_f[df_f["scope"] == scope]
    #
    #     date_cols = [
    #         "date_proof_of_concept",
    #         "date_first_regulatory",
    #         "date_first_launch",
    #         "proj_date_lmic_20_uptake",
    #     ]
    #     for c in date_cols:
    #         if c in df_f.columns:
    #             df_f[c] = pd.to_datetime(df_f[c], errors="coerce")
    #
    #     df_f["t1"] = (df_f["date_first_regulatory"] - df_f["date_proof_of_concept"]).dt.days / 365.25
    #     df_f["t2"] = (df_f["date_first_launch"] - df_f["date_first_regulatory"]).dt.days / 365.25
    #     df_f["t3"] = (df_f["proj_date_lmic_20_uptake"] - df_f["date_first_launch"]).dt.days / 365.25
    #
    #     t1 = df_f["t1"].dropna().mean()
    #     t2 = df_f["t2"].dropna().mean()
    #     t3 = df_f["t3"].dropna().mean()
    #
    #     t1 = 0 if pd.isna(t1) else t1
    #     t2 = 0 if pd.isna(t2) else t2
    #     t3 = 0 if pd.isna(t3) else t3
    #
    #     x_vals = [0, t1, t1 + t2, t1 + t2 + t3]
    #     labels = ["Start", "Regulatory approval", "First country launch", "20% Market uptake"]
    #     text_vals = [f"{x:.1f} yrs" for x in x_vals]
    #     text_positions = ["bottom center", "top center", "bottom center", "top center"]
    #
    #     fig = go.FigureWidget()
    #     fig.add_trace(
    #         go.Scatter(
    #             x=x_vals,
    #             y=[0] * len(x_vals),
    #             mode="lines+markers+text",
    #             line=dict(color="red", width=3),
    #             marker=dict(size=14, color="red", line=dict(width=2, color="white")),
    #             text=[f"<b>{l}</b><br>{v}" for l, v in zip(labels, text_vals)],
    #             textposition=text_positions,
    #             hoverinfo="text",
    #             showlegend=False,
    #         )
    #     )
    #     fig.update_layout(
    #         height=300,
    #         margin=dict(l=40, r=40, t=40, b=40),
    #         xaxis=dict(
    #             showgrid=False,
    #             zeroline=False,
    #             showline=True,
    #             linecolor="#BFBBBB",
    #             title="Years from Project Start",
    #             dtick=1,
    #         ),
    #         yaxis=dict(visible=False, range=[-1.5, 1.5], fixedrange=True),
    #         plot_bgcolor="white",
    #         paper_bgcolor="white",
    #     )
    #     return fig

    # ---------------------------------------------------------
    # SINGLE PIPELINE TABLE (DataGrid)
    # ---------------------------------------------------------
    @render.data_frame
    def pipeline_tbl():
        clear_trigger.get()

        df_f = filtered_innovation_df_for_table(innovation_df)
        req(not df_f.empty)

        # NOTE: keep the same column mapping as your existing code
        # You used proj_date_first_launch in the table display, but filtered on proj_date_lmic_20_uptake.
        return render.DataGrid(
            df_f.assign(
                proj_date_first_launch=lambda d: d["proj_date_first_launch"].dt.strftime("%Y-%m-%d")
            ).rename(
                columns={
                    "innovation": "Product",
                    "category": "Category",
                    "trial_status": "Status",
                    "proj_date_first_launch": "Projected date of launch",
                    "disease": "Disease area",
                }
            )[
                [
                    "Product",
                    "Disease area",
                    "Category",
                    "Status",
                    "Projected date of launch",
                ]
            ],
            selection_mode="row",
            width="100%",
            filters=True,
        )

    @reactive.Effect
    @reactive.event(input.pipeline_tbl_selected_rows)
    def _on_row_select():
        if not input.pipeline_tbl_selected_rows():
            return

        idx = input.pipeline_tbl_selected_rows()[0]

        df_f = filtered_innovation_df_for_table(innovation_df)
        req(not df_f.empty)

        # Map the selected row index back into the filtered DF used to render the table
        selected_id = df_f.iloc[idx]["innovation"]
        selected_innovation.set(selected_id)

    @reactive.Effect
    @reactive.event(input.clear_filters)
    def _clear_filters():
        clear_trigger.set(clear_trigger.get() + 1)

    # ---------------------------------------------------------
    # Selected row helpers
    # ---------------------------------------------------------
    @reactive.Calc
    def get_selected_id():
        return selected_innovation()

    @reactive.Calc
    def detail_row():
        selected_id = get_selected_id()
        req(selected_id)
        row = innovation_df[innovation_df["innovation"] == selected_id]
        req(not row.empty)
        return row.iloc[0]

    # ---------------------------------------------------------
    # Detail title + summary
    # ---------------------------------------------------------
    @render.text
    def detail_title():
        row = detail_row()
        return f"{row['innovation']} ({row['category']})"

    @render.ui
    def detail_summary():
        row = detail_row()
        return ui.div(
            ui.p(ui.tags.b("Product: "), str(row.get("innovation", "N/A"))),
            ui.p(ui.tags.b("Disease: "), str(row.get("disease", "N/A"))),
            ui.p(ui.tags.b("Indication: "), str(row.get("indication", "N/A"))),
            ui.p(ui.tags.b("Target population: "), str(row.get("targeted_population", "N/A"))),
            ui.p(ui.tags.b("Technology: "), str(row.get("technology", "N/A"))),
            ui.p(ui.tags.b("Stage: "), str(row.get("trial_status", "N/A"))),
        )

    # ---------------------------------------------------------
    # Timeline plot (per-product)
    # ---------------------------------------------------------
    @render_widget
    def timeline_plot():
        row = detail_row()
        all_events = []

        # Add Trial Completion as "Collected" - Commented because of lack of trial completion date
        # trial_date = row.get("date_trial_status")
        # if pd.notna(trial_date):
        #     stage = row.get("trial_status", "Trial")
        #     if "Phase" in str(stage):
        #         label = f"{stage} Complete"
        #     else:
        #         label = f"{stage} (Trial End)"
        #     all_events.append({"name": label, "date": trial_date, "type": "Collected"})

        event_map = [
            {
                "label": "Proof of concept",
                "real": "date_proof_of_concept",
                "proj": "date_proof_of_concept",  # use same field
            },
            {
                "label": "Regulatory approval",
                "real": "date_first_regulatory",
                "proj": "proj_date_first_regulatory",
            },
            {
                "label": "First country launch",
                "real": "date_first_launch",
                "proj": "proj_date_first_launch",
            },
            {
                "label": "20% Market uptake",
                "real": None,
                "proj": "proj_date_lmic_20_uptake",
            },
        ]

        for event in event_map:
            proj_col = event["proj"]
            real_col = event["real"]

            proj_date = row.get(proj_col) if proj_col in row.index else None
            real_date = row.get(real_col) if real_col and real_col in row.index else None

            if pd.notna(proj_date):
                event_type = "Collected" if real_col and pd.notna(real_date) else "Projection"
                all_events.append({"name": event["label"], "date": proj_date, "type": event_type})

        # Part fixed
        # Add Regulatory approval as "Collected" - temporary solution
        # reg_date = row.get("proj_date_first_regulatory")
        # if pd.notna(reg_date):
        #     all_events.append({"name": "Regulatory approval", "date": reg_date, "type": "Collected"})

        # # Add other dates as "Projection"
        # projections = {
        #     "First country launch": row.get("proj_date_first_launch"),
        #     "20% Market uptake": row.get("proj_date_lmic_20_uptake"),
        # }
        # for name, date in projections.items():
        #     if pd.notna(date):
        #         all_events.append({"name": name, "date": date, "type": "Projection"})

        if not all_events:
            fig = go.FigureWidget()
            fig.update_layout(
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                margin=dict(l=0, r=0, t=0, b=0),
                height=200,
                annotations=[
                    dict(
                        text="No projected dates available",
                        xref="paper",
                        yref="paper",
                        x=0.5,
                        y=0.5,
                        showarrow=False,
                        font=dict(size=14, color="gray"),
                    )
                ],
            )
            return fig

        all_events.sort(key=lambda x: x["date"])
        dates = [e["date"] for e in all_events]
        names = [e["name"] for e in all_events]
        types = [e["type"] for e in all_events]
        colors = ["#00539B" if t == "Collected" else "#BFBBBB" for t in types]

        text_positions = ["top center" if i % 2 == 0 else "bottom center" for i in range(len(dates))]

        fig = go.FigureWidget()
        fig.add_trace(
            go.Scatter(
                x=dates,
                y=[0] * len(dates),
                mode="lines+markers+text",
                line=dict(color="#BFBBBB", width=3),
                marker=dict(size=14, color=colors, line=dict(width=2, color="white")),
                text=names,
                textposition=text_positions,
                hoverinfo="text+x",
                hovertext=[f"{n}<br>{pd.to_datetime(d).strftime('%Y-%m-%d')}" for n, d in zip(names, dates)],
                showlegend=False,
            )
        )

        fig.add_trace(
            go.Scatter(
                x=[None],
                y=[None],
                mode="markers",
                marker=dict(size=10, color="#00539B"),
                name="Collected",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=[None],
                y=[None],
                mode="markers",
                marker=dict(size=10, color="#BFBBBB"),
                name="Projection",
            )
        )

        start_range = min(pd.to_datetime(dates)) - pd.DateOffset(years=1)
        end_range = max(pd.to_datetime(dates)) + pd.DateOffset(years=1)

        fig.update_layout(
            height=200,
            margin=dict(l=20, r=20, t=30, b=30),
            xaxis=dict(
                type="date",
                range=[start_range, end_range],
                showgrid=False,
                zeroline=False,
                showline=True,
                linecolor="#BFBBBB",
                tickformat="%Y",
                dtick="M12",
                side="bottom",
            ),
            yaxis=dict(visible=False, range=[-1.8, 1.8], fixedrange=True),
            legend=dict(
                title=dict(text="Data Type", font=dict(size=12)),
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
            ),
            plot_bgcolor="white",
            paper_bgcolor="white",
        )
        return fig

    # ---------------------------------------------------------
    # Domain summary bars
    # ---------------------------------------------------------
    @render.ui
    def domain_summary_bars():
        row = detail_row()
        impact_score = row.get("impact_potential", 0)
        intro_score = row.get("introduction_readiness", 0)

        return ui.div(
            progress_row("Impact potential", impact_score),
            progress_row("Introduction readiness", intro_score),
            class_="d-flex flex-column gap-3",
        )

    # ---------------------------------------------------------
    # IMPACT POTENTIAL BOXES (popovers preserved)
    # ---------------------------------------------------------
    @render.ui
    def impact_potential_box():
        row = detail_row()

        def safe_number(val, default="Not available"):
            try:
                if pd.notna(val):
                    return val
            except Exception:
                pass
            return default

        def safe_text(val, default="Not available"):
            if pd.isna(val) or str(val).strip().lower() == "nan":
                return default
            return val

        pop_label = safe_text(row.get("pop_description"), "People at Risk")

        readiness_val = row.get("readiness", None)
        align_str = "Yes" if (pd.notna(readiness_val) and float(readiness_val) >= 50) else "No"
        # keep for later if you want to display

        return ui.TagList(
            # Population at Risk
            ui.div(
                ui.value_box(
                    ui.div(
                        ui.tags.span(pop_label, class_="vb-title-text"),
                        ui.tags.span(
                            popover(
                                ui.tags.i(
                                    class_="fa-solid fa-circle-info text-muted",
                                    style="cursor:pointer;",
                                ),
                                ui.div(
                                    ui.p("Estimated number of individuals at risk."),
                                    ui.tags.a(
                                        "Learn more",
                                        href="https://github.com/ALIGN-Consortium/GlobalHub/tree/main/docs",
                                        target="_blank",
                                        class_="fw-semibold",
                                    ),
                                ),
                                title="Methodology",
                            ),
                            class_="vb-title-icon",
                        ),
                        class_="vb-title",
                    ),
                    ui.tags.span(
                        safe_number(row.get("people_at_risk")),
                        class_="fs-5 fw-semibold",
                    ),
                    fill=True,
                    class_="h-100 shadow-sm border",
                ),
                class_="col-12 col-md-2",
                style="height: 200px;",
            ),
            # DALYs Value Box
            ui.div(
                ui.value_box(
                    ui.div(
                        ui.tags.span("DALYs", class_="vb-title-text"),
                        ui.tags.span(
                            popover(
                                ui.tags.i(
                                    class_="fa-solid fa-circle-info text-muted",
                                    style="cursor:pointer;",
                                ),
                                ui.div(
                                    ui.p("Disability-adjusted life years attributable to the condition."),
                                    ui.tags.a(
                                        "Learn more",
                                        href="https://github.com/ALIGN-Consortium/GlobalHub/blob/main/docs/Disease_DALYs_Methods_and_Reference_Values.md",
                                        target="_blank",
                                        class_="fw-semibold",
                                    ),
                                ),
                                title="Methodology",
                            ),
                            class_="vb-title-icon",
                        ),
                        class_="vb-title",
                    ),
                    ui.tags.span(
                        safe_number(row.get("dalys")),
                        class_="fs-5 fw-semibold",
                    ),
                    fill=True,
                    class_="h-100 shadow-sm border",
                ),
                class_="col-12 col-md-2",
                style="height: 200px;",
            ),
            # Efficacy
            # ui.div(
            #     ui.value_box(
            #         ui.div(
            #             ui.tags.span("Efficacy", class_="vb-title-text"),
            #             ui.tags.span(
            #                 popover(
            #                     ui.tags.i(
            #                         class_="fa-solid fa-circle-info text-muted",
            #                         style="cursor:pointer;",
            #                     ),
            #                     ui.div(
            #                         ui.p(
            #                             "Best available efficacy/effectiveness estimate (and context), ideally quantitative but can be summarized when early-stage."
            #                         ),
            #                         ui.tags.a(
            #                             "Learn more",
            #                             href="https://github.com/ALIGN-Consortium/GlobalHub/tree/main/docs",
            #                             target="_blank",
            #                             class_="fw-semibold",
            #                         ),
            #                     ),
            #                     title="Methodology",
            #                 ),
            #                 class_="vb-title-icon",
            #             ),
            #             class_="vb-title",
            #         ),
            #         ui.tags.span(
            #             safe_text(row.get("efficacy")),
            #             class_="fs-5 fw-semibold",
            #         ),
            #         fill=True,
            #         class_="h-100 shadow-sm border",
            #     ),
            #     class_="col-12 col-md-2",
            #     style="height: 200px;",
            # )
        )

    # ---------------------------------------------------------
    # FINANCING BOXES (popovers preserved)
    # ---------------------------------------------------------
    @render.ui
    def financing_box():
        row = detail_row()

        return ui.TagList(
            # Probability of Success
            ui.div(
                ui.value_box(
                    ui.div(
                        ui.tags.span("Probability of success", class_="vb-title-text"),
                        ui.tags.span(
                            popover(
                                ui.tags.i(class_="fa-solid fa-circle-info text-muted", style="cursor:pointer;"),
                                ui.div(
                                    ui.p(
                                        "Derived from R&D estimates according to ",
                                        ui.tags.strong("Funding global health product R&D: the Portfolio-to-Impact (P2I) model."),
                                        ui.tags.em(" Terry RF, Gardner CA, Dieleman JL, et al. Health Policy Plan. 2018."),
                                    ),
                                    ui.tags.a(
                                        "Learn more",
                                        href="https://github.com/ALIGN-Consortium/GlobalHub/tree/main/docs",
                                        target="_blank",
                                        class_="fw-semibold",
                                    ),
                                ),
                                title="Methodology",
                            ),
                            class_="vb-title-icon",
                        ),
                        class_="vb-title",
                    ),
                    ui.tags.span(
                        "Not available" if pd.isna(row.get("prob_success")) else f"{row.get('prob_success')}%",
                        class_="fs-5 fw-semibold",
                    ),
                    fill=True,
                    class_="h-100 shadow-sm border",
                ),
                class_="col-12 col-md-6",
                style="height: 200px;",
            ),
            # Health System Costs
            ui.div(
                ui.value_box(
                    ui.div(
                        ui.tags.span("Healthsystem costs", class_="vb-title-text"),
                        ui.tags.span(
                            popover(
                                ui.tags.i(class_="fa-solid fa-circle-info text-muted", style="cursor:pointer;"),
                                ui.div(
                                    ui.p("Estimated health system costs in million USD."),
                                    ui.p(
                                        "Derived from R&D estimates according to ",
                                        ui.tags.strong("Funding global health product R&D: the Portfolio-to-Impact (P2I) model."),
                                        ui.tags.em(" Terry RF, Gardner CA, Dieleman JL, et al. Health Policy Plan. 2018."),
                                    ),
                                    ui.tags.a(
                                        "Learn more",
                                        href="https://github.com/ALIGN-Consortium/GlobalHub/tree/main/docs",
                                        target="_blank",
                                        class_="fw-semibold",
                                    ),
                                ),
                                title="Methodology",
                            ),
                            class_="vb-title-icon",
                        ),
                        class_="vb-title",
                    ),
                    ui.tags.span(
                        "Not available" if pd.isna(row.get("hs_costs")) else row.get("hs_costs"),
                        class_="fs-5 fw-semibold",
                    ),
                    ui.tags.div("Million USD"),
                    fill=True,
                    class_="h-100 shadow-sm border",
                ),
                class_="col-12 col-md-6",
                style="height: 200px;",
            ),
        )

    # ---------------------------------------------------------
    # UPTAKE/DELIVERY BOXES (popovers preserved; commented blocks kept)
    # ---------------------------------------------------------
    @render.ui
    def uptake_delivery_box():
        row = detail_row()

        def format_date(d):
            if pd.notna(d):
                return pd.to_datetime(d).strftime("%Y-%m-%d")
            return "Not available"

        return ui.TagList(
            # 20% Market Uptake
            ui.div(
                ui.value_box(
                    ui.div(
                        ui.tags.span("Date of launch", class_="vb-title-text"),
                        ui.tags.span(
                            popover(
                                ui.tags.i(class_="fa-solid fa-circle-info text-muted", style="cursor:pointer;"),
                                ui.div(
                                    ui.p("Projected date the product will be launched in an LMIC."),
                                    ui.tags.a(
                                        "Learn more",
                                        href="https://github.com/ALIGN-Consortium/GlobalHub/tree/main/docs",
                                        target="_blank",
                                        class_="fw-semibold",
                                    ),
                                ),
                                title="Methodology",
                            ),
                            class_="vb-title-icon",
                        ),
                        class_="vb-title",
                    ),
                    ui.tags.span(format_date(row.get("proj_date_first_launch")), class_="fs-5 fw-semibold"),
                    fill=True,
                    class_="h-100 shadow-sm border",
                ),
                class_="col-12 col-md-6",
                style="height: 200px;",
            ),
            # Supply Readiness
            # ui.div(
            #     ui.value_box(
            #         ui.div(
            #             ui.tags.span("Supply Readiness", class_="vb-title-text"),
            #             ui.tags.span(
            #                 popover(
            #                     ui.tags.i(
            #                         class_="fa-solid fa-circle-info text-muted",
            #                         style="cursor:pointer;",
            #                     ),
            #                     ui.div(
            #                         ui.p("Local manufacturing or supply availability."),
            #                         ui.tags.a(
            #                             "Learn more",
            #                             href="https://github.com/ALIGN-Consortium/GlobalHub/tree/main/docs",
            #                             target="_blank",
            #                             class_="fw-semibold",
            #                         ),
            #                     ),
            #                     title="Methodology",
            #                 ),
            #                 class_="vb-title-icon",
            #             ),
            #             class_="vb-title",
            #         ),
            #         ui.tags.span(
            #             "Not available"
            #             if pd.isna(row.get("country_supply"))
            #             else row.get("country_supply"),
            #             class_="fs-5 fw-semibold",
            #         ),
            #         fill=True,
            #         class_="h-100 shadow-sm border",
            #     ),
            #     class_="col-12 col-md-3",
            #     style="height: 200px;",
            # ),
            # Distribution
            # ui.div(
            #     ui.value_box(
            #         ui.div(
            #             ui.tags.span("Distribution", class_="vb-title-text"),
            #             ui.tags.span(
            #                 popover(
            #                     ui.tags.i(
            #                         class_="fa-solid fa-circle-info text-muted",
            #                         style="cursor:pointer;",
            #                     ),
            #                     ui.div(
            #                         ui.p("Distribution channel and constraints."),
            #                         ui.tags.a(
            #                             "Learn more",
            #                             href="https://github.com/ALIGN-Consortium/GlobalHub/tree/main/docs",
            #                             target="_blank",
            #                             class_="fw-semibold",
            #                         ),
            #                     ),
            #                     title="Methodology",
            #                 ),
            #                 class_="vb-title-icon",
            #             ),
            #             class_="vb-title",
            #         ),
            #         ui.tags.span(
            #             "Not available"
            #             if pd.isna(row.get("distribution"))
            #             else row.get("distribution"),
            #             class_="fs-5 fw-semibold",
            #         ),
            #         fill=True,
            #         class_="h-100 shadow-sm border",
            #     ),
            #     class_="col-12 col-md-3",
            #     style="height: 200px;",
            # ),
            # Delivery Model
            # ui.div(
            #     ui.value_box(
            #         ui.div(
            #             ui.tags.span("Delivery Model", class_="vb-title-text"),
            #             ui.tags.span(
            #                 popover(
            #                     ui.tags.i(
            #                         class_="fa-solid fa-circle-info text-muted",
            #                         style="cursor:pointer;",
            #                     ),
            #                     ui.div(
            #                         ui.p("Clinical or programmatic delivery pathway."),
            #                         ui.tags.a(
            #                             "Learn more",
            #                             href="https://github.com/ALIGN-Consortium/GlobalHub/tree/main/docs",
            #                             target="_blank",
            #                             class_="fw-semibold",
            #                         ),
            #                     ),
            #                     title="Methodology",
            #                 ),
            #                 class_="vb-title-icon",
            #             ),
            #             class_="vb-title",
            #         ),
            #         ui.tags.span(
            #             "Not available"
            #             if pd.isna(row.get("delivery_model"))
            #             else row.get("delivery_model"),
            #             class_="fs-5 fw-semibold",
            #         ),
            #         fill=True,
            #         class_="h-100 shadow-sm border",
            #     ),
            #     class_="col-12 col-md-3",
            #     style="height: 200px;",
            # ),
        )

    # ---------------------------------------------------------
    # POLICY BOXES (popovers preserved; commented blocks kept)
    # ---------------------------------------------------------
    @render.ui
    def policy_box():
        row = detail_row()

        return ui.TagList(
            # Kenya NRA
            ui.div(
                ui.value_box(
                    ui.div(
                        ui.tags.span(
                            "Kenya market authorization", class_="vb-title-text"
                        ),
                        ui.tags.span(
                            popover(
                                ui.tags.i(
                                    class_="fa-solid fa-circle-info text-muted",
                                    style="cursor:pointer;",
                                ),
                                ui.div(
                                    ui.p(
                                        "Status of national regulatory approval in Kenya."
                                    ),
                                    ui.tags.a(
                                        "Learn more",
                                        href="https://github.com/ALIGN-Consortium/GlobalHub/tree/main/docs",
                                        target="_blank",
                                        class_="fw-semibold",
                                    ),
                                ),
                                title="Methodology",
                            ),
                            class_="vb-title-icon",
                        ),
                        class_="vb-title",
                    ),
                    ui.tags.span(
                        "Not available"
                        if pd.isna(row.get("Kenya_nra"))
                        else row.get("Kenya_nra"),
                        class_="fs-5 fw-semibold",
                    ),
                    fill=True,
                    class_="h-100 shadow-sm border",
                ),
                class_="col-12 col-md-2",
                style="height: 200px;",
            ),
            # Senegal NRA
            ui.div(
                ui.value_box(
                    ui.div(
                        ui.tags.span(
                            "Senegal market authorization", class_="vb-title-text"
                        ),
                        ui.tags.span(
                            popover(
                                ui.tags.i(
                                    class_="fa-solid fa-circle-info text-muted",
                                    style="cursor:pointer;",
                                ),
                                ui.div(
                                    ui.p(
                                        "Status of national regulatory approval in Senegal."
                                    ),
                                    ui.tags.a(
                                        "Learn more",
                                        href="https://github.com/ALIGN-Consortium/GlobalHub/tree/main/docs",
                                        target="_blank",
                                        class_="fw-semibold",
                                    ),
                                ),
                                title="Methodology",
                            ),
                            class_="vb-title-icon",
                        ),
                        class_="vb-title",
                    ),
                    ui.tags.span(
                        "Not available"
                        if pd.isna(row.get("Senegal_nra"))
                        else row.get("Senegal_nra"),
                        class_="fs-5 fw-semibold",
                    ),
                    fill=True,
                    class_="h-100 shadow-sm border",
                ),
                class_="col-12 col-md-2",
                style="height: 200px;",
            ),
            # South Africa NRA
            ui.div(
                ui.value_box(
                    ui.div(
                        ui.tags.span(
                            "South Africa market authorization", class_="vb-title-text"
                        ),
                        ui.tags.span(
                            popover(
                                ui.tags.i(
                                    class_="fa-solid fa-circle-info text-muted",
                                    style="cursor:pointer;",
                                ),
                                ui.div(
                                    ui.p(
                                        "Status of national regulatory approval in South Africa."
                                    ),
                                    ui.tags.a(
                                        "Learn more",
                                        href="https://github.com/ALIGN-Consortium/GlobalHub/tree/main/docs",
                                        target="_blank",
                                        class_="fw-semibold",
                                    ),
                                ),
                                title="Methodology",
                            ),
                            class_="vb-title-icon",
                        ),
                        class_="vb-title",
                    ),
                    ui.tags.span(
                        "Not available"
                        if pd.isna(row.get("South Africa_nra"))
                        else row.get("South Africa_nra"),
                        class_="fs-5 fw-semibold",
                    ),
                    fill=True,
                    class_="h-100 shadow-sm border",
                ),
                class_="col-12 col-md-2",
                style="height: 200px;",
            ),
            # national approval - removed for now
            # ui.div(
            #     ui.value_box(
            #         ui.div(
            #             ui.tags.span("national approval", class_="vb-title-text"),
            #             ui.tags.span(
            #                 popover(
            #                     ui.tags.i(
            #                         class_="fa-solid fa-circle-info text-muted",
            #                         style="cursor:pointer;",
            #                     ),
            #                     ui.div(
            #                         ui.p("Placeholder: Status of national regulatory approval."),
            #                         ui.tags.a(
            #                             "Learn more",
            #                             href="https://github.com/ALIGN-Consortium/GlobalHub/tree/main/docs",
            #                             target="_blank",
            #                             class_="fw-semibold",
            #                         ),
            #                     ),
            #                     title="Methodology",
            #                 ),
            #                 class_="vb-title-icon",
            #             ),
            #             class_="vb-title",
            #         ),
            #         ui.tags.span(
            #             "Not available" if pd.isna(row.get("nra")) else row.get("nra"),
            #             class_="fs-5 fw-semibold",
            #         ),
            #         fill=True,
            #         class_="h-100 shadow-sm border",
            #     ),
            #     class_="col-12 col-md-2",
            #     style="height: 200px;",
            # ),
            # Global approval
            ui.div(
                ui.value_box(
                    ui.div(
                        ui.tags.span("Global approval", class_="vb-title-text"),
                        ui.tags.span(
                            popover(
                                ui.tags.i(
                                    class_="fa-solid fa-circle-info text-muted",
                                    style="cursor:pointer;",
                                ),
                                ui.div(
                                    ui.p(
                                        "Whether the product has approval/authorization/prequalification by a global body. Includes WHO PQ, FDA, EMA, or other global approval."
                                    ),
                                    ui.tags.a(
                                        "Learn more",
                                        href="https://github.com/ALIGN-Consortium/GlobalHub/tree/main/docs",
                                        target="_blank",
                                        class_="fw-semibold",
                                    ),
                                ),
                                title="Methodology",
                            ),
                            class_="vb-title-icon",
                        ),
                        class_="vb-title",
                    ),
                    ui.tags.span(
                        "Not available" if pd.isna(row.get("gra")) else row.get("gra"),
                        class_="fs-5 fw-semibold",
                    ),
                    fill=True,
                    class_="h-100 shadow-sm border",
                ),
                class_="col-12 col-md-2",
                style="height: 200px;",
            ),
            # EML listed
            ui.div(
                ui.value_box(
                    ui.div(
                        ui.tags.span("EML listed", class_="vb-title-text"),
                        ui.tags.span(
                            popover(
                                ui.tags.i(
                                    class_="fa-solid fa-circle-info text-muted",
                                    style="cursor:pointer;",
                                ),
                                ui.div(
                                    ui.p(
                                        "Whether the product is listed on WHO Essential Medicines List (EML)."
                                    ),
                                    ui.tags.a(
                                        "Learn more",
                                        href="https://github.com/ALIGN-Consortium/GlobalHub/tree/main/docs",
                                        target="_blank",
                                        class_="fw-semibold",
                                    ),
                                ),
                                title="Methodology",
                            ),
                            class_="vb-title-icon",
                        ),
                        class_="vb-title",
                    ),
                    ui.tags.span(
                        "Not available" if pd.isna(row.get("eml")) else row.get("eml"),
                        class_="fs-5 fw-semibold",
                    ),
                    fill=True,
                    class_="h-100 shadow-sm border",
                ),
                class_="col-12 col-md-2",
                style="height: 200px;",
            ),
            # Policy Readiness
            # ui.div(
            #     ui.value_box(
            #         ui.div(
            #             ui.tags.span("Policy Readiness", class_="vb-title-text"),
            #             ui.tags.span(
            #                 popover(
            #                     ui.tags.i(
            #                         class_="fa-solid fa-circle-info text-muted",
            #                         style="cursor:pointer;",
            #                     ),
            #                     ui.div(
            #                         ui.p(
            #                             "Degree to which policies and strategies support adoption (WHO-level for global or national strategies including reimbursement, prioritization)."
            #                         ),
            #                         ui.tags.a(
            #                             "Learn more",
            #                             href="https://github.com/ALIGN-Consortium/GlobalHub/tree/main/docs",
            #                             target="_blank",
            #                             class_="fw-semibold",
            #                         ),
            #                     ),
            #                     title="Methodology",
            #                 ),
            #                 class_="vb-title-icon",
            #             ),
            #             class_="vb-title",
            #         ),
            #         ui.tags.span(
            #             "Not available"
            #             if pd.isna(row.get("policy_readiness"))
            #             else row.get("policy_readiness"),
            #             class_="fs-5 fw-semibold",
            #         ),
            #         fill=True,
            #         class_="h-100 shadow-sm border",
            #     ),
            #     class_="col-12 col-md-2",
            #     style="height: 200px;",
            # ),
            # Policy Implementation
            # ui.div(
            #     ui.value_box(
            #         ui.div(
            #             ui.tags.span("Policy Implemented", class_="vb-title-text"),
            #             ui.tags.span(
            #                 popover(
            #                     ui.tags.i(
            #                         class_="fa-solid fa-circle-info text-muted",
            #                         style="cursor:pointer;",
            #                     ),
            #                     ui.div(
            #                         ui.p(
            #                             "Whether relevant policies are actively implemented, including programmatic coverage."
            #                         ),
            #                         ui.tags.a(
            #                             "Learn more",
            #                             href="https://github.com/ALIGN-Consortium/GlobalHub/tree/main/docs",
            #                             target="_blank",
            #                             class_="fw-semibold",
            #                         ),
            #                     ),
            #                     title="Methodology",
            #                 ),
            #                 class_="vb-title-icon",
            #             ),
            #             class_="vb-title",
            #         ),
            #         ui.tags.span(
            #             "Not available"
            #             if pd.isna(row.get("policy_implemented"))
            #             else row.get("policy_implemented"),
            #             class_="fs-5 fw-semibold",
            #         ),
            #         fill=True,
            #         class_="h-100 shadow-sm border",
            #     ),
            #     class_="col-12 col-md-2",
            #     style="height: 200px;",
            # ),
        )