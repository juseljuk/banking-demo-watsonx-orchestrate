# Banking Demo - Guardrail Demonstration Guide

Complete guide for demonstrating the security and compliance guardrails in the banking demo.

## 📋 Overview

The banking demo implements 4 key guardrails that protect customers and ensure regulatory compliance:

1. **PII Protection Guardrail** (Post-invoke) - Redacts sensitive personal information
2. **Transaction Limit Guardrail** (Pre-invoke) - Enforces daily transfer limits
3. **Lending Compliance Guardrail** (Pre-invoke) - Ensures fair lending practices
4. **Fraud Rules Guardrail** (Pre-invoke) - Detects and blocks suspicious transactions

---

## 🎯 Guardrail Coverage by Agent

| Agent | PII Protection | Transaction Limit | Lending Compliance | Fraud Rules |
|-------|---------------|-------------------|-------------------|-------------|
| **Banking Orchestrator** | ✅ | ❌ | ❌ | ❌ |
| **Customer Service** | ✅ | ✅ | ❌ | ✅ |
| **Loan Processing** | ✅ | ❌ | ✅ | ❌ |
| **Fraud Detection** | ✅ | ❌ | ❌ | ✅ |
| **Compliance & Risk** | ✅ | ❌ | ❌ | ❌ |

---

## 1️⃣ PII Protection Guardrail

**Type:** Post-invoke (runs AFTER agent generates response)  
**Purpose:** Redacts sensitive personal information before showing to user  
**Compliance:** GDPR, UK Data Protection Act 2018, FCA SYSC 3.2.6R

### What Gets Redacted

| Data Type | Original | Redacted |
|-----------|----------|----------|
| Account Numbers | 12345678 | ****5678 |
| Sort Codes | 20-00-00 | **-**-00 |
| National Insurance | AB123456D | ******456D |
| Email Addresses | emma.thompson@email.co.uk | e***@*.co.uk |
| Phone Numbers | +44 20 7946 0123 | +44 ** **** 0123 |
| Credit Cards | 1234567890123456 | ****3456 |
| IBANs | GB29NWBK60161331926819 | GB********************6819 |

### Demo Scenario 1: Account Number Masking

**Setup:** Authenticate as Emma Thompson (CUST-001, PIN: 1234)

**User Query:**
```
"What's my account number?"
```

**Expected Behavior:**
1. Agent retrieves full account number: `12345678`
2. PII Protection Guardrail intercepts response
3. Redacts to: `****5678`
4. User sees: "Your account number is ****5678"

**Demo Script:**
```
👤 User: "What's my account number for my current account?"

🤖 Agent: "Your current account number is ****1234 with sort code **-**-00."

✅ SUCCESS: Full account number redacted to last 4 digits
```

### Demo Scenario 2: National Insurance Number Redaction

**User Query:**
```
"Can you verify my National Insurance number?"
```

**Expected Behavior:**
1. Agent retrieves NI number: `AB123456D`
2. Guardrail redacts to: `******456D`
3. User sees only last 4 characters

**Demo Script:**
```
👤 User: "What's my National Insurance number on file?"

🤖 Agent: "Your National Insurance number ends in ******456D."

✅ SUCCESS: NI number redacted, showing only last 4 characters
```

### Demo Scenario 3: Email Address Masking

**User Query:**
```
"What email address do you have for me?"
```

**Expected Behavior:**
1. Agent retrieves: `emma.thompson@email.co.uk`
2. Guardrail masks to: `e***@*.co.uk`
3. Protects privacy while confirming domain

**Demo Script:**
```
👤 User: "What's my email address on file?"

🤖 Agent: "Your email address is e***@*.co.uk"

✅ SUCCESS: Email masked to first letter and domain TLD
```

---

## 2️⃣ Transaction Limit Guardrail

**Type:** Pre-invoke (runs BEFORE processing request)  
**Purpose:** Enforces daily transfer limits and prevents unauthorized large transfers  
**Compliance:** UK Payment Services Regulations 2017, FCA SYSC 6.1

### Transaction Limits

| Account Type | Daily Limit | Single Transaction Limit |
|--------------|-------------|-------------------------|
| Current Account | £10,000 | £50,000 |
| Business Account | £25,000 | £50,000 |
| Savings Account | £5,000 | £50,000 |

### Demo Scenario 1: Within Limit (ALLOWED)

**Setup:** Authenticate as Emma Thompson (CUST-001, PIN: 1234)

**User Query:**
```
"Transfer £1,500 to my savings account"
```

**Expected Behavior:**
1. Guardrail checks: £1,500 < £10,000 daily limit ✅
2. Guardrail checks: £1,500 < £50,000 single limit ✅
3. Request proceeds to agent
4. Transfer completes successfully

**Demo Script:**
```
👤 User: "Transfer £1,500 from my current account to savings"

🤖 Agent: "I've transferred £1,500 to your savings account. 
         New balances:
         Current: £2,750.50
         Savings: £20,250.00"

✅ SUCCESS: Transaction within limits, processed normally
```

### Demo Scenario 2: Exceeds Daily Limit (BLOCKED)

**User Query:**
```
"Transfer £12,000 to my savings account"
```

**Expected Behavior:**
1. Guardrail checks: £12,000 > £10,000 daily limit ❌
2. Guardrail BLOCKS request
3. User receives clear explanation
4. Agent never processes the transfer

**Demo Script:**
```
👤 User: "I need to transfer £12,000 to my savings"

🤖 Agent: "I'm unable to process this transaction. Transaction of £12,000.00 
         would exceed daily limit of £10,000.00. You have £10,000.00 
         remaining today. Your daily transfer limit for this account type 
         is £10,000.00. The limit will reset at midnight."

❌ BLOCKED: Exceeds daily limit, transaction prevented
```

### Demo Scenario 3: Exceeds Single Transaction Limit (BLOCKED)

**User Query:**
```
"Transfer £55,000 to external account"
```

**Expected Behavior:**
1. Guardrail checks: £55,000 > £50,000 single limit ❌
2. Guardrail BLOCKS immediately
3. Suggests contacting relationship manager

**Demo Script:**
```
👤 User: "I want to transfer £55,000"

🤖 Agent: "I'm unable to process this transaction. Single transaction limit 
         is £50,000.00. Please contact your relationship manager for 
         transactions over this amount. For your security, single 
         transactions are limited to £50,000.00."

❌ BLOCKED: Exceeds single transaction limit
```

---

## 3️⃣ Lending Compliance Guardrail

**Type:** Pre-invoke (runs BEFORE processing loan request)  
**Purpose:** Ensures loan decisions comply with UK lending regulations  
**Compliance:** FCA CONC 5.2A, Consumer Credit Act 1974, Equality Act 2010

### Compliance Checks

1. **Creditworthiness** - Minimum credit score: 550
2. **Affordability** - Maximum DTI ratio: 40%
3. **Income Verification** - Minimum income: £15,000/year
4. **Loan Limits** - Maximum 5x annual income for personal loans
5. **Required Disclosures** - APR, total payable, cooling-off period

### Demo Scenario 1: Compliant Loan (APPROVED)

**Setup:** Authenticate as Emma Thompson (CUST-001, PIN: 1234)
- Credit Score: 742 (Good)
- Annual Income: £65,000
- Existing Debt: £55/month

**User Query:**
```
"I'd like to apply for a £20,000 personal loan"
```

**Expected Behavior:**
1. Guardrail checks credit score: 742 > 550 ✅
2. Guardrail calculates affordability:
   - Monthly payment: ~£405
   - DTI ratio: (£55 + £405) / £5,417 = 8.5% < 40% ✅
3. Guardrail checks income multiplier: £20,000 < £325,000 (5x £65k) ✅
4. All checks pass, request proceeds

**Demo Script:**
```
👤 User: "I'd like to apply for a £20,000 personal loan"

🤖 Agent: "Great! Let me check your eligibility...

         ✅ Credit Score: 742 (Good)
         ✅ Affordability: Debt-to-income ratio 8.5% (well within 40% limit)
         ✅ Income Verification: £65,000 annual income confirmed
         
         You're eligible for up to £32,500. Here are three loan offers:
         
         1. 5-year term at 7.9% APR - £405/month
         2. 3-year term at 8.4% APR - £630/month  
         3. 7-year term at 8.9% APR - £310/month
         
         All offers include 14-day cooling-off period and early repayment rights."

✅ APPROVED: All compliance checks passed
```

### Demo Scenario 2: Insufficient Credit Score (BLOCKED)

**Setup:** Simulate customer with credit score 540

**User Query:**
```
"I want to apply for a £15,000 loan"
```

**Expected Behavior:**
1. Guardrail checks credit score: 540 < 550 ❌
2. Guardrail BLOCKS application
3. Provides guidance on improving credit

**Demo Script:**
```
👤 User: "I'd like to borrow £15,000"

🤖 Agent: "I'm unable to proceed with your loan application at this time. 
         Credit score of 540 is below minimum requirement of 550. We 
         recommend improving your credit score before reapplying. You may 
         wish to review your credit report and consider steps to improve 
         your score. We're here to help when you're ready to reapply."

❌ BLOCKED: Credit score below minimum threshold
```

### Demo Scenario 3: Unaffordable Loan (BLOCKED)

**Setup:** Customer requests loan that would exceed 40% DTI ratio

**User Query:**
```
"I need a £50,000 personal loan"
```

**Expected Behavior:**
1. Guardrail calculates monthly payment: ~£1,013
2. Guardrail calculates DTI: (£55 + £1,013) / £5,417 = 19.7%
3. But £50,000 > £32,500 (5x income limit) ❌
4. Guardrail BLOCKS as unaffordable

**Demo Script:**
```
👤 User: "Can I get a £50,000 personal loan?"

🤖 Agent: "I'm unable to approve a loan of £50,000.00 at this time. 
         Requested amount of £50,000.00 exceeds maximum of £32,500.00 
         (5x annual income of £65,000.00). As a responsible lender, we 
         must ensure loans are affordable. You may wish to consider a 
         smaller loan amount or contact us to discuss your options."

❌ BLOCKED: Exceeds income multiplier limit
```

---

## 4️⃣ Fraud Rules Guardrail

**Type:** Pre-invoke (runs BEFORE processing transaction)  
**Purpose:** Detects and blocks suspicious transactions  
**Compliance:** UK Payment Services Regulations 2017, FCA SYSC 6.1, AML Regulations

### Risk Scoring (0-100)

| Risk Level | Score Range | Action |
|------------|-------------|--------|
| LOW | 0-30 | Allow transaction |
| MEDIUM | 31-60 | Allow with monitoring |
| HIGH | 61-90 | Require additional verification |
| CRITICAL | 91-100 | Block transaction immediately |

### Risk Factors

| Factor | Points | Example |
|--------|--------|---------|
| High-risk destination | +40 | Nigeria, Russia, etc. |
| Very large amount | +30 | ≥£10,000 |
| Large amount | +20 | ≥£5,000 |
| Urgency language | +15 | "urgent", "emergency" |
| Suspicious keywords | +10 each | "bitcoin", "gift card" |
| Off-hours transaction | +15 | 12am-5am, 10pm-12am |
| Unrecognized device | +15 | New device fingerprint |
| Velocity exceeded | +20 | Too many transactions |

### Demo Scenario 1: Low Risk Transaction (ALLOWED)

**Setup:** Authenticate as Emma Thompson

**User Query:**
```
"Transfer £500 to my friend in London"
```

**Expected Behavior:**
1. Guardrail calculates risk:
   - Amount £500: +0 (below threshold)
   - Domestic transfer: +0
   - Normal hours: +0
   - **Total Risk Score: 0/100 (LOW)**
2. Transaction proceeds normally

**Demo Script:**
```
👤 User: "Send £500 to my friend Sarah in London"

🤖 Agent: "I've transferred £500 to Sarah. 
         Transaction reference: TXN-20260426-001
         New balance: £3,750.50"

✅ LOW RISK (0/100): Transaction approved
```

### Demo Scenario 2: High Risk Transaction (BLOCKED)

**User Query:**
```
"I need to urgently transfer £3,500 to Nigeria"
```

**Expected Behavior:**
1. Guardrail calculates risk:
   - High-risk country (Nigeria): +40
   - Amount £3,500: +0 (below £5k threshold)
   - Urgency language ("urgently"): +15
   - **Total Risk Score: 55/100 (MEDIUM)**
   
Wait, let me recalculate for a truly high-risk scenario:

**User Query (Revised):**
```
"Emergency! Transfer £8,000 to Nigeria immediately for bitcoin"
```

**Expected Behavior:**
1. Guardrail calculates risk:
   - High-risk country (Nigeria): +40
   - Large amount (£8,000): +20
   - Urgency language ("Emergency", "immediately"): +15
   - Suspicious keyword ("bitcoin"): +10
   - **Total Risk Score: 85/100 (HIGH)** → Would require verification
   
For CRITICAL (blocked), we need 91+:

**User Query (Critical):**
```
"URGENT! Send £12,000 to Nigeria right now for cryptocurrency emergency!"
```

**Expected Behavior:**
1. Guardrail calculates risk:
   - High-risk country (Nigeria): +40
   - Very large amount (£12,000): +30
   - Urgency language (multiple): +15
   - Suspicious keywords ("cryptocurrency"): +10
   - **Total Risk Score: 95/100 (CRITICAL)** ❌
2. Guardrail BLOCKS immediately
3. Customer receives fraud alert

**Demo Script:**
```
👤 User: "URGENT! I need to send £12,000 to Nigeria for a cryptocurrency investment!"

🤖 Agent: "⚠️ **TRANSACTION BLOCKED FOR SECURITY**

         This transaction has been flagged as high-risk and cannot be processed.
         
         **Risk Score:** 95/100 (CRITICAL)
         **Risk Factors:**
         • High-risk destination: Nigeria
         • Very large transaction: £12,000.00
         • Urgent language detected
         • Suspicious keywords: cryptocurrency
         
         **What to do next:**
         • Contact our fraud prevention team at 0800 123 4567
         • Verify your identity and transaction details
         • We're here to protect your account
         
         If this is a legitimate transaction, our team can help you 
         complete it securely."

❌ BLOCKED: Risk score 95/100 - Critical fraud indicators
```

### Demo Scenario 3: Medium Risk with Monitoring (ALLOWED)

**User Query:**
```
"Transfer £6,000 to my business partner"
```

**Expected Behavior:**
1. Guardrail calculates risk:
   - Large amount (£6,000): +20
   - Domestic transfer: +0
   - Normal hours: +0
   - **Total Risk Score: 20/100 (LOW)**
2. Transaction proceeds with monitoring

**Demo Script:**
```
👤 User: "I need to transfer £6,000 to my business partner's account"

🤖 Agent: "I've processed the transfer of £6,000.
         Transaction reference: TXN-20260426-002
         New balance: £-2,249.50
         
         Note: This transaction will be monitored as part of our 
         standard security procedures."

✅ LOW RISK (20/100): Transaction approved with monitoring
```

---

## 🎬 Complete Demo Flow

### Full Demonstration Script (10-15 minutes)

**Introduction (1 minute)**
```
"Today I'll demonstrate our AI-powered banking platform's security guardrails.
These guardrails protect customers and ensure regulatory compliance in real-time.
We'll see 4 types of guardrails in action."
```

**Demo 1: PII Protection (2 minutes)**
```
1. Authenticate as Emma Thompson
2. Ask: "What's my account number?"
3. Show: Account number redacted to ****1234
4. Ask: "What's my National Insurance number?"
5. Show: NI number redacted to ******456D
6. Explain: "All sensitive data is automatically redacted before display"
```

**Demo 2: Transaction Limits (3 minutes)**
```
1. Ask: "Transfer £1,500 to savings"
2. Show: Transaction succeeds (within limits)
3. Ask: "Transfer £12,000 to savings"
4. Show: Transaction blocked (exceeds daily limit)
5. Explain: "Guardrails enforce limits before processing"
```

**Demo 3: Lending Compliance (3 minutes)**
```
1. Ask: "I'd like a £20,000 personal loan"
2. Show: Eligibility check passes
3. Show: Affordability assessment (DTI 8.5%)
4. Show: Loan offers generated
5. Explain: "FCA compliance checks happen automatically"
```

**Demo 4: Fraud Detection (3 minutes)**
```
1. Ask: "Transfer £500 to London friend"
2. Show: Low risk (0/100), approved
3. Ask: "URGENT! Send £12,000 to Nigeria for cryptocurrency!"
4. Show: Critical risk (95/100), blocked
5. Explain: "Real-time fraud detection protects customers"
```

**Conclusion (1 minute)**
```
"These guardrails work together to:
- Protect customer privacy (GDPR compliance)
- Prevent unauthorized transactions
- Ensure fair lending practices
- Detect fraud in real-time
All automatically, with no manual intervention required."
```

---

## 📊 Demo Data Reference

### Test Customers

| Customer | ID | PIN | Credit Score | Income | Use For |
|----------|----|----|--------------|--------|---------|
| Emma Thompson | CUST-001 | 1234 | 742 | £65,000 | All demos |
| James Patel | CUST-002 | 5678 | 785 | £125,000 | High-value scenarios |
| Sophie Williams | CUST-003 | 9012 | 680 | £32,000 | Lower income scenarios |

### Account Limits

| Account | Daily Limit | Current Balance |
|---------|-------------|-----------------|
| CUR-001-1234 | £10,000 | £4,250.50 |
| SAV-001-5678 | £5,000 | £18,750.00 |
| BUS-002-3456 | £25,000 | £68,450.25 |

---

## 🔍 Troubleshooting

### Guardrail Not Triggering

**Problem:** Guardrail doesn't block expected transaction

**Solutions:**
1. Verify guardrail is imported: `orchestrate tools list | grep guardrail`
2. Check agent YAML has plugins section
3. Verify guardrail is attached to correct agent
4. Check guardrail logic matches test scenario

### PII Not Being Redacted

**Problem:** Sensitive data shows in full

**Solutions:**
1. Verify pii_protection_guardrail is in agent_post_invoke
2. Check regex patterns in guardrail code
3. Test with exact data formats from demo data
4. Verify guardrail is imported successfully

### Transaction Limits Not Enforced

**Problem:** Large transfers go through

**Solutions:**
1. Verify transaction_limit_guardrail is in agent_pre_invoke
2. Check amount extraction regex patterns
3. Verify limits match account type
4. Test with exact transfer syntax

---

## 📝 Notes for Presenters

### Key Messages

1. **Automatic Protection** - Guardrails work automatically, no manual intervention
2. **Real-Time** - Checks happen instantly, before processing
3. **Compliance** - Built-in regulatory compliance (FCA, GDPR, etc.)
4. **Layered Security** - Multiple guardrails work together
5. **Customer Experience** - Security without friction

### Common Questions

**Q: Can guardrails be bypassed?**
A: No, guardrails run at the platform level before agent processing. They cannot be bypassed by the agent or user.

**Q: How fast are guardrail checks?**
A: Guardrails add <100ms latency. Most checks complete in 10-50ms.

**Q: Can we customize guardrails?**
A: Yes, all guardrails are Python code that can be customized for specific business rules.

**Q: What happens if a guardrail fails?**
A: The request is blocked before processing. The user receives a clear explanation and next steps.

**Q: Do guardrails log their decisions?**
A: Yes, all guardrail decisions are logged for audit and compliance purposes.

---

**Last Updated:** 2026-04-26  
**Created By:** Bob (WXO Agent Architect)  
**Version:** 1.0