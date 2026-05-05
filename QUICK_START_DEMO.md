# Banking Demo - Quick Start Guide

## 🚀 5-Minute Setup

### 1. Bootstrap Cloudant Databases (First Time Only)
```bash
cd banking-demo
source ../.venv/bin/activate
orchestrate env activate wxo-edu

# Bootstrap Cloudant: Create databases, indexes, and seed data
cd cloudant-tools
python3 scripts/bootstrap_and_seed.py
cd ..

# Verify Cloudant setup
orchestrate connections list | grep cloudant
```

### 2. Deploy Everything
```bash
# Import Cloudant connection
./import-cloudant-connection.sh

# Deploy all components (Python tools, agents WITH guardrails, plugins)
./import-all.sh

# Deploy "no guardrails" versions for before/after demo
./import-no-guardrails.sh
```

### 3. Verify Deployment
```bash
# Check Cloudant connection
orchestrate connections list | grep cloudant

# Check Python tools (25 tools from 3 modules)
orchestrate tools list | grep -E "authenticate_customer|check_account_balance|analyze_transaction_risk|check_credit_score"

# Check agents
orchestrate agents list | grep -E "(customer_service|loan_processing)"

# Should show:
# - customer_service_agent (WITH guardrails)
# - customer_service_agent_no_guardrails (WITHOUT guardrails)
# - loan_processing_agent (WITH guardrails)
# - loan_processing_agent_no_guardrails (WITHOUT guardrails)

# Check guardrails
orchestrate tools list | grep guardrail

# Should show:
# - pii_protection_guardrail
# - transaction_limit_guardrail
# - lending_compliance_guardrail
# - fraud_rules_guardrail
```

---

## 🎭 Two Demo Approaches

### Option A: Standard Demo (WITH Guardrails)
**Best for:** Showing production-ready capabilities

**Use agents:**
- `customer_service_agent`
- `loan_processing_agent`
- `fraud_detection_agent`

**Demo scenarios:** See `GUARDRAIL_DEMO_GUIDE.md`

---

### Option B: Before & After Demo (Show Value)
**Best for:** Demonstrating why guardrails matter

**Phase 1 - "Before" (Show Problems):**
Use agents WITHOUT guardrails:
- `customer_service_agent_no_guardrails`
- `loan_processing_agent_no_guardrails`

**Phase 2 - "After" (Show Solutions):**
Switch to agents WITH guardrails:
- `customer_service_agent`
- `loan_processing_agent`

**Demo script:** See `GUARDRAIL_BEFORE_AFTER_DEMO.md`

---

## 🔐 Authentication

**All demos start with authentication:**
```
User: "CUST-001 and 1234"
```

**Demo customers:**
- Emma Thompson: `CUST-001` / PIN `1234` (Primary demo customer)
- James Patel: `CUST-002` / PIN `5678` (Business customer)
- Sophie Williams: `CUST-003` / PIN `9012` (Young professional)

---

## 🎯 Quick Demo Scenarios

### 1. PII Protection (2 minutes)

**WITHOUT Guardrails:**
```
Agent: customer_service_agent_no_guardrails
User: "What's my account number?"
Result: Full account number exposed (12345678) ❌
```

**WITH Guardrails:**
```
Agent: customer_service_agent
User: "What's my account number?"
Result: Masked account number (****1234) ✅
```

---

### 2. Transaction Limits (2 minutes)

**WITHOUT Guardrails:**
```
Agent: customer_service_agent_no_guardrails
User: "Transfer £12,000 to my savings"
Result: Transfer processed (exceeds £10k limit) ❌
```

**WITH Guardrails:**
```
Agent: customer_service_agent
User: "Transfer £12,000 to my savings"
Result: Transfer blocked (exceeds £10k limit) ✅
```

---

### 3. Lending Compliance (2 minutes)

**WITHOUT Guardrails:**
```
Agent: loan_processing_agent_no_guardrails
User: "I want a £350,000 personal loan"
Result: Loan approved (exceeds 5x income) ❌
```

**WITH Guardrails:**
```
Agent: loan_processing_agent
User: "I want a £350,000 personal loan"
Result: Loan blocked (exceeds 5x income limit) ✅
```

---

### 4. Fraud Detection (2 minutes)

**WITHOUT Guardrails:**
```
Agent: customer_service_agent_no_guardrails
User: "URGENT! Send £12,000 to Nigeria for crypto!"
Result: Transfer processed (95/100 risk score) ❌
```

**WITH Guardrails:**
```
Agent: customer_service_agent
User: "URGENT! Send £12,000 to Nigeria for crypto!"
Result: Transfer blocked (95/100 risk score) ✅
```

---

## 📊 Key Talking Points

### Business Value
- **Security:** Automatic PII protection prevents data breaches
- **Compliance:** Enforces UK lending regulations (FCA CONC 5.2A)
- **Risk Management:** Blocks high-risk fraud transactions automatically
- **Trust:** Ensures AI agents operate safely and responsibly

### Technical Capabilities
- **Pre-invoke Guardrails:** Block requests before processing
- **Post-invoke Guardrails:** Redact sensitive data in responses
- **Risk Scoring:** 0-100 scale with automatic blocking at 91+
- **Regulatory Compliance:** FCA, Consumer Credit Act, Payment Services Regulations

### ROI Impact
- **Reduced fraud losses:** 95%+ detection accuracy
- **Regulatory compliance:** Automated checks prevent fines
- **Customer trust:** Enhanced data protection
- **Operational efficiency:** Automated policy enforcement

---

## 📖 Full Documentation

- **GUARDRAIL_BEFORE_AFTER_DEMO.md** - Complete before/after demo script
- **GUARDRAIL_DEMO_GUIDE.md** - Detailed guardrail scenarios
- **GUARDRAILS_IMPLEMENTATION.md** - Technical implementation details
- **DEMO_ACCOUNTS.md** - Customer accounts and test data
- **AUTHENTICATION_GUIDE.md** - Authentication system details

---

## 🔧 Troubleshooting

### Cloudant connection issues
```bash
# Verify Cloudant connection exists
orchestrate connections list | grep cloudant

# Re-import connection if needed
./import-cloudant-connection.sh

# Test Cloudant connectivity
cd cloudant-tools
python3 tests_smoke.py
cd ..
```

### Cloudant databases empty
```bash
# Re-run bootstrap to seed databases
cd cloudant-tools
python3 scripts/bootstrap_and_seed.py
cd ..
```

### Agents not found
```bash
# Re-import agents
cd banking-demo
./import-all.sh
./import-no-guardrails.sh
```

### Guardrails not working
```bash
# Verify guardrails are imported
orchestrate tools list | grep guardrail

# Re-import if needed
orchestrate tools import -k python -f plugins/pii_protection_guardrail.py
orchestrate tools import -k python -f plugins/transaction_limit_guardrail.py
orchestrate tools import -k python -f plugins/lending_compliance_guardrail.py
orchestrate tools import -k python -f plugins/fraud_rules_guardrail.py
```

### Python tools not available
```bash
# Check imported tools (should show 25 tools)
orchestrate tools list | grep -E "authenticate_customer|check_account_balance|analyze_transaction_risk|check_credit_score"

# Re-import the Python tool modules if needed
orchestrate tools import -k python -f cloudant-tools/core_banking_tools.py -r cloudant-tools/requirements.txt
orchestrate tools import -k python -f cloudant-tools/fraud_detection_tools.py -r cloudant-tools/requirements.txt
orchestrate tools import -k python -f cloudant-tools/loan_processing_tools.py -r cloudant-tools/requirements.txt
```

---

## ⚠️ Important Notes

1. **Bootstrap Cloudant first** - Run `python3 cloudant-tools/scripts/bootstrap_and_seed.py` before first use
2. **Never use "no-guardrails" agents in production** - They are for demonstration only
3. **Always authenticate first** - Use `CUST-001 and 1234` to start
4. **Test locally first** - Run `python3 tests/test_guardrail_logic.py` to verify
5. **Monitor guardrail effectiveness** - Check logs for blocked transactions
6. **Cloudant credentials** - Ensure Cloudant connection is configured with valid credentials

---

## 🎬 Demo Checklist

- [ ] Bootstrap Cloudant databases (`python3 cloudant-tools/scripts/bootstrap_and_seed.py`)
- [ ] Import Cloudant connection (`./import-cloudant-connection.sh`)
- [ ] Deploy all components (`./import-all.sh`)
- [ ] Deploy no-guardrails versions (`./import-no-guardrails.sh`)
- [ ] Verify Cloudant connection is active
- [ ] Verify Python tools are imported (25 tools)
- [ ] Verify agents are accessible
- [ ] Test authentication (CUST-001 / 1234)
- [ ] Prepare demo scenarios
- [ ] Review talking points
- [ ] Test "before" scenarios (show problems)
- [ ] Test "after" scenarios (show solutions)
- [ ] Emphasize business value

---

**Ready to demo!** 🚀

Choose your approach:
- **Standard Demo:** Use agents with guardrails, show capabilities
- **Before & After Demo:** Show problems first, then solutions

Both approaches demonstrate the power and value of watsonx Orchestrate for banking.