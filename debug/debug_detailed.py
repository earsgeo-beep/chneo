#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de diagnostic détaillé pour CHNeoWave - Problème écran vierge
"""

import sys
from pathlib import Path

# Ajouter le répertoire src au PYTHONPATH
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from PySide6.QtWidgets import QApplication, QStackedWidget
from PySide6.QtCore import Qt

def main():
    print("=== DIAGNOSTIC DÉTAILLÉ ÉCRAN VIERGE CHNeoWave ===")
    
    # Créer QApplication
    app = QApplication([])
    
    try:
        # Import après QApplication
        from hrneowave.gui.view_manager import get_view_manager
        from hrneowave.gui.views.dashboard_view import DashboardView
        
        # Créer un QStackedWidget
        stacked_widget = QStackedWidget()
        stacked_widget.setMinimumSize(800, 600)
        
        # Créer le ViewManager
        view_manager = get_view_manager(stacked_widget)
        
        print(f"1. QStackedWidget créé: {stacked_widget}")
        print(f"2. ViewManager créé: {view_manager}")
        
        # Créer et enregistrer la vue dashboard
        dashboard_view = DashboardView()
        print(f"3. DashboardView créée: {dashboard_view}")
        print(f"   - Taille: {dashboard_view.size()}")
        print(f"   - Visible: {dashboard_view.isVisible()}")
        print(f"   - Parent: {dashboard_view.parent()}")
        
        # Enregistrer la vue
        view_manager.register_view("dashboard", dashboard_view)
        print(f"4. Vue dashboard enregistrée")
        
        # Vérifier l'état du QStackedWidget
        print(f"5. État du QStackedWidget:")
        print(f"   - Nombre de widgets: {stacked_widget.count()}")
        print(f"   - Index courant: {stacked_widget.currentIndex()}")
        print(f"   - Widget courant: {stacked_widget.currentWidget()}")
        
        # Lister tous les widgets
        for i in range(stacked_widget.count()):
            widget = stacked_widget.widget(i)
            print(f"   - Widget {i}: {widget} (visible: {widget.isVisible()})")
        
        # Tenter de basculer vers dashboard
        result = view_manager.switch_to_view("dashboard")
        print(f"6. switch_to_view('dashboard') retourne: {result}")
        
        # Vérifier l'état après switch
        print(f"7. État après switch:")
        print(f"   - Index courant: {stacked_widget.currentIndex()}")
        print(f"   - Widget courant: {stacked_widget.currentWidget()}")
        print(f"   - Vue courante ViewManager: {view_manager.get_current_view()}")
        
        # Vérifier la visibilité du dashboard
        current_widget = stacked_widget.currentWidget()
        if current_widget:
            print(f"8. Widget courant détails:")
            print(f"   - Type: {type(current_widget)}")
            print(f"   - Taille: {current_widget.size()}")
            print(f"   - Visible: {current_widget.isVisible()}")
            print(f"   - Enabled: {current_widget.isEnabled()}")
            print(f"   - StyleSheet: {current_widget.styleSheet()[:100]}...")
            
            # Vérifier les enfants
            children = current_widget.findChildren(object)
            print(f"   - Nombre d'enfants: {len(children)}")
            
            # Forcer la visibilité
            current_widget.show()
            current_widget.setVisible(True)
            print(f"   - Visibilité forcée")
        
        # Test d'affichage
        print(f"9. Test d'affichage:")
        stacked_widget.show()
        stacked_widget.setVisible(True)
        print(f"   - QStackedWidget affiché")
        
        # Vérifier si le problème vient du thème
        print(f"10. Test sans thème:")
        stacked_widget.setStyleSheet("")
        if current_widget:
            current_widget.setStyleSheet("background-color: red; color: white;")
            print(f"    - Style de test appliqué (fond rouge)")
        
        print("\n=== DIAGNOSTIC TERMINÉ ===")
        
    except Exception as e:
        print(f"❌ Erreur lors du diagnostic: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        app.quit()

if __name__ == "__main__":
    main()