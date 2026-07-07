# main.py
import threading
import time
import shutil
from pathlib import Path

from rich.live import Live
from rich.panel import Panel
from rich.text import Text

from ui.console import console
from ui.renderer import Renderer
from ui.emitter import emit
from ui.events import QuestionEvent
from ui.clock import start as start_clock
from ui.keyboard import init as kb_init, restore as kb_restore, read_key

from graph import graph
from rag.ingest import ingest_documents

DOCS_DIR = Path("documents")


def run_debate(initial_state):
    graph.invoke(initial_state)


def build_initial_state(question):
    return {
        "question": question,
        "round_number": 1,
        "max_rounds": 3,
        "search_used_a": False,
        "search_used_b": False,
        "rag_used_a": False,
        "rag_used_b": False,
        "resource_bank_a": [],
        "resource_bank_b": [],
        "history_a": [],
        "history_b": [],
        "critique_a": None,
        "critique_b": None,
        "judge_result": None,
        "stop_reason": None,
    }


def text_prompt_panel(title: str, prefix: str, buffer: str) -> Panel:
    return Panel(
        Text.assemble(
            (prefix, "bold white"),
            (buffer, "white"),
            ("▍", "bold white"),
        ),
        title=title,
        border_style="bold white",
    )


def message_panel(text: str, style: str = "title") -> Panel:
    return Panel(Text(text, justify="center", style=style))


def read_line(layout, title: str, prefix: str) -> str:
    """Blocking, non-canonical inline text entry rendered into the header panel."""
    buffer = ""
    layout["header"].update(text_prompt_panel(title, prefix, buffer))

    while True:
        key = read_key()

        if key == "ENTER":
            return buffer.strip()
        elif key == "BACKSPACE":
            buffer = buffer[:-1]
            layout["header"].update(text_prompt_panel(title, prefix, buffer))
        elif key is not None:
            buffer += key
            layout["header"].update(text_prompt_panel(title, prefix, buffer))

        time.sleep(0.02)


def handle_upload(layout) -> None:
    """
    Optional inline upload step. Enter with no input skips RAG entirely.
    Copies the given PDF into documents/ and ingests it into the vector store.
    """
    file_path_str = read_line(
        layout,
        "Upload a PDF for RAG (optional) — Enter to skip",
        "File path: ",
    )

    if not file_path_str:
        return

    src = Path(file_path_str).expanduser()

    if not src.is_file() or src.suffix.lower() != ".pdf":
        layout["header"].update(
            message_panel(f"'{file_path_str}' is not a valid PDF — skipping.", style="warning")
        )
        time.sleep(1.5)
        return

    DOCS_DIR.mkdir(exist_ok=True)
    shutil.copy(src, DOCS_DIR / src.name)

    layout["header"].update(message_panel("Ingesting document into vector store..."))

    count = ingest_documents(str(DOCS_DIR))

    if count:
        layout["header"].update(message_panel(f"Ingested {count} chunks.", style="success"))
    else:
        layout["header"].update(message_panel("No readable PDF content found.", style="warning"))

    time.sleep(1.0)


def main():
    renderer = Renderer()
    layout = renderer.get_layout()

    old_settings = kb_init()

    try:
        with Live(
            layout,
            console=console,
            refresh_per_second=20,
            screen=True,
        ):
            # -----------------------------------------------
            # Phase 0: optional document upload + ingestion
            # -----------------------------------------------
            handle_upload(layout)

            # -----------------------------------------------
            # Phase 1: collect the question inline
            # -----------------------------------------------
            question = ""
            while not question:
                question = read_line(layout, "Type your question and press Enter", "Question: ")

            # -----------------------------------------------
            # Phase 2: run the debate
            # -----------------------------------------------
            emit(QuestionEvent(question=question))
            start_clock()
            renderer.scroll.reset_all()
            renderer.refresh()

            initial_state = build_initial_state(question)

            worker = threading.Thread(target=run_debate, args=(initial_state,), daemon=True)
            worker.start()

            while worker.is_alive():
                renderer.process_events()
                while True:
                    key = read_key()
                    if key is None:
                        break
                    renderer.handle_input(key)
                time.sleep(0.03)

            for _ in range(20):
                renderer.process_events()
                time.sleep(0.05)

            while True:
                renderer.process_events()
                while True:
                    key = read_key()
                    if key is None:
                        break
                    renderer.handle_input(key)
                time.sleep(0.03)

            layout["footer"].update(
                Text(
                    "Debate finished — press Ctrl+C to exit",
                    justify="center",
                    style="bold green",
                )
            )

            while True:
                renderer.process_events()
                time.sleep(0.1)

    finally:
        kb_restore(old_settings)
        shutil.rmtree(DOCS_DIR, ignore_errors=True)
        shutil.rmtree("vector_db", ignore_errors=True)


def run():
    try:
        main()
    except KeyboardInterrupt:
        console.clear()
        console.print("[bold green]Goodbye![/bold green]")


if __name__ == "__main__":
    run()