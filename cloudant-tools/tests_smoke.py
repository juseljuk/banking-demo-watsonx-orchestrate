"""
Smoke tests for Cloudant-backed repository and data access flows.

Run with:
    PYTHONPATH=./cloudant-tools python3 ./cloudant-tools/tests_smoke.py
"""

from __future__ import annotations

import json

from common.cloudant_client import verify_cloudant_connection
from repositories.accounts import AccountRepository
from repositories.credit_reports import CreditReportRepository
from repositories.customers import CustomerRepository
from repositories.devices import DeviceRepository
from repositories.fraud_cases import FraudCaseRepository
from repositories.loan_applications import LoanApplicationRepository
from repositories.transactions import TransactionRepository


def _assert(condition: bool, message: str) -> None:
    """
    Raise an assertion error with a consistent message.

    Args:
        condition (bool): Assertion condition.
        message (str): Error message when assertion fails.
    """
    if not condition:
        raise AssertionError(message)


def run_smoke_tests() -> dict[str, object]:
    """
    Execute smoke tests for the main Cloudant-backed repository flows.

    Returns:
        dict[str, object]: Summary of smoke test execution.
    """
    results: dict[str, object] = {}

    connection = verify_cloudant_connection()
    _assert(connection.get("status") == "success", "Cloudant connection failed")
    results["connection"] = connection

    customer_repo = CustomerRepository()
    account_repo = AccountRepository()
    transaction_repo = TransactionRepository()
    credit_repo = CreditReportRepository()
    device_repo = DeviceRepository()
    fraud_repo = FraudCaseRepository()
    loan_repo = LoanApplicationRepository()

    customer = customer_repo.get_customer_by_id("CUST-001")
    _assert(customer is not None, "Customer lookup failed")
    _assert(customer_repo.verify_customer_pin("CUST-001", "1234"), "Customer PIN verification failed")
    customer_doc = customer if customer is not None else {}
    results["customer_lookup"] = {
        "customer_id": customer_doc.get("customer_id"),
        "name": f"{customer_doc.get('first_name', '')} {customer_doc.get('last_name', '')}".strip(),
    }

    customer_by_email = customer_repo.find_customer_by_email("emma.thompson@email.co.uk")
    _assert(customer_by_email is not None, "Customer email lookup failed")
    customer_email_doc = customer_by_email if customer_by_email is not None else {}
    results["customer_email_lookup"] = {
        "customer_id": customer_email_doc.get("customer_id"),
    }

    accounts = account_repo.list_accounts_for_customer("CUST-001")
    _assert(len(accounts) >= 1, "Expected at least one customer account")
    results["customer_accounts"] = {
        "count": len(accounts),
    }

    account = account_repo.get_account_by_id("CUR-001-1234")
    _assert(account is not None, "Account lookup failed")
    account_doc = account if account is not None else {}
    results["account_lookup"] = {
        "account_id": account_doc.get("account_id"),
        "current_balance": account_doc.get("current_balance"),
    }

    credit_accounts = account_repo.list_credit_card_accounts_for_customer("CUST-001")
    _assert(len(credit_accounts) >= 1, "Expected at least one credit card account")
    results["credit_card_accounts"] = {
        "count": len(credit_accounts),
    }

    recent_transactions = transaction_repo.list_recent_transactions(
        account_id="CUR-001-1234",
        limit=5,
        posted_only=True,
    )
    _assert(len(recent_transactions) >= 1, "Expected at least one recent transaction")
    results["recent_transactions"] = {
        "count": len(recent_transactions),
        "first_transaction_id": recent_transactions[0].get("transaction_id"),
    }

    pending_transactions = transaction_repo.list_pending_transactions("CUR-001-1234")
    _assert(len(pending_transactions) >= 1, "Expected at least one pending transaction")
    results["pending_transactions"] = {
        "count": len(pending_transactions),
        "total_amount": round(sum(float(item.get("amount", 0) or 0) for item in pending_transactions), 2),
    }

    credit_report = credit_repo.get_credit_report_by_customer_id("CUST-001")
    _assert(credit_report is not None, "Credit report lookup failed")
    credit_report_doc = credit_report if credit_report is not None else {}
    results["credit_report"] = {
        "customer_id": credit_report_doc.get("customer_id"),
        "bureau": credit_report_doc.get("bureau"),
        "credit_score": credit_report_doc.get("credit_score", {}).get("score"),
    }

    device = device_repo.get_device_by_id("DEV-EMMA-IPHONE")
    _assert(device is not None, "Device lookup failed")
    device_doc = device if device is not None else {}
    results["device_lookup"] = {
        "device_id": device_doc.get("device_id"),
        "trusted": device_doc.get("trusted"),
    }

    customer_devices = device_repo.list_devices_for_customer("CUST-001")
    _assert(len(customer_devices) >= 1, "Expected at least one device for customer")
    results["customer_devices"] = {
        "count": len(customer_devices),
    }

    fraud_record = fraud_repo.get_fraud_record_by_id("TXN-FRAUD-001")
    _assert(fraud_record is not None, "Fraud record lookup failed")
    fraud_record_doc = fraud_record if fraud_record is not None else {}
    results["fraud_record"] = {
        "record_id": fraud_record_doc.get("transaction_id") or fraud_record_doc.get("incident_id"),
        "risk_level": fraud_record_doc.get("risk_analysis", {}).get("risk_level"),
    }

    customer_fraud_records = fraud_repo.list_fraud_records_for_customer("CUST-001")
    _assert(len(customer_fraud_records) >= 1, "Expected at least one fraud record for customer")
    results["customer_fraud_records"] = {
        "count": len(customer_fraud_records),
    }

    loan_application = loan_repo.get_loan_application_by_id("LOAN-APP-001")
    _assert(loan_application is not None, "Loan application lookup failed")
    loan_application_doc = loan_application if loan_application is not None else {}
    results["loan_application"] = {
        "application_id": loan_application_doc.get("application_id"),
        "application_status": loan_application_doc.get("application_status"),
    }

    customer_loans = loan_repo.list_loan_applications_for_customer("CUST-001")
    _assert(len(customer_loans) >= 1, "Expected at least one loan application for customer")
    results["customer_loan_applications"] = {
        "count": len(customer_loans),
    }

    return {
        "status": "success",
        "checks_run": len(results),
        "results": results,
    }


if __name__ == "__main__":
    summary = run_smoke_tests()
    print(json.dumps(summary, indent=2))

# Made with Bob