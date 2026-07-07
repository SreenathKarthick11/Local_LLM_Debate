# renderer.py
from dataclasses import asdict

from rich.panel import Panel
from rich.text import Text

from ui.state import UIState
from ui.console import console
from ui.scroll import ScrollManager
from ui.geometry import compute_regions, viewport_size, hit_test

from ui.events import (
    QuestionEvent, RouterEvent, ResourceEvent, AgentEvent,
    CritiqueEvent, JudgeEvent, RuntimeEvent,
)
from ui.layout import build_layout
from ui.panels import (
    render_router, render_resources, render_agent_a, render_agent_b,
    render_critique_a, render_critique_b, render_judge, render_runtime,
)
from ui.event_bus import event_bus


class Renderer:

    def __init__(self):
        self.state = UIState()
        self.layout = build_layout()
        self.scroll = ScrollManager()
        self.refresh()

    def update(self, event):
        if isinstance(event, QuestionEvent):
            self._update_question(event)
        elif isinstance(event, RouterEvent):
            self._update_router(event)
        elif isinstance(event, ResourceEvent):
            self._update_resources(event)
        elif isinstance(event, AgentEvent):
            self._update_agent(event)
        elif isinstance(event, CritiqueEvent):
            self._update_critique(event)
        elif isinstance(event, JudgeEvent):
            self._update_judge(event)
        elif isinstance(event, RuntimeEvent):
            self._update_runtime(event)
        self.refresh()

    def refresh(self):
        self.layout["header"].update(
            Panel(
                Text(self.state.question or "Local LLM Multi-Agent Debate",
                     justify="center", style="title")
            )
        )

        width, height = console.size
        regions = compute_regions(width, height)

        self.layout["router"].update(
            render_router(self.state, console, viewport_size(regions["router"]), self.scroll.states["router"])
        )
        self.layout["resources"].update(
            render_resources(self.state, console, viewport_size(regions["resources"]), self.scroll.states["resources"])
        )
        self.layout["agent_a"].update(
            render_agent_a(
                self.state, console,
                viewport_size(regions["agent_a"]),
                self.scroll.states["agent_a"],
            )
        )
        self.layout["agent_b"].update(
            render_agent_b(
                self.state, console,
                viewport_size(regions["agent_b"]),
                self.scroll.states["agent_b"],
            )
        )
        self.layout["critique_a"].update(
            render_critique_a(
                self.state, console,
                viewport_size(regions["critique_a"]),
                self.scroll.states["critique_a"],
            )
        )
        self.layout["critique_b"].update(
            render_critique_b(
                self.state, console,
                viewport_size(regions["critique_b"]),
                self.scroll.states["critique_b"],
            )
        )
        self.layout["judge"].update(
            render_judge(
                self.state, console,
                viewport_size(regions["judge"]),
                self.scroll.states["judge"],
            )
        )
        self.layout["runtime"].update(render_runtime(self.state))

        self.layout["footer"].update(
            Text("Click a panel to focus • ↓/↑ or wheel to scroll • Ctrl+C to exit",
                 justify="center", style="dim")
        )

    def handle_input(self, key):
        """Feed every key from read_key() here during the debate/idle phase."""
        if isinstance(key, tuple):
            kind, col, row = key
            name = hit_test(compute_regions(*console.size), col, row)
            if kind == "CLICK" and name:
                self.scroll.focus(name)
                self.refresh()
            elif kind == "SCROLL_UP" and name:
                self.scroll.scroll_up(name, 3)
                self.refresh()
            elif kind == "SCROLL_DOWN" and name:
                self.scroll.scroll_down(name, 3)
                self.refresh()
            return

        if key in ("j", "DOWN"):
            self.scroll.scroll_focused_down()
            self.refresh()
        elif key in ("k", "UP"):
            self.scroll.scroll_focused_up()
            self.refresh()

    # -- existing _update_* / process_events / get_layout / get_state / reset / dump unchanged --
    def _update_question(self, event):
        self.state.question = event.question

    def _update_router(self, event):
        self.state.router.status = event.status
        self.state.router.use_web = event.use_web
        self.state.router.use_rag = event.use_rag
        self.state.router.use_python = event.use_python
        self.state.router.confidence = event.confidence
        self.state.router.reason = event.reason

    def _update_resources(self, event):
        self.state.resources.web = event.web
        self.state.resources.rag = event.rag
        self.state.resources.tools = event.tools

    def _update_agent(self, event):
        agent = self.state.agent_a if event.agent.upper() == "A" else self.state.agent_b
        agent.status = event.status
        agent.answer = event.answer
        agent.reasoning = event.reasoning
        agent.confidence = event.confidence

    def _update_critique(self, event):
        critique = self.state.critique_a if event.agent.upper() == "A" else self.state.critique_b
        critique.weaknesses = event.weaknesses
        critique.hallucination_risk = event.hallucination_risk
        critique.hallucinations = event.hallucinations

    def _update_judge(self, event):
        self.state.judge.winner = event.winner
        self.state.judge.reasoning = event.reasoning
        self.state.judge.confidence = event.confidence

    def _update_runtime(self, event):
        self.state.runtime.round_number = event.round_number
        self.state.runtime.max_rounds = event.max_rounds
        self.state.runtime.elapsed_seconds = event.elapsed_seconds
        self.state.runtime.stop_reason = event.stop_reason

    def process_events(self):
        for event in event_bus.poll():
            self.update(event)

    def get_layout(self):
        return self.layout

    def get_state(self):
        return self.state

    def reset(self):
        self.state = UIState()
        self.scroll.reset_all()
        self.refresh()

    def dump(self):
        return asdict(self.state)