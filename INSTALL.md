# Guide d'installation

## Prerequis

- [Docker](https://docs.docker.com/get-docker/) et Docker Compose (v2+)
- [Node.js](https://nodejs.org/) (v18+) et npm — pour le frontend React et Tailwind CSS

## Installation avec Docker (recommande)

### 1. Cloner le depot

```bash
git clone <url-du-depot>
cd test-squad-automation
```

### 2. Configurer les variables d'environnement

```bash
cp .env.example .env
```

Le fichier `.env.example` contient des valeurs par defaut fonctionnelles pour le developpement. Modifiez-les si necessaire :

| Variable | Description | Valeur par defaut |
|----------|-------------|-------------------|
| `DEBUG` | Mode debug Django | `True` |
| `SECRET_KEY` | Cle secrete Django | `change-me-in-production` |
| `DATABASE_URL` | URL de connexion PostgreSQL | `postgres://blog_user:blog_pass@postgres:5432/blog_db` |
| `REDIS_URL` | URL de connexion Redis | `redis://redis:6379/0` |
| `ALLOWED_HOSTS` | Hotes autorises | `localhost,127.0.0.1` |
| `DJANGO_SETTINGS_MODULE` | Module de settings | `config.settings.development` |
| `POSTGRES_DB` | Nom de la base | `blog_db` |
| `POSTGRES_USER` | Utilisateur PostgreSQL | `blog_user` |
| `POSTGRES_PASSWORD` | Mot de passe PostgreSQL | `blog_pass` |

### 3. Demarrer les services backend

```bash
docker compose up -d
```

Cela demarre 4 services : Django (API), PostgreSQL, Redis et Celery.

### 4. Appliquer les migrations

```bash
docker compose exec django python manage.py migrate
```

### 5. Creer un superutilisateur

```bash
docker compose exec django python manage.py createsuperuser
```

### 6. Installer et lancer le frontend React

```bash
cd frontend
npm install
npm run dev
```

Le serveur de developpement Vite demarre sur [http://localhost:5173](http://localhost:5173). Il proxy automatiquement les appels `/api` et `/media` vers le backend Django (port 8000).

### 7. Acceder a l'application

- **Frontend React** : [http://localhost:5173](http://localhost:5173)
- **API Django** : [http://localhost:8001](http://localhost:8001)
- **Administration Django** : [http://localhost:8001/admin/](http://localhost:8001/admin/)

## Installation locale (sans Docker)

### Prerequis supplementaires

- Python 3.12+
- PostgreSQL 16
- Redis 7

### 1. Creer un environnement virtuel

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
```

### 2. Installer les dependances backend

```bash
pip install -r requirements/development.txt
```

### 3. Installer les dependances frontend

```bash
cd frontend
npm install
```

### 4. Configurer les variables d'environnement

```bash
cp .env.example .env
```

Adaptez `DATABASE_URL` et `REDIS_URL` pour pointer vers vos services locaux :

```
DATABASE_URL=postgres://blog_user:blog_pass@localhost:5432/blog_db
REDIS_URL=redis://localhost:6379/0
```

### 5. Creer la base de donnees

```bash
createdb blog_db
```

### 6. Appliquer les migrations et creer un superutilisateur

```bash
python manage.py migrate
python manage.py createsuperuser
```

### 7. Lancer les serveurs

Dans un premier terminal, lancer le backend Django :

```bash
python manage.py runserver
```

Dans un second terminal, lancer le frontend React :

```bash
cd frontend
npm run dev
```

- **Frontend React** : [http://localhost:5173](http://localhost:5173)
- **API Django** : [http://localhost:8000](http://localhost:8000)

## Lancer les tests

```bash
# Avec Docker
docker compose exec django pytest --cov=apps

# En local
pytest --cov=apps
```

## Services et ports (developpement)

| Service | Role | Port expose |
|---------|------|-------------|
| `django` | API Django (DRF) | 8001 (Docker) / 8000 (local) |
| `postgres` | Base de donnees PostgreSQL | — (interne) |
| `redis` | Cache + broker Celery | 6380 |
| `celery` | Worker asynchrone | — |
| `vite` (local) | Serveur de dev frontend React | 5173 |

## Mise a jour

### Avec Docker

```bash
git pull
docker compose build
docker compose up -d
docker compose exec django python manage.py migrate
cd frontend && npm install
```

### En local

```bash
git pull
pip install -r requirements/development.txt
python manage.py migrate
cd frontend && npm install
```

## Deploiement en production

### Prerequis

- Un serveur Linux avec Docker et Docker Compose installes
- Un reverse proxy Traefik configure (reseau `n8n-traefik_default`)
- Un nom de domaine pointe vers le serveur (par defaut `blog.nickorp.com`)

### 1. Configurer les variables d'environnement

Creer un fichier `.env.prod` a la racine du projet :

```
DEBUG=False
SECRET_KEY=<cle-secrete-forte-et-unique>
DATABASE_URL=postgres://blog_user:<mot-de-passe-fort>@postgres:5432/blog_db
REDIS_URL=redis://redis:6379/0
ALLOWED_HOSTS=blog.nickorp.com
DJANGO_SETTINGS_MODULE=config.settings.production
POSTGRES_DB=blog_db
POSTGRES_USER=blog_user
POSTGRES_PASSWORD=<mot-de-passe-fort>
```

> **Important** : ne jamais commiter `.env.prod`. Le fichier est dans `.gitignore`.

### 2. Construire et demarrer les services

```bash
docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml up -d
```

Les services demarres en production :

| Service | Role |
|---------|------|
| `django` | API Django (Gunicorn, 3 workers) |
| `frontend` | Build React (Vite) et copie dans le volume nginx |
| `nginx` | Reverse proxy, fichiers statiques et media |
| `postgres` | Base de donnees PostgreSQL |
| `redis` | Cache + broker Celery |
| `celery` | Worker asynchrone |

### 3. Appliquer les migrations

```bash
docker compose -f docker-compose.prod.yml exec django python manage.py migrate
```

### 4. Creer un superutilisateur (premier deploiement)

```bash
docker compose -f docker-compose.prod.yml exec django python manage.py createsuperuser
```

### 5. Verifier le deploiement

L'application est accessible via `https://blog.nickorp.com` (HTTPS via Traefik).

### Mise a jour en production

```bash
git pull
docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml up -d
docker compose -f docker-compose.prod.yml exec django python manage.py migrate
```

> **Note** : le build du frontend est automatiquement gere par le service `frontend` dans Docker Compose (voir `docker/frontend/Dockerfile`). Il n'est pas necessaire de lancer `npm install` ou `npm run build` manuellement.

### Architecture de production

```
Client → Traefik (HTTPS/443) → Nginx (80)
                                  ├── /static/  → fichiers statiques Django
                                  ├── /media/   → uploads utilisateurs
                                  └── /*        → Django (Gunicorn:8000)
```

### Securite en production

- `DEBUG=False` obligatoire
- `SECRET_KEY` unique et forte (generer avec `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`)
- HTTPS force via Traefik avec certificat Let's Encrypt
- Cookies securises (`SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`)
- CORS restreint a `https://blog.nickorp.com`
- CSRF trusted origins configure

## Commandes utiles

```bash
# Voir les logs
docker compose logs -f django

# Arreter les services
docker compose down

# Arreter et supprimer les volumes (reset base de donnees)
docker compose down -v

# Creer une migration apres modification des modeles
docker compose exec django python manage.py makemigrations

# Ouvrir un shell Django
docker compose exec django python manage.py shell

# Voir les logs en production
docker compose -f docker-compose.prod.yml logs -f django
docker compose -f docker-compose.prod.yml logs -f nginx
```
