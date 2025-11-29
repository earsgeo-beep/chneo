# Dashboard Design Pro - CHNeoWave

## Vue d'ensemble

Le nouveau tableau de bord professionnel CHNeoWave (`DashboardViewPro`) a été conçu selon les principes du Golden Ratio et une palette maritime moderne pour offrir une expérience utilisateur fluide, ergonomique et professionnelle adaptée aux laboratoires d'études maritimes.

## Principes de Design

### 1. Structure Golden Ratio

**Proportions fondamentales :**
- Ratio principal : φ = 1.618 (nombre d'or)
- Layout en deux colonnes : Sidebar (1) / Zone principale (1.618)
- Dimensions des cartes KPI : largeur/hauteur = 1.618
- Espacement basé sur la suite de Fibonacci : 8, 13, 21, 34, 55px

**Avantages :**
- Harmonie visuelle naturelle
- Scan visuel optimal (indicateurs clés en haut à gauche)
- Équilibre parfait entre zones de contrôle et de visualisation

### 2. Palette Maritime Professionnelle

**Couleurs principales :**
```css
/* Bleus profonds et minéraux */
--maritime-deep: #055080      /* Bleu minéral profond - éléments principaux */
--maritime-light: #41B6E6     /* Bleu clair - accents et highlights */
--maritime-turquoise: #24CED5 /* Turquoise - données actives */

/* Fonds et surfaces */
--maritime-snow: #F5FBFF      /* Blanc neige - arrière-plans */
--maritime-glass: rgba(245, 251, 255, 0.95) /* Effet verre */

/* Accents et états */
--maritime-emerald: #50DAC7   /* Cyan/émeraude - succès */
--maritime-steel: #445868     /* Gris acier - texte secondaire */
--maritime-coral: #FF6B47     /* Coral - alertes uniquement */
```

**Justification colorimétrique :**
- **Bleu minéral** : Évoque la profondeur océanique, inspire confiance et stabilité
- **Turquoise** : Rappelle les eaux claires, parfait pour les données en temps réel
- **Blanc neige** : Maximise la lisibilité, réduit la fatigue oculaire
- **Coral** : Réservé aux alertes, contraste optimal pour l'attention

### 3. Thématisation Avancée

**Mode Clair (défaut) :**
- Fond principal : Blanc neige (#F5FBFF)
- Texte : Bleu minéral profond (#055080)
- Cartes : Effet verre avec ombres subtiles
- Graphiques : Courbes turquoise sur fond clair

**Mode Sombre :**
- Fond principal : Bleu minéral profond (#055080)
- Texte : Blanc neige (#F5FBFF)
- Cartes : Transparence réduite, bordures lumineuses
- Graphiques : Courbes cyan sur fond sombre

**Toggle de thème :**
- Position : Coin supérieur droit
- Animation : Transition fluide 300ms
- Icône : Soleil/Lune maritime

### 4. Typographie et Hiérarchie

**Police principale :** Inter (fallback: Roboto)
- **H1 (Titres principaux) :** 2.2rem, semi-bold
- **H2 (Sous-titres) :** 1.5rem, medium
- **Labels :** 1rem, regular
- **Captions :** 0.85rem, light

**Justification :**
- Inter : Excellente lisibilité sur écran, optimisée pour les interfaces
- Hiérarchie claire : Facilite le scan visuel rapide
- Tailles relatives : Adaptation automatique aux différentes résolutions

### 5. Composants Standardisés

#### Cartes KPI (`ProKPICard`)
- **Dimensions :** Ratio Golden (largeur/hauteur = 1.618)
- **Contenu :** Valeur centrée, icône maritime, label descriptif
- **États :** Normal, hover, actif, alerte
- **Animation :** Micro-interactions (flash sur mise à jour)

#### Sidebar de Navigation (`ProSidebar`)
- **Largeur :** 280px (1/φ de la largeur standard)
- **Sections :** Projet actuel, navigation principale, outils rapides
- **Responsive :** Collapse automatique sur écrans < 1440px

#### Zone de Visualisation (`ProFFTWidget`)
- **Largeur minimale :** 1000px (optimisé salle technique)
- **Graphiques :** Courbes fluides, axes nets, labels grands
- **Interaction :** Zoom, pan, sélection temporelle

### 6. Animations et Transitions

**Principes :**
- **Durée :** 200-300ms (perception naturelle)
- **Easing :** cubic-bezier(0.4, 0.0, 0.2, 1) (Material Design)
- **Déclencheurs :** Hover, focus, changement d'état

**Types d'animations :**
- **Cartes KPI :** Scale léger (1.02) + ombre portée
- **Navigation :** Glissement horizontal fluide
- **Graphiques :** Apparition progressive des courbes
- **Thème :** Transition couleur globale

### 7. Ergonomie et Accessibilité

**Standards respectés :**
- **WCAG 2.1 AA :** Contraste minimum 4.5:1
- **Navigation clavier :** Tab, Enter, Espace, flèches
- **Responsive :** 1920x1080 (optimal) et 1440x900 (minimum)

**Optimisations UX :**
- **Zone de clic élargie :** Minimum 44px (recommandation mobile)
- **Feedback visuel :** États hover/focus clairement définis
- **Hiérarchie visuelle :** Importance décroissante de gauche à droite, haut en bas

### 8. Performance et Optimisation

**Stratégies :**
- **CSS optimisé :** Sélecteurs efficaces, propriétés groupées
- **Animations GPU :** Transform et opacity uniquement
- **Lazy loading :** Graphiques complexes chargés à la demande
- **Mise en cache :** Styles et ressources statiques

## Architecture Technique

### Structure des fichiers
```
gui/
├── views/
│   └── dashboard_view_pro.py     # Vue principale
├── widgets/
│   ├── pro_kpi_card.py          # Cartes KPI
│   ├── pro_sidebar.py           # Navigation
│   └── pro_fft_widget.py        # Visualisation
└── styles/
    └── maritime_dashboard.qss    # Styles CSS
```

### Signaux Qt
- `acquisitionRequested` : Demande de démarrage acquisition
- `themeChanged` : Changement de thème clair/sombre
- `kpiUpdated` : Mise à jour des indicateurs

### Intégration MVC
- **Modèle :** Aucune modification (respect total du core)
- **Vue :** `DashboardViewPro` remplace `DashboardViewGolden`
- **Contrôleur :** Signaux Qt préservés, compatibilité totale

## Tests et Validation

### Tests visuels
- [x] Proportions Golden Ratio respectées
- [x] Palette maritime cohérente
- [x] Transitions fluides
- [x] Responsive 1920x1080 et 1440x900

### Tests fonctionnels
- [x] Navigation entre vues
- [x] Mise à jour KPI en temps réel
- [x] Basculement thème clair/sombre
- [x] Compatibilité rétroactive

### Tests d'accessibilité
- [x] Navigation clavier complète
- [x] Contraste WCAG 2.1 AA
- [x] Tailles de police adaptatives
- [x] États focus visibles

## Conclusion

Le nouveau tableau de bord CHNeoWave Pro représente l'aboutissement d'une approche scientifique du design d'interface, alliant :

- **Harmonie mathématique** (Golden Ratio)
- **Cohérence thématique** (palette maritime)
- **Excellence ergonomique** (standards WCAG)
- **Performance technique** (optimisations Qt)

Cette interface est parfaitement adaptée aux exigences d'un logiciel d'instrumentation scientifique moderne, offrant aux ingénieurs de laboratoire un outil à la fois puissant et agréable à utiliser.

---

*Document généré pour CHNeoWave v1.0.0 - Laboratoire d'études maritimes*
*Dernière mise à jour : Juillet 2025*