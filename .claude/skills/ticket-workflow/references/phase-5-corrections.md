# Phase 5 — Rapport des corrections de code review

Cette phase est exécutée après une code review qui a détecté des problèmes
(Phase 4 → Phase 5). Elle synthétise les corrections demandées sur la PR
en un commentaire structuré sur l'issue, puis relance un cycle de développement.

> **Note :** Les corrections issues de tests browser ne passent **plus**
> par cette phase. Les tests browser sont désormais exécutés à la demande
> via le workflow GitHub Actions `browser-tests.yml` (skill séparé
> `browser-tests-on-demand`), en dehors du `ticket-workflow`.

## 5.1 Récupération des feedbacks de la PR

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

## 5.2 Post du commentaire de corrections sur le ticket

```bash
N_CORRECTIONS=$((N_CORRECTIONS + 1))

gh issue comment {ISSUE_NUMBER} --body "## 🔄 Corrections demandées — cycle $N_CORRECTIONS

[Synthèse structurée de chaque correction demandée dans la review]
[Extraits de code concernés si mentionnés]"
```

## 5.3 Transition vers Phase 3

**Important :** Remet `CURRENT_TASK` à 0 avant la transition, car les
corrections constituent de nouvelles tâches à exécuter depuis le début :

```bash
CURRENT_TASK=0
write_state "3"
# → Exécuter Phase 3 directement (nouveau cycle de développement)
```

> **Note :** Lors du retour en Phase 3, les corrections sont traitées
> exactement comme des tâches : le commentaire `## 🔄 Corrections demandées`
> est lu en Phase 3.1 et prime sur le plan initial pour les fichiers concernés.
> Après développement, le flux repasse par Phase 4 (code review) qui
> validera (ou demandera de nouvelles corrections, jusqu'à 3 cycles maximum).
