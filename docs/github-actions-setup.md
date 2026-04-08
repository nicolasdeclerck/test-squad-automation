# Configuration GitHub Actions — Tests de non-régression

## Prérequis

- Un VPS avec Docker installé et le container `claude-worker` en cours d'exécution
- Une clé SSH permettant l'accès au VPS
- Le repo GitHub avec les permissions d'administration pour configurer les secrets

## Secrets à configurer

Aller dans **Settings → Secrets and variables → Actions → New repository secret** et ajouter les secrets suivants :

| Secret | Description | Exemple |
|---|---|---|
| `VPS_HOST` | IP ou nom de domaine du VPS | `192.168.1.100` ou `vps.example.com` |
| `VPS_SSH_KEY` | Contenu complet de la clé privée SSH (clé qui a accès au VPS) | Contenu de `~/.ssh/id_ed25519` |

> **Note :** `GITHUB_TOKEN` est injecté automatiquement par GitHub Actions. Il ne faut **pas** le créer manuellement.

## Ajouter la clé SSH

1. Copier le contenu de la clé privée :
   ```bash
   cat ~/.ssh/id_ed25519
   ```
2. Dans GitHub, aller dans **Settings → Secrets and variables → Actions**
3. Cliquer sur **New repository secret**
4. Nom : `VPS_SSH_KEY`
5. Coller le contenu complet de la clé (y compris les lignes `-----BEGIN` et `-----END`)
6. Cliquer sur **Add secret**

## Ajouter l'hôte du VPS

1. Dans GitHub, aller dans **Settings → Secrets and variables → Actions**
2. Cliquer sur **New repository secret**
3. Nom : `VPS_HOST`
4. Valeur : l'IP ou le domaine du VPS
5. Cliquer sur **Add secret**

## Fonctionnement du workflow

Le workflow `.github/workflows/regression-tests.yml` :

- Se déclenche **automatiquement chaque nuit à 2h UTC**
- Peut être **déclenché manuellement** via l'onglet Actions → Regression Tests → Run workflow
- Vérifie s'il y a eu des PRs mergées sur `main` dans les dernières 24h
- Si aucun merge : le workflow se termine proprement sans exécuter les tests
- Si au moins un merge : se connecte au VPS via SSH et lance les tests de non-régression via Claude Code
