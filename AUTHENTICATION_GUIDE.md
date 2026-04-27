# Banking Demo - Authentication Implementation Guide

## 🔐 Overview

The banking demo now implements a proper authentication flow using Customer ID and PIN code verification before allowing any banking operations.

---

## 🎯 Authentication Flow

### Step 1: Customer Initiates Contact
Customer starts conversation with the Banking Orchestrator Agent

### Step 2: Authentication Request
Orchestrator asks for:
- **Customer ID** (e.g., CUST-001)
- **4-digit PIN** (e.g., 1234)

### Step 3: Credential Verification
Orchestrator calls `authenticate_customer` tool with provided credentials

### Step 4: Session Token Generation
On successful authentication:
- System generates a unique session token
- Token format: `SESSION-{customer_id}-{timestamp}`
- Token stored in server-side session store

### Step 5: Authenticated Operations
Orchestrator passes session token to specialist agents for all operations

---

## 👥 Demo Credentials

### Emma Thompson (Primary Demo Customer)
- **Customer ID**: `CUST-001`
- **PIN**: `1234`
- **Profile**: Senior Software Engineer, London
- **Credit Score**: 742 (Good)
- **Income**: £65,000/year

### James Patel (Business Customer)
- **Customer ID**: `CUST-002`
- **PIN**: `5678`
- **Profile**: Managing Director, London
- **Credit Score**: 785 (Excellent)
- **Income**: £125,000/year

### Sophie Williams (Young Professional)
- **Customer ID**: `CUST-003`
- **PIN**: `9012`
- **Profile**: Marketing Coordinator, Manchester
- **Credit Score**: 680 (Good)
- **Income**: £32,000/year

---

## 🔧 Technical Implementation

### 1. Data Layer (`data/customers.json`)

Each customer record now includes a PIN field:

```json
{
  "CUST-001": {
    "customer_id": "CUST-001",
    "pin": "1234",
    "first_name": "Emma",
    "last_name": "Thompson",
    ...
  }
}
```

### 2. Core Banking Server (`toolkits/core_banking_server.py`)

#### Session Store
```python
# In-memory session store (demo implementation)
authenticated_sessions = {}
```

#### authenticate_customer Tool
```python
Tool(
    name="authenticate_customer",
    description="Authenticate a customer using their customer ID and PIN code",
    inputSchema={
        "type": "object",
        "properties": {
            "customer_id": {"type": "string"},
            "pin": {"type": "string"}
        },
        "required": ["customer_id", "pin"]
    }
)
```

**Implementation**:
1. Validates customer ID exists
2. Verifies PIN matches
3. Generates session token
4. Stores session in memory
5. Returns success with token and customer name

**Response on Success**:
```json
{
    "status": "success",
    "message": "Welcome back, Emma Thompson!",
    "session_token": "SESSION-CUST-001-20260426182400",
    "customer_id": "CUST-001",
    "customer_name": "Emma Thompson"
}
```

**Response on Failure**:
```json
{
    "status": "error",
    "message": "Invalid customer ID or PIN"
}
```

#### Modified get_current_customer Tool
```python
Tool(
    name="get_current_customer",
    description="Get the currently authenticated customer's information",
    inputSchema={
        "type": "object",
        "properties": {
            "session_token": {"type": "string"}
        },
        "required": ["session_token"]
    }
)
```

**Implementation**:
1. Validates session token exists
2. Retrieves customer ID from session
3. Loads customer data
4. Returns customer profile and accounts

**Response on Success**:
```json
{
    "status": "success",
    "customer_id": "CUST-001",
    "customer_name": "Emma Thompson",
    "email": "emma.thompson@email.co.uk",
    "phone": "+44 20 7946 0123",
    "accounts": [...]
}
```

**Response on Failure**:
```json
{
    "status": "error",
    "message": "Not authenticated. Please authenticate first using authenticate_customer."
}
```

### 3. Banking Orchestrator Agent

**Tools**:
- `core-banking:authenticate_customer`

**Instructions** (Key Points):
```yaml
CRITICAL - Customer Authentication Flow:
1. When a customer first contacts you, you MUST authenticate them
2. Ask for their Customer ID and 4-digit PIN
3. Call authenticate_customer with the provided credentials
4. If authentication succeeds, you'll receive a session_token
5. Pass this session_token to all specialist agents
6. If authentication fails, ask them to try again
```

**Workflow**:
1. Customer: "I'd like to check my balance"
2. Orchestrator: "To help you, I need to verify your identity. Please provide your Customer ID and 4-digit PIN."
3. Customer: "CUST-001 and 1234"
4. Orchestrator calls `authenticate_customer(customer_id="CUST-001", pin="1234")`
5. Receives session token: `SESSION-CUST-001-20260426182400`
6. Routes to customer_service_agent with session token
7. Customer service agent calls `get_current_customer(session_token="SESSION-CUST-001-20260426182400")`
8. Proceeds with balance check

### 4. Specialist Agents

All specialist agents (Customer Service, Loan Processing, Fraud Detection) updated to:

**Instructions**:
```yaml
IMPORTANT: The orchestrator will provide you with a session_token from the authenticated customer. 
You MUST use this session_token when calling get_current_customer.
```

**Tools**:
- `core-banking:get_current_customer` (requires session_token parameter)

**Workflow**:
1. Receive request from orchestrator with session token
2. Call `get_current_customer(session_token=token)`
3. If successful, proceed with customer's request
4. If authentication error, inform customer to authenticate

---

## 🧪 Testing the Authentication Flow

### Test Scenario 1: Successful Authentication

**User**: "What's my account balance?"

**Expected Flow**:
1. Orchestrator: "To help you, I need to verify your identity. Please provide your Customer ID and 4-digit PIN."
2. User: "CUST-001 and 1234"
3. Orchestrator: Calls `authenticate_customer`
4. System: Returns session token
5. Orchestrator: "Welcome back, Emma Thompson! Let me check your balance."
6. Routes to customer_service_agent with session token
7. Agent: Returns balance £4,250.50

### Test Scenario 2: Failed Authentication

**User**: "Check my balance"

**Expected Flow**:
1. Orchestrator: "Please provide your Customer ID and PIN"
2. User: "CUST-001 and 9999" (wrong PIN)
3. Orchestrator: Calls `authenticate_customer`
4. System: Returns error "Invalid customer ID or PIN"
5. Orchestrator: "I'm sorry, those credentials don't match our records. Please try again or contact support."

### Test Scenario 3: Loan Application with Authentication

**User**: "I'd like to apply for a £20,000 loan"

**Expected Flow**:
1. Orchestrator: "I can help with that. First, please provide your Customer ID and PIN"
2. User: "CUST-001 and 1234"
3. Orchestrator: Authenticates successfully
4. Orchestrator: "Welcome back, Emma! Let me check your loan eligibility."
5. Routes to loan_processing_agent with session token
6. Loan agent: Calls `get_current_customer(session_token)`
7. Loan agent: Checks eligibility, generates offers
8. Returns: "You're eligible for up to £32,500..."

---

## 🔒 Security Considerations

### Current Implementation (Demo)
- **Session Store**: In-memory (resets on server restart)
- **PIN Storage**: Plain text in JSON (demo only)
- **Session Tokens**: Simple timestamp-based format
- **No Expiration**: Sessions don't expire
- **No Rate Limiting**: Unlimited authentication attempts

### Production Requirements
- **Session Store**: Redis or database-backed
- **PIN Storage**: Hashed with bcrypt/argon2
- **Session Tokens**: Cryptographically secure random tokens
- **Expiration**: 15-30 minute session timeout
- **Rate Limiting**: Max 3 failed attempts, then lockout
- **MFA**: Two-factor authentication for high-value operations
- **Audit Logging**: Log all authentication attempts
- **HTTPS**: All communications encrypted
- **Token Rotation**: Refresh tokens periodically

---

## 📋 Deployment Checklist

### Before Deploying

- [x] Add PIN codes to customer data
- [x] Implement `authenticate_customer` tool
- [x] Modify `get_current_customer` to require session token
- [x] Update Banking Orchestrator Agent with authentication tool
- [x] Update all specialist agents to use session tokens
- [x] Copy updated data files to deployment location
- [x] Test authentication flow locally

### To Deploy

```bash
cd banking-demo

# 1. Ensure data files are updated
cp data/customers.json toolkits/data/customers.json

# 2. Activate environment
source ../.venv/bin/activate

# 3. Reactivate watsonx Orchestrate environment (if token expired)
orchestrate env activate wxo-edu

# 4. Run deployment script
./import-all.sh
```

### After Deploying

- [ ] Test authentication with Emma Thompson (CUST-001, PIN: 1234)
- [ ] Test authentication failure with wrong PIN
- [ ] Test balance check after authentication
- [ ] Test loan application after authentication
- [ ] Test session token passing between agents
- [ ] Verify error handling for unauthenticated requests

---

## 🎬 Demo Script with Authentication

### Opening (30 seconds)
"Today I'll demonstrate our AI-powered banking platform with secure customer authentication. Watch how the system verifies identity before providing any banking services."

### Demo 1: Authentication & Balance Check (2 minutes)
1. **User**: "What's my account balance?"
2. **System**: "To help you, please provide your Customer ID and PIN"
3. **User**: "CUST-001 and 1234"
4. **System**: "Welcome back, Emma Thompson! Your current account balance is £4,250.50"

**Highlight**: "Notice how the system authenticated the customer before revealing any account information. This protects customer privacy and prevents unauthorized access."

### Demo 2: Failed Authentication (1 minute)
1. **User**: "Check my balance"
2. **System**: "Please provide your Customer ID and PIN"
3. **User**: "CUST-001 and 9999"
4. **System**: "Invalid credentials. Please try again."

**Highlight**: "The system protects against unauthorized access by validating credentials before any operations."

### Demo 3: Loan Application (3 minutes)
1. **User**: "I'd like to apply for a £20,000 personal loan"
2. **System**: "First, let me verify your identity. Customer ID and PIN?"
3. **User**: "CUST-001 and 1234"
4. **System**: "Welcome back, Emma! Checking your eligibility..."
5. **System**: "You're eligible for up to £32,500. Here are three loan offers..."

**Highlight**: "The authentication token is securely passed between agents, maintaining the session throughout the multi-step loan application process."

---

## 🔄 Migration from Auto-Authentication

### What Changed

**Before** (Auto-Authentication):
- `get_current_customer` had no parameters
- Always returned Emma Thompson (CUST-001)
- No credential verification
- Suitable for simple demos only

**After** (PIN Authentication):
- `authenticate_customer` tool added
- `get_current_customer` requires session_token
- Credentials verified against customer data
- Session management implemented
- More realistic banking security

### Benefits

1. **Security**: Proper authentication before operations
2. **Multi-User**: Can demo with different customers
3. **Realistic**: Matches real banking workflows
4. **Compliance**: Demonstrates security best practices
5. **Flexibility**: Easy to switch between customers

---

## 📞 Troubleshooting

### Issue: "Not authenticated" Error

**Cause**: Session token not provided or invalid

**Solution**:
1. Ensure orchestrator calls `authenticate_customer` first
2. Verify session token is passed to specialist agents
3. Check session store hasn't been cleared (server restart)

### Issue: "Invalid customer ID or PIN"

**Cause**: Wrong credentials provided

**Solution**:
1. Verify customer ID format (CUST-001, not just 001)
2. Check PIN is correct (1234 for Emma Thompson)
3. Ensure customer data file has PIN field

### Issue: Orchestrator Not Asking for Authentication

**Cause**: Agent instructions not updated

**Solution**:
1. Verify orchestrator has `authenticate_customer` tool
2. Check instructions mention authentication flow
3. Redeploy orchestrator agent

---

**Last Updated**: 2026-04-26  
**Implementation By**: Bob (WXO Agent Architect)  
**Status**: Ready for Deployment (pending token refresh)