#!/usr/bin/env bash
# Menjalankan backend (FastAPI, port 8000) lalu frontend (Vite, port 5173) sekaligus.
# Jalankan hanya setelah semua langkah instalasi di README.md selesai.
# Ctrl+C menghentikan keduanya.
set -euo pipefail
cd "$(dirname "$0")"

UVICORN=backend/.venv/bin/uvicorn
[ -x "$UVICORN" ] || UVICORN=backend/.venv/Scripts/uvicorn.exe   # Git Bash di Windows

"$UVICORN" app.main:app --app-dir backend --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!
trap 'kill "$BACKEND_PID" 2>/dev/null || true' EXIT INT TERM

cd frontend
npm run dev
