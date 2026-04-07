---
name: ticket-workflow
description: Workflow complet de traitement d'un ticket GitHub pour test-squad-automation, de l'analyse initiale jusqu'à l'approbation finale. Gère N cycles de review et corrections via un fichier d'état local (.claude-state.json). Déclencher sur le label "analyze" posé par un humain. Inclut : analyse, plan technique, développement, tests, PR, code review, corrections post-review. Un seul label au démarrage (in progress), un seul à la fin (approved).
allowed-tools: Bash(gh:*), Bash(git:*), Bash(docker:*), Read, Write, Glob, LS, Edit
---

# Skill : ticket-workflow

Ce skill traite un ticket GitHub de bout en bout en une session continue.
Il utilise un fichier `.claude-state.json` dans le worktree pour persister l'état.
Toutes les phases s'enchaînent directement sans passer par GitHub pour redéclencher.

**Principe :** un seul label déclencheur (`analyze`), posé uniquement par un humain.
Deux changements de labels sur tout le cycle : `in progress` au démarrage,
`approved` à la fin.

---

## PHASE 0 — Initialisation et détection de l'état

### 0.1 Lecture du ticket

```bash
gh issue view {ISSUE_NUMBER} --json title,body,comments \
  --jq '{title: .title, body: .body, comments: [.comments[] | {author: .author.login, body: .body}]}'
```

### 0.2 Détermination de la phase à exécuter

Lit le fichier d'état local pour déterminer la phase courante :

```bash
STATE_FILE="$WORKTREE_PATH/.claude-state.json"

if [ -f "$STATE_FILE" ]; then
  PHASE=$(cat "$STATE_FILE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('phase','1'))")
  N_DEV=$(cat "$STATE_FILE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('n_dev',0))")
  N_REVIEW=$(cat "$STATE_FILE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('n_review',0))")
  N_CORRECTIONS=$(cat "$STATE_FILE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('n_corrections',0))")
  CURRENT_TASK=$(cat "$STATE_FILE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('current_task',0))")
  APPROVED=$(cat "$STATE_FILE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('approved',False))")
else
  # Première exécution
  PHASE="1"
  N_DEV=0
  N_REVIEW=0
  N_CORRECTIONS=0
  CURRENT_TASK=0
  APPROVED="False"
fi
```

**Fonction d'écriture d'état** (à réutiliser après chaque transition) :

```bash
write_state() {
  python3 -c "
import json, sys
state = {
  'issue_number': {ISSUE_NUMBER},
  'phase': '$1',
  'n_dev': $N_DEV,
  'n_review': $N_REVIEW,
  'n_corrections': $N_CORRECTIONS,
  'current_task': $CURRENT_TASK,
  'approved': $APPROVED,
  'branch': '${BRANCH_NAME:-}',
  'pr_number': '${PR_NUMBER:-}'
}
print(json.dumps(state, indent=2))
" > "$STATE_FILE"
}
```

**Table de routage** (basée sur les variables lues du fichier d'état) :

| Condition | Phase à exécuter |
|---|---|
| Aucun fichier d'état | → **Phase 1** : Analyse |
| `PHASE = 2` | → **Phase 2** : Plan |
| `PHASE = 3` | → **Phase 3** : Développement |
| `PHASE = 4` | → **Phase 4** : Code review |
| `PHASE = 5` | → **Phase 5** : Rapport corrections |
| `APPROVED = True` ou `PHASE = done` | → **STOP** : ticket terminé |

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
  # Branche existante : se positionner dessus
  git -C /workspace/test-squad-automation fetch origin
  git -C /workspace/test-squad-automation worktree add "$WORKTREE_PATH" "$BRANCH_NAME" 2>/dev/null \
    || git -C /workspace/test-squad-automation worktree add "$WORKTREE_PATH" \
       --track -b "$BRANCH_NAME" "origin/$BRANCH_NAME" 2>/dev/null \
    || echo "Worktree déjà existant sur $BRANCH_NAME, réutilisation"
else
  # Première fois : depuis origin/main
  git -C /workspace/test-squad-automation fetch origin
  git -C /workspace/test-squad-automation worktree add "$WORKTREE_PATH" origin/main 2>/dev/null \
    || echo "Worktree déjà existant, réutilisation"
fi

cd "$WORKTREE_PATH"
```

**✅ Critère de sortie :** `git worktree list` affiche `$WORKTREE_PATH`.

---

## PHASE 1 — Analyse du ticket

### 1.1 Analyse du contexte codebase

- Lis le `CLAUDE.md` pour comprendre les conventions du projet
- Identifie les apps Django concernées (`apps/`)
- Examine les modèles, vues, URLs et templates liés au besoin
- Repère les patterns existants (CBV, factories de test, etc.)
- Vérifie les dépendances installées (`requirements/`)

### 1.2 Détection des ambiguïtés

Identifie uniquement les points **vraiment bloquants** :
- L'objectif est-il clair et mesurable ?
- Le périmètre est-il délimité (IN vs OUT) ?
- Les critères d'acceptance sont-ils vérifiables ?

Si tu peux faire un choix raisonnable → fais-le et documente-le.

### 1.3 Post du commentaire d'analyse

```bash
gh issue comment {ISSUE_NUMBER} --body "## 🔍 Analyse

[Contexte métier et état actuel du code]

## 📋 Consignes de développement

### Fichiers à créer ou modifier
[Chemins exacts]

### Logique métier
[Description avec extraits si utile]

### Critères d'acceptance
[Liste vérifiable]

### Tests à écrire
[Noms et descriptions]

## 📦 Changements de stack
[Dépendances ou 'Aucun changement']

## ❓ Questions bloquantes
[Liste numérotée ou 'Aucune question']"
```

### 1.4 Gestion des questions bloquantes et transition

```bash
# S'il y a des questions bloquantes :
gh issue comment {ISSUE_NUMBER} --body "[questions détaillées]"
gh issue edit {ISSUE_NUMBER} --add-label 'help wanted'
write_state "1"
# → STOP en attente humaine (l'humain reposera "analyze" après avoir répondu)

# Sinon — enchaîner directement vers Phase 2 :
write_state "2"
# → Exécuter Phase 2 directement
```

---

## PHASE 2 — Plan technique

### 2.1 Récupération des consignes

Relit le commentaire d'analyse posté en Phase 1 depuis les commentaires GitHub.

Si en reprise après réponses, récupère aussi les commentaires postés après
le commentaire d'attente.

### 2.2 Analyse de l'impact

- Fichiers existants à modifier et leurs dépendances
- Complexité de chaque modification
- Risques de régression
- Patterns similaires déjà implémentés à réutiliser

### 2.3 Décomposition en tâches atomiques

Tâches de **moins de 15 minutes**, une par fichier :
- Migrations : toujours une tâche indépendante
- Tests : tâche séparée de l'implémentation
- Ordre : modèle → vue → template → tests
- Principe YAGNI : signaler tout choix dépassant les consignes

### 2.4 Post du commentaire de plan

```bash
gh issue comment {ISSUE_NUMBER} --body "## 🗺️ Plan d'implémentation

**Approche :** [résumé en une phrase]

**Fichiers impactés :** [liste]

## 📝 Tâches

**T1 — [titre]**
- Fichier : \`chemin/exact\`
- Action : créer | modifier
- Description : [détail]
- Critère de validation : [comment vérifier]
- Dépend de : T0 | aucune

[...]

## ⚠️ Points d'attention
[Risques, ordre critique, contraintes]

## 🔬 Stratégie de tests
[Tests prioritaires, fixtures, cas limites]"
```

### 2.5 Mise à jour du cahier de tests browser (TDD)

Avant de démarrer le développement, mets à jour le cahier de tests de non-régression
`docs/browser-test-checklist.md` pour refléter les fonctionnalités à implémenter.

**Principe TDD :** les tests attendus sont écrits **avant** le code, ce qui garantit
que le cahier est toujours synchronisé avec les fonctionnalités de l'application.

**Démarche :**

1. Lis le fichier `docs/browser-test-checklist.md` existant
2. Analyse les tâches du plan (étape 2.3) pour identifier les impacts sur les tests browser :
   - Nouvelle fonctionnalité utilisateur → **ajouter** de nouveaux scénarios de test
   - Modification d'un flux existant → **mettre à jour** les scénarios concernés
   - Suppression d'une fonctionnalité → **retirer** les scénarios obsolètes
   - Nouvel endpoint API consommé par le front → **ajouter** les vérifications associées
   - Changement de comportement UI (formulaire, navigation, permissions) → **adapter** les vérifications
3. Applique les modifications en respectant les conventions du cahier :
   - Tags `[PUBLIC]`, `[AUTH]`, `[OWNER]` selon le niveau d'accès requis
   - Format : action à réaliser + résultat attendu
   - Placement dans la section thématique appropriée (ou création d'une nouvelle section si nécessaire)
   - Si la fonctionnalité implique un parcours complet, ajouter un scénario end-to-end (section 12)
4. Commite la mise à jour du cahier **séparément** du code d'implémentation :

```bash
git add docs/browser-test-checklist.md
git diff --cached --quiet || git commit -m "test: update browser test checklist for #{ISSUE_NUMBER}"
```

**Si aucun changement front-end n'est identifié** (ex : refactoring backend pur,
modification de tâche Celery sans impact UI), cette étape est sautée.

### 2.6 Transition vers Phase 3

```bash
write_state "3"
# → Exécuter Phase 3 directement
```

---

## PHASE 3 — Développement

### 3.1 Récupération du plan et de la progression

Relit le commentaire de plan depuis les commentaires GitHub et récupère
`CURRENT_TASK` depuis le fichier d'état pour reprendre à la bonne tâche.

Si un commentaire `## 🔄 Corrections demandées` existe, lis-le pour connaître
les corrections spécifiques à apporter — elles priment sur le plan initial
pour les fichiers concernés.

### 3.2 Exécution des tâches

Pour chaque tâche depuis `CURRENT_TASK` :

1. Implémente en suivant le plan et les corrections éventuelles
2. Respecte les conventions du `CLAUDE.md`
3. Met à jour la progression dans le fichier d'état :

```bash
CURRENT_TASK=$((CURRENT_TASK + 1))
write_state "3"
```

### 3.3 Tests

```bash
docker compose up -d
docker compose exec -T django pip install -r requirements/development.txt -q
docker compose exec -T django pytest --cov=apps
docker compose stop
```

En cas d'échec : corriger le code, relancer. Maximum **3 tentatives**.

Si toujours en échec après 3 tentatives :
```bash
gh issue comment {ISSUE_NUMBER} --body "## ❌ Échec des tests après 3 tentatives
[logs d'erreur]
Intervention humaine requise."
gh issue edit {ISSUE_NUMBER} --add-label 'help wanted'
```
→ **STOP** (l'humain reposera `analyze` après avoir corrigé)

### 3.4 Commit et push

```bash
git config --global user.email "claude-worker@squad-automation.fr"
git config --global user.name "Claude Worker"

BRANCH_NAME="feat/issue-{ISSUE_NUMBER}-{slug-du-titre}"

# Vérifie si la branche existe déjà sur le remote
if git -C /workspace/test-squad-automation ls-remote --exit-code --heads origin "$BRANCH_NAME" > /dev/null 2>&1; then
  echo "Branche existante, commit sur $BRANCH_NAME"
else
  git checkout -b "$BRANCH_NAME"
fi

git add -A
git diff --cached --quiet || git commit -m "feat: close #{ISSUE_NUMBER} - {titre}"
git push origin "$BRANCH_NAME"
```

### 3.5 Vérification de la documentation

Après chaque implémentation, vérifie si les fichiers de documentation du projet
nécessitent des mises à jour en fonction des changements réalisés :

- **`CLAUDE.md`** : stack technique, modèles, endpoints API, conventions, architecture
- **`README.md`** : fonctionnalités, stack, structure du projet
- **`INSTALL.md`** : nouvelles dépendances, variables d'environnement, étapes d'installation

Pour chaque fichier, compare le contenu actuel avec les changements apportés.
Si une mise à jour est nécessaire, applique-la directement (pas de commentaire GitHub).

Exemples de changements déclencheurs :
- Nouveau modèle ou champ → mettre à jour la section modèles de `CLAUDE.md`
- Nouvel endpoint API → mettre à jour la section endpoints de `CLAUDE.md`
- Nouvelle dépendance Python/JS → mettre à jour `INSTALL.md` et la stack dans `README.md`/`CLAUDE.md`
- Nouvelle variable d'environnement → mettre à jour `INSTALL.md` et `CLAUDE.md`
- Nouvelle app ou dossier → mettre à jour l'arborescence dans `CLAUDE.md` et `README.md`
- Nouvelle fonctionnalité utilisateur → mettre à jour les fonctionnalités dans `README.md`

### 3.6 Commentaire de documentation

```bash
gh issue comment {ISSUE_NUMBER} --body "## 📝 Documentation

### Ce qui a été implémenté
[Résumé des fichiers créés/modifiés]

### Choix techniques
[Décisions importantes et pourquoi]

### Comment utiliser
[Guide pratique]

### Points d'attention
[Limitations, prérequis]"
```

### 3.7 Pull Request

```bash
EXISTING_PR=$(gh pr list --head "$BRANCH_NAME" --json number --jq '.[0].number' 2>/dev/null)

if [ -n "$EXISTING_PR" ]; then
  gh pr edit "$EXISTING_PR" \
    --body "## Description

Closes #{ISSUE_NUMBER}

---

## Documentation

[contenu du commentaire de doc]"
  echo "PR #$EXISTING_PR mise à jour."
else
  gh pr create \
    --title "feat: {titre du ticket}" \
    --body "## Description

Closes #{ISSUE_NUMBER}

---

## Documentation

[contenu du commentaire de doc]" \
    --base main \
    --head "$BRANCH_NAME"
fi
```

### 3.8 Transition vers Phase 4

```bash
N_DEV=$((N_DEV + 1))
write_state "4"
# → Exécuter Phase 4 directement
```

---

## PHASE 4 — Code review

### 4.1 Lancement de la review

```bash
/code-review --comment
```

### 4.2 Analyse du résultat

**Si aucun problème détecté (aucune issue de confiance ≥ 80) :**

```bash
N_REVIEW=$((N_REVIEW + 1))
APPROVED="True"
write_state "done"

gh pr review "$PR_NUMBER" --approve \
  --body "Code review automatique cycle $N_REVIEW : aucun problème détecté."

# Labels finaux
gh issue edit {ISSUE_NUMBER} --remove-label 'in progress'
gh issue edit {ISSUE_NUMBER} --add-label 'approved'
```

→ **STOP** ✅ Ticket terminé.

**Si des problèmes sont détectés :**

```bash
N_REVIEW=$((N_REVIEW + 1))
write_state "5"

gh pr review "$PR_NUMBER" --request-changes \
  --body "Code review automatique cycle $N_REVIEW : corrections nécessaires."
```

→ Exécuter Phase 5 directement

### 4.3 Nettoyage

```bash
cd /workspace/test-squad-automation
git worktree remove "$REVIEW_WORKTREE" --force 2>/dev/null || true
```

---

## PHASE 5 — Rapport des corrections

### 5.1 Récupération des feedbacks de la PR

```bash
PR_NUMBER=$(gh pr list --json number \
  --jq ".[] | select(.body | contains(\"#{ISSUE_NUMBER}\")) | .number" | head -1)

gh pr view "$PR_NUMBER" \
  --json reviews,comments \
  --jq '{
    reviews: [.reviews[] | {author: .author.login, state: .state, body: .body}],
    comments: [.comments[] | {author: .author.login, body: .body}]
  }'
```

### 5.2 Post du commentaire de corrections sur le ticket

```bash
N_CORRECTIONS=$((N_CORRECTIONS + 1))

gh issue comment {ISSUE_NUMBER} --body "## 🔄 Corrections demandées — cycle $N_CORRECTIONS

[Synthèse structurée de chaque correction demandée dans la review]
[Extraits de code concernés si mentionnés]"
```

### 5.3 Transition vers Phase 3

```bash
write_state "3"
# → Exécuter Phase 3 directement (nouveau cycle de développement)
```

---

## Résumé du flux et des interactions GitHub

```
Phase 1 (Analyse)
  ├── Questions bloquantes → commentaire + label help wanted → STOP
  └── Pas de questions → write_state("2") → Phase 2 directement

Phase 2 (Plan + mise à jour cahier de tests browser)
  └── Toujours → write_state("3") → Phase 3 directement

Phase 3 (Dev + tests + PR)
  ├── Tests échoués 3x → commentaire + label help wanted → STOP
  └── PR créée → write_state("4") → Phase 4 directement

Phase 4 (Code review)
  ├── Approuvée → write_state("done") → labels finaux + STOP ✅
  └── Corrections → write_state("5") → Phase 5 directement

Phase 5 (Rapport corrections)
  └── Toujours → write_state("3") → Phase 3 directement (nouveau cycle)
```

**Interactions GitHub :**

|Moment             |Interaction                                          |
|-------------------|-----------------------------------------------------|
|Démarrage          |Retire `analyze`, ajoute `in progress`               |
|Phase 1            |`gh issue comment` (analyse)                         |
|Phase 1 si bloqué  |`gh issue comment` (questions) + `help wanted` → STOP|
|Phase 2            |`gh issue comment` (plan) + MAJ `docs/browser-test-checklist.md`|
|Phase 3            |`gh pr create/edit` + `gh issue comment` (doc)       |
|Phase 3 si tests KO|`gh issue comment` (erreurs) + `help wanted` → STOP  |
|Phase 4            |`/code-review --comment` (automatique)               |
|Phase 5            |`gh issue comment` (corrections)                     |
|Fin                |Retire `in progress`, ajoute `approved`              |

**Total : 2 changements de labels sur tout le cycle**, quelle que soit la durée.

> **Note :** En cas d'interruption involontaire (ex : dépassement des quotas de tokens
> de Claude Code), le flux appelant (GitHub Actions) doit ajouter le label `standby`
> au ticket et poster un commentaire expliquant l'arrêt. Le fichier `.claude-state.json`
> permet de reprendre exactement où l'exécution s'est arrêtée.

## Structure de `.claude-state.json`

```json
{
  "issue_number": 42,
  "phase": "3",
  "n_dev": 0,
  "n_review": 0,
  "n_corrections": 0,
  "current_task": 2,
  "branch": "feat/issue-42-ma-feature",
  "pr_number": "15",
  "approved": false
}
```

Phases possibles : `"1"`, `"2"`, `"3"`, `"4"`, `"5"`, `"done"`

---

## Gestion des erreurs — Interruption par quota de tokens

Si l'exécution de Claude Code est interrompue (ex : dépassement du quota de tokens),
le flux appelant (GitHub Actions, script manuel) **doit** exécuter les actions
suivantes pour signaler l'arrêt :

```bash
# 1. Ajouter le label "standby" au ticket
gh issue edit {ISSUE_NUMBER} --add-label 'standby'

# 2. Poster un commentaire explicatif
gh issue comment {ISSUE_NUMBER} --body "## ⚠️ Exécution interrompue

Les travaux ont été stoppés suite au dépassement des quotas de tokens de Claude Code.

**Phase en cours :** {phase courante depuis .claude-state.json}
**Date :** $(date -u '+%Y-%m-%d %H:%M UTC')

L'exécution reprendra automatiquement à la phase interrompue grâce au fichier d'état
\`.claude-state.json\`. Pour relancer, reposer le label \`analyze\` sur le ticket."
```

**Détection de l'erreur :** Le processus Claude Code retourne un code de sortie
non-zéro en cas d'interruption. Le flux appelant doit vérifier ce code de retour
et déclencher la procédure ci-dessus.

**Reprise :** Lorsque le label `analyze` est reposé, le workflow reprend grâce
à la table de routage de la Phase 0 qui lit `.claude-state.json` et redémarre
à la bonne phase. Le label `standby` est retiré au redémarrage.

```bash
# À ajouter dans la Phase 0.3, après le retrait du label analyze :
gh issue edit {ISSUE_NUMBER} --remove-label 'standby' 2>/dev/null || true
```
