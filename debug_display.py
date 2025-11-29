#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de diagnostic pour identifier pourquoi CHNeoWave ne s'affiche pas
"""

import sys
import logging
import time
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont

# Configuration logging simple
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
log = logging.getLogger(__name__)

def test_simple_window():
    """Test avec une fenêtre Qt simple"""
    print("🧪 TEST 1: Fenêtre Qt simple")
    print("=" * 40)
    
    app = QApplication(sys.argv)
    
    # Fenêtre simple
    window = QMainWindow()
    window.setWindowTitle("Test CHNeoWave - Fenêtre Simple")
    window.setGeometry(200, 200, 600, 400)
    
    # Widget central simple
    central_widget = QWidget()
    layout = QVBoxLayout(central_widget)
    
    # Labels de test
    title = QLabel("CHNeoWave - Test d'Affichage")
    title.setAlignment(Qt.AlignCenter)
    title.setFont(QFont("Arial", 24, QFont.Bold))
    title.setStyleSheet("color: #1565C0; padding: 20px;")
    
    status = QLabel("✅ Si vous voyez cette fenêtre, Qt fonctionne correctement!")
    status.setAlignment(Qt.AlignCenter)
    status.setFont(QFont("Arial", 14))
    status.setStyleSheet("color: #2E7D32; padding: 10px;")
    
    info = QLabel("Cette fenêtre va se fermer automatiquement dans 15 secondes...")
    info.setAlignment(Qt.AlignCenter)
    info.setFont(QFont("Arial", 12))
    info.setStyleSheet("color: #666; padding: 10px;")
    
    layout.addWidget(title)
    layout.addWidget(status)
    layout.addWidget(info)
    
    window.setCentralWidget(central_widget)
    
    # Forcer l'affichage
    window.show()
    window.raise_()
    window.activateWindow()
    
    print(f"✅ Fenêtre créée - Visible: {window.isVisible()}")
    print(f"✅ Position: {window.pos()}")
    print(f"✅ Taille: {window.size()}")
    print(f"✅ Active: {window.isActiveWindow()}")
    
    # Timer pour fermer automatiquement
    timer = QTimer()
    timer.timeout.connect(app.quit)
    timer.start(15000)  # 15 secondes
    
    print("🚀 Démarrage de la boucle d'événements...")
    print("👀 La fenêtre devrait être visible maintenant!")
    
    exit_code = app.exec()
    print(f"✅ Application fermée avec code: {exit_code}")
    return exit_code

def test_chneowave_imports():
    """Test des imports CHNeoWave"""
    print("\n🧪 TEST 2: Imports CHNeoWave")
    print("=" * 40)
    
    try:
        from hrneowave.core.logging_config import setup_logging
        setup_logging()
        print("✅ Logging configuré")
        
        from hrneowave.gui.styles.theme_manager import ThemeManager
        print("✅ ThemeManager importé")
        
        from hrneowave.gui.main_window import MainWindow
        print("✅ MainWindow importé")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur d'import: {e}")
        return False

def test_chneowave_window():
    """Test avec MainWindow CHNeoWave"""
    print("\n🧪 TEST 3: MainWindow CHNeoWave")
    print("=" * 40)
    
    if not test_chneowave_imports():
        print("❌ Impossible de continuer - Erreurs d'import")
        return 1
    
    try:
        from hrneowave.core.logging_config import setup_logging
        from hrneowave.gui.styles.theme_manager import ThemeManager
        from hrneowave.gui.main_window import MainWindow
        
        app = QApplication(sys.argv)
        
        # ThemeManager
        theme_manager = ThemeManager(app)
        theme_manager.apply_theme('maritime_modern')
        print("✅ Thème appliqué")
        
        # MainWindow
        main_window = MainWindow()
        print("✅ MainWindow créée")
        
        # Forcer l'affichage
        main_window.show()
        main_window.raise_()
        main_window.activateWindow()
        
        print(f"✅ MainWindow - Visible: {main_window.isVisible()}")
        print(f"✅ Position: {main_window.pos()}")
        print(f"✅ Taille: {main_window.size()}")
        
        # Timer pour fermer automatiquement
        timer = QTimer()
        timer.timeout.connect(app.quit)
        timer.start(15000)  # 15 secondes
        
        print("🚀 Démarrage de la boucle d'événements CHNeoWave...")
        print("👀 L'interface CHNeoWave devrait être visible!")
        
        exit_code = app.exec()
        print(f"✅ CHNeoWave fermé avec code: {exit_code}")
        return exit_code
        
    except Exception as e:
        print(f"❌ Erreur CHNeoWave: {e}")
        import traceback
        traceback.print_exc()
        return 1

def main():
    """Exécute tous les tests de diagnostic"""
    print("🔍 DIAGNOSTIC AFFICHAGE CHNEOWAVE")
    print("=" * 50)
    print("Ce script va tester l'affichage étape par étape...")
    print("=" * 50)
    
    # Test 1: Fenêtre Qt simple
    result1 = test_simple_window()
    
    if result1 != 0:
        print("❌ ÉCHEC: Problème avec Qt de base")
        return 1
    
    print("\n⏳ Pause de 2 secondes...")
    time.sleep(2)
    
    # Test 2: MainWindow CHNeoWave
    result2 = test_chneowave_window()
    
    if result2 != 0:
        print("❌ ÉCHEC: Problème avec CHNeoWave")
        return 1
    
    print("\n🎉 SUCCÈS: Tous les tests d'affichage ont réussi!")
    print("✅ Qt fonctionne correctement")
    print("✅ CHNeoWave s'affiche correctement")
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)