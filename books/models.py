"""Book model."""
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class Book:
    isbn: str
    title: str
    author: str
    year: int | None = None
    genre: str | None = None

    def to_dict(self):
        return asdict(self)
