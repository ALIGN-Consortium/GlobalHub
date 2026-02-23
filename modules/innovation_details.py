from shiny import ui, reactive, req as shiny_req
from shiny.express import render
import pandas as pd
import plotly.graph_objects as go
from shinywidgets import output_widget, render_widget
from utils.data_loader import load_data
from shiny.express import render


def req(condition):
    """
    Helper to stop execution if a condition is not met (similar to R Shiny's req).
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


def innovation_details_ui(id):
    """
    Defines the User Interface for the Innovation Details module.

    Layout:
    1. Innovation Explorer: Table to select an innovation.
    2. Summary Card: Title and key metadata.
    3. Two-Column Layout:
       - Left: Overall domain readiness bars.
       - Right: Project timeline visualization.
    4. Impact Potential: Value boxes for impact metrics.
    5. Introduction Readiness: Detailed breakdown (Financing, Uptake, Policy).
    """
    return ui.div(
        # Innovation Explorer table
        ui.div(
            ui.div(
                ui.span("Innovation explorer", class_="fw-semibold"),
                class_="card-header",
            ),
            ui.div(
                ui.output_data_frame("pipeline_tbl_details"),
                class_="card-body",
            ),
            class_="card mb-4",
            min_height="500px",
        ),
        # Title & summary
        ui.div(
            ui.div(ui.output_text("detail_title"), class_="card-header"),
            ui.div(ui.output_ui("detail_summary"), class_="card-body"),
            class_="card",
            min_height="400px",
        ),
        # Two-column layout
        ui.div(
            # Left column
            ui.div(
                ui.div(
                    ui.div("Overall domain readiness", class_="card-header"),
                    ui.div(ui.output_ui("domain_summary_bars"), class_="card-body"),
                    class_="card h-100",
                ),
                class_="col-12 col-lg-4",
            ),
            # Right column
            ui.div(
                ui.div(
                    ui.div(
                        "Projected timeline for the innovation selected",
                        class_="card-header",
                    ),
                    ui.div(
                        output_widget("timeline_plot", height="200px"),
                        class_="card-body d-flex align-items-center justify-content-center",
                    ),
                    class_="card h-100",
                ),
                class_="col-12 col-lg-8",
            ),
            class_="row g-4 g-3",
        ),
        # Impact Potential
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
                        ui.output_ui("impact_potential_box"),
                        class_="card-body",
                    ),
                    class_="card bg-light border-0",
                ),
            ),
            class_="card",
            min_height="600px",
        ),
        # Introduction Readiness - Broken down by section
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
                                ui.output_ui("financing_box", class_="row g-3 mt-1"),
                                class_="card-body",
                            ),
                            class_="card h-100 bg-light border-0",
                        ),
                        class_="col-md-4",
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
                        class_="col-md-8",
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
        id=id,
    )


def innovation_details_server(id, selected_innovation, input, output, session):
    """
    Server logic for the Innovation Details module.

    Handles:
    - Displaying detailed metrics for a selected innovation.
    - Synchronizing selection with the Overview module via `selected_innovation`.
    - Rendering detailed value boxes and timelines using real data.
    """
    data = load_data()
    horizon_df = data["horizon"]
    innovation_df = data["innovation_df"]

    @render.data_frame
    def pipeline_tbl_details():
        """
        Renders the table in the Details tab, allowing independent selection.
        """
        df_filtered = innovation_df
        req(not df_filtered.empty)

            # Removing Phase 1 only
        df_filtered = df_filtered[df_filtered["trial_status"] != "Phase 1"]
        # Removing items with proj date <= today 
        
        df_filtered = df_filtered[
            df_filtered["proj_date_lmic_20_uptake"].notna()
            & (df_filtered["proj_date_lmic_20_uptake"] >= pd.Timestamp("2025-01-01"))
        ]

        return render.DataGrid(
            df_filtered.assign(
                proj_date_lmic_20_uptake=lambda d: d[
                    "proj_date_lmic_20_uptake"
                ].dt.strftime("%Y-%m-%d")
            ).rename(
                columns={
                    "innovation": "Innovation",
                    "category": "Category",
                    "trial_status": "Status",
                    "proj_date_lmic_20_uptake": "Projected Date of 20% Market Uptake",
                    "disease": "Disease Area",
                }
            )[
                [
                    "Innovation",
                    "Disease Area",
                    "Category",
                    "Status",
                    "Projected Date of 20% Market Uptake",
                ]
            ],
            selection_mode="row",
            width="100%",
            filters=True,
        )

    @reactive.Effect
    @reactive.event(input.pipeline_tbl_details_selected_rows)
    def _():
        """
        Event Handler: Updates the shared `selected_innovation` reactive value
        when a row is clicked in the details table.
        """
        if not input.pipeline_tbl_details_selected_rows():
            return
        idx = input.pipeline_tbl_details_selected_rows()[0]

        df_filtered = innovation_df

        selected_id = df_filtered.iloc[idx]["innovation"]
        selected_innovation.set(selected_id)

    @reactive.Calc
    def get_selected_id():
        """Returns the ID of the currently selected innovation."""
        return selected_innovation()

    @reactive.Calc
    def detail_row():
        """
        Retrieves the full data row for the selected innovation.
        """
        selected_id = get_selected_id()
        req(selected_id)  # Ensure selected_id is not None
        row = innovation_df[innovation_df["innovation"] == selected_id]
        req(not row.empty)  # Ensure row is not empty
        return row.iloc[0]

    def format_value_box(
        title,
        value,
        height="200px",
        is_percent=True,
        check_threshold=True,
        display_text=None,
    ):
        """Helper to format value boxes with consistent styling and logic."""

        # Handle numpy types
        if hasattr(value, "item"):
            value = value.item()

        numeric_val = 0
        is_missing = pd.isna(value) or value is None

        # NEW: detect yes/true strings
        is_yes = isinstance(value, str) and value.strip().lower() == "yes"

        if is_missing:
            display_val = "Not available"
        elif isinstance(value, (int, float)):
            numeric_val = value
            if display_text is not None:
                display_val = display_text
            elif is_percent:
                display_val = f"{int(value)}%"
            else:
                display_val = f"{int(value):,}"
        else:
            display_val = str(value)

        theme_class = ""
        icon = None
        val_class = "mb-1"

        if is_missing:
            theme_class = "bg-white text-muted border"
            val_class += " fs-4"

        elif check_threshold:
            # NEW: Yes/yes → green
            if is_yes:
                theme_class = "bg-success-subtle text-success-emphasis"
                icon = ui.tags.i(
                    class_="fa-solid fa-circle-check fs-4 position-absolute top-0 end-0 m-3 text-success"
                )

            elif numeric_val > 50:
                theme_class = "bg-success-subtle text-success-emphasis"
                icon = ui.tags.i(
                    class_="fa-solid fa-circle-check fs-4 position-absolute top-0 end-0 m-3 text-success"
                )
            else:
                theme_class = "bg-danger-subtle text-danger-emphasis"
                icon = ui.tags.i(
                    class_="fa-solid fa-circle-xmark fs-4 position-absolute top-0 end-0 m-3 text-danger"
                )

        return ui.div(
            ui.div(
                icon,
                ui.h2(str(display_val), class_=val_class),
                ui.p(title, class_="fs-6 mb-0 text-muted"),
                class_=(
                    "card-body d-flex flex-column justify-content-center "
                    f"h-100 position-relative {theme_class}"
                ),
            ),
            class_="card h-100 border-0 shadow-sm",
            style=f"height: {height};",
        )

    @render.text
    def detail_title():
        row = detail_row()
        return f"{row['innovation']} ({row['category']})"

    @render.ui
    def detail_summary():
        row = detail_row()
        return ui.div(
            ui.p(ui.tags.b("Innovation: "), str(row.get("innovation", "N/A"))),
            ui.p(ui.tags.b("Disease: "), str(row.get("disease", "N/A"))),
            ui.p(ui.tags.b("Indication: "), str(row.get("indication", "N/A"))),
            ui.p(
                ui.tags.b("Target population: "),
                str(row.get("targeted_population", "N/A")),
            ),
            ui.p(ui.tags.b("Technology: "), str(row.get("technology", "N/A"))),
            ui.p(ui.tags.b("Stage: "), str(row.get("trial_status", "N/A"))),
        )

    @render_widget
    def timeline_plot():
        """
        Renders a timeline showing Collected (Trial) vs Projected (Launch) dates.
        """
        row = detail_row()

        # Prepare data for the timeline
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
        # Define paired real + projected dates

        # Define paired real + projected dates
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
                "real": None,  # no collected equivalent
                "proj": "proj_date_lmic_20_uptake",
            },
        ]
        for event in event_map:
            proj_col = event["proj"]
            real_col = event["real"]

            proj_date = row.get(proj_col) if proj_col in row.index else None
            real_date = row.get(real_col) if real_col and real_col in row.index else None

            if pd.notna(proj_date):
                event_type = (
                    "Collected"
                    if real_col and pd.notna(real_date)
                    else "Projection"
                )

                all_events.append(
                    {
                        "name": event["label"],
                        "date": proj_date,
                        "type": event_type,
                    }
                )

        # Part fixed 
        # Add Regulatory Approval as "Collected" - temporary solution
        # reg_date = row.get("proj_date_first_regulatory")
        # if pd.notna(reg_date):
        #     all_events.append(
        #         {"name": "Regulatory approval", "date": reg_date, "type": "Collected"}
        #     )

        # # Add other dates as "Projection"
        # projections = {
        #     # "Regulatory approval": row.get("proj_date_first_regulatory"),
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

        # Sort all events by date
        all_events.sort(key=lambda x: x["date"])

        dates = [e["date"] for e in all_events]
        names = [e["name"] for e in all_events]
        types = [e["type"] for e in all_events]
        colors = ["#00539B" if t == "Collected" else "#BFBBBB" for t in types]

        # Determine text positions (alternate)
        text_positions = []
        for i in range(len(dates)):
            text_positions.append("top center" if i % 2 == 0 else "bottom center")

        fig = go.FigureWidget()

        # Add trace for the timeline line
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
                hovertext=[
                    f"{n}<br>{d.strftime('%Y-%m-%d')}" for n, d in zip(names, dates)
                ],
                showlegend=False,
            )
        )

        # Add dummy traces for legend
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

        # Calculate range padding (1 year)
        start_range = min(dates) - pd.DateOffset(years=1)
        end_range = max(dates) + pd.DateOffset(years=1)

        # Update layout
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

    @render.ui
    def domain_summary_bars():
        row = detail_row()

        # Calculate summary scores for domains using real data
        impact_score = row.get("impact_potential", 0)
        intro_score = row.get("introduction_readiness", 0)

        return ui.div(
            progress_row("Impact potential", impact_score),
            progress_row("Introduction readiness", intro_score),
            class_="d-flex flex-column gap-3",
        )

    @render.ui
    def impact_potential_box():
        row = detail_row()

        # Aligned with goals - logic using probability of success or readiness
        align_val = row.get("readiness", 0)
        align_str = "Yes" if align_val > 50 else "No"

        # Determine the label for population (use description if available)
        pop_label = str(row.get("pop_description", "People at Risk"))
        if pop_label == "nan" or not pop_label:
            pop_label = "People at Risk"

        return ui.div(
            ui.div(
                format_value_box(
                    pop_label,
                    row.get("people_at_risk", 0),
                    is_percent=False,
                    check_threshold=False,
                ),
                class_="col-12 col-md-2",
            ),
            ui.div(
                format_value_box(
                    "DALYs",
                    row.get("dalys", 0),
                    is_percent=False,
                    check_threshold=False,
                ),
                class_="col-12 col-md-2",
            ),
            ui.div(
                format_value_box(
                    "Efficacy",
                    row.get("efficacy", "Not available"),
                    is_percent=False,
                    check_threshold=False,
                ),
                class_="col-12 col-md-2",
            ),
            class_="row g-3",
        )

    @render.ui
    def financing_box():
        row = detail_row()

        return ui.TagList(
            ui.div(
                format_value_box(
                    "Prob. of Success",
                    row.get("prob_success", 0),
                    check_threshold=False,
                    is_percent=True,
                ),
                class_="col-12 col-md-6",
            ),
            ui.div(
                format_value_box(
                    "Health System Costs (Million USD)",
                    row.get("hs_costs", 0),
                    display_text=str(row.get("financing", 0)),
                    is_percent=False,
                    check_threshold=False,
                ),
                class_="col-12 col-md-6",
            ),
        )

    @render.ui
    def uptake_delivery_box():
        row = detail_row()

        def format_date(d):
            if pd.notna(d):
                if hasattr(d, "strftime"):
                    return d.strftime("%Y-%m-%d")
                return str(d)
            return "N/A"

        return ui.TagList(
            ui.div(
                format_value_box(
                    "Projected Date of 20% Market Uptake",
                    format_date(row.get("proj_date_lmic_20_uptake")),
                    is_percent=False,
                    check_threshold=False,
                ),
                class_="col-12 col-md-3",
            ),
            ui.div(
                format_value_box(
                    "Supply Readiness",
                    row.get("country_supply", "N/A"),
                    is_percent=False,
                    check_threshold=False,
                ),
                class_="col-12 col-md-3",
            ),
            ui.div(
                format_value_box(
                    "Distribution",
                    row.get("distribution", "N/A"),
                    is_percent=False,
                    check_threshold=False,
                ),
                class_="col-12 col-md-3",
            ),
            ui.div(
                format_value_box(
                    "Delivery model",
                    row.get("delivery_model", "N/A"),
                    is_percent=False,
                    check_threshold=False,
                ),
                class_="col-12 col-md-3",
            ),
        )

    @render.ui
    def policy_box():
        row = detail_row()

        return ui.TagList(
            ui.div(
                format_value_box(
                    "National Approval", row.get("nra", "No"), is_percent=False
                ),
                class_="col-12 col-md-2",
            ),
            ui.div(
                format_value_box(
                    "Global Approval", row.get("gra", "No"), is_percent=False
                ),
                class_="col-12 col-md-2",
            ),
            ui.div(
                format_value_box("EML Listed", row.get("eml", "No"), is_percent=False),
                class_="col-12 col-md-2",
            ),
            ui.div(
                format_value_box(
                    "Policy Readiness",
                    row.get("policy_readiness", "N/A"),
                    is_percent=False,
                ),
                class_="col-12 col-md-2",
            ),
            ui.div(
                format_value_box(
                    "Policy Implemented",
                    row.get("policy_implemented", "No"),
                    is_percent=False,
                ),
                class_="col-12 col-md-2",
            ),
        )
