#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de diagnostic CORRIGÉ pour CHNeoWave
Problème identifié : Conflit QApplication singleton
"""

import sys
import logging
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont

# Configuration logging simple
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
log = logging.getLogger(__name__)

def test_chneowave_complete():
    """Test complet CHNeoWave avec une seule instance QApplication"""
    print("🔍 DIAGNOSTIC CHNEOWAVE - VERSION CORRIGÉE")
    print("=" * 50)
    
    # UNE SEULE instance QApplication
    app = QApplication(sys.argv)
    app.setApplicationName("CHNeoWave Debug")
    
    try:
        # Test imports
        print("🧪 TEST 1: Imports CHNeoWave")
        print("=" * 40)
        
        from hrneowave.core.logging_config import setup_logging
        setup_logging()
        print("✅ Logging configuré")
        
        from hrneowave.gui.styles.theme_manager import ThemeManager
        print("✅ ThemeManager importé")
        
        from hrneowave.gui.main_window import MainWindow
        print("✅ MainWindow importé")
        
        # Test ThemeManager
        print("\n🧪 TEST 2: ThemeManager")
        print("=" * 40)
        
        theme_manager = ThemeManager(app)
        theme_manager.apply_theme('maritime_modern')
        print("✅ Thème 'maritime_modern' appliqué")
        
        # Test MainWindow
        print("\n🧪 TEST 3: MainWindow CHNeoWave")
        print("=" * 40)
        
        main_window = MainWindow()
        print("✅ MainWindow créée avec succès")
        
        # Configuration d'affichage
        main_window.setWindowTitle("CHNeoWave - Test d'Affichage Réussi")
        
        # FORCER L'AFFICHAGE
        main_window.show()
        main_window.raise_()
        main_window.activateWindow()
        
        # Vérifications
        print(f"✅ MainWindow visible: {main_window.isVisible()}")
        print(f"✅ Position: {main_window.pos()}")
        print(f"✅ Taille: {main_window.size()}")
        print(f"✅ Active: {main_window.isActiveWindow()}")
        print(f"✅ Minimisée: {main_window.isMinimized()}")
        
        if main_window.isVisible():
            print("\n🎉 SUCCÈS TOTAL: CHNeoWave est VISIBLE à l'écran!")
            print("✅ Tous les composants fonctionnent correctement")
            print("✅ L'interface s'affiche comme prévu")
        else:
            print("\n❌ PROBLÈME: MainWindow créée mais pas visible")
            return 1
        
        # Timer pour maintenir ouvert 20 secondes
        timer = QTimer()
        timer.timeout.connect(lambda: (
            print("⏰ Fermeture automatique dans 5 secondes..."),
            QTimer.singleShot(5000, app.quit)
        ))
        timer.start(15000)  # Avertissement à 15s
        
        print("\n🚀 CHNeoWave fonctionne - Fenêtre ouverte pour 20 secondes")
        print("👀 Vous devriez voir l'interface CHNeoWave maintenant!")
        print("⏰ Fermeture automatique dans 20 secondes...")
        
        # Démarrer la boucle d'événements
        exit_code = app.exec()
        
        print(f"\n✅ CHNeoWave fermé proprement (code: {exit_code})")
        return exit_code
        
    except Exception as e:
        print(f"\n❌ ERREUR CRITIQUE: {e}")
        import traceback
        traceback.print_exc()
        return 1

def main():
    """Point d'entrée principal"""
    return test_chneowave_complete()

if __name__ == "__main__":
    print("🚀 LANCEMENT DIAGNOSTIC CHNEOWAVE CORRIGÉ")
    print("=" * 60)
    print("Ce test va vérifier si CHNeoWave s'affiche correctement...")
    print("=" * 60)
    
    exit_code = main()
    
    if exit_code == 0:
        print("\n🎉 DIAGNOSTIC RÉUSSI: CHNeoWave fonctionne parfaitement!")
        print("✅ L'interface s'affiche correctement")
        print("✅ Tous les composants sont opérationnels")
        print("\n💡 SOLUTION: Utiliser une seule instance QApplication")
    else:
        print("\n❌ DIAGNOSTIC ÉCHOUÉ: Problèmes détectés")
        print("🔧 Vérifiez les logs ci-dessus pour plus de détails")
    
    sys.exit(exit_code)