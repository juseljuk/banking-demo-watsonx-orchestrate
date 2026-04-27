#!/bin/bash

# Banking Demo - Import Script (NO GUARDRAILS VERSION)
# This script imports agents WITHOUT guardrails for "before" demonstrations
# WARNING: These agents should NEVER be used in production!

set -e

echo "=================================================="
echo "Banking Demo - Import Agents (NO GUARDRAILS)"
echo "=================================================="
echo ""
echo "⚠️  WARNING: This imports agents WITHOUT guardrails"
echo "   These are for DEMONSTRATION purposes only!"
echo "   NEVER use these in production environments!"
echo ""
echo "=================================================="
echo ""

# Check if orchestrate CLI is available
if ! command -v orchestrate &> /dev/null; then
    echo "❌ Error: orchestrate CLI not found"
    echo "Please install: pip install ibm-watsonx-orchestrate"
    exit 1
fi

# Check prerequisites
echo "🔍 Checking Prerequisites..."
echo ""

# Check if required toolkits exist
echo "  Checking for required toolkits..."
MISSING_TOOLKITS=0

if ! orchestrate toolkits list 2>/dev/null | grep -q "core-banking"; then
    echo "    ❌ core-banking toolkit not found"
    MISSING_TOOLKITS=1
fi

if ! orchestrate toolkits list 2>/dev/null | grep -q "loan-processing"; then
    echo "    ❌ loan-processing toolkit not found"
    MISSING_TOOLKITS=1
fi

if [ $MISSING_TOOLKITS -eq 1 ]; then
    echo ""
    echo "⚠️  ERROR: Required toolkits are missing!"
    echo ""
    echo "The 'no-guardrails' agents require the same toolkits as regular agents."
    echo "Please run ./import-all.sh first to import all toolkits."
    echo ""
    echo "If ./import-all.sh failed with a 500 error, try:"
    echo "  1. Wait 15 seconds and run ./import-all.sh again"
    echo "  2. Or import toolkits manually:"
    echo "     orchestrate toolkits import -f toolkits/core-banking-toolkit.yaml"
    echo "     orchestrate toolkits import -f toolkits/loan-processing-toolkit.yaml"
    echo ""
    exit 1
fi

echo "    ✅ All required toolkits found"
echo ""

# Import agents WITHOUT guardrails
echo "📦 Importing Agents (NO GUARDRAILS)..."
echo ""

echo "  → customer_service_agent_no_guardrails..."
if orchestrate agents import -f agents/customer-service-agent-no-guardrails.yaml; then
    echo "    ✅ Imported successfully"
else
    echo "    ❌ Failed to import"
    echo "    💡 Check that core-banking toolkit is properly imported"
    exit 1
fi

echo ""
echo "  → loan_processing_agent_no_guardrails..."
if orchestrate agents import -f agents/loan-processing-agent-no-guardrails.yaml; then
    echo "    ✅ Imported successfully"
else
    echo "    ❌ Failed to import"
    echo "    💡 Check that loan-processing toolkit is properly imported"
    echo "    💡 Try: orchestrate toolkits list | grep loan-processing"
    exit 1
fi

echo ""
echo "=================================================="
echo "✅ Import Complete (NO GUARDRAILS)"
echo "=================================================="
echo ""
echo "⚠️  IMPORTANT REMINDERS:"
echo ""
echo "1. These agents are for DEMONSTRATION only"
echo "2. They expose security and compliance vulnerabilities"
echo "3. Use them to show 'before' scenarios"
echo "4. Then switch to regular agents (with guardrails) for 'after' scenarios"
echo ""
echo "📖 Demo Guide: GUARDRAIL_BEFORE_AFTER_DEMO.md"
echo ""
echo "🔄 To import agents WITH guardrails, run:"
echo "   ./import-all.sh"
echo ""
echo "=================================================="

# Made with Bob
