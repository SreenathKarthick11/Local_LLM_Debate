#!/usr/bin/env bash
set -e

echo "==> Checking for Ollama..."
if ! command -v ollama &> /dev/null; then
    echo "Ollama not found. Install it from https://ollama.com/download and re-run this script."
    exit 1
fi

echo "==> Pulling required models (this may take a while the first time)..."
ollama pull qwen2.5:3b
ollama pull qwen2.5:1.5b

echo "==> Creating virtual environment..."
python3 -m venv .venv
source .venv/bin/activate

echo "==> Installing the app..."
pip install --upgrade pip
pip install -e .

echo "==> Done. To run the app:"
echo "    source .venv/bin/activate"
echo "    python main.py"
