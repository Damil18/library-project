"""Integration tests for the HTTP API."""


def test_health(client):
    assert client.get("/health").get_json() == {"status": "ok"}


def test_books_list_empty(client):
    assert client.get("/books/").get_json() == []


def test_books_create(client):
    r = client.post(
        "/books/", json={"isbn": "111", "title": "T", "author": "A"}
    )
    assert r.status_code == 201
    assert r.get_json()["isbn"] == "111"
    assert len(client.get("/books/").get_json()) == 1


def test_books_duplicate(client):
    client.post("/books/", json={"isbn": "111", "title": "T", "author": "A"})
    r = client.post(
        "/books/", json={"isbn": "111", "title": "T2", "author": "A2"}
    )
    assert r.status_code == 409


def test_books_missing(client):
    assert client.get("/books/missing").status_code == 404


def test_books_validation(client):
    r = client.post("/books/", json={"isbn": "", "title": "T", "author": "A"})
    assert r.status_code == 400
