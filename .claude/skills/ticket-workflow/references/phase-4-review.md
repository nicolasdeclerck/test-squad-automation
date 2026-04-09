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

Le ticket est approuvé côté code mais les tests browser sont à exécuter
**séparément** via le workflow `browser-tests.yml` (sur un environnement
Docker éphémère dédié, à la demande). Le ticket reçoit donc 2 labels en
parallèle : `approved` (code OK) et `pending-browser-tests` (tests à lancer).

```bash
APPROVED="True"
write_state "done"

# Récupère les infos pour le commentaire
BRANCH_NAME=$(cat "$STATE_FILE" | python3 -c "import sys,json; print(json.load(sys.stdin).get('branch',''))")
TESTS_TABLE=$(cat "$STATE_FILE" | python3 -c "
import sys,json
d = json.load(sys.stdin)
for t in d.get('browser_tests', []):
    print(f\"| {t['id']} | {t['title']} | [{t['type']}] |\")
")
TESTS_COUNT=$(cat "$STATE_FILE" | python3 -c "import sys,json; print(len(json.load(sys.stdin).get('browser_tests',[])))")

gh issue comment {ISSUE_NUMBER} --body "## ✅ Code approuvé — Tests browser en attente

La code review automatique a approuvé le code. Les modifications sont prêtes à merger côté code.

**$TESTS_COUNT scénarios de test browser** ont été planifiés et restent à exécuter :

| ID | Scénario | Type |
|----|----------|------|
$TESTS_TABLE

### Comment lancer les tests browser

Les tests browser tournent à la demande sur un environnement Docker éphémère, via un workflow séparé :

\`\`\`bash
gh workflow run browser-tests.yml \\
  -F branch=$BRANCH_NAME \\
  -F test_filter=issue:{ISSUE_NUMBER}
\`\`\`

Ou via l'UI : **Actions → Browser Tests → Run workflow** → renseigner \`branch=$BRANCH_NAME\` et \`test_filter=issue:{ISSUE_NUMBER}\`.

Le label \`pending-browser-tests\` sera retiré automatiquement si tous les tests passent."

# Labels finaux : approved + pending-browser-tests en parallèle
gh issue edit {ISSUE_NUMBER} --remove-label 'in progress'
gh issue edit {ISSUE_NUMBER} --add-label 'approved'
gh issue edit {ISSUE_NUMBER} --add-label 'pending-browser-tests'
```

→ **STOP** ✅ Ticket approuvé côté code, tests browser à lancer manuellement.

**Si `BROWSER_TESTS = 0` (aucun test front, ex : refactoring backend pur) :**

```bash
APPROVED="True"
write_state "done"

gh issue comment {ISSUE_NUMBER} --body "## ✅ Tests browser — non requis

Aucun test browser n'a été défini pour ce ticket (pas de changement front-end identifié).
La code review a été approuvée, le ticket est considéré comme terminé.

**Tests browser : 0 prévu, 0 exécuté.**"

# Labels finaux : approved seul (pas de tests browser à attendre)
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
