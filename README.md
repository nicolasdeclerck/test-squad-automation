# Test Squad Automation — Blog Django

Application de blog multi-utilisateur avec un backend Django (API REST) et un frontend React (Vite). Elle permet la publication d'articles avec moderation des commentaires, gestion des profils utilisateurs et pages statiques.

## Fonctionnalites principales

- **Gestion d'articles** : creation, edition, publication avec brouillons, categories et tags
- **Commentaires avec moderation** : les commentaires sont soumis a validation avant publication
- **Profils utilisateurs** : inscription, connexion, gestion de profil avec avatar
- **Pages statiques** : a propos, contact, coming soon
- **Taches asynchrones** : envoi de notifications via Celery
- **Interface responsive** : frontend React avec Tailwind CSS

## Stack technique

| Composant | Technologie | Version |
|-----------|-------------|---------|
| Frontend | React + Vite | 18.x / 6.x |
| Backend / API | Django + DRF | 5.x |
| Base de donnees | PostgreSQL | 16 |
| Cache / Queue broker | Redis | 7 |
| Worker asynchrone | Celery | 5.x |
| CSS | Tailwind CSS | 3.x |
| Deploiement | Docker + Docker Compose | — |

## Installation

Consultez le [guide d'installation](INSTALL.md) pour les instructions completes (Docker et local).

## Tests

```bash
pytest --cov=apps
```

Voir la section [Lancer les tests](INSTALL.md#lancer-les-tests) dans le guide d'installation pour plus de details.

## Monitoring des erreurs

Les erreurs backend et frontend sont remontees dans Sentry avec creation automatique de tickets GitHub sur erreur high priority. Voir [docs/sentry.md](docs/sentry.md).

## Structure du projet

```
project/
├── config/              # Configuration Django (settings, urls, celery)
│   └── settings/        # Settings par environnement (base, dev, prod)
├── apps/
│   ├── accounts/        # Authentification et profils utilisateurs (API REST)
│   ├── blog/            # Articles, categories, tags, commentaires (API REST)
│   └── core/            # Pages statiques et utilitaires partages (API REST)
├── frontend/            # Application React (Vite)
│   ├── src/
│   │   ├── components/  # Composants React (blog, accounts, layout, ui)
│   │   ├── contexts/    # Contextes React (authentification)
│   │   └── api/         # Client API (fetch + CSRF)
│   ├── package.json
│   └── vite.config.js
├── templates/           # Templates HTML Django (admin, fallback)
├── static/              # Fichiers statiques Django
├── media/               # Uploads utilisateurs (images, avatars)
├── docker/              # Dockerfiles et config Nginx
├── requirements/        # Dependances Python par environnement
├── docker-compose.yml
├── docker-compose.prod.yml
└── manage.py
```

## Licence

Projet prive — tous droits reserves.
