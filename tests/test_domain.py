"""Unit tests for the domain layer (Book, Client, Loan)."""

import pytest

from library.domain.exceptions import BookAlreadyReturnedError, BookNotAvailableError
from library.domain.models import Book, BookStatus, Client, Loan


def test_book_initial_state() -> None:
    book = Book(
        id="book-1",
        title="Clean Architecture",
        author="Robert C. Martin",
        isbn="1234567890",
    )
    assert book.status == BookStatus.AVAILABLE
    assert book.is_available is True


def test_book_mark_as_borrowed_success() -> None:
    book = Book(
        id="book-1",
        title="Clean Architecture",
        author="Robert C. Martin",
        isbn="1234567890",
    )
    book.mark_as_borrowed()
    assert book.status == BookStatus.BORROWED
    assert book.is_available is False


def test_book_mark_as_borrowed_raises_when_already_borrowed() -> None:
    book = Book(
        id="book-1",
        title="Clean Architecture",
        author="Robert C. Martin",
        isbn="1234567890",
        status=BookStatus.BORROWED,
    )
    with pytest.raises(BookNotAvailableError):
        book.mark_as_borrowed()


def test_book_mark_as_returned() -> None:
    book = Book(
        id="book-1",
        title="Clean Architecture",
        author="Robert C. Martin",
        isbn="1234567890",
        status=BookStatus.BORROWED,
    )
    book.mark_as_returned()
    assert book.status == BookStatus.AVAILABLE
    assert book.is_available is True


def test_client_creation() -> None:
    client = Client(id="client-1", name="Alice", email="alice@example.com")
    assert client.id == "client-1"
    assert client.name == "Alice"
    assert client.email == "alice@example.com"


def test_loan_lifecycle() -> None:
    loan = Loan(id="loan-1", client_id="client-1", book_id="book-1")
    assert loan.is_active is True
    assert loan.returned_at is None
    assert loan.borrowed_at is not None

    loan.return_book()
    assert loan.is_active is False
    assert loan.returned_at is not None

    with pytest.raises(BookAlreadyReturnedError):
        loan.return_book()
