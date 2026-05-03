"""
Account repository helpers for Cloudant-backed access.
"""

from __future__ import annotations

from typing import Any

from common.config import CloudantSettings
from common.config import get_cloudant_settings
from repositories.base import BaseCloudantRepository


class AccountRepository(BaseCloudantRepository):
    """
    Repository for account records stored in Cloudant.
    """

    def __init__(self, settings: CloudantSettings | None = None) -> None:
        resolved_settings = settings or get_cloudant_settings()
        super().__init__(resolved_settings.databases["accounts"], settings=resolved_settings)

    def get_account_by_id(self, account_id: str) -> dict[str, Any] | None:
        """
        Fetch an account by identifier.

        Args:
            account_id (str): Account identifier.

        Returns:
            dict[str, Any] | None: Account document if found.
        """
        return self.get_document(account_id)

    def list_accounts_for_customer(self, customer_id: str) -> list[dict[str, Any]]:
        """
        List accounts belonging to a customer.

        Args:
            customer_id (str): Customer identifier.

        Returns:
            list[dict[str, Any]]: Matching account documents.
        """
        return self.find_by_selector(
            selector={
                "type": "account",
                "customer_id": customer_id,
            },
            limit=20,
        )

    def list_credit_card_accounts_for_customer(self, customer_id: str) -> list[dict[str, Any]]:
        """
        List credit card accounts for a customer.

        Args:
            customer_id (str): Customer identifier.

        Returns:
            list[dict[str, Any]]: Matching credit card account documents.
        """
        return self.find_by_selector(
            selector={
                "type": "account",
                "customer_id": customer_id,
                "account_type": "Credit Card",
            },
            limit=10,
        )

# Made with Bob
