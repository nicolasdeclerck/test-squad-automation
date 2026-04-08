# Phase 5 — Rapport des corrections (code review et tests browser)

Cette phase est utilisée dans deux contextes :
- **Après une code review** (Phase 4 → Phase 5) : corrections issues de `/code-review`
- **Après des tests browser** (Phase 6 → Phase 7→5) : corrections issues de `agent-browser`

Le contexte est déterminé par la phase d'origine stockée dans `.claude-state.json`.

## 5.1 Récupération des feedbacks

### Contexte code review (venant de Phase 4)

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

### Contexte tests browser (venant de Phase 6)

Relit le commentaire de résultats de la Phase 6 depuis les commentaires GitHub
pour extraire les anomalies détaillées.

## 5.2 Post du commentaire de corrections sur le ticket

```bash
N_CORRECTIONS=$((N_CORRECTIONS + 1))
```

### Format pour corrections code review

```bash
gh issue comment {ISSUE_NUMBER} --body "## 🔄 Corrections demandées — cycle $N_CORRECTIONS

[Synthèse structurée de chaque correction demandée dans la review]
[Extraits de code concernés si mentionnés]"
```

### Format pour corrections tests browser

```bash
gh issue comment {ISSUE_NUMBER} --body "## 🔄 Corrections demandées (tests browser) — cycle $N_CORRECTIONS

Les tests browser ont révélé les anomalies suivantes à corriger :

### [TEST_ID] — [titre du test]
- **Problème :** [description du comportement incorrect]
- **Fichiers probablement impactés :** [chemins estimés]
- **Correction attendue :** [description de ce qu'il faut corriger]

[... pour chaque FAIL ...]

> Ces corrections suivent le même processus que les corrections de code review.
> Le prochain cycle de développement (Phase 3) doit traiter ces points."
```

## 5.3 Transition vers Phase 3

```bash
write_state "3"
# → Exécuter Phase 3 directement (nouveau cycle de développement)
```

> **Note :** Lors du retour en Phase 3, les corrections sont traitées
> exactement comme des tâches : le commentaire `## 🔄 Corrections demandées`
> (ou `## 🔄 Corrections demandées (tests browser)`) est lu en Phase 3.1
> et prime sur le plan initial pour les fichiers concernés.
> Après développement, le flux repasse par Phase 4 (code review)
> puis éventuellement Phase 6 (tests browser) pour valider les corrections.
