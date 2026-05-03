"""
Customer repository helpers for Cloudant-backed access.
"""

from __future__ import annotations

from typing import Any

from common.config import CloudantSettings
from common.config import get_cloudant_settings
from repositories.base import BaseCloudantRepository


class CustomerRepository(BaseCloudantRepository):
    """
    Repository for customer records stored in Cloudant.
    """

    def __init__(self, settings: CloudantSettings | None = None) -> None:
        resolved_settings = settings or get_cloudant_settings()
        super().__init__(resolved_settings.databases["customers"], settings=resolved_settings)

    @classmethod
    def from_settings(cls, settings: CloudantSettings) -> "CustomerRepository":
        """
        Create repository from shared settings object.

        Args:
            settings (CloudantSettings): Shared Cloudant settings.

        Returns:
            CustomerRepository: Configured repository instance.
        """
        return cls(settings=settings)

    def get_customer_by_id(self, customer_id: str) -> dict[str, Any] | None:
        """
        Fetch a customer by identifier.

        Args:
            customer_id (str): Customer identifier.

        Returns:
            dict[str, Any] | None: Customer document if found.
        """
        return self.get_document(customer_id)

    def find_customer_by_email(self, email: str) -> dict[str, Any] | None:
        """
        Find a customer document by email address.

        Args:
            email (str): Customer email address.

        Returns:
            dict[str, Any] | None: Matching customer document if found.
        """
        results = self.find_by_selector(
            selector={
                "type": "customer",
                "email": email,
            },
            limit=1,
        )
        return results[0] if results else None

    def verify_customer_pin(self, customer_id: str, pin: str) -> bool:
        """
        Verify demo PIN for a customer.

        Args:
            customer_id (str): Customer identifier.
            pin (str): Demo PIN value.

        Returns:
            bool: True when the PIN matches.
        """
        normalized_customer_id = str(customer_id).strip()
        normalized_pin = str(pin).strip()

        customer = self.get_customer_by_id(normalized_customer_id)
        if not customer:
            return False

        stored_pin = str(customer.get("pin", "")).strip()
        return stored_pin == normalized_pin

# Made with Bob
