# MCP Integration Index

Quick reference for all MCP-related files and their purposes.

## 🏗️ Server Implementations

| File | Location | Purpose |
|------|----------|---------|
| `mcp_credit_server.py` | `servers/credit-check/` | HTTP-based MCP server for credit checks |
| `mcp_fastmcp_server.py` | `servers/credit-check/` | FastMCP implementation with SSE transport |
| `mock_credit_api.py` | `servers/credit-check/` | Mock credit bureau API for testing |
| `start-mcp-server.sh` | `servers/credit-check/` | Server startup orchestration script |

## 🔌 Client Implementations

| File | Location | Purpose |
|------|----------|---------|
| `mcp_config.py` | `clients/direct/` | MCP configuration management |
| `mcp_direct_client.py` | `clients/direct/` | Direct JSON-RPC MCP client |
| `mcp_tools.py` | `clients/langchain/` | LangChain tool wrappers |
| `mcp_integration.py` | `clients/langchain/` | Main MCP integration module |

## ⚙️ Configuration Files

| File | Location | Purpose |
|------|----------|---------|
| `credit-check-mcpfile.yaml` | `config/` | MCP file format specification |

## 🚀 Deployment Files

| File | Location | Purpose |
|------|----------|---------|
| `Containerfile.mcp-server` | `deployment/kubernetes/` | MCP server Docker container definition |
| `Containerfile.credit-api` | `deployment/kubernetes/` | Credit API Docker container definition |
| `mcpserver-credit-check.yaml` | `deployment/openshift/` | OpenShift MCPServer CR |

## 📚 Documentation

| File | Location | Purpose |
|------|----------|---------|
| `MCP_INTEGRATION_ANALYSIS.md` | `docs/` | Detailed MCP integration analysis |
| `README.md` | `mcp/` | Main MCP integration overview |
| `README.md` | `servers/credit-check/` | Credit check server documentation |
| `README.md` | `clients/` | Client implementations documentation |
| `README.md` | `deployment/` | Deployment configurations and options |

## 🧪 Examples & Tests

| File | Location | Purpose |
|------|----------|---------|
| `mcp_client_fixed.py` | `examples/` | Fixed MCP client example |
| `quick_test.py` | `examples/` | Quick test examples |

## 🔗 Integration Points

### With Existing Mortgage Agents
- **Application Agent**: Uses credit check MCP tools for qualification
- **Underwriting Agent**: Accesses detailed credit reports via MCP
- **Document Agent**: Can integrate with document processing MCP servers
- **Notification Agent**: Can use Twilio MCP for SMS communications

### Import Paths (After Reorganization)
```python
# MCP Integration
from mcp.clients.langchain.mcp_integration import get_mcp_tools

# Direct MCP Client
from mcp.clients.direct.mcp_direct_client import MCPClient

# MCP Configuration
from mcp.clients.direct.mcp_config import setup_twilio_mcp

# MCP Tools
from mcp.clients.langchain.mcp_tools import get_twilio_mcp_tools
```

## 🚀 Quick Start

### 1. Start Credit Check MCP Server
```bash
cd mcp/servers/credit-check/
./start-mcp-server.sh
```

### 2. Test MCP Integration
```bash
cd mcp/examples/
python quick_test.py
```

### 3. Use in LangGraph Agents
```python
from mcp.clients.langchain.mcp_integration import get_mcp_tools
tools = get_mcp_tools()
```

## 📋 Available MCP Tools

### Credit Check Tools
- `credit_score`: Get credit scores for mortgage qualification
- `verify_identity`: Verify borrower identity against credit file
- `credit_report`: Get detailed credit report for underwriting

### Twilio Tools (Mock)
- `twilio_send_sms`: Send SMS messages via Twilio
- `twilio_list_phone_numbers`: List active phone numbers
- `twilio_message_history`: Get SMS message history

## 🔧 Configuration

### Environment Variables
- `MCP_CREDIT_CHECK_ENABLED`: Enable/disable credit check MCP
- `MCP_CREDIT_CHECK_URL`: URL for credit check MCP server
- `MCP_PORT`: Port for MCP server (default: 8080)
- `FLASK_DEBUG`: Enable Flask debug mode

### Configuration Files
- `app/utils/config.yaml`: Main application configuration
- `mcp/config/credit-check-mcpfile.yaml`: MCP file format specification

## 🐛 Troubleshooting

### Common Issues
1. **Import errors**: Update import paths to use new `mcp/` structure
2. **Port conflicts**: Ensure ports 8080 and 8081 are available
3. **Dependencies**: Install required packages from requirements.txt

### Debug Commands
```bash
# Check MCP server health
curl http://localhost:8080/health

# Test credit API
curl http://localhost:8081/health

# View MCP tools
curl http://localhost:8080/mcp
```

## 📈 Next Steps

1. **Update imports** in existing agent files to use new MCP structure
2. **Test integration** with existing mortgage agent workflow
3. **Deploy MCP servers** to Kubernetes/OpenShift
4. **Add more MCP servers** for additional integrations
5. **Implement authentication** and rate limiting
