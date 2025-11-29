#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Diagnostic spécifique du problème acquisition_controller.py
"""

import sys
import traceback
from pathlib import Path

# Ajouter le chemin du projet
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_imports_step_by_step():
    """Test des imports étape par étape"""
    print("🔍 DIAGNOSTIC IMPORTS ACQUISITION CONTROLLER")
    print("=" * 50)
    
    try:
        # Test 1: Imports de base
        print("\n📋 ÉTAPE 1: Imports de base")
        print("-" * 30)
        
        import numpy as np
        print("✅ numpy importé")
        
        import time
        print("✅ time importé")
        
        import threading
        print("✅ threading importé")
        
        from typing import Dict, List, Optional, Tuple, Any
        print("✅ typing importé")
        
        from dataclasses import dataclass
        print("✅ dataclasses importé")
        
        from enum import Enum
        print("✅ enum importé")
        
        import json
        print("✅ json importé")
        
        import os
        print("✅ os importé")
        
        import logging
        print("✅ logging importé")
        
        # Test 2: Imports Qt
        print("\n📋 ÉTAPE 2: Imports Qt")
        print("-" * 30)
        
        from PySide6.QtCore import QObject, Signal, Slot, QTimer, QThread
        print("✅ PySide6.QtCore importé")
        
        from PySide6.QtWidgets import QApplication
        print("✅ PySide6.QtWidgets importé")
        
        # Test 3: Imports signal_bus
        print("\n📋 ÉTAPE 3: Imports signal_bus")
        print("-" * 30)
        
        try:
            from hrneowave.core.signal_bus import (
                get_signal_bus, get_error_bus, ErrorLevel, SessionState
            )
            print("✅ signal_bus importé")
            UNIFIED_SIGNALS_AVAILABLE = True
        except ImportError as e:
            print(f"⚠️ signal_bus non disponible: {e}")
            UNIFIED_SIGNALS_AVAILABLE = False
        
        # Test 4: Imports circular_buffer
        print("\n📋 ÉTAPE 4: Imports circular_buffer")
        print("-" * 30)
        
        try:
            from hrneowave.core.circular_buffer import create_circular_buffer, BufferConfig
            print("✅ circular_buffer importé")
        except ImportError as e:
            print(f"⚠️ circular_buffer non disponible: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur imports: {e}")
        traceback.print_exc()
        return False

def test_acquisition_controller_import():
    """Test de l'import du module acquisition_controller"""
    print("\n🔍 TEST IMPORT ACQUISITION CONTROLLER")
    print("=" * 40)
    
    try:
        print("🔄 Import du module acquisition_controller...")
        from hrneowave.gui.controllers.acquisition_controller import AcquisitionController
        print("✅ AcquisitionController importé")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur import AcquisitionController: {e}")
        traceback.print_exc()
        return False

def test_acquisition_controller_creation():
    """Test de création d'une instance AcquisitionController"""
    print("\n🔍 TEST CRÉATION ACQUISITION CONTROLLER")
    print("=" * 40)
    
    try:
        from PySide6.QtWidgets import QApplication
        from hrneowave.gui.controllers.acquisition_controller import AcquisitionController, AcquisitionConfig, AcquisitionMode
        
        # Créer QApplication
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        print("✅ QApplication créé")
        
        # Créer configuration
        print("🔄 Création configuration...")
        config = AcquisitionConfig(
            mode=AcquisitionMode.SIMULATE,
            sample_rate=32.0,
            n_channels=4,
            buffer_size=10000
        )
        print("✅ Configuration créée")
        
        # Créer contrôleur
        print("🔄 Création AcquisitionController...")
        controller = AcquisitionController(config)
        print("✅ AcquisitionController créé")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur création AcquisitionController: {e}")
        traceback.print_exc()
        return False

def test_main_window_without_acquisition():
    """Test MainWindow sans acquisition_controller"""
    print("\n🔍 TEST MAINWINDOW SANS ACQUISITION")
    print("=" * 40)
    
    try:
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import Qt, QTimer
        
        # Créer QApplication
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        print("✅ QApplication créé")
        
        # Test import MainWindow
        print("🔄 Import MainWindow...")
        from hrneowave.gui.main_window import MainWindow
        print("✅ MainWindow importé")
        
        # Test création MainWindow
        print("🔄 Création MainWindow...")
        main_window = MainWindow()
        print("✅ MainWindow créée")
        
        # Test affichage
        print("🔄 Affichage MainWindow...")
        main_window.show()
        main_window.raise_()
        main_window.activateWindow()
        
        visible = main_window.isVisible()
        print(f"✅ MainWindow visible: {visible}")
        
        if visible:
            print("🎉 SUCCÈS: MainWindow visible!")
            
            # Maintenir ouvert 3 secondes
            timer = QTimer()
            timer.timeout.connect(app.quit)
            timer.start(3000)
            
            print("🔄 Maintien ouvert 3 secondes...")
            exit_code = app.exec()
            print(f"✅ Test terminé (code: {exit_code})")
            return True
        else:
            print("❌ PROBLÈME: MainWindow non visible")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        traceback.print_exc()
        return False

def test_controllers_init():
    """Test du fichier __init__.py des controllers"""
    print("\n🔍 TEST CONTROLLERS __INIT__")
    print("=" * 40)
    
    try:
        print("🔄 Import du module controllers...")
        from hrneowave.gui.controllers import __init__ as controllers_init
        print("✅ Module controllers importé")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur import controllers: {e}")
        traceback.print_exc()
        return False

def main():
    """Point d'entrée principal"""
    print("🎯 DIAGNOSTIC ACQUISITION CONTROLLER")
    print("=" * 50)
    
    tests = [
        test_imports_step_by_step,
        test_controllers_init,
        test_acquisition_controller_import,
        test_acquisition_controller_creation,
        test_main_window_without_acquisition
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Erreur lors du test: {e}")
            failed += 1
    
    print(f"\n📊 RÉSULTATS:")
    print(f"✅ Tests réussis: {passed}")
    print(f"❌ Tests échoués: {failed}")
    
    if failed == 0:
        print("\n🎉 TOUS LES TESTS RÉUSSIS!")
        print("✅ AcquisitionController fonctionne correctement")
        return 0
    else:
        print("\n⚠️ CERTAINS TESTS ONT ÉCHOUÉ")
        print("❌ Problème identifié dans AcquisitionController")
        return 1

if __name__ == "__main__":
    exit(main()) 