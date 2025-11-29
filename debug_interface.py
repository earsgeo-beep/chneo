#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de diagnostic pour identifier pourquoi l'interface ne s'affiche pas
"""

import sys
import logging
import traceback
from pathlib import Path

# Configuration du logging pour debug
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('debug_interface.log')
    ]
)

log = logging.getLogger(__name__)

def test_complete_interface():
    """Test complet de l'interface CHNeoWave"""
    try:
        log.info("=== TEST COMPLET INTERFACE CHNEOWAVE ===")
        
        # Test d'importation
        log.info("1. Test d'importation des modules...")
        from PySide6.QtWidgets import QApplication
        from hrneowave.core.logging_config import setup_logging
        from hrneowave.gui.main_window import MainWindow
        from hrneowave.gui.styles.theme_manager import ThemeManager
        log.info("OK - Tous les modules importes avec succes")
        
        # Configuration logging
        log.info("2. Configuration du logging...")
        setup_logging()
        log.info("OK - Logging configure")
        
        # Création application
        log.info("3. Creation de QApplication...")
        app = QApplication(sys.argv)
        app.setApplicationName("CHNeoWave Debug")
        log.info("OK - QApplication creee")
        
        # Création ThemeManager
        log.info("4. Creation du ThemeManager...")
        theme_manager = ThemeManager(app)
        log.info("OK - ThemeManager cree")
        
        # Application du thème
        log.info("5. Application du theme maritime...")
        theme_manager.apply_theme('maritime_modern')
        log.info("OK - Theme applique")
        
        # Création MainWindow
        log.info("6. Creation de MainWindow...")
        main_window = MainWindow()
        log.info("OK - MainWindow creee")
        
        # Configuration fenêtre
        log.info("7. Configuration de la fenetre...")
        main_window.setWindowTitle("CHNeoWave - Test Interface")
        main_window.setGeometry(100, 100, 1200, 800)
        log.info("OK - Fenetre configuree")
        
        # Affichage
        log.info("8. Affichage de la fenetre...")
        main_window.show()
        main_window.raise_()
        main_window.activateWindow()
        
        # Vérifications
        log.info(f"Fenetre visible: {main_window.isVisible()}")
        log.info(f"Taille: {main_window.size()}")
        log.info(f"Position: {main_window.pos()}")
        log.info(f"Titre: {main_window.windowTitle()}")
        
        if main_window.isVisible():
            log.info("SUCCESS - Interface affichee avec succes!")
        else:
            log.warning("WARNING - Interface creee mais pas visible")
        
        # Attendre 5 secondes pour voir l'interface
        from PySide6.QtCore import QTimer
        timer = QTimer()
        timer.timeout.connect(app.quit)
        timer.start(5000)  # 5 secondes
        
        log.info("9. Demarrage de la boucle d'evenements (5 secondes)...")
        exit_code = app.exec()
        log.info(f"Application fermee avec code: {exit_code}")
        
        return True
        
    except Exception as e:
        log.error(f"ERREUR lors du test: {e}")
        log.error(traceback.format_exc())
        return False

def main():
    """Fonction principale de diagnostic"""
    try:
        if test_complete_interface():
            log.info("=== DIAGNOSTIC REUSSI ===")
            return 0
        else:
            log.error("=== DIAGNOSTIC ECHOUE ===")
            return 1
    except Exception as e:
        log.error(f"Erreur fatale: {e}")
        log.error(traceback.format_exc())
        return 1

if __name__ == "__main__":
    sys.exit(main())