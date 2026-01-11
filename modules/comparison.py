from shiny import ui, reactive, req as shiny_req
from shiny.express import render
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from shinywidgets import output_widget, render_widget
from utils.data_loader import load_data


def req(condition):
    """
    Helper to stop execution if a condition is not met (similar to R Shiny's req).
    """
    import pandas as pd

    if isinstance(condition, (pd.DataFrame, pd.Series)):
        if condition.empty:
            shiny_req(False)
        return
    elif not condition:
        shiny_req(False)


def comparison_ui(id):
    """
    Defines the User Interface for the Product Comparison module.
    
    Layout:
    1. Innovation Selector: Selectize input for choosing multiple products.
    2. Impact & Readiness Heatmap: A comparison table with conditional formatting.
    3. Time to Approval/Market: A comparative horizontal timeline of milestones.
    """
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
    """
    Server logic for the Product Comparison module.
    
    Handles:
    - Populating the innovation selector with unique product names.
    - Generating a comparison table with color-coded heatmap logic.
    - Plotting a comparative timeline of product milestones.
    """
    data = load_data()
    horizon_df = data["horizon"]

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
        choices = horizon_df["innovation"].unique().tolist()
        ui.update_selectize("selected_innovations_compare", choices=choices)

    @reactive.Calc
    def selected_innovations_data():
        """
        Reactive calculation that returns the subset of horizon_df 
        containing only the innovations selected by the user.
        """
        selected_ids = input.selected_innovations_compare()
        if not selected_ids:
            return pd.DataFrame()
        return horizon_df[horizon_df["innovation"].isin(selected_ids)]

    @render.table
    def comparison_heatmap():
        """
        Renders the side-by-side comparison table.
        Applies color coding (Heatmap style) to numeric rows based on performance.
        """
        selected_ids = input.selected_innovations_compare()
        if not selected_ids:
            return pd.DataFrame({"Message": ["Select innovations to compare"]})

        # Filter the main dataframe for the selected innovations
        df_filtered = horizon_df[horizon_df["innovation"].isin(selected_ids)]

        # Define the metrics we want to compare using real data columns
        # Map Display Name -> Column Name
        metrics_map = {
            "Innovation": "innovation",
            "Disease": "disease",
            "Stage": "trial_status",
            "Probability of Success": "prob_success",
            "Financing Score": "financing",
            "Readiness Score": "readiness",
            "DALYs Averted": "dalys_averted",
            "Efficacy": "efficacy",
            "Expected Market Date": "expected_date_of_market",
            "Policy Implemented": "policy_implemented",
            "NRA Approved": "nra",
            "WHO PQ / Global": "gra",
        }

        # Create a new DataFrame with selected columns
        compare_df = pd.DataFrame()

        # Build DataFrame with Innovation as Rows (default from extraction)
        # Columns will be the Display Labels
        for label, col in metrics_map.items():
            if col in df_filtered.columns:
                compare_df[label] = df_filtered[col].values
            else:
                compare_df[label] = "N/A"

        # Styling function to restore heatmap look
        def color_cells(val):
            """Returns CSS styles based on the numeric value and type."""
            if pd.isna(val) or val == "N/A":
                return "background-color: #e9ecef; color: #6c757d"  # Gray for missing

            try:
                v = float(val)
                # Heuristic logic for coloring (Green for high performance, Red for low)
                if v <= 1.0:  # Probabilities
                    if v > 0.5:
                        return "background-color: #d1fae5; color: #065f46"
                    else:
                        return "background-color: #fee2e2; color: #991b1b"
                elif v <= 2.0:  # Financing score (0-2)
                    if v > 1:
                        return "background-color: #d1fae5; color: #065f46"
                    else:
                        return "background-color: #fee2e2; color: #991b1b"
                else:  # Scores 0-100 or Counts
                    if v > 50:
                        return "background-color: #d1fae5; color: #065f46"
                    else:
                        return "background-color: #fee2e2; color: #991b1b"
            except:
                return ""

        # Specify which columns to apply heatmap styling to
        numeric_cols = [
            "Probability of Success",
            "Financing Score",
            "Readiness Score",
            "Efficacy",
        ]

        # Apply styling using Pandas Styler
        styler = compare_df.style.hide(axis="index")
        cols_to_style = [c for c in numeric_cols if c in compare_df.columns]

        if hasattr(styler, "map"):
            styler = styler.map(color_cells, subset=cols_to_style)
        else:
            styler = styler.applymap(color_cells, subset=cols_to_style)

        return styler.format(precision=2, na_rep="N/A", subset=cols_to_style)

    @render_widget
    def time_to_market_plot():
        """
        Renders a Plotly horizontal timeline showing milestones for multiple selected products.
        """
        selected_ids = input.selected_innovations_compare()
        if not selected_ids:
            return go.FigureWidget()

        df_filtered = horizon_df[horizon_df["innovation"].isin(selected_ids)]

        fig = go.FigureWidget()
        all_dates_flat = []

        # Define color map for different milestone types
        milestone_colors = {
            "Trial": "#BFBBBB",          # Gray
            "Regulatory Approval": "#228B22", # Green
            "First Launch": "#DC143C",   # Red
            "Market Entry": "#00539B"    # Blue
        }

        for i, (idx, row) in enumerate(df_filtered.iterrows()):
            innovation = row["innovation"]
            events = []

            # Add Trial Milestone (Collected Data)
            trial_date = row.get("date_trial_status")
            if pd.notna(trial_date):
                stage = row.get("trial_status", "Trial")
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

            # Add Projected Milestones
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

                # Add scatter trace for this specific innovation
                fig.add_trace(
                    go.Scatter(
                        x=dates,
                        y=[innovation] * len(dates),
                        mode="lines+markers+text",
                        name=innovation,
                        line=dict(color="#00539B", width=3),
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
                    dict(text="No timeline data available", showarrow=False, xref="paper", yref="paper", x=0.5, y=0.5)
                ],
            )
            return fig

        # Add Custom Legend Items
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

        # Dynamic Height
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