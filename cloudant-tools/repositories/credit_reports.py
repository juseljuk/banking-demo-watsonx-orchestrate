"""
Credit report repository helpers for Cloudant-backed access.
"""

from __future__ import annotations

from typing import Any

from common.config import CloudantSettings
from common.config import get_cloudant_settings
from repositories.base import BaseCloudantRepository


class CreditReportRepository(BaseCloudantRepository):
    """
    Repository for credit report records stored in Cloudant.
    """

    def __init__(self, settings: CloudantSettings | None = None) -> None:
        resolved_settings = settings or get_cloudant_settings()
        super().__init__(resolved_settings.databases["credit"], settings=resolved_settings)

    def get_credit_report_by_customer_id(self, customer_id: str) -> dict[str, Any] | None:
        """
        Fetch a credit report by customer identifier.

        Args:
            customer_id (str): Customer identifier.

        Returns:
            dict[str, Any] | None: Credit report document if found.
        """
        return self.get_document(f"CREDIT-{customer_id}")

# Made with Bob