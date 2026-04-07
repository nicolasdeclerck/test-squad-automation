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

Les URLs cibles sont **toujours** les URLs de production, sauf si les
variables d'environnement `BASE_URL` et `API_URL` sont explicitement définies :

```bash
BASE_URL="${BASE_URL:-https://blog.nickorp.com}"
API_URL="${API_URL:-https://blog.nickorp.com}"
```

**IMPORTANT : ne jamais utiliser `localhost` ou `127.0.0.1`.** Si aucune
variable d'environnement n'est définie, utiliser obligatoirement :
- `BASE_URL=https://blog.nickorp.com`
- `API_URL=https://blog.nickorp.com`

Toutes les URLs utilisées dans les tests sont construites à partir de
`BASE_URL` (ex : `${BASE_URL}/comptes/connexion`).

### 1.3 Vérification de l'environnement

Vérifie que l'application est accessible :

```bash
agent-browser open ${BASE_URL} && agent-browser wait --load networkidle && agent-browser snapshot -i
```

Si l'application n'est pas accessible, affiche un message d'erreur et **STOP**.

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

Crée une issue GitHub dédiée au suivi en temps réel de cette exécution de TNR.
Le corps de l'issue contient la liste de tous les tests extraits du cahier,
avec un statut initial `⏳` (en attente).

```bash
# Construire le corps de l'issue avec la liste des tests
ISSUE_BODY="## 🧪 Tests de non-régression — $(date -u '+%Y-%m-%d %H:%M UTC')

**Environnement :** ${BASE_URL}
**Statut :** 🔄 En cours

---

### Progression

| Statut | Test | Section |
|--------|------|---------|"

# Pour chaque test du cahier, ajouter une ligne :
# | ⏳ | [ID] Nom du test | Section |
# Exemple :
# | ⏳ | [1.1] Affichage du header | Navigation et Layout |

ISSUE_BODY="$ISSUE_BODY

---

### Légende
- ⏳ En attente
- ✅ Réussi (PASS)
- ❌ Échoué (FAIL)
- ⏭️ Ignoré (SKIP)

---
**Total :** {total} tests | ✅ 0 | ❌ 0 | ⏭️ 0"

TRACKING_ISSUE=$(gh issue create \
  --repo nicolasdeclerck/test-squad-automation \
  --title "Tests de non-régression — $(date -u '+%Y-%m-%d')" \
  --label "non-regression tests" \
  --body "$ISSUE_BODY" \
  --json number --jq '.number')
```

Conserve `TRACKING_ISSUE` (numéro de l'issue) pour la mise à jour progressive.

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

Utilise des sessions nommées pour gérer les contextes d'auth :

```bash
# Session non connectée (tests [PUBLIC])
agent-browser --session public open ${BASE_URL}

# Connexion utilisateur 1 (tests [AUTH] et [OWNER])
agent-browser --session user1 open ${BASE_URL}/comptes/connexion
agent-browser --session user1 snapshot -i
agent-browser --session user1 fill @eN "testuser@example.com"
agent-browser --session user1 fill @eM "Testpass123!"
agent-browser --session user1 click @eK
agent-browser --session user1 wait --load networkidle

# Connexion utilisateur 2 (tests inter-utilisateurs)
agent-browser --session user2 open ${BASE_URL}/comptes/connexion
# ... même flow avec testuser2@example.com ...
```

**Important :** Réutilise les sessions entre les tests du même type pour
éviter de se reconnecter à chaque test.

### 2.3 Exécution d'un test unitaire

Pour chaque scénario, le pattern est :

```bash
# 1. Navigation
agent-browser --session {session} open {url}
agent-browser --session {session} wait --load networkidle

# 2. Snapshot pour découvrir les éléments
agent-browser --session {session} snapshot -i

# 3. Actions (fill, click, select selon le scénario)
agent-browser --session {session} fill @eN "valeur"
agent-browser --session {session} click @eM

# 4. Vérification
agent-browser --session {session} snapshot -i
agent-browser --session {session} get text @eX
agent-browser --session {session} get url
```

### 2.4 Évaluation du résultat

Pour chaque vérification décrite dans le cahier :

- **PASS** : le comportement observé correspond au résultat attendu
- **FAIL** : le comportement observé diffère du résultat attendu
- **SKIP** : le test ne peut pas être exécuté (prérequis manquant, donnée de test absente)

En cas de **FAIL**, capture systématiquement :
```bash
agent-browser --session {session} screenshot /tmp/regression-fail-{test_id}.png
```

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

### 2.6 Mise à jour de l'issue de suivi

Après chaque test exécuté, mets à jour le **corps** de l'issue de suivi
(pas de commentaire) pour refléter la progression en temps réel.

**Actions :**

1. Remplace le statut du test dans le tableau :
   - `⏳` → `✅` si PASS
   - `⏳` → `❌` si FAIL (ajouter le détail entre parenthèses)
   - `⏳` → `⏭️` si SKIP
2. Met à jour les compteurs en bas de l'issue
3. Met à jour via `gh issue edit` :

```bash
# Reconstruire le corps complet de l'issue avec les statuts mis à jour
gh issue edit $TRACKING_ISSUE \
  --repo nicolasdeclerck/test-squad-automation \
  --body "$UPDATED_BODY"
```

**Important :** Ne pas mettre à jour après chaque test individuel si cela
ralentit trop l'exécution. Mettre à jour **par section** (après tous les
tests d'une même section) est un bon compromis entre suivi temps réel et
performance.

**Exemple de ligne mise à jour :**
```
| ✅ | [1.1] Affichage du header | Navigation et Layout |
| ❌ | [1.2] Navigation responsive (détail: menu burger ne s'ouvre pas) | Navigation et Layout |
| ⏭️ | [2.1] Inscription utilisateur | Authentification |
```

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

Met à jour une dernière fois le corps de l'issue de suivi pour marquer
l'exécution comme terminée :

1. Remplace `**Statut :** 🔄 En cours` par `**Statut :** ✅ Terminé` (ou
   `**Statut :** ❌ Terminé avec échecs` si des tests ont échoué)
2. S'assure que tous les compteurs sont à jour

```bash
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
