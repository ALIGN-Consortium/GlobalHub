import os
from shiny import App, ui
from shiny.ui import nav_panel
from modules.about import about_ui
from modules.overview import overview_ui, overview_server
from modules.overview_and_innovations import innovation_page_ui, innovation_page_server
from modules.innovation_details import innovation_details_ui, innovation_details_server
from modules.comparison import comparison_ui, comparison_server
from utils.theme import create_theme

# --- App Configuration ---
app_ui = ui.page_navbar(
    nav_panel(
        "About",
        about_ui("about"),
    ),
    nav_panel(
        "Overview",
        innovation_page_ui("innovation_page"),
    ),
    nav_panel(
        "Product Comparison",
        comparison_ui("comparison"),
    ),
    id="main_nav",
    title=ui.tags.div(
        ui.tags.img(src="logo/without_partners.png", height="100px"),
        # ui.tags.span(
        #     "ALIGN - Market Intelligence Hub", style="color: #1a1a1a; font-weight: 600;"
        # ),
    ),
    theme=create_theme(),
    header=ui.tags.head(
        ui.tags.link(rel="stylesheet", href="styles.css"),
        ui.tags.link(
            rel="stylesheet",
            href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css",
        ),
        ui.tags.script(
            src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"
        ),
    ),
    footer=ui.tags.footer(
        ui.tags.hr(),
        ui.tags.img(
            src="logo/with_partners.png", height="120px", style="margin-bottom: 15px;"
        ),
        ui.p("© 2026 ALIGN Consortium. All rights reserved."),
        ui.div(
            ui.tags.i(class_="fa-solid fa-globe me-2"),
            ui.tags.a("Website", href="https://alignconsortium.org", target="_blank"),
            ui.tags.span(" | "),
            ui.tags.i(class_="fa-brands fa-github me-2"),
            ui.tags.a(
                "GitHub",
                href="https://github.com/ALIGN-Consortium/GlobalHub",
                target="_blank",
            ),
            ui.tags.span(" | "),
            ui.tags.i(class_="fa-solid fa-envelope me-2"),
            ui.tags.a("Contact", href="mailto:dukeghic@duke.edu"),
        ),
        style="""
        text-align: center;
        margin-top: 50px;
        padding: 30px 20px;
        color: #6c757d;
        background-color: white;
    """,
    ),
)

def server(input, output, session):
    """
    Main server function that orchestrates module servers.
    """
    comparison_server("comparison", input, output, session)
    innovation_page_server("innovation_page")


app = App(app_ui, server, static_assets=os.path.join(os.path.dirname(__file__), "www"))
