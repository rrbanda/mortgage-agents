"""
Subprocess wrapper for MCP credit score calls.
This runs in a separate process to avoid LangGraph dev mode's strict async checking.
"""
import asyncio
import json
import sys


async def get_credit_via_mcp(mcp_url: str, ssn: str, borrower_name: str, date_of_birth: str):
    """Call MCP server to get credit score"""
    from mcp import ClientSession
    from mcp.client.sse import sse_client
    
    request_data = {
        "ssn": ssn,
        "borrower_name": borrower_name,
        "date_of_birth": date_of_birth
    }
    
    async with sse_client(mcp_url) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool("credit_score", request_data)
            
            if result.content and len(result.content) > 0:
                response_text = result.content[0].text
                
                # Parse credit score from response
                import re
                score_match = re.search(r'Credit Score:\s*(\d+)', response_text)
                
                if score_match:
                    return {
                        "status": "success",
                        "credit_score": int(score_match.group(1)),
                        "raw_response": response_text
                    }
            
            return {
                "status": "error",
                "message": "Could not parse MCP response"
            }


if __name__ == "__main__":
    # Read arguments from stdin as JSON
    input_data = json.loads(sys.stdin.read())
    
    # Run async function
    result = asyncio.run(get_credit_via_mcp(
        input_data["mcp_url"],
        input_data["ssn"],
        input_data["borrower_name"],
        input_data["date_of_birth"]
    ))
    
    # Output result as JSON
    print(json.dumps(result))
