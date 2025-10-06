#!/bin/bash

# MCP Mortgage Business Rules - Build and Push to Quay.io
# This script builds the MCP server image and pushes it to quay.io

set -e

echo "🚀 Building and Pushing MCP Mortgage Business Rules Server to Quay.io"
echo "====================================================================="

# Configuration
IMAGE_NAME="quay.io/rbrhssa/mortgage-rule-mcp"
IMAGE_TAG="latest"
CONTAINERFILE="mcp-mortgage-business-rules-Containerfile"

# Check if we're in the right directory
if [ ! -f "$CONTAINERFILE" ]; then
    echo " Error: $CONTAINERFILE not found. Please run this script from the mcp/deploy directory."
    exit 1
fi

# Check if podman/docker is available
if command -v podman &> /dev/null; then
    BUILDER="podman"
    echo " Using Podman for building"
elif command -v docker &> /dev/null; then
    BUILDER="docker"
    echo " Using Docker for building"
else
    echo " Error: Neither Podman nor Docker found. Please install one of them."
    exit 1
fi

# Build the container image
echo "🔨 Building container image: $IMAGE_NAME:$IMAGE_TAG (x86 architecture)"
if [ "$BUILDER" = "podman" ]; then
    podman build --platform linux/amd64 -f "$CONTAINERFILE" -t "$IMAGE_NAME:$IMAGE_TAG" ../../
    echo " x86 Image built successfully with Podman"
else
    docker build --platform linux/amd64 -f "$CONTAINERFILE" -t "$IMAGE_NAME:$IMAGE_TAG" ../
    echo " x86 Image built successfully with Docker"
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

echo " Image pushed successfully to $IMAGE_NAME:$IMAGE_TAG"
echo ""
echo "🎉 Build and push completed!"
echo "📋 Next steps:"
echo "1. Deploy to OpenShift: ./mcp-deploy-only.sh"
echo "2. The image is now available at: $IMAGE_NAME:$IMAGE_TAG"
echo ""
echo "🔗 Your MCP server will connect to: bolt://mortgage-db:7687"
echo "📊 Database: mortgage (with 1273 business rule nodes)"
