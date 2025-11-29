#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Diagnostic très détaillé de la construction MainWindow étape par étape
"""

import sys
import traceback
from pathlib import Path

# Ajouter le chemin du projet
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_main_window_constructor_step_by_step():
    """Test de construction MainWindow étape par étape très détaillé"""
    print("🔍 DIAGNOSTIC MAINWINDOW ÉTAPE PAR ÉTAPE")
    print("=" * 50)
    
    try:
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import Qt, QTimer
        
        # Créer QApplication
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
            app.setApplicationName("CHNeoWave Debug Step by Step")
        
        print("✅ QApplication créé")
        
        # Test import MainWindow
        print("\n📋 ÉTAPE 1: Import MainWindow")
        print("-" * 30)
        try:
            from hrneowave.gui.main_window import MainWindow
            print("✅ MainWindow importé")
        except Exception as e:
            print(f"❌ Erreur import MainWindow: {e}")
            traceback.print_exc()
            return False
        
        # Test création MainWindow étape par étape
        print("\n📋 ÉTAPE 2: Création MainWindow étape par étape")
        print("-" * 30)
        
        try:
            print("🔄 Étape 2.1: Création objet MainWindow...")
            main_window = MainWindow.__new__(MainWindow)
            print("✅ Objet MainWindow créé")
            
            print("🔄 Étape 2.2: Initialisation parent...")
            main_window.__init__()
            print("✅ __init__ terminé")
            
        except Exception as e:
            print(f"❌ Erreur création MainWindow: {e}")
            traceback.print_exc()
            return False
        
        # Test affichage
        print("\n📋 ÉTAPE 3: Test affichage")
        print("-" * 30)
        
        try:
            print("🔄 Affichage MainWindow...")
            main_window.show()
            main_window.raise_()
            main_window.activateWindow()
            
            visible = main_window.isVisible()
            print(f"✅ MainWindow visible: {visible}")
            
            if visible:
                print("🎉 SUCCÈS: MainWindow visible!")
                
                # Maintenir ouvert 5 secondes
                timer = QTimer()
                timer.timeout.connect(app.quit)
                timer.start(5000)
                
                print("🔄 Maintien ouvert 5 secondes...")
                exit_code = app.exec()
                print(f"✅ Test terminé (code: {exit_code})")
                return True
            else:
                print("❌ PROBLÈME: MainWindow non visible")
                return False
                
        except Exception as e:
            print(f"❌ Erreur affichage: {e}")
            traceback.print_exc()
            return False
            
    except Exception as e:
        print(f"❌ Erreur critique: {e}")
        traceback.print_exc()
        return False

def test_main_window_imports():
    """Test des imports utilisés par MainWindow"""
    print("\n🔍 TEST IMPORTS MAINWINDOW")
    print("=" * 40)
    
    imports_to_test = [
        ("PySide6.QtWidgets.QMainWindow", "QMainWindow"),
        ("PySide6.QtWidgets.QMessageBox", "QMessageBox"),
        ("PySide6.QtWidgets.QStackedWidget", "QStackedWidget"),
        ("PySide6.QtWidgets.QHBoxLayout", "QHBoxLayout"),
        ("PySide6.QtWidgets.QVBoxLayout", "QVBoxLayout"),
        ("PySide6.QtWidgets.QWidget", "QWidget"),
        ("PySide6.QtWidgets.QLabel", "QLabel"),
        ("PySide6.QtCore.Signal", "Signal"),
        ("PySide6.QtCore.Slot", "Slot"),
        ("PySide6.QtCore.QTimer", "QTimer"),
        ("PySide6.QtCore.Qt", "Qt"),
        ("hrneowave.gui.styles.theme_manager", "ThemeManager"),
        ("hrneowave.gui.views", "views"),
        ("hrneowave.gui.widgets.main_sidebar", "MainSidebar"),
        ("hrneowave.gui.components.breadcrumbs", "BreadcrumbsWidget"),
        ("hrneowave.gui.components.help_system", "HelpPanel"),
        ("hrneowave.gui.components.status_indicators", "SystemStatusWidget"),
    ]
    
    failed_imports = []
    
    for module_path, module_name in imports_to_test:
        try:
            if module_path.startswith("PySide6"):
                exec(f"from {module_path} import {module_name}")
            else:
                exec(f"import {module_path}")
            print(f"✅ {module_path}")
        except Exception as e:
            print(f"❌ {module_path}: {e}")
            failed_imports.append((module_path, str(e)))
    
    if failed_imports:
        print(f"\n⚠️ {len(failed_imports)} imports échoués:")
        for module_path, error in failed_imports:
            print(f"   • {module_path}: {error}")
        return False
    else:
        print("\n✅ Tous les imports réussis")
        return True

def test_main_window_methods():
    """Test des méthodes de MainWindow"""
    print("\n🔍 TEST MÉTHODES MAINWINDOW")
    print("=" * 40)
    
    try:
        from PySide6.QtWidgets import QApplication
        from hrneowave.gui.main_window import MainWindow
        
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        print("🔄 Test création MainWindow...")
        main_window = MainWindow()
        print("✅ MainWindow créée")
        
        # Test des méthodes principales
        methods_to_test = [
            ("windowTitle()", main_window.windowTitle),
            ("minimumSize()", main_window.minimumSize),
            ("centralWidget()", main_window.centralWidget),
            ("isVisible()", main_window.isVisible),
        ]
        
        for method_name, method in methods_to_test:
            try:
                result = method()
                print(f"✅ {method_name}: {result}")
            except Exception as e:
                print(f"❌ {method_name}: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur test méthodes: {e}")
        traceback.print_exc()
        return False

def test_simple_window_fixed():
    """Test de la fenêtre simplifiée corrigée"""
    print("\n🔍 TEST FENÊTRE SIMPLIFIÉE CORRIGÉE")
    print("=" * 40)
    
    try:
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import Qt, QTimer
        
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
            app.setApplicationName("CHNeoWave Simple Test")
        
        print("✅ QApplication créé")
        
        # Test import fenêtre simplifiée
        print("🔄 Import SimpleMainWindow...")
        from hrneowave.gui.simple_main_window import SimpleMainWindow
        print("✅ SimpleMainWindow importé")
        
        # Test création fenêtre simplifiée
        print("🔄 Création SimpleMainWindow...")
        main_window = SimpleMainWindow()
        print("✅ SimpleMainWindow créée")
        
        # Test affichage
        print("🔄 Affichage SimpleMainWindow...")
        main_window.show()
        main_window.raise_()
        main_window.activateWindow()
        
        visible = main_window.isVisible()
        print(f"✅ SimpleMainWindow visible: {visible}")
        
        if visible:
            print("🎉 SUCCÈS: SimpleMainWindow visible!")
            
            # Maintenir ouvert 5 secondes
            timer = QTimer()
            timer.timeout.connect(app.quit)
            timer.start(5000)
            
            print("🔄 Maintien ouvert 5 secondes...")
            exit_code = app.exec()
            print(f"✅ Test terminé (code: {exit_code})")
            return True
        else:
            print("❌ PROBLÈME: SimpleMainWindow non visible")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        traceback.print_exc()
        return False

def main():
    """Point d'entrée principal"""
    print("🎯 DIAGNOSTIC MAINWINDOW ÉTAPE PAR ÉTAPE")
    print("=" * 50)
    
    tests = [
        test_main_window_imports,
        test_simple_window_fixed,
        test_main_window_methods,
        test_main_window_constructor_step_by_step
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
        print("✅ MainWindow devrait fonctionner correctement")
        return 0
    else:
        print("\n⚠️ CERTAINS TESTS ONT ÉCHOUÉ")
        print("❌ Problème identifié dans MainWindow")
        return 1

if __name__ == "__main__":
    exit(main()) 