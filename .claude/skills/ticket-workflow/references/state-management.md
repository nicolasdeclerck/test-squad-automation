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

À réutiliser après chaque transition de phase.

> **Important :** les variables sont passées à Python **par l'environnement**
> (pas par interpolation shell dans le code Python). Cela évite qu'un
> caractère spécial (`'`, `"`, `\`, saut de ligne, `$`) dans `BRANCH_NAME`,
> `PR_NUMBER` ou une valeur numérique vide corrompe le JSON généré.

```bash
write_state() {
  NEW_PHASE="$1" \
  ISSUE_NUMBER="${ISSUE_NUMBER}" \
  STATE_FILE_PATH="$STATE_FILE" \
  N_DEV="${N_DEV:-0}" \
  N_REVIEW="${N_REVIEW:-0}" \
  N_CORRECTIONS="${N_CORRECTIONS:-0}" \
  N_BROWSER_TEST="${N_BROWSER_TEST:-0}" \
  CURRENT_TASK="${CURRENT_TASK:-0}" \
  APPROVED="${APPROVED:-False}" \
  BRANCH_NAME="${BRANCH_NAME:-}" \
  PR_NUMBER="${PR_NUMBER:-}" \
  python3 - <<'PY' > "$STATE_FILE.tmp" && mv "$STATE_FILE.tmp" "$STATE_FILE"
import json, os

state_file = os.environ["STATE_FILE_PATH"]

# Preserve browser_tests and tasks from existing state if present
existing = {}
try:
    with open(state_file) as f:
        existing = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    pass

def as_int(name, default=0):
    v = os.environ.get(name, "").strip()
    return int(v) if v else default

def as_bool(name, default=False):
    v = os.environ.get(name, "").strip().lower()
    if v in ("true", "1", "yes"):
        return True
    if v in ("false", "0", "no", ""):
        return False
    return default

state = {
    "issue_number": as_int("ISSUE_NUMBER"),
    "phase": os.environ["NEW_PHASE"],
    "n_dev": as_int("N_DEV"),
    "n_review": as_int("N_REVIEW"),
    "n_corrections": as_int("N_CORRECTIONS"),
    "n_browser_test": as_int("N_BROWSER_TEST"),
    "current_task": as_int("CURRENT_TASK"),
    "approved": as_bool("APPROVED"),
    "branch": os.environ.get("BRANCH_NAME", ""),
    "pr_number": os.environ.get("PR_NUMBER", ""),
    "browser_tests": existing.get("browser_tests", []),
    "tasks": existing.get("tasks", []),
}
print(json.dumps(state, indent=2, ensure_ascii=False))
PY
}
```

L'écriture passe par un fichier temporaire (`$STATE_FILE.tmp` + `mv`) pour
rendre le remplacement atomique : si Python échoue, le fichier d'état
précédent reste intact et la reprise fonctionne.

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

Phases possibles : `"1"`, `"2"`, `"3"`, `"4"`, `"5"`, `"done"`

> **Note :** Les phases `"6"` (tests browser) et `"7"` (corrections post-tests
> browser) ont été retirées du `ticket-workflow` lors du découplage. Les tests
> browser sont désormais exécutés à la demande via le workflow GitHub Actions
> `browser-tests.yml` (skill séparé `browser-tests-on-demand`). Si un state
> file existant contient `phase: "6"` ou `"7"`, il faut le considérer comme
> `"done"` (tests browser déportés).

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
