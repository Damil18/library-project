"""Book repository."""
from books.models import Book


class BookRepository:
    def __init__(self, conn):
        self.conn = conn

    def get_all(self):
        rows = self.conn.execute(
            "SELECT isbn, title, author, year, genre FROM books ORDER BY title"
        ).fetchall()
        return [Book(**dict(row)) for row in rows]

    def get_by_isbn(self, isbn):
        row = self.conn.execute(
            "SELECT isbn, title, author, year, genre FROM books WHERE isbn = ?",
            (isbn,),
        ).fetchone()
        return Book(**dict(row)) if row else None

    def add(self, book):
        self.conn.execute(
            "INSERT INTO books (isbn, title, author, year, genre) VALUES (?, ?, ?, ?, ?)",
            (book.isbn, book.title, book.author, book.year, book.genre),
        )
        self.conn.commit()
        return book

    def count(self):
        return self.conn.execute("SELECT COUNT(*) FROM books").fetchone()[0]
