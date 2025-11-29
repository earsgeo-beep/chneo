# SOLUTION D'URGENCE - PROBLÈME D'AFFICHAGE CHNEOWAVE

**🚨 PROBLÈME IDENTIFIÉ :** L'application se lance mais ne s'affiche pas  
**🎯 SOLUTION IMMÉDIATE :** Suivre les étapes ci-dessous  

---

## 🔥 SOLUTION RAPIDE (5 minutes)

### Étape 1 : Diagnostic Immédiat
```bash
# Lancer le diagnostic détaillé
python debug_launch_detailed.py
```

### Étape 2 : Correction Automatique
```bash
# Appliquer les corrections de lancement
python fix_launch_issue.py
```

### Étape 3 : Test Simple
```bash
# Tester avec une fenêtre simple
python test_simple_launch.py
```

### Étape 4 : Test Complet
```bash
# Lancer l'application corrigée
python main.py
```

---

## 🛠️ CORRECTION MANUELLE (Si automatique échoue)

### 1. Corriger main.py

Remplacer le contenu de `main.py` par :

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CHNeoWave - Point d'entrée principal CORRIGÉ
"""

import sys
import logging
from pathlib import Path

# Configuration logging
from hrneowave.core.logging_config import setup_logging
setup_logging()

log = logging.getLogger(__name__)

# Imports Qt
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

def main():
    """Point d'entrée principal corrigé"""
    print("🚀 Lancement de CHNeoWave v1.1.0")
    print("=" * 50)
    
    # Créer QApplication
    app = QApplication(sys.argv)
    app.setApplicationName("CHNeoWave")
    app.setQuitOnLastWindowClosed(True)
    
    print("✅ QApplication créé")

    try:
        # Thème (avec protection)
        try:
            from hrneowave.gui.styles.theme_manager import ThemeManager
            theme_manager = ThemeManager(app)
            theme_manager.apply_theme('maritime_modern')
            print("✅ Thème maritime appliqué")
        except Exception as e:
            print(f"⚠️ Erreur thème: {e}")

        # Créer MainWindow
        from hrneowave.gui.main_window import MainWindow
        main_window = MainWindow()
        print("✅ MainWindow créée")
        
        # FORCER L'AFFICHAGE
        main_window.show()
        main_window.raise_()
        main_window.activateWindow()
        
        # Forcer l'état
        main_window.setWindowState(
            main_window.windowState() & ~Qt.WindowMinimized | Qt.WindowActive
        )
        
        # Vérifications
        visible = main_window.isVisible()
        print(f"✅ Fenêtre visible: {visible}")
        
        if visible:
            print("🎉 SUCCÈS: Interface visible!")
            print("👀 L'interface devrait maintenant être affichée")
        else:
            print("❌ PROBLÈME: Interface non visible")
            main_window.showMaximized()
        
        # Boucle d'événements
        print("🔄 Démarrage boucle d'événements...")
        exit_code = app.exec()
        print(f"✅ Application fermée (code: {exit_code})")
        return exit_code
        
    except Exception as e:
        print(f"❌ ERREUR CRITIQUE: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
```

### 2. Vérifier les Imports

S'assurer que dans `src/hrneowave/gui/main_window.py` :

```python
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout
from PySide6.QtCore import Qt, Signal, Slot
```

### 3. Test Minimal

Créer `test_minimal.py` :

```python
#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from PySide6.QtWidgets import QApplication, QMainWindow, QLabel
from PySide6.QtCore import Qt

app = QApplication(sys.argv)
window = QMainWindow()
window.setWindowTitle("Test CHNeoWave")
window.setGeometry(200, 200, 400, 300)

label = QLabel("Test CHNeoWave - Interface Minimale")
label.setAlignment(Qt.AlignCenter)
window.setCentralWidget(label)

window.show()
window.raise_()
window.activateWindow()

print(f"✅ Fenêtre créée: Visible={window.isVisible()}")

app.exec()
```

---

## 🔍 DIAGNOSTIC DÉTAILLÉ

### Problèmes Possibles

1. **Erreur d'import** - Vérifier les logs
2. **Fenêtre minimisée** - Forcer l'affichage
3. **Problème de thème** - Désactiver temporairement
4. **Erreur dans MainWindow** - Utiliser fenêtre simple

### Commandes de Diagnostic

```bash
# Test 1: Fenêtre Qt simple
python test_minimal.py

# Test 2: Diagnostic complet
python debug_launch_detailed.py

# Test 3: Correction automatique
python fix_launch_issue.py

# Test 4: Application complète
python main.py
```

---

## 🚨 SOLUTIONS D'URGENCE

### Si l'application ne se lance pas du tout :

1. **Vérifier Python et PySide6** :
```bash
python --version
pip list | grep PySide6
```

2. **Réinstaller PySide6** :
```bash
pip uninstall PySide6
pip install PySide6
```

3. **Vérifier les chemins** :
```bash
python -c "import sys; print(sys.path)"
```

### Si l'application se lance mais ne s'affiche pas :

1. **Forcer l'affichage** :
```python
window.show()
window.raise_()
window.activateWindow()
window.setWindowState(Qt.WindowActive)
```

2. **Vérifier la visibilité** :
```python
print(f"Visible: {window.isVisible()}")
print(f"Active: {window.isActiveWindow()}")
print(f"Minimized: {window.isMinimized()}")
```

3. **Maximiser la fenêtre** :
```python
window.showMaximized()
```

---

## 📞 SUPPORT IMMÉDIAT

### Logs à Vérifier

1. **Console Python** - Erreurs d'import
2. **Logs CHNeoWave** - `src/hrneowave/chneowave_debug.log`
3. **Logs système** - Messages d'erreur Qt

### Tests de Validation

```bash
# Test 1: Qt fonctionne
python -c "from PySide6.QtWidgets import QApplication; print('Qt OK')"

# Test 2: Imports CHNeoWave
python -c "from hrneowave.gui.main_window import MainWindow; print('Imports OK')"

# Test 3: Fenêtre simple
python test_minimal.py

# Test 4: Application complète
python main.py
```

---

## 🎯 RÉSULTAT ATTENDU

Après application des corrections :

✅ **Application se lance sans erreur**  
✅ **Fenêtre visible à l'écran**  
✅ **Interface responsive**  
✅ **Thème maritime appliqué**  
✅ **Navigation fonctionnelle**  

---

## ⚠️ EN CAS D'ÉCHEC

Si les corrections ne fonctionnent pas :

1. **Sauvegarder les logs** :
```bash
python debug_launch_detailed.py > debug_log.txt 2>&1
```

2. **Créer un rapport d'erreur** :
```bash
python -c "import traceback; traceback.print_exc()" > error_report.txt
```

3. **Vérifier l'environnement** :
```bash
python -c "import sys; print('Python:', sys.version); import PySide6; print('PySide6:', PySide6.__version__)"
```

---

## 🚀 COMMANDES FINALES

```bash
# 1. Diagnostic
python debug_launch_detailed.py

# 2. Correction
python fix_launch_issue.py

# 3. Test
python test_simple_launch.py

# 4. Lancement
python main.py
```

**Résultat attendu :** Interface CHNeoWave visible et fonctionnelle en moins de 5 minutes. 