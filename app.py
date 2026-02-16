import os
from shiny import App, ui
from shiny.ui import nav_panel
from modules.overview import overview_ui, overview_server
from modules.innovation_details import innovation_details_ui, innovation_details_server
from modules.comparison import comparison_ui, comparison_server
from utils.theme import create_theme

# --- App Configuration ---
app_ui = ui.page_navbar(
    nav_panel(
        "Overview",
        overview_ui("overview"),
    ),
    nav_panel(
        "Innovation Details",
        innovation_details_ui("innovation_details"),
    ),
    nav_panel(
        "Product Comparison",
        comparison_ui("comparison"),
    ),
    id="main_nav",
    title=ui.tags.div(
        ui.tags.img(src="logo/without_partners.png", height="40px", style="margin-right: 10px;"),
        "ALIGN - Market Intelligence Hub"
    ),
    theme=create_theme(),
    header=ui.tags.head(
        ui.tags.link(rel="stylesheet", href="styles.css"),
        ui.tags.link(rel="stylesheet", href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css"),
        ui.tags.script(src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"),
    ),
    footer=ui.tags.footer(
        ui.tags.hr(),
        ui.tags.img(src="logo/with_partners.png", height="120px", style="margin-bottom: 10px;"),
        ui.p("© 2026 ALIGN Consortium. All rights reserved."),
        ui.p("Contact: ", ui.tags.a("placeholder@example.com", href="mailto:placeholder@example.com")),
        style="text-align: center; margin-top: 50px; padding: 20px; color: #6c757d; background-color: white;"
    ),
)

def server(input, output, session):
    """
    Main server function that orchestrates module servers.
    """
    selected_innovation = overview_server("overview", input, output, session)
    innovation_details_server("innovation_details", selected_innovation, input, output, session)
    comparison_server("comparison", input, output, session)


app = App(app_ui, server, static_assets=os.path.join(os.path.dirname(__file__), "www"))