from shiny import ui, reactive, req as shiny_req
from shiny.express import render
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from shinywidgets import output_widget, render_widget
from utils.data_loader import load_data


def req(condition):
    import pandas as pd

    if isinstance(condition, (pd.DataFrame, pd.Series)):
        if condition.empty:
            shiny_req(False)
        return
    elif not condition:
        shiny_req(False)


def comparison_ui(id):
    return ui.div(
        ui.div(
            ui.h2("Product Comparison", class_="mb-1"),
            ui.p(
                "Select multiple innovations to compare their key metrics.",
                class_="text-muted",
            ),
            ui.div(
                ui.input_selectize(
                    "selected_innovations_compare",
                    "Select Innovations to Compare",
                    choices=[],  # Will be populated dynamically
                    multiple=True,
                    width="100%",
                ),
                class_="card p-3 shadow-sm bg-light border-0 mb-4",
            ),
            class_="mb-4",
        ),
        ui.div(
            ui.div(
                ui.div(
                    ui.span("Impact & Readiness Heatmap", class_="fw-semibold"),
                    class_="card-header",
                ),
                ui.div(
                    ui.output_table("comparison_heatmap"),
                    class_="card-body d-flex justify-content-center overflow-auto",
                ),
                class_="card mb-4",
                min_height="500px",
            ),
        ),
        ui.div(
            ui.div(
                ui.div(
                    ui.div("Time to Approval/Market", class_="card-header"),
                    ui.div(
                        output_widget("time_to_market_plot"),
                        class_="card-body d-flex justify-content-center",
                    ),
                    class_="card h-100",
                ),
                class_="col-12",
            ),
            class_="row g-4",
        ),
        id=id,
    )


def comparison_server(id, input, output, session):
    data = load_data()
    horizon_df = data["horizon"]
    id_offsets = data["id_offsets"]

    # Define colors for the plots
    colors = [
        "#00539B",
        "#228B22",
        "#DC143C",
        "#FFD700",
        "#012169",
        "#BFBBBB",
    ]  # ALGIN colors

    # Populate selectize input choices
    @reactive.Effect
    def _():
        choices = horizon_df["Innovation"].unique().tolist()
        ui.update_selectize("selected_innovations_compare", choices=choices)

    @reactive.Calc
    def selected_innovations_data():
        selected_ids = input.selected_innovations_compare()
        if not selected_ids:
            return pd.DataFrame()
        return horizon_df[horizon_df["Innovation"].isin(selected_ids)]

    @render.table
    def comparison_heatmap():
        selected_ids = input.selected_innovations_compare()
        if not selected_ids:
            return pd.DataFrame({"Message": ["Select innovations to compare"]})

        # Load templates
        data = load_data()
        impact_template = data["impact_template"]
        intro_template = data["intro_template"]
        id_offsets = data["id_offsets"]

        # Prepare columns and filter out specific ones
        all_metrics = list(impact_template["metric"]) + list(intro_template["metric"])
        exclude = [
            "Cost-effectiveness",
            "Procurement model",
            "Policy Readiness",
            "Social context",
            "Guidelines and training",
            "Potential supply chain",
        ]
        metrics = [m for m in all_metrics if m not in exclude]

        # Build Data Rows
        rows = []
        for pid in selected_ids:
            row_data = {"Innovation": pid}
            offsets = id_offsets.get(pid, {})

            # Impact Scores
            imp_df = impact_template.copy()
            imp_vals = imp_df["value"].values
            if "impact" in offsets:
                imp_vals = (imp_vals + offsets["impact"]).clip(0, 100)
            imp_missing = offsets.get("impact_missing", [False] * len(imp_vals))
            imp_vals = [np.nan if m else v for v, m in zip(imp_vals, imp_missing)]

            # Map impact metrics to row
            for m, v in zip(impact_template["metric"], imp_vals):
                if m in metrics:
                    row_data[m] = v

            # Intro Scores
            intro_df = intro_template.copy()
            intro_vals = intro_df["value"].values
            if "intro_delta" in offsets:
                intro_vals = (intro_vals + offsets["intro_delta"]).clip(0, 100)
            intro_missing = offsets.get("intro_missing", [False] * len(intro_vals))
            intro_vals = [np.nan if m else v for v, m in zip(intro_vals, intro_missing)]

            # Map intro metrics to row
            for m, v in zip(intro_template["metric"], intro_vals):
                if m in metrics:
                    row_data[m] = v

            rows.append(row_data)

        df = pd.DataFrame(rows)

        # Styling function
        def color_cells(val):
            if pd.isna(val):
                return "background-color: #e9ecef; color: #6c757d"  # Gray
            try:
                v = float(val)
                if v > 51:
                    return "background-color: #d1fae5; color: #065f46"  # Green
                else:
                    return "background-color: #fee2e2; color: #991b1b"  # Red
            except:
                return ""

        # Apply styling and hide index
        styler = df.style.hide(axis="index")

        if hasattr(styler, "map"):
            styler = styler.map(color_cells, subset=metrics)
        else:
            styler = styler.applymap(color_cells, subset=metrics)

        return styler.format(precision=0, na_rep="N/A", subset=metrics)

    @render_widget
    def time_to_market_plot():
        selected_ids = input.selected_innovations_compare()
        if not selected_ids:
            return go.FigureWidget()

        df = horizon_df[horizon_df["Innovation"].isin(selected_ids)]

        fig = go.FigureWidget()

        # Collect all dates to set range
        all_dates_flat = []

        # Define color map for milestones
        milestone_colors = {
            "Trial": "#BFBBBB",  # Gray
            "Regulatory Approval": "#228B22",  # Green
            "First Launch": "#DC143C",  # Red
            "Market Entry": "#00539B",  # Blue
        }

        for i, (idx, row) in enumerate(df.iterrows()):
            innovation = row["Innovation"]

            events = []

            # Trial Completion
            trial_date = row.get("trial_completion_date")
            if pd.notna(trial_date):
                stage = row.get("Stage", "Trial")
                label = (
                    f"{stage} Complete"
                    if "Phase" in str(stage)
                    else f"{stage} (Trial End)"
                )
                events.append(
                    {
                        "name": label,
                        "date": trial_date,
                        "type": "Trial",
                        "show_label": True,
                    }
                )
                all_dates_flat.append(trial_date)

            # Projections
            projs = {
                "Regulatory Approval": row.get("expected_date_of_regulatory_approval"),
                "First Launch": row.get("expected_date_of_first_launch"),
                "Market Entry": row.get("expected_date_of_market"),
            }
            for k, v in projs.items():
                if pd.notna(v):
                    events.append(
                        {"name": k, "date": v, "type": k, "show_label": False}
                    )
                    all_dates_flat.append(v)

            if events:
                events.sort(key=lambda x: x["date"])

                dates = [e["date"] for e in events]
                names = [e["name"] if e["show_label"] else "" for e in events]
                marker_colors = [
                    milestone_colors.get(e["type"], "#00539B") for e in events
                ]

                # Add trace
                fig.add_trace(
                    go.Scatter(
                        x=dates,
                        y=[innovation] * len(dates),
                        mode="lines+markers+text",
                        name=innovation,
                        line=dict(color="#00539B", width=3),  # Line always Blue
                        marker=dict(
                            size=12,
                            color=marker_colors,
                            line=dict(width=2, color="white"),
                        ),
                        text=names,
                        textposition="top center",
                        hoverinfo="text+x+name",
                        hovertext=[
                            f"{e['name']}<br>{e['date'].strftime('%Y-%m-%d')}"
                            for e in events
                        ],
                        showlegend=False,
                    )
                )

        if not all_dates_flat:
            fig.update_layout(
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                annotations=[
                    dict(
                        text="No timeline data available",
                        showarrow=False,
                        xref="paper",
                        yref="paper",
                        x=0.5,
                        y=0.5,
                    )
                ],
            )
            return fig

        # Add Legend Items
        for name, color in milestone_colors.items():
            label = "Trial (Collected)" if name == "Trial" else name
            fig.add_trace(
                go.Scatter(
                    x=[None],
                    y=[None],
                    mode="markers",
                    marker=dict(size=10, color=color),
                    name=label,
                )
            )

        # Padding (1 year)
        start_range = min(all_dates_flat) - pd.DateOffset(years=1)
        end_range = max(all_dates_flat) + pd.DateOffset(years=1)

        # Calculate dynamic height based on number of innovations
        num_innovations = len(selected_ids)
        dynamic_height = max(400, 150 + (num_innovations * 50))

        fig.update_layout(
            height=dynamic_height,
            showlegend=True,
            legend=dict(
                title=dict(text="Milestone Type", font=dict(size=12)),
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
            ),
            margin=dict(l=20, r=20, t=50, b=50),
            xaxis=dict(
                type="date",
                range=[start_range, end_range],
                showgrid=True,
                gridcolor="#f0f0f0",
                zeroline=False,
                linecolor="#BFBBBB",
                tickformat="%Y",
                side="bottom",
            ),
            yaxis=dict(
                showgrid=False,
                linecolor="#BFBBBB",
                type="category",
                autorange="reversed",
            ),
            plot_bgcolor="white",
            paper_bgcolor="white",
        )

        return fig
