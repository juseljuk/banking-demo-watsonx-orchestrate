"""
Repository exports for Cloudant-backed standalone tools.
"""

from repositories.accounts import AccountRepository
from repositories.base import BaseCloudantRepository
from repositories.credit_reports import CreditReportRepository
from repositories.customers import CustomerRepository
from repositories.devices import DeviceRepository
from repositories.fraud_cases import FraudCaseRepository
from repositories.loan_applications import LoanApplicationRepository
from repositories.transactions import TransactionRepository

__all__ = [
    "AccountRepository",
    "BaseCloudantRepository",
    "CreditReportRepository",
    "CustomerRepository",
    "DeviceRepository",
    "FraudCaseRepository",
    "LoanApplicationRepository",
    "TransactionRepository",
]

# Made with Bob
