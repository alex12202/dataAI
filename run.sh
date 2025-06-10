#!/bin/bash

# Ověření, že je aktivní virtuální prostředí
if [ -z "$VIRTUAL_ENV" ]; then
  echo "❌ Virtuální prostředí není aktivní."
  echo ""
  echo "👉 Nejprve spusť: source .venv/bin/activate"
  echo "📎 nebo: source env.sh (pokud máš zjednodušený alias)"
  echo ""
  exit 1
fi

echo "🚀 Spouštím FastAPI aplikaci..."
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
