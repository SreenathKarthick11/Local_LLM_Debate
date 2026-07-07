# Local LLM Debate

Two locally-run LLMs debate a question, critique each other, revise, and a judge picks a winner — with a live terminal UI showing routing, resources (web/RAG/tools), and the debate as it happens.

## Requirements
- Python 3.10+
- [Ollama](https://ollama.com/download) installed and running
- A terminal with truecolor support (iTerm2, Windows Terminal, GNOME Terminal, Kitty, Alacritty)

## Setup

**macOS/Linux**
```bash
git clone <your-repo-url>
cd Local_LLM_Debate
./install.sh
```

## Run
```bash
source .venv/bin/activate   # Windows: .\.venv\Scripts\Activate.ps1
python main.py
```

- Optionally upload a PDF for retrieval-augmented answers when prompted.
- Type your question, press Enter, watch the debate.
- Click a panel to focus it, `j`/`k` or arrows or mouse wheel to scroll, Ctrl+C to exit.
