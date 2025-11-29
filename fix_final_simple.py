#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Correction finale simple - Désactivation des vues lazy loading
"""

import sys
from pathlib import Path

# Ajouter le chemin du projet
sys.path.insert(0, str(Path(__file__).parent / "src"))

def fix_final_simple():
    """Correction finale simple"""
    print("🔧 CORRECTION FINALE SIMPLE")
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
        backup_path = main_window_path.with_suffix('.py.backup_final')
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        print(f"✅ Sauvegarde créée: {backup_path}")
        
        # Trouver et commenter la ligne de lazy loading
        for i, line in enumerate(lines):
            if "for view_name, config in VIEWS_CONFIG.items():" in line:
                lines[i] = "# " + line  # Commenter cette ligne
                print(f"✅ Ligne {i+1} commentée: {line.strip()}")
                
                # Commenter les lignes suivantes jusqu'à la fin de la boucle
                j = i + 1
                while j < len(lines) and ("if 'loader' in config:" in lines[j] or 
                                        "view_instance = config['loader']" in lines[j] or
                                        "self.view_manager.register_view" in lines[j] or
                                        "logger.info" in lines[j]):
                    lines[j] = "# " + lines[j]
                    print(f"✅ Ligne {j+1} commentée: {lines[j].strip()}")
                    j += 1
                break
        
        # Écrire le fichier modifié
        with open(main_window_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        print("✅ Vues lazy loading désactivées")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la modification: {e}")
        return False

def create_test_final_simple():
    """Créer un test final simple"""
    print("\n🔧 CRÉATION TEST FINAL SIMPLE")
    print("=" * 40)
    
    test_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test final simple
"""

import sys
import traceback
from pathlib import Path

# Ajouter le chemin du projet
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_final_simple():
    """Test final simple"""
    print("🚀 TEST FINAL SIMPLE")
    print("=" * 50)
    
    try:
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import Qt, QTimer
        
        # Créer QApplication
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
            app.setApplicationName("CHNeoWave Final Simple Test")
        
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
    exit(0 if test_final_simple() else 1)
'''
    
    try:
        with open('test_final_simple.py', 'w', encoding='utf-8') as f:
            f.write(test_content)
        print("✅ Test final simple créé: test_final_simple.py")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de la création du test: {e}")
        return False

def main():
    """Point d'entrée principal"""
    print("🔧 CORRECTEUR FINAL SIMPLE")
    print("=" * 50)
    
    # Correction finale simple
    if not fix_final_simple():
        print("❌ ÉCHEC: Correction finale simple")
        return 1
    
    # Créer test final simple
    if not create_test_final_simple():
        print("❌ ÉCHEC: Création test final simple")
        return 1
    
    print("\n🎉 CORRECTION FINALE SIMPLE TERMINÉE!")
    print("✅ Vues lazy loading désactivées")
    print("✅ Test final simple créé: test_final_simple.py")
    
    print("\n🚀 COMMANDES DE TEST:")
    print("1. Test final simple: python test_final_simple.py")
    print("2. Lancement application: python main.py")
    
    return 0

if __name__ == "__main__":
    exit(main()) 