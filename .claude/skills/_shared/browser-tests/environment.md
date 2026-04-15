# Préparation de l'environnement — tests browser

Partagé entre `regression-tests` et `browser-tests-on-demand`.

## Variables d'environnement attendues

| Variable | Description | Source |
|----------|-------------|--------|
| `BASE_URL` | URL frontend (nginx) de l'environnement testé | **injecté par le workflow appelant** (`regression-tests.yml` / `browser-tests.yml`), pas de fallback |
| `API_URL` | URL API de l'environnement testé | idem |

Les deux skills construisent toutes leurs URLs à partir de `BASE_URL` (ex :
`${BASE_URL}/comptes/connexion`). **Pas de fallback** vers la production :
si la variable n'est pas définie, le skill doit échouer immédiatement avec
un message clair. Un fallback silencieux vers la prod a déjà causé un faux
positif "env non joignable" (issue #202) : le skill visait
`https://blog.nickorp.com` au lieu de l'env éphémère.

## Healthcheck initial

Avant de lancer les scénarios, vérifier que l'environnement est joignable.

**Préflight HTTP (rapide, diagnostique)** — boucle de retry avant de lancer
le navigateur, pour absorber les races de démarrage (env juste remonté,
réseau Docker juste attaché) :

```bash
# Retry curl jusqu'à ce que BASE_URL réponde 2xx/3xx (12 tentatives, 10s).
for i in $(seq 1 12); do
  if curl -sSf --max-time 10 -o /dev/null "$BASE_URL/"; then
    echo "Env reachable (attempt $i)."
    break
  fi
  echo "Preflight attempt $i/12 failed, retrying in 10s..."
  sleep 10
  if [ "$i" = "12" ]; then
    echo "ERROR: env non joignable après 12 tentatives (~2 min)."
  fi
done
```

**Check navigateur** (une seule tentative après préflight OK) :

```bash
# Sans sandbox : requis dans claude-worker (root dans container)
export AGENT_BROWSER_ARGS=--no-sandbox

agent-browser open "$BASE_URL" \
  && agent-browser wait --load networkidle \
  && agent-browser snapshot -i
```

**Si l'environnement n'est pas joignable** (préflight curl ET browser échouent) :

- `regression-tests` → créer une issue GitHub dédiée "TNR — env non joignable"
  (labels `non-regression tests`, `env-unreachable`) décrivant le problème,
  puis **STOP**. Ne jamais échouer silencieusement : la visibilité du problème
  est obligatoire même si le workflow amont a déjà remonté l'erreur.
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
