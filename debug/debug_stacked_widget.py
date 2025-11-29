#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de diagnostic simple pour le problème d'écran vierge CHNeoWave
"""

import sys
from pathlib import Path

# Ajouter le répertoire src au PYTHONPATH
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from PySide6.QtWidgets import QApplication

def main():
    print("=== DIAGNOSTIC ÉCRAN VIERGE CHNeoWave ===")
    
    # Créer QApplication
    app = QApplication([])
    
    try:
        # Simuler le processus de main.py
        from PySide6.QtWidgets import QStackedWidget
        from hrneowave.gui.view_manager import get_view_manager
        
        # Créer QStackedWidget et ViewManager
        stacked_widget = QStackedWidget()
        view_manager = get_view_manager(stacked_widget)
        
        print(f"StackedWidget count (initial): {stacked_widget.count()}")
        print(f"Current index (initial): {stacked_widget.currentIndex()}")
        
        # Enregistrer une vue comme dans main.py
        from hrneowave.gui.views.dashboard_view import DashboardView
        dashboard_view = DashboardView()
        view_manager.register_view("dashboard", dashboard_view)
        
        print(f"\nAprès enregistrement dashboard:")
        print(f"StackedWidget count: {stacked_widget.count()}")
        print(f"Current index: {stacked_widget.currentIndex()}")
        print(f"Current widget: {stacked_widget.currentWidget()}")
        print(f"Dashboard widget: {dashboard_view}")
        print(f"Widget at index 0: {stacked_widget.widget(0)}")
        
        # Tenter de changer vers dashboard
        result = view_manager.switch_to_view('dashboard')
        print(f"\nswitch_to_view('dashboard') result: {result}")
        print(f"Current index après switch: {stacked_widget.currentIndex()}")
        print(f"Current widget après switch: {stacked_widget.currentWidget()}")
        
        # Vérifier si le widget est visible
        current_widget = stacked_widget.currentWidget()
        if current_widget:
            print(f"Widget visible: {current_widget.isVisible()}")
            print(f"Widget size: {current_widget.size()}")
            print(f"Widget minimum size: {current_widget.minimumSize()}")
            print(f"Widget style sheet: {current_widget.styleSheet()[:100]}...")
        
        print("\n=== DIAGNOSTIC TERMINÉ ===")
        
    except Exception as e:
        print(f"Erreur lors du diagnostic: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()