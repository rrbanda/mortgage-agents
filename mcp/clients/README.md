# MCP Clients

This directory contains MCP client implementations for integrating MCP servers with the mortgage agent system.

## Directory Structure

```
clients/
├── README.md                    # This file
├── direct/                      # Direct MCP client implementations
│   ├── mcp_config.py           # MCP configuration management
│   └── mcp_direct_client.py    # Direct JSON-RPC MCP client
└── langchain/                   # LangChain MCP integration
    ├── mcp_tools.py            # LangChain tool wrappers
    └── mcp_integration.py      # Main MCP integration module
```

## Direct MCP Clients

### `mcp_config.py`
- **Purpose**: MCP configuration management and client setup
- **Features**:
  - Default MCP configuration creation
  - Twilio credentials management
  - MCP server startup and testing
  - Mock tool definitions for testing

### `mcp_direct_client.py`
- **Purpose**: Direct JSON-RPC communication with MCP servers
- **Features**:
  - Bypass Claude Desktop for direct MCP communication
  - JSON-RPC protocol implementation
  - Tool discovery and execution
  - Twilio MCP server integration

## LangChain Integration

### `mcp_integration.py`
- **Purpose**: Main MCP integration module for LangGraph agents
- **Features**:
  - MultiServerMCPClient integration
  - Tool loading and caching
  - Connection testing
  - Configuration-based server management

### `mcp_tools.py`
- **Purpose**: LangChain-compatible tool wrappers for MCP tools
- **Features**:
  - Twilio SMS tools via MCP
  - LangChain BaseTool compatibility
  - Input validation and error handling
  - Mock implementations for testing

## Usage Examples

### Direct MCP Client
```python
from mcp.clients.direct.mcp_direct_client import MCPClient

# Start Twilio MCP server
client = MCPClient()
await client.start_twilio_server(credentials)

# Discover tools
tools = await client.list_tools()

# Call tools
result = await client.call_tool("send_sms", {
    "to": "+1234567890",
    "body": "Hello from MCP!"
})
```

### LangChain Integration
```python
from mcp.clients.langchain.mcp_integration import get_mcp_tools

# Get MCP tools for agents
tools = get_mcp_tools()

# Use in LangGraph agent
agent = create_react_agent(llm, tools)
```

### MCP Configuration
```python
from mcp.clients.direct.mcp_config import setup_twilio_mcp

# Set up Twilio MCP with credentials
success = setup_twilio_mcp(
    account_sid="AC...",
    api_key="SK...",
    api_secret="..."
)
```

## Integration with Mortgage Agents

### Application Agent
```python
# In application_agent/__init__.py
from mcp.clients.langchain.mcp_integration import get_mcp_tools

def get_all_application_agent_tools() -> List[BaseTool]:
    # Get existing tools
    existing_tools = get_existing_tools()
    
    # Get MCP tools
    mcp_tools = get_mcp_tools()
    
    return existing_tools + mcp_tools
```

### Underwriting Agent
```python
# Credit check tools are automatically available via MCP
# No code changes needed - tools are discovered dynamically
```

## Configuration

### Environment Variables
- `MCP_CREDIT_CHECK_ENABLED`: Enable/disable credit check MCP
- `MCP_CREDIT_CHECK_URL`: URL for credit check MCP server
- `TWILIO_ACCOUNT_SID`: Twilio account SID
- `TWILIO_API_KEY`: Twilio API key
- `TWILIO_API_SECRET`: Twilio API secret

### Configuration File
The MCP client uses the main application configuration (`app/utils/config.py`) for settings.

## Testing

### Test MCP Connection
```python
from mcp.clients.langchain.mcp_integration import test_mcp_connection

# Test connection
connected = await test_mcp_connection()
print(f"MCP Connection: {'Connected' if connected else 'Failed'}")
```

### Test Direct Client
```python
from mcp.clients.direct.mcp_direct_client import test_direct_mcp_integration

# Run direct MCP test
result = await test_direct_mcp_integration()
```

## Error Handling

All MCP clients include comprehensive error handling:

- **Connection failures**: Graceful fallback to mock implementations
- **Tool execution errors**: Detailed error messages and logging
- **Configuration errors**: Clear error messages and validation
- **Network timeouts**: Configurable timeout settings

## Performance Considerations

- **Tool caching**: MCP tools are cached after first load
- **Connection pooling**: Reuse MCP server connections when possible
- **Async operations**: All MCP operations are asynchronous
- **Rate limiting**: Built-in rate limiting for external APIs

## Security

- **Credential management**: Secure storage of API credentials
- **Input validation**: All tool inputs are validated
- **Error sanitization**: Sensitive information is not exposed in errors
- **Network security**: HTTPS/TLS for all external communications

## Future Enhancements

- [ ] Additional MCP server integrations
- [ ] Enhanced error recovery
- [ ] Performance monitoring
- [ ] Advanced caching strategies
- [ ] Multi-tenant support
