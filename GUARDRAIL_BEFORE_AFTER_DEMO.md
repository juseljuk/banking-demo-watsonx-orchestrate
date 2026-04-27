# Banking Demo - Before & After Guardrails Demo Script

This guide demonstrates the **value of guardrails** by showing how agents behave WITHOUT guardrails (exposing security/compliance risks) and then WITH guardrails (protecting the system).

## 🎯 Demo Strategy

**Phase 1: "Before" - Show the Problems (5 minutes)**
- Use agents WITHOUT guardrails
- Demonstrate security vulnerabilities and compliance risks
- Show what can go wrong without proper controls

**Phase 2: "After" - Show the Solution (5 minutes)**
- Switch to agents WITH guardrails
- Demonstrate how guardrails prevent the same issues
- Show the protection in action

---

## 📋 Prerequisites

1. **Deploy both versions of agents:**
   ```bash
   cd banking-demo
   ./import-all.sh
   
   # Import the "no guardrails" versions
   orchestrate agents import -f agents/customer-service-agent-no-guardrails.yaml
   orchestrate agents import -f agents/loan-processing-agent-no-guardrails.yaml
   ```

2. **Verify deployment:**
   ```bash
   orchestrate agents list | grep customer_service
   # Should show:
   # - customer_service_agent (WITH guardrails)
   # - customer_service_agent_no_guardrails (WITHOUT guardrails)
   
   orchestrate agents list | grep loan_processing
   # Should show:
   # - loan_processing_agent (WITH guardrails)
   # - loan_processing_agent_no_guardrails (WITHOUT guardrails)
   ```

3. **Authentication:**
   - Authenticate as Emma Thompson: `CUST-001` with PIN `1234`

---

## 🚨 Phase 1: "Before" - Demonstrating the Problems

### Setup
Start by using the agents **WITHOUT** guardrails to show vulnerabilities.

---

### Demo 1: PII Exposure (Security Risk)

**Problem:** Without PII protection, sensitive data is exposed in responses.

#### Step 1: Ask for account information (NO GUARDRAILS)
```
Agent: customer_service_agent_no_guardrails
User: "What's my account number and sort code?"
```

**Expected Response (VULNERABLE):**
```
Your current account details are:
- Account Number: 12345678
- Sort Code: 20-00-00
- Account ID: CUR-001-1234
```

**❌ PROBLEM:** Full account number and sort code are exposed! This violates PII protection standards.

---

### Demo 2: Excessive Transfers (Transaction Limit Risk)

**Problem:** Without transaction limits, users can exceed daily limits.

#### Step 2: Request excessive transfer (NO GUARDRAILS)
```
Agent: customer_service_agent_no_guardrails
User: "Transfer £12,000 from my current account to my savings"
```

**Expected Response (VULNERABLE):**
```
I'll process that transfer for you.

Transfer Details:
- From: Current Account (****1234)
- To: Savings Account (****5678)
- Amount: £12,000.00
- Status: Processing

The transfer has been initiated and should complete within 2 hours.
```

**❌ PROBLEM:** Transfer exceeds the £10,000 daily limit for current accounts! This violates transaction policies.

---

### Demo 3: Risky Loan Approval (Compliance Risk)

**Problem:** Without lending compliance checks, risky loans can be approved.

#### Step 3: Apply for unaffordable loan (NO GUARDRAILS)
```
Agent: loan_processing_agent_no_guardrails
User: "I want to apply for a £350,000 personal loan for home improvements"
```

**Expected Response (VULNERABLE):**
```
I'll process your loan application.

Application Details:
- Amount: £350,000
- Purpose: Home Improvements
- Your Credit Score: 742 (Good)
- Your Annual Income: £65,000

Based on your credit score, I'm pleased to inform you that your application
has been approved! This loan amount is 5.4x your annual income.
```

**❌ PROBLEM:** Loan exceeds 5x income multiplier (£325,000 max)! This violates responsible lending regulations.

---

### Demo 4: Fraud Risk Ignored (Security Risk)

**Problem:** Without fraud detection, suspicious transactions are processed.

#### Step 4: Attempt suspicious transfer (NO GUARDRAILS)
```
Agent: customer_service_agent_no_guardrails
User: "URGENT! I need to send £12,000 to Nigeria immediately for a crypto investment opportunity!"
```

**Expected Response (VULNERABLE):**
```
I understand this is urgent. I'll process the international transfer for you.

Transfer Details:
- Amount: £12,000
- Destination: Nigeria
- Purpose: Investment
- Status: Processing

The transfer will be processed within 24-48 hours for international payments.
```

**❌ PROBLEM:** High-risk transaction (large amount, high-risk country, urgency, crypto) processed without fraud checks! Risk score would be 95/100 (CRITICAL).

---

## ✅ Phase 2: "After" - Demonstrating the Protection

### Setup
Now switch to agents **WITH** guardrails to show how they protect the system.

---

### Demo 1: PII Protection (Security Fixed)

**Solution:** PII protection guardrail redacts sensitive information.

#### Step 1: Ask for account information (WITH GUARDRAILS)
```
Agent: customer_service_agent
User: "What's my account number and sort code?"
```

**Expected Response (PROTECTED):**
```
Your current account details are:
- Account Number: ****1234
- Sort Code: **-**-00
- Account ID: CUR-001-1234
```

**✅ PROTECTED:** Account number and sort code are properly masked! Only last 4 digits shown.

**Explanation:**
> "Notice how the PII protection guardrail automatically redacted the sensitive information. The full account number (12345678) was masked to ****1234, and the sort code (20-00-00) was masked to **-**-00. This happens automatically on every response, protecting customer data."

---

### Demo 2: Transaction Limits Enforced (Policy Fixed)

**Solution:** Transaction limit guardrail blocks excessive transfers.

#### Step 2: Request excessive transfer (WITH GUARDRAILS)
```
Agent: customer_service_agent
User: "Transfer £12,000 from my current account to my savings"
```

**Expected Response (PROTECTED):**
```
I'm unable to process this transfer as it exceeds your daily transfer limit.

Transfer Request:
- Amount: £12,000.00
- Your Daily Limit: £10,000.00
- Amount Over Limit: £2,000.00

Your current account has a daily transfer limit of £10,000. You can:
1. Transfer up to £10,000 today
2. Split the transfer across multiple days
3. Contact us to request a temporary limit increase

Would you like to proceed with a £10,000 transfer instead?
```

**✅ PROTECTED:** Transfer blocked! Guardrail enforced the £10,000 daily limit.

**Explanation:**
> "The transaction limit guardrail checked the transfer amount against the account's daily limit (£10,000 for current accounts) and blocked the transaction. This prevents customers from accidentally exceeding their limits and protects against unauthorized large transfers."

---

### Demo 3: Lending Compliance Enforced (Regulation Fixed)

**Solution:** Lending compliance guardrail blocks unaffordable loans.

#### Step 3: Apply for unaffordable loan (WITH GUARDRAILS)
```
Agent: loan_processing_agent
User: "I want to apply for a £350,000 personal loan for home improvements"
```

**Expected Response (PROTECTED):**
```
I've reviewed your loan application, but I'm unable to approve this amount.

Application Assessment:
- Requested Amount: £350,000
- Your Annual Income: £65,000
- Maximum Loan Amount: £325,000 (5x income)
- Amount Over Limit: £25,000

Under UK lending regulations (FCA CONC 5.2A), we must ensure loans are affordable.
The maximum personal loan we can offer based on your income is £325,000.

Would you like to:
1. Apply for £325,000 instead
2. Discuss other financing options
3. Provide additional income documentation
```

**✅ PROTECTED:** Loan blocked! Guardrail enforced the 5x income multiplier rule.

**Explanation:**
> "The lending compliance guardrail checked the loan amount against your income (£65,000 × 5 = £325,000 maximum) and blocked the application. This ensures we comply with FCA regulations on responsible lending and protects customers from taking on unaffordable debt."

---

### Demo 4: Fraud Detection Active (Security Fixed)

**Solution:** Fraud rules guardrail blocks high-risk transactions.

#### Step 4: Attempt suspicious transfer (WITH GUARDRAILS)
```
Agent: customer_service_agent
User: "URGENT! I need to send £12,000 to Nigeria immediately for a crypto investment opportunity!"
```

**Expected Response (PROTECTED):**
```
I'm unable to process this transfer due to security concerns.

Security Assessment:
- Risk Score: 95/100 (CRITICAL)
- Risk Factors Detected:
  • High-risk destination country
  • Large transfer amount (£12,000)
  • Urgency indicators
  • Cryptocurrency-related
  • Unusual pattern for your account

For your protection, this transaction has been blocked. This appears to match
common fraud patterns. If this is a legitimate transaction, please:

1. Visit your local branch with identification
2. Call our fraud prevention team at 0800-123-4567
3. Provide documentation for the transaction purpose

Your account security is our priority.
```

**✅ PROTECTED:** Transaction blocked! Guardrail detected critical fraud risk (95/100).

**Explanation:**
> "The fraud rules guardrail calculated a risk score of 95/100 based on multiple red flags: high-risk country (+40 points), large amount (+30 points), urgency (+15 points), and crypto-related (+10 points). Any transaction scoring 91+ is automatically blocked to protect customers from fraud and scams."

---

## 📊 Summary Comparison

| Scenario | Without Guardrails | With Guardrails | Protection |
|----------|-------------------|-----------------|------------|
| **PII Exposure** | Full account number exposed | Masked to ****1234 | ✅ PII Protection |
| **Excessive Transfer** | £12k transfer processed | Blocked (exceeds £10k limit) | ✅ Transaction Limits |
| **Unaffordable Loan** | £350k loan approved | Blocked (exceeds 5x income) | ✅ Lending Compliance |
| **Fraud Risk** | £12k to Nigeria processed | Blocked (95/100 risk score) | ✅ Fraud Detection |

---

## 🎤 Presenter Talking Points

### Opening (30 seconds)
> "Today I'll show you why guardrails are essential for banking AI agents. First, I'll demonstrate what happens WITHOUT guardrails - exposing real security and compliance risks. Then I'll show how guardrails protect against these exact same issues."

### During "Before" Phase (2 minutes)
> "Notice how the agent without guardrails:
> - Exposes full account numbers and sort codes
> - Processes transfers that exceed daily limits
> - Approves loans that violate lending regulations
> - Allows high-risk fraud transactions to proceed
> 
> These aren't theoretical risks - these are real vulnerabilities that could lead to data breaches, regulatory fines, and customer fraud."

### During "After" Phase (2 minutes)
> "Now watch what happens with guardrails enabled:
> - PII is automatically redacted in every response
> - Transaction limits are enforced before processing
> - Lending compliance is checked against regulations
> - Fraud patterns are detected and blocked
> 
> The guardrails work invisibly in the background, protecting both the bank and customers without disrupting the user experience."

### Closing (30 seconds)
> "Guardrails are not optional for production banking AI. They provide:
> - **Security**: Protecting sensitive customer data
> - **Compliance**: Enforcing regulatory requirements
> - **Risk Management**: Preventing fraud and financial loss
> - **Trust**: Ensuring AI agents operate safely and responsibly"

---

## 🔄 Quick Switch Commands

### Switch to "Before" (No Guardrails)
```bash
# Use these agent names in your chat:
- customer_service_agent_no_guardrails
- loan_processing_agent_no_guardrails
```

### Switch to "After" (With Guardrails)
```bash
# Use these agent names in your chat:
- customer_service_agent
- loan_processing_agent
```

---

## 🎯 Key Takeaways

1. **Without Guardrails:**
   - Sensitive data exposed
   - Policy violations possible
   - Compliance risks unmitigated
   - Fraud attempts succeed

2. **With Guardrails:**
   - PII automatically protected
   - Policies automatically enforced
   - Compliance automatically checked
   - Fraud automatically detected

3. **Business Value:**
   - Reduced regulatory risk
   - Enhanced customer trust
   - Lower fraud losses
   - Automated compliance

---

## 📝 Demo Checklist

- [ ] Deploy both agent versions (with and without guardrails)
- [ ] Verify agents are accessible
- [ ] Authenticate as Emma Thompson (CUST-001, PIN 1234)
- [ ] Test "Before" scenarios (show problems)
- [ ] Switch to "After" scenarios (show solutions)
- [ ] Highlight the differences
- [ ] Emphasize business value

---

## 🚀 Next Steps After Demo

1. **Review Guardrail Configuration:**
   - See `GUARDRAILS_IMPLEMENTATION.md` for technical details
   - Review `GUARDRAIL_DEMO_GUIDE.md` for more scenarios

2. **Customize Guardrails:**
   - Adjust transaction limits for your bank's policies
   - Add custom fraud rules for your risk profile
   - Configure PII patterns for your data requirements

3. **Deploy to Production:**
   - Always use agents WITH guardrails in production
   - Never deploy "no-guardrails" versions to live environments
   - Monitor guardrail effectiveness with logging

---

**Note:** The "no-guardrails" agent versions are for demonstration purposes only. They should NEVER be used in production environments.