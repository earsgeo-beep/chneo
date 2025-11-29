#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Diagnostic ViewManager simplifié pour identifier la cause de l'écran gris
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def diagnostic_viewmanager():
    """Diagnostic complet du ViewManager"""
    print("=== DIAGNOSTIC VIEWMANAGER ===")
    
    try:
        # Créer QApplication en premier
        from PySide6.QtWidgets import QApplication
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        print(f"✅ QApplication utilisée: {app}")
        
        # Importer et lancer main.py pour obtenir les objets
        print("\n=== LANCEMENT MAIN.PY ===")
        
        # Exécuter le code de main.py directement
        from hrneowave.gui.main_window import MainWindow
        from hrneowave.gui.controllers.main_controller import MainController
        
        print("✅ Imports réussis")
        
        # Créer la fenêtre principale
        main_window = MainWindow()
        print(f"✅ MainWindow créée: {main_window}")
        print(f"   MainWindow visible: {main_window.isVisible()}")
        print(f"   MainWindow size: {main_window.size().toTuple()}")
        
        # Obtenir le stacked_widget
        stacked_widget = main_window.stack_widget
        print(f"✅ StackedWidget obtenu: {stacked_widget}")
        
        # Créer le contrôleur principal
        controller = MainController(main_window)
        print(f"✅ MainController créé: {controller}")
        
        # Obtenir le ViewManager depuis le contrôleur
        vm = controller.view_manager
        print(f"✅ ViewManager obtenu: {vm}")
        print(f"   ViewManager instance: {vm.__class__.__name__}")
        
        # Diagnostic du QStackedWidget
        print(f"\n=== DIAGNOSTIC QSTACKEDWIDGET ===")
        print(f"stacked_widget = {stacked_widget}")
        print(f"pages = {stacked_widget.count()}")
        print(f"index = {stacked_widget.currentIndex()}")
        print(f"widget= {stacked_widget.currentWidget()}")
        print(f"stacked_widget visible: {stacked_widget.isVisible()}")
        print(f"stacked_widget size: {stacked_widget.size().toTuple()}")
        print(f"stacked_widget sizeHint: {stacked_widget.sizeHint().toTuple()}")
        print(f"stacked_widget autoFillBackground: {stacked_widget.autoFillBackground()}")
        print(f"stacked_widget styleSheet length: {len(stacked_widget.styleSheet())}")
        
        # Diagnostic du widget courant
        current_widget = stacked_widget.currentWidget()
        if current_widget:
            print(f"\n=== DIAGNOSTIC WIDGET COURANT ===")
            cw = current_widget
            print(f"current_widget = {cw}")
            print(f"current_widget type: {type(cw).__name__}")
            print(f"size  = {cw.sizeHint().toTuple()}")
            print(f"visible= {cw.isVisible()}")
            print(f"styleLen= {len(cw.styleSheet())}")
            print(f"autoFillBackground: {cw.autoFillBackground()}")
            print(f"actual size: {cw.size().toTuple()}")
            print(f"parent: {cw.parent()}")
            
            # Vérifier le contenu du stylesheet
            if len(cw.styleSheet()) > 0:
                print(f"\n=== STYLESHEET CONTENT ===")
                stylesheet = cw.styleSheet()
                print(f"Stylesheet (first 200 chars): {stylesheet[:200]}")
                if 'transparent' in stylesheet.lower():
                    print("⚠️  ATTENTION: 'transparent' trouvé dans le stylesheet !")
                if 'background' in stylesheet.lower():
                    print("⚠️  ATTENTION: 'background' trouvé dans le stylesheet !")
        else:
            print(f"\n❌ PROBLÈME: Aucun widget courant !")
        
        # Diagnostic des vues enregistrées
        print(f"\n=== DIAGNOSTIC VUES ENREGISTRÉES ===")
        if hasattr(vm, '_views'):
            print(f"Nombre de vues enregistrées: {len(vm._views)}")
            for name, view in vm._views.items():
                print(f"  - {name}: {view} (visible: {view.isVisible()})")
        else:
            print("❌ Attribut _views non trouvé")
        
        # Afficher la fenêtre pour test visuel
        main_window.show()
        main_window.raise_()
        main_window.activateWindow()
        
        print(f"\n=== ÉTAT FINAL ===")
        print(f"MainWindow visible après show(): {main_window.isVisible()}")
        print(f"StackedWidget visible après show(): {stacked_widget.isVisible()}")
        if current_widget:
            print(f"CurrentWidget visible après show(): {current_widget.isVisible()}")
        
        # Fermer après 3 secondes
        from PySide6.QtCore import QTimer
        timer = QTimer()
        timer.timeout.connect(app.quit)
        timer.start(3000)
        
        print(f"\nLancement de l'event loop (3 secondes)...")
        app.exec()
        
        return True
        
    except Exception as e:
        print(f"❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = diagnostic_viewmanager()
    print(f"\n=== RÉSULTAT DIAGNOSTIC: {'✅ SUCCÈS' if success else '❌ ÉCHEC'} ===")
    sys.exit(0 if success else 1)