# Credit Check MCP Server

This directory contains the complete implementation of a credit check MCP server for mortgage processing.

## Files

- **`mcp_credit_server.py`**: HTTP-based MCP server implementation using Flask
- **`mcp_fastmcp_server.py`**: Proper MCP server using FastMCP library with SSE transport
- **`mock_credit_api.py`**: Mock credit bureau API that provides realistic credit data
- **`start-mcp-server.sh`**: Startup script that orchestrates both services

## Architecture

The credit check MCP server consists of two components:

1. **Mock Credit API** (Flask, port 8081): Provides realistic credit bureau endpoints
2. **MCP Server** (FastMCP, port 8080): Exposes credit tools via MCP protocol

## Available Tools

### 1. Credit Score (`credit_score`)
- **Purpose**: Get credit scores for mortgage qualification
- **Input**: SSN, first_name, last_name, date_of_birth
- **Output**: Credit score, mortgage eligibility, risk factors

### 2. Identity Verification (`verify_identity`)
- **Purpose**: Verify borrower identity against credit file
- **Input**: SSN, first_name, last_name, date_of_birth
- **Output**: Identity verification status, confidence score, fraud indicators

### 3. Credit Report (`credit_report`)
- **Purpose**: Get detailed credit report for underwriting
- **Input**: SSN, first_name, last_name, date_of_birth
- **Output**: Comprehensive credit report with trade lines and payment history

## Usage

### Starting the Server
```bash
./start-mcp-server.sh
```

This will:
1. Start the Flask credit API on port 8081
2. Start the FastMCP server on port 8080
3. Verify both services are running

### Testing the Server
```bash
# Test health endpoint
curl http://localhost:8080/health

# Test credit score tool
curl -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -d '{"method": "tools/call", "params": {"name": "credit_score", "arguments": {"ssn": "123-45-6789"}}}'
```

### Integration with LangGraph
```python
from mcp.clients.langchain.mcp_integration import get_mcp_tools

# Get credit check tools
tools = get_mcp_tools()
```

## Mock Data

The server includes realistic mock credit profiles for testing:

- **SSN 123-45-6789**: Sarah Johnson (Credit Score: 742)
- **SSN 987-65-4321**: Michael Chen (Credit Score: 680)

For unknown SSNs, the server generates realistic random credit data.

## Deployment

### Docker
```bash
docker build -f ../../deployment/kubernetes/Containerfile.mcp-server -t mcp-credit-server .
docker run -p 8080:8080 mcp-credit-server
```

### Kubernetes
```bash
kubectl apply -f ../../deployment/kubernetes/
```

### OpenShift
```bash
oc apply -f ../../deployment/openshift/mcpserver-credit-check.yaml
```

## Configuration

The server can be configured via environment variables:

- `MCP_PORT`: Port for MCP server (default: 8080)
- `FLASK_DEBUG`: Enable Flask debug mode (default: false)
- `CREDIT_API_URL`: URL for credit API (default: http://localhost:8081)

## API Endpoints

### MCP Server (Port 8080)
- `GET /`: Server information
- `GET /health`: Health check
- `GET /mcp`: MCP tools discovery (SSE)

### Credit API (Port 8081)
- `GET /health`: Health check
- `POST /credit-score`: Get credit scores
- `POST /verify-identity`: Verify identity
- `POST /credit-report`: Get detailed credit report
- `GET /openapi.json`: OpenAPI specification

## Development

### Adding New Tools
1. Add the tool function to `mcp_fastmcp_server.py`
2. Update the mock API in `mock_credit_api.py` if needed
3. Test the integration

### Customizing Mock Data
Edit the `MOCK_CREDIT_PROFILES` dictionary in `mock_credit_api.py` to add or modify test data.

## Troubleshooting

### Common Issues

1. **Port conflicts**: Ensure ports 8080 and 8081 are available
2. **Dependencies**: Install required Python packages from requirements.txt
3. **Permissions**: Make sure `start-mcp-server.sh` is executable

### Logs
Check the console output for detailed error messages and status information.
