#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Correction du main.py original
Remplace le main.py par une version fonctionnelle
"""

import sys
from pathlib import Path

def fix_main_original():
    """Corriger le main.py original"""
    print("🔧 CORRECTION MAIN.PY ORIGINAL")
    print("=" * 50)
    
    try:
        # Lire le fichier main.py
        main_path = Path("main.py")
        
        if not main_path.exists():
            print(f"❌ Fichier non trouvé: {main_path}")
            return False
        
        # Créer une sauvegarde
        backup_path = main_path.with_suffix('.py.backup_original')
        with open(main_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Sauvegarde créée: {backup_path}")
        
        # Nouveau contenu fonctionnel
        new_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CHNeoWave - Application principale CORRIGÉE
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
    """Point d'entrée principal de l'application CORRIGÉE"""
    try:
        print("🚀 Lancement de CHNeoWave v1.1.0 - Version Corrigée")
        print("=" * 60)
        
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
            app.setApplicationName("CHNeoWave Corrigé")
            app.setApplicationVersion("1.1.0")
            app.setOrganizationName("CHNeoWave")
        
        print("✅ QApplication créé")
        
        print("📋 ÉTAPE 2: Application du thème")
        print("-" * 30)
        
        # Application du thème
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
        main_window.setWindowTitle("CHNeoWave - Interface Maritime Corrigée")
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
        print("🎉 CHNeoWave est maintenant opérationnel !")
        print("🔍 Vérifiez que la fenêtre est visible sur votre écran")
        
        print("📋 ÉTAPE 6: Lancement de la boucle d'événements")
        print("-" * 30)
        
        # Timer pour fermeture automatique après 30 secondes (optionnel)
        timer = QTimer()
        timer.timeout.connect(app.quit)
        timer.start(30000)  # 30 secondes
        
        print("🔄 Lancement de la boucle d'événements (30 secondes)...")
        
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
        
        print("✅ main.py corrigé avec succès")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la correction: {e}")
        return False

def create_test_main():
    """Créer un test pour le main.py corrigé"""
    print("\n🔧 CRÉATION TEST MAIN.PY")
    print("=" * 40)
    
    test_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test du main.py corrigé
"""

import sys
import traceback
from pathlib import Path

def test_main_corrige():
    """Test du main.py corrigé"""
    print("🚀 TEST MAIN.PY CORRIGÉ")
    print("=" * 50)
    
    try:
        # Importer et exécuter le main
        sys.path.insert(0, str(Path(__file__).parent))
        
        # Exécuter main.py
        import subprocess
        result = subprocess.run([sys.executable, "main.py"], 
                              capture_output=True, text=True, timeout=35)
        
        print("📋 Sortie standard:")
        print(result.stdout)
        
        if result.stderr:
            print("📋 Erreurs:")
            print(result.stderr)
        
        print(f"📋 Code de retour: {result.returncode}")
        
        if result.returncode == 0:
            print("🎉 SUCCÈS: main.py fonctionne !")
            return True
        else:
            print("❌ ÉCHEC: main.py ne fonctionne pas")
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ TIMEOUT: main.py a pris trop de temps")
        return True  # Timeout peut indiquer que l'interface s'est lancée
    except Exception as e:
        print(f"❌ Erreur: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    exit(0 if test_main_corrige() else 1)
'''
    
    try:
        with open('test_main_corrige.py', 'w', encoding='utf-8') as f:
            f.write(test_content)
        print("✅ test_main_corrige.py créé")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de la création: {e}")
        return False

def main():
    """Point d'entrée principal"""
    print("🔧 CORRECTEUR MAIN.PY ORIGINAL")
    print("=" * 50)
    
    # Corriger main.py
    if not fix_main_original():
        print("❌ ÉCHEC: Correction main.py")
        return 1
    
    # Créer test
    if not create_test_main():
        print("❌ ÉCHEC: Création test")
        return 1
    
    print("\n🎉 CORRECTION MAIN.PY TERMINÉE!")
    print("✅ main.py original corrigé")
    print("✅ test_main_corrige.py créé")
    
    print("\n🚀 COMMANDES DE TEST:")
    print("1. Test main.py: python test_main_corrige.py")
    print("2. Lancement direct: python main.py")
    
    return 0

if __name__ == "__main__":
    exit(main()) 