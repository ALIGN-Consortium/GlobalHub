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
                        output_widget("time_to_market_plot", height="auto"),
                        id="timeline_card_body",  
                        class_="card-body",
                    ),
                    class_="card mb-4",
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
        # currently not allowing the user to chose innovations without dates forecasted.
        choices = horizon_df[horizon_df["proj_date_lmic_20_uptake"].notna()]["innovation"].unique().tolist()
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
        df_filtered = horizon_df[horizon_df["scope"] == "WHO"][horizon_df["innovation"].isin(selected_ids)].assign(
            proj_date_lmic_20_uptake=lambda d: d["proj_date_lmic_20_uptake"].dt.strftime(
                "%Y-%m-%d"
            )
        )

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
            "Expected Market Date": "proj_date_lmic_20_uptake",
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

    # @reactive.Effect
    # def _adjust_timeline_height():
    #     selected = input.selected_innovations_compare()
    #     n = len(selected) if selected else 0

    #     # Base height
    #     base = 400

    #     # Add 60px per innovation
    #     dynamic_height = base + max(0, n - 5) * 60

    #     ui.update_ui(
    #         id="timeline_card_body",
    #         style=f"min-height: {dynamic_height}px;"
    #     )

    @render_widget(
        height=lambda: f"{max(400, 150 + len(input.selected_innovations_compare() or []) * 60)}px"
    )
    def time_to_market_plot():
        selected_ids = input.selected_innovations_compare()
        if not selected_ids:
            return go.Figure()

        # 1) Restrict to the canonical rows you want to plot
        # If WHO is your global row, keep this. If not, remove scope filter.
        base = horizon_df[horizon_df["scope"] == "WHO"].copy()

        fig = go.Figure()
        all_dates_flat = []

        # Colors represent DATA TYPE (collected vs projection)
        data_type_colors = {
            "Collected": "#00539B",
            "Projection": "#BFBBBB",
        }

        # Milestone mapping: plot proj_* but classify based on corresponding date_*
        # IMPORTANT: Only include columns that actually exist in your dataset.
        event_map = [
            # If you do NOT have proj_date_proof_of_concept, delete this block or map proj to date_proof_of_concept.
            {"label": "Proof of Concept", "real": "date_proof_of_concept", "proj": "date_proof_of_concept"},
            {"label": "Regulatory Approval",   "real": "date_first_regulatory",   "proj": "proj_date_first_regulatory"},
            {"label": "First Launch",          "real": "date_first_launch",       "proj": "proj_date_first_launch"},
            {"label": "Market Entry",          "real": None,                      "proj": "proj_date_lmic_20_uptake"},
        ]

        # 2) Iterate the selected innovations (NOT rows)
        for innovation in selected_ids:
            sub = base[base["innovation"] == innovation]

            if sub.empty:
                continue

            # 3) Choose the "best" row for this innovation (most milestone dates present)
            proj_cols = [e["proj"] for e in event_map if e["proj"] in sub.columns]
            if proj_cols:
                completeness = sub[proj_cols].notna().sum(axis=1)
                row = sub.loc[completeness.idxmax()]
            else:
                row = sub.iloc[0]

            events = []

            for event in event_map:
                proj_col = event["proj"]
                real_col = event["real"]

                # Skip if projected column doesn't exist at all
                if proj_col not in row.index:
                    continue

                proj_date = row.get(proj_col)
                real_date = row.get(real_col) if real_col and real_col in row.index else None

                if pd.notna(proj_date):
                    event_type = "Collected" if (real_col and pd.notna(real_date)) else "Projection"
                    events.append({"name": event["label"], "date": proj_date, "type": event_type})
                    all_dates_flat.append(proj_date)

            # If this innovation has no events, skip adding a trace
            if not events:
                continue

            events.sort(key=lambda x: x["date"])
            dates = [e["date"] for e in events]
            labels = [e["name"] for e in events]
            marker_colors = [data_type_colors[e["type"]] for e in events]

            fig.add_trace(
                go.Scatter(
                    x=dates,
                    y=[innovation] * len(dates),
                    mode="lines+markers+text",
                    line=dict(color="#000000", width=3),
                    marker=dict(size=12, color=marker_colors, line=dict(width=2, color="white")),
                    # text=labels,
                    textposition="top center",
                    hoverinfo="text+x+name",
                    hovertext=[f"{e['name']} ({e['type']})<br>{e['date'].strftime('%Y-%m-%d')}" for e in events],
                    showlegend=False,
                )
            )

        # Nothing to show
        if not all_dates_flat:
            fig.update_layout(
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                annotations=[dict(text="No timeline data available", showarrow=False, xref="paper", yref="paper", x=0.5, y=0.5)],
                height=300,
            )
            return fig

        # Legend for data type (Collected vs Projection)
        for name, color in data_type_colors.items():
            fig.add_trace(
                go.Scatter(
                    x=[None], y=[None],
                    mode="markers",
                    marker=dict(size=10, color=color),
                    name=name,
                )
            )

        # Axis ranges
        start_range = min(all_dates_flat) - pd.DateOffset(years=1)
        end_range = max(all_dates_flat) + pd.DateOffset(years=1)

        # Make sure all selected innovations appear on Y axis in selection order
        # Plotly's category axis uses categoryarray; reverse because autorange="reversed"
        fig.update_layout(
            height=max(400, 150 + (len(selected_ids) * 50)),
            showlegend=True,
            legend=dict(
                title=dict(text="Data Type", font=dict(size=12)),
                orientation="h",
                yanchor="bottom", y=1.02,
                xanchor="right", x=1,
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
                type="category",
                categoryorder="array",
                categoryarray=list(reversed(selected_ids)),
                autorange="reversed",
                showgrid=False,
            ),
            plot_bgcolor="white",
            paper_bgcolor="white",
        )

        fig.update_xaxes(
            automargin=True
        )

        fig.update_yaxes(
            automargin=True
        )

        return fig