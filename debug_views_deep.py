#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Diagnostic très approfondi du problème dans les vues
"""

import sys
import traceback
from pathlib import Path

# Ajouter le chemin du projet
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_welcome_view_import():
    """Test d'import de WelcomeView"""
    print("🔍 TEST IMPORT WELCOMEVIEW")
    print("=" * 40)
    
    try:
        print("🔄 Import WelcomeView...")
        from hrneowave.gui.views.welcome_view import WelcomeView
        print("✅ WelcomeView importé")
        return True
    except Exception as e:
        print(f"❌ Erreur import WelcomeView: {e}")
        traceback.print_exc()
        return False

def test_dashboard_view_import():
    """Test d'import de DashboardViewMaritime"""
    print("\n🔍 TEST IMPORT DASHBOARDVIEW")
    print("=" * 40)
    
    try:
        print("🔄 Import DashboardViewMaritime...")
        from hrneowave.gui.views.dashboard_view import DashboardViewMaritime
        print("✅ DashboardViewMaritime importé")
        return True
    except Exception as e:
        print(f"❌ Erreur import DashboardViewMaritime: {e}")
        traceback.print_exc()
        return False

def test_welcome_view_creation():
    """Test de création de WelcomeView"""
    print("\n🔍 TEST CRÉATION WELCOMEVIEW")
    print("=" * 40)
    
    try:
        from PySide6.QtWidgets import QApplication
        
        # Créer QApplication
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        print("✅ QApplication créé")
        
        print("🔄 Création WelcomeView...")
        from hrneowave.gui.views.welcome_view import WelcomeView
        welcome_view = WelcomeView(parent=None)
        print("✅ WelcomeView créée")
        
        return True
    except Exception as e:
        print(f"❌ Erreur création WelcomeView: {e}")
        traceback.print_exc()
        return False

def test_dashboard_view_creation():
    """Test de création de DashboardViewMaritime"""
    print("\n🔍 TEST CRÉATION DASHBOARDVIEW")
    print("=" * 40)
    
    try:
        from PySide6.QtWidgets import QApplication
        
        # Créer QApplication
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        print("✅ QApplication créé")
        
        print("🔄 Création DashboardViewMaritime...")
        from hrneowave.gui.views.dashboard_view import DashboardViewMaritime
        dashboard_view = DashboardViewMaritime(parent=None)
        print("✅ DashboardViewMaritime créée")
        
        return True
    except Exception as e:
        print(f"❌ Erreur création DashboardViewMaritime: {e}")
        traceback.print_exc()
        return False

def test_view_manager_creation():
    """Test de création du ViewManager"""
    print("\n🔍 TEST CRÉATION VIEWMANAGER")
    print("=" * 40)
    
    try:
        from PySide6.QtWidgets import QApplication, QStackedWidget
        
        # Créer QApplication
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        print("✅ QApplication créé")
        
        print("🔄 Création QStackedWidget...")
        stack_widget = QStackedWidget()
        print("✅ QStackedWidget créé")
        
        print("🔄 Création ViewManager...")
        from hrneowave.gui.view_manager import ViewManager
        view_manager = ViewManager(stack_widget)
        print("✅ ViewManager créé")
        
        return True
    except Exception as e:
        print(f"❌ Erreur création ViewManager: {e}")
        traceback.print_exc()
        return False

def test_view_registration():
    """Test d'enregistrement des vues"""
    print("\n🔍 TEST ENREGISTREMENT DES VUES")
    print("=" * 40)
    
    try:
        from PySide6.QtWidgets import QApplication, QStackedWidget
        
        # Créer QApplication
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        print("✅ QApplication créé")
        
        # Créer QStackedWidget
        print("🔄 Création QStackedWidget...")
        stack_widget = QStackedWidget()
        print("✅ QStackedWidget créé")
        
        # Créer ViewManager
        print("🔄 Création ViewManager...")
        from hrneowave.gui.view_manager import ViewManager
        view_manager = ViewManager(stack_widget)
        print("✅ ViewManager créé")
        
        # Test enregistrement WelcomeView
        print("🔄 Enregistrement WelcomeView...")
        from hrneowave.gui.views.welcome_view import WelcomeView
        welcome_view = WelcomeView(parent=None)
        view_manager.register_view('welcome', welcome_view)
        print("✅ WelcomeView enregistrée")
        
        # Test enregistrement DashboardViewMaritime
        print("🔄 Enregistrement DashboardViewMaritime...")
        from hrneowave.gui.views.dashboard_view import DashboardViewMaritime
        dashboard_view = DashboardViewMaritime(parent=None)
        view_manager.register_view('dashboard', dashboard_view)
        print("✅ DashboardViewMaritime enregistrée")
        
        return True
    except Exception as e:
        print(f"❌ Erreur enregistrement vues: {e}")
        traceback.print_exc()
        return False

def test_view_switching():
    """Test de changement de vue"""
    print("\n🔍 TEST CHANGEMENT DE VUE")
    print("=" * 40)
    
    try:
        from PySide6.QtWidgets import QApplication, QStackedWidget
        
        # Créer QApplication
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        print("✅ QApplication créé")
        
        # Créer QStackedWidget
        print("🔄 Création QStackedWidget...")
        stack_widget = QStackedWidget()
        print("✅ QStackedWidget créé")
        
        # Créer ViewManager
        print("🔄 Création ViewManager...")
        from hrneowave.gui.view_manager import ViewManager
        view_manager = ViewManager(stack_widget)
        print("✅ ViewManager créé")
        
        # Enregistrer WelcomeView
        print("🔄 Enregistrement WelcomeView...")
        from hrneowave.gui.views.welcome_view import WelcomeView
        welcome_view = WelcomeView(parent=None)
        view_manager.register_view('welcome', welcome_view)
        print("✅ WelcomeView enregistrée")
        
        # Test changement de vue
        print("🔄 Changement vers 'welcome'...")
        view_manager.switch_to_view('welcome')
        print("✅ Changement vers 'welcome' réussi")
        
        return True
    except Exception as e:
        print(f"❌ Erreur changement de vue: {e}")
        traceback.print_exc()
        return False

def test_create_and_register_views_step_by_step():
    """Test de _create_and_register_views étape par étape très détaillé"""
    print("\n🔍 TEST _CREATE_AND_REGISTER_VIEWS ÉTAPE PAR ÉTAPE")
    print("=" * 50)
    
    try:
        from PySide6.QtWidgets import QApplication, QStackedWidget
        
        # Créer QApplication
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        print("✅ QApplication créé")
        
        # Créer QStackedWidget
        print("🔄 Création QStackedWidget...")
        stack_widget = QStackedWidget()
        print("✅ QStackedWidget créé")
        
        # Créer ViewManager
        print("🔄 Création ViewManager...")
        from hrneowave.gui.view_manager import ViewManager
        view_manager = ViewManager(stack_widget)
        print("✅ ViewManager créé")
        
        # Test étape 1: WelcomeView
        print("\n📋 ÉTAPE 1: WelcomeView")
        print("-" * 30)
        print("🔄 Import WelcomeView...")
        from hrneowave.gui.views.welcome_view import WelcomeView
        print("✅ WelcomeView importé")
        
        print("🔄 Création WelcomeView...")
        welcome_view = WelcomeView(parent=None)
        print("✅ WelcomeView créée")
        
        print("🔄 Enregistrement WelcomeView...")
        view_manager.register_view('welcome', welcome_view)
        print("✅ WelcomeView enregistrée")
        
        # Test étape 2: DashboardViewMaritime
        print("\n📋 ÉTAPE 2: DashboardViewMaritime")
        print("-" * 30)
        print("🔄 Import DashboardViewMaritime...")
        from hrneowave.gui.views.dashboard_view import DashboardViewMaritime
        print("✅ DashboardViewMaritime importé")
        
        print("🔄 Création DashboardViewMaritime...")
        dashboard_view = DashboardViewMaritime(parent=None)
        print("✅ DashboardViewMaritime créée")
        
        print("🔄 Enregistrement DashboardViewMaritime...")
        view_manager.register_view('dashboard', dashboard_view)
        print("✅ DashboardViewMaritime enregistrée")
        
        # Test étape 3: Navigation initiale
        print("\n📋 ÉTAPE 3: Navigation initiale")
        print("-" * 30)
        print("🔄 Changement vers 'welcome'...")
        view_manager.switch_to_view('welcome')
        print("✅ Navigation vers 'welcome' réussie")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur test étape par étape: {e}")
        traceback.print_exc()
        return False

def main():
    """Point d'entrée principal"""
    print("🎯 DIAGNOSTIC TRÈS APPROFONDI DES VUES")
    print("=" * 50)
    
    tests = [
        test_welcome_view_import,
        test_dashboard_view_import,
        test_welcome_view_creation,
        test_dashboard_view_creation,
        test_view_manager_creation,
        test_view_registration,
        test_view_switching,
        test_create_and_register_views_step_by_step
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
        print("✅ _create_and_register_views devrait fonctionner")
        return 0
    else:
        print("\n⚠️ CERTAINS TESTS ONT ÉCHOUÉ")
        print("❌ Problème identifié dans les vues")
        return 1

if __name__ == "__main__":
    exit(main()) 