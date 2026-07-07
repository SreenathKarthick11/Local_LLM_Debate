# ui/panels/critique.py
from rich.console import Group
from rich.panel import Panel
from rich.text import Text

from ui.state import UIState
from ui.scroll import windowed


def render_panel(title, critique, color, console=None, viewport=None, scroll_state=None):

    rows = []

    if not critique.weaknesses:
        rows.append(Text("No critique.", style="success"))
    else:
        for w in critique.weaknesses:
            rows.append(Text("• " + w))

    rows.append(Text())
    rows.append(Text(f"Hallucination Risk : {critique.hallucination_risk}", style="bold warning"))

    content = Group(*rows)

    if console and viewport and scroll_state:
        width, height = viewport
        content, more_above, more_below = windowed(console, content, width, height, scroll_state)
        title = ("▲ " if more_above else "") + title + (" ▼" if more_below else "")

    return Panel(content, title=title, border_style=color)


def render_critique_a(state, console=None, viewport=None, scroll_state=None):
    return render_panel("Critique A", state.critique_a, "color_a", console, viewport, scroll_state)


def render_critique_b(state, console=None, viewport=None, scroll_state=None):
    return render_panel("Critique B", state.critique_b, "color_b", console, viewport, scroll_state)