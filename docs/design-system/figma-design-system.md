# Design System Figma — NICKORP Blog

Guide complet pour construire le design system Figma de l'application blog NICKORP.

---

## 1. Design Tokens

### 1.1 Couleurs

#### Palette principale

| Token | Hex | Usage |
|-------|-----|-------|
| `black` | `#000000` | Boutons primaires, titres principaux |
| `white` | `#FFFFFF` | Fonds de page, texte sur boutons noirs |

#### Palette de gris (Tailwind defaults)

| Token | Hex | Usage |
|-------|-----|-------|
| `gray-50` | `#F9FAFB` | Fonds très légers |
| `gray-100` | `#F3F4F6` | Fonds légers, hover |
| `gray-200` | `#E5E7EB` | Bordures, séparateurs |
| `gray-300` | `#D1D5DB` | Fonds avatars fallback |
| `gray-400` | `#9CA3AF` | Icônes inactives, texte très léger |
| `gray-500` | `#6B7280` | Texte secondaire, timestamps |
| `gray-600` | `#4B5563` | Texte corps secondaire |
| `gray-700` | `#374151` | Labels formulaires, texte corps |
| `gray-800` | `#1F2937` | Titres secondaires, hover bouton primaire |
| `gray-900` | `#111827` | Texte principal, titres |

#### Couleurs sémantiques

| Token | Background | Text | Border | Usage |
|-------|-----------|------|--------|-------|
| `success` | `#F0FDF4` | `#166534` | `#BBF7D0` | Messages de succès |
| `success-badge` | `#DCFCE7` | `#166534` | — | Badge "Publié" |
| `warning` | `#FEFCE8` | `#854D0E` | `#FEF08A` | Messages d'alerte |
| `warning-badge` | `#FEF9C3` | `#854D0E` | — | Badge "Brouillon" |
| `danger` | `#FEF2F2` | `#991B1B` | `#FECACA` | Messages d'erreur |
| `info-badge` | `#DBEAFE` | `#1E40AF` | — | Badge "Brouillon non publié" |
| `link` | — | `#2563EB` | — | Liens texte |
| `link-hover` | — | `#1E40AF` | — | Liens hover |

---

### 1.2 Typographie

#### Police : Inter

| Style | Weight | Taille | Line Height | Usage |
|-------|--------|--------|-------------|-------|
| **Display** | Bold (700) | 36px (`text-4xl`) | 40px | Titre page d'accueil |
| **H1** | Bold (700) | 30px (`text-3xl`) | 36px | Titres de page |
| **H2** | SemiBold (600) | 24px (`text-2xl`) | 32px | Sous-titres de section |
| **H3** | SemiBold (600) | 20px (`text-xl`) | 28px | Titres d'articles (listes) |
| **Body** | Regular (400) | 16px (`text-base`) | 24px (`leading-relaxed`) | Texte courant |
| **Body Small** | Regular (400) | 14px (`text-sm`) | 20px | Texte secondaire |
| **Label** | Medium (500) | 14px (`text-sm`) | 20px | Labels de formulaires |
| **Caption** | Medium (500) | 12px (`text-xs`) | 16px | Badges, metadata |

---

### 1.3 Espacement

Basé sur l'échelle Tailwind (multiples de 4px) :

| Token | Valeur | Usage principal |
|-------|--------|----------------|
| `space-0.5` | 2px | Padding interne badges (py) |
| `space-1` | 4px | Marges très fines, gap labels |
| `space-2` | 8px | Gap petits composants, padding badges (px) |
| `space-3` | 12px | Gap moyen, padding alertes |
| `space-4` | 16px | Padding horizontal pages (px), gap moyen |
| `space-6` | 24px | Gap sections, marges entre éléments |
| `space-8` | 32px | Marges entre sections |
| `space-12` | 48px | Padding vertical pages (py) |
| `space-16` | 64px | Grand padding vertical |

---

### 1.4 Rayons de bordure

| Token | Valeur | Usage |
|-------|--------|-------|
| `rounded` | 4px | Boutons, inputs |
| `rounded-md` | 6px | Alertes, cartes |
| `rounded-full` | 9999px | Avatars, badges |

---

### 1.5 Ombres

| Token | Valeur | Usage |
|-------|--------|-------|
| `shadow-lg` | `0 10px 15px -3px rgba(0,0,0,0.1)` | Menu dropdown |

---

### 1.6 Transitions

| Propriété | Durée | Easing |
|-----------|-------|--------|
| Couleurs | 150ms | ease-in-out |

---

## 2. Composants

### 2.1 Boutons

#### Bouton Primaire (`.btn-primary`)
- **Fond** : `black`
- **Texte** : `white`, 14px, Medium
- **Padding** : 8px 16px
- **Border radius** : 4px
- **Hover** : fond `gray-800`
- **Variante full-width** : width 100%, padding 12px 16px

#### Bouton Secondaire (`.btn-secondary`)
- **Fond** : `white`
- **Texte** : `gray-700`, 14px, Medium
- **Bordure** : 1px `gray-300`
- **Padding** : 8px 16px
- **Border radius** : 4px
- **Hover** : fond `gray-50`

#### Bouton Danger (`.btn-danger`)
- **Fond** : `white`
- **Texte** : `gray-500`, 14px, Medium
- **Bordure** : 1px `gray-300`
- **Padding** : 8px 16px
- **Border radius** : 4px
- **Hover** : texte `gray-900`, fond `gray-50`

#### Bouton Icône
- **Taille icône** : 20x20px
- **Couleur** : `gray-400`
- **Hover** : `black`
- **Pas de padding** supplémentaire

**States Figma** : Default, Hover, Focus (ring 2px black offset 2px), Disabled (opacity 50%)

---

### 2.2 Champs de formulaire

#### Input Texte (`.form-input`)
- **Largeur** : 100%
- **Padding** : 8px 12px
- **Bordure** : 1px `gray-300`
- **Border radius** : 4px
- **Texte** : 14px, Regular, `gray-900`
- **Placeholder** : `gray-400`
- **Focus** : bordure `black`, ring 1px `black`
- **Erreur** : bordure `red-500`

#### Label (`.form-label`)
- **Texte** : 14px, Medium, `gray-700`
- **Marge bas** : 4px

#### Message d'erreur (`.form-error`)
- **Texte** : 14px, Regular, `red-600`
- **Marge haut** : 4px

#### Textarea
- Mêmes styles que Input Texte
- **Hauteur min** : 120px
- Auto-resize possible

---

### 2.3 Badges de statut

#### Badge Publié
- **Fond** : `#DCFCE7` (green-100)
- **Texte** : `#166534` (green-800), 12px, Medium
- **Padding** : 2px 8px
- **Border radius** : full

#### Badge Brouillon
- **Fond** : `#FEF9C3` (yellow-100)
- **Texte** : `#854D0E` (yellow-800), 12px, Medium
- **Padding** : 2px 8px
- **Border radius** : full

#### Badge Info
- **Fond** : `#DBEAFE` (blue-100)
- **Texte** : `#1E40AF` (blue-800), 12px, Medium
- **Padding** : 2px 8px
- **Border radius** : full

---

### 2.4 Alertes / Messages

Structure commune :
- **Padding** : 12px ou 16px
- **Border radius** : 6px
- **Bordure** : 1px
- **Texte** : 14px

| Variante | Fond | Bordure | Texte |
|----------|------|---------|-------|
| Success | `#F0FDF4` | `#BBF7D0` | `#166534` |
| Error | `#FEF2F2` | `#FECACA` | `#991B1B` |
| Warning | `#FEFCE8` | `#FEF08A` | `#854D0E` |

---

### 2.5 Avatar

#### Avec image
- **Forme** : Cercle
- **Tailles** : 24x24px (liste), 32x32px (detail)
- **Object-fit** : cover

#### Fallback (initiales)
- **Fond** : `gray-300`
- **Texte** : `white`, 12px (petit) / 14px (grand), SemiBold
- **Forme** : Cercle
- Affiche la première lettre du nom/email

---

### 2.6 Carte Article

- **Padding** : 24px vertical
- **Bordure bas** : 1px `gray-200`
- **Pas de fond distinct** (transparent)

Contenu :
1. **Titre** : 20px, SemiBold, `gray-900`, lien hover underline
2. **Info auteur** : Avatar 24px + Nom 14px `gray-700` + Date 14px `gray-500`
3. **Extrait** : 16px, Regular, `gray-600`, tronqué ~50 mots
4. **Actions** (si propriétaire) : Icônes edit/delete alignées à droite

---

### 2.7 Section Commentaires

#### Commentaire individuel
- **Séparateur** : 1px `gray-100` entre les commentaires
- **Padding** : 16px vertical
- **Layout** : Avatar 32px + contenu (nom, date, texte)
- **Bouton supprimer** : Icône X, `gray-400` hover `gray-900`

#### Formulaire commentaire
- Textarea + bouton primaire "Publier"
- Message de modération : texte `gray-500` 14px

---

### 2.8 Dropdown Menu (Avatar)

- **Position** : Ancré en haut à droite
- **Largeur** : 192px
- **Fond** : `white`
- **Bordure** : 1px `gray-200`
- **Border radius** : 4px
- **Ombre** : `shadow-lg`
- **Padding** : 4px vertical

Items :
- **Padding** : 8px 16px
- **Texte** : 14px, Regular, `gray-700`
- **Hover** : fond `gray-50`
- **Séparateur** : 1px `gray-100` avant le logout

---

### 2.9 Pagination

- **Layout** : Flex, justify-between, align-center
- **Liens** : 14px, `gray-500`, hover `black`
- **Indicateur page** : 14px, `gray-500` (texte statique "Page X sur Y")

---

### 2.10 Navigation Links

- **Texte** : 14px, Regular
- **Couleur** : `gray-500`
- **Hover** : `black`
- **Transition** : 150ms couleur

---

## 3. Layouts (Frames Figma)

### 3.1 Breakpoints

| Nom | Largeur | Usage |
|-----|---------|-------|
| Mobile | 375px | Layout par défaut |
| Tablet | 768px (md) | Navigation desktop visible |
| Desktop | 1440px | Max width atteint |

### 3.2 Header

**Desktop (md+)** :
- **Hauteur** : auto (padding 16px vertical)
- **Bordure bas** : 1px `gray-200`
- **Layout** : Flex, space-between
  - Gauche : Logo "NICKORP" (16px, Bold, `gray-900`)
  - Centre : Nav links (Articles, A propos, Contact)
  - Droite :
    - Non connecté : Bouton secondaire "Se connecter" + Bouton primaire "Créer un compte"
    - Connecté : Bouton primaire "Ajouter un article" + Avatar dropdown

**Mobile** :
- Logo gauche + Hamburger droite
- Menu déroulant pleine largeur avec liens + auth

### 3.3 Zone de contenu

| Page | Max-width | Usage |
|------|-----------|-------|
| Articles (liste), Détail, Accueil | 768px (`max-w-3xl`) | Contenu principal |
| Formulaires (article, profil) | 672px (`max-w-2xl`) | Formulaires d'édition |
| Auth (login, signup) | 384px (`max-w-sm`) | Formulaires d'authentification |

- **Padding horizontal** : 16px
- **Centrage** : auto margins

### 3.4 Footer

- **Bordure haut** : 1px `gray-200`
- **Padding** : 32px vertical
- **Texte** : 14px, `gray-500`, centré
- Contient : Copyright + lien optionnel "Suivi des devs"

---

## 4. Pages à maquetter

### 4.1 Pages publiques
1. **Accueil** — Hero avec derniers articles, CTA "Voir tous les articles"
2. **Liste des articles** — Cards articles paginés (10/page)
3. **Détail article** — Titre, auteur, contenu riche, section commentaires
4. **A propos** — Page statique avec texte
5. **Contact** — Liens sociaux et informations

### 4.2 Pages authentification
6. **Connexion** — Formulaire email/mot de passe
7. **Inscription** — Formulaire nom/email/mot de passe

### 4.3 Pages utilisateur connecté
8. **Mes articles** — Liste avec badges statut, actions edit/delete
9. **Créer/Modifier un article** — Formulaire titre, catégorie, tags, éditeur BlockNote
10. **Modifier mon profil** — Formulaire nom, avatar
11. **Confirmation de suppression** — Message + boutons confirmer/annuler

### 4.4 Page utilitaire
12. **Coming Soon** — Page placeholder

---

## 5. Structure Figma recommandée

```
NICKORP Design System
├── 📄 Cover
├── 🎨 Tokens
│   ├── Colors
│   ├── Typography
│   ├── Spacing
│   ├── Border Radius
│   └── Shadows
├── 🧩 Components
│   ├── Buttons (Primary, Secondary, Danger, Icon)
│   ├── Inputs (Text, Textarea, Select, File)
│   ├── Badges (Published, Draft, Info)
│   ├── Alerts (Success, Error, Warning)
│   ├── Avatar (Image, Fallback) × 2 tailles
│   ├── Card Article
│   ├── Comment
│   ├── Dropdown Menu
│   ├── Pagination
│   └── Navigation Link
├── 📐 Patterns
│   ├── Header (Desktop + Mobile) × (Logged in, Logged out)
│   ├── Footer
│   ├── Form Group (Label + Input + Error)
│   ├── Article List
│   └── Comment Section
└── 📱 Pages (Mobile + Desktop)
    ├── Home
    ├── Post List
    ├── Post Detail
    ├── Post Form (Create/Edit)
    ├── My Posts
    ├── Login
    ├── Signup
    ├── Profile Edit
    ├── About
    ├── Contact
    ├── Delete Confirmation
    └── Coming Soon
```

---

## 6. Icônes

Jeu d'icônes : **Heroicons** (outline style)

Icônes utilisées dans l'app :
- `pencil` — Modifier un article
- `trash` — Supprimer
- `x-mark` — Fermer menu / Supprimer commentaire
- `bars-3` — Menu hamburger
- `user` — Avatar fallback (optionnel)

Tailles : 20x20px (standard), 16x16px (petit contexte)
Couleur par défaut : `gray-400`, hover : `black`

---

## 7. Notes pour l'implémentation Figma

1. **Variables Figma** : Créer des variables pour toutes les couleurs et espacements (Section Tokens)
2. **Auto Layout** : Utiliser systématiquement l'auto layout pour tous les composants
3. **Composants avec variantes** : Chaque composant doit avoir ses variantes (state, size, type)
4. **Responsive** : Utiliser les contraintes et min/max width pour le responsive
5. **Nommage** : Suivre la convention `Category/Component/Variant` (ex: `Button/Primary/Default`)
6. **Text styles** : Créer un style de texte pour chaque entrée de la section Typographie
7. **Mode sombre** : Non implémenté actuellement — design light uniquement
