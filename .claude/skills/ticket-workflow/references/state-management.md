# Gestion de l'état — `.claude-state.json`

## Lecture de l'état

```bash
STATE_FILE="$WORKTREE_PATH/.claude-state.json"

if [ -f "$STATE_FILE" ]; then
  PHASE=$(cat "$STATE_FILE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('phase','1'))")
  N_DEV=$(cat "$STATE_FILE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('n_dev',0))")
  N_REVIEW=$(cat "$STATE_FILE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('n_review',0))")
  N_CORRECTIONS=$(cat "$STATE_FILE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('n_corrections',0))")
  N_BROWSER_TEST=$(cat "$STATE_FILE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('n_browser_test',0))")
  CURRENT_TASK=$(cat "$STATE_FILE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('current_task',0))")
  APPROVED=$(cat "$STATE_FILE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('approved',False))")
else
  # Première exécution
  PHASE="1"
  N_DEV=0
  N_REVIEW=0
  N_CORRECTIONS=0
  N_BROWSER_TEST=0
  CURRENT_TASK=0
  APPROVED="False"
fi
```

## Fonction d'écriture d'état

À réutiliser après chaque transition de phase :

```bash
write_state() {
  python3 -c "
import json, sys
# Preserve browser_tests from existing state if present
existing = {}
try:
    with open('$STATE_FILE') as f:
        existing = json.load(f)
except:
    pass

state = {
  'issue_number': {ISSUE_NUMBER},
  'phase': '$1',
  'n_dev': $N_DEV,
  'n_review': $N_REVIEW,
  'n_corrections': $N_CORRECTIONS,
  'n_browser_test': ${N_BROWSER_TEST:-0},
  'current_task': $CURRENT_TASK,
  'approved': $APPROVED,
  'branch': '${BRANCH_NAME:-}',
  'pr_number': '${PR_NUMBER:-}',
  'browser_tests': existing.get('browser_tests', []),
  'tasks': existing.get('tasks', [])
}
print(json.dumps(state, indent=2))
" > "$STATE_FILE"
}
```

## Structure de `.claude-state.json`

```json
{
  "issue_number": 42,
  "phase": "3",
  "n_dev": 0,
  "n_review": 0,
  "n_corrections": 0,
  "n_browser_test": 0,
  "current_task": 2,
  "branch": "feat/issue-42-ma-feature",
  "pr_number": "15",
  "approved": false,
  "tasks": [
    {"index": 0, "description": "Créer le modèle X", "status": "completed"},
    {"index": 1, "description": "Ajouter la migration", "status": "completed"},
    {"index": 2, "description": "Créer la vue API", "status": "in_progress"},
    {"index": 3, "description": "Écrire les tests", "status": "pending"}
  ],
  "browser_tests": [
    {
      "id": "AUTH-01",
      "title": "Inscription d'un nouvel utilisateur",
      "type": "PUBLIC",
      "steps": "1. Ouvrir /signup\n2. Remplir le formulaire\n3. Vérifier la redirection"
    }
  ]
}
```

Phases possibles : `"1"`, `"2"`, `"3"`, `"4"`, `"5"`, `"6"`, `"7"`, `"done"`

## Gestion des erreurs — Interruption par quota de tokens

Si l'exécution de Claude Code est interrompue (ex : dépassement du quota de tokens),
le flux appelant (GitHub Actions, script manuel) **doit** exécuter les actions
suivantes pour signaler l'arrêt :

```bash
# 1. Ajouter le label "standby" au ticket
gh issue edit {ISSUE_NUMBER} --add-label 'standby'

# 2. Poster un commentaire explicatif
gh issue comment {ISSUE_NUMBER} --body "## ⚠️ Exécution interrompue

Les travaux ont été stoppés suite au dépassement des quotas de tokens de Claude Code.

**Phase en cours :** {phase courante depuis .claude-state.json}
**Date :** $(date -u '+%Y-%m-%d %H:%M UTC')

L'exécution reprendra automatiquement à la phase interrompue grâce au fichier d'état
\`.claude-state.json\`. Pour relancer, reposer le label \`analyze\` sur le ticket."
```

**Détection de l'erreur :** Le processus Claude Code retourne un code de sortie
non-zéro en cas d'interruption. Le flux appelant doit vérifier ce code de retour
et déclencher la procédure ci-dessus.

**Reprise :** Lorsque le label `analyze` est reposé, le workflow reprend grâce
à la table de routage qui lit `.claude-state.json` et redémarre à la bonne phase.
Le label `standby` est retiré au redémarrage.
