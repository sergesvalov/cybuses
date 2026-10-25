#!/bin/bash
# Start both FastAPI app and MCP server with signal propagation

set -e

echo ">>> Running database migrations..."
python migrate.py || {
    echo "Migrations failed, aborting startup."
    exit 1
}

MCP_PORT=${MCP_PORT:-8999}
echo ">>> Starting MCP server on port ${MCP_PORT}..."
python mcp_server.py &
MCP_PID=$!

# Ensure background MCP process terminates when container exits
trap "kill $MCP_PID 2>/dev/null || true" SIGTERM SIGINT EXIT

PORT=${PORT:-8000}
HOST=${HOST:-0.0.0.0}
echo ">>> Starting FastAPI app on ${HOST}:${PORT}..."
exec uvicorn main:app --host "${HOST}" --port "${PORT}"
