"""
Fraud scenario and case repository helpers for Cloudant-backed access.
"""

from __future__ import annotations

from typing import Any

from common.config import CloudantSettings
from common.config import get_cloudant_settings
from repositories.base import BaseCloudantRepository


class FraudCaseRepository(BaseCloudantRepository):
    """
    Repository for fraud scenarios and cases stored in Cloudant.
    """

    def __init__(self, settings: CloudantSettings | None = None) -> None:
        resolved_settings = settings or get_cloudant_settings()
        super().__init__(resolved_settings.databases["fraud"], settings=resolved_settings)

    def get_fraud_record_by_id(self, record_id: str) -> dict[str, Any] | None:
        """
        Fetch a fraud scenario or case by identifier.

        Args:
            record_id (str): Fraud record identifier.

        Returns:
            dict[str, Any] | None: Fraud record document if found.
        """
        return self.get_document(record_id)

    def list_fraud_records_for_customer(self, customer_id: str) -> list[dict[str, Any]]:
        """
        List fraud records for a customer.

        Args:
            customer_id (str): Customer identifier.

        Returns:
            list[dict[str, Any]]: Matching fraud documents.
        """
        return self.find_by_selector(
            selector={
                "customer_id": customer_id,
            },
            limit=50,
        )

# Made with Bob