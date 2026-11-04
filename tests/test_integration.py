"""Integration tests for the HTTP API."""

def test_health(client):
    assert client.get("/health").get_json() == {"status": "ok"}

def test_books_and_loans_flow(client):
    # 1. Добавляем книгу
    r = client.post("/books/", json={"isbn": "111", "title": "T", "author": "A"})
    assert r.status_code == 201

    # 2. Регистрируем читателя
    r = client.post("/readers/", json={"full_name": "Иван"})
    assert r.status_code == 201
    reader_id = r.get_json()["id"]

    # 3. Выдаем книгу
    r = client.post("/loans/", json={"reader_id": reader_id, "isbn": "111"})
    assert r.status_code == 201
    loan_id = r.get_json()["id"]

    # 4. Пытаемся выдать ту же книгу еще раз (должен быть конфликт)
    r2 = client.post("/loans/", json={"reader_id": reader_id, "isbn": "111"})
    assert r2.status_code == 409

    # 5. Возвращаем книгу
    r = client.post(f"/loans/{loan_id}/return")
    assert r.status_code == 200
    assert r.get_json()["status"] == "returned"
