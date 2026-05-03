# Loan Approval Workflow - Agentic Workflow Demo

## Overview

The **Loan Approval Workflow** is a deterministic agentic workflow that demonstrates how to orchestrate multiple tools in a predictable, rule-based sequence. This workflow showcases watsonx Orchestrate's ability to create complex, multi-step business processes that execute reliably without requiring LLM decision-making at each step.

## What is an Agentic Workflow?

An agentic workflow is a **deterministic tool flow** that:
- Executes tools in a predefined sequence
- Makes decisions based on explicit business rules (not LLM reasoning)
- Branches based on tool outputs
- Provides predictable, repeatable results
- Can be used as a single tool by agents

**Key Difference from Agents:**
- **Agents**: Use LLM reasoning to decide which tools to call and when
- **Workflows**: Follow predefined logic paths with conditional branching

## Loan Approval Workflow Architecture

### Workflow Steps

```
START
  ↓
1. Check Credit Score
  ↓
2. Calculate Debt-to-Income Ratio
  ↓
3. Assess Loan Eligibility
  ↓
4. Branch on Eligibility
  ├─ TRUE (Eligible)
  │   ↓
  │   5. Generate Loan Offers
  │   ↓
  │   END (Approved with offers)
  │
  └─ FALSE (Not Eligible)
      ↓
      END (Rejected with reasons)
```

### Business Rules

The workflow implements these deterministic rules:

1. **Credit Score Check**
   - Minimum: 600
   - Retrieved from credit bureau data

2. **Debt-to-Income Ratio**
   - Maximum: 40%
   - Warning threshold: 35%

3. **Eligibility Decision**
   - Credit score >= 600 ✅
   - DTI ratio <= 40% ✅
   - Loan amount within limits ✅
   - UK resident ✅

4. **Branching Logic**
   - If ALL criteria met → Generate offers
   - If ANY criteria failed → Reject with reasons

## Integration with Banking Demo

### Authentication

The workflow **does NOT handle authentication**. It expects:
- Customer is already authenticated by the orchestrator
- `customer_id` is provided as input
- Session context is maintained by the platform

### Tools Used

The workflow calls these standalone Python tools:

1. **`check_credit_score`**
   - Input: `customer_id`
   - Output: Credit score, rating, bureau data

2. **`calculate_debt_to_income`**
   - Input: `customer_id`
   - Output: DTI ratio, monthly debt, monthly income

3. **`calculate_loan_eligibility`**
   - Input: `customer_id`, `loan_amount`, `loan_purpose`
   - Output: `eligible` (boolean), reasons, max approved amount

4. **`generate_loan_offers`**
   - Input: `customer_id`, `loan_amount`
   - Output: Array of loan offers with terms, APR, monthly payments

## Usage Examples

### Example 1: Eligible Customer (Emma Thompson)

**Input:**
```json
{
  "customer_id": "CUST-001",
  "loan_amount": 20000.00,
  "loan_purpose": "Home Improvements"
}
```

**Workflow Execution:**
1. ✅ Credit Score: 742 (Good)
2. ✅ DTI Ratio: 8.5% (Well within 40% limit)
3. ✅ Eligibility: Approved for up to £32,500
4. ✅ Branch: TRUE → Generate offers
5. ✅ Output: 3 loan offers with different terms

**Output:**
```json
{
  "status": "approved",
  "customer_id": "CUST-001",
  "loan_amount": 20000.00,
  "decision": "Loan approved based on excellent credit score (742) and low debt-to-income ratio (8.5%)",
  "offers": [
    {
      "term_months": 60,
      "apr": 7.9,
      "monthly_payment": 405.00,
      "total_payable": 24300.00
    },
    {
      "term_months": 36,
      "apr": 8.4,
      "monthly_payment": 630.00,
      "total_payable": 22680.00
    },
    {
      "term_months": 84,
      "apr": 8.9,
      "monthly_payment": 310.00,
      "total_payable": 26040.00
    }
  ],
  "next_steps": "Review the loan offers and select your preferred term. We'll send the documents for e-signature."
}
```

### Example 2: Ineligible Customer (Low Credit Score)

**Input:**
```json
{
  "customer_id": "CUST-004",
  "loan_amount": 15000.00,
  "loan_purpose": "Debt Consolidation"
}
```

**Workflow Execution:**
1. ❌ Credit Score: 540 (Below minimum 600)
2. ✅ DTI Ratio: 25% (Within limits)
3. ❌ Eligibility: Rejected due to credit score
4. ❌ Branch: FALSE → Skip offer generation
5. ❌ Output: Rejection with improvement suggestions

**Output:**
```json
{
  "status": "rejected",
  "customer_id": "CUST-004",
  "loan_amount": 15000.00,
  "decision": "Loan application declined. Credit score of 540 is below our minimum requirement of 600.",
  "offers": [],
  "next_steps": "We recommend improving your credit score before reapplying. Consider: paying down existing debts, making all payments on time, and checking your credit report for errors. We're here to help when you're ready to reapply."
}
```

## Deployment

### 1. Import the Workflow

```bash
cd banking-demo

# Import as a flow tool
orchestrate tools import -k flow -f tools/loan_approval_workflow.py
```

### 2. Verify Import

```bash
# Check that workflow is imported
orchestrate tools list | grep loan_approval_workflow

# Should show:
# loan_approval_workflow
```

### 3. Use in Agents

Add the workflow to any agent's tools list:

```yaml
# agents/loan-processing-agent.yaml
tools:
  - loan_approval_workflow  # The workflow as a single tool
  - check_credit_score
  - generate_loan_offers
  # ... other tools
```

Or use it standalone:

```yaml
# agents/automated-loan-agent.yaml
spec_version: v1
kind: native
name: automated_loan_agent
description: Fully automated loan processing using workflow

llm: groq/openai/gpt-oss-120b

instructions: |
  You process loan applications using the automated loan approval workflow.
  Simply call the workflow with customer_id, loan_amount, and loan_purpose.

tools:
  - loan_approval_workflow

guidelines:
  - condition: "Customer requests a loan"
    action: "Call loan_approval_workflow with the loan details"
    tool: "loan_approval_workflow"
```

## Benefits of Using Workflows

### 1. **Predictability**
- Same inputs always produce same outputs
- No LLM variability in decision-making
- Easier to test and validate

### 2. **Performance**
- Faster execution (no LLM reasoning between steps)
- Lower token costs
- Deterministic latency

### 3. **Compliance**
- Business rules are explicit and auditable
- Easier to demonstrate regulatory compliance
- Clear decision trail

### 4. **Maintainability**
- Business logic is centralized
- Changes to rules update all users
- Version control for business processes

### 5. **Reusability**
- Workflow can be used by multiple agents
- Can be called from other workflows
- Reduces code duplication

## Testing the Workflow

### Local Testing

```python
# test_loan_workflow.py
from loan_approval_workflow import build_loan_approval_workflow

# Test with eligible customer
input_data = {
    "customer_id": "CUST-001",
    "loan_amount": 20000.00,
    "loan_purpose": "Home Improvements"
}

# Build and run workflow
workflow = build_loan_approval_workflow()
result = workflow.run(input_data)

print(f"Status: {result['status']}")
print(f"Decision: {result['decision']}")
print(f"Offers: {len(result['offers'])}")
```

### Integration Testing

```bash
# Use orchestrate CLI evaluation
orchestrate evaluations quick-eval \
  -p tests/loan_workflow_tests.json \
  -o results/ \
  -t tools/
```

## Comparison: Agent vs Workflow

### Using Loan Processing Agent (LLM-driven)

**User**: "I'd like to apply for a £20,000 loan"

**Agent Process**:
1. LLM decides to check credit score
2. LLM interprets credit score result
3. LLM decides to calculate DTI
4. LLM interprets DTI result
5. LLM decides to assess eligibility
6. LLM interprets eligibility result
7. LLM decides to generate offers
8. LLM formats response

**Characteristics**:
- ✅ Flexible, conversational
- ✅ Can handle edge cases
- ❌ Variable execution path
- ❌ Higher token costs
- ❌ Slower (multiple LLM calls)

### Using Loan Approval Workflow (Deterministic)

**User**: "I'd like to apply for a £20,000 loan"

**Workflow Process**:
1. Check credit score (always)
2. Calculate DTI (always)
3. Assess eligibility (always)
4. Branch on result (deterministic)
5. Generate offers if eligible (conditional)
6. Return structured output (always)

**Characteristics**:
- ✅ Fast, predictable
- ✅ Lower costs
- ✅ Auditable decisions
- ✅ Consistent results
- ❌ Less flexible
- ❌ Requires predefined paths

## Best Practices

### When to Use Workflows

✅ **Use workflows when:**
- Business logic is well-defined
- Decisions follow clear rules
- Consistency is critical
- Performance matters
- Compliance requires auditability

❌ **Don't use workflows when:**
- Requirements are ambiguous
- Flexibility is needed
- Conversational context matters
- Edge cases are common

### Workflow Design Tips

1. **Keep it Simple**: 5-10 steps maximum
2. **Clear Branching**: Explicit conditions
3. **Error Handling**: Plan for tool failures
4. **Structured Output**: Use Pydantic models
5. **Documentation**: Explain business rules

## Troubleshooting

### Workflow Not Found

```bash
# Verify import
orchestrate tools list | grep loan_approval_workflow

# Reimport if needed
orchestrate tools import -k flow -f tools/loan_approval_workflow.py
```

### Branch Not Working

Check the evaluator expression:
```python
# Correct: Access node output
evaluator="flow.nodes['assess_eligibility'].output.eligible == True"

# Wrong: Direct access
evaluator="flow.output.eligible == True"
```

### Tools Not Available

Ensure MCP toolkits are imported first:
```bash
orchestrate toolkits list | grep loan-processing
```

## Next Steps

1. **Import the workflow**: `orchestrate tools import -k flow -f tools/loan_approval_workflow.py`
2. **Test with Emma Thompson**: Use CUST-001 with £20,000 loan
3. **Compare with agent**: Try same request with loan_processing_agent
4. **Measure performance**: Compare execution time and token usage
5. **Extend workflow**: Add more branches or steps as needed

---

**Created**: 2026-04-27  
**Author**: Bob (WXO Agent Architect)  
**Status**: Ready for Deployment