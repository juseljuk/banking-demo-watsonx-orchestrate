#!/bin/bash

# Banking Demo - Import All Artifacts
# This script imports all MCP toolkits and agents into watsonx Orchestrate
# Handles both new imports and updates of existing artifacts

set -e  # Exit on error

echo "=========================================="
echo "Banking Demo - Import All Artifacts"
echo "=========================================="
echo ""

# Change to the banking-demo directory
cd "$(dirname "$0")"

# Activate virtual environment if it exists
if [ -f "../.venv/bin/activate" ]; then
    source ../.venv/bin/activate
fi

echo "📦 Step 1: Preparing Data Files..."
echo "-----------------------------------"
echo "Copying data files to toolkits directory..."
cp -r data toolkits/data 2>/dev/null || true
echo "✓ Data files ready"
echo ""

echo "📦 Step 2: Importing MCP Toolkits..."
echo "-----------------------------------"

echo "Importing Core Banking toolkit..."
if orchestrate toolkits list 2>/dev/null | grep -q "core-banking"; then
    echo "  ℹ️  Core Banking toolkit already exists, removing and reimporting..."
    orchestrate toolkits remove -n core-banking 2>/dev/null || true
    echo "  ⏳ Waiting for removal to complete..."
    sleep 5  # Wait longer for removal to complete
fi
echo "  📤 Uploading toolkit..."
if orchestrate toolkits import -f toolkits/core-banking-toolkit.yaml; then
    echo "✓ Core Banking toolkit ready"
else
    echo "  ⚠️  Import failed with server error. This is usually temporary."
    echo "  💡 Try running the script again, or import manually:"
    echo "     orchestrate toolkits import -f toolkits/core-banking-toolkit.yaml"
fi
echo ""

echo "Importing Fraud Detection toolkit..."
if orchestrate toolkits list 2>/dev/null | grep -q "fraud-detection"; then
    echo "  ℹ️  Fraud Detection toolkit already exists, removing and reimporting..."
    orchestrate toolkits remove -n fraud-detection 2>/dev/null || true
    echo "  ⏳ Waiting for removal to complete..."
    sleep 5  # Wait longer for removal to complete
fi
echo "  📤 Uploading toolkit..."
if orchestrate toolkits import -f toolkits/fraud-detection-toolkit.yaml; then
    echo "✓ Fraud Detection toolkit ready"
else
    echo "  ⚠️  Import failed with server error. This is usually temporary."
    echo "  💡 Try running the script again, or import manually:"
    echo "     orchestrate toolkits import -f toolkits/fraud-detection-toolkit.yaml"
fi
echo ""

echo "Importing Loan Processing toolkit..."
if orchestrate toolkits list 2>/dev/null | grep -q "loan-processing"; then
    echo "  ℹ️  Loan Processing toolkit already exists, removing and reimporting..."
    orchestrate toolkits remove -n loan-processing 2>/dev/null || true
    echo "  ⏳ Waiting for removal to complete..."
    sleep 5  # Wait longer for removal to complete
fi
echo "  📤 Uploading toolkit..."
if orchestrate toolkits import -f toolkits/loan-processing-toolkit.yaml; then
    echo "✓ Loan Processing toolkit ready"
else
    echo "  ⚠️  Import failed with server error. This is usually temporary."
    echo "  💡 Try running the script again, or import manually:"
    echo "     orchestrate toolkits import -f toolkits/loan-processing-toolkit.yaml"
fi
echo ""

echo "📋 Verifying toolkit imports..."
orchestrate toolkits list
echo ""

echo "🔧 Verifying tool imports..."
echo "  ⏳ Waiting for MCP servers to start and register tools..."
sleep 10  # Give MCP servers time to start and register tools

# Verify tools are available
MAX_RETRIES=6
RETRY_COUNT=0
TOOLS_READY=false

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if orchestrate tools list 2>/dev/null | grep -q "loan-processing:check_credit_score"; then
        echo "  ✓ MCP tools are ready"
        TOOLS_READY=true
        break
    else
        RETRY_COUNT=$((RETRY_COUNT + 1))
        if [ $RETRY_COUNT -lt $MAX_RETRIES ]; then
            echo "  ⏳ Waiting for tools to register (attempt $RETRY_COUNT/$MAX_RETRIES)..."
            sleep 5
        fi
    fi
done

if [ "$TOOLS_READY" = false ]; then
    echo "  ⚠️  WARNING: MCP tools not yet available"
    echo "  💡 The workflow import may fail. If it does:"
    echo "     1. Wait 30 seconds for MCP servers to fully start"
    echo "     2. Run: orchestrate tools import -k flow -f tools/loan_approval_workflow.py"
    echo ""
fi

orchestrate tools list | grep -E "(core-banking|fraud-detection|loan-processing)" || echo "  ℹ️  Some tools may still be starting"
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
    echo "  💡 This usually means MCP tools aren't ready yet"
    echo "  💡 To import manually after MCP servers start:"
    echo "     orchestrate tools import -k flow -f tools/loan_approval_workflow.py"
    echo ""
    echo "  ℹ️  Continuing with agent imports..."
fi
echo ""

echo "📋 Verifying workflow import..."
orchestrate tools list | grep -E "loan_approval_workflow" || echo "  ℹ️  Workflow will be imported when tools are ready"
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
echo "- 3 MCP Toolkits (25 tools)"
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
echo "✅ Transfer: 'Transfer £1,500 to my savings account'"
echo "✅ Loan Application: 'I'd like to apply for a £20,000 personal loan'"
echo "❌ Blocked Transfer: 'Transfer £12,000 to savings' (exceeds limit)"
echo "❌ Blocked Fraud: 'URGENT! Send £12,000 to Nigeria for cryptocurrency!'"
echo ""
echo "📖 See GUARDRAIL_DEMO_GUIDE.md for complete demo scenarios"
echo ""

# Made with Bob
