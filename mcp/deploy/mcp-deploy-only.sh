#!/bin/bash

# MCP Mortgage Business Rules - Deploy Only Script
# This script deploys the pre-built MCP server image to OpenShift

set -e

echo "🚀 Deploying MCP Mortgage Business Rules Server (Pre-built Image)"
echo "=================================================================="

# Configuration
IMAGE_NAME="quay.io/rbrhssa/mortgage-rule-mcp:latest"
NAMESPACE="rh12026"
DEPLOYMENT_FILE="mcp-mortgage-business-rules-deployment.yaml"

# Check if we're in the right directory
if [ ! -f "$DEPLOYMENT_FILE" ]; then
    echo " Error: $DEPLOYMENT_FILE not found. Please run this script from the mcp/deploy directory."
    exit 1
fi

# Check if oc is available
if ! command -v oc &> /dev/null; then
    echo " Error: OpenShift CLI (oc) not found. Please install it first."
    exit 1
fi

# Check if we're logged into OpenShift
if ! oc whoami &> /dev/null; then
    echo " Error: Not logged into OpenShift. Please run 'oc login' first."
    exit 1
fi

echo " OpenShift CLI found and logged in as: $(oc whoami)"
echo "📦 Using pre-built image: $IMAGE_NAME"

# Deploy to OpenShift
echo "🚀 Deploying to OpenShift namespace: $NAMESPACE"
oc apply -f "$DEPLOYMENT_FILE"

# Wait for deployment to be ready
echo "⏳ Waiting for deployment to be ready..."
oc rollout status deployment/mcp-mortgage-business-rules -n "$NAMESPACE" --timeout=300s

# Get the route URL
echo "🌐 Getting the MCP server URL..."
ROUTE_URL=$(oc get route mcp-mortgage-business-rules-route -n "$NAMESPACE" -o jsonpath='{.spec.host}')
if [ -n "$ROUTE_URL" ]; then
    echo " MCP Server deployed successfully!"
    echo "🔗 MCP Server URL: https://$ROUTE_URL/mcp/"
    echo ""
    echo "📋 Next steps:"
    echo "1. Test the MCP server: curl -k https://$ROUTE_URL/mcp/"
    echo "2. Configure your agents to use this MCP server"
    echo "3. The server provides these tools:"
    echo "   - get_neo4j_schema: Get database schema"
    echo "   - read_neo4j_cypher: Execute read queries"
    echo ""
    echo "🎉 MCP Mortgage Business Rules Server is ready!"
else
    echo " Error: Could not get route URL"
    exit 1
fi

echo " Deployment completed successfully!"
