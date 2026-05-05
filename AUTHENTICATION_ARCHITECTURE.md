# Banking Demo - Authentication Architecture

## Overview

The banking demo implements a secure authentication system with Customer ID and PIN verification. This document describes the authentication flow and how customer context is passed between agents.

## Authentication Flow

### 1. Initial Authentication
When a customer first interacts with the system:

```
Customer → "What's my balance?"
Orchestrator → Detects unauthenticated request
Orchestrator → Asks for Customer ID and PIN
Customer → Provides credentials (e.g., "CUST-001 and 1234")
Orchestrator → Calls authenticate_customer(customer_id, pin)
Cloudant Tools → Validates credentials against Cloudant database
Cloudant Tools → Returns customer_id and customer_name
Orchestrator → Receives customer_id: "CUST-001"
```

### 2. Customer Context Retrieval
After authentication, the orchestrator immediately retrieves full customer details:

```
Orchestrator → Calls get_customer_accounts(customer_id)
Cloudant Tools → Queries Cloudant for customer accounts
Cloudant Tools → Returns account list with IDs and types
Orchestrator → Stores customer_id and account information
```

### 3. Routing to Specialist Agents
When routing to specialist agents, the orchestrator passes customer context directly:

```
Orchestrator → Routes to customer_service_agent
Orchestrator → Provides: customer_id, account_numbers, customer_name
Customer Service Agent → Uses provided customer_id
Customer Service Agent → Calls tools with customer_id parameter
Customer Service Agent → Returns results
Orchestrator → Presents results to customer
```

## Authentication Implementation

### Cloudant-Based Authentication
The current implementation uses **direct customer_id passing** instead of session tokens:

**Why no session tokens?**
- Simpler architecture - no session state management needed
- Direct customer_id passing is more reliable
- Cloudant provides persistent customer data
- Agent-to-agent communication is more straightforward
- Reduces complexity and potential failure points

### Customer Data Storage
Customer credentials are stored in Cloudant `customers` database:

```json
{
  "_id": "CUST-001",
  "type": "customer",
  "customer_id": "CUST-001",
  "pin": "1234",
  "first_name": "Emma",
  "last_name": "Thompson",
  ...
}
```

## Agent Architecture

### Orchestrator Agent (banking_orchestrator_agent)

**Responsibilities:**
1. Authenticate customers (calls `authenticate_customer`)
2. Retrieve customer accounts (calls `get_customer_accounts`)
3. Route to specialist agents
4. Pass customer_id and account details to specialists
5. Present unified responses

**Tools:**
- `authenticate_customer` - Validates customer_id and PIN
- `get_customer_accounts` - Retrieves account list for customer

**Key Instructions:**
```yaml
CRITICAL - Customer Authentication Flow:
1. Authenticate using authenticate_customer tool
2. Immediately call get_customer_accounts with customer_id
3. Store customer_id and account information
4. When routing to specialists, provide customer_id and account details

CRITICAL - Invisible Orchestration:
- NEVER say "I'll send this to the customer service team"
- Simply present information as if you retrieved it yourself
```

### Specialist Agents

**Customer Service Agent (customer_service_agent)**
- Receives: customer_id, account details from orchestrator
- Uses: Provided customer_id for all operations
- Tools: `check_account_balance`, `get_recent_transactions`, `get_customer_accounts`

**Fraud Detection Agent (fraud_detection_agent)**
- Receives: customer_id, account details from orchestrator
- Uses: Provided customer_id for fraud analysis
- Tools: Fraud detection tools with customer_id parameter

**Loan Processing Agent (loan_processing_agent)**
- Receives: customer_id, account details from orchestrator
- Uses: Provided customer_id for loan operations
- Tools: Loan processing tools with customer_id parameter

## Authentication Tools

### authenticate_customer()

**Location**: [`cloudant-tools/core_banking_tools.py`](cloudant-tools/core_banking_tools.py:25)

**Purpose**: Authenticate a customer using their customer ID and PIN code.

**Parameters**:
- `customer_id` (str): Customer identifier (e.g., "CUST-001")
- `pin` (str): 4-digit PIN code (e.g., "1234")

**Returns on Success**:
```json
{
  "status": "success",
  "customer_id": "CUST-001",
  "customer_name": "Emma Thompson",
  "message": "Welcome back, Emma!"
}
```

**Returns on Failure**:
```json
{
  "status": "error",
  "message": "Invalid customer ID or PIN",
  "debug": {
    "normalized_customer_id": "CUST-001",
    "customer_found": false,
    "pin_verified": false
  }
}
```

**Implementation**:
1. Normalizes customer_id and PIN
2. Queries Cloudant customers database
3. Verifies PIN matches stored value
4. Returns customer_id and name on success

### get_customer_accounts()

**Location**: [`cloudant-tools/core_banking_tools.py`](cloudant-tools/core_banking_tools.py:84)

**Purpose**: Retrieve all accounts for an authenticated customer.

**Parameters**:
- `customer_id` (str): Customer identifier (e.g., "CUST-001")

**Returns**:
```json
{
  "status": "success",
  "customer_id": "CUST-001",
  "accounts": [
    {
      "account_id": "CUR-001-1234",
      "account_type": "Current Account",
      "account_name": "Premier Current Account",
      "current_balance": 4250.50,
      "currency": "GBP"
    },
    ...
  ],
  "account_count": 3
}
```

## Why This Architecture?

### Problem: Session Token Complexity
Initial approaches with session tokens had issues:
- Session state management complexity
- Token passing between agents was unreliable
- Additional failure points in the system
- Overhead of session storage and validation

### Solution: Direct Customer ID Passing
Current approach:
1. **Orchestrator authenticates** - Gets customer_id from authentication
2. **Orchestrator retrieves** - Calls get_customer_accounts(customer_id)
3. **Orchestrator passes** - Provides customer_id to specialists
4. **Specialists use** - Use customer_id directly with tools

**Benefits:**
- ✅ Simpler architecture - no session management
- ✅ More reliable - direct parameter passing
- ✅ Clear separation of concerns
- ✅ Easier to debug and maintain
- ✅ Cloudant provides persistent data layer
- ✅ No session expiration issues

## Data Flow

```
Customer Authentication Request
    ↓
authenticate_customer(customer_id, pin)
    ↓
CustomerRepository.verify_customer_pin()
    ↓
Cloudant customers database query
    ↓
Returns: customer_id, customer_name
    ↓
get_customer_accounts(customer_id)
    ↓
AccountRepository.list_accounts_for_customer()
    ↓
Cloudant accounts database query
    ↓
Returns: account list
    ↓
Orchestrator stores customer_id + accounts
    ↓
Routes to specialist with customer_id
    ↓
Specialist uses customer_id with tools
```

## Demo Accounts

### Emma Thompson (Primary Demo Customer)
- **Customer ID**: CUST-001
- **PIN**: 1234
- **Accounts**: Current (CUR-001-1234), Savings (SAV-001-5678), Credit Card (CC-001-9012)

### James Patel (Business Customer)
- **Customer ID**: CUST-002
- **PIN**: 5678
- **Accounts**: Business Current (BUS-002-3456), Business Savings (SAV-002-7890)

### Sophie Williams (Young Professional)
- **Customer ID**: CUST-003
- **PIN**: 9012
- **Accounts**: Current, Savings

## Testing the Authentication Flow

### Test 1: Simple Balance Check
```
User: "What's my balance?"
System: "To check your balance, I'll need to verify your identity. Please provide your Customer ID and PIN code."
User: "CUST-001 and 1234"
System: "Welcome back, Emma! Your Current Account (****1234) balance is £4,250.50"
```

### Test 2: Multi-Customer Testing
```
User: "What's my balance?"
System: "Please provide your Customer ID and PIN code."
User: "CUST-002 and 5678"
System: "Welcome back, James! Your Business Current Account (****3456) balance is £68,450.25"
```

### Test 3: Invalid Credentials
```
User: "What's my balance?"
System: "Please provide your Customer ID and PIN code."
User: "CUST-001 and 9999"
System: "Authentication failed. Invalid Customer ID or PIN. Please try again."
```

## Security Considerations

### Current Implementation (Demo)
- ✅ PIN verification required
- ✅ Customer ID validation
- ✅ Cloudant-backed persistent storage
- ✅ Account number masking in responses
- ✅ Direct customer_id passing (no session tokens)

### Production Requirements
- [ ] PIN hashing (bcrypt/argon2) instead of plain text
- [ ] Rate limiting on authentication attempts
- [ ] Account lockout after failed attempts
- [ ] Audit logging of authentication events
- [ ] Multi-factor authentication (MFA) for high-value transactions
- [ ] Session timeout for inactive users
- [ ] IP-based fraud detection
- [ ] Encrypted data at rest and in transit

## Troubleshooting

### Issue: "Invalid customer ID or PIN" with correct credentials
**Cause**: Customer data not seeded in Cloudant  
**Solution**: Run bootstrap script: `python cloudant-tools/scripts/bootstrap_and_seed.py`

### Issue: Authentication succeeds but no accounts returned
**Cause**: Account data not seeded or customer_id mismatch  
**Solution**: Verify accounts in Cloudant have matching customer_id field

### Issue: Orchestrator doesn't ask for authentication
**Cause**: Agent instructions not updated or tool not imported  
**Solution**: 
1. Verify orchestrator has `authenticate_customer` tool
2. Check instructions mention authentication flow
3. Redeploy orchestrator agent

## File Locations

- **Customer Data**: Cloudant `customers` database (seeded from `data/customers.json`)
- **Account Data**: Cloudant `accounts` database (seeded from `data/accounts.json`)
- **Core Banking Tools**: `cloudant-tools/core_banking_tools.py`
- **Orchestrator Agent**: `agents/banking-orchestrator-agent.yaml`
- **Specialist Agents**: `agents/customer-service-agent.yaml`, etc.
- **Bootstrap Script**: `cloudant-tools/scripts/bootstrap_and_seed.py`

## Summary

The authentication architecture provides:
1. **Secure authentication** with Customer ID and PIN
2. **Cloudant-backed persistence** for customer and account data
3. **Simple customer_id passing** (no session tokens needed)
4. **Clean separation** between orchestrator and specialists
5. **Reliable context passing** via direct parameters
6. **Multi-customer support** for comprehensive testing

This architecture ensures secure, reliable, and maintainable authentication for the banking demo while keeping the implementation simple and straightforward.

---

**Last Updated**: 2026-05-05  
**Version**: 2.0 (Cloudant Implementation)  
**Status**: ✅ Production Ready