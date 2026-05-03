"""
Bootstrap Cloudant databases, create indexes, and seed them from local demo JSON files.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

from common.cloudant_client import create_cloudant_client
from common.config import get_cloudant_settings
from scripts.seed_transforms import transform_accounts
from scripts.seed_transforms import transform_credit_reports
from scripts.seed_transforms import transform_customers
from scripts.seed_transforms import transform_devices
from scripts.seed_transforms import transform_fraud_scenarios
from scripts.seed_transforms import transform_loan_applications
from scripts.seed_transforms import transform_transactions


ROOT_DATA_DIR = Path(__file__).resolve().parents[2] / "data"


TransformFunction = Callable[[Any], list[dict[str, Any]]]


SEED_PLAN: list[dict[str, Any]] = [
    {
        "database_key": "customers",
        "filename": "customers.json",
        "transform": transform_customers,
    },
    {
        "database_key": "accounts",
        "filename": "accounts.json",
        "transform": transform_accounts,
    },
    {
        "database_key": "transactions",
        "filename": "transactions.json",
        "transform": transform_transactions,
    },
    {
        "database_key": "credit",
        "filename": "credit_reports.json",
        "transform": transform_credit_reports,
    },
    {
        "database_key": "devices",
        "filename": "devices.json",
        "transform": transform_devices,
    },
    {
        "database_key": "fraud",
        "filename": "fraud_scenarios.json",
        "transform": transform_fraud_scenarios,
    },
    {
        "database_key": "loans",
        "filename": "loan_applications.json",
        "transform": transform_loan_applications,
    },
]


INDEX_PLAN: dict[str, list[dict[str, Any]]] = {
    "customers": [
        {
            "name": "idx-customers-type-email",
            "fields": ["type", "email"],
        },
    ],
    "accounts": [
        {
            "name": "idx-accounts-type-customer",
            "fields": ["type", "customer_id"],
        },
        {
            "name": "idx-accounts-type-customer-accounttype",
            "fields": ["type", "customer_id", "account_type"],
        },
    ],
    "transactions": [
        {
            "name": "idx-transactions-type-account-status-date-time",
            "fields": ["type", "account_id", "status", "date", "time"],
        },
        {
            "name": "idx-transactions-type-account-date-time",
            "fields": ["type", "account_id", "date", "time"],
        },
    ],
    "devices": [
        {
            "name": "idx-devices-type-customer",
            "fields": ["type", "customer_id"],
        },
    ],
    "fraud": [
        {
            "name": "idx-fraud-type-customer",
            "fields": ["type", "customer_id"],
        },
    ],
    "loans": [
        {
            "name": "idx-loans-type-customer",
            "fields": ["type", "customer_id"],
        },
    ],
}


def load_json_file(path: Path) -> Any:
    """
    Load JSON data from disk.

    Args:
        path (Path): Path to JSON file.

    Returns:
        Any: Parsed JSON payload.
    """
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def ensure_database_exists(database_name: str) -> None:
    """
    Ensure a Cloudant database exists.

    Args:
        database_name (str): Target database name.
    """
    client = create_cloudant_client()

    try:
        existing_databases = client.get_all_dbs().get_result()
        if database_name in existing_databases:
            return
    except Exception:
        pass

    try:
        client.put_database(db=database_name).get_result()
    except Exception as error:
        status_code = getattr(error, "code", None) or getattr(error, "status_code", None)
        message = str(error)

        if status_code == 412 or "already exists" in message.lower():
            return

        raise RuntimeError(f"Failed to create database '{database_name}': {message}") from error


def ensure_indexes(database_name: str, database_key: str) -> list[str]:
    """
    Create Mango indexes for the target database.

    Args:
        database_name (str): Physical Cloudant database name.
        database_key (str): Logical project database key.

    Returns:
        list[str]: Names of indexes attempted.
    """
    client = create_cloudant_client()
    created_indexes: list[str] = []

    for index_definition in INDEX_PLAN.get(database_key, []):
        index_name = str(index_definition["name"])
        fields = list(index_definition["fields"])
        client.post_index(
            db=database_name,
            index={"fields": fields},
            ddoc=index_name,
            name=index_name,
            type="json",
        ).get_result()
        created_indexes.append(index_name)

    return created_indexes


def seed_database(database_name: str, documents: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Seed a database with transformed documents.

    Args:
        database_name (str): Cloudant database name.
        documents (list[dict[str, Any]]): Documents to upsert.

    Returns:
        dict[str, Any]: Seeding summary.
    """
    client = create_cloudant_client()
    inserted = 0

    for document in documents:
        try:
            existing = client.get_document(db=database_name, doc_id=document["_id"]).get_result()
            if isinstance(existing, dict) and "_rev" in existing:
                document = {**document, "_rev": existing["_rev"]}
        except Exception:
            pass

        client.post_document(db=database_name, document=document).get_result()
        inserted += 1

    return {
        "database": database_name,
        "documents_processed": inserted,
    }


def bootstrap_and_seed() -> list[dict[str, Any]]:
    """
    Create databases, ensure indexes, and seed them from the local demo data directory.

    Returns:
        list[dict[str, Any]]: Per-database seeding summary.
    """
    settings = get_cloudant_settings()
    summary: list[dict[str, Any]] = []

    for item in SEED_PLAN:
        database_key = item["database_key"]
        database_name = settings.databases[database_key]
        source_path = ROOT_DATA_DIR / item["filename"]
        raw_data = load_json_file(source_path)
        documents = item["transform"](raw_data)

        ensure_database_exists(database_name)
        indexes = ensure_indexes(database_name, database_key)
        result = seed_database(database_name, documents)
        result["indexes_ensured"] = indexes
        summary.append(result)

    return summary


if __name__ == "__main__":
    results = bootstrap_and_seed()
    print(json.dumps(results, indent=2))

# Made with Bob
