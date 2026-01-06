from shiny import ui, reactive
from shiny.express import render
import plotly.graph_objects as go
import pandas as pd
from utils.data_loader import load_data
from shinywidgets import output_widget, render_widget
from pyecharts import options as opts
from pyecharts.charts import Bar, Line


def req(condition):
    import pandas as pd

    if isinstance(condition, pd.DataFrame):
        if condition.empty:
            raise StopIteration
    elif not condition:
        raise StopIteration


def overview_ui(id):
    data = load_data()
    horizon_df = data["horizon"]
    diseases = ["Overall"] + sorted(horizon_df["Disease"].dropna().unique().tolist())

    # Helper function to create KPI cards
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

    # Calculate counts for specific diseases
    def count_innovations(diseases):
        if isinstance(diseases, str):
            diseases = [diseases]
        # Filter by Disease column, not Category
        return len(
            horizon_df[horizon_df["Disease"].isin(diseases)]["Innovation"].unique()
        )

    tb_count = count_innovations(["tuberculosis"])
    hiv_count = count_innovations(["hiv"])
    malaria_count = count_innovations(["malaria", "malaria_copy"])
    mnch_count = count_innovations(["MCNH"])

    return ui.div(
        # KPI cards
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
        # Overview charts controls
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
        # Overview charts
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
        # Analytics tabs
        ui.div(
            ui.div(
                ui.div(
                    ui.span("Analytics", class_="fw-semibold"),
                    ui.input_select(
                        "impact_country",
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
                ui.div(
                    ui.div(
                        ui.div(
                            ui.div(
                                "Innovation Impact by Category", class_="card-header"
                            ),
                            ui.div(
                                ui.tags.div(
                                    "Potential population impact and cost effectiveness",
                                    style="font-weight:400; font-size:13px; color:#6b7280;",
                                ),
                                ui.output_ui("impact_combo", height="300px"),
                                class_="card-body",
                            ),
                            class_="card",
                        ),
                        class_="col-md-7",
                    ),
                    ui.div(
                        ui.div(
                            ui.div("Implementation Readiness", class_="card-header"),
                            ui.div(
                                ui.tags.div(
                                    "Innovations ready for policy implementation",
                                    style="font-weight:400; font-size:13px; color:#6b7280;",
                                ),
                                ui.output_ui("readiness_bar", height="300px"),
                                class_="card-body",
                            ),
                            class_="card",
                        ),
                        class_="col-md-5",
                    ),
                    class_="row mt-3 analytics-row g-3",
                ),
            ),
            class_="card",
            min_height="500px",
        ),
        # Innovation Explorer table
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
    data = load_data()
    pipeline_static = data["pipeline"]
    readiness_static = data["readiness"]
    impact_dat_all = data["impact_dat_all"]
    readiness_cat_all = data["readiness_cat_all"]
    horizon_df = data["horizon"]

    default_innovation_id = (
        horizon_df["Innovation"].iloc[0] if not horizon_df.empty else None
    )
    selected_innovation = reactive.Value(default_innovation_id)

    @render_widget
    def trend_chart():
        disease = input.disease_selector()

        # Calculate pipeline data dynamically based on selection
        if disease == "Overall":
            df_filtered = horizon_df
        else:
            df_filtered = horizon_df[horizon_df["Disease"] == disease]

        # Filter for Forecast period (2025 and above) and cap at 2050
        df_filtered = df_filtered[
            (df_filtered["market_year"] >= 2025) & (df_filtered["market_year"] <= 2050)
        ]

        if df_filtered.empty:
            # Return empty chart if no data
            return go.FigureWidget()

        # Aggregate counts by Year and Category
        pipeline_raw = (
            df_filtered.groupby(["market_year", "Category"])
            .size()
            .unstack(fill_value=0)
        )

        # Ensure we have a reasonable year range
        min_year = 2025
        max_year = (
            int(pipeline_raw.index.max())
            if not pipeline_raw.empty and not pd.isna(pipeline_raw.index.max())
            else 2035
        )
        # Cap max_year for display if data goes beyond, though we filtered already
        max_year = min(max_year, 2050)
        all_years = range(min_year, max_year + 1)

        if not pipeline_raw.empty:
            pipeline_raw.index = pipeline_raw.index.astype(int)

        pipeline_reindexed = pipeline_raw.reindex(all_years, fill_value=0)
        pipeline = pipeline_reindexed.cumsum().reset_index()
        pipeline = pipeline.rename(columns={"index": "year", "market_year": "year"})

        df = pipeline.melt(id_vars="year", var_name="category", value_name="count")
        req(not df.empty)

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
            yaxis=dict(
                range=[0, None], fixedrange=True
            ),  # Ensure Y-axis starts at 0 and prevent zooming below it
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
        disease = input.disease_selector()

        if disease == "Overall":
            df_filtered = horizon_df
        else:
            df_filtered = horizon_df[horizon_df["Disease"] == disease]

        if df_filtered.empty:
            return go.FigureWidget()

        stage_counts = df_filtered["Stage"].value_counts().reset_index()
        stage_counts.columns = ["status", "count"]
        total_innovations = len(df_filtered)
        stage_counts["pct"] = (stage_counts["count"] / total_innovations * 100).round(1)

        # Use consistent colors if possible
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

    @render.ui
    def impact_combo():
        country_data = impact_dat_all[
            impact_dat_all["country"] == input.impact_country()
        ]
        req(not country_data.empty)

        # Ensure no duplicates
        country_data = country_data.drop_duplicates(subset=["category"])

        # Round impact and cost_eff values before plotting
        rounded_impact = country_data["impact"].round(0).tolist()
        rounded_cost_eff = country_data["cost_eff"].round(0).tolist()

        bar = (
            Bar(init_opts=opts.InitOpts(width="100%", height="300px"))
            .add_xaxis(country_data["category"].tolist())
            .add_yaxis(
                "Impact",
                rounded_impact,
                itemstyle_opts=opts.ItemStyleOpts(color="#00539B"),
            )
            .extend_axis(
                yaxis=opts.AxisOpts(
                    name="Cost effectiveness",
                    type_="value",
                )
            )
            .set_global_opts(
                tooltip_opts=opts.TooltipOpts(
                    trigger="axis", axis_pointer_type="cross"
                ),
                xaxis_opts=opts.AxisOpts(type_="category"),
                yaxis_opts=opts.AxisOpts(name="Impact index"),
                legend_opts=opts.LegendOpts(pos_right="10%"),
            )
        )
        line = (
            Line()
            .add_xaxis(country_data["category"].tolist())
            .add_yaxis(
                "Cost effectiveness",
                rounded_cost_eff,
                yaxis_index=1,
                is_smooth=True,
                itemstyle_opts=opts.ItemStyleOpts(color="#228B22"),
            )
        )
        bar.overlap(line)
        return ui.HTML(bar.render_embed())

    @render.ui
    def readiness_bar():
        country_data = readiness_cat_all[
            readiness_cat_all["country"] == input.impact_country()
        ]
        req(not country_data.empty)

        # Ensure no duplicates
        country_data = country_data.drop_duplicates(subset=["category"])

        bar = (
            Bar(init_opts=opts.InitOpts(width="100%", height="300px"))
            .add_xaxis(country_data["category"].tolist())
            .add_yaxis(
                "Total in pipeline",
                country_data["total"].tolist(),
                itemstyle_opts=opts.ItemStyleOpts(color="#BFBBBB"),
            )
            .add_yaxis(
                "Ready",
                country_data["ready"].tolist(),
                z=10,
                itemstyle_opts=opts.ItemStyleOpts(color="#228B22"),
            )
            .set_global_opts(
                tooltip_opts=opts.TooltipOpts(trigger="axis"),
                legend_opts=opts.LegendOpts(pos_right="10%"),
            )
        )
        return ui.HTML(bar.render_embed())

    @render.ui
    def budget_chart():
        budget_df = data["budget_data"]
        req(not budget_df.empty)

        bar = (
            Bar()
            .add_xaxis(budget_df["category"].tolist())
            .add_yaxis(
                "Allocated (M)", budget_df["allocated"].round(0).astype(int).tolist()
            )
            .add_yaxis("Spent (M)", budget_df["spent"].round(0).astype(int).tolist())
            .set_global_opts(
                title_opts=opts.TitleOpts(title="Budget Allocation and Spending"),
                tooltip_opts=opts.TooltipOpts(
                    trigger="axis", axis_pointer_type="shadow"
                ),
                xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=-15)),
                yaxis_opts=opts.AxisOpts(name="Amount (Millions USD)"),
                legend_opts=opts.LegendOpts(pos_right="10%"),
            )
        )
        return ui.HTML(bar.render_embed())

    @render.ui
    def implementation_chart():
        impl_df = data["implementation_data"]
        req(not impl_df.empty)

        bar = (
            Bar()
            .add_xaxis(impl_df["category"].tolist())
            .add_yaxis(
                "Planned",
                impl_df["planned"].round(0).astype(int).tolist(),
                stack="stack1",
            )
            .add_yaxis(
                "In Progress",
                impl_df["in_progress"].round(0).astype(int).tolist(),
                stack="stack1",
            )
            .add_yaxis(
                "Completed",
                impl_df["completed"].round(0).astype(int).tolist(),
                stack="stack1",
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(title="Implementation Status by Category"),
                tooltip_opts=opts.TooltipOpts(
                    trigger="axis", axis_pointer_type="shadow"
                ),
                xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=-15)),
                yaxis_opts=opts.AxisOpts(name="Number of Items"),
                legend_opts=opts.LegendOpts(pos_right="10%"),
            )
        )
        return ui.HTML(bar.render_embed())

    @render.ui
    def risk_chart():
        risk_df = data["risk_data"]
        req(not risk_df.empty)

        categories = risk_df["category"].tolist()
        technical_risk = risk_df["technical_risk"].round(0).astype(int).tolist()
        market_risk = risk_df["market_risk"].round(0).astype(int).tolist()
        regulatory_risk = risk_df["regulatory_risk"].round(0).astype(int).tolist()
        financial_risk = risk_df["financial_risk"].round(0).astype(int).tolist()

        bar = (
            Bar()
            .add_xaxis(categories)
            .add_yaxis("Technical Risk", technical_risk)
            .add_yaxis("Market Risk", market_risk)
            .add_yaxis("Regulatory Risk", regulatory_risk)
            .add_yaxis("Financial Risk", financial_risk)
            .set_global_opts(
                title_opts=opts.TitleOpts(title="Risk Assessment by Category"),
                tooltip_opts=opts.TooltipOpts(
                    trigger="axis", axis_pointer_type="shadow"
                ),
                xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=-15)),
                yaxis_opts=opts.AxisOpts(name="Risk Score (1-10)"),
                legend_opts=opts.LegendOpts(pos_right="10%"),
            )
        )
        return ui.HTML(bar.render_embed())

    @render.ui
    def country_readiness_chart():
        cr_df = data["country_readiness_data"]
        req(not cr_df.empty)

        countries = cr_df["country"].tolist()
        policy_readiness = cr_df["policy_readiness"].round(0).astype(int).tolist()
        infra_readiness = cr_df["infra_readiness"].round(0).astype(int).tolist()
        uptake_potential = cr_df["uptake_potential"].round(0).astype(int).tolist()

        bar = (
            Bar()
            .add_xaxis(countries)
            .add_yaxis("Policy Readiness", policy_readiness)
            .add_yaxis("Infrastructure Readiness", infra_readiness)
            .add_yaxis("Uptake Potential", uptake_potential)
            .set_global_opts(
                title_opts=opts.TitleOpts(title="Country Readiness Scores"),
                tooltip_opts=opts.TooltipOpts(
                    trigger="axis", axis_pointer_type="shadow"
                ),
                xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=-15)),
                yaxis_opts=opts.AxisOpts(name="Readiness Score (%)"),
                legend_opts=opts.LegendOpts(pos_right="10%"),
            )
        )
        return ui.HTML(bar.render_embed())

    @render.data_frame
    def pipeline_tbl():
        country = input.impact_country_table()
        if country == "Overall":
            df = horizon_df
        else:
            df = horizon_df[horizon_df["Country"] == country]
        req(not df.empty)

        return render.DataGrid(
            df[["Innovation", "Disease", "Category", "Stage", "LeadOrg"]],
            selection_mode="row",
            width="100%",
            filters=True,
        )

    @reactive.Effect
    @reactive.event(input.pipeline_tbl_selected_rows)
    def _():
        if not input.pipeline_tbl_selected_rows():
            return
        idx = input.pipeline_tbl_selected_rows()[0]

        country = input.impact_country_table()
        if country == "Overall":
            df = horizon_df
        else:
            df = horizon_df[horizon_df["Country"] == country]

        selected_id = df.iloc[idx]["Innovation"]
        selected_innovation.set(selected_id)
        ui.update_navset("main_nav", "Innovation Details")

    return selected_innovation
