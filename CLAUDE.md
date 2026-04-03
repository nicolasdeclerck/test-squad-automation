# CLAUDE.md — Projet Blog Django

## Stack technique

| Composant | Technologie | Version |
|-----------|-------------|---------|
| Backend | Django | 5.x |
| Base de données | PostgreSQL | 16 |
| Cache / Queue broker | Redis | 7 |
| Worker asynchrone | Celery | 5.x |
| CSS | Tailwind CSS | 3.x |
| Éditeur riche | BlockNote.js | 0.28.x |
| Frontend (éditeur) | React | 18.x |
| Bundler JS | Vite | 6.x |
| Déploiement | Docker + Docker Compose | - |

## Architecture du projet

```
project/
├── frontend/                # Composants React (éditeur BlockNote.js)
│   └── editor.jsx           # Point d'entrée React — éditeur riche
├── config/                  # Paramètres Django (settings, urls, wsgi, asgi)
│   ├── settings/
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── urls.py
│   └── celery.py
├── apps/
│   ├── blog/                # App principale : articles, catégories, tags
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── forms.py
│   │   ├── tasks.py         # Tâches Celery (ex: envoi de notifications)
│   │   └── tests/
│   ├── accounts/            # Authentification et profils utilisateurs
│   │   ├── models.py
│   │   ├── views.py
│   │   └── tests/
│   └── core/                # Utilitaires partagés, middlewares, templatetags
├── templates/               # Templates HTML avec Tailwind
│   ├── base.html
│   ├── blog/
│   └── accounts/
├── static/
│   ├── css/
│   │   └── input.css        # Fichier source Tailwind
│   └── js/
├── media/                   # Uploads utilisateurs (images articles)
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

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

class Tag(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)

class Post(models.Model):
    STATUS_DRAFT = 'draft'
    STATUS_PUBLISHED = 'published'
    STATUS_CHOICES = [(STATUS_DRAFT, 'Brouillon'), (STATUS_PUBLISHED, 'Publié')]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    tags = models.ManyToManyField(Tag, blank=True)
    content = models.TextField()
    excerpt = models.TextField(blank=True)
    cover_image = models.ImageField(upload_to='posts/', blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
```

## Conventions de code

### Python / Django
- Respecte PEP8 strictement — utilise `black` pour le formatage (ligne max 88 chars)
- Utilise `isort` pour les imports
- Toujours utiliser des class-based views (CBV) sauf cas exceptionnels
- Les URLs utilisent des slugs, jamais les IDs en clair
- Toujours utiliser `get_object_or_404` pour les vues de détail
- Les forms Django pour toute validation de données
- Les migrations doivent être générées et incluses dans chaque PR

### Templates
- Tailwind uniquement — pas de CSS custom sauf dans `input.css` pour les directives `@layer`
- Utilise les templatetags Django standards
- Pas de logique métier dans les templates — tout passe par le contexte ou les templatetags

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
docker compose up -d           # Démarre tous les services
docker compose exec django python manage.py migrate
docker compose exec django python manage.py createsuperuser
npx tailwindcss -i ./static/css/input.css -o ./static/css/output.css --watch
```

### Services Docker
| Service | Rôle | Port exposé |
|---------|------|-------------|
| `django` | Serveur Django (gunicorn en prod) | 8000 |
| `postgres` | Base de données | 5432 |
| `redis` | Cache + broker Celery | 6379 |
| `celery` | Worker asynchrone | - |
| `nginx` | Reverse proxy (prod uniquement) | 80/443 |

### Variables d'environnement
Toujours utiliser un fichier `.env` (non commité). Exemple :
```
DEBUG=True
SECRET_KEY=...
DATABASE_URL=postgres://user:pass@postgres:5432/blog
REDIS_URL=redis://redis:6379/0
ALLOWED_HOSTS=localhost,127.0.0.1
```

## Règles de développement

- **Jamais de `SECRET_KEY` ou credentials en dur** dans le code
- **Toujours vérifier les permissions** dans les vues (un auteur ne peut modifier que ses propres articles)
- **Les images uploadées** doivent être validées (type MIME + taille max 5MB)
- **Slugs** : générés automatiquement depuis le titre via `django-autoslug` ou `pre_save` signal
- **Pagination** : 10 articles par page sur les listings
- **SEO** : chaque page doit avoir `<title>` et `<meta description>` dynamiques
- Les commentaires nécessitent une modération (`is_approved=False` par défaut)
- Utilise `select_related` et `prefetch_related` pour éviter les requêtes N+1
