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
Core Banking Server → Validates credentials
Core Banking Server → Creates session_token
Core Banking Server → Saves session to sessions.json
Orchestrator → Receives session_token
```

### 2. Customer Context Retrieval
After authentication, the orchestrator immediately retrieves full customer details:

```
Orchestrator → Calls get_current_customer(session_token)
Core Banking Server → Loads sessions.json
Core Banking Server → Validates session_token
Core Banking Server → Retrieves customer data
Core Banking Server → Returns customer_id, name, accounts
Orchestrator → Stores customer context
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

## Session Management

### File-Based Sessions
Sessions are persisted in `data/sessions.json`:

```json
{
  "sess_abc123": {
    "customer_id": "CUST-001",
    "authenticated_at": "2026-04-26T19:00:00.000Z"
  }
}
```

**Why file-based?**
- MCP server instances don't share memory
- Each tool call may use a different server instance
- File-based storage ensures session persistence across calls

### Session Token Format
- Format: `sess_` + 16 random hex characters
- Example: `sess_a1b2c3d4e5f6g7h8`
- Stored in sessions.json with customer_id and timestamp

## Agent Architecture

### Orchestrator Agent (banking_orchestrator_agent)

**Responsibilities:**
1. Authenticate customers (calls `authenticate_customer`)
2. Retrieve customer context (calls `get_current_customer`)
3. Route to specialist agents
4. Pass customer_id and account details to specialists
5. Present unified responses

**Tools:**
- `core-banking:authenticate_customer`
- `core-banking:get_current_customer`

**Key Instructions:**
```yaml
CRITICAL - Customer Authentication Flow:
1. Authenticate using authenticate_customer tool
2. Immediately call get_current_customer with session_token
3. Store customer_id and account information
4. When routing to specialists, provide customer_id and account details

CRITICAL - Invisible Orchestration:
- NEVER say "I'll send this to the customer service team"
- Simply present information as if you retrieved it yourself
```

### Specialist Agents

**Customer Service Agent (customer_service_agent)**
- Receives: customer_id, account details from orchestrator
- Does NOT call: `get_current_customer`
- Uses: Provided customer_id for all operations

**Fraud Detection Agent (fraud_detection_agent)**
- Receives: customer_id, account details from orchestrator
- Does NOT call: `get_current_customer`
- Uses: Provided customer_id for fraud analysis

**Loan Processing Agent (loan_processing_agent)**
- Receives: customer_id, account details from orchestrator
- Does NOT call: `get_current_customer`
- Uses: Provided customer_id for loan operations

## Why This Architecture?

### Problem: Session Token Passing Failed
Initial approach tried to pass session_token to specialist agents, but:
- Collaborator handoff mechanism didn't reliably pass session_token
- Specialist agents received "Invalid tool parameters" errors
- Session token was lost in agent-to-agent communication

### Solution: Orchestrator Retrieves, Specialists Use
Current approach:
1. **Orchestrator authenticates** - Gets session_token
2. **Orchestrator retrieves** - Calls get_current_customer(session_token)
3. **Orchestrator passes** - Provides customer_id to specialists
4. **Specialists use** - Use customer_id directly (no session_token needed)

**Benefits:**
- ✅ Simpler specialist agent logic
- ✅ No session token passing issues
- ✅ Clear separation of concerns
- ✅ Reliable customer context
- ✅ Better error handling

## Demo Accounts

### Emma Thompson (Primary Demo Customer)
- **Customer ID**: CUST-001
- **PIN**: 1234
- **Accounts**: Current (ACC-001), Savings (ACC-002), Credit Card (ACC-003)

### James Patel (Business Customer)
- **Customer ID**: CUST-002
- **PIN**: 5678
- **Accounts**: Business Current (ACC-004), Business Savings (ACC-005)

### Sophie Williams (Young Professional)
- **Customer ID**: CUST-003
- **PIN**: 9012
- **Accounts**: Current (ACC-006), Savings (ACC-007)

## Testing the Authentication Flow

### Test 1: Simple Balance Check
```
User: "What's my balance?"
System: "To check your balance, I'll need to verify your identity. Please provide your Customer ID and PIN code."
User: "CUST-001 and 1234"
System: "Hello Emma! Your Current Account (****0001) balance is £12,450.75"
```

### Test 2: Multi-Customer Testing
```
User: "What's my balance?"
System: "Please provide your Customer ID and PIN code."
User: "CUST-002 and 5678"
System: "Hello James! Your Business Current Account (****0004) balance is £45,230.50"
```

### Test 3: Invalid Credentials
```
User: "What's my balance?"
System: "Please provide your Customer ID and PIN code."
User: "CUST-001 and 9999"
System: "Authentication failed. Invalid Customer ID or PIN. Please try again."
```

## Security Considerations

### Current Implementation
- ✅ PIN verification required
- ✅ Session tokens for authenticated state
- ✅ File-based session persistence
- ✅ Customer ID validation
- ✅ Account number masking in responses

### Future Enhancements
- [ ] Session expiration (timeout after inactivity)
- [ ] Multi-factor authentication (MFA) for high-value transactions
- [ ] Rate limiting on authentication attempts
- [ ] Audit logging of authentication events
- [ ] Encrypted session storage
- [ ] IP-based fraud detection

## Troubleshooting

### Issue: "Invalid tool parameters" error
**Cause**: Specialist agent trying to call `get_current_customer` with session_token  
**Solution**: Remove `get_current_customer` from specialist agent tools list

### Issue: Session not found
**Cause**: sessions.json file missing or corrupted  
**Solution**: Ensure sessions.json exists in data/ directory (created automatically)

### Issue: Authentication fails with valid credentials
**Cause**: PIN mismatch in customers.json  
**Solution**: Verify PIN in data/customers.json matches expected value

### Issue: Orchestrator mentions "customer service team"
**Cause**: Instructions not emphasizing invisible orchestration  
**Solution**: Update orchestrator instructions to never mention routing

## File Locations

- **Session Storage**: `banking-demo/data/sessions.json`
- **Customer Data**: `banking-demo/data/customers.json`
- **Core Banking Server**: `banking-demo/toolkits/core_banking_server.py`
- **Orchestrator Agent**: `banking-demo/agents/banking-orchestrator-agent.yaml`
- **Specialist Agents**: `banking-demo/agents/customer-service-agent.yaml`, etc.

## Summary

The authentication architecture provides:
1. **Secure authentication** with Customer ID and PIN
2. **Persistent sessions** using file-based storage
3. **Clean separation** between orchestrator and specialists
4. **Reliable context passing** via customer_id
5. **Multi-customer support** for comprehensive testing

This architecture ensures secure, reliable, and testable authentication for the banking demo.