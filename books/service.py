"""Book service."""
from books.models import Book
from books.repository import BookRepository
from core.exceptions import ConflictError, NotFoundError, ValidationError


class BookService:
    def __init__(self, repo):
        self.repo = repo

    def list_books(self):
        return self.repo.get_all()

    def get_book(self, isbn):
        book = self.repo.get_by_isbn(isbn)
        if not book:
            raise NotFoundError("Book " + isbn + " not found")
        return book

    def add_book(self, isbn, title, author, year=None, genre=None):
        if not isbn or not isbn.strip():
            raise ValidationError("isbn is required")
        if not title or not title.strip():
            raise ValidationError("title is required")
        if not author or not author.strip():
            raise ValidationError("author is required")
        if self.repo.get_by_isbn(isbn):
            raise ConflictError("Book " + isbn + " already exists")
        book = Book(
            isbn=isbn.strip(),
            title=title.strip(),
            author=author.strip(),
            year=year,
            genre=genre,
        )
        return self.repo.add(book)
