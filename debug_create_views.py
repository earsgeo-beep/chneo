#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Diagnostic spécifique du problème dans _create_and_register_views
"""

import sys
import traceback
from pathlib import Path

# Ajouter le chemin du projet
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_views_imports():
    """Test des imports des vues"""
    print("🔍 TEST IMPORTS DES VUES")
    print("=" * 40)
    
    try:
        # Test import des vues principales
        print("🔄 Import WelcomeView...")
        from hrneowave.gui.views import WelcomeView
        print("✅ WelcomeView importé")
        
        print("🔄 Import DashboardViewMaritime...")
        from hrneowave.gui.views import DashboardViewMaritime
        print("✅ DashboardViewMaritime importé")
        
        # Test import des fonctions de chargement
        print("🔄 Import des fonctions de chargement...")
        from hrneowave.gui.views import (
            get_calibration_view,
            get_acquisition_view,
            get_analysis_view,
            get_export_view,
            get_settings_view
        )
        print("✅ Fonctions de chargement importées")
        
        # Test import des configurations
        print("🔄 Import des configurations...")
        from hrneowave.gui.views import VIEWS_CONFIG, NAVIGATION_ORDER
        print("✅ Configurations importées")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur imports vues: {e}")
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
        
        print("✅ QApplication créé")
        
        # Test création WelcomeView
        print("🔄 Création WelcomeView...")
        from hrneowave.gui.views import WelcomeView
        welcome_view = WelcomeView(parent=None)
        print("✅ WelcomeView créée")
        
        # Test création DashboardViewMaritime
        print("🔄 Création DashboardViewMaritime...")
        from hrneowave.gui.views import DashboardViewMaritime
        dashboard_view = DashboardViewMaritime(parent=None)
        print("✅ DashboardViewMaritime créée")
        
        # Test création vues avec lazy loading
        print("🔄 Test vues avec lazy loading...")
        from hrneowave.gui.views import (
            get_calibration_view,
            get_acquisition_view,
            get_analysis_view,
            get_export_view,
            get_settings_view
        )
        
        try:
            calibration_view = get_calibration_view(parent=None)
            print("✅ CalibrationView créée")
        except Exception as e:
            print(f"❌ Erreur CalibrationView: {e}")
        
        try:
            acquisition_view = get_acquisition_view(parent=None)
            print("✅ AcquisitionView créée")
        except Exception as e:
            print(f"❌ Erreur AcquisitionView: {e}")
        
        try:
            analysis_view = get_analysis_view(parent=None)
            print("✅ AnalysisView créée")
        except Exception as e:
            print(f"❌ Erreur AnalysisView: {e}")
        
        try:
            export_view = get_export_view(parent=None)
            print("✅ ExportView créée")
        except Exception as e:
            print(f"❌ Erreur ExportView: {e}")
        
        try:
            settings_view = get_settings_view(parent=None)
            print("✅ SettingsView créée")
        except Exception as e:
            print(f"❌ Erreur SettingsView: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur création vues: {e}")
        traceback.print_exc()
        return False

def test_view_manager():
    """Test du ViewManager"""
    print("\n🔍 TEST VIEW MANAGER")
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
        
        # Test enregistrement de vue
        print("🔄 Test enregistrement de vue...")
        from hrneowave.gui.views import WelcomeView
        welcome_view = WelcomeView(parent=None)
        view_manager.register_view('welcome', welcome_view)
        print("✅ Vue enregistrée")
        
        # Test changement de vue
        print("🔄 Test changement de vue...")
        view_manager.switch_to_view('welcome')
        print("✅ Changement de vue réussi")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur ViewManager: {e}")
        traceback.print_exc()
        return False

def test_create_and_register_views_step_by_step():
    """Test de _create_and_register_views étape par étape"""
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
        from hrneowave.gui.views import WelcomeView
        welcome_view = WelcomeView(parent=None)
        print("✅ WelcomeView créée")
        view_manager.register_view('welcome', welcome_view)
        print("✅ WelcomeView enregistrée")
        
        # Test étape 2: DashboardViewMaritime
        print("\n📋 ÉTAPE 2: DashboardViewMaritime")
        print("-" * 30)
        from hrneowave.gui.views import DashboardViewMaritime
        dashboard_view = DashboardViewMaritime(parent=None)
        print("✅ DashboardViewMaritime créée")
        view_manager.register_view('dashboard', dashboard_view)
        print("✅ DashboardViewMaritime enregistrée")
        
        # Test étape 3: Vues avec lazy loading
        print("\n📋 ÉTAPE 3: Vues avec lazy loading")
        print("-" * 30)
        from hrneowave.gui.views import VIEWS_CONFIG
        
        for view_name, config in VIEWS_CONFIG.items():
            if 'loader' in config:
                print(f"🔄 Test {view_name}...")
                try:
                    view_instance = config['loader'](parent=None)
                    view_manager.register_view(view_name, view_instance)
                    print(f"✅ {view_name} créée et enregistrée")
                except Exception as e:
                    print(f"❌ Erreur {view_name}: {e}")
        
        # Test étape 4: Navigation initiale
        print("\n📋 ÉTAPE 4: Navigation initiale")
        print("-" * 30)
        view_manager.switch_to_view('welcome')
        print("✅ Navigation vers 'welcome' réussie")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur test étape par étape: {e}")
        traceback.print_exc()
        return False

def main():
    """Point d'entrée principal"""
    print("🎯 DIAGNOSTIC _CREATE_AND_REGISTER_VIEWS")
    print("=" * 50)
    
    tests = [
        test_views_imports,
        test_view_creation,
        test_view_manager,
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
        print("❌ Problème identifié dans _create_and_register_views")
        return 1

if __name__ == "__main__":
    exit(main()) 