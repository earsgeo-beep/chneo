#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de diagnostic détaillé pour identifier le point d'arrêt de CHNeoWave
"""

import sys
import logging
import traceback
from pathlib import Path

# Configuration logging détaillée
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
log = logging.getLogger(__name__)

def test_step_by_step():
    """Test étape par étape pour identifier le problème"""
    print("🔍 DIAGNOSTIC DÉTAILLÉ CHNEOWAVE")
    print("=" * 50)
    
    try:
        # Étape 1: Imports de base
        print("\n📋 ÉTAPE 1: Imports de base")
        print("-" * 30)
        
        from PySide6.QtWidgets import QApplication
        print("✅ QApplication importé")
        
        from PySide6.QtCore import Qt
        print("✅ Qt importé")
        
        # Étape 2: Configuration logging
        print("\n📋 ÉTAPE 2: Configuration logging")
        print("-" * 30)
        
        from hrneowave.core.logging_config import setup_logging
        setup_logging()
        print("✅ Logging configuré")
        
        # Étape 3: Création QApplication
        print("\n📋 ÉTAPE 3: Création QApplication")
        print("-" * 30)
        
        # Vérifier si QApplication existe déjà
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
            app.setApplicationName("CHNeoWave Debug")
            print("✅ QApplication créé")
        else:
            print("✅ QApplication existant réutilisé")
        
        # Étape 4: Test ThemeManager
        print("\n📋 ÉTAPE 4: Test ThemeManager")
        print("-" * 30)
        
        try:
            from hrneowave.gui.styles.theme_manager import ThemeManager
            print("✅ ThemeManager importé")
            
            theme_manager = ThemeManager(app)
            print("✅ ThemeManager instancié")
            
            # Test d'application de thème avec protection
            try:
                theme_manager.apply_theme('maritime_modern')
                print("✅ Thème appliqué")
            except Exception as e:
                print(f"⚠️ Erreur thème: {e}")
                # Continuer sans thème
                pass
            
        except Exception as e:
            print(f"❌ Erreur ThemeManager: {e}")
            traceback.print_exc()
            return False
        
        # Étape 5: Test imports des vues
        print("\n📋 ÉTAPE 5: Test imports des vues")
        print("-" * 30)
        
        try:
            from hrneowave.gui.views import WelcomeView, DashboardViewMaritime
            print("✅ Vues importées")
            
            from hrneowave.gui.widgets.main_sidebar import MainSidebar
            print("✅ MainSidebar importé")
            
            from hrneowave.gui.components.breadcrumbs import BreadcrumbsWidget
            print("✅ BreadcrumbsWidget importé")
            
        except Exception as e:
            print(f"❌ Erreur imports vues: {e}")
            traceback.print_exc()
            return False
        
        # Étape 6: Test ViewManager
        print("\n📋 ÉTAPE 6: Test ViewManager")
        print("-" * 30)
        
        try:
            from hrneowave.gui.view_manager import ViewManager
            print("✅ ViewManager importé")
            
            from PySide6.QtWidgets import QStackedWidget
            stacked_widget = QStackedWidget()
            view_manager = ViewManager(stacked_widget)
            print("✅ ViewManager créé")
            
        except Exception as e:
            print(f"❌ Erreur ViewManager: {e}")
            traceback.print_exc()
            return False
        
        # Étape 7: Test création widgets individuels
        print("\n📋 ÉTAPE 7: Test création widgets")
        print("-" * 30)
        
        try:
            # Test MainSidebar
            sidebar = MainSidebar()
            print("✅ MainSidebar créé")
            
            # Test BreadcrumbsWidget
            breadcrumbs = BreadcrumbsWidget()
            print("✅ BreadcrumbsWidget créé")
            
            # Test WelcomeView
            welcome_view = WelcomeView()
            print("✅ WelcomeView créé")
            
        except Exception as e:
            print(f"❌ Erreur création widgets: {e}")
            traceback.print_exc()
            return False
        
        # Étape 8: Test MainWindow
        print("\n📋 ÉTAPE 8: Test MainWindow")
        print("-" * 30)
        
        try:
            from hrneowave.gui.main_window import MainWindow
            print("✅ MainWindow importé")
            
            main_window = MainWindow()
            print("✅ MainWindow créé")
            
            # Test affichage
            main_window.show()
            print("✅ MainWindow affiché")
            
            # Vérifications
            visible = main_window.isVisible()
            active = main_window.isActiveWindow()
            minimized = main_window.isMinimized()
            
            print(f"✅ Vérifications: Visible={visible}, Active={active}, Minimized={minimized}")
            
            if visible:
                print("🎉 SUCCÈS: Interface visible!")
                
                # Fermer après 3 secondes
                from PySide6.QtCore import QTimer
                timer = QTimer()
                timer.timeout.connect(app.quit)
                timer.start(3000)
                
                print("🔄 Démarrage boucle d'événements...")
                exit_code = app.exec()
                print(f"✅ Application fermée (code: {exit_code})")
                return True
            else:
                print("❌ PROBLÈME: Interface non visible")
                return False
                
        except Exception as e:
            print(f"❌ Erreur MainWindow: {e}")
            traceback.print_exc()
            return False
            
    except Exception as e:
        print(f"❌ Erreur générale: {e}")
        traceback.print_exc()
        return False

def test_minimal_window():
    """Test avec une fenêtre minimale pour isoler le problème"""
    print("\n🧪 TEST FENÊTRE MINIMALE")
    print("=" * 40)
    
    try:
        from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
        from PySide6.QtCore import Qt, QTimer
        
        # Vérifier si QApplication existe déjà
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # Fenêtre simple
        window = QMainWindow()
        window.setWindowTitle("Test CHNeoWave - Minimal")
        window.setGeometry(200, 200, 400, 300)
        
        # Widget central
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        
        # Label de test
        label = QLabel("Test CHNeoWave - Interface Minimale")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        
        window.setCentralWidget(central_widget)
        
        # Affichage
        window.show()
        window.raise_()
        window.activateWindow()
        
        print(f"✅ Fenêtre minimale créée: Visible={window.isVisible()}")
        
        # Timer pour fermer
        timer = QTimer()
        timer.timeout.connect(app.quit)
        timer.start(2000)
        
        exit_code = app.exec()
        print(f"✅ Fenêtre minimale fermée (code: {exit_code})")
        return True
        
    except Exception as e:
        print(f"❌ Erreur fenêtre minimale: {e}")
        traceback.print_exc()
        return False

def main():
    """Point d'entrée principal"""
    print("🚀 DIAGNOSTIC DÉTAILLÉ CHNEOWAVE")
    print("=" * 50)
    
    # Ajouter le chemin du projet
    sys.path.insert(0, str(Path(__file__).parent / "src"))
    
    # Test fenêtre minimale d'abord
    if not test_minimal_window():
        print("❌ ÉCHEC: Fenêtre minimale ne fonctionne pas")
        return 1
    
    # Test étape par étape
    if not test_step_by_step():
        print("❌ ÉCHEC: Problème identifié dans les étapes")
        return 1
    
    print("\n🎉 SUCCÈS: Tous les tests passés!")
    return 0

if __name__ == "__main__":
    exit(main()) 