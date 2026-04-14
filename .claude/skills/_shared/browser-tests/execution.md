# Exécution d'un scénario de test browser

Partagé entre `regression-tests` et `browser-tests-on-demand`.

## Pattern d'exécution

Pour chaque scénario :

1. **Identifier le type** (`[PUBLIC]` / `[AUTH]` / `[OWNER]`) → choisir la
   session (voir `sessions.md`).
2. **Suivre les étapes** décrites dans le scénario via `agent-browser`
   (`open`, `snapshot`, `click`, `fill`, `wait`, `get text`, `get url`).
3. **Vérifier chaque assertion** (présence d'éléments, texte attendu,
   navigation correcte).
4. **En cas d'échec** : capturer un screenshot et enregistrer le détail.
5. **Enregistrer le résultat** : `PASS` / `FAIL` / `SKIP` avec détail.

```bash
# Navigation
agent-browser --session "$SESSION" open "$URL"
agent-browser --session "$SESSION" wait --load networkidle

# Découverte des refs
agent-browser --session "$SESSION" snapshot -i

# Actions (exemple)
agent-browser --session "$SESSION" fill @eN "valeur"
agent-browser --session "$SESSION" click @eM

# Vérification
agent-browser --session "$SESSION" snapshot -i
agent-browser --session "$SESSION" get text @eX
agent-browser --session "$SESSION" get url

# En cas d'échec, screenshot obligatoire
agent-browser --session "$SESSION" screenshot /tmp/browser-fail-${TEST_ID}.png
```

## Évaluation du résultat

| Statut | Critère |
|--------|---------|
| `PASS` | Comportement observé == résultat attendu du cahier |
| `FAIL` | Comportement observé != résultat attendu |
| `SKIP` | Prérequis manquant, donnée absente, ou ID inconnu dans le checklist |

## Règles de robustesse

1. **Ne jamais s'arrêter sur un échec** — continuer avec les tests suivants.
2. **Capturer un screenshot** pour chaque `FAIL`.
3. **Timeout** : si un test bloque plus de 30 secondes, le marquer `SKIP`
   avec détail `"Timeout"`.
4. **Tests `[OWNER]`** : si les données de test (articles, commentaires) ne
   sont pas présentes, les créer en début de session plutôt que de `SKIP`.
5. **Refs dynamiques** : re-snapshotter après chaque navigation ou changement
   DOM — les refs `@eN` changent.

## Structure du résultat à conserver

Pour chaque test exécuté, conserver en mémoire :

```json
{
  "id": "1.1",
  "section": "Navigation et Layout",
  "title": "Affichage du header",
  "type": "PUBLIC",
  "status": "PASS",
  "details": "",
  "screenshot": "",
  "url": "https://..."
}
```

Les skills consommateurs (`regression-tests`, `browser-tests-on-demand`)
agrègent ces résultats pour produire leur rapport et leurs issues GitHub.
