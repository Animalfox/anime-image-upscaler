#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

VENV_PY="$ROOT/.venv/bin/python"

if ! command -v uv >/dev/null 2>&1 && ! command -v python3.12 >/dev/null 2>&1; then
  echo "Need uv or python3.12 on PATH."
  exit 1
fi

if [[ ! -x "$VENV_PY" ]]; then
  if command -v uv >/dev/null 2>&1; then
    echo "Creating .venv with Python 3.12 via uv…"
    uv venv --python 3.12 .venv
  else
    echo "Creating .venv with python3.12…"
    python3.12 -m venv .venv
  fi
else
  echo "Reusing existing .venv"
fi

if command -v uv >/dev/null 2>&1; then
  echo "Installing dependencies with uv…"
  uv pip install --python "$VENV_PY" -r requirements.txt
else
  echo "Installing dependencies with pip…"
  "$VENV_PY" -m pip install --upgrade pip
  "$VENV_PY" -m pip install -r requirements.txt
fi

echo "Install complete. Next: make up"
