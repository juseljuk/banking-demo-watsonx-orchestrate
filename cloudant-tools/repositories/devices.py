"""
Device repository helpers for Cloudant-backed access.
"""

from __future__ import annotations

from typing import Any

from common.config import CloudantSettings
from common.config import get_cloudant_settings
from repositories.base import BaseCloudantRepository


class DeviceRepository(BaseCloudantRepository):
    """
    Repository for device records stored in Cloudant.
    """

    def __init__(self, settings: CloudantSettings | None = None) -> None:
        resolved_settings = settings or get_cloudant_settings()
        super().__init__(resolved_settings.databases["devices"], settings=resolved_settings)

    def get_device_by_id(self, device_id: str) -> dict[str, Any] | None:
        """
        Fetch a device by identifier.

        Args:
            device_id (str): Device identifier.

        Returns:
            dict[str, Any] | None: Device document if found.
        """
        return self.get_document(device_id)

    def list_devices_for_customer(self, customer_id: str) -> list[dict[str, Any]]:
        """
        List devices belonging to a customer.

        Args:
            customer_id (str): Customer identifier.

        Returns:
            list[dict[str, Any]]: Matching device documents.
        """
        return self.find_by_selector(
            selector={
                "type": "device",
                "customer_id": customer_id,
            },
            limit=20,
        )

# Made with Bob