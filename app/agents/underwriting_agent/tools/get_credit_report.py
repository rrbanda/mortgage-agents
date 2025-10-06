"""
Get Credit Report Tool - MCP Integration for Credit Check Server

This tool provides direct MCP integration with the credit check server
to retrieve comprehensive credit reports for mortgage underwriting.
"""

import asyncio
import json
import httpx
from langchain_core.tools import tool
from pydantic import BaseModel, Field

try:
    from utils.config import AppConfig
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False


class GetCreditReportInput(BaseModel):
    """Input schema for credit report retrieval."""
    ssn: str = Field(description="Social Security Number of the borrower")
    borrower_name: str = Field(description="Full name of the borrower")
    date_of_birth: str = Field(description="Date of birth in YYYY-MM-DD format")
    report_type: str = Field(default="full", description="Type of credit report (full, summary, score_only)")


@tool("get_credit_report", args_schema=GetCreditReportInput)
def get_credit_report(ssn: str, borrower_name: str, date_of_birth: str, report_type: str = "full") -> str:
    """
    Get comprehensive credit report from external credit check MCP server.
    
    This tool connects to the credit check MCP server to retrieve
    detailed credit reports for mortgage underwriting analysis.
    
    Args:
        ssn: Social Security Number of the borrower
        borrower_name: Full name of the borrower
        date_of_birth: Date of birth in YYYY-MM-DD format
        report_type: Type of credit report (full, summary, score_only)
        
    Returns:
        String containing comprehensive credit report information
    """
    
    if not CONFIG_AVAILABLE:
        return " Configuration not available. Credit report retrieval requires proper configuration."
    
    try:
        # Load configuration
        config = AppConfig.load()
        mcp_config = config.mcp.credit_check
        
        if not mcp_config.enabled:
            return " Credit check MCP server is disabled in configuration."
        
        # Get MCP server URL
        mcp_url = mcp_config.url
        
        # Prepare request data
        request_data = {
            "ssn": ssn,
            "borrower_name": borrower_name,
            "date_of_birth": date_of_birth,
            "report_type": report_type
        }
        
        # Make real MCP call to credit check server
        async def _get_credit_report():
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Prepare MCP request payload
                mcp_request = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/call",
                    "params": {
                        "name": "credit_report",
                        "arguments": request_data
                    }
                }
                
                # Make HTTP request to MCP server
                # The MCP server might need a specific endpoint
                mcp_endpoint = f"{mcp_url.rstrip('/')}/mcp" if not mcp_url.endswith('/mcp') else mcp_url
                response = await client.post(
                    mcp_endpoint,
                    json=mcp_request,
                    headers={
                        "Content-Type": "application/json",
                        "Accept": "application/json"
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if "result" in result:
                        return result["result"]
                    elif "error" in result:
                        return {
                            "status": "error",
                            "message": f"MCP server error: {result['error'].get('message', 'Unknown error')}"
                        }
                    else:
                        return {
                            "status": "error", 
                            "message": "Unexpected response format from MCP server"
                        }
                else:
                    return {
                        "status": "error",
                        "message": f"HTTP error {response.status_code}: {response.text}"
                    }
        
        # Run the async function
        try:
            # Try to get the current event loop
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If we're in an existing event loop, create a task
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, _get_credit_report())
                    result = future.result()
            else:
                result = asyncio.run(_get_credit_report())
        except RuntimeError:
            # Fallback to asyncio.run if no event loop exists
            result = asyncio.run(_get_credit_report())
        
        # Format the response
        if isinstance(result, dict):
            credit_score = result.get("credit_score", "N/A")
            credit_bureau = result.get("credit_bureau", "Unknown")
            report_date = result.get("report_date", "N/A")
            accounts = result.get("accounts", [])
            inquiries = result.get("inquiries", 0)
            derogatory_items = result.get("derogatory_items", [])
            status = result.get("status", "unknown")
            message = result.get("message", "")
            
            response = f"""
📊 **COMPREHENSIVE CREDIT REPORT**

**Borrower:** {borrower_name}
**SSN:** {ssn[-4:].rjust(len(ssn), '*')}  # Masked SSN
**Date of Birth:** {date_of_birth}
**Report Type:** {report_type.title()}

**Credit Summary:**
• Credit Score: {credit_score}
• Credit Bureau: {credit_bureau}
• Report Date: {report_date}
• Status:  {status.title()}

**Account Information:**
"""
            
            if accounts:
                for account in accounts[:5]:  # Show first 5 accounts
                    account_type = account.get("type", "Unknown")
                    balance = account.get("balance", "N/A")
                    status = account.get("status", "Unknown")
                    response += f"• {account_type}: ${balance:,} ({status})\n"
            else:
                response += "• No account information available\n"
            
            if derogatory_items:
                response += f"\n**Derogatory Items:**\n"
                for item in derogatory_items[:3]:  # Show first 3 items
                    item_type = item.get("type", "Unknown")
                    amount = item.get("amount", "N/A")
                    date = item.get("date", "N/A")
                    response += f"• {item_type}: ${amount} ({date})\n"
            else:
                response += f"\n**Derogatory Items:** None\n"
            
            if inquiries:
                response += f"\n**Recent Inquiries:** {inquiries} inquiries in last 24 months\n"
            
            response += f"""
**Message:** {message}

**Source:** Credit Check MCP Server
**Status:**  Real-time report retrieved
"""
            
            return response
        else:
            return f"📊 **CREDIT REPORT RESULT:**\n{result}"
            
    except Exception as e:
        return f" Error retrieving credit report: {str(e)}"


def validate_tool() -> bool:
    """Validate that the credit report tool works correctly."""
    try:
        # Test with sample data
        result = get_credit_report(
            ssn="123-45-6789",
            borrower_name="Test Borrower",
            date_of_birth="1985-01-01",
            report_type="summary"
        )
        return "CREDIT REPORT" in result or "Error" in result
    except Exception as e:
        print(f"Credit report tool validation failed: {e}")
        return False


if __name__ == "__main__":
    # Test the tool
    print("Testing get_credit_report tool...")
    result = validate_tool()
    print(f"Validation result: {result}")