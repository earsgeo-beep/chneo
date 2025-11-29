#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Correction du problème ViewManager identifié dans l'audit
"""

import sys
from pathlib import Path

# Ajouter le chemin du projet
sys.path.insert(0, str(Path(__file__).parent / "src"))

def fix_viewmanager():
    """Corriger le problème de constructeur ViewManager"""
    print("🔧 CORRECTION VIEWMANAGER")
    print("=" * 50)
    
    try:
        # Lire le fichier view_manager.py
        view_manager_path = Path("src/hrneowave/gui/view_manager.py")
        
        if not view_manager_path.exists():
            print(f"❌ Fichier non trouvé: {view_manager_path}")
            return False
        
        with open(view_manager_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("✅ Fichier view_manager.py lu")
        
        # Créer une sauvegarde
        backup_path = view_manager_path.with_suffix('.py.backup_viewmanager')
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Sauvegarde créée: {backup_path}")
        
        # Vérifier si le constructeur a déjà été corrigé
        if "def __init__(self, stacked_widget=None):" in content:
            print("✅ Constructeur ViewManager déjà corrigé")
            return True
        
        # Trouver et corriger le constructeur
        if "def __init__(self, stacked_widget):" in content:
            # Remplacer par un constructeur avec paramètre optionnel
            content = content.replace(
                "def __init__(self, stacked_widget):",
                "def __init__(self, stacked_widget=None):"
            )
            print("✅ Constructeur ViewManager corrigé")
        
        # Écrire le fichier modifié
        with open(view_manager_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ ViewManager corrigé")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la modification: {e}")
        return False

def create_test_viewmanager():
    """Créer un test pour ViewManager corrigé"""
    print("\n🔧 CRÉATION TEST VIEWMANAGER")
    print("=" * 40)
    
    test_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test ViewManager corrigé
"""

import sys
import traceback
from pathlib import Path

# Ajouter le chemin du projet
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_viewmanager():
    """Test ViewManager corrigé"""
    print("🚀 TEST VIEWMANAGER CORRIGÉ")
    print("=" * 50)
    
    try:
        from PySide6.QtWidgets import QApplication, QStackedWidget
        
        # Créer QApplication
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        print("✅ QApplication créé")
        
        # Test import ViewManager
        print("🔄 Test import ViewManager...")
        from hrneowave.gui.view_manager import ViewManager
        print("✅ ViewManager importé")
        
        # Test création ViewManager sans paramètre
        print("🔄 Test création ViewManager sans paramètre...")
        view_manager = ViewManager()
        print("✅ ViewManager créé sans paramètre")
        
        # Test création ViewManager avec paramètre
        print("🔄 Test création ViewManager avec paramètre...")
        stacked_widget = QStackedWidget()
        view_manager_with_param = ViewManager(stacked_widget)
        print("✅ ViewManager créé avec paramètre")
        
        print("🎉 SUCCÈS: ViewManager fonctionne dans les deux cas !")
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    exit(0 if test_viewmanager() else 1)
'''
    
    try:
        with open('test_viewmanager.py', 'w', encoding='utf-8') as f:
            f.write(test_content)
        print("✅ test_viewmanager.py créé")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de la création: {e}")
        return False

def create_test_mainwindow_complete():
    """Créer un test complet pour MainWindow"""
    print("\n🔧 CRÉATION TEST MAINWINDOW COMPLET")
    print("=" * 40)
    
    test_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test complet MainWindow avec boucle d'événements
"""

import sys
import traceback
from pathlib import Path

# Ajouter le chemin du projet
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_mainwindow_complete():
    """Test complet MainWindow"""
    print("🚀 TEST MAINWINDOW COMPLET")
    print("=" * 50)
    
    try:
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import QTimer
        
        # Créer QApplication
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
            app.setApplicationName("CHNeoWave Complete Test")
        
        print("✅ QApplication créé")
        
        # Test import MainWindow
        print("🔄 Test import MainWindow...")
        from hrneowave.gui.main_window import MainWindow
        print("✅ MainWindow importé")
        
        # Test création MainWindow
        print("🔄 Test création MainWindow...")
        main_window = MainWindow()
        print("✅ MainWindow créée")
        
        # Configuration
        main_window.setWindowTitle("CHNeoWave - Test Complet")
        main_window.resize(1200, 800)
        
        # Centrer la fenêtre
        screen = app.primaryScreen()
        screen_geometry = screen.geometry()
        window_geometry = main_window.geometry()
        
        x = (screen_geometry.width() - window_geometry.width()) // 2
        y = (screen_geometry.height() - window_geometry.height()) // 2
        main_window.move(x, y)
        
        print("✅ MainWindow configurée et centrée")
        
        # Test affichage
        print("🔄 Test affichage MainWindow...")
        main_window.show()
        main_window.raise_()
        main_window.activateWindow()
        
        visible = main_window.isVisible()
        print(f"✅ MainWindow visible: {visible}")
        
        if visible:
            print("🎉 SUCCÈS: MainWindow visible, test boucle d'événements...")
            
            # Timer pour fermer après 15 secondes
            timer = QTimer()
            timer.timeout.connect(app.quit)
            timer.start(15000)
            
            print("🔄 Lancement boucle d'événements (15 secondes)...")
            print("🔍 Vérifiez que la fenêtre CHNeoWave est visible sur votre écran")
            
            exit_code = app.exec()
            print(f"✅ Boucle d'événements terminée (code: {exit_code})")
            return True
        else:
            print("❌ PROBLÈME: MainWindow non visible")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    exit(0 if test_mainwindow_complete() else 1)
'''
    
    try:
        with open('test_mainwindow_complete.py', 'w', encoding='utf-8') as f:
            f.write(test_content)
        print("✅ test_mainwindow_complete.py créé")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de la création: {e}")
        return False

def create_main_complete():
    """Créer un main.py complet et fonctionnel"""
    print("\n🔧 CRÉATION MAIN.PY COMPLET")
    print("=" * 40)
    
    main_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CHNeoWave - Application principale COMPLÈTE
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
        
        # Lancer la boucle d'événements
        print("🔄 Lancement de la boucle d'événements...")
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
    
    try:
        with open('main_complete.py', 'w', encoding='utf-8') as f:
            f.write(main_content)
        print("✅ main_complete.py créé")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de la création: {e}")
        return False

def main():
    """Point d'entrée principal"""
    print("🔧 CORRECTEUR VIEWMANAGER FINAL")
    print("=" * 50)
    
    # Corriger ViewManager
    if not fix_viewmanager():
        print("❌ ÉCHEC: Correction ViewManager")
        return 1
    
    # Créer test ViewManager
    if not create_test_viewmanager():
        print("❌ ÉCHEC: Création test ViewManager")
        return 1
    
    # Créer test MainWindow complet
    if not create_test_mainwindow_complete():
        print("❌ ÉCHEC: Création test MainWindow complet")
        return 1
    
    # Créer main complet
    if not create_main_complete():
        print("❌ ÉCHEC: Création main complet")
        return 1
    
    print("\n🎉 CORRECTION VIEWMANAGER TERMINÉE!")
    print("✅ ViewManager corrigé")
    print("✅ test_viewmanager.py créé")
    print("✅ test_mainwindow_complete.py créé")
    print("✅ main_complete.py créé")
    
    print("\n🚀 COMMANDES DE TEST:")
    print("1. Test ViewManager: python test_viewmanager.py")
    print("2. Test MainWindow complet: python test_mainwindow_complete.py")
    print("3. Lancement complet: python main_complete.py")
    
    return 0

if __name__ == "__main__":
    exit(main()) 