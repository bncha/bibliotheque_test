"""Application service orchestrating business rules and repositories."""

import uuid
from datetime import datetime

from library.domain.exceptions import (
    BookAlreadyReturnedError,
    BookNotAvailableError,
    BookNotFoundError,
    ClientNotFoundError,
    LoanNotFoundError,
    MaxLoansReachedError,
)
from library.domain.models import Book, BookStatus, Client, Loan
from library.services.repository import (
    BookRepository,
    ClientRepository,
    InMemoryBookRepository,
    InMemoryClientRepository,
    InMemoryLoanRepository,
    LoanRepository,
)

MAX_ACTIVE_LOANS_PER_CLIENT = 3


class LibraryService:
    """Orchestrates library use cases and enforces business invariants."""

    def __init__(
        self,
        book_repo: BookRepository | None = None,
        client_repo: ClientRepository | None = None,
        loan_repo: LoanRepository | None = None,
    ) -> None:
        self.book_repo = (
            book_repo if book_repo is not None else InMemoryBookRepository()
        )
        self.client_repo = (
            client_repo if client_repo is not None else InMemoryClientRepository()
        )
        self.loan_repo = (
            loan_repo if loan_repo is not None else InMemoryLoanRepository()
        )

    # --- Client Management ---

    def register_client(
        self, name: str, email: str, client_id: str | None = None
    ) -> Client:
        """Register a new library member."""
        c_id = client_id or uuid.uuid4().hex
        client = Client(id=c_id, name=name, email=email)
        return self.client_repo.save(client)

    def get_client(self, client_id: str) -> Client:
        """Retrieve a client by ID.

        Raises:
            ClientNotFoundError: If client does not exist.
        """
        client = self.client_repo.get_by_id(client_id)
        if not client:
            raise ClientNotFoundError(f"Client with ID '{client_id}' not found.")
        return client

    def list_clients(self) -> list[Client]:
        """List all registered clients."""
        return self.client_repo.list_all()

    # --- Book Management ---

    def add_book(
        self,
        title: str,
        author: str,
        isbn: str,
        book_id: str | None = None,
        status: BookStatus = BookStatus.AVAILABLE,
    ) -> Book:
        """Add a new book to the library catalog."""
        b_id = book_id or uuid.uuid4().hex
        book = Book(id=b_id, title=title, author=author, isbn=isbn, status=status)
        return self.book_repo.save(book)

    def get_book(self, book_id: str) -> Book:
        """Retrieve a book by ID.

        Raises:
            BookNotFoundError: If book does not exist.
        """
        book = self.book_repo.get_by_id(book_id)
        if not book:
            raise BookNotFoundError(f"Book with ID '{book_id}' not found.")
        return book

    def list_books(self) -> list[Book]:
        """List all books in the catalog."""
        return self.book_repo.list_all()

    # --- Loan Operations ---

    def borrow_book(
        self, client_id: str, book_id: str, loan_id: str | None = None
    ) -> Loan:
        """Borrow a book for a client.

        Rules:
            1. Client must exist.
            2. Client cannot borrow more than 3 books simultaneously.
            3. Book must exist.
            4. Book must be available.

        Raises:
            ClientNotFoundError: If client does not exist.
            MaxLoansReachedError: If client has already 3 active loans.
            BookNotFoundError: If book does not exist.
            BookNotAvailableError: If book is already borrowed.
        """
        # Rule: Client existence
        client = self.get_client(client_id)

        # Rule: Maximum 3 active loans per client
        active_loans = self.loan_repo.get_active_loans_by_client(client.id)
        if len(active_loans) >= MAX_ACTIVE_LOANS_PER_CLIENT:
            raise MaxLoansReachedError(
                f"Client '{client.name}' (ID: {client.id}) has already reached the maximum limit "
                f"of {MAX_ACTIVE_LOANS_PER_CLIENT} active loans."
            )

        # Rule: Book existence & availability
        book = self.get_book(book_id)
        if not book.is_available:
            raise BookNotAvailableError(
                f"Book '{book.title}' (ID: {book.id}) is not available for borrowing."
            )

        # Transition book state
        book.mark_as_borrowed()
        self.book_repo.save(book)

        # Create and save loan
        l_id = loan_id or uuid.uuid4().hex
        loan = Loan(id=l_id, client_id=client.id, book_id=book.id)
        return self.loan_repo.save(loan)

    def return_book(self, loan_id: str, return_date: datetime | None = None) -> Loan:
        """Return a borrowed book.

        Rules:
            1. Loan must exist.
            2. Loan must be currently active (not already returned).
            3. Associated book is marked as available.

        Raises:
            LoanNotFoundError: If loan does not exist.
            BookAlreadyReturnedError: If loan was already closed.
        """
        loan = self.loan_repo.get_by_id(loan_id)
        if not loan:
            raise LoanNotFoundError(f"Loan with ID '{loan_id}' not found.")

        if not loan.is_active:
            raise BookAlreadyReturnedError(
                f"Loan '{loan.id}' is already returned on {loan.returned_at}."
            )

        # Close loan
        loan.return_book(return_date=return_date)
        self.loan_repo.save(loan)

        # Mark corresponding book as available
        book = self.book_repo.get_by_id(loan.book_id)
        if book:
            book.mark_as_returned()
            self.book_repo.save(book)

        return loan

    def get_client_loans(self, client_id: str, active_only: bool = False) -> list[Loan]:
        """Get loans for a specific client.

        Raises:
            ClientNotFoundError: If client does not exist.
        """
        self.get_client(client_id)  # Validate client exists
        if active_only:
            return self.loan_repo.get_active_loans_by_client(client_id)
        return self.loan_repo.get_loans_by_client(client_id)

    def get_loan(self, loan_id: str) -> Loan:
        """Retrieve a loan by ID.

        Raises:
            LoanNotFoundError: If loan does not exist.
        """
        loan = self.loan_repo.get_by_id(loan_id)
        if not loan:
            raise LoanNotFoundError(f"Loan with ID '{loan_id}' not found.")
        return loan

    def list_loans(self) -> list[Loan]:
        """List all loans."""
        return self.loan_repo.list_all()
