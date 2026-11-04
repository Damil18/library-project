"""Loan service."""
from datetime import datetime, timedelta
from books.repository import BookRepository
from core.exceptions import ConflictError, NotFoundError, ValidationError
from loans.models import Loan
from loans.repository import LoanRepository
from readers.repository import ReaderRepository

MAX_ACTIVE_LOANS = 5
LOAN_DAYS = 14


class LoanService:
    def __init__(self, loan_repo, reader_repo, book_repo):
        self.loan_repo = loan_repo
        self.reader_repo = reader_repo
        self.book_repo = book_repo

    def list_loans(self):
        return self.loan_repo.get_all()

    def issue_book(self, reader_id, isbn):
        if not reader_id or not isbn:
            raise ValidationError("reader_id and isbn are required")
        if not self.reader_repo.get_by_id(reader_id):
            raise NotFoundError(f"Reader {reader_id} not found")
        if not self.book_repo.get_by_isbn(isbn):
            raise NotFoundError(f"Book {isbn} not found")
        active = self.loan_repo.get_active_by_reader(reader_id)
        if len(active) >= MAX_ACTIVE_LOANS:
            raise ConflictError(f"Reader {reader_id} already has {MAX_ACTIVE_LOANS} active loans")
        if any(loan.isbn == isbn for loan in active):
            raise ConflictError(f"Reader {reader_id} already has book {isbn}")

        now = datetime.now()
        due = now + timedelta(days=LOAN_DAYS)
        loan = Loan(
            reader_id=reader_id,
            isbn=isbn,
            issued_at=now.isoformat(timespec="seconds"),
            due_at=due.isoformat(timespec="seconds"),
            status="active",
        )
        return self.loan_repo.add(loan)

    def return_book(self, loan_id):
        loan = self.loan_repo.get_by_id(loan_id)
        if not loan:
            raise NotFoundError(f"Loan {loan_id} not found")
        if loan.status != "active":
            raise ConflictError(f"Loan {loan_id} is not active")
        loan.returned_at = datetime.now().isoformat(timespec="seconds")
        loan.status = "returned"
        self.loan_repo.update(loan)
        return loan
