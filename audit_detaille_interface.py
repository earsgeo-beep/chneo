#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Audit détaillé des problèmes d'affichage de l'interface CHNeoWave
"""

import sys
import traceback
import os
from pathlib import Path

# Ajouter le chemin du projet
sys.path.insert(0, str(Path(__file__).parent / "src"))

def audit_qt_installation():
    """Audit de l'installation Qt"""
    print("🔍 AUDIT INSTALLATION QT")
    print("=" * 50)
    
    try:
        # Test PySide6
        print("🔄 Test import PySide6...")
        from PySide6.QtWidgets import QApplication, QMainWindow, QLabel
        from PySide6.QtCore import Qt, QTimer
        print("✅ PySide6 importé avec succès")
        
        # Test création QApplication
        print("🔄 Test création QApplication...")
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
            print("✅ QApplication créé")
        else:
            print("✅ QApplication existant trouvé")
        
        # Test fenêtre simple
        print("🔄 Test fenêtre simple...")
        window = QMainWindow()
        window.setWindowTitle("Test Audit Qt")
        window.resize(400, 300)
        window.show()
        
        visible = window.isVisible()
        print(f"✅ Fenêtre simple visible: {visible}")
        
        if visible:
            print("🎉 SUCCÈS: Qt fonctionne correctement")
            window.close()
            return True
        else:
            print("❌ PROBLÈME: Fenêtre simple non visible")
            return False
            
    except Exception as e:
        print(f"❌ Erreur Qt: {e}")
        traceback.print_exc()
        return False

def audit_mainwindow_construction():
    """Audit de la construction de MainWindow"""
    print("\n🔍 AUDIT CONSTRUCTION MAINWINDOW")
    print("=" * 50)
    
    try:
        from PySide6.QtWidgets import QApplication
        
        # Créer QApplication
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        print("✅ QApplication prêt")
        
        # Test import MainWindow
        print("🔄 Test import MainWindow...")
        from hrneowave.gui.main_window import MainWindow
        print("✅ MainWindow importé")
        
        # Test création étape par étape
        print("🔄 Test création MainWindow...")
        
        # Créer MainWindow avec debug
        main_window = MainWindow()
        print("✅ MainWindow créée")
        
        # Test propriétés de base
        print(f"✅ Géométrie: {main_window.geometry()}")
        print(f"✅ Visible: {main_window.isVisible()}")
        print(f"✅ Titre: {main_window.windowTitle()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur construction MainWindow: {e}")
        traceback.print_exc()
        return False

def audit_views_creation():
    """Audit de la création des vues"""
    print("\n🔍 AUDIT CRÉATION VUES")
    print("=" * 50)
    
    try:
        from PySide6.QtWidgets import QApplication
        
        # Créer QApplication
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # Test import des vues
        print("🔄 Test import WelcomeView...")
        from hrneowave.gui.views.welcome_view import WelcomeView
        print("✅ WelcomeView importé")
        
        print("🔄 Test création WelcomeView...")
        welcome_view = WelcomeView()
        print("✅ WelcomeView créée")
        
        print("🔄 Test import DashboardViewMaritime...")
        from hrneowave.gui.views.dashboard_view import DashboardViewMaritime
        print("✅ DashboardViewMaritime importé")
        
        print("🔄 Test création DashboardViewMaritime...")
        dashboard_view = DashboardViewMaritime()
        print("✅ DashboardViewMaritime créée")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur création vues: {e}")
        traceback.print_exc()
        return False

def audit_theme_manager():
    """Audit du gestionnaire de thème"""
    print("\n🔍 AUDIT GESTIONNAIRE THÈME")
    print("=" * 50)
    
    try:
        from PySide6.QtWidgets import QApplication
        
        # Créer QApplication
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        print("🔄 Test import ThemeManager...")
        from hrneowave.gui.styles.theme_manager import ThemeManager
        print("✅ ThemeManager importé")
        
        print("🔄 Test création ThemeManager...")
        theme_manager = ThemeManager(app=app)
        print("✅ ThemeManager créé")
        
        print("🔄 Test application thème...")
        theme_manager.apply_theme('maritime_modern')
        print("✅ Thème appliqué")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur ThemeManager: {e}")
        traceback.print_exc()
        return False

def audit_view_manager():
    """Audit du gestionnaire de vues"""
    print("\n🔍 AUDIT GESTIONNAIRE VUES")
    print("=" * 50)
    
    try:
        from PySide6.QtWidgets import QApplication
        
        # Créer QApplication
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        print("🔄 Test import ViewManager...")
        from hrneowave.gui.view_manager import ViewManager
        print("✅ ViewManager importé")
        
        print("🔄 Test création ViewManager...")
        view_manager = ViewManager()
        print("✅ ViewManager créé")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur ViewManager: {e}")
        traceback.print_exc()
        return False

def audit_event_loop():
    """Audit de la boucle d'événements"""
    print("\n🔍 AUDIT BOUCLE ÉVÉNEMENTS")
    print("=" * 50)
    
    try:
        from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
        from PySide6.QtCore import Qt, QTimer
        
        # Créer QApplication
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        print("✅ QApplication créé")
        
        # Créer fenêtre de test
        window = QMainWindow()
        window.setWindowTitle("Test Boucle Événements")
        window.resize(500, 400)
        
        # Widget central
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        
        # Label de test
        label = QLabel("Test Boucle Événements - CHNeoWave")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-size: 18px; color: blue;")
        layout.addWidget(label)
        
        window.setCentralWidget(central_widget)
        
        print("✅ Fenêtre de test créée")
        
        # Afficher la fenêtre
        window.show()
        window.raise_()
        window.activateWindow()
        
        visible = window.isVisible()
        print(f"✅ Fenêtre visible: {visible}")
        
        if visible:
            print("🎉 SUCCÈS: Fenêtre visible, test boucle d'événements...")
            
            # Timer pour fermer après 5 secondes
            timer = QTimer()
            timer.timeout.connect(app.quit)
            timer.start(5000)
            
            print("🔄 Lancement boucle d'événements (5 secondes)...")
            exit_code = app.exec()
            print(f"✅ Boucle d'événements terminée (code: {exit_code})")
            return True
        else:
            print("❌ PROBLÈME: Fenêtre non visible")
            return False
            
    except Exception as e:
        print(f"❌ Erreur boucle d'événements: {e}")
        traceback.print_exc()
        return False

def audit_mainwindow_events():
    """Audit de MainWindow avec boucle d'événements"""
    print("\n🔍 AUDIT MAINWINDOW ÉVÉNEMENTS")
    print("=" * 50)
    
    try:
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import QTimer
        
        # Créer QApplication
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        print("✅ QApplication créé")
        
        # Test import MainWindow
        print("🔄 Test import MainWindow...")
        from hrneowave.gui.main_window import MainWindow
        print("✅ MainWindow importé")
        
        # Test création MainWindow
        print("🔄 Test création MainWindow...")
        main_window = MainWindow()
        print("✅ MainWindow créée")
        
        # Configuration
        main_window.setWindowTitle("CHNeoWave - Audit Événements")
        main_window.resize(1000, 700)
        
        print("✅ MainWindow configurée")
        
        # Test affichage
        print("🔄 Test affichage MainWindow...")
        main_window.show()
        main_window.raise_()
        main_window.activateWindow()
        
        visible = main_window.isVisible()
        print(f"✅ MainWindow visible: {visible}")
        
        if visible:
            print("🎉 SUCCÈS: MainWindow visible, test boucle d'événements...")
            
            # Timer pour fermer après 10 secondes
            timer = QTimer()
            timer.timeout.connect(app.quit)
            timer.start(10000)
            
            print("🔄 Lancement boucle d'événements (10 secondes)...")
            exit_code = app.exec()
            print(f"✅ Boucle d'événements terminée (code: {exit_code})")
            return True
        else:
            print("❌ PROBLÈME: MainWindow non visible")
            return False
            
    except Exception as e:
        print(f"❌ Erreur MainWindow événements: {e}")
        traceback.print_exc()
        return False

def audit_file_structure():
    """Audit de la structure des fichiers"""
    print("\n🔍 AUDIT STRUCTURE FICHIERS")
    print("=" * 50)
    
    try:
        # Vérifier les fichiers critiques
        critical_files = [
            "src/hrneowave/gui/main_window.py",
            "src/hrneowave/gui/views/welcome_view.py",
            "src/hrneowave/gui/views/dashboard_view.py",
            "src/hrneowave/gui/view_manager.py",
            "src/hrneowave/gui/styles/theme_manager.py",
            "main.py",
            "main_final.py"
        ]
        
        for file_path in critical_files:
            if Path(file_path).exists():
                size = Path(file_path).stat().st_size
                print(f"✅ {file_path} - {size} bytes")
            else:
                print(f"❌ {file_path} - MANQUANT")
        
        # Vérifier les logs
        log_file = "src/hrneowave/chneowave_debug.log"
        if Path(log_file).exists():
            size = Path(log_file).stat().st_size
            print(f"✅ {log_file} - {size} bytes")
        else:
            print(f"⚠️ {log_file} - MANQUANT")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur audit fichiers: {e}")
        return False

def audit_system_info():
    """Audit des informations système"""
    print("\n🔍 AUDIT INFORMATIONS SYSTÈME")
    print("=" * 50)
    
    try:
        import platform
        import sys
        
        print(f"✅ Système: {platform.system()}")
        print(f"✅ Version: {platform.version()}")
        print(f"✅ Architecture: {platform.architecture()}")
        print(f"✅ Python: {sys.version}")
        print(f"✅ Répertoire: {os.getcwd()}")
        
        # Vérifier l'environnement virtuel
        if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            print("✅ Environnement virtuel: ACTIF")
        else:
            print("⚠️ Environnement virtuel: NON DÉTECTÉ")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur audit système: {e}")
        return False

def main():
    """Point d'entrée principal de l'audit"""
    print("🔍 AUDIT DÉTAILLÉ CHNEOWAVE")
    print("=" * 60)
    print("Analyse complète des problèmes d'affichage de l'interface")
    print("=" * 60)
    
    results = {}
    
    # Audit système
    results['system'] = audit_system_info()
    
    # Audit fichiers
    results['files'] = audit_file_structure()
    
    # Audit Qt
    results['qt'] = audit_qt_installation()
    
    # Audit composants
    results['theme'] = audit_theme_manager()
    results['view_manager'] = audit_view_manager()
    results['views'] = audit_views_creation()
    results['mainwindow'] = audit_mainwindow_construction()
    
    # Audit événements
    results['events'] = audit_event_loop()
    results['mainwindow_events'] = audit_mainwindow_events()
    
    # Résumé
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ DE L'AUDIT")
    print("=" * 60)
    
    for test, result in results.items():
        status = "✅ SUCCÈS" if result else "❌ ÉCHEC"
        print(f"{test.upper():20} : {status}")
    
    success_count = sum(results.values())
    total_count = len(results)
    
    print(f"\n📈 RÉSULTATS: {success_count}/{total_count} tests réussis")
    
    if success_count == total_count:
        print("🎉 TOUS LES TESTS RÉUSSIS - CHNeoWave devrait fonctionner !")
    elif success_count >= total_count * 0.8:
        print("⚠️ LA PLUPART DES TESTS RÉUSSIS - Problème mineur détecté")
    else:
        print("❌ NOMBREUX PROBLÈMES DÉTECTÉS - Intervention nécessaire")
    
    return 0

if __name__ == "__main__":
    exit(main()) 