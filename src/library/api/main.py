"""FastAPI application entrypoint.

Registers routes, domain exception handlers, and configures the API.
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from library.api.routes import _default_service, router
from library.domain.exceptions import (
    BookAlreadyReturnedError,
    BookNotAvailableError,
    BookNotFoundError,
    ClientNotFoundError,
    LibraryDomainError,
    LoanNotFoundError,
    MaxLoansReachedError,
)


def seed_demo_data() -> None:
    """Pre-populates a few books and clients for demo / Swagger exploration."""
    if not _default_service.list_books():
        _default_service.add_book(
            book_id="book-1",
            title="Clean Architecture",
            author="Robert C. Martin",
            isbn="9780134494166",
        )
        _default_service.add_book(
            book_id="book-2",
            title="Domain-Driven Design",
            author="Eric Evans",
            isbn="9780321125217",
        )
        _default_service.add_book(
            book_id="book-3",
            title="Refactoring",
            author="Martin Fowler",
            isbn="9780201485677",
        )
        _default_service.add_book(
            book_id="book-4",
            title="Design Patterns",
            author="Gang of Four",
            isbn="9780201633610",
        )

    if not _default_service.list_clients():
        _default_service.register_client(
            client_id="client-1",
            name="Alice Dupont",
            email="alice@example.com",
        )
        _default_service.register_client(
            client_id="client-2",
            name="Bob Martin",
            email="bob@example.com",
        )


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Startup and shutdown lifecycle."""
    seed_demo_data()
    yield


app = FastAPI(
    title="Library Management API",
    description="API REST de gestion d'une bibliothèque suivant la Clean Architecture.",
    version="0.1.0",
    lifespan=lifespan,
)


# --- Domain Exception Handlers ---


@app.exception_handler(BookNotFoundError)
@app.exception_handler(ClientNotFoundError)
@app.exception_handler(LoanNotFoundError)
async def not_found_exception_handler(
    request: Request, exc: LibraryDomainError
) -> JSONResponse:
    """Handles not found domain exceptions and maps them to HTTP 404."""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": exc.message},
    )


@app.exception_handler(BookNotAvailableError)
@app.exception_handler(MaxLoansReachedError)
@app.exception_handler(BookAlreadyReturnedError)
@app.exception_handler(LibraryDomainError)
async def domain_bad_request_handler(
    request: Request, exc: LibraryDomainError
) -> JSONResponse:
    """Handles business rule violations and maps them to HTTP 400."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": exc.message},
    )


# --- Register Routers ---

app.include_router(router)


@app.get("/", tags=["Health"])
async def root() -> dict[str, str]:
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "Library Management API",
        "docs": "/docs",
    }
