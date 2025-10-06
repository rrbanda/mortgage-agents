# MCP Deployment Guide

This directory contains deployment configurations for MCP servers and related services.

## Directory Structure

```
deployment/
├── README.md                    # This file
├── kubernetes/                  # Kubernetes deployment files
│   ├── Containerfile.mcp-server # MCP server container definition
│   └── Containerfile.credit-api # Credit API container definition
└── openshift/                   # OpenShift deployment files
    └── mcpserver-credit-check.yaml # OpenShift MCPServer CR
```

## Container Files

### Containerfile.mcp-server
- **Purpose**: Builds the complete MCP server with both Flask API and FastMCP server
- **Services**: Runs both mock credit API (port 8081) and MCP server (port 8080)
- **Startup**: Uses `start-mcp-server.sh` to orchestrate both services
- **Use Case**: Full MCP server deployment with integrated credit API

### Containerfile.credit-api
- **Purpose**: Builds only the mock credit API service
- **Services**: Runs only the Flask credit API (port 8080)
- **Startup**: Directly runs `mock_credit_api.py`
- **Use Case**: Standalone credit API service or microservice architecture

## Deployment Options

### Option 1: Monolithic MCP Server (Recommended)
Use `Containerfile.mcp-server` for a complete MCP server deployment:

```bash
# Build the complete MCP server
docker build -f deployment/kubernetes/Containerfile.mcp-server -t mcp-credit-server .

# Run the complete MCP server
docker run -p 8080:8080 mcp-credit-server
```

**Benefits:**
- Single container deployment
- Simplified networking
- Easier to manage and scale
- Integrated health checks

### Option 2: Microservice Architecture
Use `Containerfile.credit-api` for separate credit API service:

```bash
# Build the credit API service
docker build -f deployment/kubernetes/Containerfile.credit-api -t credit-api .

# Run the credit API service
docker run -p 8080:8080 credit-api
```

**Benefits:**
- Separation of concerns
- Independent scaling
- Can be used by multiple MCP servers
- Better for complex architectures

## Kubernetes Deployment

### Using Containerfile.mcp-server
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mcp-credit-server
spec:
  replicas: 1
  selector:
    matchLabels:
      app: mcp-credit-server
  template:
    metadata:
      labels:
        app: mcp-credit-server
    spec:
      containers:
      - name: mcp-server
        image: mcp-credit-server:latest
        ports:
        - containerPort: 8080
        env:
        - name: MCP_PORT
          value: "8080"
        - name: FLASK_DEBUG
          value: "false"
```

### Using Containerfile.credit-api
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: credit-api
spec:
  replicas: 1
  selector:
    matchLabels:
      app: credit-api
  template:
    metadata:
      labels:
        app: credit-api
    spec:
      containers:
      - name: credit-api
        image: credit-api:latest
        ports:
        - containerPort: 8080
        env:
        - name: PORT
          value: "8080"
        - name: FLASK_DEBUG
          value: "false"
```

## OpenShift Deployment

The OpenShift deployment uses the ToolHive MCPServer custom resource:

```bash
# Deploy using OpenShift MCPServer CR
oc apply -f openshift/mcpserver-credit-check.yaml
```

This deployment:
- Uses the monolithic MCP server approach
- Leverages ToolHive's MCP server management
- Includes proper security contexts for OpenShift
- Provides health checks and monitoring

## Environment Variables

### MCP Server Container
- `MCP_PORT`: Port for MCP server (default: 8080)
- `FLASK_DEBUG`: Enable Flask debug mode (default: false)

### Credit API Container
- `PORT`: Port for Flask API (default: 8080)
- `FLASK_DEBUG`: Enable Flask debug mode (default: false)

## Health Checks

Both containers include health check endpoints:

### MCP Server Health Check
```bash
curl http://localhost:8080/health
```

### Credit API Health Check
```bash
curl http://localhost:8080/health
```

## Security Considerations

Both containers are configured with:
- Non-root user execution
- Minimal system dependencies
- Security-focused base images
- Proper file permissions

## Monitoring and Logging

### Logs
```bash
# View MCP server logs
docker logs <container-id>

# View credit API logs
docker logs <container-id>
```

### Health Monitoring
Both containers expose health check endpoints that can be monitored by:
- Kubernetes liveness/readiness probes
- OpenShift health checks
- External monitoring systems

## Troubleshooting

### Common Issues

1. **Port Conflicts**: Ensure ports 8080 and 8081 are available
2. **Permission Issues**: Check that containers run as non-root users
3. **Health Check Failures**: Verify that health endpoints are accessible
4. **Memory Issues**: Monitor container memory usage and adjust limits

### Debug Commands
```bash
# Check container status
docker ps

# View container logs
docker logs <container-id>

# Execute commands in container
docker exec -it <container-id> /bin/bash

# Check health endpoint
curl http://localhost:8080/health
```

## Scaling Considerations

### Horizontal Scaling
- MCP servers can be scaled horizontally
- Credit API can be scaled independently
- Use load balancers for multiple instances

### Resource Limits
Set appropriate resource limits based on usage:
```yaml
resources:
  limits:
    cpu: "200m"
    memory: "256Mi"
  requests:
    cpu: "100m"
    memory: "128Mi"
```
