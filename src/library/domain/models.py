"""Domain entities for the library management system.

These models are pure Python dataclasses representing business entities and their internal rules.
No external dependencies (FastAPI, database, etc.) are used here.
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum

from library.domain.exceptions import BookAlreadyReturnedError, BookNotAvailableError


class BookStatus(str, Enum):
    """Represents the availability status of a book."""

    AVAILABLE = "available"
    BORROWED = "borrowed"


@dataclass
class Book:
    """Represents a book in the library."""

    id: str
    title: str
    author: str
    isbn: str
    status: BookStatus = BookStatus.AVAILABLE

    @property
    def is_available(self) -> bool:
        """Check whether the book is available for borrowing."""
        return self.status == BookStatus.AVAILABLE

    def mark_as_borrowed(self) -> None:
        """Mark the book as borrowed.

        Raises:
            BookNotAvailableError: If the book is not currently available.
        """
        if not self.is_available:
            raise BookNotAvailableError(
                f"Book '{self.title}' (ID: {self.id}) is currently not available for loan."
            )
        self.status = BookStatus.BORROWED

    def mark_as_returned(self) -> None:
        """Mark the book as available after being returned."""
        self.status = BookStatus.AVAILABLE


@dataclass
class Client:
    """Represents a library client/member."""

    id: str
    name: str
    email: str


@dataclass
class Loan:
    """Represents a loan contract between a client and a book."""

    id: str
    client_id: str
    book_id: str
    borrowed_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    returned_at: datetime | None = None

    @property
    def is_active(self) -> bool:
        """Check whether the loan is ongoing (not yet returned)."""
        return self.returned_at is None

    def return_book(self, return_date: datetime | None = None) -> None:
        """Close the loan by registering a return date.

        Raises:
            BookAlreadyReturnedError: If the loan is already closed/returned.
        """
        if not self.is_active:
            raise BookAlreadyReturnedError(
                f"Loan '{self.id}' has already been returned on {self.returned_at}."
            )
        self.returned_at = return_date or datetime.now(UTC)
