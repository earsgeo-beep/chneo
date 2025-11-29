#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Diagnostic Affichage Forcé - CHNeoWave
Force l'affichage de la MainWindow et diagnostique les problèmes de visibilité
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QScreen

def diagnostic_affichage_force():
    """Diagnostic complet de l'affichage avec forçage"""
    print("=== DIAGNOSTIC AFFICHAGE FORCÉ CHNeoWave ===")
    print("🎯 OBJECTIF: Forcer l'affichage et diagnostiquer la visibilité")
    
    app = QApplication(sys.argv)
    print(f"✅ QApplication créée sur plateforme: {app.platformName()}")
    
    # Diagnostic des écrans
    screens = app.screens()
    print(f"\n📺 ÉCRANS DISPONIBLES: {len(screens)}")
    for i, screen in enumerate(screens):
        print(f"  Écran {i}: {screen.name()} - Géométrie: {screen.geometry()}")
        print(f"           DPI: {screen.logicalDotsPerInch()} - Facteur d'échelle: {screen.devicePixelRatio()}")
    
    try:
        # Import et création MainWindow
        print("\n🔍 Import et création MainWindow CHNeoWave...")
        from hrneowave.gui.main_window import MainWindow
        
        window = MainWindow()
        print("✅ MainWindow CHNeoWave créée")
        
        # Diagnostic initial
        print("\n=== DIAGNOSTIC INITIAL ===")
        print(f"📋 Titre: {window.windowTitle()}")
        print(f"📐 Géométrie: {window.geometry()}")
        print(f"👁️ Visible: {window.isVisible()}")
        print(f"🎯 Actif: {window.isActiveWindow()}")
        print(f"🖥️ Écran: {window.screen().name() if window.screen() else 'Aucun'}")
        print(f"🔧 État fenêtre: {window.windowState()}")
        print(f"📏 Taille minimale: {window.minimumSize()}")
        print(f"📏 Taille maximale: {window.maximumSize()}")
        
        # FORÇAGE AFFICHAGE MULTIPLE
        print("\n🔧 FORÇAGE AFFICHAGE MULTIPLE...")
        
        # Étape 1: Configuration forcée
        window.setWindowTitle("CHNeoWave - DIAGNOSTIC FORCÉ")
        window.setGeometry(100, 100, 1200, 800)
        window.setMinimumSize(800, 600)
        
        # Étape 2: Flags de fenêtre
        window.setWindowFlags(Qt.Window | Qt.WindowTitleHint | Qt.WindowCloseButtonHint | Qt.WindowMinMaxButtonsHint)
        
        # Étape 3: Affichage forcé multiple
        window.show()
        print("✅ show() appelé")
        
        window.raise_()
        print("✅ raise_() appelé")
        
        window.activateWindow()
        print("✅ activateWindow() appelé")
        
        # Étape 4: Forcer au premier plan
        window.setWindowState(Qt.WindowActive)
        window.setAttribute(Qt.WA_ShowWithoutActivating, False)
        
        # Étape 5: Repositionnement forcé
        primary_screen = app.primaryScreen()
        if primary_screen:
            screen_geometry = primary_screen.geometry()
            center_x = screen_geometry.center().x() - 600
            center_y = screen_geometry.center().y() - 400
            window.move(center_x, center_y)
            print(f"✅ Repositionné au centre: ({center_x}, {center_y})")
        
        # Diagnostic après forçage
        print("\n=== DIAGNOSTIC APRÈS FORÇAGE ===")
        print(f"📋 Titre: {window.windowTitle()}")
        print(f"📐 Géométrie: {window.geometry()}")
        print(f"👁️ Visible: {window.isVisible()}")
        print(f"🎯 Actif: {window.isActiveWindow()}")
        print(f"🖥️ Écran: {window.screen().name() if window.screen() else 'Aucun'}")
        print(f"🔧 État fenêtre: {window.windowState()}")
        print(f"📍 Position: ({window.x()}, {window.y()})")
        print(f"📏 Taille: {window.width()}x{window.height()}")
        
        # Test de capture d'écran
        try:
            pixmap = window.grab()
            if not pixmap.isNull():
                pixmap.save("diagnostic_affichage_capture.png")
                print("✅ Capture d'écran sauvegardée: diagnostic_affichage_capture.png")
            else:
                print("❌ Capture d'écran échouée: pixmap null")
        except Exception as e:
            print(f"❌ Erreur capture d'écran: {e}")
        
        # Test de repaint forcé
        window.repaint()
        window.update()
        app.processEvents()
        print("✅ Repaint et update forcés")
        
        # Message de diagnostic final
        def show_diagnostic_final():
            if window.isVisible():
                msg = QMessageBox()
                msg.setWindowTitle("CHNeoWave - Diagnostic Affichage")
                msg.setText(f"🔍 DIAGNOSTIC AFFICHAGE:\n\n"
                           f"✅ Fenêtre visible: {window.isVisible()}\n"
                           f"✅ Fenêtre active: {window.isActiveWindow()}\n"
                           f"✅ Géométrie: {window.geometry()}\n"
                           f"✅ Position: ({window.x()}, {window.y()})\n"
                           f"✅ Taille: {window.width()}x{window.height()}\n\n"
                           f"La fenêtre devrait être visible à l'écran !")
                msg.setIcon(QMessageBox.Information)
                msg.exec()
            else:
                print("❌ PROBLÈME: Fenêtre toujours invisible après forçage")
                print("🔍 Causes possibles:")
                print("   - Problème de pilote graphique")
                print("   - Fenêtre hors écran")
                print("   - Problème de gestionnaire de fenêtres")
                print("   - Conflit avec d'autres applications")
            
            app.quit()
        
        # Timer pour diagnostic final
        timer = QTimer()
        timer.timeout.connect(show_diagnostic_final)
        timer.start(5000)  # 5 secondes
        
        print("\n⏰ Affichage pendant 5 secondes puis diagnostic final")
        print("🔍 Vérifiez si la fenêtre CHNeoWave est visible à l'écran")
        
        return app.exec()
        
    except Exception as e:
        print(f"❌ ERREUR CRITIQUE: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    result = diagnostic_affichage_force()
    print(f"\n🏁 Diagnostic terminé avec code: {result}")
    
    if result == 0:
        print("✅ Diagnostic réussi - Vérifiez la visibilité")
    else:
        print("❌ Problème détecté - Consultez les logs")
    
    sys.exit(result)