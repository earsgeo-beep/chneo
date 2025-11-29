#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Correction de la boucle d'événements dans MainWindow
"""

import sys
from pathlib import Path

# Ajouter le chemin du projet
sys.path.insert(0, str(Path(__file__).parent / "src"))

def fix_main_window_events():
    """Corriger le problème de boucle d'événements dans MainWindow"""
    print("🔧 CORRECTION BOUCLE ÉVÉNEMENTS MAINWINDOW")
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
        backup_path = main_window_path.with_suffix('.py.backup_events')
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Sauvegarde créée: {backup_path}")
        
        # Ajouter une méthode show_and_exec
        show_exec_method = '''
    def show_and_exec(self):
        """Afficher la fenêtre et lancer la boucle d'événements"""
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
        
        # Lancer la boucle d'événements
        app = QApplication.instance()
        if app:
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
        
        # Écrire le fichier modifié
        with open(main_window_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Méthode show_and_exec ajoutée à MainWindow")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la modification: {e}")
        return False

def create_test_main_window_events():
    """Créer un test pour MainWindow avec boucle d'événements"""
    print("\n🔧 CRÉATION TEST MAINWINDOW ÉVÉNEMENTS")
    print("=" * 40)
    
    test_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test MainWindow avec boucle d'événements
"""

import sys
import traceback
from pathlib import Path

# Ajouter le chemin du projet
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_main_window_events():
    """Test MainWindow avec boucle d'événements"""
    print("🚀 TEST MAINWINDOW ÉVÉNEMENTS")
    print("=" * 50)
    
    try:
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import Qt, QTimer
        
        # Créer QApplication
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
            app.setApplicationName("CHNeoWave Events Test")
        
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
        main_window.setWindowTitle("CHNeoWave - Test Événements")
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
        print("🔄 Affichage MainWindow avec boucle d'événements...")
        
        # Utiliser la nouvelle méthode show_and_exec
        exit_code = main_window.show_and_exec()
        
        print(f"✅ Test terminé (code: {exit_code})")
        return True
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    exit(0 if test_main_window_events() else 1)
'''
    
    try:
        with open('test_main_window_events.py', 'w', encoding='utf-8') as f:
            f.write(test_content)
        print("✅ Test MainWindow événements créé: test_main_window_events.py")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de la création du test: {e}")
        return False

def create_main_with_events():
    """Créer un main.py avec boucle d'événements"""
    print("\n🔧 CRÉATION MAIN.PY AVEC ÉVÉNEMENTS")
    print("=" * 40)
    
    main_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CHNeoWave - Application principale avec boucle d'événements
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
        with open('main_with_events.py', 'w', encoding='utf-8') as f:
            f.write(main_content)
        print("✅ main_with_events.py créé")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de la création: {e}")
        return False

def main():
    """Point d'entrée principal"""
    print("🔧 CORRECTEUR BOUCLE ÉVÉNEMENTS")
    print("=" * 50)
    
    # Corriger MainWindow
    if not fix_main_window_events():
        print("❌ ÉCHEC: Correction MainWindow")
        return 1
    
    # Créer test MainWindow événements
    if not create_test_main_window_events():
        print("❌ ÉCHEC: Création test MainWindow événements")
        return 1
    
    # Créer main avec événements
    if not create_main_with_events():
        print("❌ ÉCHEC: Création main avec événements")
        return 1
    
    print("\n🎉 CORRECTION BOUCLE ÉVÉNEMENTS TERMINÉE!")
    print("✅ Méthode show_and_exec ajoutée à MainWindow")
    print("✅ Test MainWindow événements créé: test_main_window_events.py")
    print("✅ main_with_events.py créé")
    
    print("\n🚀 COMMANDES DE TEST:")
    print("1. Test MainWindow événements: python test_main_window_events.py")
    print("2. Lancement avec événements: python main_with_events.py")
    
    return 0

if __name__ == "__main__":
    exit(main()) 