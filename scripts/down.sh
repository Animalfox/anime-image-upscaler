#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PID_FILE="$ROOT/.run/upscaler.pid"
PORT_FILE="$ROOT/.port"

stop_pid() {
  local pid="$1"
  if [[ -z "$pid" ]]; then
    return 0
  fi
  if ! kill -0 "$pid" 2>/dev/null; then
    return 0
  fi
  kill "$pid" 2>/dev/null || true
  for _ in 1 2 3 4 5 6 7 8 9 10; do
    if ! kill -0 "$pid" 2>/dev/null; then
      echo "Stopped (pid $pid)"
      return 0
    fi
    sleep 0.2
  done
  kill -9 "$pid" 2>/dev/null || true
  echo "Force-stopped (pid $pid)"
}

STOPPED_ANY=0

if [[ -f "$PID_FILE" ]]; then
  PID="$(tr -d '[:space:]' < "$PID_FILE" || true)"
  if [[ -n "${PID:-}" ]]; then
    if kill -0 "$PID" 2>/dev/null; then
      stop_pid "$PID"
      STOPPED_ANY=1
    else
      echo "Process $PID is already gone"
    fi
  fi
  rm -f "$PID_FILE"
fi

if [[ -f "$PORT_FILE" ]]; then
  PORT="$(tr -d '[:space:]' < "$PORT_FILE")"
  if [[ -n "$PORT" ]]; then
    # Clean up orphans if the pid file was lost.
    while read -r extra; do
      [[ -z "$extra" ]] && continue
      stop_pid "$extra"
      STOPPED_ANY=1
    done < <(lsof -nP -iTCP:"$PORT" -sTCP:LISTEN -t 2>/dev/null || true)
    echo "Port $PORT kept in .port for the next start"
  fi
fi

if [[ "$STOPPED_ANY" -eq 0 ]]; then
  echo "Not running"
fi
