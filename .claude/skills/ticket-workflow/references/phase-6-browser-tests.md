# Phase 6 — Tests browser

Cette phase exécute les scénarios de test browser définis en Phase 2.6 via `agent-browser`.
Elle intervient **après** une code review réussie (Phase 4) et **avant** l'approbation finale.

## 6.1 Récupération de la liste de tests

```bash
BROWSER_TESTS=$(cat "$STATE_FILE" | python3 -c "
import sys, json
d = json.load(sys.stdin)
tests = d.get('browser_tests', [])
for t in tests:
    print(f\"{t['id']} | {t['type']} | {t['title']}\")
")
```

## 6.2 Préparation de l'environnement éphémère

Lance un environnement Docker éphémère identique à la production
(`docker-compose.test.yml`) via le script `tnr-docker.sh`, comme pour les
tests de non-régression. Cet environnement inclut le code de la branche PR.

```bash
# Démarrer l'environnement éphémère (build, migrate, seed test data)
./scripts/tnr-docker.sh up

# Définir les URLs de test (surchargeables via variables d'env si déjà
# définies, ex : BASE_URL=http://blog-tnr-nginx-1:80 quand on tourne dans
# claude-worker connecté au réseau Docker éphémère)
BASE_URL="${BASE_URL:-http://localhost:8080}"
API_URL="${API_URL:-http://localhost:8080}"

# Forcer Chrome à démarrer sans sandbox (nécessaire dans le container
# claude-worker, sans effet en local). AGENT_BROWSER_ARGS est documenté
# dans `agent-browser --help` comme alternative à --args.
export AGENT_BROWSER_ARGS=--no-sandbox

# Vérifier l'accessibilité de l'application
agent-browser open "$BASE_URL"
agent-browser wait --load networkidle
agent-browser snapshot -i
```

> **Note :** Ne pas utiliser `docker compose up -d` (environnement de dev).
> L'environnement éphémère (`tnr-docker.sh`) reproduit fidèlement la production :
> gunicorn, nginx, frontend buildé, PostgreSQL, Redis, Celery.

### 6.2.1 Commentaire de démarrage des tests

Poste un commentaire sur le ticket **avant** de commencer l'exécution des tests,
pour tracer le démarrage même en cas d'interruption du workflow :

```bash
TOTAL_TESTS=$(cat "$STATE_FILE" | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(len(d.get('browser_tests', [])))
")

gh issue comment {ISSUE_NUMBER} --body "## 🔄 Tests browser — démarrage (cycle $((N_BROWSER_TEST + 1)))

Lancement de **$TOTAL_TESTS scénarios** de test browser via agent-browser.

| ID | Scénario | Type |
|----|----------|------|
$(cat "$STATE_FILE" | python3 -c "
import sys, json
d = json.load(sys.stdin)
for t in d.get('browser_tests', []):
    print(f\"| {t['id']} | {t['title']} | [{t['type']}] |\")
")

Les résultats seront postés à la fin de l'exécution."
```

## 6.3 Gestion des sessions d'authentification

Utilise des sessions nommées selon le type de test, conformément au skill `agent-browser` :

- `--session public` pour les tests `[PUBLIC]`
- `--session user1` pour les tests `[AUTH]` (connexion avec `testuser@example.com` / `Testpass123!`)
- `--session user2` pour les tests `[OWNER]` nécessitant un deuxième utilisateur

Si une session authentifiée n'existe pas encore, connecte-toi d'abord. **Important :**
les refs `@e1`, `@e2`… retournés par `snapshot -i` sont dynamiques — il faut snapshotter
puis utiliser les refs réels (pas de placeholders type `@emailInput`).

```bash
agent-browser --session user1 open "$BASE_URL/comptes/connexion"
agent-browser --session user1 wait --load networkidle
agent-browser --session user1 snapshot -i
# Lis les refs retournés (ex: @e1 = email, @e2 = password, @e3 = bouton submit)
# puis interagis avec ces refs réels :
agent-browser --session user1 fill @e1 "testuser@example.com"
agent-browser --session user1 fill @e2 "Testpass123!"
agent-browser --session user1 click @e3
agent-browser --session user1 wait --load networkidle
```

## 6.4 Exécution des tests

Pour chaque scénario de la liste `browser_tests` :

1. **Exécute les étapes** décrites dans le champ `steps` du scénario en utilisant
   les commandes `agent-browser` (open, snapshot, click, fill, wait, get text, etc.)
2. **Vérifie chaque assertion** (présence d'éléments, texte attendu, navigation correcte)
3. **En cas d'échec** : capture un screenshot et enregistre le détail de l'anomalie

```bash
# Exemple d'exécution d'un scénario
agent-browser open "$BASE_URL/page-cible" --session user1
agent-browser wait --load networkidle
agent-browser snapshot -i
# Vérifications...
agent-browser screenshot --full  # En cas d'échec, pour preuve
```

4. **Enregistre le résultat** (PASS / FAIL / SKIP) pour chaque scénario

## 6.5 Compilation des résultats

Après exécution de tous les scénarios, compile les résultats :

```bash
N_BROWSER_TEST=$((N_BROWSER_TEST + 1))
```

**Si tous les tests passent (aucun FAIL) :**

```bash
APPROVED="True"
write_state "done"

gh issue comment {ISSUE_NUMBER} --body "## ✅ Tests browser — cycle $N_BROWSER_TEST

Tous les scénarios de test browser ont été exécutés avec succès.

| ID | Scénario | Résultat |
|----|----------|----------|
[tableau des résultats PASS]

**$TOTAL_PASS / $TOTAL_TESTS tests réussis.**"

# Labels finaux
gh issue edit {ISSUE_NUMBER} --remove-label 'in progress'
gh issue edit {ISSUE_NUMBER} --add-label 'approved'
```

→ **STOP** ✅ Ticket terminé.

**Si des tests échouent :**

**Si `N_BROWSER_TEST >= 3` (limite de cycles atteinte) :**

```bash
write_state "6"

gh issue comment {ISSUE_NUMBER} --body "## ⚠️ Limite de cycles de tests browser atteinte

Les tests browser ont échoué pendant **$N_BROWSER_TEST cycles consécutifs**.
Les corrections automatiques n'ont pas suffi à résoudre toutes les anomalies.

### Derniers tests en échec

| ID | Scénario | Résultat |
|----|----------|----------|
[tableau complet avec PASS/FAIL/SKIP]

Intervention humaine requise. Pour relancer après correction manuelle, reposer le label \`analyze\`."

gh issue edit {ISSUE_NUMBER} --add-label 'help wanted'
```

→ **STOP** (l'humain reposera `analyze` après avoir corrigé)

**Sinon (cycles restants) :**

```bash
write_state "7"

gh issue comment {ISSUE_NUMBER} --body "## ❌ Tests browser — cycle $N_BROWSER_TEST

Des anomalies ont été détectées lors des tests browser.

| ID | Scénario | Résultat |
|----|----------|----------|
[tableau complet avec PASS/FAIL/SKIP]

**$TOTAL_PASS réussis, $TOTAL_FAIL échoués, $TOTAL_SKIP ignorés sur $TOTAL_TESTS tests.**

### Détail des anomalies

**[TEST_ID] — [titre du test]**
- **Étape en échec :** [description de l'étape]
- **Comportement observé :** [ce qui s'est passé]
- **Comportement attendu :** [ce qui était attendu]
- **Screenshot :** [lien ou référence]

[...]"
```

→ Exécuter Phase 7 directement (la table de routage mappe Phase 7 → `phase-5-corrections.md` avec contexte tests browser)

## 6.6 Nettoyage

```bash
# Fermer toutes les sessions browser
agent-browser close --all

# Détruire l'environnement éphémère
./scripts/tnr-docker.sh down
```
