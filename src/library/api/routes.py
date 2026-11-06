"""API routes exposing library operations."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from library.api.schemas import (
    BookCreateRequest,
    BookResponse,
    BorrowRequest,
    ClientCreateRequest,
    ClientResponse,
    LoanResponse,
)
from library.services.library_service import LibraryService

router = APIRouter()

# Global default service instance for runtime dependency injection
_default_service = LibraryService()


def get_library_service() -> LibraryService:
    """Dependency provider returning the library service."""
    return _default_service


# --- Loans Endpoints ---


@router.post(
    "/loans",
    response_model=LoanResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Emprunter un livre",
    tags=["Loans"],
)
def borrow_book(
    payload: BorrowRequest,
    service: Annotated[LibraryService, Depends(get_library_service)],
) -> LoanResponse:
    """Borrow a book for a client.

    Enforces business rules:
    - Client must exist.
    - Max 3 active loans per client.
    - Book must exist and be available.
    """
    loan = service.borrow_book(client_id=payload.client_id, book_id=payload.book_id)
    return LoanResponse.model_validate(loan)


@router.post(
    "/loans/{id}/return",
    response_model=LoanResponse,
    status_code=status.HTTP_200_OK,
    summary="Rendre un livre",
    tags=["Loans"],
)
def return_book(
    id: str,
    service: Annotated[LibraryService, Depends(get_library_service)],
) -> LoanResponse:
    """Return a previously borrowed book by loan ID."""
    loan = service.return_book(loan_id=id)
    return LoanResponse.model_validate(loan)


@router.get(
    "/clients/{id}/loans",
    response_model=list[LoanResponse],
    status_code=status.HTTP_200_OK,
    summary="Voir les emprunts d'un client",
    tags=["Loans"],
)
def get_client_loans(
    id: str,
    service: Annotated[LibraryService, Depends(get_library_service)],
    active_only: bool = Query(
        default=False, description="Filter only active/unreturned loans"
    ),
) -> list[LoanResponse]:
    """Retrieve all loans for a given client."""
    loans = service.get_client_loans(client_id=id, active_only=active_only)
    return [LoanResponse.model_validate(loan) for loan in loans]


@router.get(
    "/loans",
    response_model=list[LoanResponse],
    status_code=status.HTTP_200_OK,
    summary="Lister tous les emprunts",
    tags=["Loans"],
)
def list_loans(
    service: Annotated[LibraryService, Depends(get_library_service)],
) -> list[LoanResponse]:
    """List all registered loans."""
    loans = service.list_loans()
    return [LoanResponse.model_validate(loan) for loan in loans]


@router.get(
    "/loans/{id}",
    response_model=LoanResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtenir un emprunt par son identifiant",
    tags=["Loans"],
)
def get_loan(
    id: str,
    service: Annotated[LibraryService, Depends(get_library_service)],
) -> LoanResponse:
    """Retrieve a specific loan by its ID."""
    loan = service.get_loan(loan_id=id)
    return LoanResponse.model_validate(loan)


# --- Books Endpoints ---


@router.post(
    "/books",
    response_model=BookResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Ajouter un livre",
    tags=["Books"],
)
def create_book(
    payload: BookCreateRequest,
    service: Annotated[LibraryService, Depends(get_library_service)],
) -> BookResponse:
    """Add a new book into the library catalog."""
    book = service.add_book(
        title=payload.title,
        author=payload.author,
        isbn=payload.isbn,
    )
    return BookResponse.model_validate(book)


@router.get(
    "/books",
    response_model=list[BookResponse],
    status_code=status.HTTP_200_OK,
    summary="Lister les livres",
    tags=["Books"],
)
def list_books(
    service: Annotated[LibraryService, Depends(get_library_service)],
) -> list[BookResponse]:
    """List all books in the catalog."""
    books = service.list_books()
    return [BookResponse.model_validate(b) for b in books]


@router.get(
    "/books/{id}",
    response_model=BookResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtenir un livre par son identifiant",
    tags=["Books"],
)
def get_book(
    id: str,
    service: Annotated[LibraryService, Depends(get_library_service)],
) -> BookResponse:
    """Retrieve a specific book by its ID."""
    book = service.get_book(book_id=id)
    return BookResponse.model_validate(book)


# --- Clients Endpoints ---


@router.post(
    "/clients",
    response_model=ClientResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Créer un client",
    tags=["Clients"],
)
def create_client(
    payload: ClientCreateRequest,
    service: Annotated[LibraryService, Depends(get_library_service)],
) -> ClientResponse:
    """Register a new library member."""
    client = service.register_client(
        name=payload.name,
        email=payload.email,
    )
    return ClientResponse.model_validate(client)


@router.get(
    "/clients",
    response_model=list[ClientResponse],
    status_code=status.HTTP_200_OK,
    summary="Lister les clients",
    tags=["Clients"],
)
def list_clients(
    service: Annotated[LibraryService, Depends(get_library_service)],
) -> list[ClientResponse]:
    """List all registered clients."""
    clients = service.list_clients()
    return [ClientResponse.model_validate(c) for c in clients]


@router.get(
    "/clients/{id}",
    response_model=ClientResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtenir un client par son identifiant",
    tags=["Clients"],
)
def get_client(
    id: str,
    service: Annotated[LibraryService, Depends(get_library_service)],
) -> ClientResponse:
    """Retrieve a specific client by ID."""
    client = service.get_client(client_id=id)
    return ClientResponse.model_validate(client)

