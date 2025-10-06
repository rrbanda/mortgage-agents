#!/bin/bash
set -e

echo "🏦 Starting Credit Check MCP Server..."

# Start Flask API in background on port 8081
echo "📊 Starting Flask Credit API on port 8081..."
PORT=8081 python mock_credit_api.py &
FLASK_PID=$!

# Wait for Flask to be ready
echo "⏳ Waiting for Flask API to be ready..."
sleep 5

# Verify Flask is running
curl -f http://localhost:8081/health || {
    echo " Flask API failed to start"
    exit 1
}

echo " Flask API is ready"

# Start FastMCP server with SSE transport (port from environment)
echo "🔗 Starting FastMCP Credit Server on port ${MCP_PORT:-8000}..."
# Don't override MCP_PORT - use the value from Kubernetes/ToolHive environment
export UVICORN_HOST=0.0.0.0  # Force Uvicorn to bind to all interfaces for ToolHive
exec python mcp_fastmcp_server.py

# This should never be reached, but just in case
wait $FLASK_PID
