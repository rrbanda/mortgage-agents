#!/bin/bash

# Credit Check MCP - Build and Push to Quay.io
# This script builds the Mock Credit API image and pushes it to quay.io
# This is SEPARATE from mortgage-business-rules MCP

set -e

echo "🏦 Building and Pushing Mock Credit API to Quay.io"
echo "====================================================================="

# Configuration
IMAGE_NAME="quay.io/rbrhssa/mcp-credit"
IMAGE_TAG="v3.13-mcp-server-v4"  # Simple streamable-http MCP server
CONTAINERFILE="../../deployment/kubernetes/Containerfile.credit-api"

# Check if we're in the right directory
if [ ! -f "$CONTAINERFILE" ]; then
    echo "❌ Error: $CONTAINERFILE not found."
    echo "   Please run this script from: mcp/servers/credit-check/"
    exit 1
fi

if [ ! -f "mock_credit_api.py" ]; then
    echo "❌ Error: mock_credit_api.py not found."
    echo "   Please run this script from: mcp/servers/credit-check/"
    exit 1
fi

# Check if podman/docker is available
if command -v podman &> /dev/null; then
    BUILDER="podman"
    echo "✅ Using Podman for building"
elif command -v docker &> /dev/null; then
    BUILDER="docker"
    echo "✅ Using Docker for building"
else
    echo "❌ Error: Neither Podman nor Docker found. Please install one of them."
    exit 1
fi

# Build the container image
echo ""
echo "🔨 Building container image: $IMAGE_NAME:$IMAGE_TAG"
echo "   Platform: linux/amd64"
echo "   Context: $(pwd)"
echo ""

if [ "$BUILDER" = "podman" ]; then
    podman build \
        --platform linux/amd64 \
        -f "$CONTAINERFILE" \
        -t "$IMAGE_NAME:$IMAGE_TAG" \
        .
    echo "✅ Image built successfully with Podman"
else
    docker build \
        --platform linux/amd64 \
        -f "$CONTAINERFILE" \
        -t "$IMAGE_NAME:$IMAGE_TAG" \
        .
    echo "✅ Image built successfully with Docker"
fi

# Ask user if they want to push
echo ""
read -p "🚀 Push image to quay.io? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "⏸️  Build complete. Image NOT pushed."
    echo "   To push later, run: $BUILDER push $IMAGE_NAME:$IMAGE_TAG"
    exit 0
fi

# Login to quay.io
echo "🔐 Logging into quay.io..."
if [ "$BUILDER" = "podman" ]; then
    podman login quay.io
else
    docker login quay.io
fi

# Push the image to quay.io
echo "📤 Pushing image to quay.io..."
if [ "$BUILDER" = "podman" ]; then
    podman push "$IMAGE_NAME:$IMAGE_TAG"
else
    docker push "$IMAGE_NAME:$IMAGE_TAG"
fi

echo ""
echo "✅ Image pushed successfully to $IMAGE_NAME:$IMAGE_TAG"
echo ""
echo "🎉 Build and push completed!"
echo ""
echo "📋 Next steps:"
echo "1. Update OpenShift deployment (if needed):"
echo "   oc apply -f ../../deployment/openshift/mcpserver-credit-check.yaml"
echo ""
echo "2. Verify deployment:"
echo "   oc get mcpserver credit-check -n rh12026"
echo ""
echo "3. Test the credit API:"
echo "   curl -X POST https://[your-route]/credit-score -H 'Content-Type: application/json' -d '{\"ssn\": \"987-65-4321\", \"first_name\": \"Sarah\", \"last_name\": \"Johnson\"}'"
echo ""
echo "🔗 Updated Mock Data:"
echo "   • Sarah Johnson (987-65-4321, DOB 1990-05-20) → Credit Score: 742 ✅"
echo "   • Identity Verification: WILL PASS (100% confidence)"
echo ""

