from shiny import ui, reactive
from shiny.express import render
import pandas as pd
from utils.data_loader import load_data
from shiny.express import render

def req(condition):
    import pandas as pd
    if isinstance(condition, (pd.DataFrame, pd.Series)):
        if condition.empty:
            raise StopIteration
    elif not condition:
        raise StopIteration

# Helper functions
def mini_bar(label, value):
    return ui.div(
        ui.div(
            ui.span(label, class_="mini-label"),
            ui.span(f"{int(value)}%", class_="mini-pct"),
            class_="d-flex justify-content-between align-items-center mb-1",
        ),
        ui.div(
            ui.div(class_="mini-fill", style=f"width: {int(value)}%"),
            class_="mini-track",
            role="progressbar",
            aria_valuenow=str(int(value)),
            aria_valuemin="0",
            aria_valuemax="100",
        ),
        class_="mini-row",
    )

def progress_row(label, value):
    return ui.div(
        ui.div(
            ui.span(label, class_="lbl"),
            ui.span(f"{int(value)}%"),
            class_="d-flex justify-content-between",
        ),
        ui.div(
            ui.div(
                class_="progress-bar",
                role="progressbar",
                style=f"width: {int(value)}%",
                aria_valuenow=str(int(value)),
                aria_valuemin="0",
                aria_valuemax="100",
            ),
            class_="progress",
        ),
        class_="readiness-row",
    )

def indicator_row(label, value):
    icon_class = "fa-solid fa-circle-check yes" if value else "fa-solid fa-circle-xmark no"
    return ui.div(
        ui.tags.i(class_=icon_class),
        ui.span(label, class_="indicator-label"),
        class_="indicator-row",
    )

def indicator_list(labels, values):
    rows = [indicator_row(l, v) for l, v in zip(labels, values)]
    return ui.div(rows, class_="indicator-card")

def intro_subdomain_section(title, df):
    n_checked = df["passed"].sum() # Use the new 'passed' column
    n_total = len(df)
    return ui.div(
        ui.div(
            ui.h5(title, class_="mb-0 fw-bold"),
            ui.span(f"{n_checked}/{n_total}", class_="badge-round"), # Display n_checked/n_total
            class_="subdomain-title d-flex align-items-center justify-content-between",
        ),
        indicator_list(df["metric"], df["passed"]), # Pass 'passed' to indicator_list
        class_="subdomain-block",
    )

def innovation_details_ui(id):
    return ui.div(
        # Innovation Explorer table
        ui.div(
            ui.div(
                ui.div(
                    ui.span("Innovation Explorer", class_="fw-semibold"),
                    ui.input_select("impact_country_table_details", None, choices=["Overall", "Kenya", "Senegal", "South Africa"], selected="Overall", width="220px"),
                    class_="d-flex align-items-center justify-content-between flex-wrap gap-2",
                ),
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
                    ui.div("Overall Domain Readiness", class_="card-header"),
                    ui.div(ui.output_ui("domain_summary_bars"), class_="card-body"),
                    class_="card",
                ),
                class_="col-12 col-lg-4 position-sticky",
                style="top: 1rem;",
            ),
            # Right column
            ui.div(
                ui.div(
                    ui.div("Scores within selected domain", class_="card-header"),
                    ui.div(
                        ui.navset_pill(
                            ui.nav_panel("Impact potential", value="impact"),
                            ui.nav_panel("Introduction readiness", value="intro_readiness"),
                            id="domain_tabs",
                        ),
                        ui.div(ui.output_ui("domain_bars"), class_="mt-3"),
                        class_="card-body",
                    ),
                    class_="card",
                ),
                class_="col-12 col-lg-8",
            ),
            class_="row g-4 align-items-start g-3",
        ),
        # Key Indicators
        ui.tags.hr(),
        ui.div(
            ui.div(
                ui.div(
                    ui.span("Key Indicators", class_="fw-semibold"),
                    ui.input_select("impact_country_KPIs", None, choices=["Overall", "Kenya", "Senegal", "South Africa"], selected="Overall", width="220px"),
                    class_="d-flex align-items-center justify-content-between flex-wrap gap-2",
                ),
                class_="card-header",
            ),
            ui.div(
                ui.div(
                    ui.div(ui.output_ui("kpi_box"), class_="col-12"),
                    class_="row g-3",
                ),
                class_="card-body",
            ),
            class_="card",
            min_height="600px",
        ),
        id=id,
    )

def innovation_details_server(id, selected_innovation, input, output, session):
    data = load_data()
    horizon_df = data["horizon"]
    impact_template = data["impact_template"]
    intro_template = data["intro_template"]
    id_offsets = data["id_offsets"]

    @render.data_frame
    def pipeline_tbl_details():
        country = input.impact_country_table_details()
        if country == "Overall":
            df = horizon_df
        else:
            df = horizon_df[horizon_df["Country"] == country]
        req(not df.empty)

        return render.DataGrid(
            df[["Innovation", "Disease", "Category", "Stage", "LeadOrg", "Country"]],
            selection_mode="row",
            width="100%",
            filters=True,
        )

    @reactive.Effect
    @reactive.event(input.pipeline_tbl_details_selected_rows)
    def _():
        if not input.pipeline_tbl_details_selected_rows():
            return
        idx = input.pipeline_tbl_details_selected_rows()[0]
        
        country = input.impact_country_table_details()
        if country == "Overall":
            df = horizon_df
        else:
            df = horizon_df[horizon_df["Country"] == country]

        selected_id = df.iloc[idx]["Innovation"]
        selected_innovation.set(selected_id)

    @reactive.Calc
    def get_selected_id():
        return selected_innovation()

    @reactive.Calc
    def detail_row():
        selected_id = get_selected_id()
        req(selected_id) # Ensure selected_id is not None
        row = horizon_df[horizon_df["Innovation"] == selected_id]
        req(not row.empty) # Ensure row is not empty
        return row.iloc[0]

    @reactive.Calc
    def scores_for_id():
        sel = get_selected_id()
        req(sel) # Ensure sel is not None
        
        # Impact scores
        imp = impact_template.copy()
        if sel in id_offsets:
            imp["value"] = (imp["value"] + id_offsets[sel]["impact"]).clip(0, 100)
            imp["passed"] = id_offsets[sel]["impact_passed"]
        req(not imp.empty) # Ensure imp is not empty

        # Intro scores
        intro = intro_template.copy()
        if sel in id_offsets:
            intro["value"] = (intro["value"] + id_offsets[sel]["intro_delta"]).clip(0, 100)
            intro["passed"] = intro["passed"] ^ id_offsets[sel]["intro_passed_delta"] # Apply XOR for boolean changes
        req(not intro.empty) # Ensure intro is not empty
            
        return {"impact": imp, "intro": intro}

    @render.text
    def detail_title():
        row = detail_row()
        req(row) # Ensure row is not None
        return row["Innovation"]

    @render.ui
    def detail_summary():
        row = detail_row()
        req(row) # Ensure row is not None
        return ui.div(
            ui.p(ui.tags.b("Innovation: "), row["Innovation"]),
            ui.p(ui.tags.b("Disease(s): "), row["Disease"]),
            ui.p(ui.tags.b("Target Population: "), row["TargetPop"]),
            ui.p(ui.tags.b("Lead Organization: "), row["LeadOrg"]),
        )

    @render.ui
    def domain_summary_bars():
        scores = scores_for_id()
        req(scores) # Ensure scores is not None

        labels = {
            "impact": "Impact Potential",
            "intro": "Introduction Readiness",
        }
        
        vals = {
            "impact": scores["impact"]["value"].mean(),
            "intro": (scores["intro"]["passed"].sum() / len(scores["intro"])) * 100,
        }

        df = pd.DataFrame({
            "label": labels.values(),
            "value": [round(v) for v in vals.values()]
        })
        req(not df.empty) # Ensure df is not empty

        return ui.div(
            *[mini_bar(row["label"], row["value"]) for index, row in df.iterrows()],
            class_="domain-summary-vertical"
        )

    @render.ui
    def domain_bars():
        scores = scores_for_id()
        req(scores) # Ensure scores is not None

        domain = input.domain_tabs()
        req(domain) # Ensure domain is not None
        if domain == "impact":
            df = scores["impact"]
            req(not df.empty) # Ensure df is not empty
            return ui.div(*[progress_row(row["metric"], row["value"]) for index, row in df.iterrows()])
        elif domain == "intro_readiness":
            df = scores["intro"]
            req(not df.empty) # Ensure df is not empty
            subdomains = df["subdomain"].unique()
            req(not pd.Series(subdomains).empty) # Ensure subdomains is not empty
            return ui.div(
                *[intro_subdomain_section(subdomain, df[df["subdomain"] == subdomain]) for subdomain in subdomains]
            )

    @reactive.Calc
    def rd_score_from_stage():
        row = detail_row()
        req(row) # Ensure detail_row() returns a valid row
        stage = row["Stage"]
        req(stage) # Ensure stage is not None or empty
        if "Implementation Ready" in stage:
            return 95
        elif "Post-Market Surveillance" in stage:
            return 90
        elif "Phase III" in stage:
            return 85
        elif "Phase II" in stage:
            return 65
        elif "Phase I" in stage:
            return 45
        else:
            return 50

    @reactive.Calc
    def delivery_scale_score():
        scores = scores_for_id()
        req(scores) # Ensure scores is not None
        
        intro_df = scores["intro"]
        req(not intro_df.empty) # Ensure intro_df is not None or empty

        # Filter for relevant metrics within the "intro" DataFrame
        # Assuming "Policy" and "Uptake/Delivery" subdomains are relevant for "Delivery & Scale"
        relevant_metrics = intro_df[
            (intro_df["subdomain"] == "Policy") | 
            ((intro_df["subdomain"] == "Uptake/Delivery") & (intro_df["metric"].str.contains("demand", case=False)))
        ]["value"]
        req(not relevant_metrics.empty) # Ensure relevant_metrics is not empty
        
        if not relevant_metrics.empty:
            return round(relevant_metrics.mean())
        return 0

    @reactive.Calc
    def impl_readiness_avg():
        scores = scores_for_id()
        req(scores) # Ensure scores is not None
        
        all_scores = pd.concat([scores["impact"]["value"], scores["intro"]["value"]])
        req(not all_scores.empty) # Ensure all_scores is not empty
        return round(all_scores.mean())

    @reactive.Calc
    def sel_ce():
        selected_id = get_selected_id()
        req(selected_id) # Ensure selected_id is not None
        ce_data = data["ce_all"][data["ce_all"]["id"] == selected_id]
        req(not ce_data.empty) # Ensure ce_data is not empty
        return ce_data

    @reactive.Calc
    def sel_pop():
        selected_id = get_selected_id()
        req(selected_id) # Ensure selected_id is not None
        
        pop_impact = data["pop_impact_all"]
        pop_row = pop_impact[pop_impact["id"] == selected_id]
        
        req(not pop_row.empty) # Ensure pop_row is not empty
        
        if not pop_row.empty:
            return pop_row["pop_millions"].iloc[0]
        return None

    @render.ui
    def kpi_box():
        selected_id = get_selected_id()
        req(selected_id) # Ensure selected_id is not None

        pop_m = sel_pop()
        ce_mean = sel_ce()["ce_usd_per_daly"].mean()
        impl = impl_readiness_avg()
        rd = rd_score_from_stage()
        del_score = delivery_scale_score()
        dev_score = round(0.6 * rd + 0.4 * del_score)

        return ui.div(
            ui.div(ui.value_box(
                "Population Impact Potential",
                f"{pop_m} M" if pop_m else "—",
                ui.tags.i(class_="fa fa-users"),
                ui.tags.small("Estimated potential beneficiaries"),
            ), class_="col-md-3"),
            ui.div(ui.value_box(
                "Cost-effectiveness (mean)",
                f"${int(ce_mean):,}/DALY" if not pd.isna(ce_mean) else "—",
                ui.tags.i(class_="fa fa-scale-balanced"),
                ui.tags.small("Mean across countries with data"),
            ), class_="col-md-3"),
            ui.div(ui.value_box(
                "Implementation Readiness",
                f"{impl}%",
                ui.tags.i(class_="fa fa-gauge-simple-high"),
                ui.tags.small("Average of implementation domains"),
            ), class_="col-md-3"),
            ui.div(ui.value_box(
                "Development Score",
                f"{dev_score}%",
                ui.tags.i(class_="fa fa-flask"),
                ui.tags.small("Blend of R&D trial phase and Delivery & Scale"),
            ), class_="col-md-3"),
            class_="row g-3",
        )