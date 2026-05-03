"""
Loan application repository helpers for Cloudant-backed access.
"""

from __future__ import annotations

from typing import Any

from common.config import CloudantSettings
from common.config import get_cloudant_settings
from repositories.base import BaseCloudantRepository


class LoanApplicationRepository(BaseCloudantRepository):
    """
    Repository for loan application records stored in Cloudant.
    """

    def __init__(self, settings: CloudantSettings | None = None) -> None:
        resolved_settings = settings or get_cloudant_settings()
        super().__init__(resolved_settings.databases["loans"], settings=resolved_settings)

    def get_loan_application_by_id(self, application_id: str) -> dict[str, Any] | None:
        """
        Fetch a loan application by identifier.

        Args:
            application_id (str): Loan application identifier.

        Returns:
            dict[str, Any] | None: Loan application document if found.
        """
        return self.get_document(application_id)

    def list_loan_applications_for_customer(self, customer_id: str) -> list[dict[str, Any]]:
        """
        List loan applications for a customer.

        Args:
            customer_id (str): Customer identifier.

        Returns:
            list[dict[str, Any]]: Matching loan application documents.
        """
        return self.find_by_selector(
            selector={
                "type": "loan_application",
                "customer_id": customer_id,
            },
            limit=20,
        )

# Made with Bob