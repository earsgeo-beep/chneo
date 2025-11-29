#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de debug pour identifier le problème avec MainWindow
"""

import sys
import os
import traceback

# Ajouter le chemin src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

print("=== Test d'importation ===\n")

# Test 1: Importation de PyQt5
try:
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtCore import pyqtSlot
    print("✓ PyQt5 importé avec succès")
except Exception as e:
    print(f"✗ Erreur PyQt5: {e}")
    traceback.print_exc()

# Test 2: Importation ConfigManager
try:
    from hrneowave.core.config_manager import ConfigManager
    config = ConfigManager()
    print("✓ ConfigManager importé et instancié avec succès")
except Exception as e:
    print(f"✗ Erreur ConfigManager: {e}")
    traceback.print_exc()

# Test 3: Importation MainWindow
try:
    from hrneowave.gui.main_window import MainWindow
    print("✓ MainWindow importé avec succès")
except Exception as e:
    print(f"✗ Erreur importation MainWindow: {e}")
    traceback.print_exc()
    sys.exit(1)

# Test 4: Création QApplication
try:
    app = QApplication([])
    print("✓ QApplication créée avec succès")
except Exception as e:
    print(f"✗ Erreur QApplication: {e}")
    traceback.print_exc()
    sys.exit(1)

# Test 5: Instanciation MainWindow
try:
    config = {'hardware': {'simulation_mode': True, 'backend': 'demo'}}
    window = MainWindow(config=config)
    print("✓ MainWindow instanciée avec succès")
except Exception as e:
    print(f"✗ Erreur instanciation MainWindow: {e}")
    traceback.print_exc()
    sys.exit(1)

# Test 6: Affichage et fermeture
try:
    window.show()
    print("✓ MainWindow affichée avec succès")
    window.close()
    print("✓ MainWindow fermée avec succès")
except Exception as e:
    print(f"✗ Erreur affichage/fermeture: {e}")
    traceback.print_exc()

print("\n=== Tous les tests réussis ===\n")