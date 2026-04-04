---
name: ticket-workflow
description: Workflow complet de traitement d'un ticket GitHub pour test-squad-automation, de l'analyse au développement. Gère la reprise automatique depuis l'état persisté dans les commentaires GitHub. Déclencher sur tout ticket labelisé "analyze". Inclut : analyse du besoin, plan technique, implémentation, tests et PR.
allowed-tools: Bash(gh:*), Bash(git:*), Bash(docker:*), Read, Write, Glob, LS, Edit
---

# Skill : ticket-workflow

Ce skill traite un ticket GitHub de bout en bout, de l'analyse initiale jusqu'à la
pull request. Il est **repris depuis où il s'est arrêté** à chaque exécution en
lisant les marqueurs dans les commentaires du ticket.

---

## PHASE 0 — Initialisation et détection de l'état

### 0.1 Création du worktree

```bash
WORKTREE_PATH="/workspace/test-squad-automation-issue-{ISSUE_NUMBER}"
git -C /workspace/test-squad-automation fetch origin
git -C /workspace/test-squad-automation worktree add "$WORKTREE_PATH" origin/main 2>/dev/null \
  || echo "Worktree déjà existant, réutilisation"
cd "$WORKTREE_PATH"
```

### 0.2 Lecture de l'état courant

Lis **tous** les commentaires du ticket dans l'ordre chronologique :

```bash
gh issue view {ISSUE_NUMBER} --json title,body,comments \
  --jq '{title: .title, body: .body, comments: [.comments[] | {author: .author.login, body: .body}]}'
```

### 0.3 Détermination de la phase à exécuter

Analyse les commentaires pour identifier les marqueurs présents et déterminer
quelle phase exécuter. Les marqueurs et leur signification :

| Marqueur dans les commentaires | Phase à exécuter |
|---|---|
| Aucun marqueur | → Phase 1 : Analyse |
| `<!-- STATE:ANALYSIS_DONE -->` présent, pas de `<!-- STATE:PLAN_DONE -->` | → Phase 2 : Plan |
| `<!-- STATE:WAITING_FOR_ANSWERS -->` présent, et une réponse postée après | → Phase 2 : Plan (reprend avec les réponses) |
| `<!-- STATE:WAITING_FOR_ANSWERS -->` présent, pas de réponse après | → **STOP** : en attente de réponse humaine |
| `<!-- STATE:PLAN_DONE -->` présent, pas de `<!-- STATE:DEV_DONE -->` | → Phase 3 : Développement |
| `<!-- STATE:DEV_DONE -->` présent | → **STOP** : travail terminé, PR créée |

> Les marqueurs sont des commentaires HTML invisibles inclus dans les commentaires
> GitHub. Ils permettent la reprise sans polluer l'affichage.

**⚠️ Gestion d'erreur :** si l'état est ambigu (marqueurs incohérents), lis les
commentaires dans l'ordre et déduis l'état logique le plus récent.

---

## PHASE 1 — Analyse du ticket

*Exécuter si : aucun marqueur d'état ou label `analyze` posé sans commentaire d'analyse.*

### 1.1 Lecture approfondie du ticket

```bash
gh issue view {ISSUE_NUMBER} --json title,body,comments \
  --jq '{title: .title, body: .body, comments: [.comments[] | {author: .author.login, body: .body}]}'
```

### 1.2 Analyse du contexte codebase

- Lis le `CLAUDE.md` pour comprendre les conventions du projet
- Identifie les apps Django concernées (`apps/`)
- Examine les modèles, vues, URLs et templates existants liés au besoin
- Repère les patterns déjà utilisés (CBV, factories de test, etc.)
- Vérifie les dépendances installées (`requirements/`)

### 1.3 Détection des ambiguïtés

Identifie les points bloquants **avant** de rédiger les consignes :
- L'objectif est-il clair et mesurable ?
- Le périmètre est-il délimité (IN vs OUT) ?
- Les critères d'acceptance sont-ils vérifiables ?
- Le comportement en cas d'erreur est-il spécifié ?

Si tu peux faire un choix raisonnable cohérent avec le projet → fais-le et documente-le.
Ne bloque que si la question est **vraiment bloquante**.

### 1.4 Post du commentaire d'analyse

```bash
gh issue comment {ISSUE_NUMBER} --body "## 🔍 Analyse

[Ce que tu as compris du besoin et de l'état actuel du code]

## 📋 Consignes de développement

### Fichiers à créer ou modifier
[Liste avec chemins exacts]

### Logique métier
[Description avec extraits de code si utile]

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

> Le marqueur `<!-- STATE:ANALYSIS_DONE -->` est invisible sur GitHub mais
> détectable par le skill pour la reprise.

### 1.5 Mise à jour des labels

```bash
gh issue edit {ISSUE_NUMBER} --remove-label 'analyze'
```

Puis selon les questions :
```bash
# S'il y a des questions bloquantes :
gh issue edit {ISSUE_NUMBER} --add-label 'help wanted'
# Ajoute aussi un marqueur d'attente dans un commentaire dédié :
gh issue comment {ISSUE_NUMBER} --body "<!-- STATE:WAITING_FOR_ANSWERS -->
⏳ En attente de réponses aux questions ci-dessus avant de continuer."

# S'il n'y a pas de questions :
gh issue edit {ISSUE_NUMBER} --add-label 'analyze'
# → Ce label va redéclencher le workflow qui reprendra en Phase 2
```

**✅ Critère de sortie de la phase 1 :** commentaire d'analyse posté avec
`<!-- STATE:ANALYSIS_DONE -->`.

---

## PHASE 2 — Plan technique

*Exécuter si : `<!-- STATE:ANALYSIS_DONE -->` présent et pas de `<!-- STATE:PLAN_DONE -->`.*
*Si reprise après réponses : inclure les réponses dans le contexte.*

### 2.1 Récupération des consignes et des réponses éventuelles

Récupère le commentaire contenant `<!-- STATE:ANALYSIS_DONE -->` :

```bash
gh issue view {ISSUE_NUMBER} --json comments \
  --jq '.comments[] | select(.body | contains("STATE:ANALYSIS_DONE"))'
```

Si en mode reprise après réponses, récupère aussi les commentaires postés
**après** le marqueur `<!-- STATE:WAITING_FOR_ANSWERS -->`.

### 2.2 Analyse de l'impact sur le code

- Identifie les fichiers existants qui seront modifiés
- Repère les dépendances entre fichiers à créer/modifier
- Évalue la complexité (triviale / moyenne / complexe)
- Détecte les risques de régression
- Identifie les patterns similaires déjà implémentés à réutiliser

### 2.3 Décomposition en tâches atomiques

Découpe en tâches de **moins de 15 minutes** chacune :
- Une tâche = un fichier créé ou modifié
- Les tests sont une tâche séparée de l'implémentation
- Les migrations sont toujours une tâche indépendante
- L'ordre respecte les dépendances (modèle → vue → template → tests)

**Principe YAGNI :** ne pas abstraire ce qui n'est pas demandé, signaler
tout choix qui va au-delà des consignes.

### 2.4 Post du commentaire de plan

```bash
gh issue comment {ISSUE_NUMBER} --body "## 🗺️ Plan d'implémentation

**Approche :** [résumé en une phrase]

**Fichiers impactés :**
[liste]

## 📝 Tâches

**T1 — [titre]**
- Fichier : \`chemin/exact\`
- Action : créer | modifier
- Description : [ce qui doit être fait]
- Critère de validation : [comment vérifier]
- Dépend de : [T0 ou 'aucune']

[...]

## ⚠️ Points d'attention
[Risques, régressions possibles, ordre critique]

## 🔬 Stratégie de tests
[Quels tests écrire en premier, fixtures nécessaires, cas limites]

<!-- STATE:PLAN_DONE -->
<!-- PLAN_TASK_COUNT:[N] -->
<!-- PLAN_CURRENT_TASK:0 -->"
```

> `<!-- PLAN_TASK_COUNT:N -->` et `<!-- PLAN_CURRENT_TASK:0 -->` permettent
> de reprendre le développement à la bonne tâche en cas d'interruption.

### 2.5 Mise à jour des labels

```bash
gh issue edit {ISSUE_NUMBER} --remove-label 'analyze'
gh issue edit {ISSUE_NUMBER} --add-label 'analyze'
# → Redéclenche le workflow qui reprendra en Phase 3
```

**✅ Critère de sortie de la phase 2 :** commentaire de plan posté avec
`<!-- STATE:PLAN_DONE -->`.

---

## PHASE 3 — Développement

*Exécuter si : `<!-- STATE:PLAN_DONE -->` présent et pas de `<!-- STATE:DEV_DONE -->`.*

### 3.1 Récupération du plan et de la progression

```bash
# Récupère le commentaire de plan
gh issue view {ISSUE_NUMBER} --json comments \
  --jq '.comments[] | select(.body | contains("STATE:PLAN_DONE"))'
```

Extrais `PLAN_TASK_COUNT` et `PLAN_CURRENT_TASK` pour savoir depuis quelle
tâche reprendre (en cas d'interruption lors d'une exécution précédente).

### 3.2 Mise à jour des labels

```bash
gh issue edit {ISSUE_NUMBER} --remove-label 'analyze'
gh api repos/nicolasdeclerck/test-squad-automation/issues/{ISSUE_NUMBER}/labels/go%20for%20dev \
  -X DELETE 2>/dev/null || true
gh api repos/nicolasdeclerck/test-squad-automation/issues/{ISSUE_NUMBER}/labels \
  -X POST -f "labels[]=in progress"
```

### 3.3 Exécution des tâches

Pour chaque tâche du plan (en commençant depuis `PLAN_CURRENT_TASK`) :

1. Implémente la tâche en suivant exactement la description du plan
2. Respecte les conventions du `CLAUDE.md`
3. Met à jour le compteur dans un commentaire après chaque tâche complétée :

```bash
gh issue comment {ISSUE_NUMBER} --body "<!-- STATE:TASK_PROGRESS -->
<!-- PLAN_CURRENT_TASK:[N+1] -->
✅ Tâche T[N] complétée : [titre de la tâche]"
```

### 3.4 Tests

```bash
docker compose up -d
docker compose exec -T django pip install -r requirements/development.txt -q
docker compose exec -T django pytest --cov=apps
docker compose stop
```

**Si des tests échouent :**
- Analyse les logs, corrige le code (jamais les tests sauf si manifestement incorrects)
- Relance les tests
- Maximum **3 tentatives**
- Si échec après 3 tentatives :

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

# Vérifie si la branche existe déjà
if git -C /workspace/test-squad-automation ls-remote --exit-code --heads origin "$BRANCH_NAME" > /dev/null 2>&1; then
  git -C /workspace/test-squad-automation worktree add "$WORKTREE_PATH" "$BRANCH_NAME" 2>/dev/null \
    || echo "Worktree déjà sur la bonne branche"
else
  git -C /workspace/test-squad-automation worktree add "$WORKTREE_PATH" -b "$BRANCH_NAME" origin/main
fi

git add -A
git diff --cached --quiet || git commit -m "feat: close #{ISSUE_NUMBER} - {titre du ticket}"
git push origin "$BRANCH_NAME"
```

### 3.6 Commentaire de documentation

```bash
gh issue comment {ISSUE_NUMBER} --body "## 📝 Documentation de l'implémentation

### Ce qui a été implémenté
[résumé des fichiers créés/modifiés]

### Choix techniques
[décisions importantes et pourquoi]

### Comment utiliser
[guide pratique]

### Points d'attention
[limitations, prérequis]"
```

### 3.7 Pull Request

```bash
EXISTING_PR=$(gh pr list --head "$BRANCH_NAME" --json number --jq '.[0].number' 2>/dev/null)

if [ -n "$EXISTING_PR" ]; then
  gh pr edit "$EXISTING_PR" --body "[body mis à jour]"
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
# Marque le dev comme terminé
gh issue comment {ISSUE_NUMBER} --body "<!-- STATE:DEV_DONE -->
🎉 Développement terminé. PR créée."

# Mise à jour des labels
gh api repos/nicolasdeclerck/test-squad-automation/issues/{ISSUE_NUMBER}/labels/in%20progress \
  -X DELETE 2>/dev/null || true
gh issue edit {ISSUE_NUMBER} --add-label 'to review'

# Nettoyage du worktree
cd /workspace/test-squad-automation
git worktree remove "$WORKTREE_PATH" --force
```

**✅ Critère de sortie de la phase 3 :** PR créée, label `to review` posé,
`<!-- STATE:DEV_DONE -->` présent.
