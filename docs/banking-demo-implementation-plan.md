# Banking Demo - Implementation Plan for Dummy Data

## Overview

This document outlines the implementation strategy for integrating the dummy data into the banking demonstration. We'll compare two approaches and provide a recommended solution.

---

## Approach Comparison

### Option 1: Direct Python Tool Implementation (Simple)

**How it works:**
- Dummy data stored in JSON files in `data/` directory
- Python tools load data directly from JSON files
- Tools use simple dictionary lookups to return data

**Pros:**
- ✅ Simple and straightforward
- ✅ Fast to implement
- ✅ No additional dependencies
- ✅ Easy to debug
- ✅ Good for quick demos

**Cons:**
- ❌ Data tightly coupled to tool code
- ❌ Harder to update data without modifying code
- ❌ Less realistic (doesn't simulate real API calls)
- ❌ No separation of concerns
- ❌ Difficult to reuse data across different projects

**Best for:** Quick prototypes, simple demos, time-constrained projects

---

### Option 2: MCP Server Implementation (Recommended) ⭐

**How it works:**
- Create dedicated MCP server(s) that serve banking data
- MCP server exposes tools that agents can call
- Data stored in JSON files, loaded by MCP server
- Agents interact with MCP server as if it were a real banking API

**Pros:**
- ✅ **Realistic architecture** - Mimics real-world API integration
- ✅ **Separation of concerns** - Data layer separate from agent logic
- ✅ **Reusable** - Same MCP server can be used across multiple demos
- ✅ **Maintainable** - Update data without touching agent code
- ✅ **Scalable** - Easy to add new data sources or APIs
- ✅ **Professional** - Shows best practices for production systems
- ✅ **Flexible** - Can simulate API delays, errors, rate limiting
- ✅ **Testable** - Can test MCP server independently

**Cons:**
- ⚠️ Slightly more complex initial setup
- ⚠️ Requires understanding of MCP protocol
- ⚠️ Additional component to manage

**Best for:** Professional demos, production-like environments, showcasing architecture

---

## Recommended Approach: MCP Server Architecture

For a C-suite banking demo, we **strongly recommend the MCP server approach** because:

1. **Demonstrates Production Architecture** - Shows how watsonx Orchestrate integrates with real banking systems
2. **Professional Presentation** - More impressive to technical stakeholders
3. **Flexibility** - Easy to swap mock data for real APIs later
4. **Best Practices** - Follows microservices and API-first design patterns
5. **Reusability** - Can be used for multiple demos and POCs

---

## Recommended MCP Server Architecture

### Three MCP Servers for Banking Demo

```
┌─────────────────────────────────────────────────────────────┐
│                  Banking Orchestrator Agent                  │
└────────────┬────────────────────────────────────────────────┘
             │
             ├──────────────┬──────────────┬──────────────┐
             │              │              │              │
             ▼              ▼              ▼              ▼
    ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐
    │  Customer  │  │   Fraud    │  │    Loan    │  │ Compliance │
    │  Service   │  │ Detection  │  │ Processing │  │    Agent   │
    │   Agent    │  │   Agent    │  │   Agent    │  │            │
    └─────┬──────┘  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘
          │               │               │               │
          └───────────────┴───────────────┴───────────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    │                           │
                    ▼                           ▼
          ┌──────────────────┐        ┌──────────────────┐
          │  MCP Servers     │        │   Guardrails     │
          │                  │        │                  │
          │ 1. Core Banking  │        │ • PII protection │
          │ 2. Fraud System  │        │ • Compliance     │
          │ 3. Loan System   │        │ • Access control │
          └──────────────────┘        └──────────────────┘
```

### MCP Server 1: Core Banking MCP Server

**Purpose:** Simulates core banking system APIs

**Tools Provided:**
- `check_account_balance(account_id: str) -> Dict`
- `get_recent_transactions(account_id: str, limit: int) -> List[Dict]`
- `transfer_funds(from_account: str, to_account: str, amount: float) -> Dict`
- `check_pending_deposits(account_id: str) -> List[Dict]`
- `get_payment_due_date(account_id: str, account_type: str) -> Dict`
- `update_contact_info(account_id: str, contact_type: str, value: str) -> Dict`

**Data Files:**
- `data/customers.json`
- `data/accounts.json`
- `data/transactions.json`

**File:** `toolkits/core_banking_server.py`

---

### MCP Server 2: Fraud Detection MCP Server

**Purpose:** Simulates fraud detection and monitoring system

**Tools Provided:**
- `analyze_transaction_risk(transaction_data: Dict) -> Dict`
- `check_customer_profile(customer_id: str) -> Dict`
- `verify_device_fingerprint(device_id: str, customer_id: str) -> Dict`
- `check_velocity_rules(customer_id: str, timeframe: str) -> Dict`
- `block_transaction(transaction_id: str, reason: str) -> Dict`
- `send_fraud_alert(customer_id: str, channel: str, message: str) -> Dict`
- `create_fraud_case(transaction_id: str, risk_score: int) -> Dict`

**Data Files:**
- `data/fraud_scenarios.json`
- `data/devices.json`
- `data/fraud_rules.json`

**File:** `toolkits/fraud_detection_server.py`

---

### MCP Server 3: Loan Processing MCP Server

**Purpose:** Simulates loan origination and processing system

**Tools Provided:**
- `calculate_loan_eligibility(customer_id: str, loan_amount: float, loan_purpose: str) -> Dict`
- `check_credit_score(customer_id: str) -> Dict`
- `calculate_debt_to_income(customer_id: str) -> Dict`
- `generate_loan_offers(eligibility_data: Dict) -> List[Dict]`
- `initiate_loan_approval(loan_application: Dict) -> Dict`
- `generate_loan_documents(loan_id: str) -> Dict`
- `send_for_esignature(document_id: str, customer_id: str) -> Dict`
- `disburse_funds(loan_id: str, account_id: str) -> Dict`

**Data Files:**
- `data/loan_applications.json`
- `data/credit_reports.json`
- `data/loan_products.json`

**File:** `toolkits/loan_processing_server.py`

---

## Implementation Plan

### Phase 1: Data Preparation (Week 1)

**Step 1: Create Data Directory Structure**
```bash
mkdir -p data
touch data/customers.json
touch data/accounts.json
touch data/transactions.json
touch data/fraud_scenarios.json
touch data/devices.json
touch data/loan_applications.json
touch data/credit_reports.json
```

**Step 2: Convert Markdown Data to JSON**
- Extract all data from [`banking-demo-data.md`](banking-demo-data.md)
- Create properly formatted JSON files
- Validate JSON structure

**Step 3: Create Data Loading Utilities**
```python
# data/data_loader.py
import json
from pathlib import Path
from typing import Dict, List, Any

class DataLoader:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self._cache = {}
    
    def load_customers(self) -> Dict[str, Any]:
        if 'customers' not in self._cache:
            with open(self.data_dir / 'customers.json') as f:
                self._cache['customers'] = json.load(f)
        return self._cache['customers']
    
    def load_accounts(self) -> Dict[str, Any]:
        if 'accounts' not in self._cache:
            with open(self.data_dir / 'accounts.json') as f:
                self._cache['accounts'] = json.load(f)
        return self._cache['accounts']
    
    # ... similar methods for other data files
```

---

### Phase 2: MCP Server Development (Week 2-3)

**Step 1: Core Banking MCP Server**

```python
# toolkits/core_banking_server.py
"""
Core Banking MCP Server
Simulates core banking system APIs for demo purposes
"""

import asyncio
from typing import Dict, List, Any
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
import sys
sys.path.append('..')
from data.data_loader import DataLoader

# Initialize data loader
data_loader = DataLoader()

# Create MCP server
app = Server("core-banking")

@app.list_tools()
async def list_tools() -> List[Tool]:
    """List available banking tools."""
    return [
        Tool(
            name="check_account_balance",
            description="Check the current balance of a customer account",
            inputSchema={
                "type": "object",
                "properties": {
                    "account_id": {
                        "type": "string",
                        "description": "The account identifier (e.g., CUR-001-1234)"
                    }
                },
                "required": ["account_id"]
            }
        ),
        Tool(
            name="get_recent_transactions",
            description="Retrieve recent transactions for an account",
            inputSchema={
                "type": "object",
                "properties": {
                    "account_id": {
                        "type": "string",
                        "description": "The account identifier"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of transactions to retrieve (default: 10, max: 50)",
                        "default": 10
                    }
                },
                "required": ["account_id"]
            }
        ),
        Tool(
            name="transfer_funds",
            description="Transfer funds between customer accounts",
            inputSchema={
                "type": "object",
                "properties": {
                    "from_account": {
                        "type": "string",
                        "description": "Source account identifier"
                    },
                    "to_account": {
                        "type": "string",
                        "description": "Destination account identifier"
                    },
                    "amount": {
                        "type": "number",
                        "description": "Transfer amount (must be positive)"
                    },
                    "memo": {
                        "type": "string",
                        "description": "Optional transfer memo",
                        "default": ""
                    }
                },
                "required": ["from_account", "to_account", "amount"]
            }
        )
        # ... more tools
    ]

@app.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls."""
    
    if name == "check_account_balance":
        account_id = arguments["account_id"]
        accounts = data_loader.load_accounts()
        
        account = accounts.get(account_id)
        if not account:
            return [TextContent(
                type="text",
                text=json.dumps({
                    "status": "error",
                    "message": f"Account {account_id} not found"
                })
            )]
        
        # Simulate API delay
        await asyncio.sleep(0.1)
        
        return [TextContent(
            type="text",
            text=json.dumps({
                "status": "success",
                "account_id": account["account_id"],
                "account_type": account["account_type"],
                "account_number_masked": account["account_number_masked"],
                "current_balance": account["current_balance"],
                "available_balance": account["available_balance"],
                "currency": account["currency"]
            })
        )]
    
    elif name == "get_recent_transactions":
        account_id = arguments["account_id"]
        limit = arguments.get("limit", 10)
        
        transactions = data_loader.load_transactions()
        account_txns = [t for t in transactions if t["account_id"] == account_id]
        
        # Sort by date descending and limit
        account_txns.sort(key=lambda x: x["date"], reverse=True)
        account_txns = account_txns[:limit]
        
        await asyncio.sleep(0.1)
        
        return [TextContent(
            type="text",
            text=json.dumps({
                "status": "success",
                "account_id": account_id,
                "transactions": account_txns,
                "count": len(account_txns)
            })
        )]
    
    elif name == "transfer_funds":
        from_account = arguments["from_account"]
        to_account = arguments["to_account"]
        amount = arguments["amount"]
        memo = arguments.get("memo", "")
        
        accounts = data_loader.load_accounts()
        
        # Validate accounts exist
        if from_account not in accounts:
            return [TextContent(
                type="text",
                text=json.dumps({
                    "status": "error",
                    "message": f"Source account {from_account} not found"
                })
            )]
        
        if to_account not in accounts:
            return [TextContent(
                type="text",
                text=json.dumps({
                    "status": "error",
                    "message": f"Destination account {to_account} not found"
                })
            )]
        
        # Check sufficient balance
        if accounts[from_account]["current_balance"] < amount:
            return [TextContent(
                type="text",
                text=json.dumps({
                    "status": "error",
                    "message": "Insufficient funds"
                })
            )]
        
        # Simulate transfer (in real system, this would update database)
        await asyncio.sleep(0.2)
        
        new_from_balance = accounts[from_account]["current_balance"] - amount
        new_to_balance = accounts[to_account]["current_balance"] + amount
        
        return [TextContent(
            type="text",
            text=json.dumps({
                "status": "success",
                "transaction_id": f"TXN-{int(time.time())}",
                "from_account": from_account,
                "to_account": to_account,
                "amount": amount,
                "memo": memo,
                "timestamp": datetime.now().isoformat(),
                "new_from_balance": new_from_balance,
                "new_to_balance": new_to_balance
            })
        )]
    
    # ... handle other tools
    
    return [TextContent(
        type="text",
        text=json.dumps({
            "status": "error",
            "message": f"Unknown tool: {name}"
        })
    )]

async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
```

**Step 2: Create MCP Toolkit YAML Files**

```yaml
# toolkits/core-banking-toolkit.yaml
spec_version: v1
kind: mcp
name: core-banking
description: Core banking system providing account management, transactions, and transfers
command: python3 core_banking_server.py
env: []
tools:
  - "*"
package_root: .
```

```yaml
# toolkits/fraud-detection-toolkit.yaml
spec_version: v1
kind: mcp
name: fraud-detection
description: Fraud detection and monitoring system for transaction risk analysis
command: python3 fraud_detection_server.py
env: []
tools:
  - "*"
package_root: .
```

```yaml
# toolkits/loan-processing-toolkit.yaml
spec_version: v1
kind: mcp
name: loan-processing
description: Loan origination and processing system for eligibility and approvals
command: python3 loan_processing_server.py
env: []
tools:
  - "*"
package_root: .
```

**Step 3: Import MCP Toolkits**

```bash
# Import all MCP toolkits
orchestrate toolkits import -f toolkits/core-banking-toolkit.yaml
orchestrate toolkits import -f toolkits/fraud-detection-toolkit.yaml
orchestrate toolkits import -f toolkits/loan-processing-toolkit.yaml

# Verify import
orchestrate toolkits list
orchestrate tools list
```

---

### Phase 3: Agent Configuration (Week 3)

**Update Agent YAML Files to Use MCP Tools**

```yaml
# agents/customer-service-agent.yaml
spec_version: v1
kind: native
name: customer_service_agent
description: Handles customer service inquiries and account operations

llm: groq/openai/gpt-oss-120b
style: default

instructions: |
  You are a helpful customer service agent for a UK bank.
  Use the available tools to help customers with their banking needs.

tools:
  - core-banking:check_account_balance
  - core-banking:get_recent_transactions
  - core-banking:transfer_funds
  - core-banking:check_pending_deposits
  - core-banking:get_payment_due_date

restrictions: editable
```

```yaml
# agents/fraud-detection-agent.yaml
spec_version: v1
kind: native
name: fraud_detection_agent
description: Real-time fraud detection and transaction monitoring

llm: groq/openai/gpt-oss-120b
style: react  # Use react style for real-time reasoning

instructions: |
  You are a fraud detection specialist.
  Analyze transactions for suspicious patterns and take appropriate action.

tools:
  - fraud-detection:analyze_transaction_risk
  - fraud-detection:check_velocity_rules
  - fraud-detection:block_transaction
  - fraud-detection:send_fraud_alert
  - fraud-detection:create_fraud_case

restrictions: editable
```

```yaml
# agents/loan-processing-agent.yaml
spec_version: v1
kind: native
name: loan_processing_agent
description: Automated loan application processing and approval

llm: groq/openai/gpt-oss-120b
style: planner  # Use planner style for multi-step workflows

instructions: |
  You are a loan processing specialist.
  Help customers with loan applications and provide personalized offers.

tools:
  - loan-processing:calculate_loan_eligibility
  - loan-processing:check_credit_score
  - loan-processing:generate_loan_offers
  - loan-processing:initiate_loan_approval

collaborators:
  - compliance_risk_agent

restrictions: editable
```

---

### Phase 4: Testing & Validation (Week 4)

**Step 1: Test MCP Servers Independently**

```bash
# Test core banking server
python3 toolkits/core_banking_server.py

# In another terminal, test with MCP client
# (Use MCP inspector or custom test script)
```

**Step 2: Test Agent Integration**

```bash
# Import agents
orchestrate agents import -f agents/customer-service-agent.yaml
orchestrate agents import -f agents/fraud-detection-agent.yaml
orchestrate agents import -f agents/loan-processing-agent.yaml

# Test in watsonx Orchestrate UI
# Try demo scenarios from banking-demo-data.md
```

**Step 3: End-to-End Demo Testing**

Test all four demo scenarios:
1. Simple account inquiry
2. Multi-step request
3. Fraud detection
4. Loan application

---

## Project Structure (Final)

```
banking-demo/
├── data/                           # Dummy data (JSON files)
│   ├── customers.json
│   ├── accounts.json
│   ├── transactions.json
│   ├── fraud_scenarios.json
│   ├── devices.json
│   ├── loan_applications.json
│   ├── credit_reports.json
│   └── data_loader.py             # Data loading utilities
│
├── toolkits/                       # MCP servers
│   ├── core_banking_server.py
│   ├── fraud_detection_server.py
│   ├── loan_processing_server.py
│   ├── core-banking-toolkit.yaml
│   ├── fraud-detection-toolkit.yaml
│   └── loan-processing-toolkit.yaml
│
├── agents/                         # Agent configurations
│   ├── banking-orchestrator-agent.yaml
│   ├── customer-service-agent.yaml
│   ├── fraud-detection-agent.yaml
│   ├── loan-processing-agent.yaml
│   └── compliance-risk-agent.yaml
│
├── plugins/                        # Guardrails
│   ├── customer_authentication_guardrail.py
│   ├── pii_protection_guardrail.py
│   ├── transaction_limit_guardrail.py
│   ├── lending_compliance_guardrail.py
│   └── fraud_rules_guardrail.py
│
├── docs/                           # Documentation
│   ├── banking-demo-plan.md
│   ├── banking-demo-data.md
│   └── banking-demo-implementation-plan.md (this file)
│
├── tests/                          # Test cases
│   ├── test_core_banking_server.py
│   ├── test_fraud_detection_server.py
│   └── test_loan_processing_server.py
│
├── import-all.sh                   # Deployment script
├── requirements.txt
└── README.md
```

---

## Advantages of MCP Server Approach

### 1. **Realistic Demo Architecture**
Shows how watsonx Orchestrate integrates with real banking systems through APIs.

### 2. **Easy to Swap Mock for Real**
When ready for production, simply point to real banking APIs instead of MCP servers.

### 3. **Reusable Across Demos**
Same MCP servers can be used for multiple demos, POCs, and training.

### 4. **Professional Presentation**
Demonstrates best practices and production-ready architecture to C-suite.

### 5. **Flexible Testing**
Can test MCP servers independently, making debugging easier.

### 6. **Simulates Real-World Scenarios**
Can add API delays, rate limiting, error responses to make demo more realistic.

### 7. **Clean Separation**
Agents focus on orchestration logic, MCP servers handle data access.

---

## Alternative: Hybrid Approach

For maximum flexibility, you could use a **hybrid approach**:

1. **MCP Servers** for core banking operations (accounts, transactions)
2. **Direct Python Tools** for simple utilities (validation, formatting)
3. **External APIs** for services like credit bureaus (if available)

This gives you the best of both worlds:
- Professional architecture for main banking operations
- Simple tools for utilities
- Real integrations where possible

---

## Recommendation Summary

**For your UK banking demo to C-suite executives:**

✅ **Use MCP Server Architecture**
- Create 3 MCP servers (Core Banking, Fraud Detection, Loan Processing)
- Store dummy data in JSON files
- Configure agents to use MCP tools
- Professional, scalable, production-like architecture

**Timeline:**
- Week 1: Data preparation
- Week 2-3: MCP server development
- Week 3: Agent configuration
- Week 4: Testing and refinement

**Effort:**
- Initial setup: ~2-3 weeks
- Maintenance: Minimal (just update JSON files)
- Reusability: High (use for multiple demos)

**Impact:**
- Demonstrates best practices
- Shows production-ready architecture
- Impresses technical stakeholders
- Easy to evolve into real system

---

## Next Steps

1. **Review and approve this implementation plan**
2. **Create JSON data files from markdown specification**
3. **Develop first MCP server (Core Banking)**
4. **Test with one agent**
5. **Iterate and expand to other MCP servers**
6. **Full integration testing**
7. **Demo rehearsal**

Would you like me to proceed with implementing the MCP server approach?

---

**Document Version**: 1.0  
**Last Updated**: 2026-04-26  
**Created By**: Bob (AI Planning Agent)  
**Status**: Ready for Review and Implementation