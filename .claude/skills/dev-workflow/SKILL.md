---
name: dev-workflow
description: Processus complet de developpement d'un ticket GitHub. Execute de bout en bout : mise a jour des labels, recuperation des consignes, implementation, tests, commit, push, documentation, PR et cloture. Triggers include "dev-workflow", "developpe le ticket", "implemente l'issue", ou toute demande de traiter un ticket GitHub de A a Z.
allowed-tools: Bash(gh:*), Bash(git:*), Bash(docker compose:*), Bash(docker:*)
---

# Skill : dev-workflow

Ce skill decrit le processus complet de developpement d'un ticket GitHub dans ce repo.
Tu dois l'executer de bout en bout de maniere autonome, en verifiant les criteres de
sortie a chaque etape avant de passer a la suivante.

---

## 1. Mise a jour des labels

Mets a jour les labels du ticket pour signaler que le developpement demarre.

```bash
gh api repos/nicolasdeclerck/test-squad-automation/issues/{ISSUE_NUMBER}/labels/go%20for%20dev -X DELETE
gh api repos/nicolasdeclerck/test-squad-automation/issues/{ISSUE_NUMBER}/labels -X POST -f "labels[]=in progress"
```

**Critere de sortie :** les deux commandes retournent un code 0 sans erreur.

**Gestion d'erreur :** si le label `go for dev` n'existe pas sur le ticket (deja retire),
ignore l'erreur 404 et continue.

---

## 2. Recuperation des consignes

Recupere le dernier commentaire du ticket qui contient les consignes de developpement.

```bash
gh issue view {ISSUE_NUMBER} --comments --json comments -q '.comments[-1].body'
```

**Critere de sortie :** le commentaire contient les sections `## Consignes de developpement`
et `## Questions bloquantes` (signature d'une analyse complete).

**Gestion d'erreur :** si le dernier commentaire ne ressemble pas a une analyse
(absent ou trop court), remonte dans les commentaires pour trouver celui qui contient
`## Analyse`. Ne demarre pas l'implementation sans consignes claires.

---

## 3. Creation du worktree isole

Cree un repertoire de travail isole sur une nouvelle branche pour ce ticket.

```bash
BRANCH_NAME="feat/issue-{ISSUE_NUMBER}-{slug-du-titre}"
WORKTREE_PATH="/workspace/test-squad-automation-issue-{ISSUE_NUMBER}"

git -C /workspace/test-squad-automation worktree add "$WORKTREE_PATH" -b "$BRANCH_NAME" origin/main 2>/dev/null \
  || git -C /workspace/test-squad-automation worktree add "$WORKTREE_PATH" "$BRANCH_NAME"

cd "$WORKTREE_PATH"
```

Le slug du titre est le titre du ticket en minuscules, avec les caracteres non
alphanumeriques remplaces par des tirets, tronque a 40 caracteres.

**Critere de sortie :** `git worktree list` affiche bien le nouveau repertoire
avec la bonne branche.

**Gestion d'erreur :** si le worktree existe deja (reprise), ne pas recreer la
branche -- utiliser `git worktree add "$WORKTREE_PATH" "$BRANCH_NAME"` sans le
flag `-b`.

> **Toutes les etapes suivantes (implementation, tests, commit, push, PR) doivent
> etre executees depuis `$WORKTREE_PATH`.**

---

## 4. Implementation

Implemente le ticket en suivant exactement les consignes recuperees a l'etape 2 :
- Cree ou modifie les fichiers necessaires
- Ecris les tests demandes
- Respecte les conventions du CLAUDE.md

**Critere de sortie :** tous les fichiers listes dans les consignes ont ete crees
ou modifies. Les tests demandes existent dans le code.

**Gestion d'erreur :** si une consigne est ambigue ou contradictoire avec le code
existant, applique le principe de moindre surprise -- choisis l'interpretation la plus
coherente avec le reste du projet et documente ton choix dans le commentaire de review
(etape 7).

---

## 5. Tests

Lance les tests et verifie qu'ils passent tous.

```bash
docker compose up -d
docker compose exec -T django pip install -r requirements/development.txt -q
docker compose exec -T django pytest --cov=apps
docker compose stop
```

**Critere de sortie :** exit code 0, aucun test en echec (`failed` absent des logs).

**Gestion d'erreur :**
- Si des tests echouent, analyse les logs, corrige le code (jamais les tests sauf s'ils
  sont manifestement incorrects), et relance les tests.
- Repete jusqu'a ce que tous les tests passent, avec un maximum de **3 tentatives**.
- Si apres 3 tentatives les tests echouent encore, poste un commentaire sur le ticket
  expliquant les erreurs rencontrees, ajoute le label `help wanted`, et arrete-toi.

```bash
gh issue comment {ISSUE_NUMBER} --body "## Echec des tests apres 3 tentatives\n\n{logs d'erreur}\n\nIntervention humaine requise."
gh api repos/nicolasdeclerck/test-squad-automation/issues/{ISSUE_NUMBER}/labels -X POST -f "labels[]=help wanted"
```

---

## 6. Commit et push

Commite le travail et pousse la branche. La branche a deja ete creee via le
worktree a l'etape 3.

```bash
git config --global user.email "claude-worker@squad-automation.fr"
git config --global user.name "Claude Worker"
git add -A
git diff --cached --quiet || git commit -m "feat: close #{ISSUE_NUMBER} - {titre du ticket}"
git push origin "$BRANCH_NAME"
```

**Critere de sortie :** le push retourne un code 0 et la branche est visible
sur le remote (`git ls-remote --heads origin feat/issue-{ISSUE_NUMBER}-*`).

**Gestion d'erreur :**
- Si la branche existe deja sur le remote (push rejete), utilise `--force-with-lease`
  (reprise d'une execution precedente).
- Si le depot distant est inaccessible, attends 10 secondes et reessaie une fois.
- Ne force jamais le push sur `main` ou `master`.

---

## 7. Commentaire de documentation

Poste un commentaire sur le ticket qui documente le travail realise.

```bash
gh issue comment {ISSUE_NUMBER} --body "## Documentation de l'implementation

### Ce qui a ete implemente
{resume clair des fichiers crees/modifies}

### Choix techniques
{decisions d'architecture ou d'implementation importantes et pourquoi}

### Comment utiliser cette evolution
{guide pratique : commandes, URLs, configuration necessaire}

### Points d'attention
{limitations, prerequis, choses a surveiller}"
```

**Critere de sortie :** le commentaire est poste et visible sur le ticket GitHub.

---

## 8. Pull Request

Cree la PR vers `main` en reutilisant le contenu du commentaire de documentation.

```bash
gh pr create \
  --title "feat: {titre du ticket}" \
  --body "## Description

Closes #{ISSUE_NUMBER}

---

## Documentation

{contenu du commentaire de doc}" \
  --base main \
  --head feat/issue-{ISSUE_NUMBER}-{slug-du-titre}
```

**Critere de sortie :** la PR est creee et son URL est affichee dans le terminal.

**Gestion d'erreur :**
- Si une PR existe deja pour cette branche (`gh pr list --head feat/issue-{ISSUE_NUMBER}-*`),
  ne cree pas de doublon -- mets a jour la PR existante avec `gh pr edit`.
- Si la branche n'est pas a jour avec `main`, ne rebase pas automatiquement -- signale-le
  dans la PR via un commentaire.

---

## 9. Cloture

Mets a jour les labels pour signaler que le ticket est pret pour review.

```bash
gh api repos/nicolasdeclerck/test-squad-automation/issues/{ISSUE_NUMBER}/labels/in%20progress -X DELETE
gh api repos/nicolasdeclerck/test-squad-automation/issues/{ISSUE_NUMBER}/labels -X POST -f "labels[]=to review"
```

**Critere de sortie :** le ticket affiche uniquement le label `to review`.

**Gestion d'erreur :** si le label `in progress` n'existe plus sur le ticket,
ignore l'erreur 404 et continue avec l'ajout de `to review`.

---

## 10. Nettoyage du worktree

Une fois le ticket termine, supprime le worktree isole.

```bash
cd /workspace/test-squad-automation
git worktree remove "$WORKTREE_PATH" --force
```

**Critere de sortie :** `git worktree list` ne contient plus `$WORKTREE_PATH`.
