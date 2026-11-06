"""Repository interfaces and in-memory implementations.

Provides in-memory storage for Books, Clients, and Loans without requiring an external database.
"""

from typing import Protocol

from library.domain.models import Book, Client, Loan


class BookRepository(Protocol):
    """Interface for Book data access."""

    def get_by_id(self, book_id: str) -> Book | None: ...
    def save(self, book: Book) -> Book: ...
    def list_all(self) -> list[Book]: ...


class ClientRepository(Protocol):
    """Interface for Client data access."""

    def get_by_id(self, client_id: str) -> Client | None: ...
    def save(self, client: Client) -> Client: ...
    def list_all(self) -> list[Client]: ...


class LoanRepository(Protocol):
    """Interface for Loan data access."""

    def get_by_id(self, loan_id: str) -> Loan | None: ...
    def save(self, loan: Loan) -> Loan: ...
    def get_active_loans_by_client(self, client_id: str) -> list[Loan]: ...
    def get_loans_by_client(self, client_id: str) -> list[Loan]: ...
    def list_all(self) -> list[Loan]: ...


class InMemoryBookRepository:
    """In-memory storage for books."""

    def __init__(self, initial_books: list[Book] | None = None) -> None:
        self._books: dict[str, Book] = {}
        if initial_books:
            for book in initial_books:
                self.save(book)

    def get_by_id(self, book_id: str) -> Book | None:
        return self._books.get(book_id)

    def save(self, book: Book) -> Book:
        self._books[book.id] = book
        return book

    def list_all(self) -> list[Book]:
        return list(self._books.values())


class InMemoryClientRepository:
    """In-memory storage for clients."""

    def __init__(self, initial_clients: list[Client] | None = None) -> None:
        self._clients: dict[str, Client] = {}
        if initial_clients:
            for client in initial_clients:
                self.save(client)

    def get_by_id(self, client_id: str) -> Client | None:
        return self._clients.get(client_id)

    def save(self, client: Client) -> Client:
        self._clients[client.id] = client
        return client

    def list_all(self) -> list[Client]:
        return list(self._clients.values())


class InMemoryLoanRepository:
    """In-memory storage for loans."""

    def __init__(self, initial_loans: list[Loan] | None = None) -> None:
        self._loans: dict[str, Loan] = {}
        if initial_loans:
            for loan in initial_loans:
                self.save(loan)

    def get_by_id(self, loan_id: str) -> Loan | None:
        return self._loans.get(loan_id)

    def save(self, loan: Loan) -> Loan:
        self._loans[loan.id] = loan
        return loan

    def get_active_loans_by_client(self, client_id: str) -> list[Loan]:
        return [
            loan
            for loan in self._loans.values()
            if loan.client_id == client_id and loan.is_active
        ]

    def get_loans_by_client(self, client_id: str) -> list[Loan]:
        return [loan for loan in self._loans.values() if loan.client_id == client_id]

    def list_all(self) -> list[Loan]:
        return list(self._loans.values())

