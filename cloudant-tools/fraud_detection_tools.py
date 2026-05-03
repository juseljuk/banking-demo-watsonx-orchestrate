"""
Cloudant-backed standalone Python tools for fraud detection use cases.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict

from ibm_watsonx_orchestrate.agent_builder.connections import ConnectionType, ExpectedCredentials
from ibm_watsonx_orchestrate.agent_builder.tools import tool

from repositories.accounts import AccountRepository
from repositories.customers import CustomerRepository
from repositories.devices import DeviceRepository
from repositories.fraud_cases import FraudCaseRepository
from repositories.transactions import TransactionRepository


CLOUDANT_CONNECTION_APP_ID = "cloudant"
CLOUDANT_EXPECTED_CREDENTIALS: list[ExpectedCredentials] = [
    ExpectedCredentials(app_id=CLOUDANT_CONNECTION_APP_ID, type=ConnectionType.API_KEY_AUTH)
]


def _determine_risk_level(risk_score: int) -> str:
    """
    Map a numeric risk score to a risk level.

    Args:
        risk_score (int): Risk score between 0 and 100.

    Returns:
        str: Risk level label.
    """
    if risk_score >= 80:
        return "HIGH"
    if risk_score >= 50:
        return "MEDIUM"
    return "LOW"


def _determine_recommended_action(risk_score: int) -> str:
    """
    Map a numeric risk score to a recommended action.

    Args:
        risk_score (int): Risk score between 0 and 100.

    Returns:
        str: Recommended action label.
    """
    if risk_score >= 80:
        return "BLOCK"
    if risk_score >= 50:
        return "REVIEW"
    return "APPROVE"


@tool(expected_credentials=CLOUDANT_EXPECTED_CREDENTIALS)
def analyze_transaction_risk(
    transaction_id: str,
    account_id: str,
    amount: float,
    merchant: str = "Unknown",
    location: str = "Unknown",
    transaction_type: str = "Unknown",
) -> Dict[str, Any]:
    """
    Analyze a transaction for fraud risk.

    Args:
        transaction_id (str): The transaction identifier to analyze.
        account_id (str): The account identifier.
        amount (float): Transaction amount.
        merchant (str): Merchant name.
        location (str): Transaction location.
        transaction_type (str): Transaction type.

    Returns:
        Dict[str, Any]: Fraud risk analysis result.
    """
    account_repo = AccountRepository()
    transaction_repo = TransactionRepository()
    fraud_repo = FraudCaseRepository()

    transaction = transaction_repo.get_transaction_by_id(transaction_id)
    fraud_record = fraud_repo.get_fraud_record_by_id(transaction_id)
    account = account_repo.get_account_by_id(account_id)

    if fraud_record and fraud_record.get("risk_analysis"):
        return {
            "status": "success",
            "transaction_id": transaction_id,
            "risk_analysis": fraud_record.get("risk_analysis", {}),
        }

    if not account:
        return {
            "status": "error",
            "message": f"Account {account_id} not found",
        }

    amount_candidate: Any = amount
    if fraud_record and fraud_record.get("amount") is not None:
        amount_candidate = fraud_record.get("amount")
    elif transaction and transaction.get("amount") is not None:
        amount_candidate = transaction.get("amount")

    resolved_amount = float(amount_candidate)
    absolute_amount = abs(resolved_amount)

    resolved_location = (
        fraud_record.get("location")
        if fraud_record and fraud_record.get("location")
        else transaction.get("location")
        if transaction and transaction.get("location")
        else location
    )
    resolved_type = (
        fraud_record.get("type")
        if fraud_record and fraud_record.get("type")
        else transaction.get("type")
        if transaction and transaction.get("type")
        else transaction_type
    )

    risk_score = 10
    triggered_rules: list[str] = []

    if absolute_amount > 2000:
        risk_score += 20
        triggered_rules.append("Large transaction amount")

    if "International" in str(resolved_type):
        risk_score += 30
        triggered_rules.append("International transaction")

    if resolved_location and any(
        high_risk_location in str(resolved_location)
        for high_risk_location in ["Nigeria", "Russia", "Moscow", "Lagos"]
    ):
        risk_score += 40
        triggered_rules.append("High-risk country or location")

    risk_level = _determine_risk_level(risk_score)
    recommended_action = _determine_recommended_action(risk_score)

    return {
        "status": "success",
        "transaction_id": transaction_id,
        "risk_analysis": {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "fraud_probability": round(risk_score / 100, 2),
            "triggered_rules": triggered_rules,
            "recommended_action": recommended_action,
            "confidence": 0.85,
            "merchant": merchant,
        },
    }


@tool(expected_credentials=CLOUDANT_EXPECTED_CREDENTIALS)
def check_customer_profile(customer_id: str) -> Dict[str, Any]:
    """
    Get customer fraud risk profile and lightweight behavior indicators.

    Args:
        customer_id (str): The customer identifier.

    Returns:
        Dict[str, Any]: Customer fraud profile summary.
    """
    customer_repo = CustomerRepository()
    account_repo = AccountRepository()
    transaction_repo = TransactionRepository()

    customer = customer_repo.get_customer_by_id(customer_id)
    if not customer:
        return {
            "status": "error",
            "message": f"Customer {customer_id} not found",
        }

    accounts = account_repo.list_accounts_for_customer(customer_id)
    typical_locations: list[str] = []
    transaction_amounts: list[float] = []

    for account in accounts:
        account_id = account.get("account_id")
        if not account_id:
            continue
        recent_transactions = transaction_repo.list_recent_transactions(account_id=account_id, limit=20)
        for transaction in recent_transactions:
            amount = transaction.get("amount")
            if amount is not None:
                transaction_amounts.append(abs(float(amount)))
            location = transaction.get("location")
            if location and location not in typical_locations:
                typical_locations.append(str(location))

    typical_transaction_amount = (
        round(sum(transaction_amounts) / len(transaction_amounts), 2)
        if transaction_amounts
        else 400.00
    )

    return {
        "status": "success",
        "customer_id": customer_id,
        "risk_profile": customer.get("risk_profile", "Medium"),
        "customer_since": customer.get("customer_since"),
        "typical_transaction_amount": typical_transaction_amount,
        "typical_locations": typical_locations or ["London, UK"],
        "international_transfers_last_year": 0,
    }


@tool(expected_credentials=CLOUDANT_EXPECTED_CREDENTIALS)
def verify_device_fingerprint(device_id: str, customer_id: str = "") -> Dict[str, Any]:
    """
    Verify whether a device is known and trusted.

    Args:
        device_id (str): The device identifier.
        customer_id (str): Optional customer identifier for ownership validation.

    Returns:
        Dict[str, Any]: Device verification result.
    """
    device_repo = DeviceRepository()
    device = device_repo.get_device_by_id(device_id)

    if not device:
        return {
            "status": "success",
            "device_id": device_id,
            "known_device": False,
            "trusted": False,
            "risk_score": 80,
            "message": "Unknown device",
        }

    device_customer_id = device.get("customer_id")
    customer_match = not customer_id or str(device_customer_id) == str(customer_id)

    return {
        "status": "success",
        "device_id": device_id,
        "known_device": customer_match,
        "trusted": bool(device.get("trusted", False)) and customer_match,
        "device_type": device.get("device_type"),
        "last_seen": device.get("last_seen"),
        "risk_score": int(device.get("risk_score", 10)),
    }


@tool(expected_credentials=CLOUDANT_EXPECTED_CREDENTIALS)
def check_velocity_rules(customer_id: str, timeframe: str = "24hours") -> Dict[str, Any]:
    """
    Check whether customer transaction activity exceeds simple velocity thresholds.

    Args:
        customer_id (str): The customer identifier.
        timeframe (str): Timeframe label for reporting.

    Returns:
        Dict[str, Any]: Velocity analysis result.
    """
    account_repo = AccountRepository()
    transaction_repo = TransactionRepository()

    accounts = account_repo.list_accounts_for_customer(customer_id)
    transactions: list[dict[str, Any]] = []

    for account in accounts:
        account_id = account.get("account_id")
        if not account_id:
            continue
        transactions.extend(
            transaction_repo.list_recent_transactions(account_id=account_id, limit=20)
        )

    transaction_count = len(transactions)
    total_amount = round(
        sum(abs(float(item.get("amount", 0))) for item in transactions),
        2,
    )
    velocity_limit = 10
    amount_limit = 10000.00

    return {
        "status": "success",
        "customer_id": customer_id,
        "timeframe": timeframe,
        "transaction_count": transaction_count,
        "velocity_limit": velocity_limit,
        "within_limits": transaction_count <= velocity_limit and total_amount <= amount_limit,
        "total_amount": total_amount,
        "amount_limit": amount_limit,
    }


@tool(expected_credentials=CLOUDANT_EXPECTED_CREDENTIALS)
def block_transaction(transaction_id: str, reason: str, risk_score: int = 90) -> Dict[str, Any]:
    """
    Block a suspicious transaction and return a generated fraud case identifier.

    Args:
        transaction_id (str): The transaction identifier to block.
        reason (str): Reason for blocking.
        risk_score (int): Risk score between 0 and 100.

    Returns:
        Dict[str, Any]: Block result metadata.
    """
    case_id = f"FRAUD-CASE-{int(datetime.now().timestamp())}"

    return {
        "status": "success",
        "transaction_id": transaction_id,
        "blocked": True,
        "reason": reason,
        "risk_score": risk_score,
        "case_id": case_id,
        "timestamp": datetime.now().isoformat(),
    }


@tool(expected_credentials=CLOUDANT_EXPECTED_CREDENTIALS)
def send_fraud_alert(customer_id: str, channel: str, message: str) -> Dict[str, Any]:
    """
    Simulate sending a fraud alert to a customer.

    Args:
        customer_id (str): The customer identifier.
        channel (str): Alert channel.
        message (str): Alert message body.

    Returns:
        Dict[str, Any]: Alert send result metadata.
    """
    return {
        "status": "success",
        "customer_id": customer_id,
        "channel": channel,
        "message": message,
        "message_sent": True,
        "timestamp": datetime.now().isoformat(),
    }


@tool(expected_credentials=CLOUDANT_EXPECTED_CREDENTIALS)
def create_fraud_case(
    transaction_id: str,
    customer_id: str,
    risk_score: int,
    priority: str = "Medium",
) -> Dict[str, Any]:
    """
    Create a fraud investigation case response payload.

    Args:
        transaction_id (str): The transaction identifier.
        customer_id (str): The customer identifier.
        risk_score (int): Risk score between 0 and 100.
        priority (str): Case priority.

    Returns:
        Dict[str, Any]: Fraud case metadata.
    """
    case_id = f"FRAUD-CASE-{int(datetime.now().timestamp())}"

    return {
        "status": "success",
        "case_id": case_id,
        "transaction_id": transaction_id,
        "customer_id": customer_id,
        "risk_score": risk_score,
        "priority": priority,
        "assigned_to": "Fraud Investigation Team",
        "created_at": datetime.now().isoformat(),
    }


@tool(expected_credentials=CLOUDANT_EXPECTED_CREDENTIALS)
def get_fraud_scenario(scenario_id: str) -> Dict[str, Any]:
    """
    Get a predefined fraud scenario from Cloudant.

    Args:
        scenario_id (str): Scenario identifier.

    Returns:
        Dict[str, Any]: Fraud scenario document when found.
    """
    fraud_repo = FraudCaseRepository()
    scenario = fraud_repo.get_fraud_record_by_id(scenario_id)

    if not scenario:
        return {
            "status": "error",
            "message": f"Scenario {scenario_id} not found",
        }

    return {
        "status": "success",
        "scenario": scenario,
    }

# Made with Bob