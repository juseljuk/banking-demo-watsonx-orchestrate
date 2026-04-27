# Banking Demo - Troubleshooting Guide

## Common Issues and Solutions

### 1. 500 Server Error During Toolkit Import

**Error Message:**
```
requests.exceptions.HTTPError: 500 Server Error: Internal Server Error
ClientAPIException(status_code=500, message={"detail":"An Unexpected Error Occurred."})
```

**Cause:**
This is a server-side error that typically occurs when:
- Removing and immediately reimporting a toolkit (server needs time to clean up)
- Server is temporarily overloaded
- Toolkit package has issues

**Solutions:**

#### Solution A: Wait and Retry (Recommended)
```bash
# Wait 10-15 seconds, then run the script again
sleep 15
./import-all.sh
```

#### Solution B: Import Toolkits Individually
```bash
# Import one at a time with delays
orchestrate toolkits import -f toolkits/core-banking-toolkit.yaml
sleep 10

orchestrate toolkits import -f toolkits/fraud-detection-toolkit.yaml
sleep 10

orchestrate toolkits import -f toolkits/loan-processing-toolkit.yaml
sleep 10
```

#### Solution C: Skip Removal Step
If toolkits don't exist yet, import without removing:
```bash
# Comment out the removal logic in import-all.sh
# Or manually import without checking for existing toolkits
orchestrate toolkits import -f toolkits/loan-processing-toolkit.yaml
```

#### Solution D: Manual Cleanup
```bash
# List existing toolkits
orchestrate toolkits list

# Remove problematic toolkit
orchestrate toolkits remove -n loan-processing

# Wait for cleanup
sleep 15

# Import fresh
orchestrate toolkits import -f toolkits/loan-processing-toolkit.yaml
```

---

### 2. Plugin Validation Error

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

### 3. Authentication Token Expired

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

### 4. MCP Server Not Responding

**Error Message:**
```
Tool execution failed: Connection refused
```

**Cause:**
MCP server process hasn't started or crashed.

**Solution:**

#### Check Toolkit Status
```bash
orchestrate toolkits list
```

#### Reimport Toolkit
```bash
orchestrate toolkits remove -n core-banking
sleep 10
orchestrate toolkits import -f toolkits/core-banking-toolkit.yaml
```

#### Test MCP Server Locally
```bash
cd banking-demo/toolkits
python3 core_banking_server.py
# Should start without errors
```

---

### 5. Guardrails Not Working

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

### 6. Agent Import Fails

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
# Verify toolkits are imported first
orchestrate toolkits list

# Verify guardrails are imported
orchestrate tools list | grep guardrail
```

#### Import Manually
```bash
orchestrate agents import -f agents/customer-service-agent.yaml
```

---

### 7. Data Files Not Found

**Error Message:**
```
FileNotFoundError: data/customers.json
```

**Solution:**
```bash
# Ensure data files are in correct location
ls -la banking-demo/data/
ls -la banking-demo/toolkits/data/

# Copy data files if missing
cd banking-demo
cp -r data toolkits/data
```

---

### 8. Python Dependencies Missing

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
1. MCP Toolkits first
2. Guardrail plugins second
3. Agents last

### 3. Verify Each Step
```bash
# After importing toolkits
orchestrate toolkits list

# After importing guardrails
orchestrate tools list | grep guardrail

# After importing agents
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
# Test MCP server locally
python3 toolkits/core_banking_server.py

# Test guardrail logic
python3 tests/test_guardrail_logic.py

# Test authentication
python3 toolkits/test_mcp_servers.py
```

---

## Quick Recovery Steps

If everything is broken and you want to start fresh:

```bash
# 1. Remove all artifacts
orchestrate toolkits remove -n core-banking
orchestrate toolkits remove -n fraud-detection
orchestrate toolkits remove -n loan-processing

orchestrate agents remove --name customer_service_agent
orchestrate agents remove --name loan_processing_agent
orchestrate agents remove --name fraud_detection_agent
orchestrate agents remove --name banking_orchestrator_agent
orchestrate agents remove --name compliance_risk_agent

# 2. Wait for cleanup
sleep 15

# 3. Reimport everything
cd banking-demo
./import-all.sh
```

---

## Contact Information

For issues not covered in this guide:
- Check watsonx Orchestrate documentation
- Review error logs with `--debug` flag
- Test components individually to isolate the problem