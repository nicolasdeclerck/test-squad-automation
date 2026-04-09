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

L'environnement Docker éphémère est déjà démarré par le workflow appelant.
Vérifie qu'il est joignable avant de lancer les tests :

```bash
# Forcer Chrome à démarrer sans sandbox dans claude-worker
export AGENT_BROWSER_ARGS=--no-sandbox

agent-browser open "$BASE_URL"
agent-browser wait --load networkidle
agent-browser snapshot -i
```

> **Si l'env n'est pas joignable** : marque tous les scénarios SKIP,
> compile un rapport d'erreur et termine. Le workflow appelant détruira
> l'env de toute façon (`if: always()`).

---

## PHASE 3 — Exécution des tests

### 3.1 Gestion des sessions d'authentification

Utilise des sessions nommées selon le type de test :

- `--session public` pour les tests `[PUBLIC]`
- `--session user1` pour les tests `[AUTH]` (`testuser@example.com` / `Testpass123!`)
- `--session user2` pour les tests `[OWNER]` nécessitant un deuxième utilisateur

Si une session authentifiée n'existe pas encore, connecte-toi d'abord.
**Important** : les refs `@e1`, `@e2`… retournés par `snapshot -i` sont
dynamiques — il faut snapshotter puis utiliser les refs réels (pas de
placeholders type `@emailInput`).

```bash
agent-browser --session user1 open "$BASE_URL/comptes/connexion"
agent-browser --session user1 wait --load networkidle
agent-browser --session user1 snapshot -i
# Lis les refs retournés (ex: @e1 = email, @e2 = password, @e3 = bouton submit)
agent-browser --session user1 fill @e1 "testuser@example.com"
agent-browser --session user1 fill @e2 "Testpass123!"
agent-browser --session user1 click @e3
agent-browser --session user1 wait --load networkidle
```

### 3.2 Exécution d'un scénario

Pour chaque test à exécuter :

1. **Identifie le type** (`[PUBLIC]` / `[AUTH]` / `[OWNER]`) → choisis la session
2. **Suis les étapes** décrites dans le scénario via `agent-browser`
   (open, snapshot, click, fill, wait, get text, etc.)
3. **Vérifie chaque assertion** (présence d'éléments, texte attendu, navigation correcte)
4. **En cas d'échec** : capture un screenshot et enregistre le détail
5. **Enregistre le résultat** : `PASS` / `FAIL` (avec détail) / `SKIP` (avec raison)

```bash
# Exemple générique
agent-browser --session user1 open "$BASE_URL/page-cible"
agent-browser --session user1 wait --load networkidle
agent-browser --session user1 snapshot -i
# Vérifications via agent-browser get text / get url / etc.
agent-browser --session user1 screenshot --full  # En cas d'échec, pour preuve
```

---

## PHASE 4 — Compilation et reporting des résultats

### 4.1 Construction du rapport

Compile pour chaque test :
- ID, titre, type
- Statut : PASS / FAIL / SKIP
- Détail des erreurs si FAIL
- Lien vers le screenshot si capturé

### 4.2 Mode `issue:N` — post du résultat sur l'issue

```bash
# Si TEST_FILTER commençait par "issue:", récupère le numéro
if [[ "$TEST_FILTER" == issue:* ]]; then
  ISSUE_NUM=${TEST_FILTER#issue:}

  # Construis le commentaire avec le tableau de résultats
  gh issue comment "$ISSUE_NUM" --body "## 🧪 Tests browser — résultats

**Branche testée :** \`$BRANCH\`
**Filtre :** \`$TEST_FILTER\`
**Date :** $(date -u '+%Y-%m-%d %H:%M UTC')

| ID | Scénario | Type | Résultat |
|----|----------|------|----------|
[ligne par test]

**Bilan :** ✅ \$PASS_COUNT | ❌ \$FAIL_COUNT | ⏭️ \$SKIP_COUNT sur \$TOTAL tests

[Si des FAIL : section détaillée par test échoué]"

  # Si tous passent, retire le label pending-browser-tests
  if [ "$FAIL_COUNT" = "0" ] && [ "$SKIP_COUNT" = "0" ]; then
    gh issue edit "$ISSUE_NUM" --remove-label 'pending-browser-tests'
    echo "✅ Tous les tests passent — label pending-browser-tests retiré de l'issue $ISSUE_NUM"
  else
    echo "⚠️ Des tests ont échoué/skippé — label pending-browser-tests conservé sur l'issue $ISSUE_NUM"
  fi
fi
```

### 4.3 Mode `all` ou liste explicite — rapport sur stdout

Imprime le rapport sur stdout (visible dans les logs du workflow GH Actions).
Pas de commentaire GitHub posté automatiquement (l'opérateur a déclenché
manuellement, il regarde les logs).

```
═══════════════════════════════════════════════
  RAPPORT TESTS BROWSER ON-DEMAND
═══════════════════════════════════════════════

  Branche  : $BRANCH
  Filtre   : $TEST_FILTER
  Total    : N tests
  ✓ Passed : X
  ✗ Failed : Y
  ○ Skip   : Z

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
