#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Diagnostic spécifique pour le problème de visibilité de fenêtre CHNeoWave
"""

import sys
from pathlib import Path

# Ajouter le chemin du projet
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_window_visibility():
    """Test spécifique de la visibilité de fenêtre"""
    print("🔍 DIAGNOSTIC VISIBILITÉ FENÊTRE")
    print("=" * 50)
    
    try:
        from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
        from PySide6.QtCore import Qt, QTimer
        from hrneowave.gui.main_window import MainWindow
        from hrneowave.gui.styles.theme_manager import ThemeManager
        
        # Créer QApplication
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
            app.setApplicationName("CHNeoWave Debug")
            print("✅ QApplication créé")
        else:
            print("✅ QApplication existant réutilisé")
        
        # Test 1: Fenêtre simple pour vérifier Qt
        print("\n🧪 TEST 1: Fenêtre Simple")
        print("-" * 30)
        
        simple_window = QMainWindow()
        simple_window.setWindowTitle("Test Simple")
        simple_window.setGeometry(100, 100, 300, 200)
        
        label = QLabel("Test de visibilité")
        label.setAlignment(Qt.AlignCenter)
        simple_window.setCentralWidget(label)
        
        simple_window.show()
        simple_window.raise_()
        simple_window.activateWindow()
        
        print(f"✅ Fenêtre simple visible: {simple_window.isVisible()}")
        print(f"✅ Position: {simple_window.pos()}")
        print(f"✅ Taille: {simple_window.size()}")
        
        # Test 2: MainWindow CHNeoWave
        print("\n🧪 TEST 2: MainWindow CHNeoWave")
        print("-" * 30)
        
        # Appliquer le thème
        theme_manager = ThemeManager(app)
        theme_manager.apply_theme('maritime_modern')
        print("✅ Thème appliqué")
        
        # Créer MainWindow
        main_window = MainWindow()
        print("✅ MainWindow créée")
        
        # Vérifications avant affichage
        print(f"✅ Avant show() - Visible: {main_window.isVisible()}")
        print(f"✅ Avant show() - Position: {main_window.pos()}")
        print(f"✅ Avant show() - Taille: {main_window.size()}")
        
        # Affichage
        main_window.show()
        print("✅ show() appelé")
        
        # Vérifications après show()
        print(f"✅ Après show() - Visible: {main_window.isVisible()}")
        print(f"✅ Après show() - Position: {main_window.pos()}")
        print(f"✅ Après show() - Taille: {main_window.size()}")
        
        # Forcer l'affichage
        main_window.raise_()
        main_window.activateWindow()
        print("✅ raise() et activateWindow() appelés")
        
        # Vérifications après raise()
        print(f"✅ Après raise() - Visible: {main_window.isVisible()}")
        print(f"✅ Après raise() - Position: {main_window.pos()}")
        print(f"✅ Après raise() - Taille: {main_window.size()}")
        
        # Test de maximisation si pas visible
        if not main_window.isVisible():
            print("⚠️ Fenêtre non visible, tentative de maximisation...")
            main_window.showMaximized()
            print(f"✅ Après showMaximized() - Visible: {main_window.isVisible()}")
        
        # Test de restauration si minimisée
        if main_window.isMinimized():
            print("⚠️ Fenêtre minimisée, tentative de restauration...")
            main_window.showNormal()
            print(f"✅ Après showNormal() - Visible: {main_window.isVisible()}")
        
        # Vérification finale
        visible = main_window.isVisible()
        active = main_window.isActiveWindow()
        minimized = main_window.isMinimized()
        
        print(f"\n📊 ÉTAT FINAL:")
        print(f"✅ Visible: {visible}")
        print(f"✅ Active: {active}")
        print(f"✅ Minimized: {minimized}")
        print(f"✅ Position: {main_window.pos()}")
        print(f"✅ Taille: {main_window.size()}")
        print(f"✅ Géométrie: {main_window.geometry()}")
        
        if visible:
            print("\n🎉 SUCCÈS: MainWindow est visible!")
            
            # Maintenir ouvert pour vérification visuelle
            timer = QTimer()
            timer.timeout.connect(app.quit)
            timer.start(5000)
            
            print("🔄 Maintien ouvert 5 secondes pour vérification...")
            exit_code = app.exec()
            print(f"✅ Test terminé (code: {exit_code})")
            return True
        else:
            print("\n❌ PROBLÈME: MainWindow n'est toujours pas visible")
            
            # Test de diagnostic supplémentaire
            print("\n🔍 DIAGNOSTIC SUPPLÉMENTAIRE:")
            
            # Vérifier si la fenêtre est en dehors de l'écran
            screen_geometry = app.primaryScreen().geometry()
            window_geometry = main_window.geometry()
            
            print(f"✅ Géométrie écran: {screen_geometry}")
            print(f"✅ Géométrie fenêtre: {window_geometry}")
            
            if not screen_geometry.intersects(window_geometry):
                print("⚠️ Fenêtre en dehors de l'écran!")
                # Centrer la fenêtre
                main_window.move(screen_geometry.center() - window_geometry.center())
                print("✅ Fenêtre centrée")
                main_window.show()
                
                if main_window.isVisible():
                    print("🎉 SUCCÈS: Fenêtre maintenant visible après centrage!")
                    return True
            
            return False
            
    except Exception as e:
        print(f"❌ Erreur critique: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_main_window_constructor():
    """Test du constructeur MainWindow"""
    print("\n🔍 TEST CONSTRUCTEUR MAINWINDOW")
    print("=" * 40)
    
    try:
        from PySide6.QtWidgets import QApplication
        from hrneowave.gui.main_window import MainWindow
        
        # Créer QApplication
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # Test création sans affichage
        main_window = MainWindow()
        print("✅ MainWindow créée")
        
        # Vérifications de base
        print(f"✅ Type: {type(main_window)}")
        print(f"✅ Classe: {main_window.__class__.__name__}")
        print(f"✅ Hérite de QMainWindow: {isinstance(main_window, QApplication.instance().activeWindow().__class__.__bases__[0]) if QApplication.instance().activeWindow() else 'N/A'}")
        
        # Vérifier les propriétés de base
        print(f"✅ WindowTitle: {main_window.windowTitle()}")
        print(f"✅ ObjectName: {main_window.objectName()}")
        print(f"✅ Enabled: {main_window.isEnabled()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur constructeur: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Point d'entrée principal"""
    print("🎯 DIAGNOSTIC VISIBILITÉ CHNEOWAVE")
    print("=" * 50)
    
    # Test constructeur d'abord
    if not test_main_window_constructor():
        print("❌ ÉCHEC: Problème avec le constructeur MainWindow")
        return 1
    
    # Test visibilité
    if not test_window_visibility():
        print("❌ ÉCHEC: Problème de visibilité de fenêtre")
        return 1
    
    print("\n🎉 SUCCÈS: Diagnostic terminé")
    return 0

if __name__ == "__main__":
    exit(main()) 