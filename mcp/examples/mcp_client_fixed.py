#!/usr/bin/env python3
"""
Fixed MCP Client - Proper JSON-RPC Protocol Handling

This handles the MCP protocol correctly by:
1. Filtering log notifications from actual responses
2. Implementing proper initialize handshake
3. Handling async JSON-RPC communication properly
"""

import json
import subprocess
import asyncio
import logging
from typing import Dict, List, Any, Optional
import time

logger = logging.getLogger(__name__)

class MCPClient:
    """Proper MCP client with correct JSON-RPC handling"""
    
    def __init__(self):
        self.process = None
        self.request_id = 0
        self.pending_requests = {}
        
    def _get_next_id(self) -> str:
        """Get next request ID"""
        self.request_id += 1
        return str(self.request_id)
    
    async def start_twilio_server(self, credentials: str):
        """Start Twilio MCP server with proper initialization"""
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
            
            await asyncio.sleep(3)  # Give server time to start
            
            if self.process.poll() is None:
                print(" MCP server process started")
                
                # Initialize the MCP connection
                return await self._initialize_connection()
            else:
                stdout, stderr = self.process.communicate()
                print(f" Server failed to start:")
                print(f"   stdout: {stdout[:200]}...")
                print(f"   stderr: {stderr[:200]}...")
                return False
                
        except Exception as e:
            print(f" Error starting server: {e}")
            return False
    
    async def _initialize_connection(self):
        """Initialize MCP connection with proper handshake"""
        print("🤝 Initializing MCP connection...")
        
        try:
            # Send initialize request
            init_request = {
                "jsonrpc": "2.0",
                "id": self._get_next_id(),
                "method": "initialize",
                "params": {
                    "protocolVersion": "0.1.0",
                    "capabilities": {
                        "roots": {
                            "listChanged": True
                        },
                        "sampling": {}
                    },
                    "clientInfo": {
                        "name": "LangGraph-MCP-Client",
                        "version": "1.0.0"
                    }
                }
            }
            
            # Send the request
            response = await self._send_request_and_wait(init_request)
            
            if response and "result" in response:
                print(" MCP connection initialized")
                print(f"   Server: {response['result'].get('serverInfo', {}).get('name', 'Unknown')}")
                return True
            else:
                print(f" Initialize failed: {response}")
                return False
                
        except Exception as e:
            print(f" Initialize error: {e}")
            return False
    
    async def _send_request_and_wait(self, request: Dict, timeout: int = 10) -> Dict:
        """Send request and wait for response, filtering out notifications"""
        if not self.process or self.process.poll() is not None:
            raise Exception("MCP server not running")
        
        request_id = request["id"]
        
        # Send request
        request_json = json.dumps(request) + "\n"
        self.process.stdin.write(request_json)
        self.process.stdin.flush()
        
        # Wait for response (filtering out notifications)
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                # Read line with timeout
                response_line = self.process.stdout.readline()
                if not response_line:
                    await asyncio.sleep(0.1)
                    continue
                
                response = json.loads(response_line.strip())
                
                # Check if this is a notification (no id) or log message
                if "id" not in response:
                    # This is a notification/log - ignore it
                    print(f"📋 Server log: {response.get('params', {}).get('message', 'Unknown')}")
                    continue
                
                # Check if this is our response
                if response.get("id") == request_id:
                    return response
                
            except json.JSONDecodeError:
                continue
            except Exception as e:
                print(f"⚠️  Error reading response: {e}")
                continue
            
            await asyncio.sleep(0.1)
        
        raise Exception(f"Timeout waiting for response to request {request_id}")
    
    async def list_tools(self) -> List[Dict]:
        """List available MCP tools"""
        print("🔍 Listing MCP tools...")
        
        try:
            request = {
                "jsonrpc": "2.0",
                "id": self._get_next_id(),
                "method": "tools/list",
                "params": {}
            }
            
            response = await self._send_request_and_wait(request)
            
            if "result" in response and "tools" in response["result"]:
                tools = response["result"]["tools"]
                print(f" Found {len(tools)} tools:")
                
                for tool in tools:
                    print(f"   📋 {tool['name']}")
                    print(f"      {tool.get('description', 'No description')}")
                
                return tools
            else:
                print(f" Tools list error: {response}")
                return []
                
        except Exception as e:
            print(f" Error listing tools: {e}")
            return []
    
    
    def stop_server(self):
        """Stop MCP server"""
        if self.process:
            self.process.terminate()
            self.process.wait(timeout=5)
            print("🔌 MCP server stopped")

async def test_real_mcp_sms():
    """Test real SMS sending via MCP"""
    print("📱 REAL MCP SMS TEST")
    print("=" * 30)
    
    credentials = "YOUR_ACCOUNT_SID/YOUR_API_KEY_SID:YOUR_API_KEY_SECRET"  # Replace with your Twilio credentials
    
    client = MCPClient()
    
    try:
        # Start and initialize
        if await client.start_twilio_server(credentials):
            
            # List available tools
            tools = await client.list_tools()
            
            # Find SMS tool
            sms_tool = None
            for tool in tools:
                if "CreateMessage" in tool["name"] or "message" in tool["name"].lower():
                    sms_tool = tool["name"]
                    break
            
            if sms_tool:
                print(f"🎯 Using SMS tool: {sms_tool}")
                
                # Send real SMS directly
                request = {
                    "jsonrpc": "2.0",
                    "id": client._get_next_id(),
                    "method": "tools/call", 
                    "params": {
                        "name": sms_tool,
                        "arguments": {
                            "To": "+16782928383",
                            "Body": "🎉 BREAKTHROUGH! Direct MCP integration working! Your LangGraph NotificationAgent can now send SMS via MCP protocol without Claude Desktop! 🤖📱",
                            "From": "+18554907158"
                        }
                    }
                }
                
                result = await client._send_request_and_wait(request)
                
                if "result" in result:
                    print(f" SMS sent successfully via MCP!")
                    if "content" in result["result"]:
                        for content in result["result"]["content"]:
                            if content.get("type") == "text":
                                print(f"📋 Response: {content['text'][:200]}...")
                    return True
                else:
                    print(f" SMS failed: {result}")
                    return False
                
            else:
                print(" No SMS tools found")
                
        return False
    
    finally:
        client.stop_server()

def main():
    """Main test"""
    print("🚀 DIRECT MCP CLIENT - FIXED PROTOCOL")
    print("📡 Proper JSON-RPC handling for MCP")
    print("=" * 60)
    
    result = asyncio.run(test_real_mcp_sms())
    
    if result:
        print(f"\n🎉 BREAKTHROUGH SUCCESS!")
        print(f" Direct MCP integration working!")
        print(f" No Claude Desktop needed!")
        print(f" Ready for LangGraph integration!")
        print(f" Real SMS sent via MCP!")
    else:
        print(f"\n🔧 Integration in progress...")
        print(f"   MCP protocol handling improved")

if __name__ == "__main__":
    main()
