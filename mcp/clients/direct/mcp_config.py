"""
MCP (Model Context Protocol) Configuration for Mortgage Agents

This module provides MCP client integration for LangGraph agents, starting with 
Twilio Alpha MCP server integration for SMS/communication capabilities.
"""

import asyncio
import json
import subprocess
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
import tempfile
import os

logger = logging.getLogger(__name__)

class MCPClient:
    """
    MCP Client for integrating with various MCP servers.
    Initially focused on Twilio Alpha MCP server integration.
    """
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or self._create_default_config()
        self.mcp_tools = []
        
    def _create_default_config(self) -> str:
        """Create default MCP configuration for Twilio Alpha server"""
        config = {
            "mcpServers": {
                "twilio": {
                    "command": "npx",
                    "args": [
                        "-y", 
                        "@twilio-alpha/mcp",
                        "YOUR_TWILIO_ACCOUNT_SID/YOUR_TWILIO_API_KEY:YOUR_TWILIO_API_SECRET",
                        "--services",
                        "twilio_api_v2010",
                        "--tags", 
                        "Api20100401IncomingPhoneNumber,Api20100401Message"
                    ]
                }
            }
        }
        
        # Create temp config file
        config_path = Path(tempfile.gettempdir()) / "mcp_config.json"
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
            
        logger.info(f"Created MCP config at: {config_path}")
        return str(config_path)
    
    def update_twilio_credentials(self, account_sid: str, api_key: str, api_secret: str):
        """Update Twilio credentials in MCP configuration"""
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            
            # Update the Twilio server configuration
            twilio_creds = f"{account_sid}/{api_key}:{api_secret}"
            config["mcpServers"]["twilio"]["args"][2] = twilio_creds
            
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
                
            logger.info("Updated Twilio MCP credentials")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update Twilio credentials: {e}")
            return False
    
    async def start_mcp_server(self, server_name: str = "twilio") -> bool:
        """Start the specified MCP server"""
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            
            server_config = config["mcpServers"].get(server_name)
            if not server_config:
                logger.error(f"Server {server_name} not found in config")
                return False
            
            # For now, we'll use a subprocess approach
            # In production, you'd want a more robust MCP client implementation
            command = [server_config["command"]] + server_config["args"]
            
            logger.info(f"Starting MCP server {server_name} with command: {' '.join(command)}")
            
            # Test if the MCP server can start (we won't keep it running for now)
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Give it a moment to start
            await asyncio.sleep(2)
            
            if process.poll() is None:
                # Server is running, terminate for now
                process.terminate()
                logger.info(f"MCP server {server_name} started successfully (terminated for testing)")
                return True
            else:
                stdout, stderr = process.communicate()
                logger.error(f"MCP server failed to start: {stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error starting MCP server: {e}")
            return False
    
    def get_mock_twilio_tools(self) -> List[Dict[str, Any]]:
        """
        Get mock Twilio MCP tools for testing integration.
        In a full implementation, these would come from the actual MCP server.
        """
        return [
            {
                "name": "send_sms",
                "description": "Send SMS message to phone number",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "to": {
                            "type": "string",
                            "description": "Phone number to send SMS to"
                        },
                        "body": {
                            "type": "string", 
                            "description": "SMS message body"
                        }
                    },
                    "required": ["to", "body"]
                }
            },
            {
                "name": "list_phone_numbers",
                "description": "List active phone numbers in Twilio account",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "get_message_history",
                "description": "Get SMS message history for a phone number",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "phone_number": {
                            "type": "string",
                            "description": "Phone number to get history for"
                        }
                    },
                    "required": ["phone_number"]
                }
            }
        ]


# Singleton MCP client instance
_mcp_client = None

def get_mcp_client() -> MCPClient:
    """Get singleton MCP client instance"""
    global _mcp_client
    if _mcp_client is None:
        _mcp_client = MCPClient()
    return _mcp_client


def setup_twilio_mcp(account_sid: str, api_key: str, api_secret: str) -> bool:
    """
    Set up Twilio MCP server with provided credentials.
    Returns True if successful, False otherwise.
    """
    client = get_mcp_client()
    return client.update_twilio_credentials(account_sid, api_key, api_secret)


async def test_mcp_connection() -> Dict[str, Any]:
    """Test MCP server connection and tool availability"""
    client = get_mcp_client()
    
    result = {
        "config_created": os.path.exists(client.config_file),
        "server_started": False,
        "tools_available": 0,
        "error": None
    }
    
    try:
        # Test server startup
        result["server_started"] = await client.start_mcp_server()
        
        # Get available tools (mock for now)
        tools = client.get_mock_twilio_tools()
        result["tools_available"] = len(tools)
        
    except Exception as e:
        result["error"] = str(e)
        logger.error(f"MCP connection test failed: {e}")
    
    return result
