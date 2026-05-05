# Banking Demo - Troubleshooting Guide

## Common Issues and Solutions

### 1. Cloudant Connection Issues

**Error Message:**
```
Failed to connect to Cloudant database
Connection refused or authentication failed
```

**Cause:**
- Cloudant credentials not configured
- Connection not imported
- Network connectivity issues

**Solutions:**

#### Solution A: Verify Cloudant Credentials
```bash
# Check if CLOUDANT_URL and CLOUDANT_APIKEY are set
echo $CLOUDANT_URL
echo $CLOUDANT_APIKEY

# If not set, add to .env file or export
export CLOUDANT_URL="your-cloudant-url"
export CLOUDANT_APIKEY="your-api-key"
```

#### Solution B: Import Cloudant Connection
```bash
# Import connection configuration
./import-cloudant-connection.sh

# Verify connection exists
orchestrate connections list | grep cloudant
```

#### Solution C: Test Cloudant Connection
```bash
# Run smoke tests
cd cloudant-tools
python tests_smoke.py
```

---

### 2. Cloudant Databases Empty or Missing

**Error Message:**
```
Database not found: banking_customers
No documents found in database
```

**Cause:**
- Databases not bootstrapped
- Bootstrap script not run
- Data seeding failed

**Solutions:**

#### Solution A: Run Bootstrap Script
```bash
cd cloudant-tools/scripts
python bootstrap_and_seed.py

# This will:
# - Create 8 Cloudant databases
# - Create indexes
# - Seed data from data/ JSON files
```

#### Solution B: Verify Databases Exist
```bash
# Check if databases were created
# Use Cloudant dashboard or API to verify:
# - banking_customers
# - banking_accounts
# - banking_transactions
# - banking_credit_reports
# - banking_devices
# - banking_fraud_cases
# - banking_loan_applications
# - banking_audit_logs
```

#### Solution C: Re-seed Data
```bash
cd cloudant-tools/scripts
# Delete and recreate databases
python bootstrap_and_seed.py --force
```

---

### 3. Python Tool Import Failures

**Error Message:**
```
Failed to import tool: authenticate_customer
ModuleNotFoundError: No module named 'repositories'
```

**Cause:**
- Missing Python dependencies
- Incorrect import paths
- Repository classes not found

**Solutions:**

#### Solution A: Install Dependencies
```bash
# Install all required packages
pip install -r requirements.txt
pip install -r cloudant-tools/requirements.txt
```

#### Solution B: Verify Repository Structure
```bash
# Check repository files exist
ls -la cloudant-tools/repositories/
# Should show: customers.py, accounts.py, transactions.py, etc.
```

#### Solution C: Import Tools Individually
```bash
# Import each tool module separately
orchestrate tools import -k python -f cloudant-tools/core_banking_tools.py -r cloudant-tools/requirements.txt
orchestrate tools import -k python -f cloudant-tools/fraud_detection_tools.py -r cloudant-tools/requirements.txt
orchestrate tools import -k python -f cloudant-tools/loan_processing_tools.py -r cloudant-tools/requirements.txt
```

---

### 4. 500 Server Error During Tool Import

**Error Message:**
```
requests.exceptions.HTTPError: 500 Server Error: Internal Server Error
ClientAPIException(status_code=500, message={"detail":"An Unexpected Error Occurred."})
```

**Cause:**
This is a server-side error that typically occurs when:
- Removing and immediately reimporting tools (server needs time to clean up)
- Server is temporarily overloaded
- Tool package has issues

**Solutions:**

#### Solution A: Wait and Retry (Recommended)
```bash
# Wait 10-15 seconds, then run the script again
sleep 15
./import-all.sh
```

#### Solution B: Import Tools Individually
```bash
# Import one at a time with delays
orchestrate tools import -k python -f cloudant-tools/core_banking_tools.py -r cloudant-tools/requirements.txt
sleep 10

orchestrate tools import -k python -f cloudant-tools/fraud_detection_tools.py -r cloudant-tools/requirements.txt
sleep 10

orchestrate tools import -k python -f cloudant-tools/loan_processing_tools.py -r cloudant-tools/requirements.txt
sleep 10
```

#### Solution C: Check Tool Status
```bash
# List imported tools
orchestrate tools list | grep -E "(authenticate|balance|fraud|loan)"

# Should show 25 tools from 3 modules
```

---

### 5. Plugin Validation Error

**Error Message:**
```
pydantic_core._pydantic_core.ValidationError: 1 validation error for Agent
plugins.agent_post_invoke.0
  Input should be a valid dictionary or instance of PluginRef
```

**Cause:**
Incorrect plugin reference format in agent YAML files.

**Solution:**
✅ This has been fixed in all agent YAML files. The correct format is:

```yaml
plugins:
  agent_post_invoke:
    - plugin_name: pii_protection_guardrail
  agent_pre_invoke:
    - plugin_name: transaction_limit_guardrail
```

If you see this error, verify your agent YAML files use `plugin_name:` field.

---

### 6. Authentication Token Expired

**Error Message:**
```
[ERROR] - The token found for environment 'wxo-edu' is missing or expired
```

**Solution:**
```bash
# Reactivate the environment
orchestrate env activate wxo-edu
# Enter credentials when prompted

# Then run import script
./import-all.sh
```

---

### 7. Tool Execution Failures

**Error Message:**
```
Tool execution failed: Database query error
Customer not found in database
```

**Cause:**
- Cloudant database not seeded
- Customer data missing
- Repository query issues

**Solution:**

#### Verify Data Exists
```bash
# Run smoke tests to verify data
cd cloudant-tools
python tests_smoke.py

# Should show:
# ✓ Customer CUST-001 found
# ✓ Accounts found
# ✓ Transactions found
```

#### Re-seed Databases
```bash
cd cloudant-tools/scripts
python bootstrap_and_seed.py
```

---

### 8. Guardrails Not Working

**Symptoms:**
- PII not being redacted
- Transaction limits not enforced
- Loans not being blocked

**Diagnosis:**
```bash
# Check if guardrails are imported
orchestrate tools list | grep guardrail

# Should show:
# - pii_protection_guardrail
# - transaction_limit_guardrail
# - lending_compliance_guardrail
# - fraud_rules_guardrail
```

**Solution:**
```bash
# Reimport guardrails
orchestrate tools import -k python -f plugins/pii_protection_guardrail.py
orchestrate tools import -k python -f plugins/transaction_limit_guardrail.py
orchestrate tools import -k python -f plugins/lending_compliance_guardrail.py
orchestrate tools import -k python -f plugins/fraud_rules_guardrail.py

# Verify agent YAML files have correct plugin references
# See agent YAML files for correct format
```

---

### 9. Agent Import Fails

**Error Message:**
```
Failed to import agent: <agent-name>
```

**Solution:**

#### Check YAML Syntax
```bash
# Validate YAML syntax
python3 -c "import yaml; yaml.safe_load(open('agents/customer-service-agent.yaml'))"
```

#### Check Dependencies
```bash
# Verify Python tools are imported (25 tools)
orchestrate tools list | wc -l

# Verify guardrails are imported (4 guardrails)
orchestrate tools list | grep guardrail

# Verify Cloudant connection exists
orchestrate connections list | grep cloudant
```

#### Import Manually
```bash
orchestrate agents import -f agents/customer-service-agent.yaml
```

---

### 10. Python Dependencies Missing

**Error Message:**
```
ModuleNotFoundError: No module named 'ibm_watsonx_orchestrate'
```

**Solution:**
```bash
# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
pip list | grep ibm-watsonx-orchestrate
```

---

## Best Practices to Avoid Issues

### 1. Always Use Delays When Removing/Reimporting
```bash
orchestrate toolkits remove -n my-toolkit
sleep 10  # Give server time to clean up
orchestrate toolkits import -f toolkits/my-toolkit.yaml
```

### 2. Import in Correct Order
1. Bootstrap Cloudant databases first
2. Import Cloudant connection second
3. Import Python tools third
4. Import guardrail plugins fourth
5. Import agents last

### 3. Verify Each Step
```bash
# After bootstrapping Cloudant
cd cloudant-tools
python tests_smoke.py

# After importing connection
orchestrate connections list | grep cloudant

# After importing tools (should show 25 tools)
orchestrate tools list | wc -l

# After importing guardrails (should show 4)
orchestrate tools list | grep guardrail

# After importing agents (should show 5)
orchestrate agents list
```

### 4. Use Error Handling in Scripts
```bash
if orchestrate toolkits import -f my-toolkit.yaml; then
    echo "✓ Success"
else
    echo "✗ Failed - check logs"
    exit 1
fi
```

---

## Getting Help

### Check Logs
```bash
# View recent orchestrate CLI logs
orchestrate --debug agents import -f agents/my-agent.yaml
```

### Verify Environment
```bash
# Check active environment
orchestrate env list

# Check current environment details
orchestrate env show
```

### Test Components Individually
```bash
# Test Cloudant connection
cd cloudant-tools
python tests_smoke.py

# Test guardrail logic
cd tests
python test_guardrail_logic.py

# Test workflow
python test_loan_approval_workflow.py
```

---

## Quick Recovery Steps

If everything is broken and you want to start fresh:

```bash
# 1. Bootstrap Cloudant databases
cd banking-demo/cloudant-tools/scripts
python bootstrap_and_seed.py
cd ../..

# 2. Remove all artifacts
orchestrate agents remove --name customer_service_agent
orchestrate agents remove --name loan_processing_agent
orchestrate agents remove --name fraud_detection_agent
orchestrate agents remove --name banking_orchestrator_agent
orchestrate agents remove --name compliance_risk_agent

# Remove tools (25 tools)
orchestrate tools list | grep -E "(authenticate|balance|fraud|loan)" | while read tool; do
    orchestrate tools remove -n "$tool"
done

# 3. Wait for cleanup
sleep 15

# 4. Reimport everything
./import-cloudant-connection.sh
./import-all.sh

# 5. Verify
orchestrate connections list | grep cloudant
orchestrate tools list | wc -l  # Should show ~29 (25 tools + 4 guardrails)
orchestrate agents list  # Should show 5 agents
```

---

## Contact Information

For issues not covered in this guide:
- Check watsonx Orchestrate documentation
- Review error logs with `--debug` flag
- Test Cloudant connection with smoke tests
- Verify bootstrap script completed successfully
- Check IBM Cloudant dashboard for database status
- Test components individually to isolate the problem

---

**Last Updated**: 2026-05-05
**Architecture**: Cloudant-backed standalone Python tools
**Key Components**: 8 Cloudant databases, 25 Python tools, 7 repositories, 4 guardrails, 5 agents