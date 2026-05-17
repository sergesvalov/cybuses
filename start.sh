#!/bin/bash
# Start both FastAPI app and MCP server

echo ">>> Starting MCP server on port 8888..."
python mcp_server.py &

echo ">>> Starting FastAPI app on port 8000..."
exec uvicorn main:app --host 0.0.0.0 --port 8000
