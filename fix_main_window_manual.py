#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Correction manuelle sûre de main_window.py
"""

import sys
from pathlib import Path

# Ajouter le chemin du projet
sys.path.insert(0, str(Path(__file__).parent / "src"))

def fix_main_window_manual():
    """Correction manuelle sûre de main_window.py"""
    print("🔧 CORRECTION MANUELLE MAINWINDOW")
    print("=" * 40)
    
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
        backup_path = main_window_path.with_suffix('.py.backup5')
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        print(f"✅ Sauvegarde créée: {backup_path}")
        
        # Trouver la ligne super().__init__(parent)
        super_line_index = None
        for i, line in enumerate(lines):
            if "super().__init__(parent)" in line:
                super_line_index = i
                break
        
        if super_line_index is None:
            print("❌ Ligne super().__init__(parent) non trouvée")
            return False
        
        # Ajouter debug après super().__init__(parent)
        debug_line = '        print("🔍 DEBUG: __init__ MainWindow - Début")\n'
        lines.insert(super_line_index + 1, debug_line)
        print("✅ Debug ajouté après super().__init__")
        
        # Trouver la ligne self._build_ui()
        build_ui_line_index = None
        for i, line in enumerate(lines):
            if "self._build_ui()" in line:
                build_ui_line_index = i
                break
        
        if build_ui_line_index is None:
            print("❌ Ligne self._build_ui() non trouvée")
            return False
        
        # Ajouter debug avant et après _build_ui
        debug_before = '        print("🔍 DEBUG: __init__ MainWindow - Avant _build_ui")\n'
        debug_after = '        print("🔍 DEBUG: __init__ MainWindow - Après _build_ui")\n'
        
        lines.insert(build_ui_line_index, debug_before)
        lines.insert(build_ui_line_index + 2, debug_after)
        print("✅ Debug ajouté avant et après _build_ui")
        
        # Trouver la ligne self._create_and_register_views()
        create_views_line_index = None
        for i, line in enumerate(lines):
            if "self._create_and_register_views()" in line:
                create_views_line_index = i
                break
        
        if create_views_line_index is None:
            print("❌ Ligne self._create_and_register_views() non trouvée")
            return False
        
        # Ajouter debug avant et après _create_and_register_views
        debug_before_views = '        print("🔍 DEBUG: __init__ MainWindow - Avant _create_and_register_views")\n'
        debug_after_views = '        print("🔍 DEBUG: __init__ MainWindow - Après _create_and_register_views")\n'
        debug_success = '        print("🔍 DEBUG: __init__ MainWindow - Terminé avec succès")\n'
        
        lines.insert(create_views_line_index, debug_before_views)
        lines.insert(create_views_line_index + 2, debug_after_views)
        lines.insert(create_views_line_index + 3, debug_success)
        print("✅ Debug ajouté avant et après _create_and_register_views")
        
        # Écrire le fichier modifié
        with open(main_window_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        print("✅ Fichier main_window.py modifié avec debug manuel")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la modification: {e}")
        return False

def create_test_main_window_manual():
    """Créer un test pour MainWindow avec correction manuelle"""
    print("\n🔧 CRÉATION TEST MAINWINDOW MANUEL")
    print("=" * 40)
    
    test_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test MainWindow avec correction manuelle
"""

import sys
import traceback
from pathlib import Path

# Ajouter le chemin du projet
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_main_window_manual():
    """Test MainWindow avec correction manuelle"""
    print("🚀 TEST MAINWINDOW MANUEL")
    print("=" * 40)
    
    try:
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import Qt, QTimer
        
        # Créer QApplication
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
            app.setApplicationName("CHNeoWave Manual Test")
        
        print("✅ QApplication créé")
        
        # Test import MainWindow
        print("🔄 Import MainWindow...")
        from hrneowave.gui.main_window import MainWindow
        print("✅ MainWindow importé")
        
        # Test création MainWindow
        print("🔄 Création MainWindow...")
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
    exit(0 if test_main_window_manual() else 1)
'''
    
    try:
        with open('test_main_window_manual.py', 'w', encoding='utf-8') as f:
            f.write(test_content)
        print("✅ Test MainWindow manuel créé: test_main_window_manual.py")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de la création du test: {e}")
        return False

def main():
    """Point d'entrée principal"""
    print("🔧 CORRECTEUR MAINWINDOW MANUEL")
    print("=" * 50)
    
    # Modifier main_window.py avec correction manuelle
    if not fix_main_window_manual():
        print("❌ ÉCHEC: Modification main_window.py")
        return 1
    
    # Créer test MainWindow manuel
    if not create_test_main_window_manual():
        print("❌ ÉCHEC: Création test MainWindow manuel")
        return 1
    
    print("\n🎉 CORRECTION TERMINÉE!")
    print("✅ main_window.py modifié avec correction manuelle")
    print("✅ Test MainWindow manuel créé: test_main_window_manual.py")
    
    print("\n🚀 COMMANDES DE TEST:")
    print("1. Test fenêtre simplifiée: python test_simple_window.py")
    print("2. Test MainWindow manuel: python test_main_window_manual.py")
    print("3. Lancement application: python main.py")
    
    return 0

if __name__ == "__main__":
    exit(main()) 