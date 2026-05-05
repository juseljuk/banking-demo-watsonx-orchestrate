# Banking Demo - Implementation Guide

This guide provides step-by-step instructions for deploying and testing the banking demonstration with Cloudant-backed Python tools.

## 📋 Prerequisites

- watsonx Orchestrate environment (Developer Edition or Enterprise)
- Python 3.8 or higher
- `orchestrate` CLI tool installed and configured
- Access to watsonx Orchestrate workspace
- IBM Cloudant instance (or use Developer Edition built-in Cloudant)

## 🚀 Quick Start

### 1. Set Up Cloudant

#### Option A: Using Developer Edition (Recommended)
Developer Edition includes built-in Cloudant - no additional setup needed.

#### Option B: Using IBM Cloud Cloudant
1. Create Cloudant instance in IBM Cloud
2. Generate API key with read/write permissions
3. Note your Cloudant URL and API key

### 2. Bootstrap Cloudant Databases

Run the bootstrap script to create databases and seed initial data:

```bash
cd banking-demo
python cloudant-tools/scripts/bootstrap_and_seed.py
```

This will:
- Create 8 Cloudant databases (customers, accounts, transactions, credit, devices, fraud, loans, audit)
- Create query indexes for performance
- Seed databases with demo data from `data/` folder

### 3. Configure Cloudant Connection

```bash
# Import connection configuration
orchestrate connections import -f connections/cloudant-connection.yaml

# Configure connection (draft environment)
orchestrate connections configure --app-id cloudant --env draft --type team --kind key_value

# Set credentials
orchestrate connections set-credentials --app-id cloudant --env draft --entries "api_key=$CLOUDANT_API_KEY"

# Repeat for live environment
orchestrate connections configure --app-id cloudant --env live --type team --kind key_value
orchestrate connections set-credentials --app-id cloudant --env live --entries "api_key=$CLOUDANT_API_KEY"
```

### 4. Import All Artifacts

Run the automated import script:

```bash
./import-all.sh
```

This script will:
- Import the Cloudant connection
- Import all 3 standalone Python tool modules (Core Banking, Fraud Detection, Loan Processing)
- Import the loan approval workflow
- Import all 4 guardrail plugins
- Import all 5 agents (Banking Orchestrator, Customer Service, Fraud Detection, Loan Processing, Compliance & Risk)
- Verify all imports were successful

### 5. Verify Installation

Check that the standalone tools are imported:
```bash
orchestrate tools list
```

Check that all tools are available:
```bash
orchestrate tools list | grep -E "(authenticate_customer|check_account_balance|analyze_transaction_risk|check_credit_score)"
```

Check that all agents are imported:
```bash
orchestrate agents list
```

## 🧪 Testing the Demo

### Test Scenario 1: Authentication & Account Inquiry

**User**: "What's my current account balance?"

**Expected Flow**:
1. Banking Orchestrator asks for Customer ID and PIN
2. User provides: "CUST-001 and 1234"
3. Orchestrator calls `authenticate_customer` tool
4. Cloudant validates credentials
5. Orchestrator calls `get_customer_accounts` with customer_id
6. Routes to Customer Service Agent with customer_id
7. Customer Service Agent uses `check_account_balance`
8. Returns balance for Emma Thompson's current account: £4,250.50

### Test Scenario 2: Fraud Detection

**User**: "Analyze transaction TXN-FRAUD-001"

**Expected Flow**:
1. Banking Orchestrator routes to Fraud Detection Agent
2. Fraud Detection Agent uses `analyze_transaction_risk`
3. Queries Cloudant fraud database
4. Shows high-risk international transfer to Nigeria
5. Risk score: 92/100 - BLOCKED
6. Guardrail automatically blocks critical risk transactions

### Test Scenario 3: Loan Application

**User**: "I'd like to apply for a £20,000 personal loan for home improvements"

**Expected Flow**:
1. Banking Orchestrator authenticates customer
2. Routes to Loan Processing Agent
3. Loan Processing Agent uses loan approval workflow
4. Workflow checks credit score via Cloudant
5. Calculates debt-to-income ratio
6. Generates 3 personalized loan offers
7. Returns eligibility: Up to £32,500 approved

### Test Scenario 4: Multi-Step with Guardrails

**User**: "Transfer £15,000 to my savings account"

**Expected Flow**:
1. Transaction Limit Guardrail checks daily limit (£10,000 for current accounts)
2. Blocks transaction as it exceeds limit
3. Returns: "This transfer exceeds your daily limit of £10,000"
4. Suggests splitting into multiple transactions

## 📊 Demo Data

All demo data is seeded into Cloudant from the `data/` directory:

- **customers.json** → Cloudant `customers` database - 3 customer profiles with PINs
- **accounts.json** → Cloudant `accounts` database - 5 bank accounts with balances
- **transactions.json** → Cloudant `transactions` database - Recent transaction history
- **fraud_scenarios.json** → Cloudant `fraud` database - 3 fraud scenarios
- **loan_applications.json** → Cloudant `loans` database - 3 loan applications
- **credit_reports.json** → Cloudant `credit` database - Credit bureau data
- **devices.json** → Cloudant `devices` database - Known and suspicious devices

### Primary Demo Customer: Emma Thompson

- **Customer ID**: CUST-001
- **PIN**: 1234
- **Current Account**: CUR-001-1234 (Balance: £4,250.50)
- **Savings Account**: SAV-001-5678 (Balance: £18,750.00)
- **Credit Card**: CC-001-9012 (Balance: £1,856.75)
- **Credit Score**: 742 (Good)
- **Annual Income**: £65,000

## 🏗️ Architecture

### Standalone Python Tool Modules

1. **Core Banking Tools** ([`cloudant-tools/core_banking_tools.py`](cloudant-tools/core_banking_tools.py))
   - `authenticate_customer` - Customer authentication with PIN
   - `get_customer_accounts` - Retrieve customer accounts
   - `check_account_balance` - Account balance checks
   - `get_recent_transactions` - Transaction history
   - `check_pending_deposits` - Pending deposits
   - Plus 3 more tools

2. **Fraud Detection Tools** ([`cloudant-tools/fraud_detection_tools.py`](cloudant-tools/fraud_detection_tools.py))
   - `analyze_transaction_risk` - Real-time risk scoring
   - `check_fraud_history` - Customer fraud history
   - `verify_device` - Device fingerprinting
   - `check_velocity_rules` - Velocity checks
   - `block_transaction` - Transaction blocking
   - Plus 3 more tools

3. **Loan Processing Tools** ([`cloudant-tools/loan_processing_tools.py`](cloudant-tools/loan_processing_tools.py))
   - `check_credit_score` - Credit bureau integration
   - `calculate_debt_to_income` - DTI calculation
   - `check_loan_eligibility` - Eligibility assessment
   - `generate_loan_offers` - Offer generation
   - Plus 5 more tools

### Agentic Workflows

1. **Loan Approval Workflow** ([`tools/loan_approval_workflow.py`](tools/loan_approval_workflow.py))
   - Deterministic multi-step loan processing
   - Credit score checking
   - Debt-to-income calculation
   - Eligibility assessment
   - Automated offer generation
   - 60% faster than agent-based approach

### Guardrail Plugins

1. **PII Protection** ([`plugins/pii_protection_guardrail.py`](plugins/pii_protection_guardrail.py))
   - Post-invoke guardrail
   - Redacts account numbers, NI numbers, emails, phones, credit cards

2. **Transaction Limits** ([`plugins/transaction_limit_guardrail.py`](plugins/transaction_limit_guardrail.py))
   - Pre-invoke guardrail
   - Enforces daily and single transaction limits

3. **Lending Compliance** ([`plugins/lending_compliance_guardrail.py`](plugins/lending_compliance_guardrail.py))
   - Pre-invoke guardrail
   - FCA CONC 5.2A compliance checks

4. **Fraud Rules** ([`plugins/fraud_rules_guardrail.py`](plugins/fraud_rules_guardrail.py))
   - Pre-invoke guardrail
   - Risk scoring with automatic blocking

### Agents

1. **Banking Orchestrator Agent** - Primary customer interface, authentication, routing
2. **Customer Service Agent** - Account operations and support
3. **Fraud Detection Agent** - Real-time fraud monitoring
4. **Loan Processing Agent** - Loan applications and approvals
5. **Compliance & Risk Agent** - Regulatory compliance and risk assessment

### Data Layer

**IBM Cloudant (8 Databases)**:
- `customers` - Customer profiles and authentication
- `accounts` - Account details and balances
- `transactions` - Transaction history
- `credit` - Credit reports and scores
- `devices` - Device fingerprints
- `fraud` - Fraud cases and risk analysis
- `loans` - Loan applications and offers
- `audit` - Audit logs and compliance records

**Repository Layer**:
- `CustomerRepository` - Customer data access
- `AccountRepository` - Account data access
- `TransactionRepository` - Transaction data access
- `CreditReportRepository` - Credit data access
- `DeviceRepository` - Device data access
- `FraudCaseRepository` - Fraud case data access
- `LoanApplicationRepository` - Loan data access

## 🔧 Troubleshooting

### Cloudant Connection Issues

If tools can't connect to Cloudant:

```bash
# Verify connection exists
orchestrate connections list | grep cloudant

# Re-import connection
orchestrate connections import -f connections/cloudant-connection.yaml

# Reconfigure credentials
orchestrate connections set-credentials --app-id cloudant --env draft --entries "api_key=$CLOUDANT_API_KEY"
```

### Database Not Found Errors

If you see "database not found" errors:

```bash
# Re-run bootstrap script
cd banking-demo
python cloudant-tools/scripts/bootstrap_and_seed.py
```

### Tools Not Available

If tools are not showing up:

```bash
# Re-import tools
orchestrate tools import -k python -f cloudant-tools/core_banking_tools.py -r cloudant-tools/requirements.txt
orchestrate tools import -k python -f cloudant-tools/fraud_detection_tools.py -r cloudant-tools/requirements.txt
orchestrate tools import -k python -f cloudant-tools/loan_processing_tools.py -r cloudant-tools/requirements.txt

# Verify tools are listed
orchestrate tools list
```

### Agent Not Responding

If an agent is not responding:

```bash
# Check agent status
orchestrate agents list

# Re-import the agent
orchestrate agents import -f agents/banking-orchestrator-agent.yaml
```

### Authentication Failures

If authentication always fails:

```bash
# Verify customer data in Cloudant
# Check that customers database has PIN field
# Re-run bootstrap if needed
python cloudant-tools/scripts/bootstrap_and_seed.py
```

## 📝 Next Steps

1. **Test All Demo Scenarios** - Try each of the 4 main scenarios
2. **Test Guardrails** - Verify all 4 guardrails are working
3. **Test Workflow** - Try the loan approval workflow
4. **Create Custom Scenarios** - Modify Cloudant data for new scenarios
5. **Monitor Performance** - Check response times and token usage

## 🎯 Demo Presentation Tips

1. **Start with Authentication** - Show secure PIN-based authentication
2. **Show Simple Query** - Begin with account balance inquiry
3. **Demonstrate Guardrails** - Show PII redaction and transaction limits
4. **Highlight Fraud Detection** - Real-time fraud blocking
5. **End with Workflow** - Complete loan application with deterministic workflow
6. **Emphasize ROI** - Reference the £32M+ savings and 1,200%+ ROI

## 📚 Additional Resources

- [Architecture Diagram](ARCHITECTURE_DIAGRAM.md) - Complete system architecture
- [Authentication Guide](AUTHENTICATION_GUIDE.md) - Authentication implementation
- [Authentication Architecture](AUTHENTICATION_ARCHITECTURE.md) - Technical auth details
- [Guardrail Demo Guide](GUARDRAIL_DEMO_GUIDE.md) - Guardrail demonstrations
- [Loan Approval Workflow](LOAN_APPROVAL_WORKFLOW.md) - Workflow implementation
- [Demo Accounts](DEMO_ACCOUNTS.md) - Customer credentials and scenarios

## 🆘 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the architecture documentation
3. Verify Cloudant connection and data
4. Check watsonx Orchestrate logs for errors
5. Verify all prerequisites are met

---

**Status**: Implementation Complete ✅  
**Last Updated**: 2026-05-05  
**Version**: 2.0 (Cloudant Implementation)