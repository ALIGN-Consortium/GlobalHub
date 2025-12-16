from shiny import ui, reactive
from shiny.express import render
import pandas as pd
from utils.data_loader import load_data
from pyecharts import options as opts
from pyecharts.charts import Radar, Bar # Import Bar chart

def req(condition):
    import pandas as pd
    if isinstance(condition, pd.DataFrame):
        if condition.empty:
            raise StopIteration
    elif not condition:
        raise StopIteration

def comparison_ui(id):
    return ui.div(
        ui.h2("Product Comparison"),
        ui.p("Select multiple innovations to compare their key metrics."),
        ui.div(
            ui.input_selectize(
                "selected_innovations_compare",
                "Select Innovations to Compare",
                choices=[], # Will be populated dynamically
                multiple=True,
                width="100%",
            ),
            class_="mb-4"
        ),
        ui.div(
            ui.h3("Comparison Table"),
            ui.output_data_frame("comparison_table"),
            class_="mt-4"
        ),
        ui.div(
            ui.div(
                ui.div(
                    ui.h3("Impact Potential Comparison"),
                    ui.output_ui("comparison_plot"),
                    class_="card-body"
                ),
                class_="card col-md-6"
            ),
            ui.div(
                ui.div(
                    ui.h3("Time to Approval/Market"),
                    ui.output_ui("time_to_market_plot"),
                    class_="card-body"
                ),
                class_="card col-md-6"
            ),
            class_="row g-3 mt-4"
        ),
        id=id,
    )

def comparison_server(id, input, output, session):
    data = load_data()
    horizon_df = data["horizon"]
    impact_template = data["impact_template"]
    id_offsets = data["id_offsets"]

    # Define colors for the plots
    colors = ["#00539B", "#228B22", "#DC143C", "#FFD700", "#012169", "#BFBBBB"] # ALGIN colors

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
            
            color = colors[i % len(colors)] # Cycle through colors
            radar.add(
                sel,
                [imp["value"].tolist()],
                linestyle_opts=opts.LineStyleOpts(color=color), # Explicitly set line color
                areastyle_opts=opts.AreaStyleOpts(opacity=0.5, color=color) # Explicitly set area color
            )

        radar.set_global_opts(
            legend_opts=opts.LegendOpts(orient="vertical", pos_right="5%", pos_top="15%"),
        )
        
        return ui.HTML(radar.render_embed())

    @render.ui
    def time_to_market_plot():
        selected_ids = input.selected_innovations_compare()
        if not selected_ids:
            return ui.p("Select one or more innovations to compare.")

        df = horizon_df[horizon_df["Innovation"].isin(selected_ids)]
        
        bar = (
            Bar()
            .add_xaxis(df["Innovation"].tolist())
            .add_yaxis("Time to Approval (Years)", df["Time_to_Approval"].tolist())
            .add_yaxis("Time to Market (Years)", df["Time_to_Market"].tolist())
            .set_global_opts(
                # Removed title_opts as it's redundant with card header
                legend_opts=opts.LegendOpts(pos_right="10%"),
                yaxis_opts=opts.AxisOpts(name="Years"),
                xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=-15)),
            )
        )
        return ui.HTML(bar.render_embed())
