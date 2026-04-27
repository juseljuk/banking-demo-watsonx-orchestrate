#!/usr/bin/env python3
"""
Test runner for Loan Approval Workflow using watsonx Orchestrate SDK
This script compiles, deploys, and runs the workflow with test data
"""

import asyncio
import sys
from datetime import datetime

# Import the workflow builder function
sys.path.insert(0, '../tools')
from loan_approval_workflow import build_loan_approval_workflow

from ibm_watsonx_orchestrate.flow_builder.flows import FlowEventType


async def test_workflow_with_customer(customer_id: str, loan_amount: float, loan_purpose: str):
    """Test the workflow with specific customer data"""
    
    print(f"\n{'─'*70}")
    print(f"Testing Loan Approval Workflow")
    print(f"{'─'*70}")
    print(f"Customer ID: {customer_id}")
    print(f"Loan Amount: £{loan_amount:,.2f}")
    print(f"Purpose: {loan_purpose}")
    print(f"{'─'*70}\n")
    
    try:
        # Step 1: Build the workflow
        print("⏳ Step 1: Building workflow definition...")
        my_flow_definition = build_loan_approval_workflow()
        print("✅ Workflow definition created\n")
        
        # Step 2: Compile and deploy
        print("⏳ Step 2: Compiling and deploying workflow...")
        compiled_flow = await my_flow_definition.compile_deploy()
        print("✅ Workflow compiled and deployed\n")
        
        # Step 3: Prepare input data
        input_data = {
            "customer_id": customer_id,
            "loan_amount": loan_amount,
            "loan_purpose": loan_purpose
        }
        
        print("⏳ Step 3: Invoking workflow...")
        print(f"Input: {input_data}\n")
        
        # Step 4: Invoke the workflow and process events
        print("⏳ Step 4: Invoking workflow and waiting for completion...")
        
        output = None
        error = None
        
        async for event, run in compiled_flow.invoke_events(input_data):
            if not event:
                continue
            
            if event.kind == FlowEventType.ON_FLOW_START:
                print("  ▶ Workflow started")
            elif event.kind == FlowEventType.ON_FLOW_END:
                print("  ✓ Workflow completed")
                output = run.output
                break
            elif event.kind == FlowEventType.ON_FLOW_ERROR:
                print("  ✗ Workflow failed")
                error = run.error
                break
        
        print()
        
        # Step 5: Display results
        if output is not None:
            print("✅ WORKFLOW COMPLETED SUCCESSFULLY\n")
            print(f"{'─'*70}")
            print("WORKFLOW OUTPUT:")
            print(f"{'─'*70}")
            
            if isinstance(output, dict):
                print(f"Status: {output.get('status', 'N/A')}")
                print(f"Customer ID: {output.get('customer_id', 'N/A')}")
                print(f"Loan Amount: £{output.get('loan_amount', 0):,.2f}")
                print(f"Decision: {output.get('decision', 'N/A')}")
                
                if 'offers' in output and output['offers']:
                    print(f"\nLoan Offers ({len(output['offers'])}):")
                    for i, offer in enumerate(output['offers'], 1):
                        print(f"\n  Offer {i}:")
                        print(f"    Amount: £{offer.get('amount', 0):,.2f}")
                        print(f"    Term: {offer.get('term_months', 0)} months")
                        print(f"    Rate: {offer.get('interest_rate', 0)}%")
                        print(f"    Monthly: £{offer.get('monthly_payment', 0):,.2f}")
                
                if 'next_steps' in output:
                    print(f"\nNext Steps: {output['next_steps']}")
            else:
                print(output)
            
            print(f"{'─'*70}\n")
            return True
        elif error is not None:
            print("❌ WORKFLOW FAILED\n")
            print(f"Error: {error}")
            return False
        else:
            print("❌ WORKFLOW ENDED WITHOUT RESULT\n")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def run_all_tests():
    """Run multiple test scenarios"""
    
    print("\n" + "="*70)
    print("LOAN APPROVAL WORKFLOW - INTEGRATION TEST SUITE")
    print("="*70)
    print(f"Test Run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    test_cases = [
        {
            "name": "Test 1: Emma Thompson - Good Credit",
            "customer_id": "CUST-001",
            "loan_amount": 20000.00,
            "loan_purpose": "Home Improvements"
        },
        {
            "name": "Test 2: James Patel - Business Loan",
            "customer_id": "CUST-002",
            "loan_amount": 50000.00,
            "loan_purpose": "Business Expansion"
        },
        {
            "name": "Test 3: Sophie Williams - Vehicle Purchase",
            "customer_id": "CUST-003",
            "loan_amount": 15000.00,
            "loan_purpose": "Vehicle Purchase"
        }
    ]
    
    results = []
    
    for test_case in test_cases:
        print(f"\n{'='*70}")
        print(f"{test_case['name']}")
        print(f"{'='*70}")
        
        success = await test_workflow_with_customer(
            test_case['customer_id'],
            test_case['loan_amount'],
            test_case['loan_purpose']
        )
        
        results.append({
            "name": test_case['name'],
            "success": success
        })
        
        # Wait between tests
        await asyncio.sleep(2)
    
    # Summary
    print(f"\n{'='*70}")
    print("TEST SUMMARY")
    print(f"{'='*70}")
    
    passed = sum(1 for r in results if r['success'])
    failed = len(results) - passed
    
    for result in results:
        status_icon = "✅" if result['success'] else "❌"
        status_text = "PASSED" if result['success'] else "FAILED"
        print(f"{status_icon} {result['name']}: {status_text}")
    
    print(f"\n{'─'*70}")
    print(f"Total Tests: {len(results)}")
    print(f"Passed: {passed} ({passed/len(results)*100:.0f}%)")
    print(f"Failed: {failed}")
    print(f"{'='*70}\n")
    
    if passed == len(results):
        print("🎉 ALL TESTS PASSED!")
        return 0
    else:
        print(f"⚠️  {failed} TEST(S) FAILED")
        return 1


async def main():
    """Main entry point"""
    
    # Check if specific test is requested
    if len(sys.argv) > 1:
        if sys.argv[1] == "--all":
            return await run_all_tests()
        elif sys.argv[1] == "--help":
            print("\nUsage:")
            print("  python run_loan_approval_workflow.py [OPTIONS]")
            print("\nOptions:")
            print("  --all              Run all test scenarios")
            print("  --help             Show this help message")
            print("  (no args)          Run single test with Emma Thompson")
            print("\nExamples:")
            print("  python run_loan_approval_workflow.py")
            print("  python run_loan_approval_workflow.py --all")
            return 0
    
    # Default: Run single test
    success = await test_workflow_with_customer(
        customer_id="CUST-001",
        loan_amount=20000.00,
        loan_purpose="Home Improvements"
    )
    
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)


# Made with Bob