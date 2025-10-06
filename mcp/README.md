# MCP (Model Context Protocol) Integration

This directory contains all MCP-related code for the Mortgage Agents system, organized for better maintainability and clarity.

## Directory Structure

```
mcp/
├── README.md                           # This file
├── servers/                            # MCP Server implementations
│   ├── credit-check/                   # Credit check MCP server
│   │   ├── mcp_credit_server.py        # HTTP-based MCP server
│   │   ├── mcp_fastmcp_server.py       # FastMCP implementation
│   │   ├── mock_credit_api.py          # Mock credit bureau API
│   │   └── start-mcp-server.sh         # Server startup script
│   ├── twilio/                         # Twilio MCP server (future)
│   └── document-processing/            # Document processing MCP server (future)
├── clients/                            # MCP Client implementations
│   ├── direct/                         # Direct MCP client implementations
│   │   ├── mcp_config.py               # MCP configuration management
│   │   └── mcp_direct_client.py        # Direct JSON-RPC MCP client
│   └── langchain/                      # LangChain MCP integration
│       ├── mcp_tools.py                # LangChain tool wrappers
│       └── mcp_integration.py          # Main MCP integration module
├── config/                             # MCP configuration files
│   └── credit-check-mcpfile.yaml       # MCP file format configuration
├── deployment/                         # Deployment configurations
│   ├── kubernetes/                     # Kubernetes deployment files
│   │   ├── Containerfile.mcp-server    # MCP server container definition
│   │   └── Containerfile.credit-api    # Credit API container definition
│   └── openshift/                      # OpenShift deployment files
│       └── mcpserver-credit-check.yaml # OpenShift MCPServer CR
├── docs/                               # Documentation
│   └── MCP_INTEGRATION_ANALYSIS.md     # Detailed MCP integration analysis
└── examples/                           # Example implementations
    ├── mcp_client_fixed.py             # Fixed MCP client example
    └── quick_test.py                   # Quick test examples
```

## Overview

The MCP integration provides:

1. **Credit Check MCP Server**: A complete MCP server implementation for credit bureau integration
2. **LangChain Integration**: Seamless integration with LangGraph agents
3. **Direct MCP Client**: Bypass Claude Desktop for direct MCP communication
4. **Deployment Ready**: Kubernetes and OpenShift deployment configurations

## Key Components

### Credit Check MCP Server
- **HTTP-based MCP server** (`mcp_credit_server.py`): Simple HTTP endpoints for MCP over HTTP
- **FastMCP server** (`mcp_fastmcp_server.py`): Proper MCP server using FastMCP library
- **Mock API** (`mock_credit_api.py`): Realistic mock credit bureau API for testing
- **Startup script** (`start-mcp-server.sh`): Orchestrates both Flask API and MCP server

### MCP Clients
- **Direct client** (`mcp_direct_client.py`): Direct JSON-RPC communication with MCP servers
- **LangChain integration** (`mcp_integration.py`): Integration with LangGraph agents
- **Tool wrappers** (`mcp_tools.py`): LangChain-compatible tool wrappers

### Configuration
- **MCP file** (`credit-check-mcpfile.yaml`): MCP file format specification for gen-mcp
- **Deployment configs**: Ready-to-deploy Kubernetes and OpenShift configurations

## Usage

### Starting the Credit Check MCP Server
```bash
cd mcp/servers/credit-check/
./start-mcp-server.sh
```

### Using MCP Tools in LangGraph Agents
```python
from mcp.clients.langchain.mcp_integration import get_mcp_tools

# Get MCP tools for agents
tools = get_mcp_tools()
```

### Direct MCP Client Usage
```python
from mcp.clients.direct.mcp_direct_client import MCPClient

client = MCPClient()
await client.start_twilio_server(credentials)
tools = await client.list_tools()
```

## Integration with Mortgage Agents

The MCP integration is designed to work seamlessly with the existing mortgage agent system:

1. **Application Agent**: Can use credit check MCP tools for initial qualification
2. **Underwriting Agent**: Can access detailed credit reports via MCP
3. **Document Agent**: Can integrate with document processing MCP servers
4. **Notification Agent**: Can use Twilio MCP for SMS communications

## Development

### Adding New MCP Servers
1. Create a new directory under `servers/`
2. Implement the MCP server following the existing patterns
3. Add configuration files to `config/`
4. Update deployment configurations in `deployment/`

### Testing
```bash
cd mcp/examples/
python quick_test.py
```

## Deployment

### Kubernetes
```bash
# Build and deploy MCP server
docker build -f mcp/deployment/kubernetes/Containerfile.mcp-server -t mcp-credit-server .
kubectl apply -f mcp/deployment/kubernetes/
```

### OpenShift
```bash
# Deploy using ToolHive MCPServer CR
oc apply -f mcp/deployment/openshift/mcpserver-credit-check.yaml
```

### Deployment Options
See `mcp/deployment/README.md` for detailed deployment options including:
- Monolithic MCP server deployment
- Microservice architecture deployment
- Environment configuration
- Security considerations

## Future Enhancements

- [ ] Twilio MCP server implementation
- [ ] Document processing MCP server
- [ ] Property data MCP server
- [ ] Income verification MCP server
- [ ] Enhanced authentication and authorization
- [ ] Rate limiting and cost management
- [ ] Monitoring and analytics
