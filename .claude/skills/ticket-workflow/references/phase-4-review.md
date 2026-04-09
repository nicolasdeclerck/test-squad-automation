# Phase 4 — Code review

## 4.1 Lancement de la review

```bash
/code-review --comment
```

## 4.2 Analyse du résultat

**Si aucun problème détecté (aucune issue de confiance ≥ 80) :**

```bash
N_REVIEW=$((N_REVIEW + 1))

gh pr review "$PR_NUMBER" --approve \
  --body "Code review automatique cycle $N_REVIEW : aucun problème détecté."
```

Vérifie ensuite si des tests browser sont prévus pour ce ticket :

```bash
BROWSER_TESTS=$(cat "$STATE_FILE" | python3 -c "
import sys, json
d = json.load(sys.stdin)
tests = d.get('browser_tests', [])
print(len(tests))
")
```

**Si `BROWSER_TESTS > 0` :**

```bash
write_state "6"
```

Vérifie ensuite si tu dois enchaîner Phase 6 immédiatement ou t'arrêter ici
pour laisser GitHub Actions reconstruire l'environnement TNR avec le code
de la branche PR (qui n'existait pas avant que tu la crées en Phase 3) :

```bash
if [ -n "$STOP_BEFORE_PHASE_6" ]; then
  echo "DECISION_PHASE_6=stop_here_for_env_rebuild"
else
  echo "DECISION_PHASE_6=continue_directly"
fi
```

**Examine la sortie du bash ci-dessus** :

- Si elle contient `DECISION_PHASE_6=stop_here_for_env_rebuild` :
  **arrête immédiatement ton exécution du skill**. Ne charge pas
  `references/phase-6-browser-tests.md`. Le state file `PHASE=6` sera
  repris par un second run de Claude après que GitHub Actions ait
  reconstruit l'environnement TNR à partir de la branche PR.
  → **STOP** ici.

- Si elle contient `DECISION_PHASE_6=continue_directly` :
  charge `references/phase-6-browser-tests.md` et exécute Phase 6
  directement (l'environnement TNR est déjà prêt côté appelant).

**Si `BROWSER_TESTS = 0` (aucun test front, ex : refactoring backend pur) :**

```bash
APPROVED="True"
write_state "done"

gh issue comment {ISSUE_NUMBER} --body "## ✅ Tests browser — non requis

Aucun test browser n'a été défini pour ce ticket (pas de changement front-end identifié).
La code review a été approuvée, le ticket est considéré comme terminé.

**Tests browser : 0 prévu, 0 exécuté.**"

# Labels finaux
gh issue edit {ISSUE_NUMBER} --remove-label 'in progress'
gh issue edit {ISSUE_NUMBER} --add-label 'approved'
```

→ **STOP** ✅ Ticket terminé (pas de tests browser nécessaires).

**Si des problèmes de code review sont détectés :**

```bash
N_REVIEW=$((N_REVIEW + 1))
```

**Si `N_REVIEW >= 3` (limite de cycles atteinte) :**

```bash
write_state "4"

gh pr review "$PR_NUMBER" --request-changes \
  --body "Code review automatique cycle $N_REVIEW : corrections nécessaires. Limite de 3 cycles atteinte — intervention humaine requise."

gh issue comment {ISSUE_NUMBER} --body "## ⚠️ Limite de cycles de code review atteinte

La code review automatique a détecté des problèmes pendant **$N_REVIEW cycles consécutifs**.
Les corrections automatiques n'ont pas suffi à résoudre tous les points.

Intervention humaine requise. Pour relancer après correction manuelle, reposer le label \`analyze\`."

gh issue edit {ISSUE_NUMBER} --add-label 'help wanted'
```

→ **STOP** (l'humain reposera `analyze` après avoir corrigé)

**Sinon (cycles restants) :**

```bash
write_state "5"

gh pr review "$PR_NUMBER" --request-changes \
  --body "Code review automatique cycle $N_REVIEW : corrections nécessaires."
```

→ Exécuter Phase 5 directement

## 4.3 Nettoyage

```bash
cd /workspace/test-squad-automation
git worktree remove "$REVIEW_WORKTREE" --force 2>/dev/null || true
```
