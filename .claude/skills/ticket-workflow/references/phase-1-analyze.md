# Phase 1 — Analyse du ticket

## 1.1 Analyse du contexte codebase

- Lis le `CLAUDE.md` pour comprendre les conventions du projet
- Identifie les apps Django concernées (`apps/`)
- Examine les modèles, vues, URLs et templates liés au besoin
- Repère les patterns existants (CBV, factories de test, etc.)
- Vérifie les dépendances installées (`requirements/`)

## 1.2 Détection des ambiguïtés

Identifie uniquement les points **vraiment bloquants** :
- L'objectif est-il clair et mesurable ?
- Le périmètre est-il délimité (IN vs OUT) ?
- Les critères d'acceptance sont-ils vérifiables ?

Si tu peux faire un choix raisonnable → fais-le et documente-le.

## 1.3 Post du commentaire d'analyse

Poste un commentaire **court** de notification. Le détail complet sera
documenté en Phase 3 une fois l'implémentation terminée et stabilisée.

Le commentaire **doit** commencer par `## 🔍 Analyse terminée` pour être
retrouvé par la Phase 2.

```bash
gh issue comment {ISSUE_NUMBER} --body "## 🔍 Analyse terminée

**Périmètre identifié :** [résumé en 1-2 phrases du besoin et de l'approche envisagée]

**Fichiers concernés :** [nombre] fichiers à créer/modifier

**Questions bloquantes :** [Aucune | liste courte]"
```

## 1.4 Gestion des questions bloquantes et transition

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
