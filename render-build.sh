#!/usr/bin/env bash
set -euo pipefail

python -m pip install --upgrade pip
python -m pip install "poetry==2.2.1"

# Instala dependências no ambiente do Render (sem criar venv separado)
poetry config virtualenvs.create false
poetry install --only main --no-interaction --no-ansi
