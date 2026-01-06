from shiny import ui, reactive, req as shiny_req
from shiny.express import render
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from shinywidgets import output_widget, render_widget
from pyecharts import options as opts
from pyecharts.charts import Bar, Radar
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
                    ui.span("Comparison Table", class_="fw-semibold"),
                    class_="card-header",
                ),
                ui.div(ui.output_data_frame("comparison_table"), class_="card-body"),
                class_="card mb-4",
                min_height="300px",
            ),
        ),
        ui.div(
            ui.div(
                ui.div(
                    ui.div("Impact Potential Comparison", class_="card-header"),
                    ui.div(
                        ui.output_ui("comparison_plot"),
                        class_="card-body d-flex justify-content-center",
                    ),
                    class_="card h-100",
                ),
                class_="col-md-6",
            ),
            ui.div(
                ui.div(
                    ui.div("Time to Approval/Market", class_="card-header"),
                    ui.div(
                        output_widget("time_to_market_plot"),
                        class_="card-body d-flex justify-content-center",
                    ),
                    class_="card h-100",
                ),
                class_="col-md-6",
            ),
            class_="row g-4",
        ),
        id=id,
    )


def comparison_server(id, input, output, session):
    data = load_data()
    horizon_df = data["horizon"]
    impact_template = data["impact_template"]
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

    @render.data_frame
    def comparison_table():
        df = selected_innovations_data()
        if df.empty:
            return

        return render.DataGrid(
            df[["Innovation", "Disease", "Category", "Stage", "LeadOrg", "Country"]],
            row_selection_mode="none",
        )

    @render.ui
    def comparison_plot():
        selected_ids = input.selected_innovations_compare()
        if not selected_ids:
            return ui.p("Select one or more innovations to compare.")

        radar = Radar()
        # Removed radar.set_colors(colors)

        schema = [
            opts.RadarIndicatorItem(name=metric, max_=100)
            for metric in impact_template["metric"]
        ]
        radar.add_schema(schema)

        for i, sel in enumerate(selected_ids):
            imp = impact_template.copy()
            if sel in id_offsets:
                imp["value"] = (imp["value"] + id_offsets[sel]["impact"]).clip(0, 100)

            color = colors[i % len(colors)]  # Cycle through colors
            radar.add(
                sel,
                [imp["value"].tolist()],
                linestyle_opts=opts.LineStyleOpts(
                    color=color
                ),  # Explicitly set line color
                areastyle_opts=opts.AreaStyleOpts(
                    opacity=0.5, color=color
                ),  # Explicitly set area color
            )

        radar.set_global_opts(
            legend_opts=opts.LegendOpts(
                orient="vertical", pos_right="5%", pos_top="15%"
            ),
        )

        return ui.HTML(radar.render_embed())

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
