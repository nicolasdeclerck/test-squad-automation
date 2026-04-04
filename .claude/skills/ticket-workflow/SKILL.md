---
name: ticket-workflow
description: Workflow complet de traitement d'un ticket GitHub pour test-squad-automation, de l'analyse initiale jusqu'à l'approbation finale. Gère N cycles de review et corrections via des marqueurs d'état dans les commentaires GitHub. Déclencher sur tout événement de label sur un ticket. Inclut : analyse, plan technique, développement, tests, PR, code review, corrections post-review.
allowed-tools: Bash(gh:*), Bash(git:*), Bash(docker:*), Read, Write, Glob, LS, Edit
---

# Skill : ticket-workflow

Ce skill traite un ticket GitHub de bout en bout. Il est **stateless par design** :
à chaque exécution il relit les commentaires du ticket, détecte la phase courante
via des marqueurs HTML invisibles, et reprend exactement là où il s'est arrêté.

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

Analyse les marqueurs présents dans les commentaires et le label déclencheur
pour déterminer la phase à exécuter.

**Règle de comptage pour les cycles multiples :**
- `N_DEV` = nombre de marqueurs `STATE:DEV_DONE` dans les commentaires
- `N_REVIEW` = nombre de marqueurs `STATE:REVIEW_DONE` dans les commentaires
- `N_CORRECTIONS` = nombre de marqueurs `STATE:CORRECTIONS_REPORTED` dans les commentaires

| Condition | Phase à exécuter |
|---|---|
| Aucun marqueur | → **Phase 1** : Analyse |
| `STATE:ANALYSIS_DONE`, pas de `STATE:PLAN_DONE` | → **Phase 2** : Plan |
| `STATE:WAITING_FOR_ANSWERS`, pas de réponse après | → **STOP** en attente humaine |
| `STATE:WAITING_FOR_ANSWERS`, réponse postée après | → **Phase 2** : Plan (avec réponses) |
| `STATE:PLAN_DONE`, `N_DEV = N_CORRECTIONS` | → **Phase 3** : Développement |
| `STATE:DEV_DONE`, label = `to review`, `N_REVIEW = N_DEV - 1` | → **Phase 4** : Code review |
| `STATE:REVIEW_DONE`, label = `changes requested`, `N_CORRECTIONS = N_REVIEW - 1` | → **Phase 5** : Rapport corrections |
| `STATE:CORRECTIONS_REPORTED`, `N_DEV = N_CORRECTIONS` | → **Phase 3** : Développement (cycle N+1) |
| `STATE:REVIEW_APPROVED` présent | → **STOP** : ticket terminé |

> **En cas d'ambiguïté**, le label déclencheur est prioritaire sur les marqueurs.

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
[Liste numérotée ou 'Aucune question']

<!-- STATE:ANALYSIS_DONE -->"
```

### 1.4 Mise à jour des labels

```bash
gh issue edit {ISSUE_NUMBER} --remove-label 'analyze'
```

```bash
# S'il y a des questions bloquantes :
gh issue edit {ISSUE_NUMBER} --add-label 'help wanted'
gh issue comment {ISSUE_NUMBER} --body "<!-- STATE:WAITING_FOR_ANSWERS -->
⏳ En attente de réponses avant de continuer."

# Sinon — redéclenche automatiquement en Phase 2 :
gh issue edit {ISSUE_NUMBER} --add-label 'analyze'
```

### 1.5 Nettoyage du worktree

```bash
cd /workspace/test-squad-automation
git worktree remove "$WORKTREE_PATH" --force
```

---

## PHASE 2 — Plan technique

### 2.1 Récupération des consignes

```bash
gh issue view {ISSUE_NUMBER} --json comments \
  --jq '.comments[] | select(.body | contains("STATE:ANALYSIS_DONE"))' | tail -1
```

Si en reprise après réponses, récupère aussi les commentaires postés après
`<!-- STATE:WAITING_FOR_ANSWERS -->`.

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
[Tests prioritaires, fixtures, cas limites]

<!-- STATE:PLAN_DONE -->
<!-- PLAN_TASK_COUNT:[N] -->
<!-- PLAN_CURRENT_TASK:0 -->"
```

### 2.5 Mise à jour des labels — redéclenche Phase 3

```bash
gh issue edit {ISSUE_NUMBER} --remove-label 'analyze'
gh issue edit {ISSUE_NUMBER} --add-label 'analyze'
```

### 2.6 Nettoyage du worktree

```bash
cd /workspace/test-squad-automation
git worktree remove "$WORKTREE_PATH" --force
```

---

## PHASE 3 — Développement

### 3.1 Récupération du plan et de la progression

```bash
gh issue view {ISSUE_NUMBER} --json comments \
  --jq '.comments[] | select(.body | contains("STATE:PLAN_DONE"))' | tail -1
```

Extrais `PLAN_TASK_COUNT` et `PLAN_CURRENT_TASK` pour reprendre à la bonne tâche.

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

Pour chaque tâche depuis `PLAN_CURRENT_TASK` :

1. Implémente en suivant le plan et les corrections éventuelles
2. Respecte les conventions du `CLAUDE.md`
3. Poste un marqueur de progression après chaque tâche :

```bash
gh issue comment {ISSUE_NUMBER} --body "<!-- STATE:TASK_PROGRESS -->
<!-- PLAN_CURRENT_TASK:[N+1] -->
✅ T[N] complétée : [titre]"
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
gh issue comment {ISSUE_NUMBER} --body "<!-- STATE:TESTS_FAILED -->
## ❌ Échec des tests après 3 tentatives
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
# Compte les cycles précédents pour numéroter
N_DEV=$(gh issue view {ISSUE_NUMBER} --json comments \
  --jq '[.comments[].body | select(contains("STATE:DEV_DONE"))] | length')

gh issue comment {ISSUE_NUMBER} --body "<!-- STATE:DEV_DONE -->
<!-- DEV_CYCLE:$((N_DEV + 1)) -->
🎉 Cycle de développement $((N_DEV + 1)) terminé."

# Mise à jour des labels
gh api repos/nicolasdeclerck/test-squad-automation/issues/{ISSUE_NUMBER}/labels/in%20progress \
  -X DELETE 2>/dev/null || true
gh issue edit {ISSUE_NUMBER} --add-label 'to review'

# Nettoyage du worktree
cd /workspace/test-squad-automation
git worktree remove "$WORKTREE_PATH" --force
```

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

```bash
# Compte le cycle de review en cours
N_REVIEW=$(gh issue view {ISSUE_NUMBER} --json comments \
  --jq '[.comments[].body | select(contains("STATE:REVIEW_DONE"))] | length')
```

**Si aucun problème détecté (aucune issue de confiance ≥ 80) :**

```bash
gh pr review "$PR_NUMBER" --approve \
  --body "Code review automatique cycle $((N_REVIEW + 1)) : aucun problème détecté."

gh issue comment {ISSUE_NUMBER} --body "<!-- STATE:REVIEW_DONE -->
<!-- STATE:REVIEW_APPROVED -->
<!-- REVIEW_CYCLE:$((N_REVIEW + 1)) -->
✅ Review cycle $((N_REVIEW + 1)) : approuvée."

gh issue edit {ISSUE_NUMBER} --remove-label 'to review'
gh issue edit {ISSUE_NUMBER} --add-label 'approved'
```

**Si des problèmes sont détectés :**

```bash
gh pr review "$PR_NUMBER" --request-changes \
  --body "Code review automatique cycle $((N_REVIEW + 1)) : corrections nécessaires."

gh issue comment {ISSUE_NUMBER} --body "<!-- STATE:REVIEW_DONE -->
<!-- REVIEW_CYCLE:$((N_REVIEW + 1)) -->
🔍 Review cycle $((N_REVIEW + 1)) : corrections demandées."

gh issue edit {ISSUE_NUMBER} --remove-label 'to review'
gh issue edit {ISSUE_NUMBER} --add-label 'changes requested'
```

### 4.5 Nettoyage

```bash
cd /workspace/test-squad-automation
git worktree remove "$REVIEW_WORKTREE" --force
```

---

## PHASE 5 — Rapport des corrections

*Exécutée quand label = `changes requested` et `N_CORRECTIONS < N_REVIEW`.*

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
N_CORRECTIONS=$(gh issue view {ISSUE_NUMBER} --json comments \
  --jq '[.comments[].body | select(contains("STATE:CORRECTIONS_REPORTED"))] | length')

gh issue comment {ISSUE_NUMBER} --body "## 🔄 Corrections demandées — cycle $((N_CORRECTIONS + 1))

[Synthèse structurée de chaque correction demandée dans la review]
[Extraits de code concernés si mentionnés]

<!-- STATE:CORRECTIONS_REPORTED -->
<!-- CORRECTIONS_CYCLE:$((N_CORRECTIONS + 1)) -->"
```

### 5.3 Mise à jour des labels — redéclenche Phase 3

```bash
gh issue edit {ISSUE_NUMBER} --remove-label 'changes requested'
gh issue edit {ISSUE_NUMBER} --add-label 'analyze'
# → Le trigger relancera le skill qui détectera N_DEV = N_CORRECTIONS
#   et démarrera un nouveau cycle de développement (Phase 3)
```

### 5.4 Nettoyage du worktree

```bash
cd /workspace/test-squad-automation
git worktree remove "$WORKTREE_PATH" --force 2>/dev/null || true
```

---

## Résumé de la machine d'états pour N cycles

```
Phase 1 : Analyse          → STATE:ANALYSIS_DONE
Phase 2 : Plan             → STATE:PLAN_DONE
Phase 3 : Dev (cycle 1)    → STATE:DEV_DONE (DEV_CYCLE:1) + label "to review"
Phase 4 : Review (cycle 1) → STATE:REVIEW_DONE (REVIEW_CYCLE:1)
  ├── Approuvé             → STATE:REVIEW_APPROVED + label "approved" → STOP ✅
  └── Corrections          → label "changes requested"
Phase 5 : Corrections      → STATE:CORRECTIONS_REPORTED (CORRECTIONS_CYCLE:1)
Phase 3 : Dev (cycle 2)    → STATE:DEV_DONE (DEV_CYCLE:2) + label "to review"
Phase 4 : Review (cycle 2) → STATE:REVIEW_DONE (REVIEW_CYCLE:2)
  ├── Approuvé             → STATE:REVIEW_APPROVED → STOP ✅
  └── Corrections          → ...
```

**Invariant à chaque démarrage :**
- `N_DEV = N_CORRECTIONS` → Phase 3 (dev)
- `N_DEV > N_REVIEW` → Phase 4 (review)
- `N_REVIEW > N_CORRECTIONS` → Phase 5 (rapport corrections)
- `STATE:REVIEW_APPROVED` → STOP
