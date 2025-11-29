<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" class="logo" width="120"/>

# Analyse Approfondie et Prompt de Correction Interface CHNeoWave

## 🔍 Analyse des Problèmes Identifiés

Après analyse des images fournies et recherche sur les meilleures pratiques de design d'interfaces professionnelles 2025, voici les **problèmes critiques** identifiés dans l'interface actuelle :

### Problèmes de Design Majeurs

1. **Design daté** : Interface trop classique, non alignée avec les standards modernes 2025[^1][^2]
2. **Fragmentation UX** : Scroll nécessaire pour accéder aux formulaires (anti-pattern pour logiciels professionnels)[^3][^4]
3. **Manque de hiérarchie visuelle** : Information mal organisée, sans application du nombre d'or[^5][^6]
4. **Mode sombre défaillant** : Contraste insuffisant, texte invisible (violation WCAG 2.1)[^7]
5. **Pas d'identité maritime** : Logo et branding non intégrés de manière professionnelle

### Standards Modernes à Appliquer

D'après les recherches sur les logiciels scientifiques maritimes[^8][^9] et les tendances UI 2025[^1][^2], l'interface doit respecter :

- **Principe de proximité** : Éléments liés regroupés visuellement[^10]
- **Design adaptatif** : Interface qui s'adapte au contenu sans scroll[^4]
- **Hiérarchie claire** : Application stricte du nombre d'or (ratio 1.618)[^5][^6]
- **Contraste optimal** : 4.5:1 minimum pour accessibilité[^7]


## 🚀 Prompt Ultra-Précis pour l'Agent

```
🌊 MISSION CRITIQUE : MODERNISATION COMPLÈTE INTERFACE CHNEOWAVE 2025

## CONTEXTE ET PROBLÈMES IDENTIFIÉS

### Situation Actuelle
L'interface CHNeoWave dans le dossier `qwen_design_isolated` présente des défauts critiques qui compromettent l'expérience utilisateur professionnelle :
- Design classique/daté incompatible avec standards maritimes 2025
- UX fragmentée nécessitant scroll (anti-ergonomique pour laboratoires)
- Mode sombre illisible (texte noir invisible, dimensions incorrectes)
- Absence d'identité maritime professionnelle intégrée
- Non-application du nombre d'or pour harmonie visuelle

### Références de Qualité
Transformer l'interface selon l'exemple neo-1.jpg : simple, moderne, accessible, riche, architecture professionnelle, sans scroll, avec nombre d'or appliqué et logo intégré.

## SPÉCIFICATIONS TECHNIQUES DE MODERNISATION

### 1. ARCHITECTURE GOLDEN RATIO STRICTE

**Layout principal obligatoire :**
```

.interface-container {
display: grid;
grid-template-columns: 1fr 1.618fr; /* Sidebar : Main = 1:φ */
grid-template-rows: auto 1fr;
min-height: 100vh;
gap: 0;
}

.header-section {
grid-column: 1 / -1;
height: calc(55px * 1.618); /* φ ratio pour header */
}

.sidebar-navigation {
width: 280px; /* Base φ */
max-width: calc(280px * 1.618);
}

.main-content {
width: calc(280px * 1.618 * 1.618); /* φ² ratio */
}

```

**Espacements harmoniques Fibonacci :**
```

:root {
/* Suite Fibonacci pour espacements */
--space-xs: 8px;
--space-sm: 13px;
--space-md: 21px;
--space-lg: 34px;
--space-xl: 55px;
--space-xxl: 89px;
}

```

### 2. CORRECTION CRITIQUE MODE SOMBRE

**Problème identifié :** Texte noir invisible sur fond sombre
**Solution obligatoire :**

```

/* Palette mode sombre WCAG 2.1 AA compliant */
[data-theme="dark"] {
/* Fonds professionnels */
--bg-primary: \#0f172a;        /* Bleu nuit professionnel */
--bg-secondary: \#1e293b;      /* Surfaces élevées */
--bg-tertiary: \#334155;       /* Cards et composants */

/* Textes haute lisibilité (contraste >7:1) */
--text-primary: \#f8fafc;      /* Blanc principal */
--text-secondary: \#e2e8f0;    /* Gris clair secondaire */
--text-muted: \#94a3b8;        /* Labels et légendes */

/* Couleurs maritimes adaptées */
--maritime-blue: \#3b82f6;     /* Bleu océan visible */
--maritime-cyan: \#06b6d4;     /* Cyan données */
--maritime-success: \#10b981;  /* Vert validation */
--maritime-warning: \#f59e0b;  /* Orange alertes */
--maritime-error: \#ef4444;    /* Rouge erreurs */

/* Bordures et séparateurs */
--border-primary: \#475569;    /* Bordures principales */
--border-secondary: \#64748b;  /* Bordures secondaires */
}

/* Application texte - JAMAIS noir en mode sombre */
[data-theme="dark"] .text-content {
color: var(--text-primary) !important;
background: transparent;
}

[data-theme="dark"] input,
[data-theme="dark"] textarea,
[data-theme="dark"] select {
background: var(--bg-tertiary);
color: var(--text-primary);
border: 1px solid var(--border-primary);
}

```

### 3. INTERFACE SANS SCROLL - LAYOUT ADAPTATIF

**Principe :** Tout visible dans la fenêtre, organisation intelligente des sections

```

<!-- Structure modernisée sans scroll -->

<div class="chneowave-interface" data-theme="light">
  <!-- Header avec logo intégré -->
  <header class="maritime-header">
    <div class="brand-section">
      <div class="logo-container">
        <svg class="logo-waves" viewBox="0 0 60 24">
          <!-- Vagues stylisées CHNeoWave -->
        </svg>
        <span class="brand-text">CHNeoWave</span>
      </div>
      <div class="project-context">
        <span class="project-name">Projet Maritime Actuel</span>
        <span class="project-status">Calibration en cours</span>
      </div>
    </div>
    <div class="header-actions">
      <button class="theme-toggle">🌙</button>
      <div class="user-menu">Dr. Martin Dubois</div>
    </div>
    </header>

<!-- Layout principal Golden Ratio -->

  <div class="main-layout">
    <!-- Sidebar navigation compacte -->
    <nav class="sidebar-compact">
      <div class="nav-sections">
        <div class="section-group">
          <div class="section-title">Workflow</div>
          <ul class="nav-items">
            <li class="nav-item active">Dashboard</li>
            <li class="nav-item">Calibration</li>
            <li class="nav-item">Acquisition</li>
            <li class="nav-item">Analyse</li>
          </ul>
        </div>
      </div>
    </nav>
    
    <!-- Zone principale - Tout visible sans scroll -->
    <main class="content-area">
      <!-- Section formulaires en cards compactes -->
      <div class="forms-grid golden-ratio-grid">
        <!-- Card 1: Informations projet -->
        <div class="info-card maritime-card">
          <h3>Informations Projet</h3>
          <div class="form-compact">
            <div class="field-row">
              <label>Nom:</label>
              <input type="text" value="Bassin IFREMER 2025">
            </div>
            <div class="field-row">
              <label>Code:</label>
              <input type="text" value="CHN-2025-001">
            </div>
            <!-- Plus de champs compacts -->
          </div>
        </div>
    
        <!-- Card 2: Configuration acquisition -->
        <div class="config-card maritime-card">
          <h3>Configuration</h3>
          <div class="form-compact">
            <div class="field-row">
              <label>Sondes:</label>
              <select><option>5 capteurs</option></select>
            </div>
            <div class="field-row">
              <label>Fréquence:</label>
              <select><option>1000 Hz</option></select>
            </div>
          </div>
        </div>
    
        <!-- Card 3: Statut système -->
        <div class="status-card maritime-card">
          <h3>Statut Système</h3>
          <div class="status-indicators">
            <div class="indicator good">
              <span class="dot"></span>
              <span>Acquisition: OK</span>
            </div>
            <div class="indicator good">
              <span class="dot"></span>
              <span>Calibration: 5/5</span>
            </div>
          </div>
        </div>
      </div>
    
      <!-- Section visualisation intégrée -->
      <div class="visualization-area">
        <div class="chart-container maritime-chart">
          <canvas id="main-chart"></canvas>
        </div>
      </div>
    </main>
    </div>
</div>

```

### 4. CARDS SYSTEM MODERNE (SANS SCROLL)

```

.forms-grid {
display: grid;
grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
gap: var(--space-lg);
margin-bottom: var(--space-xl);
}

.maritime-card {
background: var(--bg-card);
border-radius: 12px;
padding: var(--space-md);
border: 1px solid var(--border-light);
box-shadow: 0 2px 8px rgba(0,0,0,0.04);
transition: all 0.3s ease;

/* Golden ratio appliqué */
min-height: calc(200px * 1.618);
aspect-ratio: 1.618 / 1;
}

.maritime-card:hover {
transform: translateY(-2px);
box-shadow: 0 8px 24px rgba(0,0,0,0.08);
}

.form-compact {
display: flex;
flex-direction: column;
gap: var(--space-sm);
}

.field-row {
display: grid;
grid-template-columns: 1fr 2fr;
align-items: center;
gap: var(--space-sm);
}

```

### 5. BRANDING MARITIME INTÉGRÉ

```

.maritime-header {
background: linear-gradient(135deg, \#0f172a 0%, \#1e293b 100%);
padding: var(--space-md) var(--space-lg);
border-bottom: 2px solid var(--maritime-blue);
}

.brand-section {
display: flex;
align-items: center;
gap: var(--space-lg);
}

.logo-container {
display: flex;
align-items: center;
gap: var(--space-sm);
}

.logo-waves {
width: 60px;
height: 24px;
fill: var(--maritime-cyan);
animation: wave-motion 3s ease-in-out infinite;
}

.brand-text {
font-size: 1.5rem;
font-weight: 700;
color: white;
text-shadow: 0 1px 3px rgba(0,0,0,0.3);
}

@keyframes wave-motion {
0%, 100% { transform: scaleY(1); }
50% { transform: scaleY(1.1); }
}

```

### 6. SYSTÈME DE NAVIGATION MODERNE

```

.sidebar-compact {
width: 280px;
background: var(--bg-sidebar);
padding: var(--space-lg) var(--space-md);
border-right: 1px solid var(--border-light);
}

.nav-item {
padding: var(--space-sm) var(--space-md);
border-radius: 8px;
cursor: pointer;
transition: all 0.2s ease;
margin-bottom: var(--space-xs);
}

.nav-item.active {
background: var(--maritime-blue);
color: white;
box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
}

.nav-item:hover:not(.active) {
background: var(--bg-hover);
transform: translateX(4px);
}

```

### 7. RESPONSIVITÉ ET ACCESSIBILITÉ

```

/* Adaptation écrans laboratoire */
@media (max-width: 1400px) {
.forms-grid {
grid-template-columns: repeat(2, 1fr);
}
}

@media (max-width: 1024px) {
.forms-grid {
grid-template-columns: 1fr;
}

.main-layout {
grid-template-columns: 1fr;
}

.sidebar-compact {
width: 100%;
order: 2;
}
}

/* Accessibilité clavier */
.nav-item:focus,
.maritime-card:focus {
outline: 2px solid var(--maritime-blue);
outline-offset: 2px;
}

```

## CORRECTIONS SPÉCIFIQUES OBLIGATOIRES

### 1. ÉLIMINATION TOTALE DU SCROLL
- **Remplacer** toutes les sections verticales par des grilles horizontales
- **Utiliser** flexbox et CSS Grid pour optimiser l'espace
- **Organiser** l'information en cards compactes visibles simultanément
- **Appliquer** la règle des 7±2 éléments maximum par vue

### 2. CORRECTION MODE SOMBRE CRITIQUE
- **Remplacer** TOUS les `color: black` par `color: var(--text-primary)`
- **Appliquer** contraste minimum 7:1 pour le texte principal
- **Utiliser** `color-scheme: dark light` pour adaptation automatique
- **Tester** la lisibilité sur tous les éléments

### 3. INTÉGRATION LOGO MARITIME
- **Créer** logo SVG avec vagues animées
- **Intégrer** dans le header avec animation subtile
- **Appliquer** cohérence chromatique maritime partout
- **Ajouter** favicon et branding cohérent

### 4. APPLICATION NOMBRE D'OR STRICTE
- **Calculer** toutes les proportions selon φ = 1.618
- **Appliquer** aux grilles, cartes, espacements
- **Utiliser** la suite de Fibonacci pour les marges
- **Créer** harmonie visuelle mathématique

## PLAN D'EXÉCUTION SÉQUENTIEL

### JOUR 1 : Architecture et Layout (6h)
1. **Restructurer** le HTML selon Golden Ratio
2. **Éliminer** tout scroll vertical
3. **Créer** système de cards compactes
4. **Implémenter** grille responsive

### JOUR 2 : Correction Mode Sombre (4h)  
1. **Corriger** tous les contrastes de couleur
2. **Remplacer** textes noirs par variables
3. **Tester** lisibilité complète
4. **Valider** WCAG 2.1 AA

### JOUR 3 : Branding et Polish (4h)
1. **Intégrer** logo CHNeoWave animé
2. **Finaliser** identité maritime
3. **Ajouter** micro-animations
4. **Tests** utilisabilité finale

## CRITÈRES DE VALIDATION ABSOLUS

### Tests Visuels Obligatoires
- ✅ Interface complète visible sans scroll vertical
- ✅ Mode sombre 100% lisible (contraste ≥7:1)
- ✅ Logo CHNeoWave intégré et animé
- ✅ Proportions Golden Ratio respectées partout
- ✅ Design moderne comparable à neo-1.jpg

### Tests Fonctionnels
- ✅ Navigation fluide sans rupture
- ✅ Formulaires accessibles en mode compact
- ✅ Responsive sur résolutions 1366x768 à 4K
- ✅ Accessibilité clavier complète
- ✅ Performance 60fps sur toutes animations

## DOSSIER DE TRAVAIL

**Répertoire :** `qwen_design_isolated/`
**Fichiers à modifier :**
- `index.html` (restructuration complète)
- `css/maritime-2025.css` (nouveau système)
- `css/golden-ratio.css` (proportions φ)
- `css/dark-mode-fix.css` (correction contraste)
- `js/modern-interface.js` (interactions)

COMMENCER IMMÉDIATEMENT PAR LA RESTRUCTURATION LAYOUT
PRIORITÉ ABSOLUE : ÉLIMINER LE SCROLL + CORRIGER MODE SOMBRE
OBJECTIF : INTERFACE MARITIME PROFESSIONNELLE 2025 NIVEAU INDUSTRIEL
```

Ce prompt adresse tous les problèmes identifiés avec des solutions techniques précises basées sur les meilleures pratiques de design 2025 pour logiciels professionnels maritimes, garantissant une interface moderne, accessible et ergonomique sans compromis.

<div style="text-align: center">⁂</div>

[^1]: https://www.uxstudioteam.com/ux-blog/ui-trends-2019

[^2]: https://uihut.com/blog/top-10-ui-design-trends-to-look-for-in-2025

[^3]: https://eprints.whiterose.ac.uk/id/eprint/138058/8/Good Usability Practices in Scientific Software Development.pdf

[^4]: https://varenyaz.com/top-7-ui-ux-design-best-practices-for-manufacturing

[^5]: https://blog.prototypr.io/golden-ratio-in-ui-design-8d11e66582c3

[^6]: https://www.interaction-design.org/literature/topics/golden-ratio

[^7]: https://www.reddit.com/r/userexperience/comments/14hi9t9/is_dark_mode_considered_a_form_of_accessible/

[^8]: https://valeriobattagli.com/2604-2/

[^9]: https://www.sintef.no/en/publications/publication/1678373/

[^10]: https://www.peakboard.com/en/blog/6-design-principles-for-first-class-dashboards

[^11]: neo-1.jpg

[^12]: design-valider.jpg

[^13]: moderniser-interface.jpg

[^14]: casser.jpg

[^15]: https://www.figma.com/resource-library/ui-design-principles/

[^16]: https://maze.co/collections/ux-ui-design/ui-design-principles/

[^17]: https://www.numberanalytics.com/blog/mastering-ui-design-in-industrial-design

[^18]: https://fulminoussoftware.com/user-interface-best-practices-for-industrial-websites

[^19]: https://fireart.studio/blog/designing-modern-ui-ux/

[^20]: https://fivejars.com/insights/dark-mode-ui-9-design-considerations-you-cant-ignore/

[^21]: https://www.nngroup.com/articles/golden-ratio-ui-design/

[^22]: https://fuselabcreative.com/top-dashboard-design-trends-2025/

[^23]: https://learn.microsoft.com/en-us/windows/win32/winauto/accessibility-best-practices

[^24]: https://webandcrafts.com/blog/ui-design-principles

[^25]: https://app.uxcel.com/tutorials/12-principles-of-dark-mode-design-627

[^26]: https://design4users.com/ui-design-golden-ratio/

[^27]: https://www.uxpin.com/studio/blog/dashboard-design-principles/

[^28]: https://www.resonio.com/blog/accessibility-in-ui-design/

[^29]: https://www.uxdesigninstitute.com/blog/guide-to-the-ui-design-process/

[^30]: https://www.uxdesigninstitute.com/blog/dark-mode-design-practical-guide/

[^31]: https://www.youtube.com/watch?v=zL_XPR37zHY

[^32]: https://uxplanet.org/dashboard-that-works-a-step-by-step-guide-for-startups-in-2025-1cec1bfe7f9c

[^33]: https://lucid.co/blog/designing-for-accessibility-best-practices

[^34]: https://openautomationsoftware.com/blog/principles-successful-ui-design/

[^35]: https://www.theknowledgeacademy.com/blog/ui-design-principles/

[^36]: https://stfalcon.com/en/blog/post/user-interface-web-design-principles

[^37]: https://www.shopify.com/blog/ui-design-principles

[^38]: https://www.controleng.com/eight-data-acquisition-best-practices/

[^39]: https://www.smashingmagazine.com/2025/04/inclusive-dark-mode-designing-accessible-dark-themes/

[^40]: https://www.interaction-design.org/literature/topics/ergonomics

[^41]: https://www.uxdesigninstitute.com/blog/design-intuitive-user-interfaces/

[^42]: https://www.plantengineering.com/how-to-enhance-data-acquisition-best-practices/

[^43]: https://uxplanet.org/golden-ratio-bring-balance-in-ui-design-765c954f0ff9

[^44]: https://stephaniewalter.design/blog/dark-mode-accessibility-myth-debunked/

[^45]: https://www.forbes.com/councils/forbestechcouncil/2024/08/16/how-to-ensure-user-friendly-ergonomic-design-in-software-projects/

[^46]: https://devspheretechnologies.com/ui-design-principles-guide/

[^47]: https://dewesoft.com/blog/what-is-data-acquisition

[^48]: https://www.mockplus.com/blog/post/the-golden-ratio-in-design

[^49]: https://dubbot.com/dubblog/2023/dark-mode-a11y.html

[^50]: https://www.linkedin.com/advice/0/how-do-you-adapt-your-user-interface-design-different

[^51]: https://designli.co/blog/essential-ui-design-principles-for-business-success

[^52]: https://www.andacademy.com/resources/blog/ui-ux-design/ui-design-principles/

[^53]: https://www.youtube.com/watch?v=NTmh8l-Xl4c

[^54]: https://learn.microsoft.com/en-us/dynamics365/guidance/develop/ui-ux-design-principles

[^55]: https://cdpstudio.com/blog/maritime-ui-design/

[^56]: https://www.openbridge.no/about-openbridge

[^57]: https://www.uxdesigninstitute.com/blog/ux-design-principles/

[^58]: https://cdpstudio.com/blog/openbridge-maritime-uis/

[^59]: https://learnui.design/blog/7-rules-for-creating-gorgeous-ui-part-1.html

[^60]: https://www.uxdesigninstitute.com/blog/guide-to-the-rule-of-thirds-in-ux/

[^61]: https://dribbble.com/tags/maritime-shipping-app

[^62]: https://aircconline.com/ijsea/V10N5/10519ijsea05.pdf

[^63]: https://www.eleken.co/blog-posts/9-ui-ux-design-principles-to-make-customers-get-chills-from-your-product

[^64]: https://www.mddionline.com/software/improve-scientific-software-with-these-ux-design-best-practices

[^65]: https://www.valtech.com/blog/does-dark-mode-win-on-sustainability-and-accessibility/

[^66]: https://www.designstudiouiux.com/blog/top-ux-design-principles/

[^67]: https://hype4.academy/articles/design/best-ux-ui-design-tools-in-2025

[^68]: https://www.uxdesigninstitute.com/blog/user-interface-ui-design-tools/

[^69]: https://www.fullstack.com/labs/resources/blog/top-5-ux-ui-design-trends-in-2025-the-future-of-user-experiences

[^70]: https://gloriathemes.com/software-woocommerce-themes/

[^71]: https://devpulse.io/insights/ux-ui-design-best-practices-2025-enterprise-applications/

[^72]: https://www.instinctools.com/blog/ux-best-practices/

[^73]: https://wordpress.org/themes/professional-software-company/

[^74]: https://www.interaction-design.org/literature/article/ux-design-tools-definitive-guide

[^75]: https://divami.com/news/ux-ui-best-practices-for-designing-complex-software-products/

[^76]: https://www.sisense.com/blog/4-design-principles-creating-better-dashboards/

[^77]: https://themeforest.net/search/software company

[^78]: https://trends.uxdesign.cc

