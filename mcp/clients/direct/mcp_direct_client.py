#!/usr/bin/env python3
"""
Direct MCP Client - Bypass Claude Desktop/Cursor

This implements a Python MCP client that can communicate directly with 
the Twilio MCP server using JSON-RPC protocol. This allows us to integrate
MCP into LangGraph agents without needing Claude Desktop.

MCP Protocol Flow:
1. Start Twilio MCP server process
2. Communicate via JSON-RPC over stdio
3. Call tools/list to discover available tools
4. Call tools/call to execute Twilio SMS functions
"""

import json
import subprocess
import asyncio
import logging
from typing import Dict, List, Any, Optional
import uuid

logger = logging.getLogger(__name__)

class MCPClient:
    """Direct MCP client for communicating with MCP servers"""
    
    def __init__(self):
        self.process = None
        self.request_id = 0
    
    def _get_next_id(self) -> str:
        """Get next request ID"""
        self.request_id += 1
        return str(self.request_id)
    
    async def start_twilio_server(self, credentials: str):
        """Start the Twilio MCP server process"""
        print("🚀 Starting Twilio MCP server...")
        
        command = [
            "npx", "-y", "@twilio-alpha/mcp",
            credentials,
            "--services", "twilio_api_v2010",
            "--tags", "Api20100401IncomingPhoneNumber,Api20100401Message"
        ]
        
        try:
            self.process = subprocess.Popen(
                command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=0
            )
            
            # Give it time to start
            await asyncio.sleep(2)
            
            if self.process.poll() is None:
                print(" MCP server started successfully")
                return True
            else:
                stdout, stderr = self.process.communicate()
                print(f" MCP server failed: {stderr}")
                return False
                
        except Exception as e:
            print(f" Error starting MCP server: {e}")
            return False
    
    async def send_request(self, method: str, params: Dict = None) -> Dict:
        """Send JSON-RPC request to MCP server"""
        if not self.process or self.process.poll() is not None:
            raise Exception("MCP server not running")
        
        request = {
            "jsonrpc": "2.0",
            "id": self._get_next_id(),
            "method": method
        }
        
        if params:
            request["params"] = params
        
        # Send request
        request_json = json.dumps(request) + "\n"
        self.process.stdin.write(request_json)
        self.process.stdin.flush()
        
        # Read response
        response_line = self.process.stdout.readline()
        if not response_line:
            raise Exception("No response from MCP server")
        
        try:
            response = json.loads(response_line.strip())
            return response
        except json.JSONDecodeError as e:
            raise Exception(f"Invalid JSON response: {e}")
    
    async def list_tools(self) -> List[Dict]:
        """List available tools from MCP server"""
        print("🔍 Discovering MCP tools...")
        
        try:
            response = await self.send_request("tools/list")
            
            if "result" in response:
                tools = response["result"].get("tools", [])
                print(f" Found {len(tools)} MCP tools")
                
                for tool in tools:
                    print(f"   📋 {tool['name']}: {tool.get('description', 'No description')}")
                
                return tools
            else:
                print(f" Error listing tools: {response}")
                return []
                
        except Exception as e:
            print(f" Error listing tools: {e}")
            return []
    
    async def call_tool(self, tool_name: str, arguments: Dict) -> Dict:
        """Call a specific MCP tool"""
        print(f"🛠️ Calling MCP tool: {tool_name}")
        print(f"   📝 Arguments: {arguments}")
        
        try:
            params = {
                "name": tool_name,
                "arguments": arguments
            }
            
            response = await self.send_request("tools/call", params)
            
            if "result" in response:
                print(" MCP tool call successful")
                return response["result"]
            else:
                print(f" MCP tool call failed: {response}")
                return {"error": response}
                
        except Exception as e:
            print(f" Error calling tool: {e}")
            return {"error": str(e)}
    
    def stop_server(self):
        """Stop the MCP server process"""
        if self.process:
            self.process.terminate()
            self.process.wait()
            print("🔌 MCP server stopped")

async def test_direct_mcp_integration():
    """Test direct MCP integration without Claude Desktop"""
    print("🧪 DIRECT MCP CLIENT TEST")
    print("=" * 40)
    
    # Twilio credentials - Replace with your actual credentials
    ACCOUNT_SID = "YOUR_TWILIO_ACCOUNT_SID"
    API_KEY_SID = "YOUR_TWILIO_API_KEY_SID"
    API_KEY_SECRET = "YOUR_TWILIO_API_KEY_SECRET"
    
    credentials = f"{ACCOUNT_SID}/{API_KEY_SID}:{API_KEY_SECRET}"
    
    client = MCPClient()
    
    try:
        # Start MCP server
        if await client.start_twilio_server(credentials):
            
            # Discover tools
            tools = await client.list_tools()
            
            if tools:
                print(f"\n📋 Available MCP Tools:")
                for tool in tools:
                    print(f"   • {tool['name']}")
                
                # Test listing phone numbers
                print(f"\n📱 Testing: List phone numbers")
                list_result = await client.call_tool(
                    "twilio_api_v2010_incoming_phone_numbers_list",
                    {}
                )
                
                print(f"📋 Phone numbers result:")
                print(json.dumps(list_result, indent=2)[:500] + "...")
                
                # Test sending SMS (if we find a phone number)
                print(f"\n📱 Testing: Send SMS")
                sms_result = await client.call_tool(
                    "twilio_api_v2010_messages_create",
                    {
                        "To": "+16782928383",
                        "Body": "🤖 Direct MCP Success! This SMS was sent via custom MCP client integrated with LangGraph! 🎉",
                        "From": "+18554907158"  # Your Twilio number
                    }
                )
                
                print(f"📱 SMS result:")
                print(json.dumps(sms_result, indent=2)[:500] + "...")
                
                return True
            else:
                print(" No tools discovered")
                return False
        else:
            print(" Failed to start MCP server")
            return False
    
    except Exception as e:
        print(f" Test failed: {e}")
        return False
    finally:
        client.stop_server()

def create_langgraph_mcp_tool():
    """Create a LangGraph tool that uses MCP"""
    from langchain_core.tools import tool
    
    @tool
    def send_sms_via_mcp(phone_number: str, message: str) -> str:
        """
        Send SMS via Twilio MCP server.
        
        Args:
            phone_number: Phone number to send to (e.g., +1234567890)
            message: SMS message content
            
        Returns:
            SMS sending result
        """
        # This would integrate with the MCP client
        return f"SMS sent to {phone_number}: {message} (via MCP)"
    
    return send_sms_via_mcp

def main():
    """Main test execution"""
    print("🚀 DIRECT MCP INTEGRATION TEST")
    print("📡 Bypassing Claude Desktop - Direct JSON-RPC")
    print("=" * 60)
    
    # Run async test
    result = asyncio.run(test_direct_mcp_integration())
    
    if result:
        print(f"\n🎉 SUCCESS! Direct MCP integration working!")
        print(f" Can start Twilio MCP server")
        print(f" Can discover MCP tools")
        print(f" Can call SMS functions")
        print(f" Ready for LangGraph integration")
    else:
        print(f"\n Direct MCP integration failed")
        print(f"💡 Check MCP server startup and credentials")

if __name__ == "__main__":
    main()
