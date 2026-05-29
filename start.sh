#!/bin/bash
# Start both FastAPI app and MCP server

echo ">>> Running database migrations..."
python migrate.py
if [ $? -ne 0 ]; then
    echo "Migrations failed, aborting startup."
    exit 1
fi

echo ">>> Starting MCP server on port 8999..."
python mcp_server.py &

echo ">>> Starting FastAPI app on port 8000..."
exec uvicorn main:app --host 0.0.0.0 --port 8000
