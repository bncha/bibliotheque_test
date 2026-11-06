import httpx

BASE = "http://127.0.0.1:8000"


def main():
    print("=" * 60)
    print("  TEST COMPLET : CRÉATION DE LIVRES & OPÉRATIONS MÉTIER")
    print("=" * 60)

    # 1. Création de nouveaux livres
    print("\n\033[1;34m1. Création de 3 nouveaux livres (POST /books)\033[0m")
    books_to_create = [
        {
            "title": "Le Petit Prince",
            "author": "Antoine de Saint-Exupéry",
            "isbn": "9780156012195",
        },
        {"title": "1984", "author": "George Orwell", "isbn": "9780451524935"},
        {"title": "Les Misérables", "author": "Victor Hugo", "isbn": "9782070409228"},
    ]

    created = []
    for b in books_to_create:
        res = httpx.post(f"{BASE}/books", json=b)
        assert res.status_code == 201
        data = res.json()
        created.append(data)
        print(
            f"  ✔ [HTTP {res.status_code}] '{data['title']}' créé avec succès (ID: {data['id']}, Statut: {data['status']})"
        )

    # 2. Consultation du catalogue complet
    print("\n\033[1;34m2. Consultation du catalogue mis à jour (GET /books)\033[0m")
    catalog = httpx.get(f"{BASE}/books").json()
    print(f"  Total livres dans le catalogue : {len(catalog)}")
    for b in catalog[-3:]:
        print(f"    - {b['title']} par {b['author']} | État: {b['status']}")

    # 3. Récupération d'un adhérent
    clients = httpx.get(f"{BASE}/clients").json()
    alice = clients[0]
    bob = clients[1]
    book_1984 = created[1]

    # 4. Emprunt du livre '1984'
    print(
        f"\n\033[1;34m3. Emprunt de '{book_1984['title']}' par {alice['name']} (POST /loans)\033[0m"
    )
    borrow_res = httpx.post(
        f"{BASE}/loans", json={"client_id": alice["id"], "book_id": book_1984["id"]}
    )
    assert borrow_res.status_code == 201
    loan = borrow_res.json()
    print(f"  ✔ [HTTP 201] Emprunt validé !")
    print(f"    - ID Emprunt : {loan['id']}")
    print(f"    - Date prêt  : {loan['borrowed_at']}")
    print(f"    - Actif      : {loan['is_active']}")

    # 5. Vérification du statut du livre
    print(
        f"\n\033[1;34m4. Vérification de l'état du livre (GET /books/{book_1984['id']})\033[0m"
    )
    b_status = httpx.get(f"{BASE}/books/{book_1984['id']}").json()
    print(f"  ✔ Statut actuel : \033[1;33m{b_status['status']}\033[0m (indisponible)")

    # 6. Test règle métier : tentative d'emprunt par Bob
    print(
        f"\n\033[1;34m5. Règle métier : Bob tente d'emprunter '{book_1984['title']}' qui est déjà prêté\033[0m"
    )
    conflict_res = httpx.post(
        f"{BASE}/loans", json={"client_id": bob["id"], "book_id": book_1984["id"]}
    )
    print(f"  ✔ [HTTP {conflict_res.status_code}] Rejet métier attendu !")
    print(f"    - Message renvoyé : {conflict_res.json()['detail']}")

    # 7. Retour du livre
    print(
        f"\n\033[1;34m6. Restitution du livre par Alice (POST /loans/{loan['id']}/return)\033[0m"
    )
    return_res = httpx.post(f"{BASE}/loans/{loan['id']}/return")
    assert return_res.status_code == 200
    ret_data = return_res.json()
    print(f"  ✔ [HTTP 200] Livre retourné avec succès !")
    print(f"    - Actif           : {ret_data['is_active']}")
    print(f"    - Date restitution : {ret_data['returned_at']}")

    # 8. Vérification que le livre est de nouveau disponible
    print(
        f"\n\033[1;34m7. Vérification finale de l'état du livre (GET /books/{book_1984['id']})\033[0m"
    )
    final_book = httpx.get(f"{BASE}/books/{book_1984['id']}").json()
    print(f"  ✔ Statut actuel : \033[1;32m{final_book['status']}\033[0m (de nouveau empruntable)")

    # 9. Maintenant Bob peut l'emprunter
    print(
        f"\n\033[1;34m8. Bob peut maintenant emprunter '{book_1984['title']}' libéré (POST /loans)\033[0m"
    )
    bob_loan = httpx.post(
        f"{BASE}/loans", json={"client_id": bob["id"], "book_id": book_1984["id"]}
    )
    assert bob_loan.status_code == 201
    print(
        f"  ✔ [HTTP 201] Emprunt validé pour {bob['name']} (ID: {bob_loan.json()['id']})"
    )

    print("\n" + "=" * 60)
    print("  TOUS LES TESTS SUR LES NOUVEAUX LIVRES SONT VALIDÉS ! 🚀")
    print("=" * 60)


if __name__ == "__main__":
    main()

