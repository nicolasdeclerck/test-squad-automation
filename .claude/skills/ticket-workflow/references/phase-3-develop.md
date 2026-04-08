# Phase 3 — Développement

## 3.1 Récupération du plan et de la progression

Récupère la liste des tâches depuis le fichier d'état (clé `tasks`) et
`CURRENT_TASK` pour reprendre à la bonne tâche :

```bash
cat "$STATE_FILE" | python3 -c "
import sys, json
d = json.load(sys.stdin)
for t in d.get('tasks', []):
    status = '✅' if t['status'] == 'completed' else '⬜'
    print(f\"{status} [{t['index']}] {t['description']}\")
"
```

Si un commentaire `## 🔄 Corrections demandées` ou
`## 🔄 Corrections demandées (tests browser)` existe, récupère-le pour
connaître les corrections spécifiques à apporter — elles priment sur le
plan initial pour les fichiers concernés :

```bash
gh issue view {ISSUE_NUMBER} --json comments \
  --jq '[.comments[] | select(.body | startswith("## 🔄 Corrections demandées"))] | last | .body'
```

## 3.2 Exécution des tâches

Pour chaque tâche depuis `CURRENT_TASK` :

1. Implémente en suivant le plan et les corrections éventuelles
2. Respecte les conventions du `CLAUDE.md`
3. Met à jour la progression dans le fichier d'état :

```bash
CURRENT_TASK=$((CURRENT_TASK + 1))
write_state "3"
```

## 3.3 Tests

```bash
docker compose up -d
docker compose exec -T django pip install -r requirements/development.txt -q
docker compose exec -T django pytest --cov=apps
docker compose stop
```

En cas d'échec : corriger le code, relancer. Maximum **3 tentatives**.

Si toujours en échec après 3 tentatives :
```bash
gh issue comment {ISSUE_NUMBER} --body "## ❌ Échec des tests après 3 tentatives
[logs d'erreur]
Intervention humaine requise."
gh issue edit {ISSUE_NUMBER} --add-label 'help wanted'
```
→ **STOP** (l'humain reposera `analyze` après avoir corrigé)

## 3.4 Commit et push

```bash
git config --global user.email "claude-worker@squad-automation.fr"
git config --global user.name "Claude Worker"

BRANCH_NAME="feat/issue-{ISSUE_NUMBER}-{slug-du-titre}"

# Vérifie si la branche existe déjà sur le remote
if git -C /workspace/test-squad-automation ls-remote --exit-code --heads origin "$BRANCH_NAME" > /dev/null 2>&1; then
  echo "Branche existante, commit sur $BRANCH_NAME"
else
  git checkout -b "$BRANCH_NAME"
fi

git add -A
git diff --cached --quiet || git commit -m "feat: close #{ISSUE_NUMBER} - {titre}"
git push origin "$BRANCH_NAME"
```

## 3.5 Vérification de la documentation

Après chaque implémentation, vérifie si les fichiers de documentation du projet
nécessitent des mises à jour en fonction des changements réalisés :

- **`CLAUDE.md`** : stack technique, modèles, endpoints API, conventions, architecture
- **`README.md`** : fonctionnalités, stack, structure du projet
- **`INSTALL.md`** : nouvelles dépendances, variables d'environnement, étapes d'installation

Pour chaque fichier, compare le contenu actuel avec les changements apportés.
Si une mise à jour est nécessaire, applique-la directement (pas de commentaire GitHub).

Exemples de changements déclencheurs :
- Nouveau modèle ou champ → mettre à jour la section modèles de `CLAUDE.md`
- Nouvel endpoint API → mettre à jour la section endpoints de `CLAUDE.md`
- Nouvelle dépendance Python/JS → mettre à jour `INSTALL.md` et la stack dans `README.md`/`CLAUDE.md`
- Nouvelle variable d'environnement → mettre à jour `INSTALL.md` et `CLAUDE.md`
- Nouvelle app ou dossier → mettre à jour l'arborescence dans `CLAUDE.md` et `README.md`
- Nouvelle fonctionnalité utilisateur → mettre à jour les fonctionnalités dans `README.md`

## 3.6 Commentaire de documentation

```bash
gh issue comment {ISSUE_NUMBER} --body "## 📝 Documentation

### Ce qui a été implémenté
[Résumé des fichiers créés/modifiés]

### Choix techniques
[Décisions importantes et pourquoi]

### Comment utiliser
[Guide pratique]

### Points d'attention
[Limitations, prérequis]"
```

## 3.7 Pull Request

```bash
EXISTING_PR=$(gh pr list --head "$BRANCH_NAME" --json number --jq '.[0].number' 2>/dev/null)

if [ -n "$EXISTING_PR" ]; then
  PR_NUMBER="$EXISTING_PR"
  gh pr edit "$PR_NUMBER" \
    --body "## Description

Closes #{ISSUE_NUMBER}

---

## Documentation

[contenu du commentaire de doc]"
  echo "PR #$PR_NUMBER mise à jour."
else
  PR_NUMBER=$(gh pr create \
    --title "feat: {titre du ticket}" \
    --body "## Description

Closes #{ISSUE_NUMBER}

---

## Documentation

[contenu du commentaire de doc]" \
    --base main \
    --head "$BRANCH_NAME" 2>&1 | grep -oP '/pull/\K[0-9]+')
  echo "PR #$PR_NUMBER créée."
fi
```

**Important :** `PR_NUMBER` doit être capturé ici pour être persisté par
`write_state()` à l'étape 3.8.

## 3.8 Transition vers Phase 4

```bash
N_DEV=$((N_DEV + 1))
write_state "4"
# → Exécuter Phase 4 directement
```
