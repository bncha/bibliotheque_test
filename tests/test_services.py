"""Unit tests for the application service and business rules."""

import pytest

from library.domain.exceptions import (
    BookAlreadyReturnedError,
    BookNotAvailableError,
    BookNotFoundError,
    ClientNotFoundError,
    LoanNotFoundError,
    MaxLoansReachedError,
)
from library.services.library_service import MAX_ACTIVE_LOANS_PER_CLIENT, LibraryService


@pytest.fixture
def service() -> LibraryService:
    return LibraryService()


def test_borrow_book_success(service: LibraryService) -> None:
    client = service.register_client("Alice", "alice@example.com")
    book = service.add_book("Clean Code", "Robert C. Martin", "1111111111")

    loan = service.borrow_book(client_id=client.id, book_id=book.id)

    assert loan.client_id == client.id
    assert loan.book_id == book.id
    assert loan.is_active is True

    # Book should now be marked as borrowed
    updated_book = service.get_book(book.id)
    assert updated_book.is_available is False


def test_borrow_book_client_not_found(service: LibraryService) -> None:
    book = service.add_book("Clean Code", "Robert C. Martin", "1111111111")

    with pytest.raises(ClientNotFoundError):
        service.borrow_book(client_id="unknown-client", book_id=book.id)


def test_borrow_book_not_found(service: LibraryService) -> None:
    client = service.register_client("Alice", "alice@example.com")

    with pytest.raises(BookNotFoundError):
        service.borrow_book(client_id=client.id, book_id="unknown-book")


def test_borrow_book_not_available(service: LibraryService) -> None:
    client1 = service.register_client("Alice", "alice@example.com")
    client2 = service.register_client("Bob", "bob@example.com")
    book = service.add_book("Clean Code", "Robert C. Martin", "1111111111")

    service.borrow_book(client_id=client1.id, book_id=book.id)

    with pytest.raises(BookNotAvailableError):
        service.borrow_book(client_id=client2.id, book_id=book.id)


def test_borrow_book_max_loans_limit(service: LibraryService) -> None:
    client = service.register_client("Alice", "alice@example.com")

    # Borrow up to the limit (3 books)
    for i in range(MAX_ACTIVE_LOANS_PER_CLIENT):
        book = service.add_book(f"Book {i}", "Author", f"ISBN-{i}")
        service.borrow_book(client_id=client.id, book_id=book.id)

    # 4th book should be rejected
    fourth_book = service.add_book("Book 4", "Author", "ISBN-4")
    with pytest.raises(MaxLoansReachedError):
        service.borrow_book(client_id=client.id, book_id=fourth_book.id)


def test_return_book_success(service: LibraryService) -> None:
    client = service.register_client("Alice", "alice@example.com")
    book = service.add_book("Clean Code", "Robert C. Martin", "1111111111")
    loan = service.borrow_book(client_id=client.id, book_id=book.id)

    returned_loan = service.return_book(loan.id)

    assert returned_loan.is_active is False
    assert returned_loan.returned_at is not None

    # Book should now be available again
    updated_book = service.get_book(book.id)
    assert updated_book.is_available is True


def test_return_book_not_found(service: LibraryService) -> None:
    with pytest.raises(LoanNotFoundError):
        service.return_book("non-existent-loan-id")


def test_return_book_already_returned(service: LibraryService) -> None:
    client = service.register_client("Alice", "alice@example.com")
    book = service.add_book("Clean Code", "Robert C. Martin", "1111111111")
    loan = service.borrow_book(client_id=client.id, book_id=book.id)

    service.return_book(loan.id)

    with pytest.raises(BookAlreadyReturnedError):
        service.return_book(loan.id)


def test_get_client_loans(service: LibraryService) -> None:
    client = service.register_client("Alice", "alice@example.com")
    b1 = service.add_book("Book 1", "Author", "ISBN-1")
    b2 = service.add_book("Book 2", "Author", "ISBN-2")

    loan1 = service.borrow_book(client.id, b1.id)
    service.borrow_book(client.id, b2.id)

    # Return first book
    service.return_book(loan1.id)

    all_loans = service.get_client_loans(client.id, active_only=False)
    active_loans = service.get_client_loans(client.id, active_only=True)

    assert len(all_loans) == 2
    assert len(active_loans) == 1
