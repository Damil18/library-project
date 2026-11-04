"""Reader service."""
from datetime import datetime
from readers.models import Reader
from readers.repository import ReaderRepository
from core.exceptions import ConflictError, NotFoundError, ValidationError


class ReaderService:
    def __init__(self, repo):
        self.repo = repo

    def list_readers(self):
        return self.repo.get_all()

    def get_reader(self, reader_id):
        reader = self.repo.get_by_id(reader_id)
        if not reader:
            raise NotFoundError(f"Reader {reader_id} not found")
        return reader

    def register(self, full_name, phone=None, email=None):
        if not full_name or not full_name.strip():
            raise ValidationError("full_name is required")
        if email and self.repo.get_by_email(email):
            raise ConflictError(f"Reader with email {email} already exists")
        reader = Reader(
            full_name=full_name.strip(),
            phone=phone,
            email=email,
            registered_at=datetime.now().isoformat(timespec="seconds"),
        )
        return self.repo.add(reader)
