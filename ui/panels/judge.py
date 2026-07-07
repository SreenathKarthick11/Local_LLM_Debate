# ui/panels/judge.py
from rich.console import Group
from rich.panel import Panel
from rich.text import Text

from ui.state import UIState
from ui.widgets import confidence
from ui.scroll import windowed


def render_judge(state: UIState, console=None, viewport=None, scroll_state=None):

    judge = state.judge

    content = Group(
        Text(f"Winner : {judge.winner}", style="bold success"),
        Text(),
        confidence(judge.confidence),
        Text(),
        Text(judge.reasoning),
    )

    title = "Judge"

    if console and viewport and scroll_state:
        width, height = viewport
        content, more_above, more_below = windowed(console, content, width, height, scroll_state)
        title = ("▲ " if more_above else "") + title + (" ▼" if more_below else "")

    return Panel(content, title=title, border_style="color_judge")