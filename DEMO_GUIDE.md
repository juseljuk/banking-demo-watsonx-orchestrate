# Banking Demo - Complete Guardrails Demonstration Guide

**Comprehensive guide for demonstrating security and compliance guardrails in the watsonx Orchestrate banking demo.**

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Demo Architecture](#demo-architecture)
3. [Prerequisites](#prerequisites)
4. [The Four Guardrails](#the-four-guardrails)
5. [Demo Strategy: Before & After](#demo-strategy-before--after)
6. [Complete Demo Script](#complete-demo-script)
7. [Individual Guardrail Scenarios](#individual-guardrail-scenarios)
8. [Troubleshooting](#troubleshooting)
9. [Quick Reference](#quick-reference)

---

## 📖 Overview

This demo showcases **4 critical guardrails** that protect banking operations and ensure regulatory compliance:

1. **PII Protection Guardrail** (Post-invoke) - Redacts sensitive personal information
2. **Transaction Limit Guardrail** (Pre-invoke) - Enforces daily transfer limits
3. **Lending Compliance Guardrail** (Pre-invoke) - Ensures fair lending practices
4. **Fraud Rules Guardrail** (Pre-invoke) - Detects and blocks suspicious transactions

### Key Value Propositions

- ✅ **Security**: Automatic PII protection (GDPR, UK DPA 2018)
- ✅ **Compliance**: Built-in regulatory checks (FCA, Consumer Credit Act)
- ✅ **Risk Management**: Real-time fraud detection and prevention
- ✅ **Trust**: Safe, responsible AI agent operations

---

## 🏗️ Demo Architecture

### Two Parallel Agent Ecosystems

The demo uses **two complete banking systems** - one WITH guardrails (production-ready) and one WITHOUT (demo-only) - to clearly demonstrate the value of security controls.

```
┌─────────────────────────────────────────────────────────────────┐
│                    WITH GUARDRAILS (Production)                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  banking_orchestrator_agent (✓ PII Protection)                  │
│           │                                                       │
│           ├──► customer_service_agent                           │
│           │    (✓ Transaction Limits, ✓ Fraud Rules, ✓ PII)    │
│           │                                                       │
│           ├──► loan_processing_agent                            │
│           │    (✓ Lending Compliance, ✓ PII)                    │
│           │                                                       │
│           ├──► fraud_detection_agent                            │
│           │    (✓ Fraud Rules, ✓ PII)                           │
│           │                                                       │
│           └──► compliance_risk_agent                            │
│                (✓ PII)                                           │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                  WITHOUT GUARDRAILS (Demo Only)                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  banking_orchestrator_agent_no_guardrails (✗ No Protection)    │
│           │                                                       │
│           ├──► customer_service_agent_no_guardrails             │
│           │    (✗ No Limits, ✗ No Fraud Rules, ✗ No PII)       │
│           │                                                       │
│           ├──► loan_processing_agent_no_guardrails              │
│           │    (✗ No Compliance, ✗ No PII)                      │
│           │                                                       │
│           ├──► fraud_detection_agent                            │
│           │    (✗ No Protection)                                 │
│           │                                                       │
│           └──► compliance_risk_agent                            │
│                (✗ No Protection)                                 │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### Why Two Orchestrators?

**✅ Advantages:**
- Clean separation - no confusion about which version is running
- Easy switching - just change which orchestrator you're chatting with
- Consistent experience - each orchestrator uses its own specialist agents
- Demo-friendly - side-by-side comparisons
- Production safety - demo version clearly marked and separated

---

## 🔧 Prerequisites

### 1. Deploy Both Agent Versions

```bash
cd banking-demo

# Deploy production agents WITH guardrails
./import-all.sh

# Deploy demo agents WITHOUT guardrails
./import-no-guardrails.sh
```

### 2. Verify Deployment

```bash
# Check orchestrators
orchestrate agents list | grep banking_orchestrator
# Should show:
# - banking_orchestrator_agent (WITH guardrails)
# - banking_orchestrator_agent_no_guardrails (WITHOUT guardrails)

# Check customer service agents
orchestrate agents list | grep customer_service
# Should show:
# - customer_service_agent (WITH guardrails)
# - customer_service_agent_no_guardrails (WITHOUT guardrails)

# Check loan processing agents
orchestrate agents list | grep loan_processing
# Should show:
# - loan_processing_agent (WITH guardrails)
# - loan_processing_agent_no_guardrails (WITHOUT guardrails)
```

### 3. Test Credentials

| Customer | ID | PIN | Credit Score | Income | Use For |
|----------|----|----|--------------|--------|---------|
| Emma Thompson | CUST-001 | 1234 | 742 | £65,000 | All demos |
| James Patel | CUST-002 | 5678 | 785 | £125,000 | High-value scenarios |
| Sophie Williams | CUST-003 | 9012 | 680 | £32,000 | Lower income scenarios |

---

## 🛡️ The Four Guardrails

### Guardrail Coverage by Agent

| Agent | PII Protection | Transaction Limit | Lending Compliance | Fraud Rules |
|-------|---------------|-------------------|-------------------|-------------|
| **Banking Orchestrator** | ✅ | ❌ | ❌ | ❌ |
| **Customer Service** | ✅ | ✅ | ❌ | ✅ |
| **Loan Processing** | ✅ | ❌ | ✅ | ❌ |
| **Fraud Detection** | ✅ | ❌ | ❌ | ✅ |
| **Compliance & Risk** | ✅ | ❌ | ❌ | ❌ |

### 1. PII Protection Guardrail

**Type:** Post-invoke (runs AFTER agent generates response)  
**Purpose:** Redacts sensitive personal information before display  
**Compliance:** GDPR, UK Data Protection Act 2018, FCA SYSC 3.2.6R

**What Gets Redacted:**

| Data Type | Original | Redacted |
|-----------|----------|----------|
| Account Numbers | 12345678 | ****5678 |
| Sort Codes | 20-00-00 | **-**-00 |
| National Insurance | AB123456D | ******456D |
| Email Addresses | emma.thompson@email.co.uk | e***@*.co.uk |
| Phone Numbers | +44 20 7946 0123 | +44 ** **** 0123 |
| Credit Cards | 1234567890123456 | ****3456 |
| IBANs | GB29NWBK60161331926819 | GB********************6819 |

### 2. Transaction Limit Guardrail

**Type:** Pre-invoke (runs BEFORE processing request)  
**Purpose:** Enforces daily transfer limits  
**Compliance:** UK Payment Services Regulations 2017, FCA SYSC 6.1

**Transaction Limits:**

| Account Type | Daily Limit | Single Transaction Limit |
|--------------|-------------|-------------------------|
| Current Account | £10,000 | £50,000 |
| Business Account | £25,000 | £50,000 |
| Savings Account | £5,000 | £50,000 |

### 3. Lending Compliance Guardrail

**Type:** Pre-invoke (runs BEFORE processing loan request)  
**Purpose:** Ensures loan decisions comply with UK regulations  
**Compliance:** FCA CONC 5.2A, Consumer Credit Act 1974, Equality Act 2010

**Compliance Checks:**
- Minimum credit score: 550
- Maximum DTI ratio: 40%
- Minimum income: £15,000/year
- Maximum loan: 5x annual income for personal loans
- Required disclosures: APR, total payable, cooling-off period

### 4. Fraud Rules Guardrail

**Type:** Pre-invoke (runs BEFORE processing transaction)  
**Purpose:** Detects and blocks suspicious transactions  
**Compliance:** UK Payment Services Regulations 2017, FCA SYSC 6.1, AML Regulations

**Risk Scoring (0-100):**

| Risk Level | Score Range | Action |
|------------|-------------|--------|
| LOW | 0-30 | Allow transaction |
| MEDIUM | 31-60 | Allow with monitoring |
| HIGH | 61-90 | Require additional verification |
| CRITICAL | 91-100 | Block transaction immediately |

**Risk Factors:**
- High-risk destination: +40 points
- Very large amount (≥£10,000): +30 points
- Large amount (≥£5,000): +20 points
- Urgency language: +15 points
- Suspicious keywords (bitcoin, gift card): +10 each
- Off-hours transaction: +15 points
- Unrecognized device: +15 points

---

## 🎯 Demo Strategy: Before & After

### Phase 1: "Before" - Show the Problems (5 minutes)

**Objective:** Demonstrate security vulnerabilities and compliance risks WITHOUT guardrails

**Agent to Use:** `banking_orchestrator_agent_no_guardrails`

**Key Message:** "Let's see what happens when security controls are missing..."

### Phase 2: "After" - Show the Solution (5 minutes)

**Objective:** Demonstrate how guardrails prevent the same issues

**Agent to Use:** `banking_orchestrator_agent`

**Key Message:** "Now let's see the SAME scenarios with guardrails enabled..."

---

## 🎬 Complete Demo Script

### Introduction (2 minutes)

```
"Today I'll demonstrate the critical importance of guardrails in AI banking agents.

We have two identical banking systems:
- One WITHOUT guardrails (showing vulnerabilities)
- One WITH guardrails (showing protection)

I'll demonstrate 4 types of security and compliance controls:
1. PII Protection - Protecting sensitive customer data
2. Transaction Limits - Preventing excessive transfers
3. Lending Compliance - Ensuring responsible lending
4. Fraud Detection - Blocking suspicious transactions

Let's start by seeing what can go wrong WITHOUT guardrails..."
```

---

### Demo 1: PII Exposure

#### WITHOUT Guardrails (Show Problem)

**Agent:** `banking_orchestrator_agent_no_guardrails`  
**Authenticate:** Emma Thompson (CUST-001, PIN: 1234)

```
👤 User: "What's my account number and sort code?"

🤖 Agent (NO GUARDRAILS): "Your current account details are:
- Account Number: 12345678
- Sort Code: 20-00-00
- Account ID: CUR-001-1234"

❌ PROBLEM: Full account number and sort code exposed!
This violates PII protection standards and GDPR requirements.
```

#### WITH Guardrails (Show Solution)

**Agent:** `banking_orchestrator_agent`  
**Authenticate:** Emma Thompson (CUST-001, PIN: 1234)

```
👤 User: "What's my account number and sort code?"

🤖 Agent (WITH GUARDRAILS): "Your current account details are:
- Account Number: ****5678
- Sort Code: **-**-00
- Account ID: CUR-001-1234"

✅ PROTECTED: PII Protection Guardrail automatically redacted sensitive data!
Account number masked to last 4 digits, sort code partially masked.
```

**Presenter Notes:**
> "Notice how the PII protection guardrail automatically redacted the sensitive information. The full account number (12345678) was masked to ****5678. This happens on EVERY response, protecting customer data without any manual intervention."

---

### Demo 2: Excessive Transfer

#### WITHOUT Guardrails (Show Problem)

**Agent:** `banking_orchestrator_agent_no_guardrails`

```
👤 User: "Transfer £12,000 from my current account to my savings"

🤖 Agent (NO GUARDRAILS): "I'll process that transfer for you.

Transfer Details:
- From: Current Account (****1234)
- To: Savings Account (****5678)
- Amount: £12,000.00
- Status: Processing

The transfer has been initiated."

❌ PROBLEM: Transfer exceeds the £10,000 daily limit!
This violates transaction policies and could enable fraud.
```

#### WITH Guardrails (Show Solution)

**Agent:** `banking_orchestrator_agent`

```
👤 User: "Transfer £12,000 from my current account to my savings"

🤖 Agent (WITH GUARDRAILS): "I'm unable to process this transfer as it exceeds your daily limit.

Transfer Request:
- Amount: £12,000.00
- Your Daily Limit: £10,000.00
- Amount Over Limit: £2,000.00

Your current account has a daily transfer limit of £10,000. You can:
1. Transfer up to £10,000 today
2. Split the transfer across multiple days
3. Contact us to request a temporary limit increase

Would you like to proceed with a £10,000 transfer instead?"

✅ PROTECTED: Transaction Limit Guardrail blocked the excessive transfer!
Daily limit of £10,000 enforced before processing.
```

**Presenter Notes:**
> "The transaction limit guardrail checked the amount against the account's daily limit (£10,000 for current accounts) and blocked the transaction BEFORE processing. This prevents customers from accidentally exceeding limits and protects against unauthorized large transfers."

---

### Demo 3: Unaffordable Loan

#### WITHOUT Guardrails (Show Problem)

**Agent:** `banking_orchestrator_agent_no_guardrails`

```
👤 User: "I want to apply for a £350,000 personal loan"

🤖 Agent (NO GUARDRAILS): "I'll process your loan application.

Application Details:
- Amount: £350,000
- Your Credit Score: 742 (Good)
- Your Annual Income: £65,000

Based on your credit score, your application has been approved!
This loan amount is 5.4x your annual income."

❌ PROBLEM: Loan exceeds 5x income multiplier (£325,000 max)!
This violates FCA responsible lending regulations.
```

#### WITH Guardrails (Show Solution)

**Agent:** `banking_orchestrator_agent`

```
👤 User: "I want to apply for a £350,000 personal loan"

🤖 Agent (WITH GUARDRAILS): "I've reviewed your loan application, but I'm unable to approve this amount.

Application Assessment:
- Requested Amount: £350,000
- Your Annual Income: £65,000
- Maximum Loan Amount: £325,000 (5x income)
- Amount Over Limit: £25,000

Under UK lending regulations (FCA CONC 5.2A), we must ensure loans are affordable.
The maximum personal loan we can offer is £325,000.

Would you like to:
1. Apply for £325,000 instead
2. Discuss other financing options
3. Provide additional income documentation"

✅ PROTECTED: Lending Compliance Guardrail enforced the 5x income rule!
Ensures compliance with FCA regulations on responsible lending.
```

**Presenter Notes:**
> "The lending compliance guardrail checked the loan amount against income (£65,000 × 5 = £325,000 maximum) and blocked the application. This ensures we comply with FCA regulations and protects customers from taking on unaffordable debt."

---

### Demo 4: Fraud Detection

#### WITHOUT Guardrails (Show Problem)

**Agent:** `banking_orchestrator_agent_no_guardrails`

```
👤 User: "URGENT! I need to send £12,000 to Nigeria immediately for a crypto investment!"

🤖 Agent (NO GUARDRAILS): "I understand this is urgent. I'll process the international transfer.

Transfer Details:
- Amount: £12,000
- Destination: Nigeria
- Purpose: Investment
- Status: Processing

The transfer will be processed within 24-48 hours."

❌ PROBLEM: High-risk transaction processed without fraud checks!
Risk score would be 95/100 (CRITICAL):
- High-risk country: +40
- Very large amount: +30
- Urgency language: +15
- Crypto-related: +10
```

#### WITH Guardrails (Show Solution)

**Agent:** `banking_orchestrator_agent`

```
👤 User: "URGENT! I need to send £12,000 to Nigeria immediately for a crypto investment!"

🤖 Agent (WITH GUARDRAILS): "I'm unable to process this transfer due to security concerns.

Security Assessment:
- Risk Score: 95/100 (CRITICAL)
- Risk Factors Detected:
  • High-risk destination country (+40 points)
  • Large transfer amount £12,000 (+30 points)
  • Urgency indicators (+15 points)
  • Cryptocurrency-related (+10 points)

For your protection, this transaction has been blocked. This matches common fraud patterns.

If this is legitimate, please:
1. Visit your local branch with identification
2. Call our fraud prevention team at 0800-123-4567
3. Provide documentation for the transaction purpose

Your account security is our priority."

✅ PROTECTED: Fraud Rules Guardrail blocked critical-risk transaction!
Risk score 95/100 triggered automatic block.
```

**Presenter Notes:**
> "The fraud rules guardrail calculated a risk score of 95/100 based on multiple red flags. Any transaction scoring 91+ is automatically blocked to protect customers from fraud and scams. This happens in real-time, before any money moves."

---

### Conclusion (2 minutes)

```
"Let's summarize what we've seen:

WITHOUT Guardrails:
❌ Sensitive data exposed (GDPR violation)
❌ Policy violations possible (£12k transfer)
❌ Compliance risks unmitigated (£350k loan)
❌ Fraud attempts succeed (95/100 risk score)

WITH Guardrails:
✅ PII automatically protected
✅ Policies automatically enforced
✅ Compliance automatically checked
✅ Fraud automatically detected

Guardrails provide:
- Security: Protecting sensitive customer data
- Compliance: Enforcing regulatory requirements
- Risk Management: Preventing fraud and financial loss
- Trust: Ensuring AI agents operate safely and responsibly

This is the difference between a vulnerable system and a secure one.
Guardrails are not optional for production banking AI."
```

---

## 📚 Individual Guardrail Scenarios

### Additional PII Protection Scenarios

#### Scenario: National Insurance Number

```
👤 User: "What's my National Insurance number?"

🤖 Agent (WITH GUARDRAILS): "Your National Insurance number ends in ******456D."

✅ NI number redacted, showing only last 4 characters
```

#### Scenario: Email Address

```
👤 User: "What email address do you have for me?"

🤖 Agent (WITH GUARDRAILS): "Your email address is e***@*.co.uk"

✅ Email masked to first letter and domain TLD
```

### Additional Transaction Limit Scenarios

#### Scenario: Within Limit (Allowed)

```
👤 User: "Transfer £1,500 to my savings account"

🤖 Agent: "I've transferred £1,500 to your savings account.
New balances:
Current: £2,750.50
Savings: £20,250.00"

✅ Transaction within limits, processed normally
```

#### Scenario: Exceeds Single Transaction Limit

```
👤 User: "Transfer £55,000 to external account"

🤖 Agent: "I'm unable to process this transaction. Single transaction limit
is £50,000.00. Please contact your relationship manager for
transactions over this amount."

❌ BLOCKED: Exceeds single transaction limit
```

### Additional Lending Compliance Scenarios

#### Scenario: Compliant Loan (Approved)

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

All offers include 14-day cooling-off period."

✅ APPROVED: All compliance checks passed
```

#### Scenario: Insufficient Credit Score

```
👤 User: "I want to apply for a £15,000 loan"

🤖 Agent: "I'm unable to proceed with your loan application at this time.
Credit score of 540 is below minimum requirement of 550.

We recommend improving your credit score before reapplying.
We're here to help when you're ready to reapply."

❌ BLOCKED: Credit score below minimum threshold
```

### Additional Fraud Detection Scenarios

#### Scenario: Low Risk (Allowed)

```
👤 User: "Transfer £500 to my friend in London"

🤖 Agent: "I've transferred £500 to your friend.
Transaction reference: TXN-20260426-001
New balance: £3,750.50"

✅ LOW RISK (0/100): Transaction approved
```

#### Scenario: Medium Risk with Monitoring

```
👤 User: "Transfer £6,000 to my business partner"

🤖 Agent: "I've processed the transfer of £6,000.
Transaction reference: TXN-20260426-002

Note: This transaction will be monitored as part of our
standard security procedures."

✅ LOW RISK (20/100): Transaction approved with monitoring
```

---

## 🔍 Troubleshooting

### Guardrail Not Triggering

**Problem:** Guardrail doesn't block expected transaction

**Solutions:**
1. Verify guardrail is imported:
   ```bash
   orchestrate tools list | grep guardrail
   ```
2. Check agent YAML has plugins section
3. Verify guardrail is attached to correct agent
4. Ensure using agent WITH guardrails (not `_no_guardrails` version)

### PII Not Being Redacted

**Problem:** Sensitive data shows in full

**Solutions:**
1. Verify `pii_protection_guardrail` is in `agent_post_invoke` section
2. Check regex patterns in guardrail code match data formats
3. Test with exact data formats from demo data
4. Verify guardrail imported successfully

### Transaction Limits Not Enforced

**Problem:** Large transfers go through

**Solutions:**
1. Verify `transaction_limit_guardrail` is in `agent_pre_invoke` section
2. Check amount extraction regex patterns
3. Verify limits match account type
4. Ensure using correct agent (not `_no_guardrails` version)

### Wrong Agent Version Responding

**Problem:** Getting unexpected behavior

**Solution:** Verify you're chatting with the correct orchestrator:
- WITH guardrails: `banking_orchestrator_agent`
- WITHOUT guardrails: `banking_orchestrator_agent_no_guardrails`

---

## 📖 Quick Reference

### Agent Names

| Purpose | Agent Name |
|---------|-----------|
| **WITH Guardrails** | |
| Orchestrator | `banking_orchestrator_agent` |
| Customer Service | `customer_service_agent` |
| Loan Processing | `loan_processing_agent` |
| **WITHOUT Guardrails** | |
| Orchestrator | `banking_orchestrator_agent_no_guardrails` |
| Customer Service | `customer_service_agent_no_guardrails` |
| Loan Processing | `loan_processing_agent_no_guardrails` |

### Import Scripts

```bash
# Deploy WITH guardrails (production)
./import-all.sh

# Deploy WITHOUT guardrails (demo only)
./import-no-guardrails.sh
```

### Summary Comparison Table

| Scenario | Without Guardrails | With Guardrails | Protection |
|----------|-------------------|-----------------|------------|
| **PII Exposure** | Full account number exposed | Masked to ****1234 | ✅ PII Protection |
| **Excessive Transfer** | £12k transfer processed | Blocked (exceeds £10k limit) | ✅ Transaction Limits |
| **Unaffordable Loan** | £350k loan approved | Blocked (exceeds 5x income) | ✅ Lending Compliance |
| **Fraud Risk** | £12k to Nigeria processed | Blocked (95/100 risk score) | ✅ Fraud Detection |

### Key Talking Points

**Opening:**
> "Guardrails are essential for banking AI. I'll show what happens WITHOUT them, then how they protect against the same issues."

**During Demo:**
> "Notice how guardrails work invisibly in the background, protecting both the bank and customers without disrupting the user experience."

**Closing:**
> "Guardrails provide Security, Compliance, Risk Management, and Trust. They're not optional for production banking AI."

---

## ⚠️ Important Notes

### Production Deployment

**CRITICAL:** Only deploy agents WITH guardrails to production:
- `banking_orchestrator_agent`
- `customer_service_agent`
- `loan_processing_agent`
- `fraud_detection_agent`
- `compliance_risk_agent`

**NEVER deploy the `_no_guardrails` versions to production environments!**

### Demo Best Practices

1. **Always start with "Before"** - Show the problem first
2. **Use same test scenarios** - Consistency proves the point
3. **Explain each guardrail** - Help audience understand the protection
4. **Keep credentials visible** - Use the demo accounts provided
5. **Reset between demos** - Clear conversation history for clean demos

---

## 📚 Related Documentation

- **GUARDRAILS_IMPLEMENTATION.md** - Technical implementation details
- **IMPLEMENTATION_SUMMARY.md** - Project statistics and architecture
- **TESTING_GUIDE.md** - Testing procedures and verification
- **TROUBLESHOOTING.md** - Common issues and solutions

---

**Last Updated:** 2026-05-05  
**Created By:** Bob (WXO Agent Architect)  
**Version:** 2.0 (Unified Guide)  
**Architecture:** Cloudant-backed standalone Python tools