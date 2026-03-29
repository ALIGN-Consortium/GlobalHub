from shiny import ui, reactive, module, render, req as shiny_req
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from shinywidgets import output_widget, render_widget
from utils.data_loader import load_data


def req(condition):
    """
    Helper to stop execution if a condition is not met (similar to R Shiny's req).
    """
    if isinstance(condition, (pd.DataFrame, pd.Series)):
        if condition.empty:
            shiny_req(False)
        return
    elif not condition:
        shiny_req(False)


@module.ui
def comparison_ui():
    """
    Defines the User Interface for the Product Comparison module.
    """
    return ui.div(
        ui.div(
            ui.div(
                ui.div(
                        ui.h2("Product comparison", class_="mb-1"),
                    ui.p(
                        "Review and compare the products you added to your list.",
                        class_="text-muted",
                    ),
                    class_="col-md-8",
                ),
                ui.div(
                    ui.input_selectize(
                        "product_search_comp",
                        "Add more products:",
                        choices=[],  # Filled by server
                        multiple=True,
                        width="100%",
                    ),
                    ui.input_action_button(
                        "add_search_to_cart_comp",
                        ui.tags.span(
                            ui.tags.i(class_="fa-solid fa-plus me-1"), "Add to list"
                        ),
                        class_="btn btn-primary btn-sm w-100 mt-2",
                    ),
                    class_="col-md-4 card p-3",
                ),
                class_="row mb-4 align-items-center",
            ),
            ui.div(
                ui.div(
                    ui.div(
                        ui.span("Products in Your List", class_="fw-semibold"),
                        ui.input_action_button(
                            "remove_selected_from_cart_comp",
                            ui.tags.span(
                                ui.tags.i(class_="fa-solid fa-trash me-1"), "Remove from list"
                            ),
                            class_="btn btn-sm btn-outline-danger",
                        ),
                        class_="d-flex justify-content-between align-items-center w-100",
                    ),
                    class_="card-header",
                ),
                ui.div(
                    ui.output_data_frame("pipeline_compare"),
                    class_="card-body p-0",
                ),
                class_="card mb-4",
                style="min-height:350px;",
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
                    ui.div("Speedometer Introduction Milestone Tracking", class_="card-header"),
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
    )


@module.server
def comparison_server(input, output, session, cart):
    """
    Server logic for the Product Comparison module.
    """
    data = load_data()
    horizon_df = data["horizon"].copy()
    selected_comp_innovation = reactive.Value(None)

    def comparison_base_df():
        """
        Returns only products currently in the cart.
        """
        items = list(cart.get())
        out = horizon_df[horizon_df["innovation"].isin(items)].copy()

        return (
            out.loc[out["scope"] == "WHO"].copy().reset_index(drop=True)
        )


        # out = horizon_df[horizon_df["trial_status"] != "Phase 1"].copy()

        # # Removes empty time stamps or time stamps way too in the past
        # out = out[
        #     out["proj_date_lmic_20_uptake"].notna()
        #     & (out["proj_date_lmic_20_uptake"] >= pd.Timestamp("2025-01-01"))
        # ]
        # return (
        #     out.loc[out["scope"] == "WHO"].copy().reset_index(drop=True)
        # )

    def selected_rows_as_list():
        rows = input.pipeline_compare_selected_rows()

        if rows is None or rows == []:
            return []

        return np.atleast_1d(rows).tolist()

    @reactive.Calc
    def selected_innovation_ids():
        # In the new logic, all products in comparison_base_df (i.e. in cart) are compared
        base = comparison_base_df()
        if base.empty:
            return []
        return base["innovation"].tolist()

    @render.data_frame
    def pipeline_compare():
        df = comparison_base_df().assign(
            proj_date_first_launch=lambda d: pd.to_datetime(
                d["proj_date_first_launch"], errors="coerce"
            ).dt.strftime("%Y-%m-%d")
        )

        return render.DataGrid(
            df.rename(
                columns={
                    "innovation": "Product",
                    "disease": "Disease",
                    "trial_status": "Stage",
                    "proj_date_first_launch": "Projected launch",
                }
            )[["Product", "Disease", "Stage", "Projected launch"]],
            selection_mode="row",
            filters=False,
            summary=False,
            width="100%",
        )

    @reactive.Effect
    @reactive.event(input.pipeline_compare_selected_rows)
    def _on_row_select_comp():
        if not input.pipeline_compare_selected_rows():
            selected_comp_innovation.set(None)
            return

        idx = input.pipeline_compare_selected_rows()[0]
        df_f = comparison_base_df()
        if not df_f.empty and idx < len(df_f):
            selected_id = df_f.iloc[idx]["innovation"]
            selected_comp_innovation.set(selected_id)

    @reactive.Effect
    def _update_comp_search():
        all_products = sorted(horizon_df["innovation"].dropna().unique().tolist())
        ui.update_selectize(
            "product_search_comp",
            choices=all_products,
            selected=None,
            server=True
        )

    @reactive.Effect
    @reactive.event(input.add_search_to_cart_comp)
    def _add_search_to_cart_comp():
        searched = input.product_search_comp()
        if searched:
            current = cart.get()
            new_cart = current.copy()
            for prod in searched:
                new_cart.add(prod)
            cart.set(new_cart)
            ui.update_selectize("product_search_comp", selected=[])

    @reactive.Effect
    @reactive.event(input.remove_selected_from_cart_comp)
    def _remove_selected_from_cart_comp():
        selected_id = selected_comp_innovation.get()
        if selected_id:
            current = cart.get()
            if selected_id in current:
                new_cart = current.copy()
                new_cart.remove(selected_id)
                cart.set(new_cart)
                ui.notification_show(f"Removed {selected_id} from comparison list", type="message")
                selected_comp_innovation.set(None)
        else:
            ui.notification_show("Please select a product to remove from the list", type="warning")

    @reactive.Effect
    def _sync_selection():
        current_cart = cart.get()
        selected_id = selected_comp_innovation.get()
        if selected_id and selected_id not in current_cart:
            selected_comp_innovation.set(None)

    @reactive.Calc
    def selected_innovations_data():
        selected_ids = selected_innovation_ids()

        if not selected_ids:
            return pd.DataFrame()

        return horizon_df[horizon_df["innovation"].isin(selected_ids)].copy()

    @render.table
    def comparison_heatmap():
        selected_ids = selected_innovation_ids()

        if not selected_ids:
            return pd.DataFrame({"Message": ["Select products to compare"]})
        df_filtered = (
            horizon_df.loc[
                (horizon_df["scope"] == "WHO")
                & (horizon_df["innovation"].isin(selected_ids))
            ]
            .copy()
            .assign(
                proj_date_first_launch=lambda d: pd.to_datetime(
                    d["proj_date_first_launch"], errors="coerce"
                ).dt.strftime("%Y-%m-%d")
            )
        )

        metrics_map = {
            "Product": "innovation",
            "Disease": "disease",
            "Stage": "trial_status",
            "Projected first launch": "proj_date_first_launch",
            "Kenya market authorization": "Kenya_nra",
            "Senegal market authorization": "Senegal_nra",
            "South Africa market authorization": "South Africa_nra",
            "Global market authorization": "gra",
            "WHO EML listed": "eml",
        }

        compare_df = pd.DataFrame()
        for label, col in metrics_map.items():
            if col in df_filtered.columns:
                compare_df[label] = df_filtered[col].values
            else:
                compare_df[label] = "N/A"

        numeric_cols = [
            "Probability of Success",
            "Financing Score",
            "Readiness Score",
            "Efficacy",
        ]

        yes_no_cols = [
            "Kenya market authorization",
            "Senegal market authorization",
            "South Africa market authorization",
            "Global Mkt Authorization",
            "WHO EML listed",
        ]

        def color_cells(val):
            if pd.isna(val) or val == "N/A":
                return "background-color:#f8f9fa;color:#BFBBBB" # Neutral Gray

            if isinstance(val, str):
                v = val.strip().lower()

                if v == "yes":
                    return "background-color:rgba(34, 139, 34, 0.1);color:#228B22;font-weight:700" # Success Green

                if v == "no":
                    return "background-color:rgba(220, 20, 60, 0.1);color:#DC143C;font-weight:700" # Error Red

            try:
                v = float(val)

                if v <= 1:
                    return (
                        "background-color:rgba(34, 139, 34, 0.1);color:#228B22"
                        if v > 0.5
                        else "background-color:rgba(220, 20, 60, 0.1);color:#DC143C"
                    )
                elif v <= 2:
                    return (
                        "background-color:rgba(34, 139, 34, 0.1);color:#228B22"
                        if v > 1
                        else "background-color:rgba(220, 20, 60, 0.1);color:#DC143C"
                    )
                else:
                    return (
                        "background-color:rgba(34, 139, 34, 0.1);color:#228B22"
                        if v > 50
                        else "background-color:rgba(220, 20, 60, 0.1);color:#DC143C"
                    )
            except Exception:
                return ""

        cols_to_style = [
            c for c in numeric_cols + yes_no_cols if c in compare_df.columns
        ]

        styler = (
            compare_df.style.hide(axis="index")
            .set_table_attributes('class="table table-striped table-hover table-sm"')
            .set_properties(
                **{
                    "text-align": "center",
                    "vertical-align": "middle",
                    "font-size": "0.9rem",
                    "padding": "6px",
                }
            )
            .set_table_styles(
                [
                    {
                        "selector": "th",
                        "props": [
                            ("background-color", "#012169"),
                            ("color", "white"),
                            ("font-weight", "600"),
                            ("text-align", "center"),
                        ],
                    },
                    {
                        "selector": "td",
                        "props": [
                            ("border", "1px solid #dee2e6"),
                        ],
                    },
                ]
            )
        )

        if cols_to_style:
            if hasattr(styler, "map"):
                styler = styler.map(color_cells, subset=cols_to_style)
            else:
                styler = styler.applymap(color_cells, subset=cols_to_style)

        return styler.format(na_rep="—")

    @render_widget(
    height=lambda: f"{max(400, 150 + len(list(cart.get())) * 60)}px"
)
    def time_to_market_plot():
        selected_ids = selected_innovation_ids()

        if not selected_ids:
            fig = go.Figure()
            fig.update_layout(
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                annotations=[
                    dict(
                        text="Select products to compare",
                        showarrow=False,
                        xref="paper",
                        yref="paper",
                        x=0.5,
                        y=0.5,
                    )
                ],
                height=300,
                plot_bgcolor="white",
                paper_bgcolor="white",
            )
            return fig

        base = comparison_base_df()

        fig = go.Figure()
        all_dates_flat = []

        # Milestone colors
        event_colors = {
            "Proof of Concept": "#00539B",      # Accent Blue
            "Marketing Authorization": "#012169", # Primary Blue
            "First Country Launch": "#228B22",    # Success Green
            "20% Market Uptake": "#8b5cf6",
        }

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

        for innovation in selected_ids:
            sub = base[base["innovation"] == innovation]

            if sub.empty:
                continue

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

                if proj_col not in row.index:
                    continue

                proj_date = row.get(proj_col)
                real_date = (
                    row.get(real_col) if real_col and real_col in row.index else None
                )

                if pd.notna(proj_date):
                    event_type = (
                        "Actual"
                        if (real_col and pd.notna(real_date))
                        else "Projection"
                    )

                    events.append(
                        {
                            "name": event["label"],
                            "date": proj_date,
                            "type": event_type,
                        }
                    )

                    all_dates_flat.append(proj_date)

            if not events:
                continue

            events.sort(key=lambda x: x["date"])

            dates = [e["date"] for e in events]
            names = [e["name"] for e in events]
            marker_colors = [event_colors[e["name"]] for e in events]
            types = [e["type"] for e in events]

            fig.add_trace(
                go.Scatter(
                    x=dates,
                    y=[innovation] * len(dates),
                    mode="lines+markers",
                    line=dict(color="#000000", width=3),
                    marker=dict(
                        size=12,
                        color=marker_colors,
                        line=dict(width=2, color="white"),
                    ),
                    text=names,
                    customdata=types,
                    hovertemplate=(
                        "<b>%{text}</b><br>"
                        "Date: %{x|%Y-%m-%d}<br>"
                        "Source: %{customdata}<extra></extra>"
                    ),
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
                height=300,
                plot_bgcolor="white",
                paper_bgcolor="white",
            )
            return fig

        # Legend entries for milestones
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

        start_range = min(all_dates_flat) - pd.DateOffset(years=1)
        end_range = max(all_dates_flat) + pd.DateOffset(years=1)

        fig.update_layout(
            height=max(400, 150 + (len(selected_ids) * 50)),
            showlegend=True,
            legend=dict(
                title=dict(text="Milestones", font=dict(size=12)),
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
                type="category",
                categoryorder="array",
                categoryarray=list(reversed(selected_ids)),
                autorange="reversed",
                showgrid=False,
            ),
            plot_bgcolor="white",
            paper_bgcolor="white",
        )

        fig.update_xaxes(automargin=True)
        fig.update_yaxes(automargin=True)

        return fig