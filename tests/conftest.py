"""Test fixtures."""
import pytest

from app import create_app


@pytest.fixture
def app(tmp_path):
    db_path = tmp_path / "test.db"
    app = create_app(
        {
            "DATABASE_PATH": str(db_path),
            "TESTING": True,
            "PROPAGATE_EXCEPTIONS": False,
        }
    )
    yield app


@pytest.fixture
def client(app):
    return app.test_client()
