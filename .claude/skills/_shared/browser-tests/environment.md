# Préparation de l'environnement — tests browser

Partagé entre `regression-tests` et `browser-tests-on-demand`.

## Variables d'environnement attendues

| Variable | Description | Défaut |
|----------|-------------|--------|
| `BASE_URL` | URL frontend (nginx) de l'environnement testé | `https://blog.nickorp.com` (`regression-tests`) / injecté par le workflow (`browser-tests-on-demand`) |
| `API_URL` | URL API de l'environnement testé | idem |

Les deux skills construisent toutes leurs URLs à partir de `BASE_URL` (ex :
`${BASE_URL}/comptes/connexion`).

## Healthcheck initial

Avant de lancer les scénarios, vérifier que l'environnement est joignable :

```bash
# Sans sandbox : requis dans claude-worker (root dans container)
export AGENT_BROWSER_ARGS=--no-sandbox

agent-browser open "$BASE_URL" \
  && agent-browser wait --load networkidle \
  && agent-browser snapshot -i
```

**Si l'environnement n'est pas joignable** :

- `regression-tests` → afficher un message d'erreur et **STOP**.
- `browser-tests-on-demand` → marquer tous les scénarios `SKIP` (raison :
  "env non joignable"), compiler le rapport habituel, terminer avec code 0
  (le workflow appelant détruira l'env via `if: always()`).

## Distinguer erreur infra vs erreur test

Si le healthcheck échoue, **ne pas** noter les scénarios `FAIL` — la cause
est infrastructurelle, pas fonctionnelle. Utiliser `SKIP` + détail, pour
qu'un FAIL massif ne maquille pas un bug réseau.

## Durée de vie de l'environnement

L'environnement Docker éphémère est géré par le **workflow GitHub Actions
appelant** (`regression-tests.yml` ou `browser-tests.yml`). Le skill ne
touche **jamais** à `tnr-docker.sh`.

## Nettoyage final

```bash
agent-browser close --all
```

Le workflow appelant s'occupe du `docker network disconnect` et du
`tnr-docker.sh down` dans une étape `if: always()`.
