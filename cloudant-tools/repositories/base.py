"""
Base repository helpers for Cloudant-backed data access.
"""

from __future__ import annotations

from typing import Any

from common.cloudant_client import create_cloudant_client
from common.config import (
    DEFAULT_CONNECTION_APP_ID,
    CloudantSettings,
    get_cloudant_settings,
)


class BaseCloudantRepository:
    """
    Shared repository base class for Cloudant document access.
    """

    def __init__(
        self,
        database_name: str,
        settings: CloudantSettings | None = None,
        app_id: str = DEFAULT_CONNECTION_APP_ID,
    ) -> None:
        self.app_id = app_id
        self.settings = settings or get_cloudant_settings(app_id=app_id)
        self.client = create_cloudant_client(self.settings, app_id=app_id)
        self.database_name = database_name

    def get_document(self, document_id: str) -> dict[str, Any] | None:
        """
        Fetch a single document by ID.

        Args:
            document_id (str): Cloudant document identifier.

        Returns:
            dict[str, Any] | None: Document body if found, else None.
        """
        try:
            response = self.client.get_document(
                db=self.database_name,
                doc_id=document_id,
            ).get_result()
            return dict(response)
        except Exception:
            return None

    def upsert_document(self, document: dict[str, Any]) -> dict[str, Any]:
        """
        Create or update a document in Cloudant.

        Args:
            document (dict[str, Any]): Document to persist. Must include `_id`.

        Returns:
            dict[str, Any]: Result metadata from Cloudant.
        """
        if "_id" not in document:
            raise ValueError("Document must include '_id' for Cloudant persistence")

        existing = self.get_document(document["_id"])
        payload = dict(document)

        if existing and "_rev" in existing and "_rev" not in payload:
            payload["_rev"] = existing["_rev"]

        response = self.client.post_document(
            db=self.database_name,
            document=payload,
        ).get_result()

        return dict(response)

    def find_by_selector(
        self,
        selector: dict[str, Any],
        limit: int = 50,
        sort: list[dict[str, str]] | None = None,
        fields: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Query documents using a Mango selector.

        Args:
            selector (dict[str, Any]): Mango selector.
            limit (int): Maximum number of results.
            sort (list[dict[str, str]] | None): Optional sort specification.
            fields (list[str] | None): Optional projected fields.

        Returns:
            list[dict[str, Any]]: Matching documents.
        """
        payload: dict[str, Any] = {
            "selector": selector,
            "limit": limit,
        }

        if sort:
            payload["sort"] = sort

        if fields:
            payload["fields"] = fields

        response = self.client.post_find(
            db=self.database_name,
            selector=payload["selector"],
            limit=payload["limit"],
            sort=payload.get("sort"),
            fields=payload.get("fields"),
        ).get_result()

        return [dict(doc) for doc in response.get("docs", [])]

# Made with Bob
