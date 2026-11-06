Test technique – Gestion d’une bibliothèque
Objectif

Ce test est donné à tous les niveaux, l'important n'est pas de tout faire mais de montrer votre compréhension du code, du travail en équipe et de la structure d'un projet data. Avancez sereinement et donnez le meilleur de vous même ! Il sera suivi d'un échange pour debriefer.

Vous allez concevoir une application simple de gestion de bibliothèque.
L’objectif est d’évaluer votre capacité à :

    structurer un projet collaboratif de manière propre et maintenable,
    modéliser un domaine métier en programmation orientée objet,
    appliquer les bonnes pratiques,
    exposer la logique métier via une API REST.

Le code sera évalué sur la dernière version disponible sur la branche main. Merci de veiller à ce que main reste toujours dans un état fonctionnel et exploitable. Si vous devez effectuer des changements expérimentaux, non terminés ou susceptibles de casser le projet, créez une nouvelle branche dédiée. La branche main doit toujours refléter la dernière version stable et exécutable de votre travail.
Contexte

Vous rejoignez une équipe de développement chargée de concevoir un outil interne de gestion des prêts de livres.
Ce projet est collaboratif : votre travail servira de base à d’autres développeurs.

L’enjeu est donc autant technique que structurel : le code doit être clair, extensible et respecter les principes de développement propres.
Étapes à réaliser

1. Initialisation du projet collaboratif

   Mettez en place la structure de base du projet.
   Configurez les outils de qualité que vous jugez pertinents.
   Ajoutez un fichier README.md décrivant comment installer et exécuter le projet et ce que vous trouverez pertinents.
   Faites un premier commit propre (chore: initial project setup).

Objectif : évaluer votre capacité à structurer un projet pour le travail en équipe. 2. Conception des entités métier

Concevez les trois entités principales :

    Book : représente un livre (titre, auteur, ISBN, état, etc.)
    Client : représente un client pouvant emprunter des livres
    Loan : représente un emprunt entre un client et un livre, avec ses dates

Vous êtes libre de modéliser ces entités et leurs relations comme vous le souhaitez, en respectant les principes SOLID et une approche orientée objet propre. Vous pouvez lire les règles métier pour vous alimenter votre réflexion.

Objectif : évaluer la conception et la clarté du modèle métier. 3. Implémentation des règles métier

Mettez en place la logique de gestion des emprunts et retours.
Les règles suivantes doivent être respectées :

    Un livre ne peut être emprunté que s’il est disponible.
    Un client ne peut pas emprunter plus de 3 livres simultanément.
    Un retour ne peut être effectué que si un emprunt correspondant existe.
    Chaque emprunt doit contenir une date d’emprunt (et de retour lors du rendu).

Objectif : évaluer la gestion d’états cohérents et la robustesse du code. 4. Interactions entre les objets

Ajoutez une couche de coordination (ou de service) permettant de gérer les interactions entre les entités :

    emprunter un livre,
    retourner un livre,
    consulter les emprunts d’un client.

Cette couche doit centraliser la logique sans la dupliquer dans les entités.

Objectif : vérifier la séparation des responsabilités et la structure du code. 5. Exposition de l’API

Exposez la logique métier à travers une API REST.
L’implémentation du framework est libre (FastAPI recommandé mais non obligatoire).

Objectif : évaluer la structuration d’une API claire et cohérente.
Bonnes pratiques attendues

    Code clair, typé et documenté
    Architecture cohérente et extensible
    Commits fréquents, explicites et structurés
    Respect des conventions de style
    Documentation minimale (README clair, instructions d’exécution)

Durée indicative

Environ 1 heure de travail.
L’objectif n’est pas d’obtenir une application complète, mais un socle technique propre, structuré.
Livraison

Le projet doit pouvoir être :

    cloné,
    installé,
    exécuté,
    et testé simplement, à partir du README.

Pensez à vous relire : le dépôt sera lu comme s’il devait être repris par un autre développeur dès demain.
