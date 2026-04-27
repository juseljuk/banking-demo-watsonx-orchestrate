# Banking Demo - Account Details Reference

Quick reference for all customer accounts and IDs to use during the demo.

## 🔐 Authentication Required

**The demo implements secure customer authentication.** Before accessing any banking services:
- You **MUST authenticate** with your Customer ID and 4-digit PIN
- The Banking Orchestrator will request your credentials when you first contact it
- After successful authentication, you receive a session token for subsequent operations
- You can then ask naturally without providing account numbers

**Authentication Flow:**
1. **You**: "What's my account balance?"
2. **System**: "To help you, I need to verify your identity. Please provide your Customer ID and 4-digit PIN."
3. **You**: "CUST-001 and 1234"
4. **System**: "Welcome back, Emma Thompson! Your current account balance is £4,250.50"

**Demo Credentials:**
- **Emma Thompson**: Customer ID `CUST-001`, PIN `1234`
- **James Patel**: Customer ID `CUST-002`, PIN `5678`
- **Sophie Williams**: Customer ID `CUST-003`, PIN `9012`

---

## 👤 Customer 1: Emma Thompson (Primary Demo Customer)

**Customer ID:** `CUST-001`

### Accounts

#### Current Account
- **Account ID:** `CUR-001-1234`
- **Account Number (Masked):** `****1234`
- **Sort Code:** `20-00-00`
- **Current Balance:** £4,250.50
- **Available Balance:** £4,250.50
- **Overdraft Limit:** £500.00
- **Daily Transfer Limit:** £10,000.00

#### Savings Account
- **Account ID:** `SAV-001-5678`
- **Account Number (Masked):** `****5678`
- **Sort Code:** `20-00-00`
- **Current Balance:** £18,750.00
- **Available Balance:** £18,750.00
- **Interest Rate:** 4.25% AER

#### Credit Card
- **Account ID:** `CC-001-9012`
- **Card Number (Masked):** `****9012`
- **Credit Limit:** £12,000.00
- **Current Balance:** £1,856.75
- **Available Credit:** £10,143.25
- **Payment Due Date:** 2026-05-15
- **Minimum Payment:** £55.00

### Personal Details
- **Email:** emma.thompson@email.co.uk
- **Phone:** +44 20 7946 0123
- **Mobile:** +44 7700 900123
- **Address:** 42 Kensington High Street, London, W8 5SA
- **Credit Score:** 742 (Good)
- **Annual Income:** £65,000
- **Employment:** Senior Software Engineer at Digital Solutions Ltd

---

## 👤 Customer 2: James Patel (Business Customer)

**Customer ID:** `CUST-002`
**PIN:** `5678`

### Accounts

#### Business Current Account
- **Account ID:** `BUS-002-3456`
- **Account Number (Masked):** `****3456`
- **Sort Code:** `20-00-00`
- **Current Balance:** £68,450.25
- **Available Balance:** £68,450.25
- **Daily Transfer Limit:** £25,000.00

#### Business Savings Account
- **Account ID:** `SAV-002-7890`
- **Account Number (Masked):** `****7890`
- **Sort Code:** `20-00-00`
- **Current Balance:** £125,600.00
- **Available Balance:** £125,600.00
- **Interest Rate:** 3.75% AER

### Personal Details
- **Email:** james.patel@patelconsulting.co.uk
- **Phone:** +44 20 7946 0456
- **Mobile:** +44 7700 900456
- **Address:** 15 Canary Wharf, London, E14 5AB
- **Credit Score:** 785 (Excellent)
- **Annual Income:** £125,000
- **Business:** Patel Consulting Ltd

---

## 👤 Customer 3: Sophie Williams (Young Professional)

**Customer ID:** `CUST-003`
**PIN:** `9012`

### Personal Details
- **Email:** sophie.williams@email.co.uk
- **Phone:** +44 161 496 0789
- **Mobile:** +44 7700 900789
- **Address:** 78 Deansgate, Manchester, M3 2BW
- **Credit Score:** 680 (Good)
- **Annual Income:** £32,000
- **Employment:** Marketing Coordinator at Creative Marketing Ltd

---

## 🎯 Demo Scenarios with Account IDs

### Scenario 1: Check Balance
**Query:** "What's the balance on account CUR-001-1234?"  
**Expected:** £4,250.50

### Scenario 2: View Transactions
**Query:** "Show me recent transactions for account CUR-001-1234"  
**Expected:** 5 recent transactions including salary, groceries, dining

### Scenario 3: Transfer Funds
**Query:** "Transfer £1,500 from CUR-001-1234 to SAV-001-5678"  
**Expected:** Successful transfer confirmation

### Scenario 4: Check Pending Deposits
**Query:** "Are there any pending deposits for CUR-001-1234?"  
**Expected:** £1,200 cheque deposit pending

### Scenario 5: Credit Card Payment Due
**Query:** "When is the payment due for credit card CC-001-9012?"  
**Expected:** 2026-05-15, minimum payment £55.00

### Scenario 6: Get All Customer Accounts
**Query:** "Show me all accounts for customer CUST-001"  
**Expected:** 3 accounts (Current, Savings, Credit Card)

---

## 🚨 Fraud Detection Scenarios

### High-Risk Transaction (BLOCKED)
- **Transaction ID:** `TXN-FRAUD-001`
- **Account:** CUR-001-1234
- **Amount:** £3,500
- **Destination:** Nigeria
- **Risk Score:** 92/100
- **Status:** BLOCKED

### Account Takeover Attempt (CRITICAL)
- **Incident ID:** `FRAUD-INC-002`
- **Account:** CUR-001-1234
- **Pattern:** Multiple failed logins from Moscow
- **Risk Score:** 98/100
- **Status:** ACCOUNT LOCKED

### Legitimate Transaction (APPROVED)
- **Transaction ID:** `TXN-LEGIT-001`
- **Account:** CUR-001-1234
- **Amount:** £899
- **Merchant:** John Lewis, London
- **Risk Score:** 15/100
- **Status:** APPROVED

---

## 💰 Loan Applications

### Personal Loan - Emma Thompson (APPROVED)
- **Application ID:** `LOAN-APP-001`
- **Customer:** CUST-001
- **Amount:** £20,000
- **Purpose:** Home Improvements
- **Status:** Approved
- **Credit Score:** 742
- **DTI Ratio:** 1.0%

### Business Loan - James Patel (PENDING REVIEW)
- **Application ID:** `LOAN-APP-002`
- **Customer:** CUST-002
- **Amount:** £500,000
- **Purpose:** Equipment Purchase
- **Status:** Pending Manual Review
- **Credit Score:** 785

### Car Finance - Sophie Williams (CONDITIONAL)
- **Application ID:** `LOAN-APP-003`
- **Customer:** CUST-003
- **Amount:** £22,000
- **Purpose:** Vehicle Purchase (VW Golf)
- **Status:** Conditional Approval
- **Credit Score:** 680

---

## 📱 Device IDs for Fraud Testing

### Trusted Devices (Emma Thompson)
- **iPhone:** `DEV-EMMA-IPHONE`
- **MacBook:** `DEV-EMMA-MACBOOK`

### Suspicious Device
- **Unknown PC:** `DEV-UNKNOWN-001`
- **Location:** Lagos, Nigeria
- **Risk Score:** 95/100

---

## 💡 Quick Demo Commands

### Authentication (Required First Step)
```
User: "What's my account balance?"
System: "To help you, I need to verify your identity. Please provide your Customer ID and 4-digit PIN."
User: "CUST-001 and 1234"
System: "Welcome back, Emma Thompson! Let me check your balance..."
```

### Customer Service (After Authentication - Natural Language)
```
"What's my current account balance?"
"Show me my last 5 transactions"
"Transfer £1,500 to my savings account"
"When is my credit card payment due?"
"Are there any pending deposits?"
"What accounts do I have?"
```

**Note:** After authentication, the agent knows your identity and accounts - no need to provide account IDs!

### Customer Service (With Specific Account IDs - Optional)
```
"What's the balance on account CUR-001-1234?"
"Show transactions for my savings account SAV-001-5678"
"Transfer £1,500 from CUR-001-1234 to SAV-001-5678"
```

### Fraud Detection
```
"Analyze transaction TXN-FRAUD-001"
"Check the fraud scenario FRAUD-INC-002"
"Verify device DEV-UNKNOWN-001"
"What's the risk score for transaction TXN-LEGIT-001?"
```

### Loan Processing (Requires Authentication)
```
User: "I'd like to apply for a £20,000 personal loan"
System: "I can help with that. First, please provide your Customer ID and PIN"
User: "CUST-001 and 1234"
System: "Welcome back, Emma! Let me check your eligibility..."
```

After authentication:
```
"Check my credit score" (returns 742 for authenticated customer)
"What's my debt-to-income ratio?"
"Show me loan application LOAN-APP-001"
```

---

**Note:** All account numbers, sort codes, and personal details are fictional and for demo purposes only.