# CHNeoWave - Guide Design Maritime 2025

## 🌊 Introduction au Design System Maritime

Ce guide définit les standards de design pour l'interface CHNeoWave, conçue spécifiquement pour les laboratoires d'étude maritime sur modèles réduits. Il établit un langage visuel cohérent, des composants réutilisables et des patterns d'interaction optimisés pour les ingénieurs et chercheurs en environnement maritime.

---

## 📐 Principes Fondamentaux

### 1. Clarté Cognitive

L'interface doit minimiser la charge cognitive en présentant uniquement les informations essentielles au contexte actuel. Chaque vue doit avoir un objectif clair et une hiérarchie visuelle évidente.

### 2. Proportions Harmonieuses

Toutes les dimensions, espacements et layouts suivent le Golden Ratio (1:1.618) et la suite de Fibonacci pour créer une harmonie visuelle naturelle qui facilite la lecture des données scientifiques.

### 3. Cohérence Maritime

La palette de couleurs, les métaphores visuelles et la terminologie reflètent l'environnement maritime professionnel, créant une familiarité immédiate pour les utilisateurs du domaine.

### 4. Performance Fluide

Toutes les animations et transitions sont optimisées pour maintenir 60fps, avec des temps de réponse inférieurs à 100ms pour garantir une expérience utilisateur sans friction.

---

## 🎨 Système de Couleurs Maritime

### Palette Primaire

| Couleur | Hex | RGB | Usage |
|---------|-----|-----|-------|
| Ocean Deep | `#0A1929` | `10, 25, 41` | Arrière-plans, textes principaux |
| Harbor Blue | `#1565C0` | `21, 101, 192` | Éléments principaux, accents |
| Steel Blue | `#1976D2` | `25, 118, 210` | Boutons actifs, liens |
| Frost White | `#FAFBFC` | `250, 251, 252` | Arrière-plans clairs, textes sur fond sombre |

### Palette Secondaire

| Couleur | Hex | RGB | Usage |
|---------|-----|-----|-------|
| Deep Navy | `#0D47A1` | `13, 71, 161` | Éléments d'accent secondaires |
| Tidal Green | `#00838F` | `0, 131, 143` | Indicateurs positifs, succès |
| Coral Alert | `#FF5722` | `255, 87, 34` | Alertes, erreurs, avertissements |

### Palette de Support

| Couleur | Hex | RGB | Usage |
|---------|-----|-----|-------|
| Storm Gray | `#37474F` | `55, 71, 79` | Textes secondaires, icônes |
| Seafoam | `#E0F7FA` | `224, 247, 250` | Arrière-plans subtils, séparateurs |

### Variables CSS

```css
:root {
  --ocean-deep: #0A1929;
  --harbor-blue: #1565C0;
  --steel-blue: #1976D2;
  --frost-white: #FAFBFC;
  --deep-navy: #0D47A1;
  --tidal-green: #00838F;
  --coral-alert: #FF5722;
  --storm-gray: #37474F;
  --seafoam: #E0F7FA;
}
```

---

## 📏 Espacement & Layout

### Système d'Espacement Fibonacci

Tous les espacements suivent la suite de Fibonacci pour créer une progression naturelle:

| Nom | Valeur | Usage |
|-----|--------|-------|
| space-xs | 8px | Espacement minimal entre éléments liés |
| space-sm | 13px | Espacement standard entre éléments |
| space-md | 21px | Padding interne des conteneurs |
| space-lg | 34px | Marges entre sections |
| space-xl | 55px | Espacement entre blocs majeurs |
| space-xxl | 89px | Espacement maximal |

### Grille Golden Ratio

- **Sidebar** : 280px (1 unité)
- **Zone principale** : 453px (1.618 unité)
- **Ratio Card** : largeur:hauteur = 1.618:1

### Rayons de Bordure

| Élément | Rayon |
|---------|-------|
| Cards | 8px |
| Boutons | 4px |
| Inputs | 4px |
| Tooltips | 4px |

---

## 🔤 Typographie Maritime

### Hiérarchie Typographique

| Élément | Taille | Poids | Interligne | Usage |
|---------|--------|-------|--------------|-------|
| H1 | 34px | 600 | 1.2 | Titres principaux |
| H2 | 21px | 600 | 1.3 | Titres de section |
| H3 | 16px | 500 | 1.4 | Sous-titres |
| Body | 14px | 400 | 1.5 | Texte courant |
| Caption | 12px | 400 | 1.4 | Légendes, notes |
| Code | 13px | 400 | 1.6 | Données techniques |

### Famille de Polices

```css
font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
```

### Contraste & Lisibilité

- Contraste texte/fond: minimum 4.5:1 (WCAG AA)
- Taille minimale texte: 12px
- Interligne: 1.5x pour le corps de texte

---

## 🧩 Composants Standardisés

### MaritimeCard

Conteneur principal pour regrouper des informations connexes.

```css
.MaritimeCard {
  background-color: var(--frost-white);
  border-radius: 8px;
  padding: 21px;
  box-shadow: 0 2px 8px rgba(10, 25, 41, 0.1);
}
```

### KPIIndicator

Affichage de métriques clés avec titre, valeur et icône.

```css
.KPIIndicator {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.KPIIndicator-title {
  font-size: 12px;
  color: var(--storm-gray);
}

.KPIIndicator-value {
  font-size: 21px;
  font-weight: 600;
  color: var(--ocean-deep);
}
```

### StatusBeacon

Indicateur d'état avec code couleur.

```css
.StatusBeacon {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.StatusBeacon--active {
  background-color: var(--tidal-green);
  box-shadow: 0 0 8px var(--tidal-green);
}

.StatusBeacon--warning {
  background-color: #FFC107;
  box-shadow: 0 0 8px #FFC107;
}

.StatusBeacon--error {
  background-color: var(--coral-alert);
  box-shadow: 0 0 8px var(--coral-alert);
}
```

### MaritimeButton

Boutons d'action standardisés.

```css
.MaritimeButton {
  padding: 8px 21px;
  border-radius: 4px;
  font-weight: 500;
  transition: all 0.2s ease;
}

.MaritimeButton--primary {
  background-color: var(--harbor-blue);
  color: var(--frost-white);
}

.MaritimeButton--secondary {
  background-color: transparent;
  color: var(--harbor-blue);
  border: 1px solid var(--harbor-blue);
}
```

### ProgressStepper

Navigation par étapes avec indicateur de progression.

```css
.ProgressStepper {
  display: flex;
  flex-direction: column;
  gap: 21px;
}

.ProgressStepper-step {
  display: flex;
  align-items: center;
  gap: 13px;
}

.ProgressStepper-indicator {
  width: 21px;
  height: 21px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.ProgressStepper-step--completed .ProgressStepper-indicator {
  background-color: var(--tidal-green);
  color: var(--frost-white);
}

.ProgressStepper-step--current .ProgressStepper-indicator {
  background-color: var(--harbor-blue);
  color: var(--frost-white);
}

.ProgressStepper-step--pending .ProgressStepper-indicator {
  background-color: var(--seafoam);
  color: var(--storm-gray);
}
```

---

## 🎭 États & Animations

### États des Composants

| État | Apparence | Transition |
|------|-----------|------------|
| Default | État normal | - |
| Hover | Légère élévation, luminosité +5% | 200ms ease |
| Active/Pressed | Échelle 98%, luminosité -5% | 100ms ease |
| Focus | Anneau lumineux 2px | 200ms ease |
| Disabled | Opacité 50%, non-interactif | 200ms ease |
| Loading | Skeleton loader ou pulsation | 1.5s ease infinite |
| Error | Bordure/fond rouge subtil | 200ms ease |

### Animations Standards

| Animation | Durée | Courbe | Usage |
|-----------|-------|--------|-------|
| Fade | 200ms | ease-out | Apparition/disparition |
| Slide | 300ms | cubic-bezier(0.4, 0, 0.2, 1) | Transitions entre vues |
| Scale | 150ms | ease | Feedback interaction |
| Pulse | 1.5s | ease-in-out | Indicateurs d'activité |

---

## 📱 Responsive Design

### Breakpoints

| Nom | Dimension | Cible |
|-----|-----------|-------|
| sm | ≥ 768px | Petits écrans |
| md | ≥ 1024px | Écrans moyens |
| lg | ≥ 1366px | Grands écrans |
| xl | ≥ 1920px | Très grands écrans |

### Adaptations

- **Sidebar**: Collapsible sous 1024px
- **Grille KPI**: 1 colonne (sm), 2 colonnes (md), 3 colonnes (lg+)
- **Graphiques**: Hauteur adaptative, minimum 300px
- **Contrôles**: Regroupés en accordéon sous 768px

---

## 📊 Visualisation de Données

### Graphiques

- **Couleurs**: Utiliser la palette secondaire pour différencier les séries
- **Grille**: Subtile, gris clair (#EEEEEE)
- **Axes**: Étiquettes en Storm Gray, taille 12px
- **Tooltips**: Apparaître au hover, fond blanc, ombre légère

### Tableaux

- **En-têtes**: Fond Harbor Blue léger, texte Storm Gray
- **Lignes alternées**: Blanc et Seafoam très léger
- **Hover ligne**: Highlight subtil
- **Pagination**: Maximum 25 lignes par page

---

## 🧠 Patterns d'Interaction

### Navigation

- **Sidebar**: Navigation principale, toujours visible sur grands écrans
- **Breadcrumbs**: Pour la navigation hiérarchique profonde
- **Tabs**: Pour alterner entre vues connexes

### Formulaires

- **Validation inline**: Feedback immédiat sous le champ
- **Groupement logique**: Sections avec titres clairs
- **Progression**: Indication visuelle de l'avancement

### Feedback

- **Toasts**: Notifications temporaires, 4 secondes par défaut
- **Alertes**: Messages persistants nécessitant attention
- **Confirmations**: Pour actions destructives ou irréversibles

---

## 🛠️ Implémentation Technique

### Organisation des Styles

- `maritime_design_system.qss`: Styles globaux et variables
- `maritime_components.qss`: Styles des composants réutilisables
- `maritime_animations.qss`: Définitions des animations
- `maritime_layout.qss`: Grilles et structures de page

### Bonnes Pratiques

- Utiliser les variables CSS pour toutes les couleurs et espacements
- Préfixer les classes spécifiques avec `Maritime-`
- Suivre la convention BEM pour les modificateurs
- Documenter les composants avec des commentaires

---

## 🔍 Accessibilité

### Standards Minimaux

- Contraste texte/fond: WCAG AA (4.5:1)
- Navigation clavier complète
- Focus visuel évident
- Textes alternatifs pour éléments visuels
- Taille minimale des cibles tactiles: 44x44px

### Tests Recommandés

- Vérification contraste avec Color Contrast Analyzer
- Navigation sans souris
- Test avec différentes tailles de texte

---

## 📝 Checklist de Validation

Utiliser cette checklist pour valider chaque vue avant intégration:

- [ ] Palette de couleurs conforme
- [ ] Espacements Fibonacci respectés
- [ ] Typographie selon hiérarchie définie
- [ ] Composants standardisés utilisés
- [ ] États interactifs implémentés
- [ ] Animations fluides (60fps)
- [ ] Responsive sur tous breakpoints
- [ ] Accessibilité WCAG AA
- [ ] Performance optimisée
- [ ] Documentation complète