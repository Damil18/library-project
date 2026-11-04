"""LoanService unit tests."""
from datetime import datetime
import pytest
from books import Book
from core.exceptions import ConflictError, NotFoundError
from loans import Loan, LoanService
from readers import Reader


class FakeBookRepo:
    def __init__(self):
        self.books = [Book("111", "T1", "A1"), Book("222", "T2", "A2")]
    def get_by_isbn(self, isbn):
        return next((b for b in self.books if b.isbn == isbn), None)

class FakeReaderRepo:
    def __init__(self):
        self.readers = [Reader(id=1, full_name="R1", registered_at="x")]
    def get_by_id(self, reader_id):
        return next((r for r in self.readers if r.id == reader_id), None)

class FakeLoanRepo:
    def __init__(self):
        self.loans = []
        self._next = 1
    def get_all(self):
        return list(self.loans)
    def get_by_id(self, loan_id):
        return next((l for l in self.loans if l.id == loan_id), None)
    def get_active_by_reader(self, reader_id):
        return [l for l in self.loans if l.reader_id == reader_id and l.status == "active"]
    def add(self, loan):
        loan.id = self._next
        self._next += 1
        self.loans.append(loan)
        return loan
    def update(self, loan):
        for i, l in enumerate(self.loans):
            if l.id == loan.id:
                self.loans[i] = loan
                return

@pytest.fixture
def service():
    return LoanService(FakeLoanRepo(), FakeReaderRepo(), FakeBookRepo())

def test_issue_book_success(service):
    loan = service.issue_book(1, "111")
    assert loan.id == 1
    assert loan.status == "active"

def test_return_book(service):
    loan = service.issue_book(1, "111")
    returned = service.return_book(loan.id)
    assert returned.status == "returned"
