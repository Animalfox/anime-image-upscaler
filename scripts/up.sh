#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

PORT_FILE="$ROOT/.port"
PID_FILE="$ROOT/.run/upscaler.pid"
LOG_FILE="$ROOT/.run/upscaler.log"
VENV_PY="$ROOT/.venv/bin/python"

mkdir -p "$ROOT/.run"

if [[ ! -x "$VENV_PY" ]]; then
  echo "Missing .venv. Run: make install"
  exit 1
fi

if [[ ! -f "$PORT_FILE" ]]; then
  # Ephemeral port 49152–65535, chosen once and kept forever.
  PORT=$((49152 + RANDOM % 16384))
  printf '%s\n' "$PORT" > "$PORT_FILE"
  echo "Pinned port: $PORT → $PORT_FILE"
fi

PORT="$(tr -d '[:space:]' < "$PORT_FILE")"

if [[ -f "$PID_FILE" ]]; then
  OLD_PID="$(tr -d '[:space:]' < "$PID_FILE")"
  if [[ -n "$OLD_PID" ]] && kill -0 "$OLD_PID" 2>/dev/null; then
    echo "Already running (pid $OLD_PID) → http://127.0.0.1:$PORT"
    exit 0
  fi
  rm -f "$PID_FILE"
fi

# start_new_session=True detaches from shell/Cursor; plain nohup can still get killed.
"$VENV_PY" - "$ROOT" "$PORT" "$PID_FILE" "$LOG_FILE" <<'PY'
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

root, port, pid_file, log_file = sys.argv[1:5]
env = os.environ.copy()
env["PYTHONPATH"] = root
env["PYTHONUNBUFFERED"] = "1"
log = open(log_file, "w", encoding="utf-8")
proc = subprocess.Popen(
    [
        sys.executable,
        "-m",
        "uvicorn",
        "app.main:app",
        "--host",
        "127.0.0.1",
        "--port",
        port,
        "--log-level",
        "info",
    ],
    cwd=root,
    env=env,
    stdout=log,
    stderr=subprocess.STDOUT,
    start_new_session=True,
)
Path(pid_file).write_text(f"{proc.pid}\n", encoding="utf-8")

url = f"http://127.0.0.1:{port}/health"
for _ in range(50):
    if proc.poll() is not None:
        sys.stderr.write(
            f"Server exited immediately (code {proc.returncode}). Check log: {log_file}\n"
        )
        sys.exit(1)
    try:
        with urllib.request.urlopen(url, timeout=0.4) as resp:
            if resp.status == 200:
                break
    except (urllib.error.URLError, TimeoutError):
        time.sleep(0.1)
else:
    sys.stderr.write(f"Server did not become ready in time. Check log: {log_file}\n")
    sys.exit(1)

print(proc.pid)
PY

PID="$(tr -d '[:space:]' < "$PID_FILE")"
echo "Anime Image Upscaler: http://127.0.0.1:$PORT  (pid $PID)"
echo "Log: $LOG_FILE"
