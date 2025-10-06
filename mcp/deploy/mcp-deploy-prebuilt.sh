#!/bin/bash

# 🚀 Deploy MCP Mortgage Business Rules Server (Pre-built Image)
# ==============================================================

set -e

# Configuration
NAMESPACE="rh12026"
DEPLOYMENT_FILE="mcp-mortgage-business-rules-deployment.yaml"

echo "🚀 Deploying MCP Mortgage Business Rules Server (Pre-built Image)"
echo "================================================================="

# Check if we're logged into OpenShift
if ! oc whoami &> /dev/null; then
    echo " Not logged into OpenShift. Please run 'oc login' first."
    exit 1
fi

echo " Logged into OpenShift as: $(oc whoami)"

# Check if namespace exists
if ! oc get namespace $NAMESPACE &> /dev/null; then
    echo " Namespace $NAMESPACE does not exist. Please create it first."
    exit 1
fi

echo " Namespace $NAMESPACE exists"

# Check if mortgage-db service exists
if ! oc get service mortgage-db -n $NAMESPACE &> /dev/null; then
    echo " Service 'mortgage-db' not found in namespace $NAMESPACE"
    echo "   Please ensure your Neo4j database is deployed and accessible."
    exit 1
fi

echo " Service 'mortgage-db' found in namespace $NAMESPACE"

# Check if mortgage-db-secret exists
if ! oc get secret mortgage-db-secret -n $NAMESPACE &> /dev/null; then
    echo " Secret 'mortgage-db-secret' not found in namespace $NAMESPACE"
    echo "   Please create the secret with the Neo4j password."
    exit 1
fi

echo " Secret 'mortgage-db-secret' found in namespace $NAMESPACE"

# Deploy the MCP server
echo "🔨 Deploying MCP server using pre-built image: mcp/neo4j-cypher:latest"
oc apply -f $DEPLOYMENT_FILE

echo "⏳ Waiting for deployment to be ready..."
oc rollout status deployment/mcp-mortgage-business-rules -n $NAMESPACE --timeout=300s

echo " Deployment completed successfully!"

# Get the route URL
ROUTE_URL=$(oc get route mcp-mortgage-business-rules-route -n $NAMESPACE -o jsonpath='{.spec.host}')
echo ""
echo "🌐 MCP Server is available at:"
echo "   HTTP: http://$ROUTE_URL/mcp/"
echo "   HTTPS: https://$ROUTE_URL/mcp/"
echo ""
echo "🔧 Test the server:"
echo "   curl -X POST https://$ROUTE_URL/mcp/ \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"jsonrpc\": \"2.0\", \"id\": 1, \"method\": \"tools/list\"}'"
echo ""
echo "🎉 MCP Mortgage Business Rules Server deployed successfully!"
