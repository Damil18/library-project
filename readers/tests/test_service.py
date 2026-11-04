"""ReaderService unit tests."""
from datetime import datetime
import pytest
from core.exceptions import ConflictError, NotFoundError, ValidationError
from readers import Reader, ReaderService


class FakeReaderRepository:
    def __init__(self):
        self.readers = []
        self._next_id = 1

    def get_all(self):
        return list(self.readers)

    def get_by_id(self, reader_id):
        return next((r for r in self.readers if r.id == reader_id), None)

    def get_by_email(self, email):
        return next((r for r in self.readers if r.email == email), None)

    def add(self, reader):
        created = Reader(
            id=self._next_id,
            full_name=reader.full_name,
            phone=reader.phone,
            email=reader.email,
            registered_at=reader.registered_at or datetime.now().isoformat(timespec="seconds"),
        )
        self._next_id += 1
        self.readers.append(created)
        return created


@pytest.fixture
def service():
    return ReaderService(FakeReaderRepository())


def test_register(service):
    reader = service.register("Иван Иванов", email="ivan@example.com")
    assert reader.id == 1
    assert reader.full_name == "Иван Иванов"

def test_register_duplicate_email(service):
    service.register("A", email="a@example.com")
    with pytest.raises(ConflictError):
        service.register("B", email="a@example.com")
