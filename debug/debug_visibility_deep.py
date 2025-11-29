#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Diagnostic approfondi du problème de visibilité
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget, QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import QTimer

def test_basic_stacked_widget():
    """Test basique d'un QStackedWidget"""
    print("\n=== TEST BASIQUE QStackedWidget ===")
    
    app = QApplication.instance() or QApplication(sys.argv)
    
    # Fenêtre principale simple
    main_window = QMainWindow()
    main_window.setWindowTitle("Test QStackedWidget")
    main_window.resize(800, 600)
    
    # Widget central
    central_widget = QWidget()
    main_window.setCentralWidget(central_widget)
    
    # Layout
    layout = QVBoxLayout(central_widget)
    
    # QStackedWidget
    stacked = QStackedWidget()
    layout.addWidget(stacked)
    
    # Widget de test simple
    test_widget = QWidget()
    test_widget.setStyleSheet("background-color: red; color: white;")
    test_layout = QVBoxLayout(test_widget)
    test_label = QLabel("WIDGET DE TEST VISIBLE")
    test_layout.addWidget(test_label)
    
    # Ajouter au stack
    stacked.addWidget(test_widget)
    stacked.setCurrentIndex(0)
    
    # Diagnostic avant show
    print(f"Avant show():")
    print(f"  - stacked.count(): {stacked.count()}")
    print(f"  - stacked.isVisible(): {stacked.isVisible()}")
    print(f"  - test_widget.isVisible(): {test_widget.isVisible()}")
    print(f"  - main_window.isVisible(): {main_window.isVisible()}")
    
    # Afficher la fenêtre
    main_window.show()
    
    # Diagnostic après show
    print(f"Après show():")
    print(f"  - stacked.count(): {stacked.count()}")
    print(f"  - stacked.isVisible(): {stacked.isVisible()}")
    print(f"  - test_widget.isVisible(): {test_widget.isVisible()}")
    print(f"  - main_window.isVisible(): {main_window.isVisible()}")
    
    # Forcer la visibilité
    stacked.setVisible(True)
    stacked.show()
    test_widget.setVisible(True)
    test_widget.show()
    
    print(f"Après forçage:")
    print(f"  - stacked.isVisible(): {stacked.isVisible()}")
    print(f"  - test_widget.isVisible(): {test_widget.isVisible()}")
    
    # Timer pour fermer
    QTimer.singleShot(3000, app.quit)
    
    return app.exec()

def test_chneowave_structure():
    """Test avec la structure CHNeoWave"""
    print("\n=== TEST STRUCTURE CHNEOWAVE ===")
    
    app = QApplication.instance() or QApplication(sys.argv)
    
    # Import des modules CHNeoWave
    from src.hrneowave.gui.views.dashboard_view import DashboardView
    from src.hrneowave.gui.view_manager import get_view_manager
    from src.hrneowave.gui.theme import get_stylesheet
    
    # Fenêtre principale
    main_window = QMainWindow()
    main_window.setWindowTitle("Test CHNeoWave Structure")
    main_window.resize(800, 600)
    main_window.setStyleSheet(get_stylesheet())
    
    # Widget central
    central_widget = QWidget()
    main_window.setCentralWidget(central_widget)
    
    # Layout
    layout = QVBoxLayout(central_widget)
    layout.setContentsMargins(0, 0, 0, 0)
    
    # QStackedWidget
    stacked = QStackedWidget()
    layout.addWidget(stacked)
    
    # ViewManager
    view_manager = get_view_manager(stacked)
    
    # Créer et enregistrer WelcomeView
    dashboard_view = DashboardView()
    view_manager.register_view("dashboard", dashboard_view)
    
    print(f"Après register_view:")
    print(f"  - stacked.count(): {stacked.count()}")
    print(f"  - stacked.currentIndex(): {stacked.currentIndex()}")
    print(f"  - stacked.currentWidget(): {stacked.currentWidget()}")
    
    # Changer vers welcome
    success = view_manager.switch_to_view("welcome")
    print(f"switch_to_view success: {success}")
    
    print(f"Après switch_to_view:")
    print(f"  - stacked.currentIndex(): {stacked.currentIndex()}")
    print(f"  - stacked.currentWidget(): {stacked.currentWidget()}")
    print(f"  - dashboard_view.isVisible(): {dashboard_view.isVisible()}")
    
    # Afficher la fenêtre
    main_window.show()
    
    print(f"Après main_window.show():")
    print(f"  - main_window.isVisible(): {main_window.isVisible()}")
    print(f"  - stacked.isVisible(): {stacked.isVisible()}")
    print(f"  - welcome_view.isVisible(): {welcome_view.isVisible()}")
    
    # Forcer la visibilité explicitement
    stacked.setVisible(True)
    stacked.show()
    dashboard_view.setVisible(True)
    dashboard_view.show()
    stacked.update()
    dashboard_view.update()
    
    print(f"Après forçage explicite:")
    print(f"  - stacked.isVisible(): {stacked.isVisible()}")
    print(f"  - welcome_view.isVisible(): {welcome_view.isVisible()}")
    
    # Timer pour fermer
    QTimer.singleShot(5000, app.quit)
    
    return app.exec()

if __name__ == "__main__":
    print("🔍 Diagnostic approfondi de visibilité")
    
    # Test 1: QStackedWidget basique
    result1 = test_basic_stacked_widget()
    print(f"Test basique terminé avec code: {result1}")
    
    # Test 2: Structure CHNeoWave
    result2 = test_chneowave_structure()
    print(f"Test CHNeoWave terminé avec code: {result2}")
    
    print("\n✅ Diagnostic terminé")