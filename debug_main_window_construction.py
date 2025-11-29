#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Diagnostic spécifique de la construction MainWindow CHNeoWave
"""

import sys
import traceback
from pathlib import Path

# Ajouter le chemin du projet
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_imports():
    """Test des imports critiques"""
    print("🔍 TEST DES IMPORTS CRITIQUES")
    print("=" * 40)
    
    try:
        from PySide6.QtWidgets import QApplication, QMainWindow
        print("✅ PySide6.QtWidgets importé")
        
        from hrneowave.gui.main_window import MainWindow
        print("✅ MainWindow importé")
        
        from hrneowave.gui.styles.theme_manager import ThemeManager
        print("✅ ThemeManager importé")
        
        return True
    except Exception as e:
        print(f"❌ Erreur imports: {e}")
        traceback.print_exc()
        return False

def test_view_imports():
    """Test des imports des vues"""
    print("\n🔍 TEST DES IMPORTS DE VUES")
    print("=" * 40)
    
    try:
        from hrneowave.gui.views import WelcomeView, DashboardViewMaritime
        print("✅ Vues principales importées")
        
        from hrneowave.gui.views import get_calibration_view, get_acquisition_view
        print("✅ Fonctions de chargement importées")
        
        return True
    except Exception as e:
        print(f"❌ Erreur imports vues: {e}")
        traceback.print_exc()
        return False

def test_widget_imports():
    """Test des imports des widgets"""
    print("\n🔍 TEST DES IMPORTS DE WIDGETS")
    print("=" * 40)
    
    try:
        from hrneowave.gui.widgets.main_sidebar import MainSidebar
        print("✅ MainSidebar importé")
        
        from hrneowave.gui.components.breadcrumbs import BreadcrumbsWidget
        print("✅ BreadcrumbsWidget importé")
        
        from hrneowave.gui.components.help_system import HelpPanel
        print("✅ HelpPanel importé")
        
        from hrneowave.gui.components.status_indicators import SystemStatusWidget
        print("✅ SystemStatusWidget importé")
        
        return True
    except Exception as e:
        print(f"❌ Erreur imports widgets: {e}")
        traceback.print_exc()
        return False

def test_main_window_construction_step_by_step():
    """Test de construction MainWindow étape par étape"""
    print("\n🔍 TEST CONSTRUCTION MAINWINDOW ÉTAPE PAR ÉTAPE")
    print("=" * 50)
    
    try:
        from PySide6.QtWidgets import QApplication
        from hrneowave.gui.main_window import MainWindow
        
        # Créer QApplication
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
            print("✅ QApplication créé")
        else:
            print("✅ QApplication existant réutilisé")
        
        # Test 1: Création de base
        print("\n📋 ÉTAPE 1: Création de base")
        print("-" * 30)
        
        main_window = MainWindow.__new__(MainWindow)
        print("✅ Objet MainWindow créé")
        
        # Test 2: Initialisation parent
        print("\n📋 ÉTAPE 2: Initialisation parent")
        print("-" * 30)
        
        main_window.__init__()
        print("✅ __init__ terminé")
        
        # Test 3: Vérifications de base
        print("\n📋 ÉTAPE 3: Vérifications de base")
        print("-" * 30)
        
        print(f"✅ WindowTitle: {main_window.windowTitle()}")
        print(f"✅ MinimumSize: {main_window.minimumSize()}")
        print(f"✅ CentralWidget: {main_window.centralWidget() is not None}")
        
        # Test 4: Affichage
        print("\n📋 ÉTAPE 4: Affichage")
        print("-" * 30)
        
        main_window.show()
        main_window.raise_()
        main_window.activateWindow()
        
        visible = main_window.isVisible()
        print(f"✅ Visible: {visible}")
        
        if visible:
            print("🎉 SUCCÈS: MainWindow visible!")
            
            # Maintenir ouvert 3 secondes
            from PySide6.QtCore import QTimer
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
        print(f"❌ Erreur construction: {e}")
        traceback.print_exc()
        return False

def test_view_creation():
    """Test de création des vues individuelles"""
    print("\n🔍 TEST CRÉATION DES VUES")
    print("=" * 40)
    
    try:
        from PySide6.QtWidgets import QApplication
        
        # Créer QApplication
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # Test WelcomeView
        print("\n📋 TEST WelcomeView")
        print("-" * 20)
        
        from hrneowave.gui.views import WelcomeView
        welcome_view = WelcomeView()
        print("✅ WelcomeView créée")
        
        # Test DashboardViewMaritime
        print("\n📋 TEST DashboardViewMaritime")
        print("-" * 20)
        
        from hrneowave.gui.views import DashboardViewMaritime
        dashboard_view = DashboardViewMaritime()
        print("✅ DashboardViewMaritime créée")
        
        # Test vues avec lazy loading
        print("\n📋 TEST VUES LAZY LOADING")
        print("-" * 20)
        
        from hrneowave.gui.views import get_calibration_view, get_acquisition_view
        
        try:
            calibration_view = get_calibration_view()
            print("✅ CalibrationView créée")
        except Exception as e:
            print(f"❌ Erreur CalibrationView: {e}")
        
        try:
            acquisition_view = get_acquisition_view()
            print("✅ AcquisitionView créée")
        except Exception as e:
            print(f"❌ Erreur AcquisitionView: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur création vues: {e}")
        traceback.print_exc()
        return False

def test_widget_creation():
    """Test de création des widgets individuels"""
    print("\n🔍 TEST CRÉATION DES WIDGETS")
    print("=" * 40)
    
    try:
        from PySide6.QtWidgets import QApplication
        
        # Créer QApplication
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # Test MainSidebar
        print("\n📋 TEST MainSidebar")
        print("-" * 20)
        
        from hrneowave.gui.widgets.main_sidebar import MainSidebar
        sidebar = MainSidebar()
        print("✅ MainSidebar créé")
        
        # Test BreadcrumbsWidget
        print("\n📋 TEST BreadcrumbsWidget")
        print("-" * 20)
        
        from hrneowave.gui.components.breadcrumbs import BreadcrumbsWidget
        breadcrumbs = BreadcrumbsWidget()
        print("✅ BreadcrumbsWidget créé")
        
        # Test HelpPanel
        print("\n📋 TEST HelpPanel")
        print("-" * 20)
        
        from hrneowave.gui.components.help_system import HelpPanel
        help_panel = HelpPanel()
        print("✅ HelpPanel créé")
        
        # Test SystemStatusWidget
        print("\n📋 TEST SystemStatusWidget")
        print("-" * 20)
        
        from hrneowave.gui.components.status_indicators import SystemStatusWidget
        status_widget = SystemStatusWidget()
        print("✅ SystemStatusWidget créé")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur création widgets: {e}")
        traceback.print_exc()
        return False

def main():
    """Point d'entrée principal"""
    print("🎯 DIAGNOSTIC CONSTRUCTION MAINWINDOW")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_view_imports,
        test_widget_imports,
        test_widget_creation,
        test_view_creation,
        test_main_window_construction_step_by_step
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
        print("✅ MainWindow devrait se construire correctement")
        return 0
    else:
        print("\n⚠️ CERTAINS TESTS ONT ÉCHOUÉ")
        print("❌ Problème identifié dans la construction")
        return 1

if __name__ == "__main__":
    exit(main()) 