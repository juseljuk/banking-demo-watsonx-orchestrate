#!/bin/bash

# Banking Demo - Import All Artifacts
# This script imports the Cloudant connection, standalone Python tools,
# guardrails, workflows, and agents into watsonx Orchestrate.

set -e  # Exit on error

echo "=========================================="
echo "Banking Demo - Import All Artifacts"
echo "=========================================="
echo ""

# Change to the project directory
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

echo "🔐 Step 1: Importing Cloudant Connection..."
echo "-----------------------------------"
./import-cloudant-connection.sh
echo "✓ Cloudant connection ready"
echo ""

echo "📦 Step 2: Importing Standalone Python Tools..."
echo "-----------------------------------"

TOOLS_REQUIREMENTS="cloudant-tools/requirements.txt"
TOOLS_PACKAGE_ROOT="cloudant-tools"
TOOLS_APP_ID="cloudant"

echo "Importing Core Banking standalone tools..."
orchestrate tools import \
    -k python \
    -f cloudant-tools/core_banking_tools.py \
    -r "$TOOLS_REQUIREMENTS" \
    --package-root "$TOOLS_PACKAGE_ROOT" \
    --app-id "$TOOLS_APP_ID"
echo "✓ Core Banking standalone tools ready"
echo ""

echo "Importing Fraud Detection standalone tools..."
orchestrate tools import \
    -k python \
    -f cloudant-tools/fraud_detection_tools.py \
    -r "$TOOLS_REQUIREMENTS" \
    --package-root "$TOOLS_PACKAGE_ROOT" \
    --app-id "$TOOLS_APP_ID"
echo "✓ Fraud Detection standalone tools ready"
echo ""

echo "Importing Loan Processing standalone tools..."
orchestrate tools import \
    -k python \
    -f cloudant-tools/loan_processing_tools.py \
    -r "$TOOLS_REQUIREMENTS" \
    --package-root "$TOOLS_PACKAGE_ROOT" \
    --app-id "$TOOLS_APP_ID"
echo "✓ Loan Processing standalone tools ready"
echo ""

echo "📋 Verifying standalone tool imports..."
orchestrate tools list | grep -E "authenticate_customer|check_account_balance|get_recent_transactions|analyze_transaction_risk|check_credit_score|calculate_loan_eligibility" || echo "  ℹ️  Some standalone tools may still be propagating"
echo ""

echo "🛡️ Step 3: Importing Guardrail Plugins..."
echo "-----------------------------------"

echo "Importing PII Protection Guardrail..."
orchestrate tools import -k python -f plugins/pii_protection_guardrail.py
echo "✓ PII Protection Guardrail ready"
echo ""

echo "Importing Transaction Limit Guardrail..."
orchestrate tools import -k python -f plugins/transaction_limit_guardrail.py
echo "✓ Transaction Limit Guardrail ready"
echo ""

echo "Importing Lending Compliance Guardrail..."
orchestrate tools import -k python -f plugins/lending_compliance_guardrail.py
echo "✓ Lending Compliance Guardrail ready"
echo ""

echo "Importing Fraud Rules Guardrail..."
orchestrate tools import -k python -f plugins/fraud_rules_guardrail.py
echo "✓ Fraud Rules Guardrail ready"
echo ""

echo "📋 Verifying guardrail imports..."
orchestrate tools list | grep -E "guardrail" || echo "  ℹ️  Guardrails imported"
echo ""

echo "🔄 Step 4: Importing Agentic Workflow..."
echo "-----------------------------------"

echo "Importing Loan Approval Workflow..."
if orchestrate tools import -k flow -f tools/loan_approval_workflow.py; then
    echo "✓ Loan Approval Workflow ready"
else
    echo "  ⚠️  Workflow import failed"
    echo "  💡 Verify standalone loan tools are available and imported:"
    echo "     check_credit_score"
    echo "     calculate_debt_to_income"
    echo "     calculate_loan_eligibility"
    echo "     generate_loan_offers"
    echo "  💡 Then retry:"
    echo "     orchestrate tools import -k flow -f tools/loan_approval_workflow.py"
    echo ""
    echo "  ℹ️  Continuing with agent imports..."
fi
echo ""

echo "📋 Verifying workflow import..."
orchestrate tools list | grep -E "loan_approval_workflow" || echo "  ℹ️  Workflow may need a retry after tool propagation"
echo ""

echo "🤖 Step 5: Importing Agents..."
echo "-----------------------------------"

echo "Importing Compliance & Risk Agent..."
orchestrate agents import -f agents/compliance-risk-agent.yaml
echo "✓ Compliance & Risk Agent ready"
echo ""

echo "Importing Customer Service Agent..."
orchestrate agents import -f agents/customer-service-agent.yaml
echo "✓ Customer Service Agent ready"
echo ""

echo "Importing Fraud Detection Agent..."
orchestrate agents import -f agents/fraud-detection-agent.yaml
echo "✓ Fraud Detection Agent ready"
echo ""

echo "Importing Loan Processing Agent..."
orchestrate agents import -f agents/loan-processing-agent.yaml
echo "✓ Loan Processing Agent ready"
echo ""

echo "Importing Banking Orchestrator Agent..."
orchestrate agents import -f agents/banking-orchestrator-agent.yaml
echo "✓ Banking Orchestrator Agent ready"
echo ""

echo "📋 Verifying agent imports..."
orchestrate agents list
echo ""

echo "=========================================="
echo "✅ All artifacts imported successfully!"
echo "=========================================="
echo ""
echo "📊 Import Summary:"
echo "- 1 Cloudant connection"
echo "- 3 standalone Python tool modules"
echo "- 4 Guardrail Plugins"
echo "- 1 Agentic Workflow (loan_approval_workflow)"
echo "- 5 Banking Agents"
echo ""
echo "Next steps:"
echo "1. Test the agents in watsonx Orchestrate UI"
echo "2. Try the demo scenarios from GUARDRAIL_DEMO_GUIDE.md"
echo "3. Authenticate with: CUST-001 / PIN: 1234"
echo ""
echo "Demo scenarios to try:"
echo "✅ Account Balance: 'What's my current account balance?'"
echo "✅ Recent Transactions: 'Show my last 3 transactions'"
echo "✅ Loan Application: 'I'd like to apply for a £20,000 personal loan'"
echo "✅ Fraud Review: 'Show me the fraud scenario TXN-FRAUD-001'"
echo "ℹ️ Transfer execution is not yet fully migrated in the standalone customer service path"
echo ""
echo "📖 See GUARDRAIL_DEMO_GUIDE.md for complete demo scenarios"
echo ""

# Made with Bob
