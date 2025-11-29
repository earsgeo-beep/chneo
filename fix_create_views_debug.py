#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Correction de _create_and_register_views avec debug très détaillé
"""

import sys
from pathlib import Path

# Ajouter le chemin du projet
sys.path.insert(0, str(Path(__file__).parent / "src"))

def fix_create_views_with_debug():
    """Modifier _create_and_register_views pour ajouter du debug très détaillé"""
    print("🔧 CORRECTION _CREATE_AND_REGISTER_VIEWS AVEC DEBUG")
    print("=" * 50)
    
    try:
        # Lire le fichier main_window.py
        main_window_path = Path("src/hrneowave/gui/main_window.py")
        
        if not main_window_path.exists():
            print(f"❌ Fichier non trouvé: {main_window_path}")
            return False
        
        with open(main_window_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("✅ Fichier main_window.py lu")
        
        # Créer une sauvegarde
        backup_path = main_window_path.with_suffix('.py.backup6')
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Sauvegarde créée: {backup_path}")
        
        # Trouver la méthode _create_and_register_views
        method_start = content.find("def _create_and_register_views(self):")
        if method_start == -1:
            print("❌ Méthode _create_and_register_views non trouvée")
            return False
        
        # Trouver le début du corps de la méthode
        body_start = content.find(":", method_start) + 1
        body_start = content.find("\n", body_start) + 1
        
        # Ajouter du debug très détaillé
        debug_code = '''
        print("🔍 DEBUG: _create_and_register_views - Début")
        print("🔍 DEBUG: _create_and_register_views - Étape 1: Import des vues")
        '''
        
        # Insérer au début de la méthode
        content = content[:body_start] + debug_code + content[body_start:]
        print("✅ Debug ajouté au début de _create_and_register_views")
        
        # Trouver la ligne "welcome_view = WelcomeView(parent=None)"
        welcome_line = content.find("welcome_view = WelcomeView(parent=None)")
        if welcome_line != -1:
            debug_before_welcome = '''
        print("🔍 DEBUG: _create_and_register_views - Étape 2: Création WelcomeView")
        '''
            content = content[:welcome_line] + debug_before_welcome + content[welcome_line:]
            print("✅ Debug ajouté avant création WelcomeView")
        
        # Trouver la ligne "self.view_manager.register_view('welcome', welcome_view)"
        register_welcome_line = content.find("self.view_manager.register_view('welcome', welcome_view)")
        if register_welcome_line != -1:
            debug_after_welcome = '''
        print("🔍 DEBUG: _create_and_register_views - WelcomeView enregistrée")
        '''
            register_welcome_end = content.find("\n", register_welcome_line) + 1
            content = content[:register_welcome_end] + debug_after_welcome + content[register_welcome_end:]
            print("✅ Debug ajouté après enregistrement WelcomeView")
        
        # Trouver la ligne "dashboard_view = DashboardViewMaritime(parent=None)"
        dashboard_line = content.find("dashboard_view = DashboardViewMaritime(parent=None)")
        if dashboard_line != -1:
            debug_before_dashboard = '''
        print("🔍 DEBUG: _create_and_register_views - Étape 3: Création DashboardViewMaritime")
        '''
            content = content[:dashboard_line] + debug_before_dashboard + content[dashboard_line:]
            print("✅ Debug ajouté avant création DashboardViewMaritime")
        
        # Trouver la ligne "self.view_manager.register_view('dashboard', dashboard_view)"
        register_dashboard_line = content.find("self.view_manager.register_view('dashboard', dashboard_view)")
        if register_dashboard_line != -1:
            debug_after_dashboard = '''
        print("🔍 DEBUG: _create_and_register_views - DashboardViewMaritime enregistrée")
        '''
            register_dashboard_end = content.find("\n", register_dashboard_line) + 1
            content = content[:register_dashboard_end] + debug_after_dashboard + content[register_dashboard_end:]
            print("✅ Debug ajouté après enregistrement DashboardViewMaritime")
        
        # Trouver la ligne "for view_name, config in VIEWS_CONFIG.items():"
        for_line = content.find("for view_name, config in VIEWS_CONFIG.items():")
        if for_line != -1:
            debug_before_for = '''
        print("🔍 DEBUG: _create_and_register_views - Étape 4: Vues avec lazy loading")
        '''
            content = content[:for_line] + debug_before_for + content[for_line:]
            print("✅ Debug ajouté avant boucle lazy loading")
        
        # Trouver la ligne "self.view_manager.switch_to_view('welcome')"
        switch_line = content.find("self.view_manager.switch_to_view('welcome')")
        if switch_line != -1:
            debug_before_switch = '''
        print("🔍 DEBUG: _create_and_register_views - Étape 5: Navigation initiale")
        '''
            content = content[:switch_line] + debug_before_switch + content[switch_line:]
            print("✅ Debug ajouté avant navigation initiale")
        
        # Trouver la fin de la méthode et ajouter debug final
        method_end = content.find("\n    def _update_breadcrumbs_for_view", method_start)
        if method_end == -1:
            method_end = content.find("\n    @Slot", method_start)
        
        if method_end != -1:
            debug_final = '''
        print("🔍 DEBUG: _create_and_register_views - Terminé avec succès")
        '''
            content = content[:method_end] + debug_final + content[method_end:]
            print("✅ Debug ajouté à la fin de _create_and_register_views")
        
        # Écrire le fichier modifié
        with open(main_window_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Fichier main_window.py modifié avec debug très détaillé")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la modification: {e}")
        return False

def create_test_main_window_debug_detailed():
    """Créer un test pour MainWindow avec debug très détaillé"""
    print("\n🔧 CRÉATION TEST MAINWINDOW DEBUG DÉTAILLÉ")
    print("=" * 40)
    
    test_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test MainWindow avec debug très détaillé
"""

import sys
import traceback
from pathlib import Path

# Ajouter le chemin du projet
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_main_window_debug_detailed():
    """Test MainWindow avec debug très détaillé"""
    print("🚀 TEST MAINWINDOW DEBUG DÉTAILLÉ")
    print("=" * 50)
    
    try:
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import Qt, QTimer
        
        # Créer QApplication
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
            app.setApplicationName("CHNeoWave Debug Detailed Test")
        
        print("✅ QApplication créé")
        
        # Test import MainWindow
        print("🔄 Import MainWindow...")
        from hrneowave.gui.main_window import MainWindow
        print("✅ MainWindow importé")
        
        # Test création MainWindow avec debug très détaillé
        print("🔄 Création MainWindow avec debug très détaillé...")
        print("=" * 50)
        main_window = MainWindow()
        print("=" * 50)
        print("✅ MainWindow créée avec succès")
        
        # Test affichage
        print("🔄 Affichage MainWindow...")
        main_window.show()
        main_window.raise_()
        main_window.activateWindow()
        
        visible = main_window.isVisible()
        print(f"✅ MainWindow visible: {visible}")
        
        if visible:
            print("🎉 SUCCÈS: MainWindow visible!")
            
            # Maintenir ouvert 10 secondes
            timer = QTimer()
            timer.timeout.connect(app.quit)
            timer.start(10000)
            
            print("🔄 Maintien ouvert 10 secondes...")
            exit_code = app.exec()
            print(f"✅ Test terminé (code: {exit_code})")
            return True
        else:
            print("❌ PROBLÈME: MainWindow non visible")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    exit(0 if test_main_window_debug_detailed() else 1)
'''
    
    try:
        with open('test_main_window_debug_detailed.py', 'w', encoding='utf-8') as f:
            f.write(test_content)
        print("✅ Test MainWindow debug détaillé créé: test_main_window_debug_detailed.py")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de la création du test: {e}")
        return False

def main():
    """Point d'entrée principal"""
    print("🔧 CORRECTEUR _CREATE_AND_REGISTER_VIEWS DEBUG")
    print("=" * 50)
    
    # Modifier _create_and_register_views avec debug très détaillé
    if not fix_create_views_with_debug():
        print("❌ ÉCHEC: Modification _create_and_register_views")
        return 1
    
    # Créer test MainWindow debug détaillé
    if not create_test_main_window_debug_detailed():
        print("❌ ÉCHEC: Création test MainWindow debug détaillé")
        return 1
    
    print("\n🎉 CORRECTION TERMINÉE!")
    print("✅ _create_and_register_views modifié avec debug très détaillé")
    print("✅ Test MainWindow debug détaillé créé: test_main_window_debug_detailed.py")
    
    print("\n🚀 COMMANDES DE TEST:")
    print("1. Test fenêtre simplifiée: python test_simple_window.py")
    print("2. Diagnostic approfondi: python debug_views_deep.py")
    print("3. Test MainWindow debug détaillé: python test_main_window_debug_detailed.py")
    print("4. Lancement application: python main.py")
    
    return 0

if __name__ == "__main__":
    exit(main()) 