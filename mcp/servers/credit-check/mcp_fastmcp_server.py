#!/usr/bin/env python3
"""
Proper MCP Server using FastMCP for agentic tool discovery
Compatible with langchain-mcp-adapters SSE transport
"""

import os
import asyncio
import logging
import requests
from mcp.server.fastmcp import FastMCP

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Credit API URL - configurable via environment variable
# In OpenShift, set CREDIT_API_URL to the actual service endpoint
# Example: http://credit-api-service:8081 or https://credit-api-route.apps.cluster.com
CREDIT_API_URL = os.getenv("CREDIT_API_URL", "http://localhost:8081")

# Initialize FastMCP server
mcp = FastMCP("Credit Check")

@mcp.tool()
def credit_score(ssn: str, first_name: str = "", last_name: str = "", date_of_birth: str = "") -> str:
    """Get credit scores for mortgage qualification"""
    try:
        payload = {
            "ssn": ssn,
            "first_name": first_name,
            "last_name": last_name,
            "date_of_birth": date_of_birth
        }
        
        response = requests.post(
            f"{CREDIT_API_URL}/credit-score",
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        result = response.json()
        
        # Return formatted response for agent
        credit_score = result.get('credit_score', 'Unknown')
        status = result.get('status', 'Unknown')
        
        return f"Credit Score: {credit_score}, Status: {status}, Bureau: {result.get('bureau', 'Mock')}"
        
    except Exception as e:
        logger.error(f"Credit score API error: {e}")
        return f"Credit check failed: {str(e)}"

@mcp.tool()
def verify_identity(ssn: str, first_name: str, last_name: str, date_of_birth: str = "") -> str:
    """Verify borrower identity for mortgage application"""
    try:
        payload = {
            "ssn": ssn,
            "first_name": first_name,
            "last_name": last_name,
            "date_of_birth": date_of_birth
        }
        
        response = requests.post(
            f"{CREDIT_API_URL}/verify-identity",
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        result = response.json()
        
        # Return formatted response
        verified = result.get('identity_verified', False)
        confidence = result.get('confidence_score', 0)
        
        return f"Identity Verified: {verified}, Confidence: {confidence}%, Match Details: {result.get('match_details', {})}"
        
    except Exception as e:
        logger.error(f"Identity verification API error: {e}")
        return f"Identity verification failed: {str(e)}"

@mcp.tool()
def credit_report(ssn: str, first_name: str = "", last_name: str = "", date_of_birth: str = "") -> str:
    """Get detailed credit report for mortgage underwriting"""
    try:
        payload = {
            "ssn": ssn,
            "first_name": first_name,
            "last_name": last_name,
            "date_of_birth": date_of_birth
        }
        
        response = requests.post(
            f"{CREDIT_API_URL}/credit-report",
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        result = response.json()
        
        # Return comprehensive credit report for underwriting
        return f"""
CREDIT REPORT SUMMARY:
- Credit Score: {result.get('credit_score', 'N/A')}
- Payment History: {result.get('payment_history_score', 'N/A')}
- Credit Utilization: {result.get('credit_utilization', 'N/A')}%
- Length of Credit History: {result.get('credit_history_months', 'N/A')} months
- Total Accounts: {result.get('total_accounts', 'N/A')}
- Recent Inquiries: {result.get('recent_inquiries', 'N/A')}
- Derogatory Marks: {result.get('derogatory_marks', 'N/A')}
- Bureau: {result.get('bureau', 'Mock Credit Bureau')}
"""
        
    except Exception as e:
        logger.error(f"Credit report API error: {e}")
        return f"Credit report failed: {str(e)}"

if __name__ == "__main__":
    import os
    import asyncio
    import uvicorn
    
    logger.info("🏦 Starting FastMCP Credit Check Server...")
    logger.info(" MCP Server starting (binding to 0.0.0.0 for ToolHive)")
    
    # Get port from environment
    port = int(os.environ.get('MCP_PORT', 8000))
    
    # Use uvicorn.Config and Server directly for full control over host binding
    config = uvicorn.Config(
        app=mcp.sse_app(),
        host="0.0.0.0",  # Bind to all interfaces for ToolHive
        port=port,
        log_level="info"
    )
    server = uvicorn.Server(config)
    
    # Run the server
    asyncio.run(server.serve())
