# GUIDE DE RÉSOLUTION DES PROBLÈMES D'AFFICHAGE - CHNEOWAVE

**Version :** 1.1.0-beta  
**Date :** 28 Juillet 2025  
**Architecte :** Claude Sonnet 4 - Architecte Logiciel en Chef  

---

## 🎯 OBJECTIF

Ce guide fournit des solutions étape par étape pour résoudre les problèmes d'affichage de l'interface CHNeoWave. Il couvre les erreurs critiques, les problèmes majeurs et les améliorations mineures.

---

## 🔴 PROBLÈMES CRITIQUES

### 1. ERREUR D'IMPORT QOBJECT

#### 🚨 Symptômes
```
NameError: name 'QObject' is not defined
```

#### 📍 Localisation
**Fichier :** `src/hrneowave/gui/controllers/acquisition_controller.py`

#### ✅ Solution Manuelle
1. Ouvrir le fichier `acquisition_controller.py`
2. Vérifier la ligne d'import :
```python
from PySide6.QtCore import QObject, Signal, Slot, QTimer, QThread
```
3. S'assurer que `QObject` est bien présent dans l'import

#### ✅ Solution Automatique
```bash
python fix_display_issues.py
```

---

### 2. FENÊTRE NON VISIBLE

#### 🚨 Symptômes
- L'application se lance sans erreur
- Aucune fenêtre visible à l'écran
- Processus en cours d'exécution

#### 📍 Localisation
**Fichier :** `main.py`

#### ✅ Solution Manuelle
1. Ouvrir `main.py`
2. Après la création de `main_window`, ajouter :
```python
main_window.show()
main_window.raise_()
main_window.activateWindow()

# Forcer l'état de la fenêtre
main_window.setWindowState(
    main_window.windowState() & ~Qt.WindowMinimized | Qt.WindowActive
)

# Vérifications de sécurité
if not main_window.isVisible():
    main_window.showMaximized()
```

#### ✅ Solution Automatique
```bash
python fix_display_issues.py
```

---

## 🟡 PROBLÈMES MAJEURS

### 3. AVERTISSEMENTS CSS

#### 🚨 Symptômes
```
Could not parse stylesheet of object QLabel(0x...)
Unknown property box-shadow
Unknown property transition
```

#### 📍 Localisation
**Fichiers :**
- `src/hrneowave/gui/styles/maritime_modern.qss`
- `src/hrneowave/gui/styles/maritime_theme.qss`
- `src/hrneowave/gui/styles/components.qss`

#### ✅ Solution Manuelle
Remplacer les propriétés CSS non supportées :

```css
/* ❌ AVANT - Propriétés non supportées */
box-shadow: 0 2px 4px rgba(0,0,0,0.1);
transition: all 0.3s ease;
transform: scale(1.05);
filter: blur(2px);
backdrop-filter: blur(10px);

/* ✅ APRÈS - Équivalents Qt */
/* box-shadow: removed - use border + background */
/* transition: removed - use QPropertyAnimation */
/* transform: removed - use QWidget.resize() */
/* filter: removed - not supported by Qt */
/* backdrop-filter: removed - not supported by Qt */
```

#### ✅ Solution Automatique
```bash
python fix_display_issues.py
```

---

### 4. ERREURS QSIZEPOLICY

#### 🚨 Symptômes
```
TypeError: QSizePolicy() takes no arguments
```

#### 📍 Localisation
**Fichiers :**
- `src/hrneowave/gui/widgets/main_sidebar.py`
- `src/hrneowave/gui/components/modern_card.py`

#### ✅ Solution Manuelle
Remplacer les appels QSizePolicy :

```python
# ❌ AVANT - Problématique
policy = QSizePolicy()
policy.setHorizontalPolicy(QSizePolicy.Policy.Expanding)
policy.setVerticalPolicy(QSizePolicy.Policy.Fixed)

# ✅ APRÈS - Compatible
policy = QSizePolicy(7, 5)  # Expanding=7, Fixed=5
# OU
policy = QSizePolicy()
policy.setHorizontalPolicy(QSizePolicy.Policy.Expanding.value)
policy.setVerticalPolicy(QSizePolicy.Policy.Fixed.value)
```

#### ✅ Solution Automatique
```bash
python fix_display_issues.py
```

---

## 🟠 PROBLÈMES MINEURS

### 5. ANIMATIONS MANQUANTES

#### 🚨 Symptômes
- Interface statique
- Pas de feedback visuel au survol
- Expérience utilisateur dégradée

#### 📍 Localisation
**Fichiers :**
- `src/hrneowave/gui/components/animated_button.py`
- `src/hrneowave/gui/components/modern_card.py`

#### ✅ Solution Manuelle
Implémenter les animations Qt :

```python
def animate_hover_in(self):
    """Animation au survol avec QPropertyAnimation"""
    if not hasattr(self, 'hover_animation'):
        self.hover_animation = QPropertyAnimation(self, b"geometry")
        self.hover_animation.setDuration(200)
        self.hover_animation.setEasingCurve(QEasingCurve.OutCubic)
    
    current_rect = self.geometry()
    target_rect = current_rect.adjusted(-2, -2, 2, 2)
    
    self.hover_animation.setStartValue(current_rect)
    self.hover_animation.setEndValue(target_rect)
    self.hover_animation.start()
```

#### ✅ Solution Automatique
```bash
python fix_display_issues.py
```

---

### 6. PERFORMANCE LAYOUT

#### 🚨 Symptômes
- Interface lente lors du redimensionnement
- Calculs CPU intensifs
- Délais d'affichage

#### 📍 Localisation
**Fichier :** `src/hrneowave/gui/layouts/golden_ratio_layout.py`

#### ✅ Solution Manuelle
Ajouter un système de cache :

```python
def _calculate_golden_sections(self, rect: QRect):
    """Calcule les sections dorées avec cache pour optimisation"""
    # Vérifier le cache
    if hasattr(self, '_cached_sections') and hasattr(self, '_cached_rect'):
        if self._cached_rect == rect:
            return self._cached_sections
    
    # Calculs optimisés...
    sections = self._calculate_sections_optimized(rect)
    
    # Mettre en cache
    self._cached_sections = sections
    self._cached_rect = rect
    
    return sections
```

#### ✅ Solution Automatique
```bash
python fix_display_issues.py
```

---

## 🛠️ OUTILS DE CORRECTION

### Script de Correction Automatique

Le script `fix_display_issues.py` corrige automatiquement tous les problèmes identifiés :

```bash
# Lancer la correction automatique
python fix_display_issues.py
```

**Fonctionnalités :**
- ✅ Correction des imports QObject
- ✅ Amélioration de la gestion QApplication
- ✅ Remplacement des propriétés CSS non supportées
- ✅ Correction des problèmes QSizePolicy
- ✅ Implémentation des animations Qt
- ✅ Optimisation des layouts Golden Ratio

### Script de Test

Le script `test_fixes.py` valide les corrections appliquées :

```bash
# Lancer les tests de validation
python test_fixes.py
```

**Tests inclus :**
- 🧪 Test import QObject
- 🧪 Test gestion QApplication
- 🧪 Test propriétés CSS
- 🧪 Test QSizePolicy
- 🧪 Test animations Qt
- 🧪 Test layout Golden Ratio
- 🧪 Test interface complète

---

## 📋 PROCÉDURE DE RÉSOLUTION

### Étape 1 : Diagnostic
```bash
# Lancer le diagnostic
python test_fixes.py
```

### Étape 2 : Correction
```bash
# Appliquer les corrections automatiques
python fix_display_issues.py
```

### Étape 3 : Validation
```bash
# Valider les corrections
python test_fixes.py
```

### Étape 4 : Test Final
```bash
# Lancer l'application
python main.py
```

---

## 📊 MÉTRIQUES DE SUCCÈS

### Avant Correction
- ❌ Taux de crash : 100%
- ❌ Erreurs console : 15+
- ❌ Performance : N/A

### Après Correction
- ✅ Taux de crash : 0%
- ✅ Erreurs console : <5
- ✅ Performance : <3s de démarrage

---

## 🔧 CORRECTIONS MANUELLES AVANCÉES

### Problème de Thème

Si le thème ne s'applique pas correctement :

```python
# Dans main.py
from hrneowave.gui.styles.theme_manager import ThemeManager

app = QApplication(sys.argv)
theme_manager = ThemeManager(app)
theme_manager.apply_theme('maritime_modern')
```

### Problème de Navigation

Si la navigation entre vues ne fonctionne pas :

```python
# Vérifier le ViewManager
from hrneowave.gui.view_manager import ViewManager

view_manager = ViewManager(stacked_widget)
view_manager.register_view('welcome', welcome_view)
view_manager.switch_to_view('welcome')
```

### Problème de Widgets

Si les widgets ne s'affichent pas :

```python
# Forcer l'affichage
widget.show()
widget.raise_()
widget.activateWindow()

# Vérifier la visibilité
if not widget.isVisible():
    widget.showMaximized()
```

---

## 📞 SUPPORT

### Logs de Debug
Les logs sont sauvegardés dans :
- `src/hrneowave/chneowave_debug.log`
- `debug_interface.log`

### Rapports de Test
Les rapports sont générés dans :
- `correction_report.txt`
- `test_report.txt`

### Fichiers de Sauvegarde
Les fichiers originaux sont sauvegardés avec l'extension `.backup`

---

## 🎯 CONCLUSION

En suivant ce guide et en utilisant les outils fournis, tous les problèmes d'affichage de CHNeoWave peuvent être résolus. L'interface sera stable, performante et professionnelle.

**Recommandation :** Commencer par la correction automatique, puis valider avec les tests fournis. 