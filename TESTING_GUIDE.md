# Banking Demo - Testing Guide

## 🎯 Quick Start Testing

The banking demo is now deployed and ready to test in watsonx Orchestrate UI.

---

## 🔑 Important: Auto-Authentication

**All agents now automatically identify you as Emma Thompson (CUST-001)** when you start a conversation. You don't need to provide account numbers or customer IDs.

### What This Means:
- ✅ Just ask: "What's my balance?"
- ✅ Just say: "I'd like to apply for a loan"
- ❌ Don't say: "My account number is CUR-001-1234"

The agents will automatically:
1. Call `get_current_customer` to identify you as Emma Thompson
2. Retrieve your customer ID (CUST-001)
3. Access all your accounts and data

---

## 📋 Test Scenarios

### Scenario 1: Simple Balance Check ✅
**What to say**: "What's my current account balance?"

**Expected Response**:
- Agent identifies you as Emma Thompson
- Returns balance: £4,250.50
- Shows account: Current Account (CUR-001-1234)
- Response time: 2-3 seconds

**Tools Used**:
- `core-banking:get_current_customer`
- `core-banking:check_account_balance`

---

### Scenario 2: Fund Transfer ✅
**What to say**: "Transfer £1,500 to my savings account"

**Expected Response**:
- Agent identifies you automatically
- Lists your accounts (Current and Savings)
- Processes transfer from Current to Savings
- Confirms new balances
- Response time: 3-4 seconds

**Tools Used**:
- `core-banking:get_current_customer`
- `core-banking:get_customer_accounts`
- `core-banking:transfer_funds`

---

### Scenario 3: Transaction History ✅
**What to say**: "Show me my recent transactions"

**Expected Response**:
- Agent identifies you automatically
- Returns 5 most recent transactions
- Shows dates, amounts, merchants
- Response time: 2-3 seconds

**Tools Used**:
- `core-banking:get_current_customer`
- `core-banking:get_recent_transactions`

---

### Scenario 4: Loan Application ✅ (FIXED)
**What to say**: "I'd like to apply for a £20,000 personal loan"

**Expected Response**:
- Agent identifies you as Emma Thompson automatically
- Checks your credit score (742 - Good)
- Calculates eligibility (income £65,000, DTI ratio)
- Determines you're eligible for up to £32,500
- Generates 3 loan offers with different terms
- Response time: 4-5 seconds

**Tools Used**:
- `core-banking:get_current_customer`
- `loan-processing:calculate_loan_eligibility`
- `loan-processing:check_credit_score`
- `loan-processing:generate_loan_offers`

**Previous Issue**: Agent was asking for account number  
**Fix Applied**: Added `get_current_customer` tool to loan processing agent

---

### Scenario 5: Multi-Step Request ✅
**What to say**: "Transfer £1,500 to savings, check pending deposits, and tell me when my credit card payment is due"

**Expected Response**:
- Agent identifies you automatically
- Processes transfer
- Checks pending deposits (should show 1 pending)
- Gets credit card payment due date (15th of next month)
- Synthesizes all information in one response
- Response time: 5-6 seconds

**Tools Used**:
- `core-banking:get_current_customer`
- `core-banking:transfer_funds`
- `core-banking:check_pending_deposits`
- `core-banking:get_payment_due_date`

---

### Scenario 6: Fraud Detection (Simulated) 🔍
**What to say**: "Show me fraud scenario 1" or "Analyze a £3,500 transfer to Nigeria"

**Expected Response**:
- Agent identifies you automatically
- Analyzes transaction risk
- Returns high risk score (85-95)
- Explains fraud indicators (large amount, high-risk country, unusual time)
- Recommends blocking
- Response time: 2-3 seconds

**Tools Used**:
- `core-banking:get_current_customer`
- `fraud-detection:analyze_transaction_risk`
- `fraud-detection:get_fraud_scenario`

---

## 🤖 Agent Routing

The **Banking Orchestrator Agent** intelligently routes requests to specialist agents:

### Customer Service Agent
- Balance checks
- Transfers
- Transaction history
- General account inquiries

### Loan Processing Agent
- Loan applications
- Eligibility checks
- Loan offers
- Credit score inquiries

### Fraud Detection Agent
- Transaction risk analysis
- Fraud alerts
- Suspicious activity
- Device verification

### Compliance & Risk Agent
- Regulatory questions
- Compliance checks
- Audit requirements
- Risk assessments

---

## 📊 Emma Thompson's Profile

When you test, you're automatically identified as:

**Name**: Emma Thompson  
**Customer ID**: CUST-001  
**Location**: London, Kensington  
**Occupation**: Senior Software Engineer  
**Income**: £65,000/year  
**Credit Score**: 742 (Good)

**Accounts**:
1. **Current Account** (CUR-001-1234)
   - Balance: £4,250.50
   - Sort Code: 20-00-00
   - IBAN: GB29NWBK20000012345678

2. **Savings Account** (SAV-001-5678)
   - Balance: £15,750.00
   - Interest Rate: 2.5%

3. **Credit Card** (CC-001-9012)
   - Balance: £850.00
   - Credit Limit: £5,000
   - Payment Due: 15th of each month

---

## ✅ What to Test

### Basic Functionality
- [ ] Balance inquiry works
- [ ] Transfer processes correctly
- [ ] Transaction history displays
- [ ] Loan application flows smoothly
- [ ] Multi-step requests work

### Agent Routing
- [ ] Orchestrator routes to correct specialist
- [ ] Customer service handles account queries
- [ ] Loan agent handles loan requests
- [ ] Fraud agent handles risk analysis

### Auto-Authentication
- [ ] No need to provide account numbers
- [ ] Agent identifies Emma Thompson automatically
- [ ] All tools work with auto-identified customer

### Response Quality
- [ ] Responses are clear and professional
- [ ] Numbers are formatted correctly (£ symbol)
- [ ] Dates are in UK format
- [ ] Information is accurate

---

## 🐛 Known Issues & Fixes

### Issue 1: Loan Agent Asking for Account Number ✅ FIXED
**Problem**: Loan processing agent was asking users to provide account numbers  
**Fix**: Added `core-banking:get_current_customer` tool to loan agent  
**Status**: Deployed and ready to test

### Issue 2: Data Files Not Found ✅ FIXED
**Problem**: MCP servers couldn't find data files when deployed  
**Fix**: Copied data to `toolkits/data/` and added path fallback logic  
**Status**: All tests passing

---

## 🔄 If Something Doesn't Work

### 1. Check Agent is Using get_current_customer
Look for this in the agent's reasoning:
```
Using tool: core-banking:get_current_customer
Result: Emma Thompson (CUST-001)
```

### 2. Verify Tools are Imported
```bash
cd banking-demo
source ../.venv/bin/activate
orchestrate tools list | grep -E "(core-banking|fraud-detection|loan-processing)"
```

### 3. Reimport Agents
```bash
cd banking-demo
./import-all.sh
```

### 4. Check Logs
Look for errors in the agent's reasoning panel (click "Show Reasoning")

---

## 📞 Next Steps After Testing

1. **Document Results**: Note which scenarios work well and which need improvement
2. **Test Edge Cases**: Try unusual requests or error scenarios
3. **Performance**: Measure response times for each scenario
4. **User Experience**: Evaluate if responses are clear and helpful
5. **Multi-Agent**: Test complex scenarios requiring multiple agents

---

## 🎓 Tips for Demo Presentation

1. **Start Simple**: Begin with balance check to show basic functionality
2. **Show Complexity**: Move to multi-step requests to demonstrate intelligence
3. **Highlight Speed**: Point out 2-3 second response times
4. **Emphasize Auto-Auth**: Explain how users don't need to remember account numbers
5. **Demonstrate Routing**: Show how orchestrator routes to specialists
6. **Show Fraud**: Use fraud scenario to demonstrate real-time protection

---

**Last Updated**: 2026-04-26  
**Status**: Ready for Testing  
**Next Action**: Test all scenarios in watsonx Orchestrate UI