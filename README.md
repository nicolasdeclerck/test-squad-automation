# Test Squad Automation — Blog Django

Application de blog multi-utilisateur construite avec Django. Elle permet la publication d'articles avec moderation des commentaires, gestion des profils utilisateurs et pages statiques.

## Fonctionnalites principales

- **Gestion d'articles** : creation, edition, publication avec brouillons, categories et tags
- **Commentaires avec moderation** : les commentaires sont soumis a validation avant publication
- **Profils utilisateurs** : inscription, connexion, gestion de profil avec avatar
- **Pages statiques** : a propos, contact, coming soon
- **Taches asynchrones** : envoi de notifications via Celery
- **Interface responsive** : stylisee avec Tailwind CSS

## Stack technique

| Composant | Technologie | Version |
|-----------|-------------|---------|
| Backend | Django | 5.x |
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

## Structure du projet

```
project/
├── config/              # Configuration Django (settings, urls, celery)
│   └── settings/        # Settings par environnement (base, dev, prod)
├── apps/
│   ├── accounts/        # Authentification et profils utilisateurs
│   ├── blog/            # Articles, categories, tags, commentaires
│   └── core/            # Pages statiques et utilitaires partages
├── templates/           # Templates HTML (Tailwind CSS)
├── static/              # Fichiers statiques (CSS, JS)
├── media/               # Uploads utilisateurs (images, avatars)
├── docker/              # Dockerfiles
├── requirements/        # Dependances Python par environnement
├── docker-compose.yml
└── manage.py
```

## Licence

Projet prive — tous droits reserves.
