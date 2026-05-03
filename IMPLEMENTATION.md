# Banking Demo - Implementation Guide

This guide provides step-by-step instructions for deploying and testing the banking demonstration.

## 📋 Prerequisites

- watsonx Orchestrate environment (Developer Edition or Enterprise)
- Python 3.8 or higher
- `orchestrate` CLI tool installed and configured
- Access to watsonx Orchestrate workspace

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd banking-demo
pip install -r requirements.txt
```

### 2. Import All Artifacts

Run the automated import script:

```bash
./import-all.sh
```

This script will:
- Import the Cloudant connection
- Import all 3 standalone Python tool modules (Core Banking, Fraud Detection, Loan Processing)
- Import all 5 agents (Banking Orchestrator, Customer Service, Fraud Detection, Loan Processing, Compliance & Risk)
- Verify all imports were successful

### 3. Verify Installation

Check that the standalone tools are imported:
```bash
orchestrate tools list
```

Check that all tools are available:
```bash
orchestrate tools list | grep -E "(core-banking|fraud-detection|loan-processing)"
```

Check that all agents are imported:
```bash
orchestrate agents list
```

## 🧪 Testing the Demo

### Test Scenario 1: Simple Account Inquiry

**User**: "What's my current account balance?"

**Expected Flow**:
1. Banking Orchestrator routes to Customer Service Agent
2. Customer Service Agent uses `check_account_balance`
3. Returns balance for Emma Thompson's current account: £4,250.50

### Test Scenario 2: Fund Transfer

**User**: "Transfer £1,500 from my current account to my savings account"

**Expected Flow**:
1. Banking Orchestrator routes to Customer Service Agent
2. Customer Service Agent uses `transfer_funds`
3. Confirms transfer and shows new balances

### Test Scenario 3: Fraud Detection

**User**: "Analyze transaction TXN-FRAUD-001"

**Expected Flow**:
1. Banking Orchestrator routes to Fraud Detection Agent
2. Fraud Detection Agent uses `get_fraud_scenario`
3. Shows high-risk international transfer to Nigeria
4. Risk score: 92/100 - BLOCKED

### Test Scenario 4: Loan Application

**User**: "I'd like to apply for a £20,000 personal loan for home improvements"

**Expected Flow**:
1. Banking Orchestrator routes to Loan Processing Agent
2. Loan Processing Agent checks eligibility
3. Generates 3 personalized loan offers
4. Customer selects offer and initiates approval

## 📊 Demo Data

All demo data is stored in the `data/` directory:

- **customers.json** - 3 customer profiles (Emma, James, Sophie)
- **accounts.json** - 5 bank accounts with balances
- **transactions.json** - Recent transaction history
- **fraud_scenarios.json** - 3 fraud scenarios (high-risk, account takeover, legitimate)
- **loan_applications.json** - 3 loan applications (approved, pending, conditional)
- **credit_reports.json** - Credit bureau data
- **devices.json** - Known and suspicious devices

### Primary Demo Customer: Emma Thompson

- **Customer ID**: CUST-001
- **Current Account**: CUR-001-1234 (Balance: £4,250.50)
- **Savings Account**: SAV-001-5678 (Balance: £18,750.00)
- **Credit Card**: CC-001-9012 (Balance: £1,856.75)
- **Credit Score**: 742 (Good)
- **Annual Income**: £65,000

## 🏗️ Architecture

### Standalone Python Tool Modules

1. **Core Banking Tools** ([`cloudant-tools/core_banking_tools.py`](cloudant-tools/core_banking_tools.py))
   - Account balance checks
   - Transaction history
   - Fund transfers
   - Pending deposits
   - Payment due dates

2. **Fraud Detection Tools** ([`cloudant-tools/fraud_detection_tools.py`](cloudant-tools/fraud_detection_tools.py))
   - Transaction risk analysis
   - Customer profile checks
   - Device fingerprinting
   - Velocity rule checks
   - Transaction blocking
   - Fraud alerts and case creation

3. **Loan Processing Tools** ([`cloudant-tools/loan_processing_tools.py`](cloudant-tools/loan_processing_tools.py))
   - Loan eligibility calculation
   - Credit score checks
   - Debt-to-income ratio calculation
   - Loan offer generation
   - Approval workflow initiation
   - Document generation and e-signature

### Agents

1. **Banking Orchestrator Agent** - Primary customer interface, routes to specialists
2. **Customer Service Agent** - Account operations and support
3. **Fraud Detection Agent** - Real-time fraud monitoring
4. **Loan Processing Agent** - Loan applications and approvals
5. **Compliance & Risk Agent** - Regulatory compliance and risk assessment

## 🔧 Troubleshooting

### Standalone Tool Import/Configuration Issues

If standalone tools are unavailable or misconfigured:

```bash
# Re-import all required artifacts
cd banking-demo
./import-all.sh
```

### Tools Not Available

If tools are not showing up:

```bash
# Re-import standalone tools and related artifacts
./import-all.sh

# Verify tools are listed
orchestrate tools list
```

### Agent Not Responding

If an agent is not responding:

```bash
# Check agent status
orchestrate agents list

# Re-import the agent
orchestrate agents import -f agents/customer-service-agent.yaml
```

### Standalone Tool Configuration Issues

Ensure you're running commands from the `banking-demo` directory and that the Cloudant connection/import process has been completed:

```bash
cd banking-demo
./import-all.sh
```

## 📝 Next Steps

1. **Test All Demo Scenarios** - Try each of the 4 main scenarios
2. **Implement Guardrails** - Add the security guardrails from `plugins/` directory
3. **Create Test Cases** - Develop automated tests in `tests/` directory
4. **Customize Data** - Modify JSON files to create your own scenarios
5. **Add More Agents** - Extend with additional specialist agents

## 🎯 Demo Presentation Tips

1. **Start Simple** - Begin with account balance inquiry
2. **Show Multi-Step** - Demonstrate transfer + balance check
3. **Highlight Fraud** - Show real-time fraud detection blocking
4. **End with Loans** - Complete loan application workflow
5. **Emphasize ROI** - Reference the £32M+ savings and 1,200%+ ROI

## 📚 Additional Resources

- [Banking Demo Plan](docs/banking-demo-plan.md) - Complete architecture and use cases
- [Banking Demo Data](docs/banking-demo-data.md) - Detailed data specifications
- [Implementation Plan](docs/banking-demo-implementation-plan.md) - legacy architecture history and implementation background
- [Guardrail Validation](docs/banking-demo-guardrail-validation.md) - Security coverage

## 🆘 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the planning documents in `docs/`
3. Verify all prerequisites are met
4. Check watsonx Orchestrate logs for errors

---

**Status**: Implementation Complete ✅  
**Last Updated**: 2026-04-26  
**Version**: 1.0