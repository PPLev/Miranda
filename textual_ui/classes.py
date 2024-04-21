from textual import widgets
from textual.widget import Widget


class Horizontal(Widget, inherit_bindings=False):
    """A container with horizontal layout and no scrollbars."""

    DEFAULT_CSS = """
    Horizontal {
        width: auto;
        height: 1fr;
        layout: horizontal;
        overflow: hidden hidden;
    }
    """
