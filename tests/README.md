# Banking Demo - Test Suite

## Overview

This directory contains test files for validating guardrail business logic and workflow functionality.

## Test Files

### test_loan_approval_workflow.py

**NEW!** Comprehensive test suite for the Loan Approval Workflow demonstrating agentic workflow patterns.

**Features:**
- Tests workflow as a standalone tool
- 5 test scenarios covering different customer profiles
- Simulates workflow execution steps
- Shows expected inputs and outputs
- Includes CLI testing instructions

**Running the Test:**
```bash
# Run workflow tests
cd banking-demo
python3 tests/test_loan_approval_workflow.py
```

**Test Scenarios:**
1. **Emma Thompson** - Good credit (742), low DTI (8.5%)
2. **Small Loan** - £5,000 debt consolidation
3. **High-Value Loan** - £30,000 near maximum eligibility
4. **James Patel** - Excellent credit (785), business loan
5. **Sophie Williams** - Good credit (680), vehicle purchase

**Expected Output:**
```
🧪 Loan Approval Workflow Test Suite
======================================================================
LOAN APPROVAL WORKFLOW - TEST SUITE
======================================================================

Test 1: Eligible Customer (Emma Thompson)
──────────────────────────────────────────────────────────────────────
✅ Workflow Steps Executed:
   1. ✓ Check Credit Score: 742
   2. ✓ Calculate DTI: 8.5%
   3. ✓ Assess Eligibility: Eligible
   4. ✓ Generate Loan Offers: 3 offers created

✅ TEST PASSED

[... 4 more tests ...]

======================================================================
TEST SUMMARY
======================================================================
Total Tests: 5
Passed: 5 (100%)
🎉 ALL TESTS PASSED!
```

**Testing with Orchestrate CLI:**

The test script also provides instructions for testing with the actual platform:

```bash
# Verify workflow is imported
orchestrate tools list | grep loan_approval_workflow

# Test with Emma Thompson
orchestrate tools run loan_approval_workflow \
  --input '{"customer_id": "CUST-001", "loan_amount": 20000, "loan_purpose": "Home Improvements"}'
```

### test_guardrail_logic.py

Comprehensive test suite for all 4 guardrails:
- **PII Protection Guardrail** - Tests redaction of 7 types of sensitive data
- **Transaction Limit Guardrail** - Tests daily and single transaction limits
- **Lending Compliance Guardrail** - Tests credit checks and affordability
- **Fraud Rules Guardrail** - Tests risk scoring and fraud detection

### Running Tests

```bash
# Run all guardrail tests
cd banking-demo
python3 tests/test_guardrail_logic.py
```

### Expected Output

```
============================================================
BANKING DEMO - GUARDRAIL LOGIC TEST SUITE
============================================================

🧪 TESTING PII PROTECTION GUARDRAIL
✅ Account redaction
✅ Sort code redaction
✅ NI redaction
✅ Email redaction
📊 PII Protection: 4/4 tests passed

🧪 TESTING TRANSACTION LIMIT GUARDRAIL
✅ Within limit
✅ Exceeds limit
✅ Single transaction
✅ Business limit
📊 Transaction Limits: 4/4 tests passed

🧪 TESTING LENDING COMPLIANCE GUARDRAIL
✅ Credit check (approved)
✅ Credit check (rejected)
✅ Affordability (approved)
✅ Affordability (rejected)
📊 Lending Compliance: 4/4 tests passed

🧪 TESTING FRAUD RULES GUARDRAIL
✅ Low risk
✅ Elevated risk
✅ Critical risk
✅ Medium risk
📊 Fraud Detection: 4/4 tests passed

============================================================
TEST SUMMARY
============================================================
PII Protection.......................... ✅ PASSED
Transaction Limits...................... ✅ PASSED
Lending Compliance...................... ✅ PASSED
Fraud Detection......................... ✅ PASSED
============================================================
✅ ALL GUARDRAIL TESTS PASSED!
============================================================
```

## Test Coverage

### PII Protection (4 tests)
1. Account number redaction (8 digits → ****XXXX)
2. Sort code redaction (XX-XX-XX → **-**-XX)
3. NI number redaction (LLNNNNNNL → ******NNNNL)
4. Email redaction (user@domain → u***@*.domain)

### Transaction Limits (4 tests)
1. Within daily limit (£1,500 < £10,000)
2. Exceeds daily limit (£12,000 > £10,000)
3. Exceeds single transaction limit (£55,000 > £50,000)
4. Business account higher limit (£20,000 < £25,000)

### Lending Compliance (4 tests)
1. Good credit score approved (742 > 550)
2. Low credit score rejected (540 < 550)
3. Affordable loan approved (£20k, DTI 8.5%)
4. Unaffordable loan rejected (£350k > 5x income)

### Fraud Detection (4 tests)
1. Low risk transaction (£500 domestic = 0/100)
2. Elevated risk (£8k to Nigeria = 60/100)
3. Critical risk (£12k Nigeria urgent crypto = 95/100)
4. Medium risk (£6k domestic = 20/100)

## Test Methodology

Tests validate the core business logic of each guardrail by:
1. Calling the business logic functions directly
2. Providing test inputs
3. Verifying expected outputs
4. Checking edge cases and boundary conditions

Tests are independent of the watsonx Orchestrate framework and can run locally without any external dependencies.

## Adding New Tests

To add new test cases:

1. Add a new test function in `test_guardrail_logic.py`
2. Follow the existing pattern:
   ```python
   def test_new_feature():
       tests_passed = 0
       tests_total = 0
       
       # Test case 1
       tests_total += 1
       result = your_function(test_input)
       if result == expected:
           print(f"✅ Test passed")
           tests_passed += 1
       else:
           print(f"❌ Test failed")
       
       print(f"\n📊 Feature: {tests_passed}/{tests_total} tests passed")
       return tests_passed == tests_total
   ```
3. Add to `run_all_tests()` function
4. Run tests to verify

## Continuous Integration

These tests can be integrated into CI/CD pipelines:

```bash
# In CI/CD script
cd banking-demo
python3 tests/test_guardrail_logic.py
if [ $? -eq 0 ]; then
    echo "✅ All tests passed"
else
    echo "❌ Tests failed"
    exit 1
fi
```

## Test Maintenance

- Update tests when guardrail logic changes
- Add tests for new features
- Keep test data realistic and representative
- Document expected behaviors clearly

---

**Last Updated:** 2026-04-26  
**Test Coverage:** 16 test cases across 4 guardrails  
**Status:** ✅ All tests passing