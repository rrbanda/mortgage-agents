#!/bin/bash
#
# Script to add SMTP credentials to OpenShift/Kubernetes cluster
# This creates a secret and patches the deployment to use it
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "════════════════════════════════════════════════════════════"
echo "  SMTP SECRET SETUP FOR MORTGAGE-AGENTS"
echo "════════════════════════════════════════════════════════════"
echo ""

# Get namespace
NAMESPACE="${1:-rh12026}"
echo "📦 Using namespace: ${NAMESPACE}"
echo ""

# Check if secret already exists
if oc get secret mortgage-agents-smtp -n ${NAMESPACE} &> /dev/null; then
    echo -e "${YELLOW}⚠️  Secret 'mortgage-agents-smtp' already exists${NC}"
    read -p "Do you want to update it? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Exiting without changes."
        exit 0
    fi
    DELETE_EXISTING=true
else
    DELETE_EXISTING=false
fi

# Prompt for SMTP credentials
echo "Please enter your SMTP credentials:"
echo ""

read -p "SMTP Server (default: smtp.gmail.com): " SMTP_SERVER
SMTP_SERVER=${SMTP_SERVER:-smtp.gmail.com}

read -p "SMTP Port (default: 587): " SMTP_PORT
SMTP_PORT=${SMTP_PORT:-587}

read -p "SMTP User (your email): " SMTP_USER
if [ -z "$SMTP_USER" ]; then
    echo -e "${RED}❌ SMTP User is required${NC}"
    exit 1
fi

read -s -p "SMTP Password (App Password): " SMTP_PASSWORD
echo ""
if [ -z "$SMTP_PASSWORD" ]; then
    echo -e "${RED}❌ SMTP Password is required${NC}"
    exit 1
fi

read -p "From Email (default: ${SMTP_USER}): " SMTP_FROM_EMAIL
SMTP_FROM_EMAIL=${SMTP_FROM_EMAIL:-${SMTP_USER}}

read -p "From Name (default: Mortgage System): " SMTP_FROM_NAME
SMTP_FROM_NAME=${SMTP_FROM_NAME:-"Mortgage System"}

echo ""
echo "════════════════════════════════════════════════════════════"
echo "Configuration Summary:"
echo "════════════════════════════════════════════════════════════"
echo "  Server:     ${SMTP_SERVER}:${SMTP_PORT}"
echo "  User:       ${SMTP_USER}"
echo "  From Email: ${SMTP_FROM_EMAIL}"
echo "  From Name:  ${SMTP_FROM_NAME}"
echo "  Password:   ****************"
echo "════════════════════════════════════════════════════════════"
echo ""

read -p "Create/update this secret? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 0
fi

# Delete existing secret if needed
if [ "$DELETE_EXISTING" = true ]; then
    echo "🗑️  Deleting existing secret..."
    oc delete secret mortgage-agents-smtp -n ${NAMESPACE}
fi

# Create the secret
echo "🔐 Creating secret 'mortgage-agents-smtp'..."
oc create secret generic mortgage-agents-smtp \
  --from-literal=SMTP_SERVER="${SMTP_SERVER}" \
  --from-literal=SMTP_PORT="${SMTP_PORT}" \
  --from-literal=SMTP_USER="${SMTP_USER}" \
  --from-literal=SMTP_PASSWORD="${SMTP_PASSWORD}" \
  --from-literal=SMTP_FROM_EMAIL="${SMTP_FROM_EMAIL}" \
  --from-literal=SMTP_FROM_NAME="${SMTP_FROM_NAME}" \
  -n ${NAMESPACE}

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Secret created successfully!${NC}"
else
    echo -e "${RED}❌ Failed to create secret${NC}"
    exit 1
fi

echo ""
echo "════════════════════════════════════════════════════════════"
echo "  NEXT STEP: Update Deployment"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "To add these secrets to your deployment, run:"
echo ""
echo -e "${GREEN}  oc patch deployment mortgage-agents -n ${NAMESPACE} --type='json' -p='[${NC}"
echo -e "${GREEN}    {${NC}"
echo -e "${GREEN}      \"op\": \"add\",${NC}"
echo -e "${GREEN}      \"path\": \"/spec/template/spec/containers/0/envFrom\",${NC}"
echo -e "${GREEN}      \"value\": [{\"secretRef\": {\"name\": \"mortgage-agents-smtp\"}}]${NC}"
echo -e "${GREEN}    }${NC}"
echo -e "${GREEN}  ]'${NC}"
echo ""
echo "Or update your deployment YAML to include:"
echo ""
echo "  spec:"
echo "    template:"
echo "      spec:"
echo "        containers:"
echo "          - name: mortgage-agents"
echo "            envFrom:"
echo "              - secretRef:"
echo "                  name: mortgage-agents-smtp"
echo ""
echo "════════════════════════════════════════════════════════════"

