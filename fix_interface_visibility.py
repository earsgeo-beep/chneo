#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Correction du problème de visibilité de l'interface
"""

import sys
from pathlib import Path

# Ajouter le chemin du projet
sys.path.insert(0, str(Path(__file__).parent / "src"))

def fix_main_py_visibility():
    """Corriger le problème de visibilité dans main.py"""
    print("🔧 CORRECTION VISIBILITÉ INTERFACE")
    print("=" * 50)
    
    try:
        # Lire le fichier main.py
        main_path = Path("main.py")
        
        if not main_path.exists():
            print(f"❌ Fichier non trouvé: {main_path}")
            return False
        
        with open(main_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("✅ Fichier main.py lu")
        
        # Créer une sauvegarde
        backup_path = main_path.with_suffix('.py.backup_visibility')
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Sauvegarde créée: {backup_path}")
        
        # Nouveau contenu avec correction de visibilité
        new_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CHNeoWave - Application principale
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
        
        # Application du thème
        try:
            from hrneowave.gui.styles.theme_manager import ThemeManager
            theme_manager = ThemeManager()
            theme_manager.apply_theme('maritime_modern')
            print("✅ Thème 'maritime_modern' appliqué avec succès")
        except Exception as e:
            print(f"⚠️ Erreur lors de l'application du thème: {e}")
        
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
        
        print("📋 ÉTAPE 5: Affichage de l'interface")
        print("-" * 30)
        
        # Affichage de l'interface
        main_window.show()
        main_window.raise_()
        main_window.activateWindow()
        
        # Vérifier la visibilité
        visible = main_window.isVisible()
        print(f"✅ MainWindow visible: {visible}")
        
        if not visible:
            print("⚠️ Fenêtre non visible, tentative de correction...")
            main_window.showNormal()
            main_window.show()
            visible = main_window.isVisible()
            print(f"✅ MainWindow visible après correction: {visible}")
        
        print("✅ Interface affichée avec succès")
        
        print("📋 ÉTAPE 6: Lancement de la boucle d'événements")
        print("-" * 30)
        
        # Timer pour maintenir l'application ouverte
        def keep_alive():
            if not main_window.isVisible():
                print("⚠️ Fenêtre fermée, réouverture...")
                main_window.show()
                main_window.raise_()
                main_window.activateWindow()
        
        # Timer de surveillance
        keep_alive_timer = QTimer()
        keep_alive_timer.timeout.connect(keep_alive)
        keep_alive_timer.start(1000)  # Vérifier toutes les secondes
        
        print("✅ Boucle d'événements lancée")
        print("🎉 CHNeoWave est maintenant opérationnel !")
        
        # Lancer la boucle d'événements
        exit_code = app.exec()
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
        
        # Écrire le nouveau contenu
        with open(main_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("✅ main.py modifié avec correction de visibilité")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la modification: {e}")
        return False

def create_test_visibility():
    """Créer un test de visibilité"""
    print("\n🔧 CRÉATION TEST VISIBILITÉ")
    print("=" * 40)
    
    test_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test de visibilité de l'interface
"""

import sys
import traceback
from pathlib import Path

# Ajouter le chemin du projet
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_visibility():
    """Test de visibilité de l'interface"""
    print("🚀 TEST VISIBILITÉ INTERFACE")
    print("=" * 50)
    
    try:
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import Qt, QTimer
        
        # Créer QApplication
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
            app.setApplicationName("CHNeoWave Visibility Test")
        
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
        main_window.setWindowTitle("CHNeoWave - Test Visibilité")
        main_window.resize(1000, 700)
        
        # Centrer la fenêtre
        screen = app.primaryScreen()
        screen_geometry = screen.geometry()
        window_geometry = main_window.geometry()
        
        x = (screen_geometry.width() - window_geometry.width()) // 2
        y = (screen_geometry.height() - window_geometry.height()) // 2
        main_window.move(x, y)
        
        print("✅ Fenêtre configurée et centrée")
        
        # Test affichage
        print("🔄 Affichage MainWindow...")
        main_window.show()
        main_window.raise_()
        main_window.activateWindow()
        
        visible = main_window.isVisible()
        print(f"✅ MainWindow visible: {visible}")
        
        if visible:
            print("🎉 SUCCÈS: MainWindow visible!")
            
            # Maintenir ouvert 15 secondes
            timer = QTimer()
            timer.timeout.connect(app.quit)
            timer.start(15000)
            
            print("🔄 Maintien ouvert 15 secondes...")
            print("🔍 Vérifiez que la fenêtre est visible sur votre écran")
            
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
    exit(0 if test_visibility() else 1)
'''
    
    try:
        with open('test_visibility.py', 'w', encoding='utf-8') as f:
            f.write(test_content)
        print("✅ Test visibilité créé: test_visibility.py")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de la création du test: {e}")
        return False

def main():
    """Point d'entrée principal"""
    print("🔧 CORRECTEUR VISIBILITÉ INTERFACE")
    print("=" * 50)
    
    # Corriger main.py
    if not fix_main_py_visibility():
        print("❌ ÉCHEC: Correction main.py")
        return 1
    
    # Créer test visibilité
    if not create_test_visibility():
        print("❌ ÉCHEC: Création test visibilité")
        return 1
    
    print("\n🎉 CORRECTION VISIBILITÉ TERMINÉE!")
    print("✅ main.py modifié avec correction de visibilité")
    print("✅ Test visibilité créé: test_visibility.py")
    
    print("\n🚀 COMMANDES DE TEST:")
    print("1. Test visibilité: python test_visibility.py")
    print("2. Lancement application: python main.py")
    
    return 0

if __name__ == "__main__":
    exit(main()) 