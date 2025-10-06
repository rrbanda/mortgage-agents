#!/usr/bin/env python3
"""
Credit Check MCP Server
HTTP-based MCP server implementation for credit check functionality compatible with ToolHive
"""

import asyncio
import logging
import json
import requests
import os
from typing import Any, Dict
from flask import Flask, request, jsonify, Response

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask app for HTTP endpoints
app = Flask(__name__)

# Credit API URL - configurable via environment variable
# In OpenShift, set CREDIT_API_URL to the actual service endpoint
# Example: http://credit-api-service:8081 or https://credit-api-route.apps.cluster.com
CREDIT_API_URL = os.getenv("CREDIT_API_URL", "http://localhost:8081")

# MCP tool definitions
TOOLS = [
    {
        "name": "credit_score",
        "description": "Get credit scores for mortgage qualification",
        "inputSchema": {
            "type": "object",
            "properties": {
                "ssn": {
                    "type": "string",
                    "description": "Social Security Number (format: XXX-XX-XXXX)"
                },
                "first_name": {
                    "type": "string", 
                    "description": "First name of the borrower"
                },
                "last_name": {
                    "type": "string",
                    "description": "Last name of the borrower"
                },
                "date_of_birth": {
                    "type": "string",
                    "description": "Date of birth (YYYY-MM-DD format)"
                }
            },
            "required": ["ssn"]
        }
    },
    {
        "name": "verify_identity",
        "description": "Verify borrower identity for mortgage application",
        "inputSchema": {
            "type": "object",
            "properties": {
                "ssn": {
                    "type": "string",
                    "description": "Social Security Number (format: XXX-XX-XXXX)"
                },
                "first_name": {
                    "type": "string",
                    "description": "First name of the borrower"
                },
                "last_name": {
                    "type": "string", 
                    "description": "Last name of the borrower"
                },
                "date_of_birth": {
                    "type": "string",
                    "description": "Date of birth (YYYY-MM-DD format)"
                }
            },
            "required": ["ssn", "first_name", "last_name"]
        }
    },
    {
        "name": "credit_report",
        "description": "Get detailed credit report for mortgage underwriting",
        "inputSchema": {
            "type": "object",
            "properties": {
                "ssn": {
                    "type": "string",
                    "description": "Social Security Number (format: XXX-XX-XXXX)"
                },
                "first_name": {
                    "type": "string",
                    "description": "First name of the borrower"
                },
                "last_name": {
                    "type": "string",
                    "description": "Last name of the borrower"
                },
                "date_of_birth": {
                    "type": "string",
                    "description": "Date of birth (YYYY-MM-DD format)"
                }
            },
            "required": ["ssn"]
        }
    }
]

# HTTP endpoints for MCP over HTTP

@app.route('/mcp', methods=['GET'])
def handle_mcp_sse():
    """Handle MCP requests over Server-Sent Events."""
    def generate_sse():
        try:
            # Send initialization response
            yield f"data: {json.dumps({'result': {'tools': TOOLS}})}\n\n"
        except Exception as e:
            logger.error(f"SSE generation failed: {e}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return Response(
        generate_sse(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Access-Control-Allow-Origin': '*'
        }
    )

def call_credit_api(endpoint: str, arguments: dict) -> dict:
    """Call the credit API and return the result."""
    try:
        response = requests.post(
            f"{CREDIT_API_URL}{endpoint}",
            json=arguments,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        response.raise_for_status()
        return response.json()
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Credit API request failed: {e}")
        raise Exception(f"Credit API error: {str(e)}")

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    try:
        # Check if credit API is responsive
        response = requests.get(f"{CREDIT_API_URL}/health", timeout=5)
        if response.status_code == 200:
            return jsonify({
                "status": "healthy",
                "mcp_server": "running",
                "credit_api": "connected"
            })
        else:
            return jsonify({
                "status": "degraded",
                "mcp_server": "running", 
                "credit_api": "unavailable"
            }), 503
    except:
        return jsonify({
            "status": "degraded",
            "mcp_server": "running",
            "credit_api": "unreachable"
        }), 503

@app.route('/', methods=['GET'])
def root():
    """Root endpoint with MCP server info."""
    return jsonify({
        "name": "Credit Check MCP Server",
        "description": "MCP server for mortgage credit check functionality",
        "version": "1.0.0",
        "transport": "http",
        "endpoints": {
            "mcp": "/mcp",
            "health": "/health"
        },
        "tools": [tool["name"] for tool in TOOLS]
    })

if __name__ == "__main__":
    logger.info("🏦 Starting Credit Check MCP HTTP Server...")
    
    # Get port from environment (for OpenShift compatibility)
    port = int(os.environ.get('MCP_PORT', 8080))
    debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    
    logger.info(f" MCP Server starting on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
