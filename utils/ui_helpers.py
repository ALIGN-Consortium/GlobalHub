from shiny import ui

def with_tooltip(element, message, placement="top"):
    """
    Wraps a UI element with a Shiny tooltip.
    """
    return ui.tooltip(element, message, placement=placement)

def info_tooltip(message, placement="top"):
    """
    Returns a standard info icon (fa-circle-info) with a hovering tooltip.
    """
    return ui.tooltip(
        ui.tags.i(
            class_="fa-solid fa-circle-info text-muted",
            style="cursor:pointer; margin-left: 0.5rem;"
        ),
        message,
        placement=placement
    )
