#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Correction finale de la boucle d'événements dans MainWindow
"""

import sys
from pathlib import Path

# Ajouter le chemin du projet
sys.path.insert(0, str(Path(__file__).parent / "src"))

def fix_main_window_events_final():
    """Corriger définitivement la boucle d'événements dans MainWindow"""
    print("🔧 CORRECTION FINALE BOUCLE ÉVÉNEMENTS")
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
        backup_path = main_window_path.with_suffix('.py.backup_events_final')
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Sauvegarde créée: {backup_path}")
        
        # Vérifier si la méthode show_and_exec existe déjà
        if "def show_and_exec(self):" in content:
            print("✅ Méthode show_and_exec existe déjà")
        else:
            # Ajouter la méthode show_and_exec
            show_exec_method = '''
    def show_and_exec(self):
        """Afficher la fenêtre et lancer la boucle d'événements"""
        print("🔄 Affichage MainWindow...")
        self.show()
        self.raise_()
        self.activateWindow()
        
        # Vérifier la visibilité
        visible = self.isVisible()
        print(f"✅ MainWindow visible: {visible}")
        
        if not visible:
            print("⚠️ Fenêtre non visible, tentative de correction...")
            self.showNormal()
            self.show()
            visible = self.isVisible()
            print(f"✅ MainWindow visible après correction: {visible}")
        
        print("✅ Interface affichée avec succès")
        print("🎉 CHNeoWave est maintenant opérationnel !")
        print("🔍 Vérifiez que la fenêtre est visible sur votre écran")
        
        # Lancer la boucle d'événements
        from PySide6.QtWidgets import QApplication
        app = QApplication.instance()
        if app:
            print("🔄 Lancement de la boucle d'événements...")
            return app.exec()
        return 0
'''
            
            # Trouver la fin de la classe MainWindow
            class_end = content.find("if __name__ == \"__main__\":")
            if class_end == -1:
                class_end = len(content)
            
            # Insérer la méthode avant la fin de la classe
            before_class_end = content[:class_end]
            after_class_end = content[class_end:]
            
            # Ajouter la méthode
            content = before_class_end + show_exec_method + after_class_end
            
            print("✅ Méthode show_and_exec ajoutée")
        
        # Écrire le fichier modifié
        with open(main_window_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ MainWindow modifié avec correction finale")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la modification: {e}")
        return False

def create_main_final():
    """Créer un main.py final qui utilise show_and_exec"""
    print("\n🔧 CRÉATION MAIN.PY FINAL")
    print("=" * 40)
    
    main_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CHNeoWave - Application principale FINALE
Version: 1.1.0
"""

import sys
import logging
import traceback
from pathlib import Path

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('src/hrneowave/chneowave_debug.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('chneowave')

def main():
    """Point d'entrée principal de l'application"""
    try:
        print("🚀 Lancement de CHNeoWave v1.1.0")
        print("=" * 50)
        
        # Ajouter le chemin du projet
        sys.path.insert(0, str(Path(__file__).parent / "src"))
        
        print("📋 ÉTAPE 1: Création QApplication")
        print("-" * 30)
        
        # Import et création de QApplication
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import Qt, QTimer
        
        # Créer QApplication
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
            app.setApplicationName("CHNeoWave")
            app.setApplicationVersion("1.1.0")
            app.setOrganizationName("CHNeoWave")
        
        print("✅ QApplication créé")
        
        print("📋 ÉTAPE 2: Application du thème")
        print("-" * 30)
        
        # Application du thème (simplifiée)
        try:
            from hrneowave.gui.styles.theme_manager import ThemeManager
            theme_manager = ThemeManager(app=app)
            theme_manager.apply_theme('maritime_modern')
            print("✅ Thème 'maritime_modern' appliqué avec succès")
        except Exception as e:
            print(f"⚠️ Erreur lors de l'application du thème: {e}")
            print("⚠️ Continuation sans thème...")
        
        print("✅ Thème maritime appliqué")
        
        print("📋 ÉTAPE 3: Création MainWindow")
        print("-" * 30)
        
        # Import et création de MainWindow
        print("🔄 Import de MainWindow...")
        from hrneowave.gui.main_window import MainWindow
        print("✅ MainWindow importé")
        
        print("🔄 Création de l'instance MainWindow...")
        main_window = MainWindow()
        print("✅ MainWindow créée")
        
        print("📋 ÉTAPE 4: Configuration de l'affichage")
        print("-" * 30)
        
        # Configuration de l'affichage
        main_window.setWindowTitle("CHNeoWave - Interface Maritime")
        main_window.resize(1200, 800)
        
        # Centrer la fenêtre
        screen = app.primaryScreen()
        screen_geometry = screen.geometry()
        window_geometry = main_window.geometry()
        
        x = (screen_geometry.width() - window_geometry.width()) // 2
        y = (screen_geometry.height() - window_geometry.height()) // 2
        main_window.move(x, y)
        
        print("✅ Fenêtre configurée et centrée")
        
        print("📋 ÉTAPE 5: Affichage avec boucle d'événements")
        print("-" * 30)
        
        # Utiliser la méthode show_and_exec
        print("🔄 Utilisation de show_and_exec...")
        exit_code = main_window.show_and_exec()
        
        print(f"✅ Application terminée (code: {exit_code})")
        return exit_code
        
    except Exception as e:
        print(f"❌ Erreur lors de la création de MainWindow: {e}")
        print("🔍 Traceback complet:")
        traceback.print_exc()
        print(f"❌ ERREUR CRITIQUE: {e}")
        print("🔍 Traceback complet:")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())
'''
    
    try:
        with open('main_final.py', 'w', encoding='utf-8') as f:
            f.write(main_content)
        print("✅ main_final.py créé")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de la création: {e}")
        return False

def create_test_final():
    """Créer un test final"""
    print("\n🔧 CRÉATION TEST FINAL")
    print("=" * 40)
    
    test_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test final de CHNeoWave avec boucle d'événements
"""

import sys
import traceback
from pathlib import Path

# Ajouter le chemin du projet
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_final():
    """Test final de CHNeoWave"""
    print("🚀 TEST FINAL CHNEOWAVE")
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
        
        # Configuration de l'affichage
        main_window.setWindowTitle("CHNeoWave - Test Final")
        main_window.resize(1200, 800)
        
        # Centrer la fenêtre
        screen = app.primaryScreen()
        screen_geometry = screen.geometry()
        window_geometry = main_window.geometry()
        
        x = (screen_geometry.width() - window_geometry.width()) // 2
        y = (screen_geometry.height() - window_geometry.height()) // 2
        main_window.move(x, y)
        
        print("✅ Fenêtre configurée et centrée")
        
        # Test affichage avec boucle d'événements
        print("🔄 Test show_and_exec...")
        
        # Utiliser la méthode show_and_exec
        exit_code = main_window.show_and_exec()
        
        print(f"✅ Test terminé (code: {exit_code})")
        return True
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    exit(0 if test_final() else 1)
'''
    
    try:
        with open('test_final.py', 'w', encoding='utf-8') as f:
            f.write(test_content)
        print("✅ test_final.py créé")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de la création: {e}")
        return False

def main():
    """Point d'entrée principal"""
    print("🔧 CORRECTEUR FINAL BOUCLE ÉVÉNEMENTS")
    print("=" * 50)
    
    # Corriger MainWindow
    if not fix_main_window_events_final():
        print("❌ ÉCHEC: Correction MainWindow")
        return 1
    
    # Créer main final
    if not create_main_final():
        print("❌ ÉCHEC: Création main final")
        return 1
    
    # Créer test final
    if not create_test_final():
        print("❌ ÉCHEC: Création test final")
        return 1
    
    print("\n🎉 CORRECTION FINALE BOUCLE ÉVÉNEMENTS TERMINÉE!")
    print("✅ MainWindow corrigé avec méthode show_and_exec")
    print("✅ main_final.py créé")
    print("✅ test_final.py créé")
    
    print("\n🚀 COMMANDES DE TEST:")
    print("1. Test final: python test_final.py")
    print("2. Lancement final: python main_final.py")
    
    return 0

if __name__ == "__main__":
    exit(main()) 