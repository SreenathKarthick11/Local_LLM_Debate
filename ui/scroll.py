# ui/scroll.py
from dataclasses import dataclass

from rich.console import Console
from rich.segment import Segment
from rich.cells import cell_len
from rich.measure import Measurement

SCROLLABLE_PANELS = ("router", "resources", "agent_a", "agent_b", "critique_a", "critique_b", "judge")


@dataclass
class ScrollState:
    offset: int = 0
    max_offset: int = 0

    def scroll_down(self, n=1):
        self.offset = min(self.offset + n, self.max_offset)

    def scroll_up(self, n=1):
        self.offset = max(self.offset - n, 0)

    def reset(self):
        self.offset = 0
        self.max_offset = 0


class ScrollManager:
    def __init__(self):
        self.states = {name: ScrollState() for name in SCROLLABLE_PANELS}
        self.focused = None

    def focus(self, name):
        if name in self.states:
            self.focused = name

    def scroll_down(self, name, n=1):
        if name in self.states:
            self.states[name].scroll_down(n)

    def scroll_up(self, name, n=1):
        if name in self.states:
            self.states[name].scroll_up(n)

    def scroll_focused_down(self, n=1):
        if self.focused:
            self.scroll_down(self.focused, n)

    def scroll_focused_up(self, n=1):
        if self.focused:
            self.scroll_up(self.focused, n)

    def reset_all(self):
        for s in self.states.values():
            s.reset()


class _SegmentLines:
    """Re-emits a pre-sliced list of already-rendered lines, with a known fixed width."""

    def __init__(self, lines, width: int):
        self.lines = lines
        self._width = width

    def __rich_console__(self, console, options):
        for line in self.lines:
            yield from line
            yield Segment.line()

    def __rich_measure__(self, console, options):
        return Measurement(self._width, self._width)


def windowed(console: Console, renderable, width: int, height: int, state: ScrollState):
    options = console.options.update(width=width, height=None)
    lines = console.render_lines(renderable, options, pad=False)

    total = len(lines)
    state.max_offset = max(0, total - height)
    state.offset = max(0, min(state.offset, state.max_offset))

    window = lines[state.offset: state.offset + height]
    while len(window) < height:
        window.append([])

    more_above = state.offset > 0
    more_below = (state.offset + height) < total

    return _SegmentLines(window, width), more_above, more_below