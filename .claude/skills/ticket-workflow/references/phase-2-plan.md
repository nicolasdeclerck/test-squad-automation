# Phase 2 — Plan technique

## 2.1 Récupération des consignes

Relit le commentaire d'analyse posté en Phase 1 depuis les commentaires GitHub.

Si en reprise après réponses, récupère aussi les commentaires postés après
le commentaire d'attente.

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

## 2.5 Mise à jour du cahier de tests browser (TDD)

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

## 2.6 Définition de la liste de tests browser du ticket

Après la mise à jour du cahier de tests, définis la liste des scénarios de test
browser **spécifiques à ce ticket** qui seront exécutés en Phase 6 après la code review.

**Démarche :**

1. Identifie tous les scénarios de `docs/browser-test-checklist.md` impactés par ce ticket :
   - Les scénarios **ajoutés** dans l'étape 2.5
   - Les scénarios **modifiés** dans l'étape 2.5
   - Les scénarios existants qui testent des fonctionnalités **touchées** par les changements
     (tests de non-régression directe)
2. Collecte pour chaque scénario : son identifiant (ex : `NAV-01`), son titre, son type
   (`[PUBLIC]`, `[AUTH]`, `[OWNER]`), et les étapes détaillées telles que décrites dans le cahier
3. Enregistre cette liste dans le fichier d'état `.claude-state.json` sous la clé `browser_tests` :

```json
{
  "browser_tests": [
    {
      "id": "NAV-01",
      "title": "Affichage du header",
      "type": "PUBLIC",
      "steps": "1. Ouvrir la page d'accueil\n2. Vérifier la présence du header..."
    },
    {
      "id": "E2E-02",
      "title": "Brouillon → édition avec autosave → publication",
      "type": "AUTH",
      "steps": "1. Se connecter...\n2. Créer un brouillon..."
    }
  ]
}
```

4. Le nombre de scénarios est mentionné dans le commentaire court de Phase 2.4.
   Le détail complet (tableau des scénarios avec IDs) sera posté au démarrage
   de la Phase 6 (section 6.2.1).

**Si aucun changement front-end n'est identifié**, la liste `browser_tests` est vide (`[]`)
et la Phase 6 sera automatiquement sautée.

## 2.7 Transition vers Phase 3

```bash
write_state "3"
# → Exécuter Phase 3 directement
```
