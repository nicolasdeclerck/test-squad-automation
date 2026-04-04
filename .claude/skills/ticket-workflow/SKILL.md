---
name: ticket-workflow
description: Workflow complet de traitement d'un ticket GitHub pour test-squad-automation, de l'analyse initiale jusqu'à l'approbation finale. Gère N cycles de review et corrections via un fichier d'état local (.claude-state.json). Déclencher sur tout événement de label sur un ticket. Inclut : analyse, plan technique, développement, tests, PR, code review, corrections post-review.
allowed-tools: Bash(gh:*), Bash(git:*), Bash(docker:*), Read, Write, Glob, LS, Edit
---

# Skill : ticket-workflow

Ce skill traite un ticket GitHub de bout en bout. Il utilise un fichier
`.claude-state.json` dans le worktree pour persister l'état entre les phases.
Les phases 1→2→3 s'enchaînent directement dans la même session.

---

## PHASE 0 — Initialisation et détection de l'état

### 0.1 Lecture du label déclencheur

```bash
gh issue view {ISSUE_NUMBER} --json labels \
  --jq '[.labels[].name]'
```

Identifie le label qui a déclenché cette exécution parmi :
`analyze`, `to review`, `changes requested`

### 0.2 Lecture de tous les commentaires

```bash
gh issue view {ISSUE_NUMBER} --json title,body,comments \
  --jq '{title: .title, body: .body, comments: [.comments[] | {author: .author.login, body: .body}]}'
```

### 0.3 Détermination de la phase à exécuter

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
| `PHASE = waiting`, pas de réponse après | → **STOP** en attente humaine |
| `PHASE = waiting`, réponse postée après | → **Phase 2** : Plan (avec réponses) |
| `PHASE = 3`, `N_DEV = N_CORRECTIONS` | → **Phase 3** : Développement |
| `PHASE = 4`, label = `to review` | → **Phase 4** : Code review |
| `PHASE = 5`, label = `changes requested` | → **Phase 5** : Rapport corrections |
| `APPROVED = True` | → **STOP** : ticket terminé |

> **En cas d'ambiguïté**, le label déclencheur est prioritaire.

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
gh issue edit {ISSUE_NUMBER} --remove-label 'analyze'
gh issue edit {ISSUE_NUMBER} --add-label 'help wanted'
write_state "waiting"
# → STOP en attente humaine

# Sinon — enchaîner directement vers Phase 2 :
gh issue edit {ISSUE_NUMBER} --remove-label 'analyze'
write_state "2"
# → Exécuter Phase 2 directement (pas de redéclenchement via label)
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

### 2.5 Transition vers Phase 3

```bash
write_state "3"
# → Exécuter Phase 3 directement (pas de redéclenchement via label)
```

---

## PHASE 3 — Développement

### 3.1 Récupération du plan et de la progression

Relit le commentaire de plan depuis les commentaires GitHub et récupère
`CURRENT_TASK` depuis le fichier d'état pour reprendre à la bonne tâche.

Si un commentaire `## 🔄 Corrections demandées` existe, lis-le pour connaître
les corrections spécifiques à apporter — elles priment sur le plan initial
pour les fichiers concernés.

### 3.2 Mise à jour des labels

```bash
gh issue edit {ISSUE_NUMBER} --remove-label 'analyze'
gh api repos/nicolasdeclerck/test-squad-automation/issues/{ISSUE_NUMBER}/labels/go%20for%20dev \
  -X DELETE 2>/dev/null || true
gh api repos/nicolasdeclerck/test-squad-automation/issues/{ISSUE_NUMBER}/labels \
  -X POST -f "labels[]=in progress"
```

### 3.3 Exécution des tâches

Pour chaque tâche depuis `CURRENT_TASK` :

1. Implémente en suivant le plan et les corrections éventuelles
2. Respecte les conventions du `CLAUDE.md`
3. Met à jour la progression dans le fichier d'état :

```bash
CURRENT_TASK=$((CURRENT_TASK + 1))
write_state "3"
```

### 3.4 Tests

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
gh issue edit {ISSUE_NUMBER} --remove-label 'in progress'
gh issue edit {ISSUE_NUMBER} --add-label 'help wanted'
```
→ **STOP**

### 3.5 Commit et push

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

### 3.8 Finalisation

```bash
N_DEV=$((N_DEV + 1))
write_state "4"

# Mise à jour des labels
gh api repos/nicolasdeclerck/test-squad-automation/issues/{ISSUE_NUMBER}/labels/in%20progress \
  -X DELETE 2>/dev/null || true
gh issue edit {ISSUE_NUMBER} --add-label 'to review'

# Nettoyage du worktree
cd /workspace/test-squad-automation
git worktree remove "$WORKTREE_PATH" --force
```

→ **STOP** (attendre label `to review` pour déclencher Phase 4)

---

## PHASE 4 — Code review

### 4.1 Mise à jour de main

```bash
git -C /workspace/test-squad-automation fetch origin
git -C /workspace/test-squad-automation checkout main
git -C /workspace/test-squad-automation reset --hard origin/main
```

### 4.2 Création du worktree de review

```bash
PR_INFO=$(gh pr list --json number,headRefName \
  --jq ".[] | select(.body | contains(\"#{ISSUE_NUMBER}\"))" | head -1)
PR_NUMBER=$(echo "$PR_INFO" | jq -r '.number')
HEAD_BRANCH=$(echo "$PR_INFO" | jq -r '.headRefName')

REVIEW_WORKTREE="/workspace/test-squad-automation-review-{ISSUE_NUMBER}"
git -C /workspace/test-squad-automation worktree add "$REVIEW_WORKTREE" "$HEAD_BRANCH" 2>/dev/null \
  || echo "Worktree de review déjà existant, réutilisation"
cd "$REVIEW_WORKTREE"
```

### 4.3 Lancement de la review

```bash
/code-review --comment
```

### 4.4 Analyse du résultat et mise à jour des labels

**Si aucun problème détecté (aucune issue de confiance ≥ 80) :**

```bash
N_REVIEW=$((N_REVIEW + 1))
APPROVED="True"
write_state "done"

gh pr review "$PR_NUMBER" --approve \
  --body "Code review automatique cycle $N_REVIEW : aucun problème détecté."

gh issue edit {ISSUE_NUMBER} --remove-label 'to review'
gh issue edit {ISSUE_NUMBER} --add-label 'approved'
```

**Si des problèmes sont détectés :**

```bash
N_REVIEW=$((N_REVIEW + 1))
write_state "5"

gh pr review "$PR_NUMBER" --request-changes \
  --body "Code review automatique cycle $N_REVIEW : corrections nécessaires."

gh issue edit {ISSUE_NUMBER} --remove-label 'to review'
gh issue edit {ISSUE_NUMBER} --add-label 'changes requested'
```

### 4.5 Nettoyage

```bash
cd /workspace/test-squad-automation
git worktree remove "$REVIEW_WORKTREE" --force
```

→ **STOP**

---

## PHASE 5 — Rapport des corrections

*Exécutée quand label = `changes requested` et `PHASE = 5`.*

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
gh issue edit {ISSUE_NUMBER} --remove-label 'changes requested'
gh issue edit {ISSUE_NUMBER} --add-label 'analyze'
write_state "3"
# → Exécuter Phase 3 directement (nouveau cycle de développement)
```

### 5.4 Nettoyage du worktree

```bash
cd /workspace/test-squad-automation
git worktree remove "$WORKTREE_PATH" --force 2>/dev/null || true
```

---

## Résumé du flux et des interactions GitHub

```
Phase 1 : Analyse          → write_state "2" → enchaîner Phase 2
Phase 2 : Plan             → write_state "3" → enchaîner Phase 3
Phase 3 : Dev (cycle N)    → write_state "4" + label "to review" → STOP
Phase 4 : Review (cycle N)
  ├── Approuvé             → write_state "done" + label "approved" → STOP ✅
  └── Corrections          → write_state "5" + label "changes requested" → STOP
Phase 5 : Corrections      → write_state "3" + label "analyze" → enchaîner Phase 3
```

**Interactions GitHub par phase :**

|Moment              |Interaction GitHub                                                |
|--------------------|------------------------------------------------------------------|
|Phase 1             |`gh issue comment` (analyse) + labels                             |
|Phase 1 si questions|`gh issue comment` (questions) + label `help wanted`              |
|Phase 2             |`gh issue comment` (plan)                                         |
|Phase 3 démarrage   |label `in progress`                                               |
|Phase 3 fin         |`gh pr create/edit` + `gh issue comment` (doc) + label `to review`|
|Phase 4             |`/code-review --comment` + `gh pr review` + labels                |
|Phase 5             |`gh issue comment` (corrections) + label `analyze`                |

**Invariant à chaque démarrage :**
- `N_DEV = N_CORRECTIONS` → Phase 3 (dev)
- `N_DEV > N_REVIEW` → Phase 4 (review)
- `N_REVIEW > N_CORRECTIONS` → Phase 5 (rapport corrections)
- `APPROVED = True` → STOP
