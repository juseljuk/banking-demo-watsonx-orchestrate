"""
Cloudant-backed standalone Python tools for loan processing use cases.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict

from dotenv import load_dotenv
from ibm_watsonx_orchestrate.agent_builder.connections import ConnectionType, ExpectedCredentials
from ibm_watsonx_orchestrate.agent_builder.tools import tool
from ibmcloudant.cloudant_v1 import CloudantV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

try:
    from ibm_watsonx_orchestrate.run import connections as wxo_connections
except Exception:
    wxo_connections = None


DEFAULT_CONNECTION_PREFIX = "CLOUDANT_CONN"
DEFAULT_IAM_URL = "https://iam.cloud.ibm.com/identity/token"
CLOUDANT_CONNECTION_APP_ID = "cloudant"
CLOUDANT_EXPECTED_CREDENTIALS: list[ExpectedCredentials] = [
    ExpectedCredentials(app_id=CLOUDANT_CONNECTION_APP_ID, type=ConnectionType.API_KEY_AUTH)
]


@dataclass(frozen=True)
class CloudantSettings:
    """
    Configuration values required to connect to IBM Cloudant.
    """

    url: str
    api_key: str
    iam_url: str
    databases: dict[str, str]
    credential_source: str
    connection_prefix: str


def _load_environment() -> None:
    """
    Load local environment variables for local development when available.
    """
    load_dotenv(override=False)


def _get_first_env(*names: str) -> str:
    """
    Return the first non-empty environment variable value.
    """
    import os

    for name in names:
        value = os.getenv(name, "").strip()
        if value:
            return value
    return ""


def _get_connection_prefix() -> str:
    """
    Resolve the watsonx Orchestrate connection prefix used for injected environment variables.
    """
    _load_environment()
    return _get_first_env("CLOUDANT_CONNECTION_PREFIX", "WXO_CLOUDANT_CONNECTION_PREFIX") or DEFAULT_CONNECTION_PREFIX


def _get_wxo_api_key_connection(app_id: str = CLOUDANT_CONNECTION_APP_ID) -> tuple[str, str] | None:
    """
    Resolve a watsonx Orchestrate API key connection at runtime when available.
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


def _get_cloudant_settings(app_id: str = CLOUDANT_CONNECTION_APP_ID) -> CloudantSettings:
    """
    Build Cloudant settings from WXO runtime connection, injected env vars, or local env.
    """
    import os

    _load_environment()
    connection_prefix = _get_connection_prefix()
    api_key_connection = _get_wxo_api_key_connection(app_id)

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
        raise ValueError("Missing Cloudant URL.")
    if not api_key:
        raise ValueError("Missing Cloudant API key.")

    if runtime_url or runtime_api_key:
        credential_source = "wxo_runtime_connection"
    elif _get_first_env(connection_url_key) or _get_first_env(connection_api_key_key):
        credential_source = "wxo_connection_env"
    else:
        credential_source = "local_env"

    databases = {
        "customers": _get_first_env("CLOUDANT_DB_CUSTOMERS") or "bank_customers",
        "credit": _get_first_env("CLOUDANT_DB_CREDIT") or "bank_credit",
        "loans": _get_first_env("CLOUDANT_DB_LOANS") or "bank_loans",
    }

    return CloudantSettings(
        url=url,
        api_key=api_key,
        iam_url=iam_url,
        databases=databases,
        credential_source=credential_source,
        connection_prefix=connection_prefix,
    )


def _create_cloudant_client(settings: CloudantSettings | None = None) -> CloudantV1:
    """
    Create an authenticated Cloudant client.
    """
    resolved_settings = settings or _get_cloudant_settings()
    authenticator = IAMAuthenticator(resolved_settings.api_key, url=resolved_settings.iam_url)
    client = CloudantV1(authenticator=authenticator)
    client.set_service_url(resolved_settings.url)
    return client


def _get_document(database_name: str, document_id: str) -> dict[str, Any] | None:
    """
    Fetch a single document by database and ID.
    """
    client = _create_cloudant_client()
    try:
        response = client.get_document(db=database_name, doc_id=document_id).get_result()
        return dict(response)
    except Exception:
        return None


def _get_customer(customer_id: str) -> dict[str, Any] | None:
    """
    Fetch a customer document.
    """
    settings = _get_cloudant_settings()
    return _get_document(settings.databases["customers"], customer_id)


def _get_credit_report(customer_id: str) -> dict[str, Any] | None:
    """
    Fetch a credit report document.
    """
    settings = _get_cloudant_settings()
    return _get_document(settings.databases["credit"], f"CREDIT-{customer_id}")


def _get_loan_application(application_id: str) -> dict[str, Any] | None:
    """
    Fetch a loan application document.
    """
    settings = _get_cloudant_settings()
    return _get_document(settings.databases["loans"], application_id)


@tool(expected_credentials=CLOUDANT_EXPECTED_CREDENTIALS)
def check_credit_score(customer_id: str) -> Dict[str, Any]:
    """
    Check customer credit score from credit bureau.

    Args:
        customer_id (str): The customer identifier.

    Returns:
        Dict[str, Any]: Credit score information.
    """
    credit_report = _get_credit_report(customer_id)

    if not credit_report:
        return {
            "status": "error",
            "message": f"Credit report not found for customer {customer_id}",
        }

    credit_score = credit_report.get("credit_score", {})

    return {
        "status": "success",
        "customer_id": customer_id,
        "credit_score": credit_score.get("score"),
        "rating": credit_score.get("rating"),
        "bureau": credit_report.get("bureau"),
        "report_date": credit_report.get("report_date"),
    }


def _calculate_debt_to_income_values(customer_id: str) -> dict[str, Any]:
    """
    Calculate raw debt-to-income values for internal reuse.
    """
    customer = _get_customer(customer_id)
    credit_report = _get_credit_report(customer_id)

    if not customer:
        return {
            "status": "error",
            "message": f"Customer {customer_id} not found",
        }

    annual_income = float(customer.get("employment", {}).get("annual_income", 0) or 0)
    monthly_income = annual_income / 12 if annual_income > 0 else 0.0

    total_monthly_debt = 0.0
    if credit_report:
        for account in credit_report.get("credit_accounts", []):
            if account.get("status") == "Open":
                current_balance = float(account.get("current_balance", 0) or 0)
                total_monthly_debt += current_balance * 0.03

    debt_to_income_ratio = total_monthly_debt / monthly_income if monthly_income > 0 else 0.0

    return {
        "status": "success",
        "customer_id": customer_id,
        "debt_to_income_ratio": round(debt_to_income_ratio, 3),
        "debt_to_income_percentage": f"{round(debt_to_income_ratio * 100, 1)}%",
        "monthly_income": round(monthly_income, 2),
        "total_monthly_debt": round(total_monthly_debt, 2),
    }


@tool(expected_credentials=CLOUDANT_EXPECTED_CREDENTIALS)
def calculate_debt_to_income(customer_id: str) -> Dict[str, Any]:
    """
    Calculate debt-to-income ratio for a customer.

    Args:
        customer_id (str): The customer identifier.

    Returns:
        Dict[str, Any]: Debt-to-income analysis.
    """
    return _calculate_debt_to_income_values(customer_id)


@tool(expected_credentials=CLOUDANT_EXPECTED_CREDENTIALS)
def calculate_loan_eligibility(
    customer_id: str,
    loan_amount: float,
    loan_purpose: str,
    credit_score: int | None = None,
    debt_to_income_ratio: float | None = None,
) -> Dict[str, Any]:
    """
    Calculate loan eligibility for a customer.

    Args:
        customer_id (str): The customer identifier.
        loan_amount (float): Requested loan amount.
        loan_purpose (str): Purpose of the loan.
        credit_score (int | None): Optional credit score from bureau. If omitted,
            it is resolved from Cloudant.
        debt_to_income_ratio (float | None): Optional DTI ratio as decimal. If omitted,
            it is calculated from Cloudant-backed customer and credit data.

    Returns:
        Dict[str, Any]: Eligibility assessment.
    """
    customer = _get_customer(customer_id)

    if not customer:
        return {
            "status": "error",
            "message": f"Customer {customer_id} not found",
        }

    annual_income = float(customer.get("employment", {}).get("annual_income", 0) or 0)
    max_loan_amount = annual_income * 0.5

    if credit_score is None:
        credit_report = _get_credit_report(customer_id)
        credit_score_data = credit_report.get("credit_score", {}) if credit_report else {}
        resolved_credit_score = credit_score_data.get("score", customer.get("credit_score", 0))
        credit_score = int(resolved_credit_score or 0)

    if debt_to_income_ratio is None:
        dti_result = _calculate_debt_to_income_values(customer_id)
        if dti_result["status"] != "success":
            return {
                "status": "error",
                "message": f"Unable to calculate debt-to-income ratio for customer {customer_id}",
            }
        debt_to_income_ratio = float(dti_result["debt_to_income_ratio"] or 0.0)

    eligible = True
    if credit_score < 600:
        eligible = False
        reason = "Credit score below minimum threshold of 600"
    elif debt_to_income_ratio > 0.40:
        eligible = False
        reason = f"Debt-to-income ratio exceeds 40% ({round(debt_to_income_ratio * 100, 1)}%)"
    elif loan_amount > max_loan_amount:
        eligible = False
        reason = f"Requested amount exceeds maximum (£{max_loan_amount:.2f})"
    else:
        reason = "Meets eligibility criteria"

    if credit_score >= 750:
        risk_rating = "A+ (Excellent)"
    elif credit_score >= 700:
        risk_rating = "A (Very Good)"
    elif credit_score >= 650:
        risk_rating = "B+ (Good)"
    else:
        risk_rating = "B (Acceptable)"

    return {
        "status": "success",
        "customer_id": customer_id,
        "eligible": eligible,
        "reason": reason,
        "credit_score": credit_score,
        "debt_to_income_ratio": round(debt_to_income_ratio, 3),
        "debt_to_income_percentage": f"{round(debt_to_income_ratio * 100, 1)}%",
        "annual_income": annual_income,
        "requested_amount": loan_amount,
        "max_approved_amount": round(max_loan_amount, 2),
        "risk_rating": risk_rating,
        "loan_purpose": loan_purpose,
    }


@tool(expected_credentials=CLOUDANT_EXPECTED_CREDENTIALS)
def generate_loan_offers(
    customer_id: str,
    loan_amount: float,
    credit_score: int | None = None,
) -> Dict[str, Any]:
    """
    Generate personalized loan offers based on eligibility.

    Args:
        customer_id (str): The customer identifier.
        loan_amount (float): Requested loan amount.
        credit_score (int | None): Optional customer credit score. If omitted,
            it is resolved from Cloudant-backed credit data.

    Returns:
        Dict[str, Any]: List of generated loan offers.
    """
    if credit_score is None:
        customer = _get_customer(customer_id)
        credit_report = _get_credit_report(customer_id)
        if not customer and not credit_report:
            return {
                "status": "error",
                "message": f"Unable to resolve credit score for customer {customer_id}",
            }

        credit_score_data = credit_report.get("credit_score", {}) if credit_report else {}
        resolved_credit_score = credit_score_data.get("score")
        if resolved_credit_score is None and customer:
            resolved_credit_score = customer.get("credit_score", 0)

        credit_score = int(resolved_credit_score or 0)

    if credit_score >= 750:
        base_apr = 6.5
    elif credit_score >= 700:
        base_apr = 7.5
    elif credit_score >= 650:
        base_apr = 8.5
    else:
        base_apr = 9.5

    offers: list[dict[str, Any]] = []
    for index, (term, apr_adjustment) in enumerate([(36, -0.5), (60, 0.0), (84, 0.5)]):
        apr = base_apr + apr_adjustment
        monthly_rate = apr / 100 / 12
        monthly_payment = (
            (loan_amount * monthly_rate) / (1 - (1 + monthly_rate) ** (-term))
            if monthly_rate > 0
            else loan_amount / term
        )
        total_interest = (monthly_payment * term) - loan_amount
        total_repayment = loan_amount + total_interest

        offers.append(
            {
                "offer_id": f"OFFER-{customer_id[-3:]}-{chr(65 + index)}",
                "loan_amount": loan_amount,
                "term_months": term,
                "apr": round(apr, 1),
                "monthly_payment": round(monthly_payment, 2),
                "total_interest": round(total_interest, 2),
                "total_repayment": round(total_repayment, 2),
                "recommended": index == 1,
            }
        )

    return {
        "status": "success",
        "customer_id": customer_id,
        "offers": offers,
    }


@tool(expected_credentials=CLOUDANT_EXPECTED_CREDENTIALS)
def initiate_loan_approval(
    customer_id: str,
    loan_amount: float,
    loan_purpose: str,
    selected_offer_id: str = "",
) -> Dict[str, Any]:
    """
    Initiate a lightweight loan approval workflow response.

    Args:
        customer_id (str): The customer identifier.
        loan_amount (float): Loan amount.
        loan_purpose (str): Purpose of the loan.
        selected_offer_id (str): Optional selected offer identifier.

    Returns:
        Dict[str, Any]: Loan approval initiation metadata.
    """
    application_id = f"LOAN-APP-{int(datetime.now().timestamp())}"

    return {
        "status": "success",
        "application_id": application_id,
        "customer_id": customer_id,
        "loan_amount": loan_amount,
        "loan_purpose": loan_purpose,
        "selected_offer_id": selected_offer_id,
        "application_status": "Approved",
        "approval_date": datetime.now().isoformat(),
        "processing_time_minutes": 15,
        "automated_approval": True,
        "next_steps": [
            "Review and sign loan agreement",
            "E-signature via DocuSign",
            "Funds disbursement within 24 hours",
        ],
    }


@tool(expected_credentials=CLOUDANT_EXPECTED_CREDENTIALS)
def generate_loan_documents(application_id: str) -> Dict[str, Any]:
    """
    Generate loan agreement document metadata.

    Args:
        application_id (str): Loan application identifier.

    Returns:
        Dict[str, Any]: Generated document metadata.
    """
    document_id = f"DOC-{int(datetime.now().timestamp())}"

    return {
        "status": "success",
        "application_id": application_id,
        "document_id": document_id,
        "documents": [
            {
                "type": "Loan Agreement",
                "status": "Generated",
                "pages": 12,
            },
            {
                "type": "Truth in Lending Disclosure",
                "status": "Generated",
                "pages": 3,
            },
            {
                "type": "Direct Debit Mandate",
                "status": "Generated",
                "pages": 2,
            },
        ],
        "generated_at": datetime.now().isoformat(),
    }


@tool(expected_credentials=CLOUDANT_EXPECTED_CREDENTIALS)
def send_for_esignature(document_id: str, customer_id: str) -> Dict[str, Any]:
    """
    Send loan documents for electronic signature.

    Args:
        document_id (str): Document identifier.
        customer_id (str): Customer identifier.

    Returns:
        Dict[str, Any]: E-signature dispatch metadata.
    """
    customer = _get_customer(customer_id)

    if not customer:
        return {
            "status": "error",
            "message": f"Customer {customer_id} not found",
        }

    return {
        "status": "success",
        "document_id": document_id,
        "customer_id": customer_id,
        "email_sent_to": customer.get("email"),
        "esignature_link": f"https://docusign.example.com/sign/{document_id}",
        "expires_at": (datetime.now() + timedelta(days=7)).isoformat(),
    }


@tool(expected_credentials=CLOUDANT_EXPECTED_CREDENTIALS)
def disburse_funds(application_id: str, account_id: str) -> Dict[str, Any]:
    """
    Disburse approved loan funds to a customer account.

    Args:
        application_id (str): Loan application identifier.
        account_id (str): Destination account identifier.

    Returns:
        Dict[str, Any]: Disbursement metadata.
    """
    return {
        "status": "success",
        "application_id": application_id,
        "account_id": account_id,
        "disbursement_status": "Completed",
        "disbursement_date": datetime.now().isoformat(),
        "transaction_id": f"TXN-{int(datetime.now().timestamp())}",
        "message": "Funds have been deposited to your account",
    }


@tool(expected_credentials=CLOUDANT_EXPECTED_CREDENTIALS)
def get_loan_application(application_id: str) -> Dict[str, Any]:
    """
    Get details of a loan application from Cloudant.

    Args:
        application_id (str): Loan application identifier.

    Returns:
        Dict[str, Any]: Loan application document when found.
    """
    application = _get_loan_application(application_id)

    if not application:
        return {
            "status": "error",
            "message": f"Loan application {application_id} not found",
        }

    return {
        "status": "success",
        "application": application,
    }

# Made with Bob