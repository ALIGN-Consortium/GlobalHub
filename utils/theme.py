from shiny import ui
from .config import COLORS

def create_theme() -> ui.Theme:
    """Creates and configures the application theme."""
    return ui.Theme().add_defaults(
        primary=COLORS["primary"],
        secondary=COLORS["secondary"],
        bg=COLORS["bg"],
        fg=COLORS["fg"],
    ).add_rules(
        """
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=Inter+Tight:wght@400;700&display=swap');

        body {
            font-family: 'Inter', sans-serif;
        }

        h1, h2, h3, h4, h5, h6 {
            font-family: 'Inter Tight', sans-serif;
        }
        """
    )
