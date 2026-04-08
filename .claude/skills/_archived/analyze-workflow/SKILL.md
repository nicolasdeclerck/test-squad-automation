---
name: analyze-workflow
description: Processus complet d'analyse d'un ticket GitHub pour le repo test-squad-automation. Execute de bout en bout : lecture du ticket, analyse du contexte codebase, detection des ambiguites, redaction et post du commentaire d'analyse, mise a jour des labels. Triggers include "analyze-workflow", "analyse le ticket", "analyse l'issue", ou toute demande d'analyser un ticket GitHub.
allowed-tools: Bash(gh:*), Bash(git:*)
---

# Skill : analyze-workflow

Ce skill décrit le processus complet d'analyse d'un ticket GitHub pour le repo
`test-squad-automation`. Tu dois l'exécuter de bout en bout de manière autonome.

Ce skill s'inspire de deux skills communautaires éprouvés :
- `trailofbits/ask-questions-if-underspecified` — pour la gestion des ambiguïtés
- `trailofbits/audit-context-building` — pour l'analyse approfondie du code existant

---

## 0. Création du worktree isolé

Crée un répertoire de travail isolé pour ce ticket afin de permettre l'exécution parallèle.

```bash
WORKTREE_PATH="/workspace/test-squad-automation-issue-{ISSUE_NUMBER}"
git -C /workspace/test-squad-automation worktree add "$WORKTREE_PATH" origin/main 2>/dev/null \
  || echo "Worktree déjà existant, réutilisation de $WORKTREE_PATH"
cd "$WORKTREE_PATH"
```

**✅ Critère de sortie :** `git worktree list` affiche le nouveau répertoire.

> **Toutes les commandes suivantes du skill doivent être exécutées depuis `$WORKTREE_PATH`.**

---

## 1. Lecture du ticket et de son historique

Lis le ticket et **tous** ses commentaires dans l'ordre chronologique :

```bash
gh issue view {ISSUE_NUMBER} --json title,body,comments \
  --jq '{title: .title, body: .body, comments: [.comments[] | {author: .author.login, body: .body}]}'
```

**✅ Critère de sortie :** tu as une vision complète du besoin et des échanges passés.

**⚠️ Gestion d'erreur :** si c'est un second passage en analyse (commentaire existant
contenant `## Analyse`), ne réécris pas l'analyse complète — passe directement à
l'étape 6 (mode suivi).

---

## 2. Analyse du contexte codebase

Effectue une analyse approfondie du code existant **avant** de formuler quoi que ce soit :

- Lis le `CLAUDE.md` pour comprendre les conventions du projet
- Identifie les apps Django concernées par le ticket (`apps/`)
- Examine les modèles, vues, URLs et templates existants liés au besoin
- Repère les patterns déjà utilisés dans le projet (CBV, factories de test, etc.)
- Vérifie les dépendances déjà installées (`requirements/`)

**✅ Critère de sortie :** tu comprends le code existant suffisamment pour évaluer
l'impact et la complexité de l'implémentation demandée.

---

## 3. Détection des ambiguïtés (inspiré de `ask-questions-if-underspecified`)

Avant de rédiger les consignes, identifie les points qui ont **plusieurs interprétations
plausibles** ou des **détails manquants bloquants** :

Pose-toi ces questions :
- L'objectif final est-il clair et mesurable ?
- Le périmètre est-il délimité (ce qui est IN vs OUT) ?
- Y a-t-il des contraintes techniques non mentionnées ?
- Les critères d'acceptance sont-ils vérifiables ?
- Le comportement attendu en cas d'erreur est-il spécifié ?

Ne pose une question que si elle est **vraiment bloquante** pour démarrer.
Si tu peux faire un choix raisonnable cohérent avec le reste du projet, fais-le
et documente-le dans les consignes plutôt que de bloquer.

---

## 4. Rédaction et post du commentaire d'analyse

Rédige et poste un commentaire structuré sur le ticket :

```bash
gh issue comment {ISSUE_NUMBER} --body "..."
```

Le commentaire doit contenir exactement ces sections :

### ## 🔍 Analyse
Ce que tu as compris du besoin, du contexte métier et de l'état actuel du code.
Inclus les éléments clés découverts lors de l'étape 2 (fichiers existants, patterns,
ce qui est déjà fait vs ce qui manque).

### ## 📋 Consignes de développement
Description détaillée et actionnable de ce qui doit être implémenté :
- **Fichiers à créer ou modifier** (chemins exacts)
- **Logique métier à implémenter** (avec extraits de code si utile)
- **Critères d'acceptance** (liste de conditions vérifiables)
- **Tests à écrire** (noms de tests et ce qu'ils vérifient)

### ## 📦 Changements de stack
Dépendances à ajouter/modifier dans `requirements/`, ou `Aucun changement`.

### ## ❓ Questions bloquantes
Liste numérotée des questions **strictement nécessaires** avant de démarrer,
ou `Aucune question — le besoin est clair et le développement peut démarrer.`

**✅ Critère de sortie :** le commentaire est posté et lisible sur GitHub.

---

## 5. Mise à jour des labels

```bash
gh issue edit {ISSUE_NUMBER} --remove-label 'analyze'
```

Puis selon le résultat de l'étape 3 :

```bash
# S'il y a des questions bloquantes :
gh issue edit {ISSUE_NUMBER} --add-label 'help wanted'

# S'il n'y a pas de questions :
gh issue edit {ISSUE_NUMBER} --add-label 'go for dev'
```

**✅ Critère de sortie :** le label `analyze` est retiré, et exactement un des deux
labels (`help wanted` ou `go for dev`) a été ajouté.

**⚠️ Gestion d'erreur :** si un label n'existe pas sur le repo, crée-le d'abord :
```bash
gh label create 'help wanted' --color '#e4e669'
gh label create 'go for dev' --color '#0075ca'
```

---

## 6. Nettoyage du worktree

Une fois l'analyse terminée, supprime le worktree isolé.

```bash
cd /workspace/test-squad-automation
git worktree remove "$WORKTREE_PATH" --force
```

**✅ Critère de sortie :** `git worktree list` ne contient plus `$WORKTREE_PATH`.

---

## 7. Mode suivi (second passage en analyse)

Si un commentaire `## 🔍 Analyse` existe déjà sur le ticket, tu es en mode suivi.
Dans ce cas, **ne reposte pas une analyse complète**. À la place :

1. Identifie les questions bloquantes que tu avais posées
2. Identifie les réponses apportées dans les commentaires suivants
3. Poste un commentaire **synthétique** commençant par `## ✅ Mise à jour suite à vos réponses` qui :
   - Confirme les points clarifiés
   - Met à jour uniquement les sections des consignes impactées par les réponses
4. Applique ensuite l'étape 5 normalement
