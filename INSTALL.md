# Guide d'installation

## Prerequis

- [Docker](https://docs.docker.com/get-docker/) et Docker Compose (v2+)
- [Node.js](https://nodejs.org/) (v18+) et npm — pour la compilation Tailwind CSS

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

### 3. Demarrer les services

```bash
docker compose up -d
```

Cela demarre 4 services : Django, PostgreSQL, Redis et Celery.

### 4. Appliquer les migrations

```bash
docker compose exec django python manage.py migrate
```

### 5. Creer un superutilisateur

```bash
docker compose exec django python manage.py createsuperuser
```

### 6. Installer et compiler Tailwind CSS

```bash
npm install
npx tailwindcss -i ./static/css/input.css -o ./static/css/output.css
```

Pour le developpement avec recompilation automatique :

```bash
npx tailwindcss -i ./static/css/input.css -o ./static/css/output.css --watch
```

### 7. Acceder a l'application

- Application : [http://localhost:8001](http://localhost:8001)
- Administration Django : [http://localhost:8001/admin/](http://localhost:8001/admin/)

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

### 2. Installer les dependances

```bash
pip install -r requirements/development.txt
npm install
```

### 3. Configurer les variables d'environnement

```bash
cp .env.example .env
```

Adaptez `DATABASE_URL` et `REDIS_URL` pour pointer vers vos services locaux :

```
DATABASE_URL=postgres://blog_user:blog_pass@localhost:5432/blog_db
REDIS_URL=redis://localhost:6379/0
```

### 4. Creer la base de donnees

```bash
createdb blog_db
```

### 5. Appliquer les migrations et creer un superutilisateur

```bash
python manage.py migrate
python manage.py createsuperuser
```

### 6. Compiler Tailwind CSS

```bash
npx tailwindcss -i ./static/css/input.css -o ./static/css/output.css --watch
```

### 7. Lancer le serveur

```bash
python manage.py runserver
```

L'application est accessible sur [http://localhost:8000](http://localhost:8000).

## Lancer les tests

```bash
# Avec Docker
docker compose exec django pytest --cov=apps

# En local
pytest --cov=apps
```

## Services et ports

| Service | Role | Port expose |
|---------|------|-------------|
| `django` | Serveur Django | 8001 |
| `postgres` | Base de donnees PostgreSQL | — (interne) |
| `redis` | Cache + broker Celery | 6380 |
| `celery` | Worker asynchrone | — |

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
```
