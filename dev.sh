#!/usr/bin/env bash
# Starts both the backend and frontend for local development.
# Ctrl+C stops both.
set -e

cleanup() {
  echo "Stopping..."
  kill "$BACKEND_PID" "$FRONTEND_PID" 2>/dev/null
}
trap cleanup EXIT

echo "Starting backend on :8000..."
(cd backend && uvicorn app:app --reload --port 8000) &
BACKEND_PID=$!

echo "Starting frontend on :5173..."
(cd frontend && npm run dev) &
FRONTEND_PID=$!

wait
