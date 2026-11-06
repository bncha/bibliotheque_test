"""Pydantic schemas for HTTP requests and responses."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class BorrowRequest(BaseModel):
    """Payload for borrowing a book."""

    client_id: str = Field(..., description="ID of the borrowing client")
    book_id: str = Field(..., description="ID of the book to borrow")


class BookCreateRequest(BaseModel):
    """Payload for creating a new book."""

    title: str = Field(..., min_length=1, description="Book title")
    author: str = Field(..., min_length=1, description="Book author")
    isbn: str = Field(..., min_length=1, description="ISBN code")


class BookResponse(BaseModel):
    """Representation of a book in API responses."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    author: str
    isbn: str
    status: str


class ClientCreateRequest(BaseModel):
    """Payload for creating a new client."""

    name: str = Field(..., min_length=1, description="Client full name")
    email: str = Field(..., min_length=3, description="Client email address")


class ClientResponse(BaseModel):
    """Representation of a client in API responses."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    email: str


class LoanResponse(BaseModel):
    """Representation of a loan in API responses."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    client_id: str
    book_id: str
    borrowed_at: datetime
    returned_at: datetime | None
    is_active: bool


class ErrorResponse(BaseModel):
    """Standardized error response body."""

    detail: str
