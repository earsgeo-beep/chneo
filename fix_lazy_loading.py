#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Désactivation temporaire des vues avec lazy loading
"""

import sys
from pathlib import Path

# Ajouter le chemin du projet
sys.path.insert(0, str(Path(__file__).parent / "src"))

def disable_lazy_loading():
    """Désactiver temporairement les vues avec lazy loading"""
    print("🔧 DÉSACTIVATION VUES LAZY LOADING")
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
        backup_path = main_window_path.with_suffix('.py.backup_lazy')
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Sauvegarde créée: {backup_path}")
        
        # Trouver et commenter la boucle lazy loading
        lazy_loading_start = content.find("for view_name, config in VIEWS_CONFIG.items():")
        if lazy_loading_start == -1:
            print("❌ Boucle lazy loading non trouvée")
            return False
        
        # Trouver la fin de la boucle
        lazy_loading_end = content.find("self.view_manager.switch_to_view('welcome')", lazy_loading_start)
        if lazy_loading_end == -1:
            print("❌ Fin de boucle lazy loading non trouvée")
            return False
        
        # Commenter toute la section lazy loading
        before_lazy = content[:lazy_loading_start]
        after_lazy = content[lazy_loading_end:]
        
        commented_lazy = '''        # Vues avec lazy loading (temporairement désactivées)
        # for view_name, config in VIEWS_CONFIG.items():
        #     if 'loader' in config:
        #         view_instance = config['loader'](parent=None)
        #         self.view_manager.register_view(view_name, view_instance)
        #         logger.info(f"[VIEW REGISTRATION] '{view_name}' view registered with object ID: {id(view_instance)}")

        # Navigation initiale
'''
        
        # Reconstruire le contenu
        content = before_lazy + commented_lazy + after_lazy
        
        # Écrire le fichier modifié
        with open(main_window_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Vues lazy loading désactivées")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la modification: {e}")
        return False

def create_test_main_window_final():
    """Créer un test final pour MainWindow"""
    print("\n🔧 CRÉATION TEST MAINWINDOW FINAL")
    print("=" * 40)
    
    test_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test MainWindow final (sans lazy loading)
"""

import sys
import traceback
from pathlib import Path

# Ajouter le chemin du projet
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_main_window_final():
    """Test MainWindow final"""
    print("🚀 TEST MAINWINDOW FINAL")
    print("=" * 50)
    
    try:
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import Qt, QTimer
        
        # Créer QApplication
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
            app.setApplicationName("CHNeoWave Final Test")
        
        print("✅ QApplication créé")
        
        # Test import MainWindow
        print("🔄 Import MainWindow...")
        from hrneowave.gui.main_window import MainWindow
        print("✅ MainWindow importé")
        
        # Test création MainWindow
        print("🔄 Création MainWindow...")
        main_window = MainWindow()
        print("✅ MainWindow créée")
        
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
    exit(0 if test_main_window_final() else 1)
'''
    
    try:
        with open('test_main_window_final.py', 'w', encoding='utf-8') as f:
            f.write(test_content)
        print("✅ Test MainWindow final créé: test_main_window_final.py")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de la création du test: {e}")
        return False

def main():
    """Point d'entrée principal"""
    print("🔧 CORRECTEUR LAZY LOADING")
    print("=" * 50)
    
    # Désactiver les vues lazy loading
    if not disable_lazy_loading():
        print("❌ ÉCHEC: Désactivation lazy loading")
        return 1
    
    # Créer test MainWindow final
    if not create_test_main_window_final():
        print("❌ ÉCHEC: Création test MainWindow final")
        return 1
    
    print("\n🎉 CORRECTION LAZY LOADING TERMINÉE!")
    print("✅ Vues lazy loading désactivées")
    print("✅ Test MainWindow final créé: test_main_window_final.py")
    
    print("\n🚀 COMMANDES DE TEST:")
    print("1. Test MainWindow final: python test_main_window_final.py")
    print("2. Lancement application: python main.py")
    
    return 0

if __name__ == "__main__":
    exit(main()) 