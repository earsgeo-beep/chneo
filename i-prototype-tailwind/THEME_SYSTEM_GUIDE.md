# Guide du Système de Thèmes CHNeoWave

## Vue d'ensemble

Le système de thèmes CHNeoWave a été entièrement corrigé pour assurer une application uniforme des couleurs et styles sur toute l'interface. Le thème Solarized Light (beige) a été implémenté avec les couleurs officielles de la palette Solarized.

## Thèmes Disponibles

### 1. Thème Clair (Light)
- **Identifiant**: `light`
- **Palette**: Couleurs claires professionnelles
- **Utilisation**: Interface par défaut

### 2. Thème Sombre (Dark)
- **Identifiant**: `dark`
- **Palette**: Couleurs sombres pour les environnements à faible luminosité
- **Utilisation**: Mode nuit

### 3. Thème Solarized Light (Beige)
- **Identifiant**: `beige`
- **Palette**: Palette Solarized Light officielle
- **Utilisation**: Interface scientifique et maritime

## Variables CSS du Thème

### Couleurs de Fond
```css
--bg-primary: #fdf6e3;      /* Fond principal */
--bg-secondary: #eee8d5;    /* Fond secondaire */
--bg-tertiary: #f4f1e8;     /* Fond tertiaire */
--bg-elevated: #ffffff;     /* Fond surélevé */
--bg-surface: #faf8f0;      /* Fond de surface */
--bg-overlay: rgba(253, 246, 227, 0.95); /* Fond d'overlay */
```

### Couleurs de Texte
```css
--text-primary: #586e75;    /* Texte principal */
--text-secondary: #657b83;  /* Texte secondaire */
--text-tertiary: #839496;   /* Texte tertiaire */
--text-muted: #93a1a1;      /* Texte atténué */
--text-inverse: #fdf6e3;    /* Texte inversé */
```

### Couleurs d'Accent
```css
--accent-primary: #268bd2;      /* Accent principal */
--accent-primary-hover: #1e6bb8; /* Accent principal au survol */
--accent-secondary: #2aa198;    /* Accent secondaire */
--accent-secondary-hover: #1f7a72; /* Accent secondaire au survol */
```

### Couleurs de Statut
```css
--status-success: #859900;      /* Succès */
--status-success-bg: #f4f6e8;   /* Fond succès */
--status-warning: #b58900;      /* Avertissement */
--status-warning-bg: #fdf6e3;   /* Fond avertissement */
--status-error: #dc322f;        /* Erreur */
--status-error-bg: #fdf2f2;     /* Fond erreur */
--status-info: #268bd2;         /* Information */
--status-info-bg: #f0f8ff;      /* Fond information */
```

### Couleurs de Bordure
```css
--border-primary: #e6dcc9;      /* Bordure principale */
--border-secondary: #d4c4a8;    /* Bordure secondaire */
--border-accent: #cb4b16;       /* Bordure d'accent */
```

## Application du Thème

### 1. Initialisation
Le thème est initialisé au démarrage de l'application dans `main.tsx` :
```typescript
const savedTheme = localStorage.getItem('chneowave-theme');
const theme = savedTheme && ['light', 'dark', 'beige'].includes(savedTheme) ? savedTheme : 'light';

document.documentElement.setAttribute('data-theme', theme);
document.body.classList.add(`theme-${theme}`);
```

### 2. Changement de Thème
Le composant `ThemeSelector` gère le changement de thème :
```typescript
const applyTheme = (theme: Theme) => {
  document.documentElement.removeAttribute('data-theme');
  document.body.classList.remove('theme-light', 'theme-dark', 'theme-beige');
  
  document.documentElement.setAttribute('data-theme', theme);
  document.body.classList.add(`theme-${theme}`);
  
  localStorage.setItem('chneowave-theme', theme);
};
```

### 3. Utilisation dans les Composants
Tous les composants utilisent maintenant les variables CSS du thème :
```tsx
<div style={{
  backgroundColor: 'var(--bg-elevated)',
  color: 'var(--text-primary)',
  border: '1px solid var(--border-primary)'
}}>
  Contenu
</div>
```

## Composants Corrigés

### Navigation
- `MinimalistNavigation.tsx` : Utilise les variables CSS pour tous les éléments
- Logo avec gradient dynamique
- Navigation items avec états actifs/inactifs
- Indicateur de statut système

### Dashboard
- `MinimalistDashboard.tsx` : Cartes et métriques thématisées
- Indicateurs de statut avec couleurs appropriées
- Barres de progression avec gradients
- Boutons d'action stylisés

### Pages
- Toutes les pages utilisent les variables CSS
- Icônes et éléments visuels cohérents
- États de statut uniformes

## Transitions et Animations

### Transitions Fluides
```css
* {
  transition: color 0.2s ease-out, background-color 0.2s ease-out, border-color 0.2s ease-out;
}
```

### Animations
- Fade-in pour les éléments
- Slide-in pour les sections
- Hover effects avec transformations

## Persistance

Le thème choisi est sauvegardé dans le localStorage et restauré au redémarrage de l'application.

## Accessibilité

- Contraste approprié pour tous les thèmes
- Focus states visibles
- Transitions fluides pour éviter les changements brusques

## Tests

Pour tester le système de thèmes :

1. Ouvrir l'interface sur http://localhost:5173
2. Utiliser le sélecteur de thème en haut à droite
3. Vérifier que tous les éléments changent de couleur
4. Recharger la page pour vérifier la persistance
5. Tester la navigation entre les différentes pages

## Maintenance

Pour ajouter un nouveau thème :

1. Ajouter les variables CSS dans `theme-system.css`
2. Mettre à jour le type `Theme` dans `ThemeSelector.tsx`
3. Ajouter l'option dans le sélecteur
4. Tester sur tous les composants

## Résolution des Problèmes

### Thème ne s'applique pas
- Vérifier que `data-theme` est défini sur `document.documentElement`
- Vérifier que les variables CSS sont correctement définies
- Inspecter les styles dans les outils de développement

### Couleurs incohérentes
- Vérifier que tous les composants utilisent les variables CSS
- Remplacer les couleurs hardcodées par les variables appropriées
- Tester sur tous les thèmes

### Performance
- Les transitions sont optimisées avec `will-change`
- Utilisation de `transform` pour les animations
- Éviter les reflows inutiles
