# Guide de l'Interface Utilisateur : La Grille Fibonacci

## 1. Philosophie de Conception : Harmonie et Clarté

L'interface de CHNeoWave v1.0.0 a été conçue en s'appuyant sur des principes mathématiques intemporels : le **nombre d'or (φ ≈ 1.618)** et la **suite de Fibonacci (1, 1, 2, 3, 5, 8, 13...)**. Cette approche n'est pas purement esthétique ; elle vise à créer une expérience utilisateur (UX) qui soit :

- **Harmonieuse** : Les proportions basées sur φ sont naturellement agréables à l'œil humain, réduisant la charge cognitive.
- **Hiérarchisée** : La croissance exponentielle de la suite de Fibonacci permet de créer des hiérarchies visuelles claires entre les éléments (titres, textes, conteneurs).
- **Cohérente** : En utilisant un système de grille et d'espacement prédictible, chaque vue de l'application partage une structure sous-jacente commune, rendant la navigation plus intuitive.

## 2. Le Cœur du Système : `FibonacciGridMixin`

Pour implémenter ce système de manière efficace et réutilisable, la classe `FibonacciGridMixin` a été introduite dans `src/hrneowave/gui/layouts/fibonacci_grid_mixin.py`.

Ce mixin fournit des méthodes statiques pour construire des `QGridLayout` qui respectent les ratios de Fibonacci.

### `create_fibonacci_grid(base_unit=8)`

Cette méthode est le principal constructeur de grille. Elle retourne un `QGridLayout` préconfiguré avec :

- **Marges** : Les marges extérieures de la grille sont définies par une valeur de la suite (par défaut, 13px, soit `fib(7)`).
- **Espacements** : L'espacement horizontal et vertical entre les cellules de la grille est également défini par une valeur de la suite (par défaut, 8px, soit `fib(6)`).

**Exemple d'utilisation dans une vue :**

```python
from hrneowave.gui.layouts.fibonacci_grid_mixin import FibonacciGridMixin

class MyView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = FibonacciGridMixin.create_fibonacci_grid()
        # ... ajouter des widgets au layout
        self.setLayout(self.layout)
```

### `get_fibonacci_stretch_factors(count=5)`

Pour créer des mises en page responsives où les colonnes ou les lignes ne grandissent pas de manière uniforme, cette méthode retourne une liste de facteurs d'étirement (stretch factors) basés sur la suite de Fibonacci.

Ceci est particulièrement utile pour les mises en page de type "sidebar/contenu" où le contenu principal doit occuper proportionnellement plus d'espace.

**Exemple :**

```python
layout = QGridLayout()
stretches = FibonacciGridMixin.get_fibonacci_stretch_factors(2) # Retourne [3, 5]
layout.setColumnStretch(0, stretches[0]) # Colonne 0
layout.setColumnStretch(1, stretches[1]) # Colonne 1 (plus large)
```

## 3. Application Pratique : Le `DashboardView`

Le `DashboardView` est un excellent exemple de l'application de ces principes :

- La grille principale utilise `create_fibonacci_grid()` pour un espacement cohérent.
- Les cartes KPI (`PhiCard`) ont des dimensions qui respectent le ratio φ. Leur largeur et hauteur sont dans un rapport proche de 1.618.
- Les facteurs d'étirement de la grille sont calculés avec `get_fibonacci_stretch_factors()` pour que la zone du graphe FFT (plus importante) occupe un espace proportionnel à sa signification (un rectangle de ratio 8:5, deux nombres consécutifs de la suite).

## 4. Variables de Style (`variables.qss`)

La philosophie Fibonacci/φ est également étendue aux feuilles de style QSS. Le fichier `src/hrneowave/gui/theme/variables.qss` centralise ces valeurs :

```css
:root {
    /* ... autres variables ... */

    /* Suite de Fibonacci */
    --fibonacci-1: 1px;
    --fibonacci-2: 2px;
    --fibonacci-3: 3px;
    --fibonacci-5: 5px;
    --fibonacci-8: 8px;
    --fibonacci-13: 13px;

    /* Ratio φ (nombre d'or) */
    --phi: 1.618;
    --phi-inverse: 0.618;
    --phi-gap: var(--fibonacci-13); /* 13px, φ * 8px */
}
```

La variable `--phi-gap` est ensuite utilisée dans `theme_dark.qss` pour définir les `padding` des conteneurs, assurant une cohérence parfaite entre la logique de layout Python et le stylisme QSS.

## 5. Conclusion

En adoptant une approche de conception basée sur la grille de Fibonacci et le nombre d'or, CHNeoWave assure une interface non seulement esthétique mais aussi fonctionnelle, prédictible et facile à maintenir. Ce système fournit un cadre robuste pour les développements futurs, garantissant que l'application restera cohérente et harmonieuse à mesure qu'elle évolue.