"""
Transform local demo JSON files into Cloudant document shapes.
"""

from __future__ import annotations

from typing import Any


def transform_customers(source: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Convert customer map into Cloudant customer documents.

    Args:
        source (dict[str, Any]): Raw customer JSON keyed by customer ID.

    Returns:
        list[dict[str, Any]]: Cloudant-ready customer documents.
    """
    documents: list[dict[str, Any]] = []

    for customer_id, customer in source.items():
        document = {
            "_id": customer_id,
            "type": "customer",
            **customer,
        }
        documents.append(document)

    return documents


def transform_accounts(source: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Convert account map into Cloudant account documents.

    Args:
        source (dict[str, Any]): Raw account JSON keyed by account ID.

    Returns:
        list[dict[str, Any]]: Cloudant-ready account documents.
    """
    documents: list[dict[str, Any]] = []

    for account_id, account in source.items():
        document = {
            "_id": account_id,
            "type": "account",
            **account,
        }
        documents.append(document)

    return documents


def transform_transactions(source: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Convert transaction list into Cloudant transaction documents.

    Args:
        source (list[dict[str, Any]]): Raw transaction list.

    Returns:
        list[dict[str, Any]]: Cloudant-ready transaction documents.
    """
    documents: list[dict[str, Any]] = []

    for transaction in source:
        transaction_id = str(transaction["transaction_id"])
        document = {
            "_id": transaction_id,
            **transaction,
            "type": "transaction",
            "transaction_type": transaction.get("type"),
        }
        documents.append(document)

    return documents


def transform_credit_reports(source: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Convert credit report map into Cloudant credit report documents.

    Args:
        source (dict[str, Any]): Raw credit report JSON keyed by customer ID.

    Returns:
        list[dict[str, Any]]: Cloudant-ready credit report documents.
    """
    documents: list[dict[str, Any]] = []

    for customer_id, report in source.items():
        document = {
            "_id": f"CREDIT-{customer_id}",
            "type": "credit_report",
            **report,
        }
        documents.append(document)

    return documents


def transform_devices(source: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Convert device map into Cloudant device documents.

    Args:
        source (dict[str, Any]): Raw device JSON keyed by device ID.

    Returns:
        list[dict[str, Any]]: Cloudant-ready device documents.
    """
    documents: list[dict[str, Any]] = []

    for device_id, device in source.items():
        document = {
            "_id": device_id,
            "type": "device",
            **device,
        }
        documents.append(document)

    return documents


def transform_fraud_scenarios(source: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Convert fraud scenario map into Cloudant fraud documents.

    Args:
        source (dict[str, Any]): Raw fraud scenario JSON keyed by scenario ID.

    Returns:
        list[dict[str, Any]]: Cloudant-ready fraud scenario documents.
    """
    documents: list[dict[str, Any]] = []

    for scenario_id, scenario in source.items():
        document_type = "fraud_incident" if "incident_id" in scenario else "fraud_scenario"
        document = {
            "_id": scenario_id,
            "type": document_type,
            **scenario,
        }
        documents.append(document)

    return documents


def transform_loan_applications(source: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Convert loan application map into Cloudant loan documents.

    Args:
        source (dict[str, Any]): Raw loan application JSON keyed by application ID.

    Returns:
        list[dict[str, Any]]: Cloudant-ready loan application documents.
    """
    documents: list[dict[str, Any]] = []

    for application_id, application in source.items():
        document = {
            "_id": application_id,
            "type": "loan_application",
            **application,
        }
        documents.append(document)

    return documents

# Made with Bob
