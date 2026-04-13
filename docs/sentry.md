# Gestion des alertes Sentry

Ce projet envoie les erreurs backend (Django) et frontend (React) vers [Sentry](https://sentry.io) via deux projets distincts.

## Projets Sentry

| Projet Sentry | Runtime | Variable d'environnement |
|---------------|---------|--------------------------|
| `blog-backend` | Django | `SENTRY_DSN` (dans `.env.prod`) |
| `blog-frontend` | React + Vite | `VITE_SENTRY_DSN` (dans `.env`, injecte au build) |

Les DSN sont des URLs commencant par `https://<key>@o<org>.ingest.de.sentry.io/<project>`.

## Configuration

### Backend Django

- SDK : `sentry-sdk[django]` (dans `requirements/production.txt`)
- Init : `config/settings/production.py`
- Activation conditionnelle : si `SENTRY_DSN` est defini, sinon desactive

Parametres cles :
- `traces_sample_rate=0.1` — 10% des requetes tracees (performance monitoring)
- `send_default_pii=True` — envoie l'identifiant utilisateur et l'IP
- `environment` — lit `SENTRY_ENV` (defaut : `production`)

### Frontend React

- SDK : `@sentry/react` (dans `frontend/package.json`)
- Init : `frontend/src/main.jsx`
- Le DSN est inline dans le bundle JS au moment du `npm run build` via l'ARG Docker `VITE_SENTRY_DSN`

Parametres cles :
- `tracesSampleRate: 0.1`
- `replayOnErrorSampleRate: 1.0` — session replay sur chaque erreur
- `replaysSessionSampleRate: 0.0` — pas de replay aleatoire hors erreurs

## Alert rules et creation automatique d'issues GitHub

Chaque projet Sentry est configure pour creer automatiquement un ticket GitHub sur une nouvelle erreur high priority.

### Configuration d'une alerte

Dans Sentry : **Alerts → Create Alert → Issue Alert**

1. **Environment** : `production`
2. **When** : `A new issue is created`
3. **Filters** : `The issue's priority is equal or greater than high`
4. **Then** : `Create a new GitHub issue`
   - Integration : installation GitHub de l'organisation
   - Repo : `nicolasdeclerck/test-squad-automation`
   - Labels : `bug`, `sentry`
5. **Rate limit** : `1 action per hour per issue`

### Workflow

1. Une erreur se produit en production
2. Sentry classe automatiquement la priorite (low/medium/high)
3. Si la priorite est >= high, un ticket GitHub est cree avec :
   - Titre reprenant l'exception
   - Body contenant stack trace et lien vers l'issue Sentry
4. Le ticket est traite (fix + PR + merge)
5. L'issue Sentry est resolue manuellement ou automatiquement au prochain release

### Priorisation

Sentry classe les issues selon la frequence, l'impact utilisateur et la gravite :

| Priorite | Declenche une alerte ? | Exemple |
|----------|-----------------------|---------|
| `high` | Oui | Exception non geree en prod, crash recurrent |
| `medium` | Non (par defaut) | Erreur occasionnelle, impact limite |
| `low` | Non | Warning, deprecation, test |

Pour elever artificiellement la priorite d'une categorie, utiliser les [Issue Priority rules](https://docs.sentry.io/product/issues/issue-priority/) dans les settings du projet.

## Depannage

### Les evenements ne remontent pas dans Sentry

1. Verifier que la variable d'environnement est bien presente :
   - Backend : `docker compose -f docker-compose.prod.yml exec django env | grep SENTRY`
   - Frontend : inspecter le bundle JS pour trouver une portion du DSN (`grep <key> dist/assets/*.js`)
2. Verifier qu'aucun adblocker / Enhanced Tracking Protection ne bloque les requetes vers `*.ingest.sentry.io` (Firefox classe Sentry comme tracker)
3. Verifier les [Inbound Filters](https://docs.sentry.io/concepts/data-management/filtering/) du projet Sentry (IPs, navigateurs legacy, etc.)
4. Cote frontend, se rappeler que Vite inline les variables `VITE_*` au **build**, pas au runtime — un changement de DSN necessite un rebuild de l'image `frontend`

### Les alertes ne creent pas de tickets GitHub

1. Verifier que l'integration GitHub est toujours active : **Settings → Integrations → GitHub**
2. Verifier que le token n'a pas expire et que les permissions couvrent le repo cible
3. Verifier dans **Alerts → [votre regle] → History** que l'alerte s'est bien declenchee

## References

- [Documentation SDK Python](https://docs.sentry.io/platforms/python/integrations/django/)
- [Documentation SDK React](https://docs.sentry.io/platforms/javascript/guides/react/)
- [Issue Priority](https://docs.sentry.io/product/issues/issue-priority/)
- [Alert Rules](https://docs.sentry.io/product/alerts/alert-types/#issue-alerts)
