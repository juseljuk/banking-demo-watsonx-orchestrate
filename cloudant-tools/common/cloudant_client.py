"""
Cloudant client helpers for standalone Python tools.
"""

from __future__ import annotations

from typing import Any

from ibmcloudant.cloudant_v1 import CloudantV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

from common.config import (
    DEFAULT_CONNECTION_APP_ID,
    CloudantSettings,
    get_cloudant_settings,
)


def create_cloudant_client(
    settings: CloudantSettings | None = None,
    app_id: str = DEFAULT_CONNECTION_APP_ID,
) -> CloudantV1:
    """
    Create an authenticated IBM Cloudant client.

    Args:
        settings (CloudantSettings | None): Optional preloaded settings.
        app_id (str): watsonx Orchestrate connection app id for runtime lookup.

    Returns:
        CloudantV1: Authenticated Cloudant client instance.
    """
    resolved_settings = settings or get_cloudant_settings(app_id=app_id)

    authenticator = IAMAuthenticator(
        resolved_settings.api_key,
        url=resolved_settings.iam_url,
    )
    client = CloudantV1(authenticator=authenticator)
    client.set_service_url(resolved_settings.url)

    return client


def verify_cloudant_connection() -> dict[str, Any]:
    """
    Validate that the configured Cloudant service is reachable.

    Returns:
        dict[str, Any]: Basic connection metadata from the Cloudant instance.
    """
    settings = get_cloudant_settings(app_id=DEFAULT_CONNECTION_APP_ID)
    client = create_cloudant_client(settings=settings, app_id=DEFAULT_CONNECTION_APP_ID)
    response = client.get_server_information().get_result()

    return {
        "status": "success",
        "credential_source": settings.credential_source,
        "connection_prefix": settings.connection_prefix,
        "vendor": response.get("vendor", {}),
        "version": response.get("version"),
        "features": response.get("features", []),
    }


def list_configured_databases() -> dict[str, Any]:
    """
    Return the logical database configuration defined for this project.

    Returns:
        dict[str, Any]: Configured Cloudant database names by domain.
    """
    settings = get_cloudant_settings(app_id=DEFAULT_CONNECTION_APP_ID)

    return {
        "status": "success",
        "url": settings.url,
        "credential_source": settings.credential_source,
        "connection_prefix": settings.connection_prefix,
        "databases": settings.databases,
    }

# Made with Bob
