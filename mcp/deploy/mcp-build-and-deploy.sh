#!/bin/bash

# MCP Mortgage Business Rules - Build and Deploy Script
# This script builds and deploys the MCP server to OpenShift

set -e

echo "🚀 Building and Deploying MCP Mortgage Business Rules Server"
echo "=============================================================="

# Configuration
IMAGE_NAME="mcp-mortgage-business-rules"
NAMESPACE="rh12026"
CONTAINERFILE="mcp-mortgage-business-rules-Containerfile"
DEPLOYMENT_FILE="mcp-mortgage-business-rules-deployment.yaml"

# Check if we're in the right directory
if [ ! -f "$CONTAINERFILE" ]; then
    echo " Error: $CONTAINERFILE not found. Please run this script from the mcp/deploy directory."
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

# Build the container image using Podman (x86 architecture)
echo "🔨 Building container image: $IMAGE_NAME (x86 architecture)"
if command -v podman &> /dev/null; then
    echo "Using Podman to build x86 image..."
    podman build --platform linux/amd64 -f "$CONTAINERFILE" -t "$IMAGE_NAME:latest" ../
    echo " x86 Image built successfully with Podman"
elif command -v docker &> /dev/null; then
    echo "Using Docker to build x86 image..."
    docker build --platform linux/amd64 -f "$CONTAINERFILE" -t "$IMAGE_NAME:latest" ../../
    echo " x86 Image built successfully with Docker"
else
    echo " Error: Neither Podman nor Docker found. Please install one of them."
    exit 1
fi

# Tag the image for OpenShift internal registry
echo "🏷️ Tagging image for OpenShift registry..."
REGISTRY_URL=$(oc get route default-route -n openshift-image-registry --template='{{ .spec.host }}' 2>/dev/null || echo "image-registry.openshift-image-registry.svc:5000")
FULL_IMAGE_NAME="$REGISTRY_URL/$NAMESPACE/$IMAGE_NAME:latest"

if command -v podman &> /dev/null; then
    podman tag "$IMAGE_NAME:latest" "$FULL_IMAGE_NAME"
    echo " Image tagged as: $FULL_IMAGE_NAME"
else
    docker tag "$IMAGE_NAME:latest" "$FULL_IMAGE_NAME"
    echo " Image tagged as: $FULL_IMAGE_NAME"
fi

# Push the image to OpenShift registry
echo "📤 Pushing image to OpenShift registry..."
if command -v podman &> /dev/null; then
    podman push "$FULL_IMAGE_NAME" --tls-verify=false
else
    docker push "$FULL_IMAGE_NAME"
fi
echo " Image pushed successfully"

# Update the deployment YAML with the correct image name
echo "📝 Updating deployment with image: $FULL_IMAGE_NAME"
sed -i.bak "s|image: mcp-mortgage-business-rules:latest|image: $FULL_IMAGE_NAME|g" "$DEPLOYMENT_FILE"

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

# Restore the original deployment file
mv "$DEPLOYMENT_FILE.bak" "$DEPLOYMENT_FILE" 2>/dev/null || true

echo " Deployment completed successfully!"
