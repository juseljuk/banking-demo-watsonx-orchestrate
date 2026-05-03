"""
Cloudant-backed standalone Python tools for core banking use cases.
"""

from __future__ import annotations

from typing import Any, Dict

from ibm_watsonx_orchestrate.agent_builder.connections import ConnectionType, ExpectedCredentials
from ibm_watsonx_orchestrate.agent_builder.tools import tool

from common.config import get_cloudant_settings
from repositories.accounts import AccountRepository
from repositories.customers import CustomerRepository
from repositories.transactions import TransactionRepository


CLOUDANT_CONNECTION_APP_ID = "cloudant"
CLOUDANT_EXPECTED_CREDENTIALS: list[ExpectedCredentials] = [
    ExpectedCredentials(app_id=CLOUDANT_CONNECTION_APP_ID, type=ConnectionType.API_KEY_AUTH)
]


@tool(expected_credentials=CLOUDANT_EXPECTED_CREDENTIALS)
def authenticate_customer(customer_id: str, pin: str) -> Dict[str, Any]:
    """
    Authenticate a customer using demo customer ID and PIN.

    Args:
        customer_id (str): The customer identifier (e.g., CUST-001)
        pin (str): The customer's 4-digit demo PIN

    Returns:
        Dict[str, Any]: Authentication result including:
            - status: Operation status
            - customer_id: Customer identifier
            - customer_name: Full customer name
            - message: Authentication message
    """
    normalized_customer_id = str(customer_id).strip()
    normalized_pin = str(pin).strip()

    settings = get_cloudant_settings()
    customer_repo = CustomerRepository(settings=settings)

    raw_lookup_error = None
    raw_lookup_customer = None
    try:
        raw_lookup_customer = customer_repo.client.get_document(
            db=customer_repo.database_name,
            doc_id=normalized_customer_id,
        ).get_result()
    except Exception as exc:
        raw_lookup_error = str(exc)

    customer = customer_repo.get_customer_by_id(normalized_customer_id)
    pin_verified = customer_repo.verify_customer_pin(normalized_customer_id, normalized_pin)

    if not customer or not pin_verified:
        return {
            "status": "error",
            "message": "Invalid customer ID or PIN",
            "debug": {
                "normalized_customer_id": normalized_customer_id,
                "normalized_pin_length": len(normalized_pin),
                "customer_found": customer is not None,
                "pin_verified": pin_verified,
                "credential_source": settings.credential_source,
                "customers_db": settings.databases.get("customers"),
                "raw_lookup_found": raw_lookup_customer is not None,
                "raw_lookup_error": raw_lookup_error,
            },
        }

    return {
        "status": "success",
        "customer_id": normalized_customer_id,
        "customer_name": f"{customer.get('first_name', '')} {customer.get('last_name', '')}".strip(),
        "message": f"Welcome back, {customer.get('first_name', 'customer')}!",
    }


@tool(expected_credentials=CLOUDANT_EXPECTED_CREDENTIALS)
def get_customer_accounts(customer_id: str) -> Dict[str, Any]:
    """
    Get all accounts for a customer.

    Args:
        customer_id (str): The customer identifier (e.g., CUST-001)

    Returns:
        Dict[str, Any]: Customer account list and count.
    """
    account_repo = AccountRepository()
    accounts = account_repo.list_accounts_for_customer(customer_id)

    return {
        "status": "success",
        "customer_id": customer_id,
        "accounts": accounts,
        "count": len(accounts),
    }


@tool(expected_credentials=CLOUDANT_EXPECTED_CREDENTIALS)
def check_account_balance(account_id: str) -> Dict[str, Any]:
    """
    Check the current balance of an account.

    Args:
        account_id (str): The account identifier (e.g., CUR-001-1234)

    Returns:
        Dict[str, Any]: Account balance details.
    """
    account_repo = AccountRepository()
    account = account_repo.get_account_by_id(account_id)

    if not account:
        return {
            "status": "error",
            "message": f"Account {account_id} not found",
        }

    return {
        "status": "success",
        "account_id": account.get("account_id"),
        "account_type": account.get("account_type"),
        "account_name": account.get("account_name"),
        "current_balance": account.get("current_balance"),
        "available_balance": account.get("available_balance"),
        "currency": account.get("currency"),
        "status_text": account.get("status"),
    }


@tool(expected_credentials=CLOUDANT_EXPECTED_CREDENTIALS)
def get_recent_transactions(account_id: str, limit: int = 10) -> Dict[str, Any]:
    """
    Retrieve recent posted transactions for an account.

    Args:
        account_id (str): The account identifier (e.g., CUR-001-1234)
        limit (int): Number of transactions to retrieve (default: 10)

    Returns:
        Dict[str, Any]: Recent transaction list and count.
    """
    transaction_repo = TransactionRepository()
    transactions = transaction_repo.list_recent_transactions(
        account_id=account_id,
        limit=min(max(limit, 1), 50),
        posted_only=True,
    )

    return {
        "status": "success",
        "account_id": account_id,
        "transactions": transactions,
        "count": len(transactions),
    }


@tool(expected_credentials=CLOUDANT_EXPECTED_CREDENTIALS)
def check_pending_deposits(account_id: str) -> Dict[str, Any]:
    """
    Check pending deposits or other pending transactions for an account.

    Args:
        account_id (str): The account identifier (e.g., CUR-001-1234)

    Returns:
        Dict[str, Any]: Pending transaction list and total amount.
    """
    transaction_repo = TransactionRepository()
    pending_transactions = transaction_repo.list_pending_transactions(account_id)

    return {
        "status": "success",
        "account_id": account_id,
        "pending_deposits": pending_transactions,
        "count": len(pending_transactions),
        "total_amount": round(sum(float(item.get("amount", 0)) for item in pending_transactions), 2),
    }


# Made with Bob