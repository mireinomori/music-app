#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
RUNTIME_DIR="$ROOT_DIR/.runtime"
mkdir -p "$RUNTIME_DIR"

start_process() {
  local name="$1"
  local pid_file="$RUNTIME_DIR/$name.pid"
  local log_file="$RUNTIME_DIR/$name.log"
  shift

  if [[ -f "$pid_file" ]] && kill -0 "$(cat "$pid_file")" 2>/dev/null; then
    echo "$name is already running (PID $(cat "$pid_file"))"
    return
  fi

  nohup "$@" >"$log_file" 2>&1 < /dev/null &
  echo $! >"$pid_file"
  echo "started $name (PID $!, log: $log_file)"
}

start_process backend "$ROOT_DIR/.venv/bin/python" -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --app-dir "$ROOT_DIR/backend"
start_process frontend npm run dev --prefix "$ROOT_DIR/frontend" -- --host 127.0.0.1

sleep 1
if command -v open >/dev/null 2>&1; then
  open -a "Google Chrome" http://127.0.0.1:5173/ || true
fi

echo "おと譜を起動しました: http://127.0.0.1:5173/"
