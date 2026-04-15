---
name: regression-tests
description: Exécute les tests de non-régression browser décrits dans docs/browser-test-checklist.md via agent-browser, compile les résultats et crée des issues GitHub pour chaque problème détecté. Déclencher avec "/regression-tests" ou quand l'utilisateur demande de "lancer les tests de non-régression", "tester l'application dans le navigateur", "vérifier la non-régression".
allowed-tools: Bash(npx agent-browser:*), Bash(agent-browser:*), Bash(git:*), Read, Glob, Edit, Write
---

# Skill : regression-tests

Ce skill exécute l'intégralité des tests de non-régression décrits dans
`docs/browser-test-checklist.md` via `agent-browser`, puis crée des issues
GitHub pour chaque problème détecté.

---

## PHASE 1 — Préparation

### 1.1 Lecture du cahier de tests

Lis le fichier `docs/browser-test-checklist.md` pour récupérer :
- Les prérequis (URLs, utilisateurs de test)
- La liste complète des scénarios de test organisés par section

### 1.2 Configuration des URLs cibles

Les URLs cibles sont déterminées par les variables d'environnement
`BASE_URL` et `API_URL`. Par défaut, elles pointent vers la production :

```bash
BASE_URL="${BASE_URL:-https://blog.nickorp.com}"
API_URL="${API_URL:-https://blog.nickorp.com}"
```

Si aucune variable d'environnement n'est définie, utiliser :
- `BASE_URL=https://blog.nickorp.com`
- `API_URL=https://blog.nickorp.com`

Toutes les URLs utilisées dans les tests sont construites à partir de
`BASE_URL` (ex : `${BASE_URL}/comptes/connexion`).

#### Mode Docker local (environnement éphémère)

Pour exécuter les TNR sur un environnement Docker local identique à la
production mais accessible uniquement en localhost :

```bash
# 1. Démarrer l'environnement éphémère
./scripts/tnr-docker.sh up

# 2. Lancer les tests avec BASE_URL sur localhost
BASE_URL=http://localhost:8080 API_URL=http://localhost:8080 /regression-tests

# 3. Détruire l'environnement après les tests
./scripts/tnr-docker.sh down
```

L'environnement Docker éphémère (`docker-compose.test.yml`) reproduit
fidèlement la production : gunicorn, nginx, frontend buildé, PostgreSQL,
Redis, Celery — mais sans Traefik ni certificat TLS.

### 1.3 Vérification de l'environnement

Lis la référence partagée `.claude/skills/_shared/browser-tests/environment.md`
et applique le healthcheck (préflight curl avec retries, puis check navigateur).

**Si l'environnement reste non joignable** après tous les retries : **créer une
issue GitHub dédiée** pour que le problème soit tracé (le workflow amont peut
l'avoir déjà remonté côté CI, mais la visibilité côté issues est obligatoire) :

```bash
ENV_ISSUE_BODY="## ⚠️ Environnement non joignable

Le healthcheck des tests de non-régression a échoué : \`${BASE_URL}\` ne
répond pas (préflight curl + \`agent-browser open\` ont tous deux échoué
après retries).

**Date :** $(date -u '+%Y-%m-%d %H:%M UTC')
**BASE_URL :** ${BASE_URL}

Les scénarios ne seront pas exécutés. Vérifier :
- l'état des containers \`blog-tnr-*\` sur le VPS
- la connexion de \`claude-worker\` au réseau \`blog-tnr_default\`
- les logs nginx / django de l'environnement éphémère"

gh issue create \
  --repo nicolasdeclerck/test-squad-automation \
  --title "Tests de non-régression — Environnement non joignable $(date -u '+%Y-%m-%d')" \
  --label "non-regression tests,env-unreachable" \
  --body "$ENV_ISSUE_BODY"
```

Puis **STOP** (ne pas créer l'issue de suivi 1.5, ne pas lancer les scénarios).

### 1.4 Initialisation du rapport

Crée un fichier de rapport temporaire pour collecter les résultats :

```bash
REPORT_FILE="/tmp/regression-report-$(date +%Y%m%d-%H%M%S).json"
```

Initialise en mémoire une structure de résultats :

```
results = {
  "date": "YYYY-MM-DD HH:MM",
  "total": 0,
  "passed": 0,
  "failed": 0,
  "skipped": 0,
  "tests": []
}
```

### 1.5 Création de l'issue de suivi GitHub

Crée une issue GitHub dédiée au suivi de cette exécution de TNR.
Le corps de l'issue contient uniquement le nombre total de tests à lancer.

```bash
ISSUE_BODY="## 🧪 Tests de non-régression — $(date -u '+%Y-%m-%d %H:%M UTC')

**Environnement :** ${BASE_URL}
**Statut :** 🔄 En cours

---

**{total} tests** à exécuter."

TRACKING_ISSUE=$(gh issue create \
  --repo nicolasdeclerck/test-squad-automation \
  --title "Tests de non-régression — $(date -u '+%Y-%m-%d')" \
  --label "non-regression tests" \
  --body "$ISSUE_BODY" \
  --json number --jq '.number')
```

Conserve `TRACKING_ISSUE` (numéro de l'issue) pour les commentaires de progression.

---

## PHASE 2 — Exécution des tests

### 2.1 Principe d'exécution

Parcours chaque scénario du cahier de tests **dans l'ordre des sections**.
Pour chaque test :

1. **Identifie le type** : `[PUBLIC]`, `[AUTH]` ou `[OWNER]`
2. **Prépare le contexte d'authentification** si nécessaire (voir 2.2)
3. **Exécute les actions** décrites via `agent-browser`
4. **Vérifie les résultats attendus** via `snapshot`, `get text`, `get url`, `screenshot`
5. **Enregistre le résultat** : PASS, FAIL (avec détail), ou SKIP

### 2.2 Gestion de l'authentification

Lis la référence partagée `.claude/skills/_shared/browser-tests/sessions.md`
pour les conventions de sessions (`public` / `user1` / `user2`) et le flow
de connexion avec refs dynamiques.

### 2.3 Exécution d'un test unitaire

Lis la référence partagée `.claude/skills/_shared/browser-tests/execution.md`
pour le pattern d'exécution complet.

### 2.4 Évaluation du résultat

Les règles `PASS` / `FAIL` / `SKIP` sont décrites dans
`.claude/skills/_shared/browser-tests/execution.md`. Pour la TNR :

- En cas de `FAIL`, nomme le screenshot `/tmp/regression-fail-{test_id}.png`
  (convention spécifique au skill `regression-tests` pour suivi des runs
  nightly).

### 2.5 Enregistrement du résultat

Pour chaque test exécuté, ajoute une entrée au rapport :

```json
{
  "id": "1.1",
  "section": "Navigation et Layout",
  "name": "Affichage du header",
  "type": "PUBLIC",
  "status": "PASS|FAIL|SKIP",
  "details": "Description du problème si FAIL",
  "screenshot": "/tmp/regression-fail-1.1.png si FAIL",
  "url": "URL au moment du test"
}
```

### 2.6 Commentaire de progression sur l'issue de suivi

Après chaque **section** terminée, ajoute un **commentaire** sur l'issue
de suivi avec les résultats de cette section.

```bash
COMMENT_BODY="### {section_name}

| Statut | Test |
|--------|------|"

# Pour chaque test de la section, ajouter une ligne :
# | ✅ | [1.1] Affichage du header |
# | ❌ | [1.2] Navigation responsive — menu burger ne s'ouvre pas |
# | ⏭️ | [1.3] Test ignoré — Timeout |

COMMENT_BODY="$COMMENT_BODY

**Résultat section :** ✅ {passed} | ❌ {failed} | ⏭️ {skipped}
**Progression globale :** {tests_done}/{total} tests exécutés"

gh issue comment $TRACKING_ISSUE \
  --repo nicolasdeclerck/test-squad-automation \
  --body "$COMMENT_BODY"
```

**Important :** Un commentaire par section, pas par test individuel.

---

## PHASE 3 — Compilation des résultats

### 3.1 Résumé dans la console

Affiche un résumé clair des résultats :

```
═══════════════════════════════════════════════
  RAPPORT DE NON-RÉGRESSION — {date}
═══════════════════════════════════════════════

  Total : {total} tests
  ✓ Réussis  : {passed}
  ✗ Échoués  : {failed}
  ○ Ignorés  : {skipped}

───────────────────────────────────────────────
  DÉTAIL DES ÉCHECS
───────────────────────────────────────────────

  [{id}] {name}
    Section  : {section}
    Type     : {type}
    Détail   : {details}
    URL      : {url}
    Capture  : {screenshot}

═══════════════════════════════════════════════
```

### 3.2 Sauvegarde du rapport JSON

Écris le rapport complet dans le fichier :

```bash
# Écrire results en JSON dans $REPORT_FILE
```

Affiche le chemin du rapport : `Rapport sauvegardé : {REPORT_FILE}`

---

## PHASE 4 — Création des issues GitHub

### 4.1 Principe

Pour chaque test en **FAIL**, crée une issue GitHub dédiée.
Ne crée **aucune issue** si tous les tests sont PASS.

### 4.2 Vérification des doublons

Avant de créer une issue, vérifie qu'une issue ouverte avec le même
identifiant de test n'existe pas déjà :

```bash
gh search issues "regression {test_id}" --repo nicolasdeclerck/test-squad-automation --state open --json title --jq '.[].title'
```

Si une issue ouverte correspond déjà, **ne pas créer de doublon** —
ajouter un commentaire sur l'issue existante avec la date du nouveau
constat si le détail diffère.

### 4.3 Création de l'issue

Pour chaque FAIL sans doublon :

```bash
gh issue create \
  --repo nicolasdeclerck/test-squad-automation \
  --title "Régression [{test_id}] {test_name}" \
  --body "## Contexte

Test de non-régression automatisé — {date}

## Test échoué

| Champ | Valeur |
|-------|--------|
| ID | {test_id} |
| Section | {section} |
| Nom | {test_name} |
| Type | {type} |
| URL testée | {url} |

## Comportement observé

{details}

## Comportement attendu

{expected — extrait du cahier de tests}

## Capture d'écran

> Screenshot pris au moment du constat : \`{screenshot_path}\`

## Référence

Cahier de tests : \`docs/browser-test-checklist.md\` — section {section}"
```

### 4.4 Résumé des issues créées

Affiche la liste des issues créées :

```
Issues GitHub créées :
  - #{number} Régression [1.1] Affichage du header
  - #{number} Régression [7.2] Formulaire de commentaire — Non connecté
```

---

## PHASE 5 — Nettoyage et finalisation

### 5.1 Fermeture des sessions browser

```bash
agent-browser close --all
```

### 5.2 Finalisation de l'issue de suivi

Met à jour le **corps** de l'issue pour marquer l'exécution comme terminée,
et ajoute un **commentaire final** avec le bilan.

```bash
# Mise à jour du statut dans le corps de l'issue
FINAL_STATUS="✅ Terminé"
if [ "$FAILED_COUNT" -gt 0 ]; then
  FINAL_STATUS="❌ Terminé avec échecs"
fi

FINAL_BODY="## 🧪 Tests de non-régression — $(date -u '+%Y-%m-%d %H:%M UTC')

**Environnement :** ${BASE_URL}
**Statut :** ${FINAL_STATUS}

---

**${TOTAL} tests** exécutés — ✅ ${PASSED} | ❌ ${FAILED} | ⏭️ ${SKIPPED}"

gh issue edit $TRACKING_ISSUE \
  --repo nicolasdeclerck/test-squad-automation \
  --body "$FINAL_BODY"
```

Si tous les tests sont passés, ferme l'issue :

```bash
if [ "$FAILED_COUNT" -eq 0 ]; then
  gh issue close $TRACKING_ISSUE \
    --repo nicolasdeclerck/test-squad-automation \
    --reason completed
fi
```

### 5.3 Résumé final

Affiche un résumé concis :

```
Tests de non-régression terminés.
  {passed}/{total} tests réussis
  {failed} issues créées sur GitHub
  Suivi : issue #{TRACKING_ISSUE}
  Rapport : {REPORT_FILE}
```

---

## Règles d'exécution

1. **Exécuter TOUS les tests** du cahier, pas un sous-ensemble
2. **Ne jamais s'arrêter sur un échec** — continuer les tests suivants
3. **Capturer une screenshot** pour chaque FAIL
4. **Respecter l'ordre des sections** du cahier
5. **Réutiliser les sessions** authentifiées entre les tests du même type
6. **Ne pas créer d'issues en double** — toujours vérifier les existantes
7. **Les tests [OWNER]** nécessitent de créer des données de test (articles, commentaires) en début de session si elles n'existent pas
8. **Timeout** : si un test est bloqué plus de 30 secondes, le marquer SKIP avec le détail "Timeout"
