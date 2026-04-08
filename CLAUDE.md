# CLAUDE.md — Projet Blog Django + React

## Stack technique

| Composant | Technologie | Version |
|-----------|-------------|---------|
| Frontend | React + Vite | 18.x / 6.x |
| UI Components | Mantine | 7.x |
| Éditeur rich text | BlockNote | 0.24.x |
| Backend / API | Django + DRF | 5.x |
| Base de données | PostgreSQL | 16 |
| Cache / Queue broker | Redis | 7 |
| Worker asynchrone | Celery | 5.x |
| CSS | Tailwind CSS | 3.x |
| Déploiement | Docker + Docker Compose | — |

## Architecture du projet

```
project/
├── config/                  # Configuration Django (settings, urls, celery)
│   ├── settings/
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── urls.py
│   └── celery.py
├── apps/
│   ├── blog/                # Articles, commentaires (API REST)
│   │   ├── models.py
│   │   ├── api_views.py     # Vues DRF (APIView)
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   ├── forms.py
│   │   ├── tasks.py         # Tâches Celery (ex: envoi de notifications)
│   │   └── tests/
│   ├── accounts/            # Authentification et profils utilisateurs (API REST)
│   │   ├── models.py
│   │   ├── api_views.py
│   │   ├── serializers.py
│   │   └── tests/
│   └── core/                # Pages statiques, dev tracking GitHub (API REST)
│       ├── api_views.py
│       ├── services.py      # Intégration API GitHub
│       └── views.py
├── frontend/                # Application React (Vite)
│   ├── src/
│   │   ├── components/      # Composants React (blog, accounts, core, layout, ui)
│   │   ├── contexts/        # Contextes React (AuthContext)
│   │   ├── api/             # Client API (fetch + gestion CSRF)
│   │   └── styles/          # Styles Tailwind
│   ├── package.json
│   └── vite.config.js
├── templates/               # Templates HTML Django (admin, fallback)
├── static/                  # Fichiers statiques Django
├── media/                   # Uploads utilisateurs (avatars)
├── docker/
│   ├── django/Dockerfile
│   ├── celery/Dockerfile
│   └── nginx/
├── docker-compose.yml
├── docker-compose.prod.yml
├── requirements/
│   ├── base.txt
│   ├── development.txt
│   └── production.txt
└── manage.py
```

## Modèles de données principaux

```python
# apps/blog/models.py

class Post(models.Model):
    STATUS_DRAFT = 'draft'
    STATUS_PUBLISHED = 'published'
    STATUS_CHOICES = [(STATUS_DRAFT, 'Brouillon'), (STATUS_PUBLISHED, 'Publié')]

    title = models.CharField(max_length=200, blank=True)
    slug = models.SlugField(unique=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    draft_title = models.CharField(max_length=200, blank=True)
    draft_content = models.TextField(blank=True)
    has_draft = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class PostVersion(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='versions')
    version_number = models.PositiveIntegerField()
    title = models.CharField(max_length=200)
    content = models.TextField()
    published_at = models.DateTimeField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    # UniqueConstraint: (post, version_number)
    # ordering: ['-version_number']

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

# apps/accounts/models.py

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True,
                               validators=[validate_avatar])  # 5MB max, JPEG/PNG/WebP
```

## Endpoints API principaux

```
# Blog
/api/blog/posts/                   → Liste et création d'articles
/api/blog/posts/<slug>/            → Détail, mise à jour, suppression
/api/blog/posts/<slug>/autosave/   → Sauvegarde auto du brouillon
/api/blog/posts/<slug>/publish/    → Publication d'un article
/api/blog/posts/<slug>/comments/   → Création de commentaire
/api/blog/comments/<id>/           → Suppression de commentaire
/api/blog/posts/<slug>/versions/   → Liste paginée des versions (auteur uniquement)
/api/blog/posts/<slug>/versions/<version_number>/ → Détail d'une version (auteur uniquement)
/api/blog/posts/<slug>/versions/<version_number>/restore/ → Restauration d'une version comme brouillon

# Accounts
/api/accounts/csrf/                → Token CSRF
/api/accounts/login/               → Connexion
/api/accounts/signup/              → Inscription
/api/accounts/logout/              → Déconnexion
/api/accounts/me/                  → Utilisateur courant
/api/accounts/profile/             → Mise à jour du profil
/api/accounts/avatar/delete/       → Suppression de l'avatar

# Core
/api/core/dev-tracking/            → Suivi des issues GitHub
```

## Conventions de code

### Python / Django
- Respecte PEP8 strictement — utilise `black` pour le formatage (ligne max 88 chars)
- Utilise `isort` pour les imports
- Vues API avec `APIView` et `generics` de DRF (pas de ViewSets/routers)
- Sérializers DRF pour la validation et la sérialisation des données
- Authentification par session (`SessionAuthentication`) avec gestion CSRF
- Les URLs utilisent des slugs, jamais les IDs en clair
- Toujours utiliser `get_object_or_404` pour les vues de détail
- Les migrations doivent être générées et incluses dans chaque PR

### Frontend React
- Composants fonctionnels avec hooks
- Gestion d'état via React Context (AuthContext)
- Client API custom avec gestion automatique du CSRF token
- Routing avec React Router DOM
- UI avec Mantine + Tailwind CSS
- Éditeur rich text avec BlockNote
- Sanitisation HTML avec DOMPurify

### Tests
- Utilise `pytest-django`
- Chaque nouvelle fonctionnalité doit avoir des tests unitaires et d'intégration
- Les factories sont dans `tests/factories.py` de chaque app (utilise `factory_boy`)
- Coverage minimum attendu : 80%
- Lancer les tests : `pytest --cov=apps`

### Celery
- Toutes les tâches asynchrones dans `tasks.py` de l'app concernée
- Utilise `shared_task` de Celery
- Toujours définir `bind=True`, `max_retries=3` et gérer les exceptions

## Configuration CI/CD

### Docker Compose (développement)
```bash
docker compose up -d           # Démarre tous les services (django, postgres, redis, celery)
docker compose exec django python manage.py migrate
docker compose exec django python manage.py createsuperuser
cd frontend && npm install && npm run dev   # Démarre le serveur Vite (port 5173)
```

### Services Docker
| Service | Rôle | Port exposé |
|---------|------|-------------|
| `django` | Serveur Django API (DRF) | 8001 → 8000 |
| `postgres` | Base de données | 5432 (interne) |
| `redis` | Cache + broker Celery | 6380 → 6379 |
| `celery` | Worker asynchrone | — |
| `nginx` | Reverse proxy (prod uniquement) | 80/443 |

Le frontend Vite tourne en dehors de Docker en développement sur le port **5173**.
CORS est configuré pour autoriser `http://localhost:5173`.

### Variables d'environnement
Toujours utiliser un fichier `.env` (non commité). Exemple :
```
DEBUG=True
SECRET_KEY=...
DATABASE_URL=postgres://user:pass@postgres:5432/blog
REDIS_URL=redis://redis:6379/0
ALLOWED_HOSTS=localhost,127.0.0.1
GITHUB_REPO_API_URL=https://api.github.com/repos/...
GITHUB_API_TOKEN=...
```

## Règles de développement

- **Jamais de `SECRET_KEY` ou credentials en dur** dans le code
- **Toujours vérifier les permissions** dans les vues (un auteur ne peut modifier que ses propres articles)
- **Avatars uploadés** : validés (type MIME JPEG/PNG/WebP + taille max 5MB)
- **Slugs** : générés automatiquement depuis le titre via `save()` override sur le modèle Post
- **Pagination** : 10 articles par page (configuré dans `REST_FRAMEWORK` settings)
- Les commentaires nécessitent une modération (`is_approved=False` par défaut)
- Utilise `select_related` et `prefetch_related` pour éviter les requêtes N+1
- **Brouillons** : les articles utilisent `draft_title` / `draft_content` avec auto-save, publiés via `publish()`
