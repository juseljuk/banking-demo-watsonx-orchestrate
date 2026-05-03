"""
Transaction repository helpers for Cloudant-backed access.
"""

from __future__ import annotations

from typing import Any

from common.config import CloudantSettings
from common.config import get_cloudant_settings
from repositories.base import BaseCloudantRepository


class TransactionRepository(BaseCloudantRepository):
    """
    Repository for transaction and transfer event records stored in Cloudant.
    """

    def __init__(self, settings: CloudantSettings | None = None) -> None:
        resolved_settings = settings or get_cloudant_settings()
        super().__init__(resolved_settings.databases["transactions"], settings=resolved_settings)

    def get_transaction_by_id(self, transaction_id: str) -> dict[str, Any] | None:
        """
        Fetch a transaction by identifier.

        Args:
            transaction_id (str): Transaction identifier.

        Returns:
            dict[str, Any] | None: Transaction document if found.
        """
        return self.get_document(transaction_id)

    def list_recent_transactions(
        self,
        account_id: str,
        limit: int = 10,
        posted_only: bool = True,
    ) -> list[dict[str, Any]]:
        """
        List recent transactions for an account.

        Args:
            account_id (str): Account identifier.
            limit (int): Maximum number of results.
            posted_only (bool): Whether to restrict to posted transactions.

        Returns:
            list[dict[str, Any]]: Matching transaction documents.
        """
        selector: dict[str, Any] = {
            "type": "transaction",
            "account_id": account_id,
        }

        if posted_only:
            selector["status"] = "Posted"

        return self.find_by_selector(
            selector=selector,
            limit=limit,
            sort=[{"date": "desc"}, {"time": "desc"}],
        )

    def list_pending_transactions(self, account_id: str) -> list[dict[str, Any]]:
        """
        List pending transactions for an account.

        Args:
            account_id (str): Account identifier.

        Returns:
            list[dict[str, Any]]: Pending transaction documents.
        """
        return self.find_by_selector(
            selector={
                "type": "transaction",
                "account_id": account_id,
                "status": "Pending",
            },
            limit=50,
            sort=[{"date": "desc"}, {"time": "desc"}],
        )

# Made with Bob
