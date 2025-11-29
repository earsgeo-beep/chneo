#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Correction sûre de _create_and_register_views avec debug
"""

import sys
import re
from pathlib import Path

# Ajouter le chemin du projet
sys.path.insert(0, str(Path(__file__).parent / "src"))

def fix_create_views_safe():
    """Modifier _create_and_register_views de manière sûre"""
    print("🔧 CORRECTION SÛRE _CREATE_AND_REGISTER_VIEWS")
    print("=" * 50)
    
    try:
        # Lire le fichier main_window.py
        main_window_path = Path("src/hrneowave/gui/main_window.py")
        
        if not main_window_path.exists():
            print(f"❌ Fichier non trouvé: {main_window_path}")
            return False
        
        with open(main_window_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        print("✅ Fichier main_window.py lu")
        
        # Créer une sauvegarde
        backup_path = main_window_path.with_suffix('.py.backup7')
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        print(f"✅ Sauvegarde créée: {backup_path}")
        
        # Trouver la méthode _create_and_register_views
        method_start = None
        for i, line in enumerate(lines):
            if "def _create_and_register_views(self):" in line:
                method_start = i
                break
        
        if method_start is None:
            print("❌ Méthode _create_and_register_views non trouvée")
            return False
        
        print(f"✅ Méthode _create_and_register_views trouvée à la ligne {method_start + 1}")
        
        # Trouver le début du corps de la méthode (après la ligne de définition)
        body_start = method_start + 1
        
        # Ajouter du debug au début de la méthode
        debug_lines = [
            '        print("🔍 DEBUG: _create_and_register_views - Début")\n',
            '        print("🔍 DEBUG: _create_and_register_views - Étape 1: Import des vues")\n'
        ]
        
        lines.insert(body_start, debug_lines[0])
        lines.insert(body_start + 1, debug_lines[1])
        print("✅ Debug ajouté au début de _create_and_register_views")
        
        # Trouver et ajouter du debug avant la création de WelcomeView
        for i, line in enumerate(lines):
            if "welcome_view = WelcomeView(parent=None)" in line:
                debug_line = '        print("🔍 DEBUG: _create_and_register_views - Étape 2: Création WelcomeView")\n'
                lines.insert(i, debug_line)
                print("✅ Debug ajouté avant création WelcomeView")
                break
        
        # Trouver et ajouter du debug après l'enregistrement de WelcomeView
        for i, line in enumerate(lines):
            if "self.view_manager.register_view('welcome', welcome_view)" in line:
                debug_line = '        print("🔍 DEBUG: _create_and_register_views - WelcomeView enregistrée")\n'
                lines.insert(i + 1, debug_line)
                print("✅ Debug ajouté après enregistrement WelcomeView")
                break
        
        # Trouver et ajouter du debug avant la création de DashboardViewMaritime
        for i, line in enumerate(lines):
            if "dashboard_view = DashboardViewMaritime(parent=None)" in line:
                debug_line = '        print("🔍 DEBUG: _create_and_register_views - Étape 3: Création DashboardViewMaritime")\n'
                lines.insert(i, debug_line)
                print("✅ Debug ajouté avant création DashboardViewMaritime")
                break
        
        # Trouver et ajouter du debug après l'enregistrement de DashboardViewMaritime
        for i, line in enumerate(lines):
            if "self.view_manager.register_view('dashboard', dashboard_view)" in line:
                debug_line = '        print("🔍 DEBUG: _create_and_register_views - DashboardViewMaritime enregistrée")\n'
                lines.insert(i + 1, debug_line)
                print("✅ Debug ajouté après enregistrement DashboardViewMaritime")
                break
        
        # Trouver et ajouter du debug avant la boucle lazy loading
        for i, line in enumerate(lines):
            if "for view_name, config in VIEWS_CONFIG.items():" in line:
                debug_line = '        print("🔍 DEBUG: _create_and_register_views - Étape 4: Vues avec lazy loading")\n'
                lines.insert(i, debug_line)
                print("✅ Debug ajouté avant boucle lazy loading")
                break
        
        # Trouver et ajouter du debug avant la navigation initiale
        for i, line in enumerate(lines):
            if "self.view_manager.switch_to_view('welcome')" in line:
                debug_line = '        print("🔍 DEBUG: _create_and_register_views - Étape 5: Navigation initiale")\n'
                lines.insert(i, debug_line)
                print("✅ Debug ajouté avant navigation initiale")
                break
        
        # Trouver la fin de la méthode et ajouter debug final
        method_end = None
        for i in range(method_start + 1, len(lines)):
            if lines[i].strip().startswith("def ") and lines[i].strip().endswith(":"):
                method_end = i
                break
        
        if method_end is None:
            # Si on ne trouve pas la fin, ajouter à la fin du fichier
            method_end = len(lines)
        
        debug_final = '        print("🔍 DEBUG: _create_and_register_views - Terminé avec succès")\n'
        lines.insert(method_end, debug_final)
        print("✅ Debug ajouté à la fin de _create_and_register_views")
        
        # Écrire le fichier modifié
        with open(main_window_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        print("✅ Fichier main_window.py modifié avec debug sûr")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la modification: {e}")
        return False

def create_test_main_window_safe():
    """Créer un test sûr pour MainWindow"""
    print("\n🔧 CRÉATION TEST MAINWINDOW SÛR")
    print("=" * 40)
    
    test_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test MainWindow avec debug sûr
"""

import sys
import traceback
from pathlib import Path

# Ajouter le chemin du projet
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_main_window_safe():
    """Test MainWindow avec debug sûr"""
    print("🚀 TEST MAINWINDOW SÛR")
    print("=" * 50)
    
    try:
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import Qt, QTimer
        
        # Créer QApplication
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
            app.setApplicationName("CHNeoWave Safe Test")
        
        print("✅ QApplication créé")
        
        # Test import MainWindow
        print("🔄 Import MainWindow...")
        from hrneowave.gui.main_window import MainWindow
        print("✅ MainWindow importé")
        
        # Test création MainWindow avec debug sûr
        print("🔄 Création MainWindow avec debug sûr...")
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
    exit(0 if test_main_window_safe() else 1)
'''
    
    try:
        with open('test_main_window_safe.py', 'w', encoding='utf-8') as f:
            f.write(test_content)
        print("✅ Test MainWindow sûr créé: test_main_window_safe.py")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de la création du test: {e}")
        return False

def main():
    """Point d'entrée principal"""
    print("🔧 CORRECTEUR SÛR _CREATE_AND_REGISTER_VIEWS")
    print("=" * 50)
    
    # Modifier _create_and_register_views de manière sûre
    if not fix_create_views_safe():
        print("❌ ÉCHEC: Modification _create_and_register_views")
        return 1
    
    # Créer test MainWindow sûr
    if not create_test_main_window_safe():
        print("❌ ÉCHEC: Création test MainWindow sûr")
        return 1
    
    print("\n🎉 CORRECTION SÛRE TERMINÉE!")
    print("✅ _create_and_register_views modifié avec debug sûr")
    print("✅ Test MainWindow sûr créé: test_main_window_safe.py")
    
    print("\n🚀 COMMANDES DE TEST:")
    print("1. Test fenêtre simplifiée: python test_simple_window.py")
    print("2. Diagnostic approfondi: python debug_views_deep.py")
    print("3. Test MainWindow sûr: python test_main_window_safe.py")
    print("4. Lancement application: python main.py")
    
    return 0

if __name__ == "__main__":
    exit(main()) 