"""Integration tests for the REST API endpoints."""

import pytest
from fastapi.testclient import TestClient

from library.api.main import app
from library.api.routes import get_library_service
from library.services.library_service import LibraryService


@pytest.fixture
def client() -> TestClient:
    # Use an isolated LibraryService instance per test
    test_service = LibraryService()
    app.dependency_overrides[get_library_service] = lambda: test_service
    with TestClient(app) as tc:
        yield tc
    app.dependency_overrides.clear()


def test_create_and_get_book(client: TestClient) -> None:
    resp = client.post(
        "/books",
        json={
            "title": "Refactoring",
            "author": "Martin Fowler",
            "isbn": "9780201485677",
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Refactoring"
    assert data["status"] == "available"

    book_id = data["id"]
    get_resp = client.get(f"/books/{book_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == book_id


def test_create_and_get_client(client: TestClient) -> None:
    resp = client.post(
        "/clients",
        json={"name": "Alice Dupont", "email": "alice@example.com"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Alice Dupont"
    assert data["email"] == "alice@example.com"

    client_id = data["id"]
    get_resp = client.get(f"/clients/{client_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == client_id


def test_borrow_and_return_book(client: TestClient) -> None:
    # Create client and book
    client_res = client.post(
        "/clients", json={"name": "Bob", "email": "bob@example.com"}
    ).json()
    book_res = client.post(
        "/books", json={"title": "DDD", "author": "Evans", "isbn": "123"}
    ).json()

    # Borrow book
    borrow_res = client.post(
        "/loans", json={"client_id": client_res["id"], "book_id": book_res["id"]}
    )
    assert borrow_res.status_code == 201
    loan = borrow_res.json()
    assert loan["client_id"] == client_res["id"]
    assert loan["book_id"] == book_res["id"]
    assert loan["is_active"] is True

    loan_id = loan["id"]

    # Verify book is now borrowed
    book_check = client.get(f"/books/{book_res['id']}").json()
    assert book_check["status"] == "borrowed"

    # Return book
    return_res = client.post(f"/loans/{loan_id}/return")
    assert return_res.status_code == 200
    returned_loan = return_res.json()
    assert returned_loan["is_active"] is False
    assert returned_loan["returned_at"] is not None

    # Check client loans
    loans_res = client.get(f"/clients/{client_res['id']}/loans")
    assert loans_res.status_code == 200
    assert len(loans_res.json()) == 1


def test_borrow_unavailable_book_fails(client: TestClient) -> None:
    c1 = client.post("/clients", json={"name": "C1", "email": "c1@example.com"}).json()
    c2 = client.post("/clients", json={"name": "C2", "email": "c2@example.com"}).json()
    b = client.post("/books", json={"title": "B", "author": "A", "isbn": "1"}).json()

    # C1 borrows B
    res1 = client.post("/loans", json={"client_id": c1["id"], "book_id": b["id"]})
    assert res1.status_code == 201

    # C2 tries to borrow B
    res2 = client.post("/loans", json={"client_id": c2["id"], "book_id": b["id"]})
    assert res2.status_code == 400
    assert "not available" in res2.json()["detail"].lower()


def test_borrow_max_loans_fails(client: TestClient) -> None:
    c = client.post("/clients", json={"name": "C", "email": "c@example.com"}).json()

    for i in range(3):
        b = client.post(
            "/books", json={"title": f"B{i}", "author": "A", "isbn": str(i)}
        ).json()
        resp = client.post("/loans", json={"client_id": c["id"], "book_id": b["id"]})
        assert resp.status_code == 201

    # 4th borrow attempt
    b4 = client.post("/books", json={"title": "B4", "author": "A", "isbn": "4"}).json()
    resp4 = client.post("/loans", json={"client_id": c["id"], "book_id": b4["id"]})
    assert resp4.status_code == 400
    assert "maximum limit" in resp4.json()["detail"].lower()


def test_return_already_returned_loan(client: TestClient) -> None:
    c = client.post("/clients", json={"name": "C", "email": "c@example.com"}).json()
    b = client.post("/books", json={"title": "B", "author": "A", "isbn": "1"}).json()
    loan = client.post("/loans", json={"client_id": c["id"], "book_id": b["id"]}).json()

    # First return
    client.post(f"/loans/{loan['id']}/return")

    # Second return
    res = client.post(f"/loans/{loan['id']}/return")
    assert res.status_code == 400
    assert "already returned" in res.json()["detail"].lower()


def test_loan_not_found(client: TestClient) -> None:
    res = client.post("/loans/unknown-loan-id/return")
    assert res.status_code == 404


def test_root_endpoint(client: TestClient) -> None:
    res = client.get("/")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_list_books(client: TestClient) -> None:
    client.post("/books", json={"title": "Book 1", "author": "Auth 1", "isbn": "ISBN1"})
    client.post("/books", json={"title": "Book 2", "author": "Auth 2", "isbn": "ISBN2"})
    res = client.get("/books")
    assert res.status_code == 200
    assert len(res.json()) >= 2


def test_list_clients(client: TestClient) -> None:
    client.post("/clients", json={"name": "Alice", "email": "alice@test.com"})
    res = client.get("/clients")
    assert res.status_code == 200
    assert len(res.json()) >= 1


def test_list_loans_and_get_loan(client: TestClient) -> None:
    c = client.post("/clients", json={"name": "User", "email": "user@test.com"}).json()
    b = client.post(
        "/books", json={"title": "Book", "author": "Auth", "isbn": "123"}
    ).json()
    loan = client.post("/loans", json={"client_id": c["id"], "book_id": b["id"]}).json()

    list_res = client.get("/loans")
    assert list_res.status_code == 200
    assert len(list_res.json()) >= 1

    get_res = client.get(f"/loans/{loan['id']}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == loan["id"]
