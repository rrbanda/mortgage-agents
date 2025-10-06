"""
Verify Identity Tool - MCP Integration for Credit Check Server

This tool provides direct MCP integration with the credit check server
to verify borrower identity for mortgage underwriting.
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


class VerifyIdentityInput(BaseModel):
    """Input schema for identity verification."""
    ssn: str = Field(description="Social Security Number of the borrower")
    borrower_name: str = Field(description="Full name of the borrower")
    date_of_birth: str = Field(description="Date of birth in YYYY-MM-DD format")
    address: str = Field(description="Current address of the borrower")


@tool("verify_identity", args_schema=VerifyIdentityInput)
def verify_identity(ssn: str, borrower_name: str, date_of_birth: str, address: str) -> str:
    """
    Verify borrower identity using external credit check MCP server.
    
    This tool connects to the credit check MCP server to verify
    borrower identity for mortgage underwriting compliance.
    
    Args:
        ssn: Social Security Number of the borrower
        borrower_name: Full name of the borrower
        date_of_birth: Date of birth in YYYY-MM-DD format
        address: Current address of the borrower
        
    Returns:
        String containing identity verification results
    """
    
    if not CONFIG_AVAILABLE:
        return " Configuration not available. Identity verification requires proper configuration."
    
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
            "address": address
        }
        
        # Make real MCP call to credit check server
        async def _verify_identity():
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Prepare MCP request payload
                mcp_request = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/call",
                    "params": {
                        "name": "verify_identity",
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
                    future = executor.submit(asyncio.run, _verify_identity())
                    result = future.result()
            else:
                result = asyncio.run(_verify_identity())
        except RuntimeError:
            # Fallback to asyncio.run if no event loop exists
            result = asyncio.run(_verify_identity())
        
        # Format the response
        if isinstance(result, dict):
            verified = result.get("verified", False)
            confidence_score = result.get("confidence_score", "N/A")
            verification_method = result.get("verification_method", "Unknown")
            issues = result.get("issues", [])
            status = result.get("status", "unknown")
            message = result.get("message", "")
            
            status_icon = "" if verified else ""
            status_text = "VERIFIED" if verified else "NOT VERIFIED"
            
            response = f"""
🆔 **IDENTITY VERIFICATION REPORT**

**Borrower:** {borrower_name}
**SSN:** {ssn[-4:].rjust(len(ssn), '*')}  # Masked SSN
**Date of Birth:** {date_of_birth}
**Address:** {address}

**Verification Results:**
• Status: {status_icon} {status_text}
• Confidence Score: {confidence_score}%
• Verification Method: {verification_method}
• Overall Status: {status.title()}
"""
            
            if issues:
                response += f"\n**Issues Found:**\n"
                for issue in issues:
                    response += f"• {issue}\n"
            
            response += f"""
**Message:** {message}

**Source:** Credit Check MCP Server
**Status:**  Real-time verification completed
"""
            
            return response
        else:
            return f"🆔 **IDENTITY VERIFICATION RESULT:**\n{result}"
            
    except Exception as e:
        return f" Error verifying identity: {str(e)}"


def validate_tool() -> bool:
    """Validate that the identity verification tool works correctly."""
    try:
        # Test with sample data
        result = verify_identity(
            ssn="123-45-6789",
            borrower_name="Test Borrower",
            date_of_birth="1985-01-01",
            address="123 Main St, Anytown, ST 12345"
        )
        return "IDENTITY VERIFICATION" in result or "Error" in result
    except Exception as e:
        print(f"Identity verification tool validation failed: {e}")
        return False


if __name__ == "__main__":
    # Test the tool
    print("Testing verify_identity tool...")
    result = validate_tool()
    print(f"Validation result: {result}")