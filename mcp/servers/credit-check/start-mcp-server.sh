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

# Verify Flask is running using Python (curl not available in slim image)
python -c "import requests; requests.get('http://localhost:8081/health', timeout=5).raise_for_status()" || {
    echo " Flask API failed to start"
    exit 1
}

echo " Flask API is ready"

# Start MCP server with HTTP transport (port from environment)
echo "🔗 Starting MCP Credit Server on port ${MCP_PORT:-8000}..."
exec python mcp_server.py

# This should never be reached, but just in case
wait $FLASK_PID
