# modules/innovation_page.py
from shiny import ui, reactive, module, render, req
from shiny.render import DataGrid
from shiny.ui import popover
from utils.ui_helpers import info_tooltip
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
      - KPIs
      - Market overview (trend + donut)
      - Product explorer table (single DataGrid)
      - Detail section (title/summary + readiness + timeline)
      - Impact potential
      - Introduction readiness (Financing + Uptake/Delivery + Policy)
    """
    return ui.TagList(
        ui.div(
            # =====================================================
            # KPI CARDS
            # =====================================================
            ui.div(
                ui.div(ui.output_ui("kpi_databases"), class_="col-md-6"),
                ui.div(ui.output_ui("kpi_products"), class_="col-md-6"),
                class_="row mb-4 g-3",
            ),
            # =====================================================
            # MARKET OVERVIEW
            # =====================================================
            ui.div(
                ui.div(
                    ui.div(
                        ui.span("Market overview", class_="fw-semibold"),
                        ui.div(
                            ui.span(
                                "Select disease target:",
                                class_="fw-semibold text-muted",
                            ),
                            ui.tags.span(
                                popover(
                                    ui.tags.i(
                                        class_="fa-solid fa-circle-info text-muted",
                                        style="cursor:pointer;",
                                    ),
                                    ui.div(
                                        ui.p(
                                            "The disease target filter applies to all visuals and tables below. Click the 'Reset filters' button on the botton right of the screen to reset all filters."
                                        ),
                                    ),
                                    title="Filters info",
                                ),
                                class_="ms-2",
                            ),
                            ui.input_select(
                                "disease_selector",
                                None,
                                choices=[
                                    "All products"
                                ],  # filled by server via ui.update_select
                                selected="All products",
                                width="220px",
                            ),
                            class_="d-flex align-items-center gap-2",
                        ),
                        class_="card-header d-flex align-items-center justify-content-between flex-wrap gap-2",
                    ),
                    ui.div(
                        ui.div(
                            ui.div(
                                ui.div(
                                    ui.div(
                                        ui.tags.span(
                                            "Products Projected to Enter LMIC Markets in the Next 3 Years"
                                        ),
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
                                ui.div(
                                    ui.output_data_frame("products_coming_years"),
                                    class_="card-body p-0",
                                    style="height:410px; overflow:auto;",
                                ),
                                class_="card h-100 mb-0",
                            ),
                            class_="col-md-4",
                        ),
                        ui.div(
                            ui.div(
                                ui.div(
                                    ui.tags.span("Product Type Summary"),
                                    info_tooltip(
                                        "Clicking on a product type will filter the database and visuals below. Clicking the blue icon in the right corner of the screen to reset all filters"
                                    ),
                                    class_="card-header d-flex align-items-center justify-content-between",
                                ),
                                ui.div(
                                    output_widget("treemap_chart", height="360px"),
                                    class_="card-body",
                                ),
                                class_="card h-100 mb-0",
                            ),
                            class_="col-md-4",
                        ),
                        ui.div(
                            ui.div(
                                ui.div(
                                    ui.tags.span("Product Type Summary"),
                                    info_tooltip(
                                        "Clicking on a development status below will filter the database and visuals below. Clicking the blue icon in the right corner of the screen to reset all filters"
                                    ),
                                    class_="card-header d-flex align-items-center justify-content-between",
                                ),
                                ui.div(
                                    output_widget("pie_chart", height="360px"),
                                    class_="card-body",
                                ),
                                class_="card h-100 mb-0",
                            ),
                            class_="col-md-4",
                        ),
                        class_="row g-3",
                    ),
                    class_="card-body",
                ),
                class_="card mb-4",
            ),
            class_="col-12",
        ),
        # =====================================================
        # PRODUCT EXPLORER (single table)
        # =====================================================
        ui.div(
            ui.div(
                ui.div(
                    ui.div(
                        ui.span(
                            "Product Explorer",
                            ui.tags.span(
                                popover(
                                    ui.tags.i(
                                        class_="fa-solid fa-circle-info text-muted",
                                        style="cursor:pointer;",
                                    ),
                                    ui.div(
                                        ui.p(
                                            "Click the 'Clear table filters' or 'Reset filters' buttons to reset table or page filters, respectively."
                                        ),
                                    ),
                                    title="Filters info",
                                ),
                                class_="ms-2",
                            ),
                            class_="fw-semibold",
                        ),
                        ui.div(
                            ui.input_action_button(
                                "clear_filters",
                                ui.tags.span(
                                    ui.tags.i(class_="fa-solid fa-rotate-left me-1"),
                                    "Clear table filters",
                                ),
                                class_="btn btn-sm btn-outline-secondary",
                            ),
                            ui.input_action_button(
                                "add_selected_to_cart",
                                ui.tags.span(
                                    ui.tags.i(class_="fa-solid fa-cart-plus me-1"),
                                    "Add to cart",
                                ),
                                class_="btn btn-sm btn-success",
                            ),
                            class_="d-flex gap-2",
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
                                ui.tags.span("Date of First Launch in an LMIC"),
                                ui.tags.span(
                                    popover(
                                        ui.tags.i(
                                            class_="fa-solid fa-circle-info text-muted",
                                            style="cursor:pointer;",
                                        ),
                                        ui.div(
                                            ui.p(
                                                "Observed or projected date of launch in an LMIC. Data represents median, first and third quantile, respectively. Dates in the past represent products launched in an LMIC other than Kenya, South Africa or Senegal.",
                                                ui.p(
                                                    "Projections calculated based on the method by: ",
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
                                            title="Methodology",
                                        ),
                                        class_="ms-2",
                                    ),
                                    class_="ms-2",
                                ),
                                class_="d-flex align-items-center gap-1",
                            ),
                            class_="card-header",
                        ),
                        ui.div(ui.output_ui("date_launch_box"), class_="card-body"),
                        class_="card h-100",
                    ),
                    class_="col-12 col-lg-4",
                ),
                # Right column
                ui.div(
                    ui.div(
                        ui.div(
                            ui.div(
                                ui.tags.span(
                                    "Speedometer Introduction Milestone Tracking"
                                ),
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
                            output_widget(
                                "timeline_plot", height="200px", width="100%"
                            ),
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
            # INTRODUCTION READINESS
            # =====================================================
            ui.div(
                ui.div(
                    ui.div(
                        ui.span("Global Introduction Readiness", class_="fw-semibold"),
                        class_="d-flex align-items-center justify-content-between flex-wrap gap-2",
                    ),
                    class_="card-header",
                ),
                ui.div(
                    ui.output_ui("policy_box", class_="row g-3"),
                    class_="card-body",
                ),
                class_="card",
                min_height="600px",
            ),
            class_="container-fluid px-3 py-3",
        ),
        # floating filter status
        ui.output_ui("filter_status_display"),
        # floating reset button
        ui.div(
            ui.tooltip(
                ui.input_action_button(
                    "reset_page_filters",
                    ui.tags.i(class_="fa-solid fa-rotate-left"),
                    class_="btn btn-primary",
                ),
                "Reset all page filters",
                placement="left",
            ),
            class_="floating-reset-btn",
        ),
    )


@module.server
def innovation_page_server(input, output, session, cart):
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
    # Populate dropdown choices
    # ---------------------------------------------------------
    diseases = ["All products"] + sorted(horizon_df["disease"].dropna().unique().tolist())
    all_products = sorted(horizon_df["innovation"].dropna().unique().tolist())

    @reactive.Effect
    def _update_choices():
        ui.update_select(
            "disease_selector",
            choices=diseases,
            selected="All products",
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
            ui.div(
                ui.tags.i(class_=f"fa-solid fa-{icon} fa-2x text-primary opacity-50")
            ),
            class_="d-flex justify-content-between align-items-center p-3",
        )

    def count_innovations(diseases_list):
        if isinstance(diseases_list, str):
            diseases_list = [diseases_list]
        return len(
            horizon_df[horizon_df["disease"].isin(diseases_list)]["innovation"].unique()
        )

    @render.ui
    def kpi_databases():
        return ui.card(kpi_card(14, "Databases aggregated", "", "database"))

    @render.ui
    def kpi_products():
        df = page_df()
        return ui.card(
            kpi_card(df.innovation.nunique(), "Products included", "", "table")
        )

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
    selected_category = reactive.Value(None)
    selected_status = reactive.Value(None)

    # ---------------------------------------------------------
    # Layout settle delay
    # ---------------------------------------------------------
    @reactive.Effect
    def _layout_delay():
        reactive.invalidate_later(0.5)
        layout_ready.set(True)

    @reactive.Calc
    def base_df():
        # Core data for the page: WHO scope, excluding Phase 1
        df = innovation_df[innovation_df["trial_status"] != "Phase 1"].copy()
        return df

    @reactive.Calc
    def disease_df():
        df = base_df()
        disease = input.disease_selector()
        if disease != "All products":
            df = df[df["disease"] == disease]
        return df

    @reactive.Calc
    def category_filtered_df():
        df = disease_df()
        status = selected_status.get()
        if status:
            df = df[df["trial_status"] == status]
        return df


    @reactive.Calc
    def status_filtered_df():
        df = disease_df()
        category = selected_category.get()
        if category:
            df = df[df["category"] == category]
        return df

    @reactive.Calc
    def page_df():
        df = disease_df()
        category = selected_category.get()
        status = selected_status.get()

        if category:
            df = df[df["category"] == category]
        if status:
            df = df[df["trial_status"] == status]

        return df

    @reactive.Calc
    def table_df():
        # Applies disease, category AND date filters
        df_f = page_df()
        df_f = df_f[
            df_f["proj_date_lmic_20_uptake"].notna()
            & (df_f["proj_date_lmic_20_uptake"] >= pd.Timestamp("2025-01-01"))
        ]
        return df_f

    # ---------------------------------------------------------
    # Pie (donut) chart
    # ---------------------------------------------------------
    @render_widget
    def pie_chart():
        # Ensure reactivity by calling .get() early
        selected = selected_status.get()
        df_unique = status_filtered_df()

        stage_counts = df_unique["trial_status"].value_counts().reset_index()
        stage_counts.columns = ["status", "count"]
        total_innovations = len(df_unique)
        if total_innovations == 0:
            return go.FigureWidget()

        stage_counts["pct"] = (stage_counts["count"] / total_innovations * 100).round(1)

        color_map = {
            "Preclinical": "#BFBBBB",  # Neutral Gray
            "Phase 1": "#00539B",       # Accent Blue
            "Phase 2": "#00539B",
            "Phase 3": "#012169",       # Primary Blue
            "Phase 4": "#012169",
            "Observational": "#8b5cf6",
            "Implementation/Pilot": "#228B22", # Success Green
            "Not in trials": "#DC143C", # Error Red
            "Unknown": "#BFBBBB",
        }

        # Apply selection highlighting: gray out non-selected slices
        colors = []
        for status in stage_counts["status"]:
            base_color = color_map.get(status, "#cbd5e1")
            if selected and status != selected:
                colors.append("#e5e7eb")  # Light gray
            else:
                colors.append(base_color)

        fig = go.FigureWidget(
            data=[
                go.Pie(
                    labels=stage_counts["status"],
                    values=stage_counts["pct"],
                    hole=0.4,
                    marker=dict(colors=colors, line=dict(color="#FFFFFF", width=2)),
                    textinfo="label+percent",
                    textposition="outside",
                )
            ]
        )
        fig.update_layout(
            showlegend=True,
            margin=dict(l=0, r=0, t=0, b=0),
            clickmode="event+select",
        )

        def on_click(trace, points, state):
            if not points.point_inds:
                return
            # Use label if available, otherwise fallback to index
            clicked_status = (
                points.labels[0]
                if hasattr(points, "labels") and points.labels
                else stage_counts["status"].iloc[points.point_inds[0]]
            )
            # Toggle logic
            if selected_status.get() == clicked_status:
                selected_status.set(None)
            else:
                selected_status.set(clicked_status)

        fig.data[0].on_click(on_click)

        return fig

    # ---------------------------------------------------------
    # SINGLE PIPELINE TABLE (DataGrid)
    # ---------------------------------------------------------
    @render.data_frame
    def pipeline_tbl():
        clear_trigger.get()
        df_f = table_df()
        if df_f.empty:
            return None

        # NOTE: keep the same column mapping as your existing code
        # You used proj_date_first_launch in the table display, but filtered on proj_date_lmic_20_uptake.
        return render.DataGrid(
            df_f.assign(
                proj_date_first_launch=lambda d: d[
                    "proj_date_first_launch"
                ].dt.strftime("%Y-%m-%d")
            ).rename(
                columns={
                    "innovation": "Product",
                    "manufacturer": "Manufacturer",
                    "category": "Category",
                    "trial_status": "Status",
                    "proj_date_first_launch": "Projected date of launch",
                    "disease": "Disease area",
                }
            )[
                [
                    "Product",
                    "Manufacturer",
                    "Disease area",
                    "Category",
                    "Status",
                    "Projected date of launch",
                ]
            ],
            selection_mode="row",
            width="100%",
            filters=True,
            summary=False,
        )

    @render.data_frame
    def products_coming_years():
        clear_trigger.get()
        df_f = page_df()

        today = pd.Timestamp.today()
        three_years = today + pd.DateOffset(years=3)

        df_f = df_f.loc[
            (df_f["proj_date_first_launch"] >= today)
            & (df_f["proj_date_first_launch"] <= three_years)
        ].copy()

        if df_f.empty:
            return None
        return render.DataGrid(
            df_f.assign(
                proj_date_first_launch=lambda d: d[
                    "proj_date_first_launch"
                ].dt.strftime("%Y-%m-%d")
            ).rename(
                columns={
                    "innovation": "Product",
                    "proj_date_first_launch": "Projected date of launch",
                }
            )[
                [
                    "Product",
                    "Projected date of launch",
                ]
            ],
            selection_mode="row",
            width="100%",
            filters=False,
            summary=False,
        )

    @reactive.Effect
    @reactive.event(input.pipeline_tbl_selected_rows)
    def _on_row_select():
        if not input.pipeline_tbl_selected_rows():
            return

        idx = input.pipeline_tbl_selected_rows()[0]
        df_f = table_df()
        if df_f.empty:
            return None
        if idx < len(df_f):
            selected_id = df_f.iloc[idx]["innovation"]
            selected_innovation.set(selected_id)

    @reactive.Effect
    @reactive.event(input.clear_filters)
    def _clear_filters():
        clear_trigger.set(clear_trigger.get() + 1)

    @reactive.Effect
    @reactive.event(input.add_selected_to_cart)
    def _add_selected_to_cart():
        selected_id = selected_innovation()
        if selected_id:
            current = cart.get()
            new_cart = current.copy()
            new_cart.add(selected_id)
            cart.set(new_cart)
            ui.notification_show(f"Added {selected_id} to comparison list", type="message")


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
            ui.p(
                ui.tags.b("Target population: "),
                str(row.get("targeted_population", "N/A")),
            ),
            ui.p(ui.tags.b("Technology: "), str(row.get("technology", "N/A"))),
            ui.p(ui.tags.b("Stage: "), str(row.get("trial_status", "N/A"))),
            ui.p(ui.tags.b("Manufacturer: "), str(row.get("manufacturer", "N/A"))),
        )

    # ---------------------------------------------------------
    # Timeline plot (per-product)
    # ---------------------------------------------------------
    @render_widget
    def timeline_plot():
        row = detail_row()
        all_events = []

        event_map = [
            {
                "label": "Proof of Concept",
                "real": "date_proof_of_concept",
                "proj": "date_proof_of_concept",
            },
            {
                "label": "Marketing Authorization",
                "real": "date_first_regulatory",
                "proj": "proj_date_first_regulatory",
            },
            {
                "label": "First Country Launch",
                "real": "date_first_launch",
                "proj": "proj_date_first_launch",
            },
            {
                "label": "20% Market Uptake",
                "real": None,
                "proj": "proj_date_lmic_20_uptake",
            },
        ]

        for event in event_map:
            proj_col = event["proj"]
            real_col = event["real"]

            proj_date = row.get(proj_col) if proj_col in row.index else None
            real_date = (
                row.get(real_col) if real_col and real_col in row.index else None
            )

            if pd.notna(proj_date):
                event_type = (
                    "Observed" if real_col and pd.notna(real_date) else "Speedometer Projection"
                )

                all_events.append(
                    {
                        "name": event["label"],
                        "date": proj_date,
                        "type": event_type,
                    }
                )

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

        # Color by milestone
        event_colors = {
            "Proof of Concept": "#00539B",      # Accent Blue
            "Marketing Authorization": "#012169", # Primary Blue
            "First Country Launch": "#228B22",    # Success Green
            "20% Market Uptake": "#8b5cf6",
        }

        colors = [event_colors.get(n, "#444444") for n in names]

        text_positions = [
            "top center" if i % 2 == 0 else "bottom center"
            for i in range(len(dates))
        ]

        fig = go.FigureWidget()

        fig.add_trace(
            go.Scatter(
                x=dates,
                y=[0] * len(dates),
                mode="lines+markers+text",
                line=dict(color="#BFBBBB", width=3),
                marker=dict(
                    size=14,
                    color=colors,
                    line=dict(width=2, color="white"),
                ),
                text=names,
                textposition=text_positions,
                customdata=types,
                hovertemplate=(
                    "<b>%{text}</b><br>"
                    "Date: %{x|%Y-%m-%d}<br>"
                    "Data: %{customdata}<extra></extra>"
                ),
                showlegend=False,
            )
        )

        for label, color in event_colors.items():
            fig.add_trace(
                go.Scatter(
                    x=[None],
                    y=[None],
                    mode="markers",
                    marker=dict(size=12, color=color),
                    name=label,
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
            yaxis=dict(
                visible=False,
                range=[-1.8, 1.8],
                fixedrange=True,
            ),
            plot_bgcolor="white",
            paper_bgcolor="white",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                title=dict(text="Milestones")
            )
        )

        return fig
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
        align_str = (
            "Yes" if (pd.notna(readiness_val) and float(readiness_val) >= 50) else "No"
        )
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
                                    ui.p(
                                        "Disability-adjusted life years attributable to the condition."
                                    ),
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
        )

    @render.ui
    def date_launch_box():
        row = detail_row()

        def format_date(d):
            if pd.notna(d):
                return pd.to_datetime(d).strftime("%Y-%m-%d")
            return "Not available"

        is_observed = row.get("date_first_launch_observed_y_n") == "Y"

        median = format_date(row.get("proj_date_first_launch"))
        lower = format_date(row.get("proj_date_first_launch_25"))
        upper = format_date(row.get("proj_date_first_launch_75"))

        # Main value with asterisk
        main_value = ui.tags.span(
            f"{median}",
            class_="fs-5 fw-semibold",
        )

        # Range (only if projected)
        range_line = (
            ui.tags.div(
                f"Range (25th–75th): {lower} to {upper}",
                class_="text-muted"
            )
            if not is_observed else None
        )

        # Footnote
        footnote = ui.tags.div(
            "*Observed" if is_observed else "*Speedometer projection",
            class_="text-muted small"
        )

        return ui.TagList(
            ui.div(
                main_value,
                range_line,
                footnote,
                class_="col-12 col-md-12 d-flex flex-column justify-content-center",
                # style="height: 200px;",
            ),
        )
    # ---------------------------------------------------------
    # POLICY BOXES (popovers preserved; commented blocks kept)
    # ---------------------------------------------------------
    @render.ui
    def filter_status_display():
        disease = input.disease_selector()
        category = selected_category.get()
        status = selected_status.get()

        if disease == "All products" and category is None and status is None:
            return None

        status_items = []
        if disease != "All products":
            status_items.append(f"Disease: {disease}")
        if category:
            status_items.append(f"Category: {category}")
        if status:
            status_items.append(f"Status: {status}")

        return ui.div(
            ui.div(
                ui.tags.span("Current filters:", class_="fw-bold me-2"),
                *[ui.tags.span(item, class_="badge bg-info me-1") for item in status_items],
            ),
            class_="floating-filter-status shadow-sm",
        )

    @render.ui
    def policy_box():
        row = detail_row()

        return ui.TagList(
            # Kenya NRA
            ui.div(
                ui.value_box(
                    ui.div(
                        ui.tags.span(
                            "Kenya Market Authorization", class_="vb-title-text"
                        ),
                        ui.tags.span(
                            popover(
                                ui.tags.i(
                                    class_="fa-solid fa-circle-info text-muted",
                                    style="cursor:pointer;",
                                ),
                                ui.div(
                                    ui.p(
                                        "Status of national marketing authorization in Kenya."
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
                            "Senegal Market Authorization", class_="vb-title-text"
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
                            "South Africa Market Authorization", class_="vb-title-text"
                        ),
                        ui.tags.span(
                            popover(
                                ui.tags.i(
                                    class_="fa-solid fa-circle-info text-muted",
                                    style="cursor:pointer;",
                                ),
                                ui.div(
                                    ui.p(
                                        "Status of national marketing authorization in South Africa."
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
            # Global approval
            ui.div(
                ui.value_box(
                    ui.div(
                        ui.tags.span("Global Approval", class_="vb-title-text"),
                        ui.tags.span(
                            popover(
                                ui.tags.i(
                                    class_="fa-solid fa-circle-info text-muted",
                                    style="cursor:pointer;",
                                ),
                                ui.div(
                                    ui.p(
                                        "Whether the product has approval/authorization/prequalification by a global body. Includes WHO PQ, US FDA, EMA, or other global approval."
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
                        ui.tags.span(
                            "WHO Essential Medicines/Diagnostics",
                            class_="vb-title-text",
                        ),
                        ui.tags.span(
                            popover(
                                ui.tags.i(
                                    class_="fa-solid fa-circle-info text-muted",
                                    style="cursor:pointer;",
                                ),
                                ui.div(
                                    ui.p(
                                        "Whether the product is listed on WHO Essential Medicines/Devices List (EML)."
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
                class_="col-12 col-md-2 px-0",
                style="height: 200px;",
            ),
        )

    @render_widget
    def treemap_chart():
        selected = selected_category.get()
        df_unique = category_filtered_df()

        type_counts = (
            df_unique["category"].fillna("Unknown").value_counts().reset_index()
        )
        type_counts.columns = ["category", "count"]

        if type_counts.empty:
            return go.FigureWidget()

        category_colors = {
            "Diagnostic": "#00539B",    # Accent Blue
            "Drug": "#012169",          # Primary Blue
            "Vaccine": "#228B22",       # Success Green
            "Medical Device": "#8b5cf6",
            "Vector Control": "#DC143C", # Error Red
            "Software": "#ec4899",
            "Other": "#BFBBBB",         # Neutral Gray
            "Unknown": "#BFBBBB",
        }

        colors = []
        for cat in type_counts["category"]:
            base_color = category_colors.get(cat, "#94a3b8")
            if selected and cat != selected:
                colors.append("#e5e7eb")
            else:
                colors.append(base_color)

        fig = go.FigureWidget(
            data=[
                go.Treemap(
                    labels=type_counts["category"],
                    parents=[""] * len(type_counts),
                    values=type_counts["count"],
                    textinfo="label+value",
                    hovertemplate="<b>%{label}</b><br>Products: %{value}<extra></extra>",
                    marker=dict(colors=colors),
                )
            ]
        )

        fig.update_layout(
            margin=dict(l=0, r=0, t=0, b=0),
            paper_bgcolor="rgba(0,0,0,0)",
            clickmode="event+select",
        )

        def on_click(trace, points, state):
            if not points.point_inds:
                return
            clicked_category = (
                points.labels[0]
                if hasattr(points, "labels") and points.labels
                else type_counts["category"].iloc[points.point_inds[0]]
            )
            if selected_category.get() == clicked_category:
                selected_category.set(None)
            else:
                selected_category.set(clicked_category)

        fig.data[0].on_click(on_click)

        return fig

    @reactive.Effect
    def _auto_select_on_filter():
        df_f = table_df()
        if not df_f.empty:
            current = selected_innovation.get()
            if current not in df_f["innovation"].values:
                selected_innovation.set(df_f.iloc[0]["innovation"])
        else:
            selected_innovation.set(None)

    @reactive.Effect
    @reactive.event(input.reset_page_filters)
    def _reset_page_filters():
        clear_trigger.set(clear_trigger.get() + 1)
        selected_category.set(None)
        selected_status.set(None)
        selected_innovation.set(None)

        ui.update_select(
            "disease_selector",
            selected="All products",
        )
        # We don't strictly need to set selected_innovation here
        # because _auto_select_on_filter will handle it when table_df changes.
