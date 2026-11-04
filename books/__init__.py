"""Books module."""
from books.models import Book
from books.service import BookService

__all__ = ["Book", "BookService"]
