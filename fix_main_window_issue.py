#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Correction du problème de construction MainWindow CHNeoWave
"""

import sys
from pathlib import Path

# Ajouter le chemin du projet
sys.path.insert(0, str(Path(__file__).parent / "src"))

def fix_main_py_with_debug():
    """Corriger le fichier main.py avec debug détaillé"""
    print("🔧 CORRECTION MAIN.PY AVEC DEBUG DÉTAILLÉ")
    print("=" * 50)
    
    main_py_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CHNeoWave - Point d'entrée principal
Logiciel d'acquisition et d'analyse de houle pour laboratoires maritimes

Version 1.1.0 - Correction avec debug détaillé
"""

import sys
import logging
import traceback
from pathlib import Path

# Configuration du logging centralisée
from hrneowave.core.logging_config import setup_logging
setup_logging()

log = logging.getLogger(__name__)

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QTimer

def main():
    """
    Point d'entrée principal de l'application CHNeoWave.
    Initialise et lance l'interface graphique avec debug détaillé.
    """
    print("🚀 Lancement de CHNeoWave v1.1.0")
    print("=" * 50)
    
    log.info(f"Lancement de CHNeoWave v1.1.0")
    
    # Créer QApplication
    print("📋 ÉTAPE 1: Création QApplication")
    print("-" * 30)
    
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
        print("📋 ÉTAPE 2: Application du thème")
        print("-" * 30)
        
        log.info("Initialisation du gestionnaire de thèmes...")
        from hrneowave.gui.styles.theme_manager import ThemeManager
        theme_manager = ThemeManager(app)
        theme_manager.apply_theme('maritime_modern')
        print("✅ Thème maritime appliqué")

        # Créer MainWindow avec debug détaillé
        print("📋 ÉTAPE 3: Création MainWindow")
        print("-" * 30)
        
        log.info("Création de la fenêtre principale...")
        
        try:
            print("🔄 Import de MainWindow...")
            from hrneowave.gui.main_window import MainWindow
            print("✅ MainWindow importé")
            
            print("🔄 Création de l'instance MainWindow...")
            main_window = MainWindow()
            print("✅ MainWindow créée")
            
            log.info("MainWindow créée avec succès")
            
        except Exception as e:
            log.error(f"Erreur lors de la création de MainWindow: {e}", exc_info=True)
            print(f"❌ Erreur MainWindow: {e}")
            print("🔍 Traceback complet:")
            traceback.print_exc()
            raise
        
        # Configuration de la fenêtre
        print("📋 ÉTAPE 4: Configuration de la fenêtre")
        print("-" * 30)
        
        try:
            main_window.setWindowTitle("CHNeoWave - Laboratoire d'Hydrodynamique Maritime")
            main_window.resize(1200, 800)
            
            # Centrer la fenêtre sur l'écran
            screen_geometry = app.primaryScreen().geometry()
            window_geometry = main_window.geometry()
            center_point = screen_geometry.center() - window_geometry.center()
            main_window.move(center_point)
            
            print("✅ Fenêtre configurée et centrée")
            
        except Exception as e:
            log.error(f"Erreur lors de la configuration de la fenêtre: {e}", exc_info=True)
            print(f"❌ Erreur configuration fenêtre: {e}")
            traceback.print_exc()
        
        # Affichage de la fenêtre
        print("📋 ÉTAPE 5: Affichage de la fenêtre")
        print("-" * 30)
        
        log.info("Affichage de la fenêtre principale.")
        print("🖥️ Affichage de l'interface...")
        
        try:
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
            
        except Exception as e:
            log.error(f"Erreur lors de l'affichage de la fenêtre: {e}", exc_info=True)
            print(f"❌ Erreur affichage fenêtre: {e}")
            traceback.print_exc()
        
        # Vérifications détaillées
        print("📋 ÉTAPE 6: Vérifications détaillées")
        print("-" * 30)
        
        try:
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
            
        except Exception as e:
            log.error(f"Erreur lors des vérifications: {e}", exc_info=True)
            print(f"❌ Erreur vérifications: {e}")
            traceback.print_exc()
        
        # Si toujours pas visible, essayer la maximisation
        if not visible:
            print("📋 ÉTAPE 7: Tentative de maximisation")
            print("-" * 30)
            
            try:
                log.warning("La fenêtre n'est pas visible, tentative de maximisation...")
                print("⚠️ Tentative de maximisation...")
                main_window.showMaximized()
                
                # Vérifier à nouveau
                visible = main_window.isVisible()
                print(f"✅ Après showMaximized() - Visible: {visible}")
                
            except Exception as e:
                log.error(f"Erreur lors de la maximisation: {e}", exc_info=True)
                print(f"❌ Erreur maximisation: {e}")
                traceback.print_exc()
        
        # Vérification finale
        print("📋 ÉTAPE 8: Vérification finale")
        print("-" * 30)
        
        if visible:
            print("🎉 SUCCÈS: CHNeoWave est visible à l'écran!")
            print("👀 L'interface devrait maintenant être affichée")
            
            # Timer pour s'assurer que la fenêtre reste visible
            def ensure_visibility():
                try:
                    if not main_window.isVisible():
                        print("⚠️ Fenêtre devenue invisible, tentative de restauration...")
                        main_window.show()
                        main_window.raise_()
                        main_window.activateWindow()
                except Exception as e:
                    print(f"❌ Erreur dans ensure_visibility: {e}")
            
            # Timer de vérification toutes les 2 secondes
            visibility_timer = QTimer()
            visibility_timer.timeout.connect(ensure_visibility)
            visibility_timer.start(2000)
            
        else:
            print("❌ PROBLÈME: CHNeoWave n'est toujours pas visible")
            print("🔍 Tentative de diagnostic...")
            
            try:
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
                    
            except Exception as e:
                log.error(f"Erreur lors du diagnostic: {e}", exc_info=True)
                print(f"❌ Erreur diagnostic: {e}")
                traceback.print_exc()
            
            return 1
        
        # Démarrage de la boucle d'événements
        print("📋 ÉTAPE 9: Démarrage boucle d'événements")
        print("-" * 30)
        
        log.info("Démarrage de la boucle d'événements de l'application.")
        print("🔄 Démarrage de la boucle d'événements...")
        
        try:
            # CORRECTION CRITIQUE: Démarrer la boucle d'événements
            exit_code = app.exec()
            
            log.info(f"Application terminée avec le code de sortie: {exit_code}")
            print(f"✅ CHNeoWave fermé (code: {exit_code})")
            return exit_code
            
        except Exception as e:
            log.error(f"Erreur lors de la boucle d'événements: {e}", exc_info=True)
            print(f"❌ Erreur boucle d'événements: {e}")
            traceback.print_exc()
            return 1
        
    except Exception as e:
        log.critical(f"Une erreur critique a empêché le lancement de l'application: {e}", exc_info=True)
        print(f"❌ ERREUR CRITIQUE: {e}")
        print("🔍 Traceback complet:")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
'''
    
    try:
        with open('main.py', 'w', encoding='utf-8') as f:
            f.write(main_py_content)
        print("✅ main.py corrigé avec debug détaillé")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de la correction de main.py: {e}")
        return False

def create_simple_test():
    """Créer un test simple pour isoler le problème"""
    print("\n🔧 CRÉATION TEST SIMPLE")
    print("=" * 30)
    
    test_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test simple pour isoler le problème MainWindow
"""

import sys
from pathlib import Path

# Ajouter le chemin du projet
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_simple_main_window():
    """Test simple de MainWindow"""
    print("🚀 TEST SIMPLE MAINWINDOW")
    print("=" * 40)
    
    try:
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import Qt, QTimer
        
        # Créer QApplication
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
            app.setApplicationName("CHNeoWave Simple Test")
        
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
            
            # Maintenir ouvert 5 secondes
            timer = QTimer()
            timer.timeout.connect(app.quit)
            timer.start(5000)
            
            print("🔄 Maintien ouvert 5 secondes...")
            exit_code = app.exec()
            print(f"✅ Test terminé (code: {exit_code})")
            return True
        else:
            print("❌ PROBLÈME: MainWindow non visible")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    exit(0 if test_simple_main_window() else 1)
'''
    
    try:
        with open('test_simple_main_window.py', 'w', encoding='utf-8') as f:
            f.write(test_content)
        print("✅ Test simple créé: test_simple_main_window.py")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de la création du test simple: {e}")
        return False

def main():
    """Point d'entrée principal"""
    print("🔧 CORRECTEUR MAINWINDOW CHNEOWAVE")
    print("=" * 50)
    
    # Créer une sauvegarde
    try:
        from shutil import copy2
        copy2('main.py', 'main.py.backup2')
        print("✅ Sauvegarde créée: main.py.backup2")
    except Exception as e:
        print(f"⚠️ Impossible de créer la sauvegarde: {e}")
    
    # Corriger main.py
    if not fix_main_py_with_debug():
        print("❌ ÉCHEC: Correction de main.py")
        return 1
    
    # Créer test simple
    if not create_simple_test():
        print("❌ ÉCHEC: Création du test simple")
        return 1
    
    print("\n🎉 CORRECTION TERMINÉE!")
    print("✅ main.py corrigé avec debug détaillé")
    print("✅ Test simple créé: test_simple_main_window.py")
    
    print("\n🚀 COMMANDES DE TEST:")
    print("1. Test simple: python test_simple_main_window.py")
    print("2. Diagnostic construction: python debug_main_window_construction.py")
    print("3. Lancement application: python main.py")
    
    return 0

if __name__ == "__main__":
    exit(main()) 