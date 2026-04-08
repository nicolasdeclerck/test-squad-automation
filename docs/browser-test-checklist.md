# Cahier de tests de non-regression — Browser Tests

> **Objectif** : Ce document recense les scénarios de test fonctionnels à exécuter dans le navigateur pour valider le bon fonctionnement de l'application Blog Django + React.
> Il est conçu pour être utilisé par `agent-browser` dans le cadre de l'automatisation des tests front-end.

## Prérequis

| Élément | Valeur |
|---------|--------|
| URL Frontend | Définie par la variable `BASE_URL` (par défaut : `https://blog.nickorp.com`) |
| URL API | Définie par la variable `API_URL` (par défaut : `https://blog.nickorp.com`) |
| Navigateur cible | Chromium (via Playwright) |
| Utilisateur test 1 | email: `testuser@example.com` / mot de passe: `Testpass123!` |
| Utilisateur test 2 | email: `testuser2@example.com` / mot de passe: `Testpass123!` |

> **Note** : Les utilisateurs de test doivent être créés au préalable via l'interface d'inscription ou via le backend Django.
>
> **Configuration des URLs** : Les variables `BASE_URL` et `API_URL` permettent de cibler différents environnements.
> Par défaut (si non définies), utiliser les URLs de production :
> `BASE_URL=https://blog.nickorp.com` / `API_URL=https://blog.nickorp.com`
> **Ne jamais utiliser `localhost` sauf si explicitement demandé.**

---

## Conventions

- **[PUBLIC]** : Test exécutable sans authentification
- **[AUTH]** : Nécessite un utilisateur connecté
- **[OWNER]** : Nécessite d'être l'auteur de la ressource
- Chaque test indique : l'action à réaliser, le résultat attendu, et les sélecteurs/URLs clés

---

## 1. Navigation et Layout

### 1.1 — [PUBLIC] Affichage du header

- **Action** : Ouvrir `{BASE_URL}`
- **Vérifications** :
  - Le logo/nom "NICKORP" est visible dans le header
  - Les liens "Accueil", "Articles", "A propos", "Contact" sont visibles
  - Les boutons "Connexion" et "Inscription" sont visibles (utilisateur non connecté)

### 1.2 — [AUTH] Header utilisateur connecté

- **Action** : Se connecter puis vérifier le header
- **Vérifications** :
  - Le bouton "Connexion" / "Inscription" disparaît
  - Le nom d'utilisateur ou avatar apparaît dans le header
  - Un bouton "Ajouter un article" est visible
  - Un menu déroulant utilisateur est accessible (clic sur le nom/avatar)
  - Le menu contient : "Mes brouillons", "Modifier profil", "Déconnexion"

### 1.3 — [PUBLIC] Affichage du footer

- **Action** : Scroller en bas de page
- **Vérifications** :
  - Le footer est visible avec le copyright
  - Le lien "Suivi des devs" est visible si connecté

### 1.4 — [PUBLIC] Navigation mobile (responsive)

- **Action** : Redimensionner la fenêtre en dessous de 768px
- **Vérifications** :
  - Le menu burger apparaît
  - Clic sur le menu burger ouvre la navigation mobile
  - Tous les liens de navigation sont accessibles dans le menu mobile

---

## 2. Authentification

### 2.1 — [PUBLIC] Inscription d'un nouvel utilisateur

- **URL** : `/comptes/inscription`
- **Action** : Remplir le formulaire avec email, mot de passe et confirmation
- **Vérifications** :
  - Le formulaire affiche les champs : email, mot de passe, confirmation mot de passe
  - Soumission avec des données valides redirige vers `/`
  - L'utilisateur est automatiquement connecté après inscription
  - Le header reflète l'état connecté

### 2.2 — [PUBLIC] Inscription — Validation des erreurs

- **URL** : `/comptes/inscription`
- **Actions et vérifications** :
  - Soumission avec champs vides → message d'erreur affiché
  - Mots de passe non identiques → message d'erreur affiché
  - Email déjà utilisé → message d'erreur affiché
  - Mot de passe trop court/simple → message d'erreur affiché

### 2.3 — [PUBLIC] Connexion utilisateur

- **URL** : `/comptes/connexion`
- **Action** : Saisir email et mot de passe valides, soumettre
- **Vérifications** :
  - Les champs email et mot de passe sont affichés
  - Soumission réussie redirige vers `/`
  - Le header affiche l'état connecté
  - Le lien vers l'inscription est présent ("Pas encore de compte ?")

### 2.4 — [PUBLIC] Connexion — Erreurs

- **URL** : `/comptes/connexion`
- **Actions et vérifications** :
  - Email/mot de passe incorrects → message d'erreur affiché
  - Champs vides → message d'erreur affiché

### 2.5 — [AUTH] Déconnexion

- **Action** : Cliquer sur le menu utilisateur puis "Déconnexion"
- **Vérifications** :
  - L'utilisateur est redirigé vers `/`
  - Le header affiche les boutons "Connexion" / "Inscription"
  - Les routes protégées redirigent vers `/comptes/connexion`

### 2.6 — [PUBLIC] Protection des routes

- **Action** : Accéder directement à `/articles/creer` sans être connecté
- **Vérifications** :
  - Redirection automatique vers `/comptes/connexion`
  - Même comportement pour `/articles/mes-brouillons`, `/comptes/profil/modifier`

---

## 3. Articles — Liste et consultation

### 3.1 — [PUBLIC] Page d'accueil — Liste des articles

- **URL** : `/`
- **Vérifications** :
  - Les articles publiés sont affichés sous forme de cartes
  - Maximum 10 articles affichés
  - Chaque carte affiche : titre, auteur (nom + avatar), date, extrait du contenu
  - Un lien "Voir tous les articles" est présent si plus de 10 articles existent

### 3.2 — [PUBLIC] Page articles — Pagination

- **URL** : `/articles`
- **Vérifications** :
  - Les articles publiés sont listés avec pagination (10 par page)
  - Les boutons "Précédent" / "Suivant" fonctionnent
  - Le numéro de page actuel est indiqué
  - Les brouillons ne sont PAS affichés dans la liste

### 3.3 — [PUBLIC] Détail d'un article

- **URL** : `/articles/{slug}`
- **Vérifications** :
  - Le titre de l'article est affiché
  - Le contenu riche (BlockNote) est rendu correctement en HTML
  - L'auteur est affiché avec son avatar et son nom
  - La date de publication est affichée
  - La section commentaires est visible en bas de page

### 3.4 — [AUTH/OWNER] Boutons d'action sur un article

- **URL** : `/articles/{slug}` (en tant qu'auteur de l'article)
- **Vérifications** :
  - Les icônes "Modifier" et "Supprimer" sont visibles
  - Clic sur "Modifier" redirige vers `/articles/{slug}/modifier`
  - Clic sur "Supprimer" redirige vers `/articles/{slug}/supprimer`
  - Ces boutons sont ABSENTS si l'utilisateur n'est pas l'auteur

### 3.5 — [AUTH/OWNER] Bandeau "Modifications non publiées" sur un article publié

- **URL** : `/articles/{slug}` (article publié avec `has_draft === true`, en tant qu'auteur)
- **Vérifications** :
  - Un bandeau/alerte indiquant "Cet article a des modifications non publiées" est visible
  - Le bandeau contient un lien "Voir les modifications" qui mène à `/articles/{slug}/modifier`
  - Le bandeau n'est PAS visible pour un utilisateur non-auteur
  - Le bandeau n'est PAS visible pour un visiteur non connecté
  - Le bandeau n'est PAS visible si `has_draft === false`

### 3.6 — [AUTH/OWNER] Bouton "Publier les modifications" pour re-publication

- **URL** : `/articles/{slug}` (article publié avec `has_draft === true`, en tant qu'auteur)
- **Vérifications** :
  - Un bouton "Publier les modifications" est visible (libellé différent de "Publier" pour un premier draft)
  - Clic sur le bouton appelle l'API de publication
  - Après succès : le bandeau disparaît, le contenu mis à jour est affiché, `has_draft` repasse à `false`
  - Le bouton "Publier" classique est toujours affiché pour un article en statut "draft"

### 3.7 — [AUTH/OWNER] Badge "brouillon en cours" dans les listes d'articles

- **URL** : `/` ou `/articles` (en tant qu'auteur d'un article publié avec `has_draft === true`)
- **Vérifications** :
  - Un badge ou icône discret (ex: icône crayon) est visible sur la carte de l'article
  - Le badge n'est PAS visible pour un utilisateur non-auteur
  - Le badge n'est PAS visible pour un visiteur non connecté

---

## 4. Articles — Création et édition

### 4.1 — [AUTH] Création d'un article — Brouillon

- **URL** : `/articles/creer`
- **Action** : Remplir le titre, ajouter du contenu via l'éditeur BlockNote, cliquer "Enregistrer comme brouillon"
- **Vérifications** :
  - Le champ titre est un textarea redimensionnable (max 200 caractères)
  - L'éditeur BlockNote est fonctionnel (saisie de texte, formatage)
  - Clic sur "Enregistrer comme brouillon" sauvegarde l'article
  - Redirection vers la page de l'article après sauvegarde
  - L'article apparaît dans "Mes brouillons" et PAS dans la liste publique

### 4.2 — [AUTH] Création d'un article — Publication directe

- **URL** : `/articles/creer`
- **Action** : Remplir le titre et le contenu, cliquer "Publier"
- **Vérifications** :
  - L'article est publié et visible dans la liste des articles
  - Redirection vers la page de l'article publié
  - La date de publication est définie

### 4.3 — [AUTH] Création d'un article — Validation

- **URL** : `/articles/creer`
- **Actions et vérifications** :
  - Soumission sans titre → message d'erreur ou comportement empêchant la sauvegarde
  - Le titre est limité à 200 caractères

### 4.4 — [AUTH/OWNER] Modification d'un article (brouillon)

- **URL** : `/articles/{slug}/modifier`
- **Action** : Modifier le titre et/ou le contenu, cliquer "Mettre à jour"
- **Vérifications** :
  - Le formulaire est pré-rempli avec le titre et le contenu existants
  - L'éditeur BlockNote charge le contenu existant
  - Après sauvegarde, les modifications sont reflétées sur la page de l'article
  - Le slug peut changer si le titre est modifié

### 4.6 — [AUTH/OWNER] Édition d'un article publié (brouillon continu)

- **URL** : `/articles/{slug}/modifier` (article publié)
- **Action** : Modifier le titre et/ou le contenu d'un article déjà publié
- **Vérifications** :
  - L'éditeur est pré-rempli avec le contenu du brouillon (draft) si un brouillon existe, sinon avec le contenu publié
  - Les modifications sont sauvegardées en tant que brouillon (via autosave), sans modifier le contenu publié visible par les lecteurs
  - La page publique de l'article (`/articles/{slug}`) continue d'afficher le contenu de la dernière publication
  - Un lecteur non-auteur voit toujours le contenu publié, même si un brouillon est en cours

### 4.5 — [AUTH] Éditeur BlockNote — Fonctionnalités

- **URL** : `/articles/creer` ou `/articles/{slug}/modifier`
- **Vérifications** :
  - Saisie de texte basique fonctionne
  - Formatage gras, italique, souligné fonctionne
  - Création de titres (h1, h2, h3) fonctionne
  - Création de listes (à puces, numérotées) fonctionne
  - Le menu de blocs (slash `/`) est accessible

---

## 5. Articles — Suppression

### 5.1 — [AUTH/OWNER] Suppression d'un article

- **URL** : `/articles/{slug}/supprimer`
- **Vérifications** :
  - Une page de confirmation s'affiche avec un avertissement
  - Le titre de l'article à supprimer est mentionné
  - Un bouton "Supprimer" et un bouton/lien "Annuler" sont présents
  - Clic sur "Supprimer" supprime l'article et redirige vers `/`
  - L'article n'apparaît plus dans aucune liste

### 5.2 — [AUTH] Suppression — Non-propriétaire

- **Action** : Accéder à `/articles/{slug}/supprimer` pour un article dont on n'est PAS l'auteur
- **Vérifications** :
  - L'action est refusée (erreur 403 ou redirection)

---

## 6. Brouillons

### 6.1 — [AUTH] Liste des brouillons

- **URL** : `/articles/mes-brouillons`
- **Vérifications** :
  - Seuls les brouillons de l'utilisateur connecté sont affichés
  - Chaque brouillon est affiché sous forme de carte
  - La pagination fonctionne (10 par page)
  - Les articles publiés ne sont PAS dans cette liste

### 6.2 — [AUTH] Accès aux brouillons depuis le menu

- **Action** : Cliquer sur le menu utilisateur → "Mes brouillons"
- **Vérifications** :
  - Redirection vers `/articles/mes-brouillons`
  - La liste des brouillons s'affiche correctement

---

## 7. Commentaires

### 7.1 — [AUTH] Ajout d'un commentaire

- **URL** : `/articles/{slug}` (article publié)
- **Action** : Remplir le formulaire de commentaire et soumettre
- **Vérifications** :
  - Le formulaire de commentaire est visible pour les utilisateurs connectés
  - Après soumission, un message de modération s'affiche ("Votre commentaire est en attente de modération" ou similaire)
  - Le champ de commentaire est vidé après soumission

### 7.2 — [PUBLIC] Formulaire de commentaire — Non connecté

- **URL** : `/articles/{slug}`
- **Vérifications** :
  - Le formulaire de commentaire n'est PAS affiché
  - Un message invite l'utilisateur à se connecter pour commenter

### 7.3 — [PUBLIC] Affichage des commentaires approuvés

- **URL** : `/articles/{slug}` (article avec commentaires approuvés)
- **Vérifications** :
  - Les commentaires approuvés sont affichés avec : auteur, avatar, date, contenu
  - Les commentaires non approuvés ne sont PAS visibles
  - Si plus de 10 commentaires, un bouton "Charger plus" est visible

### 7.4 — [AUTH/OWNER] Suppression d'un commentaire

- **URL** : `/articles/{slug}`
- **Action** : Cliquer sur le bouton de suppression d'un commentaire dont on est l'auteur
- **Vérifications** :
  - Le bouton de suppression n'est visible que pour l'auteur du commentaire
  - Après suppression, le commentaire disparaît de la liste

---

## 8. Profil utilisateur

### 8.1 — [AUTH] Modification du profil

- **URL** : `/comptes/profil/modifier`
- **Action** : Modifier le prénom et/ou le nom de famille, soumettre
- **Vérifications** :
  - Le formulaire affiche les champs : prénom, nom de famille
  - Les champs sont pré-remplis avec les valeurs actuelles
  - Un message de succès s'affiche après la sauvegarde
  - Les modifications sont reflétées dans le header (nom/avatar)

### 8.2 — [AUTH] Upload d'avatar

- **URL** : `/comptes/profil/modifier`
- **Action** : Sélectionner une image JPEG/PNG/WebP < 5MB et soumettre
- **Vérifications** :
  - Le champ d'upload d'avatar est présent
  - L'avatar actuel est affiché si existant
  - Après upload, le nouvel avatar est affiché
  - L'avatar est mis à jour dans le header

### 8.3 — [AUTH] Upload d'avatar — Validation

- **URL** : `/comptes/profil/modifier`
- **Actions et vérifications** :
  - Upload d'un fichier > 5MB → message d'erreur
  - Upload d'un fichier non-image (ex: .txt, .pdf) → message d'erreur
  - Seuls JPEG, PNG et WebP sont acceptés

### 8.4 — [AUTH] Suppression d'avatar

- **URL** : `/comptes/profil/modifier`
- **Action** : Cliquer sur le bouton de suppression d'avatar
- **Vérifications** :
  - Une confirmation est demandée avant suppression
  - Après suppression, l'avatar revient aux initiales par défaut
  - Le header est mis à jour (initiales au lieu de l'image)

---

## 9. Pages statiques

### 9.1 — [PUBLIC] Page "A propos"

- **URL** : `/a-propos`
- **Vérifications** :
  - La page s'affiche correctement
  - Le contenu de présentation est visible

### 9.2 — [PUBLIC] Page "Contact"

- **URL** : `/contact`
- **Vérifications** :
  - La page s'affiche correctement
  - Les liens vers GitHub et LinkedIn sont présents et cliquables

---

## 10. Suivi des développements (Dev Tracking)

### 10.1 — [AUTH] Affichage des issues GitHub

- **URL** : `/suivi-des-devs`
- **Vérifications** :
  - La liste des issues GitHub est affichée
  - Chaque issue affiche : titre et labels avec couleurs
  - La pagination fonctionne (10 par page)

### 10.2 — [AUTH] Gestion des erreurs API GitHub

- **URL** : `/suivi-des-devs` (si API GitHub indisponible)
- **Vérifications** :
  - Un message d'erreur explicite est affiché
  - L'application ne plante pas

---

## 11. Composants UI transversaux

### 11.1 — [PUBLIC] Avatar avec initiales

- **Vérifications** :
  - Les utilisateurs sans avatar affichent leurs initiales
  - Les initiales sont correctes (première lettre prénom + nom)
  - L'avatar est affiché en différentes tailles selon le contexte (sm/md/lg)

### 11.2 — [PUBLIC] Pagination

- **Vérifications** (sur `/articles` ou `/articles/mes-brouillons`) :
  - Les boutons "Précédent" / "Suivant" sont affichés si nécessaire
  - Le bouton "Précédent" est désactivé sur la première page
  - Le bouton "Suivant" est désactivé sur la dernière page
  - Le numéro de page courant est affiché

---

## 12. Historique des versions

### 12.1 — [AUTH/OWNER] Bouton historique des versions visible pour l'auteur

- **URL** : `/articles/{slug}` (article publié par l'utilisateur connecté, ayant au moins une version)
- **Vérifications** :
  - Un bouton ou lien "Historique des versions" est visible
  - Le bouton redirige vers `/articles/{slug}/versions`

### 12.2 — [AUTH] Bouton historique des versions absent pour un non-auteur

- **URL** : `/articles/{slug}` (article publié par un autre utilisateur)
- **Vérifications** :
  - Le bouton "Historique des versions" n'est PAS visible

### 12.3 — [PUBLIC] Bouton historique absent pour un visiteur non connecté

- **URL** : `/articles/{slug}`
- **Vérifications** :
  - Le bouton "Historique des versions" n'est PAS visible

### 12.4 — [AUTH/OWNER] Liste des versions d'un article

- **URL** : `/articles/{slug}/versions`
- **Vérifications** :
  - La liste des versions est affichée
  - Chaque entrée affiche : numéro de version (badge), titre, date de publication
  - Les versions sont triées de la plus récente à la plus ancienne
  - Un lien de retour vers l'article est présent
  - Le clic sur une version redirige vers `/articles/{slug}/versions/{n}`

### 12.5 — [AUTH/OWNER] Détail d'une version (lecture seule)

- **URL** : `/articles/{slug}/versions/{n}`
- **Vérifications** :
  - Le numéro de version, le titre et la date de publication sont affichés
  - Le contenu de la version est affiché en lecture seule (rendu BlockNote)
  - Un bouton "Restaurer cette version" est présent
  - Un lien de retour vers la liste des versions est présent
  - Un lien de retour vers l'article est présent

### 12.7 — [AUTH/OWNER] Restauration d'une version comme brouillon

- **URL** : `/articles/{slug}/versions/{n}`
- **Action** : Cliquer sur le bouton "Restaurer cette version"
- **Vérifications** :
  - Une modale de confirmation s'affiche avec un message indiquant que le brouillon actuel sera remplacé
  - Clic sur "Annuler" ferme la modale sans effet
  - Clic sur "Confirmer" appelle l'API de restauration
  - Après succès, une notification de succès s'affiche
  - Redirection automatique vers `/articles/{slug}/modifier`
  - L'éditeur affiche le contenu de la version restaurée (draft_title et draft_content mis à jour)

### 12.8 — [AUTH] Restauration d'une version — Non-auteur

- **Action** : Un utilisateur non-auteur tente d'accéder à `/articles/{slug}/versions/{n}`
- **Vérifications** :
  - L'accès à la page de version est refusé (403 ou message d'erreur)
  - Le bouton "Restaurer cette version" n'est pas accessible

### 12.6 — [AUTH/OWNER] Protection des routes versions

- **Action** : Accéder à `/articles/{slug}/versions` sans être connecté
- **Vérifications** :
  - Redirection vers `/comptes/connexion`
  - Même comportement pour `/articles/{slug}/versions/{n}`

---

## 13. Scénarios end-to-end (parcours complets)

### 13.1 — Parcours complet : inscription → création article → commentaire

1. Ouvrir `/comptes/inscription`
2. Créer un compte avec `newuser@example.com` / `Testpass123!`
3. Vérifier la redirection vers `/` et l'état connecté
4. Naviguer vers `/articles/creer`
5. Saisir un titre "Mon premier article de test"
6. Ajouter du contenu dans l'éditeur BlockNote
7. Cliquer "Publier"
8. Vérifier que l'article est visible dans la liste
9. Ouvrir l'article
10. Ajouter un commentaire "Super article !"
11. Vérifier le message de modération

### 13.2 — Parcours complet : brouillon → édition → publication

1. Se connecter avec un utilisateur existant
2. Naviguer vers `/articles/creer`
3. Saisir un titre et du contenu
4. Cliquer "Enregistrer comme brouillon"
5. Vérifier dans `/articles/mes-brouillons` que le brouillon apparaît
6. Cliquer sur le brouillon pour l'ouvrir
7. Cliquer sur "Modifier"
8. Modifier le titre et le contenu
9. Cliquer "Mettre à jour"
10. Vérifier que les modifications sont appliquées

### 13.3 — Parcours complet : gestion du profil

1. Se connecter
2. Naviguer vers `/comptes/profil/modifier`
3. Modifier le prénom et le nom
4. Uploader un avatar (image JPEG < 5MB)
5. Sauvegarder
6. Vérifier que le header affiche le nouvel avatar
7. Naviguer vers un article dont on est l'auteur
8. Vérifier que l'avatar est affiché à côté de l'article
9. Retourner sur le profil
10. Supprimer l'avatar
11. Vérifier que les initiales s'affichent à la place

### 13.4 — Parcours complet : permissions inter-utilisateurs

1. Se connecter avec l'utilisateur 1
2. Créer et publier un article
3. Se déconnecter
4. Se connecter avec l'utilisateur 2
5. Ouvrir l'article de l'utilisateur 1
6. Vérifier que les boutons "Modifier" et "Supprimer" sont ABSENTS
7. Vérifier que le formulaire de commentaire est accessible
8. Ajouter un commentaire
9. Vérifier le message de modération

### 13.5 — Parcours complet : publication → historique des versions

1. Se connecter avec l'utilisateur 1
2. Créer un article et le publier (version 1)
3. Modifier l'article (titre et contenu), puis re-publier (version 2)
4. Sur la page de l'article, vérifier que le bouton "Historique des versions" est visible
5. Cliquer sur "Historique des versions"
6. Vérifier que 2 versions sont listées avec les bons numéros et titres
7. Cliquer sur la version 1
8. Vérifier que le contenu original est affiché en lecture seule
9. Naviguer vers la liste des versions via le lien retour
10. Se déconnecter
11. Se connecter avec l'utilisateur 2
12. Ouvrir l'article de l'utilisateur 1
13. Vérifier que le bouton "Historique des versions" est ABSENT

### 13.6 — Parcours complet : publication → restauration de version → re-publication

1. Se connecter avec l'utilisateur 1
2. Créer un article avec titre "Version originale" et du contenu, le publier (version 1)
3. Modifier le titre en "Version modifiée" et le contenu, re-publier (version 2)
4. Vérifier que l'article affiche "Version modifiée"
5. Naviguer vers "Historique des versions"
6. Cliquer sur la version 1
7. Vérifier que le contenu original "Version originale" est affiché
8. Cliquer sur "Restaurer cette version"
9. Confirmer dans la modale
10. Vérifier la notification de succès
11. Vérifier la redirection vers l'éditeur
12. Vérifier que l'éditeur contient le titre "Version originale" et le contenu de la version 1
13. Vérifier que l'article publié affiche toujours "Version modifiée" (non publié automatiquement)

### 13.7 — Parcours complet : re-publication avec indicateur de modifications non publiées

1. Se connecter avec l'utilisateur 1
2. Créer un article avec titre "Article à re-publier" et du contenu, le publier (version 1)
3. Naviguer vers `/articles/{slug}/modifier`
4. Modifier le titre et le contenu (sauvegardé via autosave)
5. Quitter l'éditeur et revenir sur `/articles/{slug}`
6. Vérifier qu'un bandeau "Modifications non publiées" est visible
7. Vérifier qu'un lien "Voir les modifications" est présent dans le bandeau
8. Vérifier qu'un bouton "Publier les modifications" est visible (pas "Publier")
9. Se déconnecter, se connecter avec l'utilisateur 2
10. Ouvrir le même article
11. Vérifier que le bandeau "Modifications non publiées" est ABSENT
12. Vérifier que le bouton "Publier les modifications" est ABSENT
13. Se déconnecter, se connecter avec l'utilisateur 1
14. Ouvrir l'article, cliquer sur "Publier les modifications"
15. Vérifier que le bandeau disparaît après publication
16. Vérifier que le contenu mis à jour est affiché
17. Vérifier dans "Historique des versions" qu'une nouvelle version a été créée
18. Vérifier dans la liste des articles que le badge "brouillon en cours" a disparu

### 13.8 — Parcours complet : édition continue d'un article publié (brouillon continu)

1. Se connecter avec l'utilisateur 1
2. Créer un article avec titre "Article initial" et du contenu, le publier (version 1)
3. Vérifier que l'article est visible dans la liste avec le titre "Article initial"
4. Naviguer vers `/articles/{slug}/modifier`
5. Modifier le titre en "Article en cours d'édition" et le contenu (les changements sont sauvegardés via autosave)
6. Ne PAS publier — quitter l'éditeur
7. Vérifier que la page publique `/articles/{slug}` affiche toujours "Article initial" pour un lecteur
8. Se déconnecter, se connecter avec l'utilisateur 2
9. Vérifier que l'article affiche "Article initial" (contenu publié)
10. Se déconnecter, se connecter avec l'utilisateur 1
11. Naviguer vers `/articles/{slug}/modifier`
12. Vérifier que l'éditeur est pré-rempli avec "Article en cours d'édition" (contenu draft)
13. Publier l'article
14. Vérifier que l'article affiche maintenant "Article en cours d'édition" (version 2)
15. Naviguer vers "Historique des versions"
16. Vérifier que 2 versions sont listées
