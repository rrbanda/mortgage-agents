# Quick Start Guide

## Prerequisites

Before getting started, ensure you have the following installed:

- **gen-mcp binary**: [Download from GitHub releases](https://github.com/genmcp/gen-mcp/releases)
- **Python 3.11+**: [Download Python](https://www.python.org/downloads/)
- **Docker**: [Install Docker](https://docs.docker.com/get-docker/)
- **Docker Compose**: [Install Docker Compose](https://docs.docker.com/compose/install/)
- **Git**: [Install Git](https://git-scm.com/downloads)

## Quick Setup

### 1. Install gen-mcp

```bash
# Download gen-mcp binary (replace with latest version)
curl -L https://github.com/genmcp/gen-mcp/releases/latest/download/genmcp-linux-amd64 -o genmcp
chmod +x genmcp
sudo mv genmcp /usr/local/bin

# Verify installation
genmcp --version
```

### 2. Start Backend Services

```bash
# Start Neo4j and business rules backend using Docker Compose
docker-compose up -d

# Wait for services to be ready
docker-compose logs -f
```

### 3. Start gen-mcp Server

```bash
# Navigate to the spec directory
cd docs/mortgage-business-rules-mcp-spec

# Start gen-mcp server using our mcpfile.yaml
genmcp run -f mcpfile.yaml
```

The gen-mcp server will start on `http://localhost:8080` by default, and will proxy requests to the backend service on `http://localhost:3000`.

## Quick Test

### Test Application Intake Rules

```bash
curl -X POST http://localhost:8000/tools/evaluate_application_intake_rules \
  -H "Content-Type: application/json" \
  -d '{
    "application_data": {
      "personal_info": {
        "first_name": "John",
        "last_name": "Smith",
        "ssn": "123-45-6789",
        "phone": "555-123-4567",
        "email": "john@example.com"
      },
      "current_address": {
        "street": "123 Main St",
        "city": "Anytown",
        "state": "CA",
        "zip": "12345"
      },
      "employment": {
        "employer_name": "Acme Corp",
        "title": "Software Engineer",
        "monthly_income": 8000
      },
      "loan_details": {
        "loan_purpose": "purchase",
        "loan_amount": 400000,
        "property_address": "456 Oak Ave"
      },
      "financial": {
        "assets": 50000,
        "debts": 2000
      },
      "property_info": {
        "property_type": "single_family_detached",
        "occupancy_type": "primary_residence"
      }
    }
  }'
```

### Test Qualification Thresholds

```bash
curl -X POST http://localhost:8000/tools/check_qualification_thresholds \
  -H "Content-Type: application/json" \
  -d '{
    "qualification_data": {
      "credit_score": 720,
      "monthly_income": 8000,
      "monthly_debts": 2000,
      "down_payment_amount": 80000,
      "down_payment_percent": 0.20,
      "loan_amount": 400000,
      "property_value": 500000,
      "loan_purpose": "purchase",
      "property_type": "single_family_detached",
      "occupancy_type": "primary_residence"
    }
  }'
```

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# Neo4j Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
NEO4J_DATABASE=mortgage_rules

# Server Configuration
MCP_SERVER_PORT=8000
MCP_SERVER_HOST=0.0.0.0

# Logging
LOG_LEVEL=INFO
```

### Docker Compose Configuration

The `docker-compose.yml` file includes:

```yaml
version: '3.8'

services:
  neo4j:
    image: neo4j:5.13
    ports:
      - "7474:7474"
      - "7687:7687"
    environment:
      NEO4J_AUTH: neo4j/your_password
    volumes:
      - neo4j_data:/data
      - neo4j_logs:/logs

  mcp-server:
    build: .
    ports:
      - "8000:8000"
    environment:
      NEO4J_URI: bolt://neo4j:7687
      NEO4J_USER: neo4j
      NEO4J_PASSWORD: your_password
    depends_on:
      - neo4j

volumes:
  neo4j_data:
  neo4j_logs:
```

## Available Tools

The MCP server exposes 8 business rules tools:

1. **`evaluate_application_intake_rules`** - Application intake validation
2. **`check_qualification_thresholds`** - Qualification threshold evaluation
3. **`assess_credit_score_rules`** - Credit score assessment
4. **`evaluate_income_calculation_rules`** - Income calculation rules
5. **`check_document_verification_rules`** - Document verification
6. **`assess_underwriting_rules`** - Underwriting rules evaluation
7. **`evaluate_pricing_rules`** - Pricing rules evaluation
8. **`check_compliance_rules`** - Compliance rules checking

## MCP Protocol Usage

### Using MCP Client

```python
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    # Connect to MCP server
    server_params = StdioServerParameters(
        command="python",
        args=["src/mcp_server.py"]
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the session
            await session.initialize()
            
            # List available tools
            tools = await session.list_tools()
            print("Available tools:", tools)
            
            # Call a tool
            result = await session.call_tool(
                "evaluate_application_intake_rules",
                arguments={
                    "application_data": {
                        "personal_info": {
                            "first_name": "John",
                            "last_name": "Smith"
                        }
                        # ... other data
                    }
                }
            )
            print("Result:", result)

if __name__ == "__main__":
    asyncio.run(main())
```

### Using HTTP API

The server also exposes HTTP endpoints for each tool:

```bash
# Get OpenAPI specification
curl http://localhost:8000/openapi.json

# List available tools
curl http://localhost:8000/tools/

# Call a specific tool
curl -X POST http://localhost:8000/tools/evaluate_application_intake_rules \
  -H "Content-Type: application/json" \
  -d '{"application_data": {...}}'
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_tools/test_application_rules_tools.py

# Run with coverage
pytest --cov=src tests/
```

### Code Quality

```bash
# Format code
black src/ tests/

# Type checking
mypy src/

# Linting
flake8 src/ tests/
```

### Adding New Tools

1. Create tool implementation in `src/tools/`
2. Add input/output schemas in `src/schemas/`
3. Implement rule evaluator in `src/rules_engine/`
4. Add tests in `tests/test_tools/`
5. Update documentation

## Troubleshooting

### Common Issues

#### Neo4j Connection Issues

```bash
# Check Neo4j status
docker-compose ps neo4j

# Check Neo4j logs
docker-compose logs neo4j

# Test Neo4j connection
docker exec -it mortgage-business-rules-mcp-neo4j-1 cypher-shell -u neo4j -p your_password
```

#### MCP Server Issues

```bash
# Check server logs
python src/mcp_server.py --log-level DEBUG

# Test server health
curl http://localhost:8000/health

# Check server status
curl http://localhost:8000/status
```

#### Business Rules Issues

```bash
# Check if rules are loaded
python scripts/check_rules.py

# Reload rules
python scripts/load_rules.py --force

# Validate rules
python scripts/validate_rules.py
```

### Performance Issues

#### Slow Response Times

1. Check Neo4j query performance
2. Enable query caching
3. Optimize database indexes
4. Monitor server resources

#### High Memory Usage

1. Check for memory leaks
2. Optimize data structures
3. Implement connection pooling
4. Monitor garbage collection

### Getting Help

- **Documentation**: Check the full documentation in `docs/`
- **Issues**: Report issues on GitHub
- **Discussions**: Join discussions for questions
- **Support**: Contact support team for critical issues

## Next Steps

1. **Explore the API**: Try different tools and scenarios
2. **Read the Documentation**: Check the full specification
3. **Integrate with Your System**: Use the MCP protocol or HTTP API
4. **Customize Rules**: Modify business rules for your needs
5. **Contribute**: Help improve the project

## Resources

- **MCP Protocol**: [Model Context Protocol Documentation](https://modelcontextprotocol.io/)
- **GenMCP Framework**: [GenMCP GitHub Repository](https://github.com/genmcp/gen-mcp)
- **Neo4j Documentation**: [Neo4j Python Driver](https://neo4j.com/docs/python-manual/current/)
- **Pydantic Documentation**: [Pydantic Documentation](https://pydantic-docs.helpmanual.io/)
