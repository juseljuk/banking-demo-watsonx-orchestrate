#!/bin/bash

# Banking Demo - Import Cloudant Connection
# This script imports the Cloudant API key connection and sets credentials
# for watsonx Orchestrate using environment variables from cloudant-tools/.env
#
# Required environment variables:
#   CLOUDANT_URL
#   CLOUDANT_API_KEY

set -e

echo "=========================================="
echo "Banking Demo - Import Cloudant Connection"
echo "=========================================="
echo ""

cd "$(dirname "$0")"

# Activate virtual environment if it exists
if [ -f "../.venv/bin/activate" ]; then
    source ../.venv/bin/activate
fi

# Check if orchestrate CLI is available
if ! command -v orchestrate >/dev/null 2>&1; then
    echo "❌ Error: orchestrate CLI not found"
    echo "Please install: pip install ibm-watsonx-orchestrate"
    exit 1
fi

# Load local environment variables for convenience
if [ -f "cloudant-tools/.env" ]; then
    set -a
    source cloudant-tools/.env
    set +a
    echo "✓ Loaded environment from cloudant-tools/.env"
else
    echo "ℹ️  No cloudant-tools/.env file found; using current shell environment"
fi
echo ""

# Validate required variables
if [ -z "${CLOUDANT_URL:-}" ]; then
    echo "❌ Error: CLOUDANT_URL is not set"
    exit 1
fi

if [ -z "${CLOUDANT_API_KEY:-}" ]; then
    echo "❌ Error: CLOUDANT_API_KEY is not set"
    exit 1
fi

APP_ID="cloudant"
CONNECTION_FILE="connections/cloudant-connection.yaml"

echo "📦 Step 1: Importing connection definition..."
echo "-----------------------------------"
orchestrate connections import -f "$CONNECTION_FILE"
echo "✓ Connection definition imported"
echo ""

set_credentials_for_env() {
    local environment="$1"

    echo "🔐 Setting credentials for ${environment}..."
    orchestrate connections set-credentials \
        --app-id "$APP_ID" \
        --env "$environment" \
        --api-key "$CLOUDANT_API_KEY"
    echo "✓ Credentials set for ${environment}"
    echo ""
}

echo "📦 Step 2: Setting connection credentials..."
echo "-----------------------------------"
set_credentials_for_env "draft"
set_credentials_for_env "live"

echo "📋 Step 3: Verifying connection exists..."
echo "-----------------------------------"
orchestrate connections list
echo ""

echo "=========================================="
echo "✅ Cloudant connection ready"
echo "=========================================="
echo ""
echo "Connection app id: ${APP_ID}"
echo "Imported file: ${CONNECTION_FILE}"
echo ""
echo "Credentials configured:"
echo "- server_url from connections/cloudant-connection.yaml"
echo "- api_key"
echo ""

# Made with Bob