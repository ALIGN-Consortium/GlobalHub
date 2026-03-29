import os
from shiny import App, ui, reactive, render
from shiny.ui import nav_panel

# --- Modules ---
from modules.about import about_ui
from modules.overview_and_innovations import (
    innovation_page_ui,
    innovation_page_server,
)
from modules.comparison import comparison_ui, comparison_server

# --- Theme ---
from utils.theme import create_theme


# =========================================================
# UI
# =========================================================
app_ui = ui.page_navbar(

    # -------------------------
    # NAVIGATION
    # -------------------------
    nav_panel(
        "About",
        about_ui("about"),
    ),

    nav_panel(
        "Overview",
        innovation_page_ui("innovation_page"),
    ),

    nav_panel(
        "Product comparison",
        comparison_ui("comparison"),
    ),

    id="main_nav",

    # -------------------------
    # TITLE / LOGO
    # -------------------------
    title=ui.tags.div(
        ui.tags.img(
            src="logo/without_partners.png",
            height="60px",
            class_="brand-logo",
        ),
        class_="d-flex align-items-center",
    ),

    # -------------------------
    # THEME
    # -------------------------
    theme=create_theme(),

    # -------------------------
    # HEADER (Sticky hero)
    # -------------------------
    header=ui.TagList(
        ui.tags.head(
            ui.tags.link(rel="stylesheet", href="styles.css"),
            ui.tags.link(
                rel="stylesheet",
                href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css",
            ),
            ui.tags.script(
                src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"
            ),
        ),

        ui.div(
            ui.div(
                ui.div(
                    ui.div(
                        ui.h1("ALIGN Global Hub", class_="fw-bold display-5 mb-1"),
                        ui.p(
                            "Market intelligence hub for global health products",
                            class_="lead text-muted mb-0",
                        ),
                        class_="flex-grow-1",
                    ),
                    ui.output_ui("cart_container"),
                    class_="d-flex align-items-center justify-content-between",
                ),
                class_="container-fluid px-4",
            ),
            class_="sticky-hero-container",
        ),
    ),

    # -------------------------
    # FOOTER
    # -------------------------
    footer=ui.tags.footer(
        ui.tags.hr(),
        ui.tags.img(
            src="logo/with_partners.png",
            height="120px",
            style="margin-bottom: 15px;",
        ),
        ui.p("© 2026 ALIGN Consortium. All rights reserved."),
        ui.div(
            ui.tags.i(class_="fa-solid fa-globe me-2"),
            ui.tags.a(
                "Website",
                href="https://alignconsortium.org",
                target="_blank",
            ),
            ui.tags.span(" | "),
            ui.tags.i(class_="fa-brands fa-github me-2"),
            ui.tags.a(
                "GitHub",
                href="https://github.com/ALIGN-Consortium/GlobalHub",
                target="_blank",
            ),
            ui.tags.span(" | "),
            ui.tags.i(class_="fa-solid fa-envelope me-2"),
            ui.tags.a(
                "Contact",
                href="mailto:align@duke.edu",
            ),
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


# =========================================================
# SERVER
# =========================================================
def server(input, output, session):

    # -------------------------
    # Shared cart state
    # -------------------------
    cart = reactive.Value(set())

    # -------------------------
    # Module servers
    # -------------------------
    comparison_server("comparison", cart=cart)
    innovation_page_server("innovation_page", cart=cart)

    # -------------------------
    # Cart UI (hidden on About)
    # -------------------------
    @render.ui
    def cart_container():

        # Hide cart on About page
        if input.main_nav() == "About":
            return None

        items = list(cart.get())
        count = len(items)

        return ui.div(
            ui.popover(

                # Trigger button
                ui.tags.button(
                    ui.tags.i(class_="fa-solid fa-cart-shopping"),
                    ui.tags.span(
                        str(count),
                        class_="badge rounded-pill bg-danger ms-1",
                    )
                    if count > 0
                    else "",
                    class_="btn btn-outline-primary position-relative",
                    type="button",
                ),

                # Popover content
                ui.div(
                    ui.h6("My comparison list", class_="mb-3"),

                    ui.div(
                        *(
                            [
                                ui.div(
                                    ui.tags.span(item),
                                    ui.tags.button(
                                        ui.tags.i(class_="fa-solid fa-xmark"),
                                        class_="btn btn-sm btn-ghost float-end",
                                        onclick=f"Shiny.setInputValue('remove_from_cart', '{item}', {{priority: 'event'}})",
                                    ),
                                    class_="cart-item d-flex justify-content-between align-items-center w-100",
                                )
                                for item in items
                            ]
                            if items
                            else [ui.p("No products added yet.", class_="text-muted")]
                        ),
                        style="max-height: 300px; overflow-y: auto; min-width: 250px;",
                    ),

                    ui.hr(),

                    ui.div(
                        ui.tags.button(
                            "Compare your products",
                            class_="btn btn-primary btn-sm flex-grow-1",
                            onclick="Shiny.setInputValue('go_to_comparison', Math.random(), {priority: 'event'})",
                        ),
                        ui.tags.button(
                            ui.tags.i(class_="fa-solid fa-trash"),
                            class_="btn btn-outline-danger btn-sm ms-2",
                            title="Clear cart",
                            onclick="Shiny.setInputValue('clear_cart', Math.random(), {priority: 'event'})",
                        ),
                        class_="d-flex",
                    ),

                    class_="p-2",
                ),

                placement="bottom",
            ),
            class_="ms-auto d-flex align-items-center",
        )

    # -------------------------
    # Cart logic
    # -------------------------
    @reactive.Effect
    @reactive.event(input.remove_from_cart)
    def _remove_item():
        item_to_remove = input.remove_from_cart()
        current = cart.get()

        if item_to_remove in current:
            new_cart = current.copy()
            new_cart.remove(item_to_remove)
            cart.set(new_cart)

    @reactive.Effect
    @reactive.event(input.go_to_comparison)
    def _go_to_comparison():
        ui.update_navs("main_nav", selected="Product comparison")

    @reactive.Effect
    @reactive.event(input.clear_cart)
    def _clear_cart():
        cart.set(set())


# =========================================================
# APP
# =========================================================
app = App(
    app_ui,
    server,
    static_assets=os.path.join(os.path.dirname(__file__), "www"),
)