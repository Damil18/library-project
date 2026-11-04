"""Loans module."""
from loans.models import Loan
from loans.service import LoanService

__all__ = ["Loan", "LoanService"]
