"""
Configuration helpers for Cloudant-backed standalone Python tools.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict

from dotenv import load_dotenv

try:
    from ibm_watsonx_orchestrate.run import connections as wxo_connections
except Exception:  # pragma: no cover - local development fallback when WXO runtime is absent
    wxo_connections = None


ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
EXAMPLE_ENV_PATH = Path(__file__).resolve().parent.parent / ".env.example"

DEFAULT_CONNECTION_PREFIX = "CLOUDANT_CONN"
DEFAULT_IAM_URL = "https://iam.cloud.ibm.com/identity/token"
DEFAULT_CONNECTION_APP_ID = "cloudant"


@dataclass(frozen=True)
class CloudantSettings:
    """
    Configuration values required to connect to IBM Cloudant.

    Attributes:
        url (str): Cloudant service URL.
        api_key (str): Cloudant IAM API key.
        iam_url (str): IAM token URL.
        databases (Dict[str, str]): Logical database names keyed by domain.
        credential_source (str): Source of credentials, for example `wxo_runtime_connection`,
            `wxo_connection_env`, or `local_env`.
        connection_prefix (str): Prefix used for watsonx Orchestrate injected environment variables.
    """

    url: str
    api_key: str
    iam_url: str
    databases: Dict[str, str]
    credential_source: str
    connection_prefix: str


def load_environment() -> None:
    """
    Load local environment variables from [`cloudant-tools/.env`](cloudant-tools/.env)
    if present, otherwise leave the current process environment unchanged.
    """
    if ENV_PATH.exists():
        load_dotenv(ENV_PATH)
    elif EXAMPLE_ENV_PATH.exists():
        load_dotenv(EXAMPLE_ENV_PATH, override=False)


def _get_first_env(*names: str) -> str:
    """
    Return the first non-empty environment variable value.

    Args:
        *names (str): Candidate environment variable names.

    Returns:
        str: First non-empty value, otherwise empty string.
    """
    for name in names:
        value = os.getenv(name, "").strip()
        if value:
            return value
    return ""


def get_connection_prefix() -> str:
    """
    Resolve the watsonx Orchestrate connection prefix used for injected environment variables.

    Returns:
        str: Environment variable prefix for injected connection values.
    """
    load_environment()
    return _get_first_env("CLOUDANT_CONNECTION_PREFIX", "WXO_CLOUDANT_CONNECTION_PREFIX") or DEFAULT_CONNECTION_PREFIX


def get_wxo_api_key_connection(
    app_id: str = DEFAULT_CONNECTION_APP_ID,
) -> tuple[str, str] | None:
    """
    Resolve a watsonx Orchestrate API key connection at runtime when available.

    Args:
        app_id (str): watsonx Orchestrate connection app id.

    Returns:
        tuple[str, str] | None: Tuple of `(url, api_key)`, or None when not available.
    """
    if wxo_connections is None:
        return None

    try:
        connection_values = wxo_connections.api_key_auth(app_id)
    except Exception:
        return None

    url = str(getattr(connection_values, "url", "") or "").strip()
    api_key = str(getattr(connection_values, "api_key", "") or "").strip()

    if not url or not api_key:
        return None

    return url, api_key


def get_cloudant_settings(
    app_id: str = DEFAULT_CONNECTION_APP_ID,
) -> CloudantSettings:
    """
    Build Cloudant settings from either a watsonx Orchestrate API key connection
    retrieved via [`connections.api_key_auth()`](connections/associate_connection_to_tool/python_connections.mdx:156),
    injected environment variables, or local `.env` values.

    Resolution order:
    1. watsonx Orchestrate runtime API key connection lookup
    2. watsonx Orchestrate injected environment variables
    3. local environment values from `.env`

    Args:
        app_id (str): watsonx Orchestrate connection app id.

    Returns:
        CloudantSettings: Parsed Cloudant configuration.

    Raises:
        ValueError: If required Cloudant settings are missing.
    """
    load_environment()

    connection_prefix = get_connection_prefix()
    api_key_connection = get_wxo_api_key_connection(app_id)

    connection_url_key = f"{connection_prefix}_URL"
    connection_api_key_key = f"{connection_prefix}_API_KEY"
    connection_iam_url_key = f"{connection_prefix}_IAM_URL"

    runtime_url = ""
    runtime_api_key = ""

    if api_key_connection:
        runtime_url, runtime_api_key = api_key_connection

    url = runtime_url or _get_first_env(connection_url_key, "CLOUDANT_URL")
    api_key = runtime_api_key or _get_first_env(connection_api_key_key, "CLOUDANT_API_KEY")
    iam_url = _get_first_env(connection_iam_url_key, "CLOUDANT_IAM_URL") or DEFAULT_IAM_URL

    if url and "://" not in url:
        url = f"https://{url.lstrip('/')}"

    if not url:
        raise ValueError(
            "Missing Cloudant URL. Expected watsonx Orchestrate API key connection field "
            "`url`, injected variable "
            f"`{connection_url_key}`, or local variable `CLOUDANT_URL`."
        )

    if not api_key:
        raise ValueError(
            "Missing Cloudant API key. Expected watsonx Orchestrate API key connection field "
            "`api_key`, injected variable "
            f"`{connection_api_key_key}`, or local variable `CLOUDANT_API_KEY`."
        )

    if runtime_url or runtime_api_key:
        credential_source = "wxo_runtime_connection"
    elif os.getenv(connection_url_key, "").strip() or os.getenv(connection_api_key_key, "").strip():
        credential_source = "wxo_connection_env"
    else:
        credential_source = "local_env"

    databases = {
        "customers": os.getenv("CLOUDANT_DB_CUSTOMERS", "bank_customers").strip(),
        "accounts": os.getenv("CLOUDANT_DB_ACCOUNTS", "bank_accounts").strip(),
        "transactions": os.getenv("CLOUDANT_DB_TRANSACTIONS", "bank_transactions").strip(),
        "credit": os.getenv("CLOUDANT_DB_CREDIT", "bank_credit").strip(),
        "devices": os.getenv("CLOUDANT_DB_DEVICES", "bank_devices").strip(),
        "fraud": os.getenv("CLOUDANT_DB_FRAUD", "bank_fraud").strip(),
        "loans": os.getenv("CLOUDANT_DB_LOANS", "bank_loans").strip(),
        "audit": os.getenv("CLOUDANT_DB_AUDIT", "bank_audit").strip(),
    }

    return CloudantSettings(
        url=url,
        api_key=api_key,
        iam_url=iam_url,
        databases=databases,
        credential_source=credential_source,
        connection_prefix=connection_prefix,
    )

# Made with Bob
