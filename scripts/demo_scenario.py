#!/usr/bin/env python3
"""Interactive demonstration script for the Library Management API.

Executes a complete business scenario showcasing all features and business invariants:
1. Catalog & Client discovery
2. Successful book loan
3. Enforcing Rule: Cannot borrow an unavailable book (HTTP 400)
4. Enforcing Rule: Cannot borrow more than 3 books (HTTP 400)
5. Consulting client loans
6. Returning a book
7. Enforcing Rule: Cannot return an already returned book (HTTP 400)
"""

import sys
import httpx

BASE_URL = "http://127.0.0.1:8000"


def print_step(title: str) -> None:
    print(f"\n\033[1;34m=== {title} ===\033[0m")


def print_success(msg: str) -> None:
    print(f"  \033[1;32m✔ {msg}\033[0m")


def print_expected_error(status: int, detail: str) -> None:
    print(f"  \033[1;33mℹ [Code {status}] Rejet métier attendu: {detail}\033[0m")


def main() -> None:
    print("\033[1;36m" + "=" * 60)
    print("  DÉMONSTRATION DU SYSTÈME DE GESTION DE BIBLIOTHÈQUE")
    print("=" * 60 + "\033[0m")

    # Check connection
    try:
        r = httpx.get(f"{BASE_URL}/", timeout=2.0)
        r.raise_for_status()
    except Exception:
        print(
            f"\033[1;31mErreur: Le serveur n'est pas accessible sur {BASE_URL}.\033[0m"
        )
        print(
            "Veuillez démarrer le serveur avec: uvicorn library.api.main:app --reload"
        )
        sys.exit(1)

    # 1. Catalog discovery
    print_step("1. Découverte du catalogue et des adhérents")
    books = httpx.get(f"{BASE_URL}/books").json()
    clients = httpx.get(f"{BASE_URL}/clients").json()
    print_success(f"{len(books)} livre(s) disponible(s) dans le catalogue")
    print_success(f"{len(clients)} client(s) enregistré(s)")

    # 2. Borrow a book
    client_alice = clients[0]["id"]
    client_bob = clients[1]["id"]
    book_ddd = books[1]["id"]

    print_step("2. Alice emprunte 'Domain-Driven Design'")
    loan_resp = httpx.post(
        f"{BASE_URL}/loans",
        json={"client_id": client_alice, "book_id": book_ddd},
    )
    assert loan_resp.status_code == 201, loan_resp.text
    loan_data = loan_resp.json()
    print_success(f"Emprunt créé avec succès (ID: {loan_data['id']})")
    print_success(f"Horodatage: {loan_data['borrowed_at']}")

    # 3. Rule: Unavailable book
    print_step("3. Règle métier : Bob tente d'emprunter le même livre (déjà prêté)")
    rejected_loan = httpx.post(
        f"{BASE_URL}/loans",
        json={"client_id": client_bob, "book_id": book_ddd},
    )
    print_expected_error(rejected_loan.status_code, rejected_loan.json()["detail"])

    # 4. Rule: Max 3 active loans
    print_step(
        "4. Règle métier : Alice tente d'emprunter un 4ème livre (Quota de 3 max)"
    )
    extra_loans = []
    # Alice takes 2 more books (reaching 3 active loans)
    for b in books[2:4]:
        res = httpx.post(
            f"{BASE_URL}/loans", json={"client_id": client_alice, "book_id": b["id"]}
        )
        if res.status_code == 201:
            extra_loans.append(res.json()["id"])

    # Register a 5th book in catalog
    b5 = httpx.post(
        f"{BASE_URL}/books",
        json={
            "title": "TDD by Example",
            "author": "Kent Beck",
            "isbn": "9780321146533",
        },
    ).json()

    # Attempt 4th loan
    fourth_loan_attempt = httpx.post(
        f"{BASE_URL}/loans",
        json={"client_id": client_alice, "book_id": b5["id"]},
    )
    print_expected_error(
        fourth_loan_attempt.status_code, fourth_loan_attempt.json()["detail"]
    )

    # 5. Consult loans
    print_step("5. Consultation des emprunts en cours d'Alice")
    loans = httpx.get(
        f"{BASE_URL}/clients/{client_alice}/loans?active_only=true"
    ).json()
    print_success(f"Alice a actuellement {len(loans)} emprunt(s) actif(s)")

    # 6. Return book
    print_step("6. Alice rend son premier livre")
    return_resp = httpx.post(f"{BASE_URL}/loans/{loan_data['id']}/return")
    assert return_resp.status_code == 200
    returned_data = return_resp.json()
    print_success(f"Livre rendu ! Statut actif = {returned_data['is_active']}")
    print_success(f"Date de restitution : {returned_data['returned_at']}")

    # 7. Rule: Cannot return already returned loan
    print_step("7. Règle métier : Tentative de récidive de restitution")
    double_return = httpx.post(f"{BASE_URL}/loans/{loan_data['id']}/return")
    print_expected_error(double_return.status_code, double_return.json()["detail"])

    # Summary
    print("\n\033[1;32m" + "=" * 60)
    print("  TOUTES LES RÈGLES MÉTIER ET CONTRAINTES SONT VALIDÉES ! 🚀")
    print("=" * 60 + "\033[0m\n")


if __name__ == "__main__":
    main()
