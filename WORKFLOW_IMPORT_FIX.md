# Workflow Import Issue - Quick Fix Guide

## Problem

When running `./import-all.sh`, you may see this error:

```
Invalid value: Failed to load model from file tools/loan_approval_workflow.py: 
tool 'loan-processing:check_credit_score' not found
```

## Root Cause

The workflow (`loan_approval_workflow.py`) references MCP toolkit tools like `loan-processing:check_credit_score`. These tools are only available AFTER the MCP servers have fully started and registered their tools with the platform.

The import script tries to import the workflow immediately after importing the toolkits, but the MCP servers need time to:
1. Start up
2. Initialize
3. Register their tools with the platform

## Solution

The updated `import-all.sh` script now includes:

1. **Automatic wait period** - Waits 10 seconds after toolkit import
2. **Tool availability check** - Verifies tools are registered before proceeding
3. **Retry logic** - Attempts to verify tools up to 6 times (30 seconds total)
4. **Graceful failure** - Continues with other imports if workflow fails

## Manual Fix (If Workflow Import Fails)

If the workflow import still fails during `./import-all.sh`, follow these steps:

### Step 1: Wait for MCP Servers
```bash
# Wait 30-60 seconds for MCP servers to fully start
sleep 30
```

### Step 2: Verify Tools Are Available
```bash
# Check if loan-processing tools are registered
orchestrate tools list | grep "loan-processing"
```

You should see tools like:
- `loan-processing:check_credit_score`
- `loan-processing:calculate_debt_to_income`
- `loan-processing:calculate_loan_eligibility`
- etc.

### Step 3: Import Workflow Manually
```bash
# Once tools are available, import the workflow
orchestrate tools import -k flow -f tools/loan_approval_workflow.py
```

### Step 4: Verify Workflow Import
```bash
# Check if workflow was imported successfully
orchestrate tools list | grep "loan_approval_workflow"
```

You should see:
```
loan_approval_workflow
```

## Prevention

To avoid this issue in future runs:

1. **Run import-all.sh twice** - First run imports toolkits, second run (after waiting) imports workflow
2. **Use the updated script** - The new version includes automatic waiting and retry logic
3. **Import workflow separately** - Import toolkits first, wait, then import workflow

## Alternative: Two-Step Import

### Step 1: Import Toolkits and Guardrails
```bash
#!/bin/bash
# Import toolkits
orchestrate toolkits import -f toolkits/core-banking-toolkit.yaml
orchestrate toolkits import -f toolkits/fraud-detection-toolkit.yaml
orchestrate toolkits import -f toolkits/loan-processing-toolkit.yaml

# Import guardrails
orchestrate tools import -k python -f plugins/pii_protection_guardrail.py
orchestrate tools import -k python -f plugins/transaction_limit_guardrail.py
orchestrate tools import -k python -f plugins/lending_compliance_guardrail.py
orchestrate tools import -k python -f plugins/fraud_rules_guardrail.py

echo "Waiting for MCP servers to start..."
sleep 30
```

### Step 2: Import Workflow and Agents
```bash
#!/bin/bash
# Import workflow (after MCP servers are ready)
orchestrate tools import -k flow -f tools/loan_approval_workflow.py

# Import agents
orchestrate agents import -f agents/compliance-risk-agent.yaml
orchestrate agents import -f agents/customer-service-agent.yaml
orchestrate agents import -f agents/fraud-detection-agent.yaml
orchestrate agents import -f agents/loan-processing-agent.yaml
orchestrate agents import -f agents/banking-orchestrator-agent.yaml
```

## Understanding MCP Server Startup

MCP (Model Context Protocol) servers are separate processes that:

1. **Start asynchronously** - They don't block the import script
2. **Register tools gradually** - Tools appear in the platform after server initialization
3. **Need initialization time** - Typically 10-30 seconds depending on server complexity

The workflow import fails if it tries to reference tools before they're registered.

## Verification Commands

### Check if MCP servers are running
```bash
# List all toolkits (should show core-banking, loan-processing, fraud-detection)
orchestrate toolkits list
```

### Check if tools are registered
```bash
# List all tools (should show toolkit:tool_name format)
orchestrate tools list
```

### Check if workflow is imported
```bash
# List tools and filter for workflow
orchestrate tools list | grep workflow
```

### Check if agents are imported
```bash
# List all agents
orchestrate agents list
```

## Success Indicators

When everything is working correctly, you should see:

✅ **Toolkits imported** - 3 toolkits (core-banking, fraud-detection, loan-processing)
✅ **Tools registered** - ~25 tools with toolkit prefixes (e.g., `loan-processing:check_credit_score`)
✅ **Guardrails imported** - 4 guardrail plugins
✅ **Workflow imported** - `loan_approval_workflow` appears in tools list
✅ **Agents imported** - 5 agents (orchestrator + 4 specialists)

## Still Having Issues?

If the workflow import continues to fail:

1. **Check MCP server logs** - Look for errors in server startup
2. **Verify toolkit YAML files** - Ensure `command` and `package_root` are correct
3. **Test MCP servers manually** - Run the server command directly to check for errors
4. **Restart the platform** - Sometimes a fresh start helps
5. **Import without workflow** - Skip workflow import and use individual tools instead

## Contact Support

If none of these solutions work, provide:
- Full error message from `./import-all.sh`
- Output of `orchestrate toolkits list`
- Output of `orchestrate tools list`
- MCP server logs (if available)