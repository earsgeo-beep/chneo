#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Correction de main_window.py avec debug très détaillé
"""

import sys
from pathlib import Path

# Ajouter le chemin du projet
sys.path.insert(0, str(Path(__file__).parent / "src"))

def fix_main_window_with_detailed_debug():
    """Modifier main_window.py pour ajouter un debug très détaillé"""
    print("🔧 CORRECTION MAINWINDOW AVEC DEBUG DÉTAILLÉ")
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
        backup_path = main_window_path.with_suffix('.py.backup3')
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Sauvegarde créée: {backup_path}")
        
        # Ajouter des prints de debug dans __init__
        print("🔄 Ajout de debug détaillé dans __init__...")
        
        # Trouver la méthode __init__
        init_start = content.find("def __init__(self, config=None, parent=None):")
        if init_start == -1:
            print("❌ Méthode __init__ non trouvée")
            return False
        
        # Trouver le début du corps de __init__
        body_start = content.find(":", init_start) + 1
        body_start = content.find("\n", body_start) + 1
        
        # Ajouter les prints de debug
        debug_code = '''
        print("🔍 DEBUG: Début __init__ MainWindow")
        print("🔍 DEBUG: Étape 1 - Appel super().__init__")
        '''
        
        # Insérer après super().__init__
        super_call = content.find("super().__init__(parent)", body_start)
        if super_call != -1:
            super_end = content.find("\n", super_call) + 1
            content = content[:super_end] + debug_code + content[super_end:]
            print("✅ Debug ajouté après super().__init__")
        
        # Ajouter debug avant _build_ui
        build_ui_call = content.find("self._build_ui()")
        if build_ui_call != -1:
            debug_before_build = '''
        print("🔍 DEBUG: Étape 2 - Avant _build_ui")
        '''
            content = content[:build_ui_call] + debug_before_build + content[build_ui_call:]
            print("✅ Debug ajouté avant _build_ui")
        
        # Ajouter debug après _build_ui
        if build_ui_call != -1:
            build_ui_end = content.find("\n", build_ui_call) + 1
            debug_after_build = '''
        print("🔍 DEBUG: Étape 3 - Après _build_ui")
        '''
            content = content[:build_ui_end] + debug_after_build + content[build_ui_end:]
            print("✅ Debug ajouté après _build_ui")
        
        # Ajouter debug dans _build_ui
        build_ui_def = content.find("def _build_ui(self):")
        if build_ui_def != -1:
            build_ui_body_start = content.find(":", build_ui_def) + 1
            build_ui_body_start = content.find("\n", build_ui_body_start) + 1
            
            debug_build_ui = '''
        print("🔍 DEBUG: _build_ui - Début")
        print("🔍 DEBUG: _build_ui - Étape 1: Configuration fenêtre")
        '''
            
            content = content[:build_ui_body_start] + debug_build_ui + content[build_ui_body_start:]
            print("✅ Debug ajouté dans _build_ui")
        
        # Ajouter debug avant _create_and_register_views
        create_views_call = content.find("self._create_and_register_views()")
        if create_views_call != -1:
            debug_before_views = '''
        print("🔍 DEBUG: Étape 4 - Avant _create_and_register_views")
        '''
            content = content[:create_views_call] + debug_before_views + content[create_views_call:]
            print("✅ Debug ajouté avant _create_and_register_views")
        
        # Ajouter debug après _create_and_register_views
        if create_views_call != -1:
            create_views_end = content.find("\n", create_views_call) + 1
            debug_after_views = '''
        print("🔍 DEBUG: Étape 5 - Après _create_and_register_views")
        print("🔍 DEBUG: __init__ MainWindow terminé avec succès")
        '''
            content = content[:create_views_end] + debug_after_views + content[create_views_end:]
            print("✅ Debug ajouté après _create_and_register_views")
        
        # Ajouter debug dans _create_and_register_views
        create_views_def = content.find("def _create_and_register_views(self):")
        if create_views_def != -1:
            create_views_body_start = content.find(":", create_views_def) + 1
            create_views_body_start = content.find("\n", create_views_body_start) + 1
            
            debug_create_views = '''
        print("🔍 DEBUG: _create_and_register_views - Début")
        print("🔍 DEBUG: _create_and_register_views - Étape 1: Import des vues")
        '''
            
            content = content[:create_views_body_start] + debug_create_views + content[create_views_body_start:]
            print("✅ Debug ajouté dans _create_and_register_views")
        
        # Écrire le fichier modifié
        with open(main_window_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Fichier main_window.py modifié avec debug détaillé")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la modification: {e}")
        return False

def create_test_main_window_debug():
    """Créer un test spécifique pour MainWindow avec debug"""
    print("\n🔧 CRÉATION TEST MAINWINDOW DEBUG")
    print("=" * 40)
    
    test_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test MainWindow avec debug détaillé
"""

import sys
import traceback
from pathlib import Path

# Ajouter le chemin du projet
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_main_window_with_debug():
    """Test MainWindow avec debug détaillé"""
    print("🚀 TEST MAINWINDOW AVEC DEBUG DÉTAILLÉ")
    print("=" * 50)
    
    try:
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import Qt, QTimer
        
        # Créer QApplication
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
            app.setApplicationName("CHNeoWave Debug Test")
        
        print("✅ QApplication créé")
        
        # Test import MainWindow
        print("🔄 Import MainWindow...")
        from hrneowave.gui.main_window import MainWindow
        print("✅ MainWindow importé")
        
        # Test création MainWindow avec debug
        print("🔄 Création MainWindow avec debug...")
        print("=" * 40)
        main_window = MainWindow()
        print("=" * 40)
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
    exit(0 if test_main_window_with_debug() else 1)
'''
    
    try:
        with open('test_main_window_debug.py', 'w', encoding='utf-8') as f:
            f.write(test_content)
        print("✅ Test MainWindow debug créé: test_main_window_debug.py")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de la création du test: {e}")
        return False

def main():
    """Point d'entrée principal"""
    print("🔧 CORRECTEUR MAINWINDOW DEBUG DÉTAILLÉ")
    print("=" * 50)
    
    # Modifier main_window.py avec debug détaillé
    if not fix_main_window_with_detailed_debug():
        print("❌ ÉCHEC: Modification main_window.py")
        return 1
    
    # Créer test MainWindow debug
    if not create_test_main_window_debug():
        print("❌ ÉCHEC: Création test MainWindow debug")
        return 1
    
    print("\n🎉 CORRECTION TERMINÉE!")
    print("✅ main_window.py modifié avec debug détaillé")
    print("✅ Test MainWindow debug créé: test_main_window_debug.py")
    
    print("\n🚀 COMMANDES DE TEST:")
    print("1. Test fenêtre simplifiée: python test_simple_window.py")
    print("2. Test MainWindow debug: python test_main_window_debug.py")
    print("3. Diagnostic étape par étape: python debug_main_window_step_by_step.py")
    print("4. Lancement application: python main.py")
    
    return 0

if __name__ == "__main__":
    exit(main()) 