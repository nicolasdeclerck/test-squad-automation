# Phase 2 — Plan technique

## 2.1 Récupération des consignes

Récupère le commentaire d'analyse posté en Phase 1 depuis les commentaires GitHub :

```bash
gh issue view {ISSUE_NUMBER} --json comments \
  --jq '[.comments[] | select(.body | startswith("## 🔍 Analyse terminée"))] | last | .body'
```

Si en reprise après réponses à des questions bloquantes, récupère aussi les
commentaires postés après le commentaire d'attente :

```bash
gh issue view {ISSUE_NUMBER} --json comments \
  --jq '[.comments[] | {author: .author.login, body: .body}]'
```

## 2.2 Analyse de l'impact

- Fichiers existants à modifier et leurs dépendances
- Complexité de chaque modification
- Risques de régression
- Patterns similaires déjà implémentés à réutiliser

## 2.3 Décomposition en tâches atomiques

Tâches de **moins de 15 minutes**, une par fichier :
- Migrations : toujours une tâche indépendante
- Tests : tâche séparée de l'implémentation
- Ordre : modèle → vue → template → tests
- Principe YAGNI : signaler tout choix dépassant les consignes

## 2.4 Post du commentaire de plan

Poste un commentaire **court** de notification. Le détail complet de l'implémentation
sera documenté en Phase 3 une fois le code stabilisé.

```bash
gh issue comment {ISSUE_NUMBER} --body "## 🗺️ Plan défini — développement en cours

**Approche :** [résumé en une phrase]

**Tâches :** [N] tâches sur [M] fichiers

**Tests browser prévus :** [N scénarios | aucun (pas d'impact front-end)]"
```

> **Note :** L'analyse complète (fichiers, tâches, critères, choix techniques)
> est réalisée en interne. Elle sera documentée dans le commentaire de Phase 3
> après implémentation et code review.

## 2.5 Planification des tests browser (TDD)

Lis le fichier `references/browser-test-planning.md` et exécute les deux étapes :
1. Mise à jour du cahier `docs/browser-test-checklist.md`
2. Définition de la liste `browser_tests` dans `.claude-state.json`

**Si aucun changement front-end n'est identifié**, sauter cette étape
et laisser `browser_tests` vide (`[]`).

## 2.6 Persistance des tâches dans le fichier d'état

Enregistre la liste ordonnée des tâches dans `.claude-state.json` sous la clé `tasks`,
afin que la Phase 3 puisse les retrouver même en cas de reprise de session :

```json
{
  "tasks": [
    {"index": 0, "description": "Créer le modèle X dans apps/blog/models.py", "status": "pending"},
    {"index": 1, "description": "Ajouter la migration", "status": "pending"},
    {"index": 2, "description": "Créer la vue API dans apps/blog/api_views.py", "status": "pending"},
    {"index": 3, "description": "Écrire les tests dans apps/blog/tests/", "status": "pending"}
  ]
}
```

**Important :** cette clé est préservée par `write_state()` au même titre que `browser_tests`.

## 2.7 Transition vers Phase 3

```bash
write_state "3"
# → Exécuter Phase 3 directement
```
