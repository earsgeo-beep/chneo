#!/usr/bin/env python3
"""
Test simple d'importation pour diagnostiquer les problèmes
"""

import sys
import os

# Ajouter le répertoire src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

print("=== Test d'importation simple ===")

try:
    print("1. Test PyQt5...")
    from PySide6.QtWidgets import QApplication
    print("   ✓ PyQt5 importé avec succès")
except Exception as e:
    print(f"   ✗ Erreur PyQt5: {e}")
    sys.exit(1)

try:
    print("2. Test ConfigManager...")
    from hrneowave.core.config_manager import ConfigManager
    print("   ✓ ConfigManager importé avec succès")
except Exception as e:
    print(f"   ✗ Erreur ConfigManager: {e}")

try:
    print("3. Test MainWindow...")
    from hrneowave.gui.main_window import MainWindow
    print("   ✓ MainWindow importé avec succès")
except Exception as e:
    print(f"   ✗ Erreur MainWindow: {e}")
    sys.exit(1)

try:
    print("4. Test instanciation QApplication...")
    app = QApplication([])
    print("   ✓ QApplication créée avec succès")
except Exception as e:
    print(f"   ✗ Erreur QApplication: {e}")
    sys.exit(1)

try:
    print("5. Test instanciation MainWindow...")
    config = {'simulation': {'enabled': True}}
    window = MainWindow(config=config)
    print("   ✓ MainWindow instanciée avec succès")
except Exception as e:
    print(f"   ✗ Erreur instanciation MainWindow: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n=== Tous les tests d'importation réussis ! ===")
app.quit()