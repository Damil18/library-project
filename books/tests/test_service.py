"""BookService unit tests."""
import pytest

from books import Book, BookService
from core.exceptions import ConflictError, NotFoundError, ValidationError


class FakeBookRepository:
    def __init__(self):
        self.books = []

    def get_all(self):
        return list(self.books)

    def get_by_isbn(self, isbn):
        return next((b for b in self.books if b.isbn == isbn), None)

    def add(self, book):
        self.books.append(book)
        return book

    def count(self):
        return len(self.books)


@pytest.fixture
def service():
    return BookService(FakeBookRepository())


def test_add_book(service):
    book = service.add_book("123", "Title", "Author")
    assert book.isbn == "123"
    assert service.get_book("123").title == "Title"


def test_add_book_requires_isbn(service):
    with pytest.raises(ValidationError):
        service.add_book("", "Title", "Author")


def test_add_book_requires_title(service):
    with pytest.raises(ValidationError):
        service.add_book("123", "", "Author")


def test_add_book_duplicate(service):
    service.add_book("123", "T", "A")
    with pytest.raises(ConflictError):
        service.add_book("123", "T2", "A2")


def test_get_missing_book(service):
    with pytest.raises(NotFoundError):
        service.get_book("missing")
