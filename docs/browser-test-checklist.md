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
  - Les liens "Accueil", "Articles", "Contact" sont visibles
  - Les boutons "Connexion" et "Inscription" sont visibles (utilisateur non connecté)

### 1.2 — [AUTH] Header utilisateur connecté

- **Action** : Se connecter puis vérifier le header
- **Vérifications** :
  - Le bouton "Connexion" / "Inscription" disparaît
  - Le nom d'utilisateur ou avatar apparaît dans le header
  - Un bouton "Ajouter un article" est visible **uniquement pour les superutilisateurs**
  - Un menu déroulant utilisateur est accessible (clic sur le nom/avatar)
  - Le menu contient : "Modifier profil", "Déconnexion"
  - Le menu contient "Mes brouillons" **uniquement pour les superutilisateurs**

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
  - Même comportement pour `/comptes/profil/modifier`

### 2.7 — [AUTH] Protection des routes superutilisateur

- **Action** : Se connecter avec un utilisateur non-superutilisateur et accéder à `/articles/creer`
- **Vérifications** :
  - L'accès est refusé (redirection ou message d'erreur 403)
  - Même comportement pour `/articles/{slug}/modifier`, `/articles/{slug}/supprimer` et `/articles/mes-brouillons`

---

## 3. Articles — Liste et consultation

### 3.1 — [PUBLIC] Page d'accueil — Liste des articles

- **URL** : `/`
- **Vérifications** :
  - Les articles publiés sont affichés sous forme de cartes
  - Maximum 10 articles affichés
  - Chaque carte affiche : titre, auteur (nom + avatar), date, extrait du contenu, les tags de l'article (s'il en a), et l'image de couverture en miniature (si définie)
  - L'image de couverture est correctement alignée avec le contenu de la carte (pas de décalage horizontal)
  - Les tags sont affichés en dessous du titre de chaque carte
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
  - L'image de couverture est affichée en grand au-dessus du contenu (si définie)
  - Les tags de l'article sont affichés en dessous du titre (s'il en a)
  - Le contenu riche (BlockNote) est rendu correctement en HTML
  - L'auteur est affiché avec son avatar et son nom
  - La date de publication est affichée
  - En desktop (≥ 1024px), les commentaires sont affichés dans une colonne à droite de l'article
  - En mobile (< 1024px), les commentaires sont affichés sous l'article

### 3.4 — [AUTH/OWNER] Boutons d'action sur un article

- **URL** : `/articles/{slug}` (en tant qu'auteur superutilisateur de l'article)
- **Vérifications** :
  - Les boutons "Modifier" et "Supprimer" sont visibles uniquement si l'utilisateur est **superutilisateur ET auteur**
  - Les boutons d'action sont positionnés **en dessous du titre**, pas à sa droite
  - Tous les boutons ont un style visuel harmonisé (bordure, padding et taille de texte cohérents)
  - Clic sur "Modifier" redirige vers `/articles/{slug}/modifier`
  - Clic sur "Supprimer" redirige vers `/articles/{slug}/supprimer`
  - Ces boutons sont ABSENTS si l'utilisateur n'est pas superutilisateur
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
  - Un badge "Brouillon en cours" est visible **en dessous du titre** de la carte de l'article (pas à côté du titre)
  - Le badge n'est PAS visible pour un utilisateur non-auteur
  - Le badge n'est PAS visible pour un visiteur non connecté

### 3.8 — [AUTH/OWNER] Dropdown d'actions dans les listes d'articles

- **URL** : `/` ou `/articles` (en tant qu'auteur superutilisateur d'un article)
- **Vérifications** :
  - Un bouton "..." (trois points) est visible à droite du titre de la carte
  - Le bouton "..." n'est PAS visible pour un utilisateur non-auteur ou non-superutilisateur
  - Clic sur "..." ouvre un dropdown (menu déroulant) contenant les actions "Modifier" et "Supprimer"
  - Clic sur "Modifier" dans le dropdown redirige vers `/articles/{slug}/modifier`
  - Clic sur "Supprimer" dans le dropdown redirige vers `/articles/{slug}/supprimer`
  - Le dropdown se ferme correctement au clic extérieur ou après sélection d'une action

---

## 4. Articles — Création et édition

### 4.1 — [AUTH/SUPERUSER] Création d'un article — Brouillon

- **URL** : `/articles/creer` (accessible uniquement aux superutilisateurs)
- **Action** : Remplir le titre, ajouter du contenu via l'éditeur BlockNote, cliquer "Enregistrer comme brouillon"
- **Vérifications** :
  - Le champ titre est un textarea redimensionnable (max 200 caractères)
  - L'éditeur BlockNote est fonctionnel (saisie de texte, formatage)
  - Clic sur "Enregistrer comme brouillon" sauvegarde l'article
  - Redirection vers la page de l'article après sauvegarde
  - L'article apparaît dans "Mes brouillons" et PAS dans la liste publique

### 4.2 — [AUTH/SUPERUSER] Création d'un article — Publication directe

- **URL** : `/articles/creer` (accessible uniquement aux superutilisateurs)
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

### 4.4 — [AUTH/OWNER] Modification d'un article (brouillon) avec autosave

- **URL** : `/articles/{slug}/modifier`
- **Action** : Modifier le titre et/ou le contenu, attendre l'autosave
- **Vérifications** :
  - Le formulaire est pré-rempli avec le titre et le contenu existants
  - L'éditeur BlockNote charge le contenu existant
  - Après modification, l'autosave se déclenche automatiquement (indicateur "Sauvegarde en cours..." puis "Brouillon sauvegardé")
  - Le bouton "Modifier" n'est PAS affiché (remplacé par l'autosave)
  - Les modifications sont sauvegardées en tant que brouillon via l'endpoint `/autosave/`

### 4.6 — [AUTH/OWNER] Édition d'un article publié (brouillon continu) avec autosave

- **URL** : `/articles/{slug}/modifier` (article publié)
- **Action** : Modifier le titre et/ou le contenu d'un article déjà publié
- **Vérifications** :
  - L'éditeur est pré-rempli avec le contenu du brouillon (draft) si un brouillon existe, sinon avec le contenu publié
  - Les modifications sont sauvegardées automatiquement en tant que brouillon via l'endpoint `/autosave/` (pas le PATCH classique)
  - L'indicateur de sauvegarde affiche "Sauvegarde en cours..." puis "Brouillon sauvegardé à HH:MM"
  - Le bouton "Modifier" n'est PAS affiché (remplacé par l'autosave)
  - La page publique de l'article (`/articles/{slug}`) continue d'afficher le contenu de la dernière publication
  - Un lecteur non-auteur voit toujours le contenu publié, même si un brouillon est en cours

### 4.7 — [AUTH] Autosave — Indicateur de statut

- **URL** : `/articles/{slug}/modifier`
- **Action** : Modifier le titre ou le contenu et observer l'indicateur
- **Vérifications** :
  - Un indicateur discret est visible entre le titre et l'éditeur
  - Pendant la sauvegarde : affiche "Sauvegarde en cours..." (ou icône de chargement)
  - Après succès : affiche "Brouillon sauvegardé" avec horodatage (ex: "Brouillon sauvegardé à 14:32")
  - En cas d'erreur : affiche "Erreur de sauvegarde"

### 4.8 — [AUTH] Autosave — Debounce (délai avant sauvegarde)

- **URL** : `/articles/{slug}/modifier`
- **Action** : Taper du texte en continu dans le titre ou l'éditeur
- **Vérifications** :
  - L'autosave ne se déclenche PAS à chaque frappe
  - L'autosave se déclenche environ 1 à 2 secondes après la dernière modification
  - L'indicateur passe à "Sauvegarde en cours..." seulement après le délai

### 4.9 — [AUTH] Autosave — Nouveau article (première sauvegarde manuelle)

- **URL** : `/articles/creer`
- **Action** : Saisir un titre et du contenu, cliquer "Enregistrer en brouillon"
- **Vérifications** :
  - Avant la première sauvegarde, aucun autosave ne se déclenche (pas de slug disponible)
  - Après clic sur "Enregistrer en brouillon", l'article est créé
  - L'utilisateur est redirigé vers la page d'édition de l'article
  - L'autosave est alors actif pour les modifications suivantes

### 4.10 — [AUTH] Autosave — Protection contre la perte de données

- **URL** : `/articles/{slug}/modifier`
- **Action** : Modifier du contenu puis tenter de quitter la page avant que l'autosave ne se déclenche
- **Vérifications** :
  - Le navigateur affiche un avertissement de confirmation avant de quitter (dialogue `beforeunload`)
  - Si l'utilisateur annule, il reste sur la page et l'autosave se termine normalement

### 4.17 — [AUTH/SUPERUSER] Ajout d'une image de couverture à un article

- **URL** : `/articles/creer` ou `/articles/{slug}/modifier`
- **Action** : Cliquer sur la zone d'upload d'image de couverture et sélectionner une image JPEG/PNG/WebP < 10 Mo
- **Vérifications** :
  - Une zone d'upload d'image de couverture est visible au-dessus du titre
  - Après sélection de l'image, un aperçu de l'image est affiché dans la zone
  - L'image de couverture est sauvegardée avec l'article (brouillon ou publication)
  - Après rechargement de la page d'édition, l'image de couverture est toujours affichée
  - Un bouton de suppression permet de retirer l'image de couverture

### 4.18 — [AUTH/SUPERUSER] Image de couverture — Validation

- **URL** : `/articles/creer` ou `/articles/{slug}/modifier`
- **Actions et vérifications** :
  - Upload d'un fichier non-image (ex: .txt, .pdf) → message d'erreur affiché
  - Upload d'un fichier > 10 Mo → message d'erreur affiché
  - Les formats JPEG, PNG, WebP et GIF sont acceptés

### 4.19 — [AUTH/SUPERUSER] Image de couverture — Suppression

- **URL** : `/articles/{slug}/modifier` (article avec une image de couverture)
- **Action** : Cliquer sur le bouton de suppression de l'image de couverture
- **Vérifications** :
  - L'image de couverture disparaît de la zone d'upload
  - Après sauvegarde/autosave, l'image de couverture n'est plus associée à l'article
  - La carte de l'article dans les listes n'affiche plus de miniature

### 4.5 — [AUTH] Éditeur BlockNote — Fonctionnalités

- **URL** : `/articles/creer` ou `/articles/{slug}/modifier`
- **Vérifications** :
  - Saisie de texte basique fonctionne
  - Formatage gras, italique, souligné fonctionne
  - Création de titres (h1, h2, h3) fonctionne
  - Création de listes (à puces, numérotées) fonctionne
  - Le menu de blocs (slash `/`) est accessible
  - Aucune bordure bleue (outline) n'apparaît autour de la zone de saisie lorsqu'on clique ou saisit du texte (vérifier sur Firefox notamment)

### 4.11 — [AUTH/SUPERUSER] Upload d'image dans l'éditeur BlockNote

- **URL** : `/articles/creer` ou `/articles/{slug}/modifier`
- **Action** : Insérer une image dans l'éditeur (via le menu slash `/` → Image, ou via copier-coller d'une image)
- **Vérifications** :
  - L'image s'affiche correctement dans l'éditeur après upload
  - L'image est toujours visible après sauvegarde (autosave) et rechargement de la page
  - L'image est servie depuis le serveur (URL commençant par `/media/blog/images/`)
  - Pas de carré avec point d'interrogation ni d'icône d'image cassée

### 4.12 — [AUTH/SUPERUSER] Upload d'image — Validation

- **URL** : `/articles/creer` ou `/articles/{slug}/modifier`
- **Actions et vérifications** :
  - Upload d'un fichier non-image (ex: .txt, .pdf) → l'image n'est pas insérée ou un message d'erreur s'affiche
  - Upload d'un fichier > 5 Mo → l'image n'est pas insérée ou un message d'erreur s'affiche
  - Les formats JPEG, PNG, WebP et GIF sont acceptés

### 4.15 — [AUTH/SUPERUSER] Upload de vidéo dans l'éditeur BlockNote

- **URL** : `/articles/creer` ou `/articles/{slug}/modifier`
- **Action** : Insérer une vidéo dans l'éditeur (via le menu slash `/` → Video, ou via le bouton d'ajout de bloc)
- **Vérifications** :
  - La vidéo s'affiche correctement dans l'éditeur après upload
  - La vidéo est toujours visible après sauvegarde (autosave) et rechargement de la page
  - La vidéo est servie depuis le serveur (URL commençant par `/media/blog/videos/`)
  - Le lecteur vidéo est fonctionnel (lecture, pause)

### 4.16 — [AUTH/SUPERUSER] Upload de vidéo — Validation

- **URL** : `/articles/creer` ou `/articles/{slug}/modifier`
- **Actions et vérifications** :
  - Upload d'un fichier vidéo MP4 valide (< 50 Mo) → la vidéo est insérée avec succès
  - Upload d'un fichier vidéo WebM valide → la vidéo est insérée avec succès
  - Upload d'un fichier au format non autorisé (ex: .avi, .mov) → une notification d'erreur s'affiche avec le message précisant le format (ex: « Format non autorisé. Utilisez MP4, WebM ou OGG. »)
  - Upload d'un fichier > 50 Mo → une notification d'erreur s'affiche avec le message précisant la taille (ex: « La taille de la vidéo ne doit pas dépasser 50 Mo. »)
  - Les formats MP4, WebM et OGG sont acceptés

---

### 4.13 — [AUTH/SUPERUSER] Ajout de tags à un article

- **URL** : `/articles/creer` ou `/articles/{slug}/modifier`
- **Action** : Utiliser le champ TagsInput pour ajouter des tags à l'article
- **Vérifications** :
  - Un champ de saisie de tags (TagsInput Mantine) est visible dans le formulaire
  - L'utilisateur peut taper un nouveau tag et l'ajouter (touche Entrée ou virgule)
  - Lors de la saisie, les tags existants correspondants sont proposés en autocomplétion (5 maximum)
  - L'autocomplétion filtre les tags contenant la chaîne saisie
  - Les tags ajoutés sont affichés comme des badges dans le champ
  - L'utilisateur peut supprimer un tag en cliquant sur la croix du badge
  - Après sauvegarde (brouillon ou publication), les tags sont persistés
  - En édition, les tags existants de l'article sont pré-remplis dans le champ

### 4.14 — [AUTH/SUPERUSER] Tags — Autocomplétion avec tags existants

- **URL** : `/articles/creer`
- **Action** : Créer un article avec des tags, puis créer un nouvel article et taper un tag existant
- **Vérifications** :
  - Les tags créés précédemment apparaissent dans les suggestions d'autocomplétion
  - Maximum 5 suggestions sont affichées
  - Les suggestions se mettent à jour au fur et à mesure de la saisie

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

### 6.1 — [AUTH/SUPERUSER] Liste des brouillons

- **URL** : `/articles/mes-brouillons` (accessible uniquement aux superutilisateurs)
- **Vérifications** :
  - Seuls les brouillons du superutilisateur connecté sont affichés
  - Chaque brouillon est affiché sous forme de carte
  - La pagination fonctionne (10 par page)
  - Les articles publiés ne sont PAS dans cette liste

### 6.2 — [AUTH/SUPERUSER] Accès aux brouillons depuis le menu

- **Action** : Se connecter en tant que superutilisateur, cliquer sur le menu utilisateur → "Mes brouillons"
- **Vérifications** :
  - Le lien "Mes brouillons" est visible dans le menu
  - Redirection vers `/articles/mes-brouillons`
  - La liste des brouillons s'affiche correctement

### 6.3 — [AUTH] Brouillons inaccessibles pour un utilisateur non-superutilisateur

- **Action** : Se connecter avec un utilisateur non-superutilisateur
- **Vérifications** :
  - Le lien "Mes brouillons" est ABSENT du menu utilisateur (desktop et mobile)
  - L'accès direct à `/articles/mes-brouillons` redirige vers `/` (accès refusé)

### 6.4 — [AUTH/OWNER] Affichage du détail d'un brouillon non publié

- **URL** : `/articles/{slug}` (article en statut "draft", jamais publié, en tant qu'auteur)
- **Vérifications** :
  - Le titre du brouillon est affiché correctement
  - Le contenu du brouillon est affiché correctement (rendu BlockNote non vide)
  - Les boutons d'action (Modifier, Supprimer) sont visibles pour l'auteur superutilisateur
  - La zone de commentaires (formulaire + liste) n'est PAS affichée

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

### 7.3 — [PUBLIC] Affichage des commentaires approuvés (composant Mantine)

- **URL** : `/articles/{slug}` (article avec commentaires approuvés)
- **Vérifications** :
  - Les commentaires approuvés sont affichés avec le composant Mantine comment-simple : avatar rond (Mantine Avatar), nom de l'auteur, date, contenu
  - Chaque commentaire affiche l'avatar de l'auteur (image ou initiales) via le composant Mantine Avatar
  - Le nom de l'auteur et la date sont affichés sur la même ligne (Mantine Group)
  - Le contenu du commentaire est affiché sous le nom/date avec un retrait à gauche
  - Les commentaires non approuvés ne sont PAS visibles
  - Si plus de 10 commentaires, un bouton "Charger plus" est visible

### 7.5 — [PUBLIC] Layout commentaires desktop vs mobile

- **URL** : `/articles/{slug}` (article avec commentaires)
- **Vérifications** :
  - En desktop (≥ 1024px) : les commentaires et le formulaire sont affichés dans une colonne à droite de l'article
  - En mobile (< 1024px) : les commentaires et le formulaire sont affichés sous l'article (layout vertical)
  - Le formulaire de commentaire est positionné au-dessus de la liste des commentaires dans la colonne de droite (desktop)

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
  - Le formulaire affiche les champs : prénom, nom de famille, email
  - Les champs sont pré-remplis avec les valeurs actuelles
  - Un message de succès s'affiche après la sauvegarde
  - Les modifications sont reflétées dans le header (nom/avatar)

### 8.5 — [AUTH] Modification de l'email

- **URL** : `/comptes/profil/modifier`
- **Action** : Modifier l'adresse email avec une adresse valide, soumettre
- **Vérifications** :
  - Le champ email est pré-rempli avec l'adresse actuelle
  - Après modification, un message de succès s'affiche
  - Le champ email affiche la nouvelle adresse après rechargement

### 8.6 — [AUTH] Modification de l'email — Validation

- **URL** : `/comptes/profil/modifier`
- **Actions et vérifications** :
  - Email invalide (format incorrect) → message d'erreur affiché
  - Email déjà utilisé par un autre utilisateur → message d'erreur affiché

### 8.2 — [AUTH] Upload d'avatar

- **URL** : `/comptes/profil/modifier`
- **Action** : Sélectionner une image JPEG/PNG/WebP < 5MB et soumettre
- **Vérifications** :
  - Le champ d'upload d'avatar est présent
  - L'avatar actuel est affiché si existant
  - Après upload, le nouvel avatar est affiché
  - L'avatar est mis à jour dans le header

### 8.2b — [AUTH] Upload d'avatar — Compression automatique

- **URL** : `/comptes/profil/modifier`
- **Action** : Uploader une image large (ex: 2000×2000 JPEG ou PNG) et soumettre
- **Vérifications** :
  - L'avatar est affiché correctement après upload (pas de distorsion)
  - L'image servie par le serveur est en format JPEG (vérifier l'URL ou le Content-Type)
  - L'image servie ne dépasse pas 300×300 pixels (vérifiable via les dimensions naturelles de l'image dans le DOM)

### 8.3 — [AUTH] Upload d'avatar — Validation

- **URL** : `/comptes/profil/modifier`
- **Actions et vérifications** :
  - Upload d'un fichier > 5MB → message d'erreur
  - Upload d'un fichier non-image (ex: .txt, .pdf) → message d'erreur
  - Seuls JPEG, PNG et WebP sont acceptés

### 8.4 — [AUTH] Suppression d'avatar

- **URL** : `/comptes/profil/modifier`
- **Pré-requis** : L'utilisateur a un avatar uploadé (cf. test 8.2)
- **Action** : Cliquer sur le bouton « Supprimer l'avatar »
- **Vérifications** :
  - Des boutons de confirmation inline apparaissent (« Confirmer la suppression » et « Annuler »)
  - Clic sur « Annuler » masque les boutons de confirmation et revient à l'état initial
  - Clic sur « Confirmer la suppression » supprime l'avatar
  - Après suppression, l'avatar revient aux initiales par défaut
  - Le header est mis à jour (initiales au lieu de l'image)
  - Un message de succès s'affiche

---

## 9. Pages statiques

### 9.1 — [PUBLIC] Page "Contact"

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

### 13.2 — Parcours complet : brouillon → édition avec autosave → publication

1. Se connecter avec un utilisateur existant
2. Naviguer vers `/articles/creer`
3. Saisir un titre et du contenu
4. Cliquer "Enregistrer en brouillon"
5. Vérifier dans `/articles/mes-brouillons` que le brouillon apparaît
6. Cliquer sur le brouillon pour l'ouvrir
7. Cliquer sur "Modifier"
8. Modifier le titre et le contenu
9. Attendre que l'indicateur affiche "Brouillon sauvegardé"
10. Vérifier que les modifications sont sauvegardées automatiquement (pas de bouton "Modifier"/"Mettre à jour")

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

### 13.4 — Parcours complet : permissions inter-utilisateurs (superutilisateur vs utilisateur normal)

1. Se connecter avec un superutilisateur
2. Créer et publier un article
3. Se déconnecter
4. Se connecter avec un utilisateur non-superutilisateur
5. Ouvrir l'article du superutilisateur
6. Vérifier que les boutons "Modifier" et "Supprimer" sont ABSENTS
7. Vérifier que le bouton "Ajouter un article" est ABSENT dans le header
8. Accéder directement à `/articles/creer` → vérifier que l'accès est refusé
9. Vérifier que le formulaire de commentaire est accessible
10. Ajouter un commentaire
11. Vérifier le message de modération

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
