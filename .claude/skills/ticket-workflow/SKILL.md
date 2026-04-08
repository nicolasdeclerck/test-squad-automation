---
name: ticket-workflow
description: Workflow complet de traitement d'un ticket GitHub pour test-squad-automation, de l'analyse initiale jusqu'à l'approbation finale. Gère N cycles de review et corrections via un fichier d'état local (.claude-state.json). Déclencher sur le label "analyze" posé par un humain. Inclut : analyse, plan technique, développement, tests unitaires, PR, code review, tests browser via agent-browser, corrections post-review et post-tests-browser. Un seul label au démarrage (in progress), un seul à la fin (approved).
allowed-tools: Bash(gh:*), Bash(git:*), Bash(docker:*), Bash(agent-browser:*), Bash(npx agent-browser:*), Read, Write, Glob, LS, Edit
---

# Skill : ticket-workflow

Ce skill traite un ticket GitHub de bout en bout en une session continue.
Il utilise un fichier `.claude-state.json` dans le worktree pour persister l'état.
Toutes les phases s'enchaînent directement sans passer par GitHub pour redéclencher.

**Principe :** un seul label déclencheur (`analyze`), posé uniquement par un humain.
Deux changements de labels sur tout le cycle : `in progress` au démarrage,
`approved` à la fin.

**Architecture du skill :** les instructions détaillées de chaque phase sont dans
les fichiers `references/`. Ce fichier ne contient que l'orchestration.

---

## Fichiers de référence

| Fichier | Contenu |
|---------|---------|
| `references/state-management.md` | `write_state()`, structure JSON, gestion erreurs/interruptions |
| `references/phase-1-analyze.md` | Analyse du ticket et du codebase |
| `references/phase-2-plan.md` | Plan technique, tâches atomiques |
| `references/browser-test-planning.md` | Planification TDD des tests browser (cahier + liste du ticket) |
| `references/phase-3-develop.md` | Développement, tests, commit, PR, documentation |
| `references/phase-4-review.md` | Code review automatique |
| `references/phase-5-corrections.md` | Rapport des corrections (code review ET tests browser, unifié) |
| `references/phase-6-browser-tests.md` | Exécution des tests browser via agent-browser |

---

## PHASE 0 — Initialisation et routage

### 0.1 Lecture du ticket

```bash
gh issue view {ISSUE_NUMBER} --json title,body,comments \
  --jq '{title: .title, body: .body, comments: [.comments[] | {author: .author.login, body: .body}]}'
```

### 0.2 Lecture de l'état

Lis le fichier `references/state-management.md` pour la fonction `write_state()`
et la structure du fichier d'état, puis applique la lecture :

```bash
STATE_FILE="$WORKTREE_PATH/.claude-state.json"

if [ -f "$STATE_FILE" ]; then
  PHASE=$(cat "$STATE_FILE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('phase','1'))")
  # ... (voir references/state-management.md pour les autres variables)
else
  PHASE="1"
fi
```

### 0.3 Labels au démarrage

```bash
# Retire le label analyze (posé par l'humain pour déclencher/relancer)
gh issue edit {ISSUE_NUMBER} --remove-label 'analyze'

# Retire le label standby si présent (reprise après interruption)
gh issue edit {ISSUE_NUMBER} --remove-label 'standby' 2>/dev/null || true

# Ajoute in progress uniquement si première exécution (pas de fichier d'état)
if [ "$PHASE" = "1" ] && [ ! -f "$STATE_FILE" ]; then
  gh issue edit {ISSUE_NUMBER} --add-label 'in progress'
fi
```

### 0.4 Création du worktree

Détecte si une branche PR existe déjà pour ce ticket :

```bash
BRANCH_NAME=$(git -C /workspace/test-squad-automation branch -r \
  | grep "origin/feat/issue-{ISSUE_NUMBER}-" | head -1 | xargs | sed 's|origin/||')

WORKTREE_PATH="/workspace/test-squad-automation-issue-{ISSUE_NUMBER}"

if [ -n "$BRANCH_NAME" ]; then
  git -C /workspace/test-squad-automation fetch origin
  git -C /workspace/test-squad-automation worktree add "$WORKTREE_PATH" "$BRANCH_NAME" 2>/dev/null \
    || git -C /workspace/test-squad-automation worktree add "$WORKTREE_PATH" \
       --track -b "$BRANCH_NAME" "origin/$BRANCH_NAME" 2>/dev/null \
    || echo "Worktree déjà existant sur $BRANCH_NAME, réutilisation"
else
  git -C /workspace/test-squad-automation fetch origin
  git -C /workspace/test-squad-automation worktree add "$WORKTREE_PATH" origin/main 2>/dev/null \
    || echo "Worktree déjà existant, réutilisation"
fi

cd "$WORKTREE_PATH"
```

**Critère de sortie :** `git worktree list` affiche `$WORKTREE_PATH`.

### 0.5 Table de routage

**Lis le fichier de référence correspondant à la phase courante, puis exécute-le.**

| Condition | Action |
|---|---|
| Aucun fichier d'état | → Lis `references/phase-1-analyze.md` et exécute Phase 1 |
| `PHASE = 2` | → Lis `references/phase-2-plan.md` et exécute Phase 2 |
| `PHASE = 3` | → Lis `references/phase-3-develop.md` et exécute Phase 3 |
| `PHASE = 4` | → Lis `references/phase-4-review.md` et exécute Phase 4 |
| `PHASE = 5` | → Lis `references/phase-5-corrections.md` et exécute (contexte : code review) |
| `PHASE = 6` | → Lis `references/phase-6-browser-tests.md` et exécute Phase 6 |
| `PHASE = 7` | → Lis `references/phase-5-corrections.md` et exécute (contexte : tests browser) |
| `APPROVED = True` ou `PHASE = done` | → **STOP** : ticket terminé |

> **Important :** Chaque fichier de référence contient les instructions complètes
> de la phase, y compris les transitions vers la phase suivante via `write_state()`.
> Après une transition, lis le fichier de référence de la nouvelle phase et
> enchaîne directement.

---

## Résumé du flux

```
Phase 1 (Analyse)
  ├── Questions bloquantes → commentaire + label help wanted → STOP
  └── Pas de questions → Phase 2 directement

Phase 2 (Plan + cahier de tests browser + liste tests du ticket)
  └── Toujours → Phase 3 directement

Phase 3 (Dev + tests + PR)
  ├── Tests échoués 3x → commentaire + label help wanted → STOP
  └── PR créée → Phase 4 directement

Phase 4 (Code review)
  ├── Approuvée + tests browser prévus → Phase 6 directement
  ├── Approuvée + pas de tests browser → labels finaux + STOP ✅
  ├── Corrections + N_REVIEW < 3 → Phase 5 directement
  └── Corrections + N_REVIEW ≥ 3 → label help wanted → STOP ⚠️

Phase 5 (Rapport corrections — code review OU tests browser)
  └── Toujours → Phase 3 directement (nouveau cycle)

Phase 6 (Tests browser via agent-browser)
  ├── Tous les tests passent → labels finaux + STOP ✅
  ├── Anomalies + N_BROWSER_TEST < 3 → Phase 7 directement (→ phase-5-corrections.md, contexte browser)
  └── Anomalies + N_BROWSER_TEST ≥ 3 → label help wanted → STOP ⚠️
```

**Interactions GitHub :**

| Moment | Interaction |
|--------|-------------|
| Démarrage | Retire `analyze`, ajoute `in progress` |
| Phase 1 | `gh issue comment` (notification : analyse terminée) |
| Phase 1 si bloqué | `gh issue comment` (questions) + `help wanted` → STOP |
| Phase 2 | `gh issue comment` (notification : plan défini + nb tests browser) + MAJ `docs/browser-test-checklist.md` |
| Phase 3 | `gh pr create/edit` + `gh issue comment` (documentation détaillée) |
| Phase 3 si tests KO | `gh issue comment` (erreurs) + `help wanted` → STOP |
| Phase 4 sans tests | `/code-review` + `gh issue comment` (tests browser non requis) |
| Phase 4 avec tests | `/code-review` → Phase 6 |
| Phase 5 | `gh issue comment` (corrections code review ou browser) |
| Phase 6 | `gh issue comment` (démarrage) + `agent-browser` + `gh issue comment` (résultats) |
| Fin | Retire `in progress`, ajoute `approved` |

**Total : 2 changements de labels sur tout le cycle**, quelle que soit la durée.

> **Note :** En cas d'interruption involontaire, voir `references/state-management.md`
> pour la procédure de reprise (label `standby`, commentaire d'arrêt).
