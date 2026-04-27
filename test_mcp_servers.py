#!/usr/bin/env python3
"""
Test script to verify MCP servers work correctly
"""

import asyncio
import json
import sys
from pathlib import Path

# Add toolkits directory to path
sys.path.insert(0, str(Path(__file__).parent / "toolkits"))

async def test_core_banking_server():
    """Test Core Banking MCP Server"""
    print("\n" + "="*60)
    print("Testing Core Banking MCP Server")
    print("="*60)
    
    try:
        from core_banking_server import app, call_tool
        
        # Test 1: get_current_customer
        print("\n1. Testing get_current_customer...")
        result = await call_tool("get_current_customer", {})
        data = json.loads(result[0].text)
        assert data["status"] == "success"
        assert data["customer_id"] == "CUST-001"
        assert len(data["accounts"]) == 3
        print("   ✓ get_current_customer works!")
        print(f"   Customer: {data['customer_name']}")
        print(f"   Accounts: {len(data['accounts'])}")
        
        # Test 2: check_account_balance
        print("\n2. Testing check_account_balance...")
        result = await call_tool("check_account_balance", {"account_id": "CUR-001-1234"})
        data = json.loads(result[0].text)
        assert data["status"] == "success"
        assert data["current_balance"] == 4250.50
        print("   ✓ check_account_balance works!")
        print(f"   Balance: £{data['current_balance']}")
        
        # Test 3: get_recent_transactions
        print("\n3. Testing get_recent_transactions...")
        result = await call_tool("get_recent_transactions", {"account_id": "CUR-001-1234", "limit": 5})
        data = json.loads(result[0].text)
        assert data["status"] == "success"
        assert data["count"] > 0
        print("   ✓ get_recent_transactions works!")
        print(f"   Transactions found: {data['count']}")
        
        print("\n✅ Core Banking Server: ALL TESTS PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ Core Banking Server: FAILED - {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_fraud_detection_server():
    """Test Fraud Detection MCP Server"""
    print("\n" + "="*60)
    print("Testing Fraud Detection MCP Server")
    print("="*60)
    
    try:
        from fraud_detection_server import app, call_tool
        
        # Test 1: analyze_transaction_risk
        print("\n1. Testing analyze_transaction_risk...")
        result = await call_tool("analyze_transaction_risk", {
            "transaction_id": "TXN-TEST-001",
            "account_id": "CUR-001-1234",
            "amount": 3500.00,
            "merchant": "Unknown Merchant",
            "location": "Nigeria",
            "transaction_type": "International Transfer"
        })
        data = json.loads(result[0].text)
        assert data["status"] == "success"
        assert data["risk_analysis"]["risk_score"] > 50  # Should be high risk
        print("   ✓ analyze_transaction_risk works!")
        print(f"   Risk Score: {data['risk_analysis']['risk_score']}/100")
        print(f"   Risk Level: {data['risk_analysis']['risk_level']}")
        
        # Test 2: get_fraud_scenario
        print("\n2. Testing get_fraud_scenario...")
        result = await call_tool("get_fraud_scenario", {"scenario_id": "TXN-FRAUD-001"})
        data = json.loads(result[0].text)
        assert data["status"] == "success"
        assert data["scenario"]["risk_analysis"]["risk_score"] == 92
        print("   ✓ get_fraud_scenario works!")
        print(f"   Scenario: {data['scenario']['type']}")
        
        print("\n✅ Fraud Detection Server: ALL TESTS PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ Fraud Detection Server: FAILED - {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_loan_processing_server():
    """Test Loan Processing MCP Server"""
    print("\n" + "="*60)
    print("Testing Loan Processing MCP Server")
    print("="*60)
    
    try:
        from loan_processing_server import app, call_tool
        
        # Test 1: check_credit_score
        print("\n1. Testing check_credit_score...")
        result = await call_tool("check_credit_score", {"customer_id": "CUST-001"})
        data = json.loads(result[0].text)
        assert data["status"] == "success"
        assert data["credit_score"] == 742
        print("   ✓ check_credit_score works!")
        print(f"   Credit Score: {data['credit_score']}")
        print(f"   Rating: {data['rating']}")
        
        # Test 2: calculate_loan_eligibility
        print("\n2. Testing calculate_loan_eligibility...")
        result = await call_tool("calculate_loan_eligibility", {
            "customer_id": "CUST-001",
            "loan_amount": 20000.00,
            "loan_purpose": "Home Improvements"
        })
        data = json.loads(result[0].text)
        assert data["status"] == "success"
        assert data["eligible"] == True
        print("   ✓ calculate_loan_eligibility works!")
        print(f"   Eligible: {data['eligible']}")
        print(f"   Max Loan: £{data['max_approved_amount']}")
        
        # Test 3: get_loan_application
        print("\n3. Testing get_loan_application...")
        result = await call_tool("get_loan_application", {"application_id": "LOAN-APP-001"})
        data = json.loads(result[0].text)
        assert data["status"] == "success"
        assert data["application"]["application_id"] == "LOAN-APP-001"
        print("   ✓ get_loan_application works!")
        print(f"   Status: {data['application']['application_status']}")
        
        print("\n✅ Loan Processing Server: ALL TESTS PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ Loan Processing Server: FAILED - {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("MCP SERVERS TEST SUITE")
    print("="*60)
    
    results = []
    
    # Test each server
    results.append(await test_core_banking_server())
    results.append(await test_fraud_detection_server())
    results.append(await test_loan_processing_server())
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    passed = sum(results)
    total = len(results)
    print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 ALL MCP SERVERS WORKING CORRECTLY!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} server(s) failed")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

# Made with Bob
