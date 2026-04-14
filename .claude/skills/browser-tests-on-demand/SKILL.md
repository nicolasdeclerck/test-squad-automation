---
name: browser-tests-on-demand
description: Exécute un sous-ensemble (ou la totalité) des tests browser définis dans docs/browser-test-checklist.md sur un environnement Docker éphémère, à la demande, via le workflow GitHub Actions browser-tests.yml. Reçoit en entrée la branche à tester (BRANCH) et un filtre de sélection (TEST_FILTER) qui peut être "all", "issue:N" ou une liste comma-séparée d'IDs. Découplé du ticket-workflow pour plus de vélocité.
allowed-tools: Bash(gh:*), Bash(git:*), Bash(agent-browser:*), Bash(npx agent-browser:*), Bash(python3:*), Bash(cat:*), Bash(pkill:*), Bash(grep:*), Bash(awk:*), Bash(sed:*), Read, Write, Glob, LS, Edit
---

# Skill : browser-tests-on-demand

Exécute des scénarios de test browser sur un environnement Docker éphémère
qui a été démarré au préalable par le workflow GitHub Actions appelant
(`.github/workflows/browser-tests.yml`).

**Découplage du ticket-workflow** : ce skill ne fait pas partie du flow
de traitement d'un ticket. Il est invoqué à la demande pour valider les
changements front d'une branche spécifique, avec un sous-ensemble de tests
choisi par l'opérateur.

## Variables d'entrée (env vars injectées par le workflow)

| Variable | Description | Exemple |
|----------|-------------|---------|
| `BRANCH` | Branche Git testée (déjà checked-out côté env) | `feat/issue-174-...` |
| `TEST_FILTER` | Sélection des tests à exécuter | voir § Phase 1.2 |
| `BASE_URL` | URL nginx de l'env éphémère | `http://blog-tnr-nginx-1:80` |
| `API_URL` | URL API de l'env éphémère | `http://blog-tnr-nginx-1:80` |

L'environnement Docker éphémère est démarré et détruit **par le workflow
appelant**. Le skill ne touche jamais à `tnr-docker.sh`.

---

## PHASE 1 — Détermination du périmètre de tests

### 1.1 Lecture et validation des inputs

```bash
echo "=== Browser tests on-demand ==="
echo "BRANCH      : ${BRANCH:-(non défini)}"
echo "TEST_FILTER : ${TEST_FILTER:-(non défini)}"
echo "BASE_URL    : ${BASE_URL:-(non défini)}"
echo "API_URL     : ${API_URL:-(non défini)}"

if [ -z "$BRANCH" ] || [ -z "$TEST_FILTER" ] || [ -z "$BASE_URL" ]; then
  echo "❌ Variables d'entrée manquantes. Arrêt."
  exit 1
fi
```

### 1.2 Résolution du filtre vers une liste d'IDs de tests

`TEST_FILTER` accepte 3 formats :

#### Format `all` — tous les scénarios du checklist

Lit tous les scénarios définis dans `docs/browser-test-checklist.md` et
inclut leurs IDs dans la liste à exécuter.

#### Format `issue:N` — scénarios planifiés pour une issue donnée

Lit le state file du worktree de l'issue N pour récupérer les `browser_tests`
qui ont été planifiés en Phase 2 du `ticket-workflow` :

```bash
ISSUE_NUM=${TEST_FILTER#issue:}
STATE_FILE="/workspace/test-squad-automation-issue-${ISSUE_NUM}/.claude-state.json"

if [ ! -f "$STATE_FILE" ]; then
  echo "❌ Pas de state file trouvé pour l'issue $ISSUE_NUM ($STATE_FILE)"
  echo "L'issue doit avoir été traitée par ticket-workflow au préalable."
  exit 1
fi

TEST_IDS=$(cat "$STATE_FILE" | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(','.join([t['id'] for t in d.get('browser_tests', [])]))
")

if [ -z "$TEST_IDS" ]; then
  echo "❌ Aucun test browser planifié dans le state file de l'issue $ISSUE_NUM."
  exit 1
fi
```

#### Format liste comma-séparée — IDs explicites

Ex : `NAV-01,8.1,8.2`. Le filtre **est** la liste, on l'utilise telle quelle.

### 1.3 Récupération des définitions complètes des tests

Pour chaque ID retenu, lis la définition complète du scénario depuis
`docs/browser-test-checklist.md` : titre, type (`[PUBLIC]`/`[AUTH]`/`[OWNER]`),
étapes détaillées, résultat attendu.

> **Important** : si un ID n'est pas trouvé dans le checklist, marque-le
> SKIP avec le détail "ID inconnu" et continue avec les autres.

---

## PHASE 2 — Préparation de l'environnement

Lis la référence partagée `.claude/skills/_shared/browser-tests/environment.md`
et applique le healthcheck initial. Si l'environnement n'est pas joignable,
marque tous les scénarios `SKIP` et passe à la compilation du rapport.

---

## PHASE 3 — Exécution des tests

### 3.1 Gestion des sessions d'authentification

Lis la référence partagée `.claude/skills/_shared/browser-tests/sessions.md`
pour les conventions de sessions (`public` / `user1` / `user2`) et la
procédure de connexion avec refs dynamiques.

### 3.2 Exécution d'un scénario

Lis la référence partagée `.claude/skills/_shared/browser-tests/execution.md`
pour le pattern d'exécution, les règles d'évaluation (PASS/FAIL/SKIP), la
capture de screenshots et la structure du résultat à conserver.

---

## PHASE 4 — Compilation et reporting des résultats

### 4.1 Agrégation des résultats en mémoire

Pour chaque test exécuté, conserve :
- `id`, `title`, `type`
- `status` : `PASS` / `FAIL` / `SKIP`
- `details` : description du problème si FAIL ou raison si SKIP
- `screenshot` : chemin si capturé
- `url` : URL au moment du test

Calcule les compteurs `PASS_COUNT`, `FAIL_COUNT`, `SKIP_COUNT`, `TOTAL`.

### 4.2 Création de l'issue de suivi GitHub (toujours)

**Une issue de suivi GitHub est créée pour chaque run**, quel que soit le
mode de filtre. Elle constitue l'historique persistant des tests à la demande
et utilise le même label `non-regression tests` que la TNR nightly, pour une
vue unifiée des exécutions de tests.

#### 4.2.1 Construction du corps de l'issue

```bash
# Récupère le numéro de l'issue liée si mode issue:N
LINKED_ISSUE=""
if [[ "$TEST_FILTER" == issue:* ]]; then
  LINKED_ISSUE=${TEST_FILTER#issue:}
fi

# Status global
if [ "$FAIL_COUNT" = "0" ] && [ "$SKIP_COUNT" = "0" ]; then
  STATUS_EMOJI="✅"
  STATUS_TEXT="Tous les tests passent"
elif [ "$FAIL_COUNT" = "0" ]; then
  STATUS_EMOJI="⚠️"
  STATUS_TEXT="Tests passés avec SKIPs"
else
  STATUS_EMOJI="❌"
  STATUS_TEXT="Échecs détectés"
fi

# URL du run GitHub Actions courant (injectée par le workflow caller)
RUN_URL="${GITHUB_SERVER_URL:-https://github.com}/${GITHUB_REPOSITORY:-nicolasdeclerck/test-squad-automation}/actions/runs/${GITHUB_RUN_ID:-}"
```

#### 4.2.2 Création de l'issue avec tableau de résultats

Construis le corps de l'issue avec :
- Header : date, branche, filtre, status global
- Lien vers l'issue parente si mode `issue:N`
- Tableau de résultats (une ligne par test)
- Section détaillée pour chaque FAIL
- Lien vers le run GitHub Actions

Puis crée l'issue avec le label `non-regression tests`.

> **Important :** `gh issue create` ne supporte **pas** `--json` ; il sort
> l'URL de l'issue créée sur stdout. On extrait le numéro de l'URL.

```bash
# Écris d'abord le corps dans un fichier temporaire pour éviter les pièges
# de quoting multi-niveau (backticks, $, guillemets imbriqués).
BODY_FILE=$(mktemp)
{
  echo "## 🧪 Tests browser on-demand"
  echo ""
  echo "**Date :** $(date -u '+%Y-%m-%d %H:%M UTC')"
  echo "**Branche testée :** \`$BRANCH\`"
  echo "**Filtre :** \`$TEST_FILTER\`"
  echo "**Statut :** $STATUS_EMOJI $STATUS_TEXT"
  [ -n "$LINKED_ISSUE" ] && echo "**Issue liée :** #$LINKED_ISSUE"
  echo "**Run GitHub Actions :** $RUN_URL"
  echo ""
  echo "---"
  echo ""
  echo "### Résultats ($PASS_COUNT ✅ / $FAIL_COUNT ❌ / $SKIP_COUNT ⏭️ sur $TOTAL)"
  echo ""
  echo "| ID | Scénario | Type | Résultat |"
  echo "|----|----------|------|----------|"
  # [une ligne par test, emoji selon status]
  # [Si FAIL_COUNT > 0 : section "Détail des échecs" avec un bloc par FAIL]
} > "$BODY_FILE"

ISSUE_URL=$(gh issue create \
  --repo nicolasdeclerck/test-squad-automation \
  --title "Tests browser on-demand — $(date -u '+%Y-%m-%d %H:%M') — ${STATUS_EMOJI}" \
  --label "non-regression tests" \
  --body-file "$BODY_FILE")

TRACKING_ISSUE=$(echo "$ISSUE_URL" | grep -oE '[0-9]+$')

if [ -z "$TRACKING_ISSUE" ]; then
  echo "❌ Impossible d'extraire le numéro d'issue depuis : $ISSUE_URL"
  exit 1
fi

echo "Issue de suivi créée : #$TRACKING_ISSUE"
rm -f "$BODY_FILE"
```

#### 4.2.3 Fermeture de l'issue si tout passe

```bash
if [ "$FAIL_COUNT" = "0" ] && [ "$SKIP_COUNT" = "0" ]; then
  gh issue close "$TRACKING_ISSUE" \
    --repo nicolasdeclerck/test-squad-automation \
    --reason completed
  echo "✅ Issue #$TRACKING_ISSUE fermée (tous les tests passent)"
else
  echo "⚠️ Issue #$TRACKING_ISSUE laissée ouverte (échecs/skips détectés)"
fi
```

### 4.3 Mode `issue:N` — liaison avec l'issue parente

Si `TEST_FILTER` commençait par `issue:`, la tracking issue est liée à une
issue parente (le ticket d'origine). Dans ce cas :

1. Post un commentaire sur l'issue parente qui référence la tracking issue
2. Si tous les tests passent, retire le label `pending-browser-tests` de la parente

```bash
if [ -n "$LINKED_ISSUE" ]; then
  gh issue comment "$LINKED_ISSUE" \
    --repo nicolasdeclerck/test-squad-automation \
    --body "## 🧪 Tests browser exécutés

Les tests browser planifiés pour ce ticket ont été exécutés :

**Résultat :** $STATUS_EMOJI $PASS_COUNT ✅ / $FAIL_COUNT ❌ / $SKIP_COUNT ⏭️ sur $TOTAL tests

Voir l'issue de suivi détaillée : #$TRACKING_ISSUE
Run GitHub Actions : $RUN_URL"

  if [ "$FAIL_COUNT" = "0" ] && [ "$SKIP_COUNT" = "0" ]; then
    gh issue edit "$LINKED_ISSUE" \
      --repo nicolasdeclerck/test-squad-automation \
      --remove-label 'pending-browser-tests'
    echo "✅ Label pending-browser-tests retiré de l'issue #$LINKED_ISSUE"
  else
    echo "⚠️ Label pending-browser-tests conservé sur l'issue #$LINKED_ISSUE (échecs/skips)"
  fi
fi
```

### 4.4 Affichage stdout (toujours)

En plus de la tracking issue, imprime un résumé sur stdout qui sera visible
dans les logs du workflow GitHub Actions :

```
═══════════════════════════════════════════════
  RAPPORT TESTS BROWSER ON-DEMAND
═══════════════════════════════════════════════

  Branche        : $BRANCH
  Filtre         : $TEST_FILTER
  Issue liée     : #$LINKED_ISSUE (si applicable)
  Issue de suivi : #$TRACKING_ISSUE
  Run URL        : $RUN_URL

  Total    : $TOTAL tests
  ✓ Passed : $PASS_COUNT
  ✗ Failed : $FAIL_COUNT
  ○ Skip   : $SKIP_COUNT

───────────────────────────────────────────────
  DÉTAIL DES ÉCHECS
───────────────────────────────────────────────

  [ID] Titre
    Type     : ...
    Détail   : ...
    Capture  : /tmp/...

═══════════════════════════════════════════════
```

---

## PHASE 5 — Nettoyage

```bash
agent-browser close --all
```

> La destruction de l'environnement Docker éphémère est gérée **par le
> workflow GitHub Actions** `browser-tests.yml` (étape `Tear down env`,
> `if: always()`), pas par le skill.

---

## Codes de sortie attendus

- **0** : succès (peu importe les résultats des tests, le skill a fait son job)
- **1** : erreur de configuration (inputs manquants, env non joignable, state file introuvable)

Le statut PASS/FAIL des tests **ne fait pas** échouer le skill — il se reflète
dans le commentaire posté ou le rapport stdout. C'est au workflow appelant ou
à l'opérateur d'agir sur ces résultats.
