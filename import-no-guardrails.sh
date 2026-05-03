#!/bin/bash

# Banking Demo - Import Script (NO GUARDRAILS VERSION)
# This script imports agents WITHOUT guardrails for "before" demonstrations
# using the standalone Cloudant-backed Python tools.
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

cd "$(dirname "$0")"

# Activate virtual environment if it exists
if [ -f "../.venv/bin/activate" ]; then
    source ../.venv/bin/activate
fi

# Check if orchestrate CLI is available
if ! command -v orchestrate &> /dev/null; then
    echo "❌ Error: orchestrate CLI not found"
    echo "Please install: pip install ibm-watsonx-orchestrate"
    exit 1
fi

# Check prerequisites
echo "🔍 Checking Prerequisites..."
echo ""

echo "  Checking for required standalone tools..."
MISSING_TOOLS=0

check_required_tool() {
    local tool_name="$1"
    if ! orchestrate tools list 2>/dev/null | grep -q "$tool_name"; then
        echo "    ❌ ${tool_name} not found"
        MISSING_TOOLS=1
    fi
}

check_required_tool "authenticate_customer"
check_required_tool "get_customer_accounts"
check_required_tool "check_account_balance"
check_required_tool "get_recent_transactions"
check_required_tool "check_pending_deposits"
check_required_tool "check_credit_score"
check_required_tool "calculate_debt_to_income"
check_required_tool "get_loan_application"

if [ $MISSING_TOOLS -eq 1 ]; then
    echo ""
    echo "⚠️  ERROR: Required standalone tools are missing!"
    echo ""
    echo "The 'no-guardrails' agents require the same standalone Python tools as the regular agents."
    echo "Please run ./import-all.sh first to import the connection, standalone tools, workflow, and agents."
    echo ""
    echo "If needed, verify available tools with:"
    echo "  orchestrate tools list | grep -E 'authenticate_customer|get_customer_accounts|check_account_balance|check_credit_score'"
    echo ""
    exit 1
fi

echo "    ✅ All required standalone tools found"
echo ""

# Import agents WITHOUT guardrails
echo "📦 Importing Agents (NO GUARDRAILS)..."
echo ""

echo "  → banking_orchestrator_agent_no_guardrails..."
if orchestrate agents import -f agents/banking-orchestrator-agent-no-guardrails.yaml; then
    echo "    ✅ Imported successfully"
else
    echo "    ❌ Failed to import"
    echo "    💡 Check that standalone authentication tools are properly imported"
    exit 1
fi

echo ""
echo "  → customer_service_agent_no_guardrails..."
if orchestrate agents import -f agents/customer-service-agent-no-guardrails.yaml; then
    echo "    ✅ Imported successfully"
else
    echo "    ❌ Failed to import"
    echo "    💡 Check that standalone banking tools are properly imported"
    exit 1
fi

echo ""
echo "  → loan_processing_agent_no_guardrails..."
if orchestrate agents import -f agents/loan-processing-agent-no-guardrails.yaml; then
    echo "    ✅ Imported successfully"
else
    echo "    ❌ Failed to import"
    echo "    💡 Check that standalone loan tools and workflow are properly imported"
    echo "    💡 Try: orchestrate tools list | grep -E 'check_credit_score|calculate_debt_to_income|loan_approval_workflow'"
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
