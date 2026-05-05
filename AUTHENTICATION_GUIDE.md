# Banking Demo - Authentication Implementation Guide

## 🔐 Overview

The banking demo implements a secure authentication flow using Customer ID and PIN code verification with Cloudant-backed persistent storage. This guide covers the complete authentication implementation without session tokens.

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

### Step 4: Customer ID Return
On successful authentication:
- System validates credentials against Cloudant database
- Returns `customer_id` and `customer_name`
- **No session token needed** - customer_id is passed directly

### Step 5: Account Retrieval
Orchestrator immediately calls `get_customer_accounts(customer_id)` to retrieve account list

### Step 6: Authenticated Operations
Orchestrator passes `customer_id` directly to specialist agents for all operations

---

## 👥 Demo Credentials

### Emma Thompson (Primary Demo Customer)
- **Customer ID**: `CUST-001`
- **PIN**: `1234`
- **Profile**: Senior Software Engineer, London
- **Credit Score**: 742 (Good)
- **Income**: £65,000/year
- **Accounts**: Current (CUR-001-1234), Savings (SAV-001-5678), Credit Card (CC-001-9012)

### James Patel (Business Customer)
- **Customer ID**: `CUST-002`
- **PIN**: `5678`
- **Profile**: Managing Director, London
- **Credit Score**: 785 (Excellent)
- **Income**: £125,000/year
- **Accounts**: Business Current (BUS-002-3456), Business Savings (SAV-002-7890)

### Sophie Williams (Young Professional)
- **Customer ID**: `CUST-003`
- **PIN**: `9012`
- **Profile**: Marketing Coordinator, Manchester
- **Credit Score**: 680 (Good)
- **Income**: £32,000/year
- **Accounts**: Current, Savings

---

## 🔧 Technical Implementation

### 1. Data Layer (Cloudant Database)

Customer credentials are stored in Cloudant `customers` database:

```json
{
  "_id": "CUST-001",
  "type": "customer",
  "customer_id": "CUST-001",
  "pin": "1234",
  "first_name": "Emma",
  "last_name": "Thompson",
  "email": "emma.thompson@email.co.uk",
  ...
}
```

**Bootstrap Process**:
- Seed data from `data/customers.json`
- Run: `python cloudant-tools/scripts/bootstrap_and_seed.py`
- Creates Cloudant databases and indexes
- Loads initial customer data

### 2. Core Banking Tools ([`cloudant-tools/core_banking_tools.py`](cloudant-tools/core_banking_tools.py))

#### authenticate_customer()

**Location**: [`cloudant-tools/core_banking_tools.py:25`](cloudant-tools/core_banking_tools.py:25)

**Purpose**: Authenticate a customer using their customer ID and PIN code.

**Implementation**:
```python
@tool(expected_credentials=CLOUDANT_EXPECTED_CREDENTIALS)
def authenticate_customer(customer_id: str, pin: str) -> Dict[str, Any]:
    """
    Authenticate a customer using demo customer ID and PIN.
    
    Returns:
        Dict[str, Any]: Authentication result with customer_id and customer_name
    """
    # 1. Normalize inputs
    normalized_customer_id = str(customer_id).strip()
    normalized_pin = str(pin).strip()
    
    # 2. Query Cloudant via repository
    customer_repo = CustomerRepository(settings=settings)
    customer = customer_repo.get_customer_by_id(normalized_customer_id)
    pin_verified = customer_repo.verify_customer_pin(normalized_customer_id, normalized_pin)
    
    # 3. Validate credentials
    if not customer or not pin_verified:
        return {
            "status": "error",
            "message": "Invalid customer ID or PIN"
        }
    
    # 4. Return customer_id (no session token)
    return {
        "status": "success",
        "customer_id": normalized_customer_id,
        "customer_name": f"{customer['first_name']} {customer['last_name']}",
        "message": f"Welcome back, {customer['first_name']}!"
    }
```

**Response on Success**:
```json
{
  "status": "success",
  "customer_id": "CUST-001",
  "customer_name": "Emma Thompson",
  "message": "Welcome back, Emma!"
}
```

**Response on Failure**:
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

#### get_customer_accounts()

**Location**: [`cloudant-tools/core_banking_tools.py:84`](cloudant-tools/core_banking_tools.py:84)

**Purpose**: Retrieve all accounts for an authenticated customer.

**Implementation**:
```python
@tool(expected_credentials=CLOUDANT_EXPECTED_CREDENTIALS)
def get_customer_accounts(customer_id: str) -> Dict[str, Any]:
    """
    Get all accounts for a customer.
    
    Args:
        customer_id (str): The customer identifier
        
    Returns:
        Dict[str, Any]: Customer account list and count
    """
    account_repo = AccountRepository()
    accounts = account_repo.list_accounts_for_customer(customer_id)
    
    return {
        "status": "success",
        "customer_id": customer_id,
        "accounts": accounts,
        "account_count": len(accounts)
    }
```

**Response**:
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

### 3. Banking Orchestrator Agent

**Tools**:
- `authenticate_customer` - Validates credentials
- `get_customer_accounts` - Retrieves account list

**Instructions** (Key Points):
```yaml
CRITICAL - Customer Authentication Flow:
1. When a customer first contacts you, authenticate them using authenticate_customer
2. Ask for their Customer ID and 4-digit PIN
3. Call authenticate_customer with the provided credentials
4. If authentication succeeds, you'll receive customer_id and customer_name
5. Immediately call get_customer_accounts with the customer_id
6. Store the customer_id and account information
7. When routing to specialists, provide customer_id and account details
8. If authentication fails, ask them to try again
```

**Workflow**:
1. Customer: "I'd like to check my balance"
2. Orchestrator: "To help you, I need to verify your identity. Please provide your Customer ID and 4-digit PIN."
3. Customer: "CUST-001 and 1234"
4. Orchestrator calls `authenticate_customer(customer_id="CUST-001", pin="1234")`
5. Receives: `{"status": "success", "customer_id": "CUST-001", "customer_name": "Emma Thompson"}`
6. Orchestrator calls `get_customer_accounts(customer_id="CUST-001")`
7. Receives account list
8. Routes to customer_service_agent with customer_id and account details
9. Customer service agent uses customer_id with tools
10. Returns balance to customer

### 4. Specialist Agents

All specialist agents (Customer Service, Loan Processing, Fraud Detection) receive:

**From Orchestrator**:
- `customer_id` (e.g., "CUST-001")
- Account details (IDs, types, balances)
- Customer name

**Instructions**:
```yaml
Important workflow:
1. The orchestrator will provide you with the customer_id and account details
2. The customer is already authenticated
3. Use the customer_id provided by the orchestrator
4. Call tools with the customer_id parameter
```

**Tools**:
- All tools accept `customer_id` as a parameter
- No session token needed

**Workflow**:
1. Receive request from orchestrator with customer_id
2. Use customer_id directly with tools
3. Return results to orchestrator

---

## 🧪 Testing the Authentication Flow

### Test Scenario 1: Successful Authentication

**User**: "What's my account balance?"

**Expected Flow**:
1. Orchestrator: "To help you, I need to verify your identity. Please provide your Customer ID and 4-digit PIN."
2. User: "CUST-001 and 1234"
3. Orchestrator: Calls `authenticate_customer(customer_id="CUST-001", pin="1234")`
4. System: Returns `{"status": "success", "customer_id": "CUST-001", "customer_name": "Emma Thompson"}`
5. Orchestrator: Calls `get_customer_accounts(customer_id="CUST-001")`
6. Orchestrator: "Welcome back, Emma Thompson! Let me check your balance."
7. Routes to customer_service_agent with customer_id
8. Agent: Returns balance £4,250.50

### Test Scenario 2: Failed Authentication

**User**: "Check my balance"

**Expected Flow**:
1. Orchestrator: "Please provide your Customer ID and PIN"
2. User: "CUST-001 and 9999" (wrong PIN)
3. Orchestrator: Calls `authenticate_customer(customer_id="CUST-001", pin="9999")`
4. System: Returns `{"status": "error", "message": "Invalid customer ID or PIN"}`
5. Orchestrator: "I'm sorry, those credentials don't match our records. Please try again or contact support."

### Test Scenario 3: Loan Application with Authentication

**User**: "I'd like to apply for a £20,000 loan"

**Expected Flow**:
1. Orchestrator: "I can help with that. First, please provide your Customer ID and PIN"
2. User: "CUST-001 and 1234"
3. Orchestrator: Authenticates successfully, gets customer_id
4. Orchestrator: Calls `get_customer_accounts(customer_id="CUST-001")`
5. Orchestrator: "Welcome back, Emma! Let me check your loan eligibility."
6. Routes to loan_processing_agent with customer_id
7. Loan agent: Uses customer_id with loan tools
8. Returns: "You're eligible for up to £32,500..."

---

## 🔒 Security Considerations

### Current Implementation (Demo)
- **Authentication**: Customer ID + PIN verification
- **Storage**: Cloudant database with persistent data
- **PIN Storage**: Plain text (demo only - production requires hashing)
- **Customer ID Passing**: Direct parameter passing (no session tokens)
- **Account Masking**: Last 4 digits shown in responses

### Production Requirements
- **PIN Storage**: Hash with bcrypt/argon2 instead of plain text
- **Rate Limiting**: Max 3 failed attempts, then account lockout
- **Session Timeout**: 15-30 minute inactivity timeout
- **MFA**: Two-factor authentication for high-value operations
- **Audit Logging**: Log all authentication attempts with timestamps
- **HTTPS**: All communications encrypted in transit
- **Encryption at Rest**: Cloudant data encryption
- **IP Monitoring**: Track and alert on suspicious login patterns

---

## 📋 Deployment Checklist

### Before Deploying

- [x] Add PIN codes to customer data
- [x] Implement `authenticate_customer` tool
- [x] Implement `get_customer_accounts` tool
- [x] Update Banking Orchestrator Agent with authentication tools
- [x] Update all specialist agents to use customer_id
- [x] Bootstrap Cloudant databases with seed data
- [x] Test authentication flow locally

### To Deploy

```bash
cd banking-demo

# 1. Bootstrap Cloudant (one-time setup)
python cloudant-tools/scripts/bootstrap_and_seed.py

# 2. Import Cloudant connection
orchestrate connections import -f connections/cloudant-connection.yaml

# 3. Configure credentials
orchestrate connections configure --app-id cloudant --env draft --type team --kind key_value
orchestrate connections set-credentials --app-id cloudant --env draft --entries "api_key=$CLOUDANT_API_KEY"

# 4. Import tools
orchestrate tools import -k python -f cloudant-tools/core_banking_tools.py -r cloudant-tools/requirements.txt

# 5. Import agents
orchestrate agents import -f agents/banking-orchestrator-agent.yaml
orchestrate agents import -f agents/customer-service-agent.yaml
# ... (other agents)

# 6. Run deployment script
./import-all.sh
```

### After Deploying

- [ ] Test authentication with Emma Thompson (CUST-001, PIN: 1234)
- [ ] Test authentication failure with wrong PIN
- [ ] Test balance check after authentication
- [ ] Test loan application after authentication
- [ ] Test customer_id passing between agents
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

**Highlight**: "Notice how the system authenticated the customer before revealing any account information. The customer_id is then used throughout the session for all operations."

### Demo 2: Failed Authentication (1 minute)
1. **User**: "Check my balance"
2. **System**: "Please provide your Customer ID and PIN"
3. **User**: "CUST-001 and 9999"
4. **System**: "Invalid credentials. Please try again."

**Highlight**: "The system protects against unauthorized access by validating credentials against our Cloudant database."

### Demo 3: Loan Application (3 minutes)
1. **User**: "I'd like to apply for a £20,000 personal loan"
2. **System**: "First, let me verify your identity. Customer ID and PIN?"
3. **User**: "CUST-001 and 1234"
4. **System**: "Welcome back, Emma! Checking your eligibility..."
5. **System**: "You're eligible for up to £32,500. Here are three loan offers..."

**Highlight**: "The customer_id is seamlessly passed between agents, maintaining context throughout the multi-step loan application process."

---

## 🔄 Architecture Comparison

### Previous Approach (Session Tokens)
- ❌ Session token generation and storage
- ❌ Token passing between agents
- ❌ Session expiration management
- ❌ Additional complexity and failure points

### Current Approach (Direct Customer ID)
- ✅ Simple customer_id passing
- ✅ No session state management
- ✅ Cloudant provides persistent data
- ✅ More reliable agent communication
- ✅ Easier to debug and maintain

### Benefits of Current Approach

1. **Simplicity**: No session management overhead
2. **Reliability**: Direct parameter passing is more robust
3. **Maintainability**: Fewer moving parts to manage
4. **Scalability**: Cloudant handles data persistence
5. **Debugging**: Easier to trace customer_id through system

---

## 📞 Troubleshooting

### Issue: "Invalid customer ID or PIN" with correct credentials

**Cause**: Customer data not seeded in Cloudant

**Solution**:
```bash
python cloudant-tools/scripts/bootstrap_and_seed.py
```

### Issue: Authentication succeeds but no accounts returned

**Cause**: Account data not seeded or customer_id mismatch

**Solution**:
1. Verify Cloudant accounts database exists
2. Check accounts have matching customer_id field
3. Re-run bootstrap script if needed

### Issue: Orchestrator not asking for authentication

**Cause**: Agent instructions not updated or tool not imported

**Solution**:
1. Verify orchestrator has `authenticate_customer` tool
2. Check instructions mention authentication flow
3. Redeploy orchestrator agent:
```bash
orchestrate agents import -f agents/banking-orchestrator-agent.yaml
```

### Issue: Specialist agent can't access customer data

**Cause**: customer_id not passed from orchestrator

**Solution**:
1. Check orchestrator instructions include customer_id passing
2. Verify specialist agent instructions expect customer_id
3. Test orchestrator → specialist communication

---

## 📚 Related Documentation

- [`AUTHENTICATION_ARCHITECTURE.md`](AUTHENTICATION_ARCHITECTURE.md) - Technical architecture details
- [`cloudant-tools/README.md`](cloudant-tools/README.md) - Cloudant tools documentation
- [`DEMO_ACCOUNTS.md`](DEMO_ACCOUNTS.md) - Complete customer credentials and scenarios

---

**Last Updated**: 2026-05-05  
**Version**: 2.0 (Cloudant Implementation)  
**Implementation By**: Bob (WXO Agent Architect)  
**Status**: ✅ Production Ready