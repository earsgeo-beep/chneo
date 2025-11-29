#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Correction du problème de visibilité de fenêtre CHNeoWave
"""

import sys
from pathlib import Path

# Ajouter le chemin du projet
sys.path.insert(0, str(Path(__file__).parent / "src"))

def fix_main_py():
    """Corriger le fichier main.py pour forcer l'affichage"""
    print("🔧 CORRECTION DU FICHIER MAIN.PY")
    print("=" * 40)
    
    main_py_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CHNeoWave - Point d'entrée principal
Logiciel d'acquisition et d'analyse de houle pour laboratoires maritimes

Version 1.1.0 - Correction visibilité fenêtre
"""

import sys
import logging
from pathlib import Path

# Configuration du logging centralisée
from hrneowave.core.logging_config import setup_logging
setup_logging()

log = logging.getLogger(__name__)

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QTimer
from hrneowave.gui.main_window import MainWindow
from hrneowave.gui.styles.theme_manager import ThemeManager

def main():
    """
    Point d'entrée principal de l'application CHNeoWave.
    Initialise et lance l'interface graphique avec correction de visibilité.
    """
    print("🚀 Lancement de CHNeoWave v1.1.0")
    print("=" * 50)
    
    log.info(f"Lancement de CHNeoWave v1.1.0")
    
    # Créer QApplication
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
        app.setApplicationName("CHNeoWave")
        app.setApplicationVersion("1.1.0")
        app.setOrganizationName("Laboratoire d'Hydrodynamique Maritime")
        app.setQuitOnLastWindowClosed(True)
        print("✅ QApplication créé")
    else:
        print("✅ QApplication existant réutilisé")

    try:
        # Appliquer le thème
        log.info("Initialisation du gestionnaire de thèmes...")
        theme_manager = ThemeManager(app)
        theme_manager.apply_theme('maritime_modern')
        print("✅ Thème maritime appliqué")

        # Créer MainWindow
        log.info("Création de la fenêtre principale...")
        main_window = MainWindow()
        log.info("MainWindow créée avec succès")
        print("✅ MainWindow créée")
        
        # CORRECTION CRITIQUE: Configuration de la fenêtre AVANT affichage
        main_window.setWindowTitle("CHNeoWave - Laboratoire d'Hydrodynamique Maritime")
        main_window.resize(1200, 800)
        
        # Centrer la fenêtre sur l'écran
        screen_geometry = app.primaryScreen().geometry()
        window_geometry = main_window.geometry()
        center_point = screen_geometry.center() - window_geometry.center()
        main_window.move(center_point)
        
        print("✅ Fenêtre configurée et centrée")
        
        # CORRECTION CRITIQUE: Séquence d'affichage robuste
        log.info("Affichage de la fenêtre principale.")
        print("🖥️ Affichage de l'interface...")
        
        # 1. Afficher la fenêtre
        main_window.show()
        print("✅ show() appelé")
        
        # 2. Forcer l'affichage
        main_window.raise_()
        main_window.activateWindow()
        print("✅ raise() et activateWindow() appelés")
        
        # 3. S'assurer que la fenêtre n'est pas minimisée
        if main_window.isMinimized():
            main_window.showNormal()
            print("✅ showNormal() appelé")
        
        # 4. Forcer l'état actif
        main_window.setWindowState(Qt.WindowActive)
        print("✅ setWindowState(WindowActive) appelé")
        
        # 5. Vérifications détaillées
        visible = main_window.isVisible()
        active = main_window.isActiveWindow()
        minimized = main_window.isMinimized()
        
        log.info(f"Fenêtre visible: {visible}, Taille: {main_window.size()}")
        log.info(f"Position de la fenêtre: {main_window.pos()}")
        log.info(f"État de la fenêtre: Active={active}, Minimized={minimized}")
        
        print(f"✅ Fenêtre visible: {visible}")
        print(f"✅ Position: {main_window.pos()}")
        print(f"✅ Taille: {main_window.size()}")
        print(f"✅ Active: {active}")
        print(f"✅ Minimized: {minimized}")
        
        # 6. Si toujours pas visible, essayer la maximisation
        if not visible:
            log.warning("La fenêtre n'est pas visible, tentative de maximisation...")
            print("⚠️ Tentative de maximisation...")
            main_window.showMaximized()
            
            # Vérifier à nouveau
            visible = main_window.isVisible()
            print(f"✅ Après showMaximized() - Visible: {visible}")
        
        # 7. Vérification finale
        if visible:
            print("🎉 SUCCÈS: CHNeoWave est visible à l'écran!")
            print("👀 L'interface devrait maintenant être affichée")
            
            # CORRECTION: Timer pour s'assurer que la fenêtre reste visible
            def ensure_visibility():
                if not main_window.isVisible():
                    print("⚠️ Fenêtre devenue invisible, tentative de restauration...")
                    main_window.show()
                    main_window.raise_()
                    main_window.activateWindow()
            
            # Timer de vérification toutes les 2 secondes
            visibility_timer = QTimer()
            visibility_timer.timeout.connect(ensure_visibility)
            visibility_timer.start(2000)
            
        else:
            print("❌ PROBLÈME: CHNeoWave n'est toujours pas visible")
            print("🔍 Tentative de diagnostic...")
            
            # Diagnostic supplémentaire
            screen_geometry = app.primaryScreen().geometry()
            window_geometry = main_window.geometry()
            
            print(f"✅ Géométrie écran: {screen_geometry}")
            print(f"✅ Géométrie fenêtre: {window_geometry}")
            
            if not screen_geometry.intersects(window_geometry):
                print("⚠️ Fenêtre en dehors de l'écran!")
                # Centrer la fenêtre
                main_window.move(screen_geometry.center() - window_geometry.center())
                main_window.show()
                print("✅ Fenêtre centrée et affichée")
            
            return 1
        
        log.info("Démarrage de la boucle d'événements de l'application.")
        print("🔄 Démarrage de la boucle d'événements...")
        
        # CORRECTION CRITIQUE: Démarrer la boucle d'événements
        exit_code = app.exec()
        
        log.info(f"Application terminée avec le code de sortie: {exit_code}")
        print(f"✅ CHNeoWave fermé (code: {exit_code})")
        return exit_code
        
    except Exception as e:
        log.critical(f"Une erreur critique a empêché le lancement de l'application: {e}", exc_info=True)
        print(f"❌ ERREUR CRITIQUE: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
'''
    
    try:
        with open('main.py', 'w', encoding='utf-8') as f:
            f.write(main_py_content)
        print("✅ main.py corrigé avec succès")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de la correction de main.py: {e}")
        return False

def create_test_launch_script():
    """Créer un script de test de lancement"""
    print("\n🔧 CRÉATION SCRIPT DE TEST")
    print("=" * 30)
    
    test_script_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test de lancement CHNeoWave avec correction de visibilité
"""

import sys
from pathlib import Path

# Ajouter le chemin du projet
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_launch():
    """Test de lancement avec correction de visibilité"""
    print("🚀 TEST LANCEMENT CHNEOWAVE")
    print("=" * 40)
    
    try:
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import Qt, QTimer
        from hrneowave.gui.main_window import MainWindow
        from hrneowave.gui.styles.theme_manager import ThemeManager
        
        # Créer QApplication
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
            app.setApplicationName("CHNeoWave Test")
            app.setQuitOnLastWindowClosed(True)
        
        # Appliquer le thème
        theme_manager = ThemeManager(app)
        theme_manager.apply_theme('maritime_modern')
        print("✅ Thème appliqué")
        
        # Créer MainWindow
        main_window = MainWindow()
        print("✅ MainWindow créée")
        
        # Configuration de la fenêtre
        main_window.setWindowTitle("CHNeoWave Test")
        main_window.resize(1200, 800)
        
        # Centrer la fenêtre
        screen_geometry = app.primaryScreen().geometry()
        window_geometry = main_window.geometry()
        center_point = screen_geometry.center() - window_geometry.center()
        main_window.move(center_point)
        
        # Séquence d'affichage robuste
        main_window.show()
        main_window.raise_()
        main_window.activateWindow()
        main_window.setWindowState(Qt.WindowActive)
        
        print("✅ Fenêtre affichée et configurée")
        
        # Vérifications
        visible = main_window.isVisible()
        active = main_window.isActiveWindow()
        
        print(f"✅ Visible: {visible}")
        print(f"✅ Active: {active}")
        print(f"✅ Position: {main_window.pos()}")
        print(f"✅ Taille: {main_window.size()}")
        
        if visible:
            print("🎉 SUCCÈS: Interface visible!")
            
            # Maintenir ouvert 10 secondes
            timer = QTimer()
            timer.timeout.connect(app.quit)
            timer.start(10000)
            
            print("🔄 Maintien ouvert 10 secondes...")
            exit_code = app.exec()
            print(f"✅ Test terminé (code: {exit_code})")
            return True
        else:
            print("❌ PROBLÈME: Interface non visible")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    exit(0 if test_launch() else 1)
'''
    
    try:
        with open('test_launch_corrected.py', 'w', encoding='utf-8') as f:
            f.write(test_script_content)
        print("✅ Script de test créé: test_launch_corrected.py")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de la création du script de test: {e}")
        return False

def main():
    """Point d'entrée principal"""
    print("🔧 CORRECTEUR DE VISIBILITÉ CHNEOWAVE")
    print("=" * 50)
    
    # Créer une sauvegarde
    try:
        from shutil import copy2
        copy2('main.py', 'main.py.backup')
        print("✅ Sauvegarde créée: main.py.backup")
    except Exception as e:
        print(f"⚠️ Impossible de créer la sauvegarde: {e}")
    
    # Corriger main.py
    if not fix_main_py():
        print("❌ ÉCHEC: Correction de main.py")
        return 1
    
    # Créer script de test
    if not create_test_launch_script():
        print("❌ ÉCHEC: Création du script de test")
        return 1
    
    print("\n🎉 CORRECTION TERMINÉE!")
    print("✅ main.py corrigé avec séquence d'affichage robuste")
    print("✅ Script de test créé: test_launch_corrected.py")
    
    print("\n🚀 COMMANDES DE TEST:")
    print("1. Test de lancement: python test_launch_corrected.py")
    print("2. Lancement application: python main.py")
    print("3. Diagnostic: python debug_window_visibility.py")
    
    return 0

if __name__ == "__main__":
    exit(main()) 