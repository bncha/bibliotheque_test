# Système de Gestion d'une Bibliothèque

Application de gestion de prêts de livres conçue selon les principes de la **Clean Architecture** (architecture en couches) avec **Python 3.13** et **FastAPI**.

---

## 🏛️ Architecture du Projet

Le projet suit une séparation stricte des responsabilités sans couplage ascendant :

```
src/library/
├── domain/                  # 1. Cœur métier (Pur Python, sans framework)
│   ├── models.py            # Entités métier : Book, Client, Loan
│   └── exceptions.py        # Exceptions métier (MaxLoansReachedError, BookNotAvailableError...)
├── services/                # 2. Logique applicative & Orchestration
│   ├── library_service.py   # Règles de gestion des emprunts et retours
│   └── repository.py        # Abstractions et stockage en mémoire (In-Memory)
└── api/                     # 3. Couche d'exposition (FastAPI)
    ├── schemas.py           # Modèles Pydantic de requêtes/réponses
    ├── routes.py            # Endpoints REST (/loans, /books, /clients)
    └── main.py              # Application FastAPI, gestionnaires d'erreurs HTTP
```

### Règles métier appliquées
1. **Disponibilité** : Un livre ne peut être emprunté que s'il est disponible.
2. **Quota d'emprunts** : Un client ne peut pas emprunter plus de **3 livres simultanément**.
3. **Validité du retour** : Un retour ne peut être effectué que sur un emprunt actif existant.
4. **Traçabilité** : Chaque emprunt horodate la date de prêt et la date de retour.

---

## 🚀 Prérequis

- **Python 3.13+**

---

## ⚙️ Installation

1. **Cloner le dépôt ou se placer dans le projet** :
   ```bash
   cd "bibliotheque test"
   ```

2. **Créer et activer l'environnement virtuel** :
   ```bash
   python3.13 -m venv .venv
   source .venv/bin/activate
   ```

3. **Installer les dépendances en mode éditable avec les outils de dev** :
   ```bash
   pip install -e ".[dev]"
   ```

---

## ▶️ Démarrage de l'API

Lancer le serveur de développement Uvicorn :

```bash
uvicorn library.api.main:app --reload
```

L'API est alors accessible sur :
- **Documentation interactive (Swagger UI)** : [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Documentation alternative (ReDoc)** : [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- **Point de contrôle de santé** : [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

> 💡 Des données de démonstration (livres et clients préenregistrés) sont automatiquement initialisées au démarrage pour tester directement dans le Swagger.

---

## 🧪 Tests et Qualité de code

### Exécuter le scénario complet de démo (serveur lancé)
```bash
python scripts/demo_scenario.py
# ou: make demo
```

### Exécuter les tests unitaires et d'intégration
```bash
pytest -v
# Avec rapport de couverture :
pytest --cov=src/library --cov-report=term-missing
```

### Vérifier le style et le formatage du code
```bash
ruff check src tests
ruff format --check src tests
```

---

## 📡 Endpoints REST Principaux

| Méthode | Endpoint | Description | Réponses types |
|---|---|---|---|
| `POST` | `/loans` | Emprunter un livre | `201 Created` / `400 Bad Request` / `404 Not Found` |
| `POST` | `/loans/{id}/return` | Rendre un livre emprunté | `200 OK` / `400 Bad Request` / `404 Not Found` |
| `GET` | `/clients/{id}/loans` | Voir les emprunts d'un client | `200 OK` / `404 Not Found` |
| `POST` | `/books` | Ajouter un nouveau livre | `201 Created` |
| `GET` | `/books` | Lister les livres | `200 OK` |
| `POST` | `/clients` | Inscrire un client | `201 Created` |
| `GET` | `/clients` | Lister les clients | `200 OK` |

### Exemple : Emprunter un livre
```bash
curl -X POST "http://127.0.0.1:8000/loans" \
  -H "Content-Type: application/json" \
  -d '{"client_id": "client-1", "book_id": "book-1"}'
```

### Exemple : Rendre un livre
```bash
curl -X POST "http://127.0.0.1:8000/loans/<ID_EMPRUNT>/return"
```

### Exemple : Voir les emprunts actifs d'un client
```bash
curl -X GET "http://127.0.0.1:8000/clients/client-1/loans?active_only=true"
```
