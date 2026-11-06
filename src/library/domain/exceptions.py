"""Domain exceptions for the library management system.

These exceptions represent business rule violations and are pure Python
without any external framework dependencies.
"""


class LibraryDomainError(Exception):
    """Base exception for all domain-specific errors."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class BookNotAvailableError(LibraryDomainError):
    """Raised when an operation requires an available book, but it is currently borrowed."""


class BookAlreadyReturnedError(LibraryDomainError):
    """Raised when attempting to return a loan that has already been returned."""


class MaxLoansReachedError(LibraryDomainError):
    """Raised when a client attempts to borrow more than the allowed maximum number of books."""


class LoanNotFoundError(LibraryDomainError):
    """Raised when a requested loan does not exist."""


class BookNotFoundError(LibraryDomainError):
    """Raised when a requested book does not exist."""


class ClientNotFoundError(LibraryDomainError):
    """Raised when a requested client does not exist."""
