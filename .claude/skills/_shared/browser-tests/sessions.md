# Gestion des sessions d'authentification — tests browser

Partagé entre `regression-tests` et `browser-tests-on-demand`.

## Sessions nommées

Les tests utilisent des sessions `agent-browser` nommées pour éviter de se
reconnecter à chaque test et pour isoler les contextes d'auth :

| Session | Usage | Identifiant | Mot de passe |
|---------|-------|-------------|--------------|
| `public` | Tests `[PUBLIC]` (non connecté) | — | — |
| `user1` | Tests `[AUTH]` et `[OWNER]` | `testuser@example.com` | `Testpass123!` |
| `user2` | Tests inter-utilisateurs | `testuser2@example.com` | `Testpass123!` |

## Connexion d'une session authentifiée

Les refs `@e1`, `@e2`, … retournés par `snapshot -i` sont **dynamiques**. Il
faut snapshotter puis utiliser les refs réels (pas de placeholders type
`@emailInput`).

```bash
# Dans claude-worker, Chrome doit démarrer sans sandbox
export AGENT_BROWSER_ARGS=--no-sandbox

agent-browser --session user1 open "$BASE_URL/comptes/connexion"
agent-browser --session user1 wait --load networkidle
agent-browser --session user1 snapshot -i
# Lire les refs retournés dans la sortie (ex: @e1 = email, @e2 = password, @e3 = submit)
agent-browser --session user1 fill @e1 "testuser@example.com"
agent-browser --session user1 fill @e2 "Testpass123!"
agent-browser --session user1 click @e3
agent-browser --session user1 wait --load networkidle
```

## Règles d'utilisation

1. **Réutiliser** les sessions entre tests du même type (pas de reconnexion par
   test).
2. **Choisir** la session à partir du type déclaré du scénario (`[PUBLIC]` /
   `[AUTH]` / `[OWNER]`).
3. **Ne jamais** mélanger les sessions dans un même scénario — un test
   `[OWNER]` peut toutefois utiliser `user1` + `user2` quand il teste
   l'interaction inter-utilisateur (explicitement prévu dans le scénario).
4. **Nettoyage final** : `agent-browser close --all` à la fin du run.
