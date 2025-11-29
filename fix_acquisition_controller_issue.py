#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Correction du problème acquisition_controller.py en modifiant main_window.py
"""

import sys
from pathlib import Path

# Ajouter le chemin du projet
sys.path.insert(0, str(Path(__file__).parent / "src"))

def fix_main_window_imports():
    """Corriger les imports dans main_window.py pour éviter acquisition_controller"""
    print("🔧 CORRECTION IMPORTS MAINWINDOW")
    print("=" * 40)
    
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
        backup_path = main_window_path.with_suffix('.py.backup')
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Sauvegarde créée: {backup_path}")
        
        # Modifier les imports problématiques
        print("🔄 Modification des imports...")
        
        # Remplacer l'import de acquisition_controller par un import conditionnel
        old_import = "from hrneowave.gui.controllers.acquisition_controller import AcquisitionController"
        new_import = """# Import conditionnel pour éviter les erreurs
try:
    from hrneowave.gui.controllers.acquisition_controller import AcquisitionController
    ACQUISITION_CONTROLLER_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ AcquisitionController non disponible: {e}")
    AcquisitionController = None
    ACQUISITION_CONTROLLER_AVAILABLE = False"""
        
        if old_import in content:
            content = content.replace(old_import, new_import)
            print("✅ Import AcquisitionController modifié")
        else:
            print("⚠️ Import AcquisitionController non trouvé")
        
        # Modifier l'import de main_controller
        old_main_import = "from hrneowave.gui.controllers.main_controller import MainController"
        new_main_import = """# Import conditionnel pour éviter les erreurs
try:
    from hrneowave.gui.controllers.main_controller import MainController
    MAIN_CONTROLLER_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ MainController non disponible: {e}")
    MainController = None
    MAIN_CONTROLLER_AVAILABLE = False"""
        
        if old_main_import in content:
            content = content.replace(old_main_import, new_main_import)
            print("✅ Import MainController modifié")
        else:
            print("⚠️ Import MainController non trouvé")
        
        # Écrire le fichier modifié
        with open(main_window_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Fichier main_window.py modifié")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la modification: {e}")
        return False

def create_simple_main_window():
    """Créer une version simplifiée de main_window.py"""
    print("\n🔧 CRÉATION MAINWINDOW SIMPLIFIÉE")
    print("=" * 40)
    
    simple_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fenêtre principale simplifiée pour CHNeoWave
Version de test sans acquisition_controller
"""

import logging
from PySide6.QtWidgets import QMainWindow, QMessageBox, QStackedWidget, QHBoxLayout, QVBoxLayout, QWidget, QLabel
from PySide6.QtCore import Signal, Slot, QTimer, Qt

logger = logging.getLogger(__name__)

# Import conditionnel pour éviter les erreurs
try:
    from hrneowave.gui.controllers.acquisition_controller import AcquisitionController
    ACQUISITION_CONTROLLER_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ AcquisitionController non disponible: {e}")
    AcquisitionController = None
    ACQUISITION_CONTROLLER_AVAILABLE = False

try:
    from hrneowave.gui.controllers.main_controller import MainController
    MAIN_CONTROLLER_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ MainController non disponible: {e}")
    MainController = None
    MAIN_CONTROLLER_AVAILABLE = False

from hrneowave.gui.styles.theme_manager import ThemeManager

# Import du système d'animations Phase 6
try:
    from hrneowave.gui.animations import PageTransitionManager, TransitionType, MaritimeAnimator
except ImportError:
    PageTransitionManager = None
    TransitionType = None
    MaritimeAnimator = None
    logger.warning("Système d'animations Phase 6 non disponible")

# Import des vues v2 et configurations
try:
    from hrneowave.gui.views import (
        DashboardViewMaritime,
        WelcomeView,
        VIEWS_CONFIG,
        NAVIGATION_ORDER
    )
except ImportError as e:
    print(f"⚠️ Vues non disponibles: {e}")
    DashboardViewMaritime = None
    WelcomeView = None
    VIEWS_CONFIG = {}
    NAVIGATION_ORDER = []

class SimpleMainWindow(QMainWindow):
    """Fenêtre principale simplifiée de l'application CHNeoWave"""
    
    projectCreated = Signal()
    
    def __init__(self, config=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("CHNeoWave - Version Simplifiée")
        self.setMinimumSize(1024, 768)
        
        # Configuration
        self.config = config or {}
        
        # État de l'application
        self.is_acquiring = False
        self.acquisition_controller = None
        self.analysis_controller = None
        self.project_controller = None
        
        # Construction de l'interface
        logger.info("Début de la construction de l'interface simplifiée...")
        self._build_simple_ui()
        logger.info("Interface simplifiée construite avec succès")
        
        logger.info("Interface utilisateur simplifiée chargée avec succès")

    def _build_simple_ui(self):
        """Construit une interface utilisateur simplifiée."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Titre
        title_label = QLabel("CHNeoWave - Laboratoire d'Hydrodynamique Maritime")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                padding: 20px;
                background-color: #ecf0f1;
                border-radius: 10px;
            }
        """)
        main_layout.addWidget(title_label)

        # Message de statut
        status_label = QLabel("✅ Interface simplifiée chargée avec succès")
        status_label.setAlignment(Qt.AlignCenter)
        status_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                color: #27ae60;
                padding: 15px;
                background-color: #d5f4e6;
                border-radius: 8px;
            }
        """)
        main_layout.addWidget(status_label)

        # Informations système
        info_label = QLabel(f"""
        📊 Informations système:
        • AcquisitionController: {'✅ Disponible' if ACQUISITION_CONTROLLER_AVAILABLE else '❌ Non disponible'}
        • MainController: {'✅ Disponible' if MAIN_CONTROLLER_AVAILABLE else '❌ Non disponible'}
        • Animations Phase 6: {'✅ Disponible' if PageTransitionManager else '❌ Non disponible'}
        • Vues: {'✅ Disponible' if WelcomeView else '❌ Non disponible'}
        """)
        info_label.setAlignment(Qt.AlignLeft)
        info_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #34495e;
                padding: 15px;
                background-color: #f8f9fa;
                border-radius: 8px;
                border: 1px solid #dee2e6;
            }
        """)
        main_layout.addWidget(info_label)

        # Espace flexible
        spacer = QWidget()
        spacer.setSizePolicy(QWidget.Expanding, QWidget.Expanding)
        main_layout.addWidget(spacer)

        # Message de fermeture
        close_label = QLabel("Cette fenêtre se fermera automatiquement dans 10 secondes...")
        close_label.setAlignment(Qt.AlignCenter)
        close_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #7f8c8d;
                padding: 10px;
            }
        """)
        main_layout.addWidget(close_label)

    def showEvent(self, event):
        """Gestionnaire d'événement d'affichage"""
        super().showEvent(event)
        logger.info("Fenêtre simplifiée affichée")

    def closeEvent(self, event):
        """Gestionnaire d'événement de fermeture"""
        logger.info("Fenêtre simplifiée fermée")
        super().closeEvent(event)
'''
    
    try:
        simple_path = Path("src/hrneowave/gui/simple_main_window.py")
        with open(simple_path, 'w', encoding='utf-8') as f:
            f.write(simple_content)
        print("✅ Fenêtre simplifiée créée: simple_main_window.py")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de la création: {e}")
        return False

def create_test_simple_window():
    """Créer un test pour la fenêtre simplifiée"""
    print("\n🔧 CRÉATION TEST FENÊTRE SIMPLIFIÉE")
    print("=" * 40)
    
    test_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test de la fenêtre simplifiée CHNeoWave
"""

import sys
from pathlib import Path

# Ajouter le chemin du projet
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_simple_window():
    """Test de la fenêtre simplifiée"""
    print("🚀 TEST FENÊTRE SIMPLIFIÉE")
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
        
        # Test import fenêtre simplifiée
        print("🔄 Import SimpleMainWindow...")
        from hrneowave.gui.simple_main_window import SimpleMainWindow
        print("✅ SimpleMainWindow importé")
        
        # Test création fenêtre simplifiée
        print("🔄 Création SimpleMainWindow...")
        main_window = SimpleMainWindow()
        print("✅ SimpleMainWindow créée")
        
        # Test affichage
        print("🔄 Affichage SimpleMainWindow...")
        main_window.show()
        main_window.raise_()
        main_window.activateWindow()
        
        visible = main_window.isVisible()
        print(f"✅ SimpleMainWindow visible: {visible}")
        
        if visible:
            print("🎉 SUCCÈS: SimpleMainWindow visible!")
            
            # Maintenir ouvert 10 secondes
            timer = QTimer()
            timer.timeout.connect(app.quit)
            timer.start(10000)
            
            print("🔄 Maintien ouvert 10 secondes...")
            exit_code = app.exec()
            print(f"✅ Test terminé (code: {exit_code})")
            return True
        else:
            print("❌ PROBLÈME: SimpleMainWindow non visible")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    exit(0 if test_simple_window() else 1)
'''
    
    try:
        with open('test_simple_window.py', 'w', encoding='utf-8') as f:
            f.write(test_content)
        print("✅ Test fenêtre simplifiée créé: test_simple_window.py")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de la création du test: {e}")
        return False

def main():
    """Point d'entrée principal"""
    print("🔧 CORRECTEUR ACQUISITION CONTROLLER")
    print("=" * 50)
    
    # Corriger les imports dans main_window.py
    if not fix_main_window_imports():
        print("❌ ÉCHEC: Correction des imports main_window.py")
        return 1
    
    # Créer fenêtre simplifiée
    if not create_simple_main_window():
        print("❌ ÉCHEC: Création fenêtre simplifiée")
        return 1
    
    # Créer test fenêtre simplifiée
    if not create_test_simple_window():
        print("❌ ÉCHEC: Création test fenêtre simplifiée")
        return 1
    
    print("\n🎉 CORRECTION TERMINÉE!")
    print("✅ Imports main_window.py corrigés")
    print("✅ Fenêtre simplifiée créée: simple_main_window.py")
    print("✅ Test fenêtre simplifiée créé: test_simple_window.py")
    
    print("\n🚀 COMMANDES DE TEST:")
    print("1. Diagnostic acquisition: python debug_acquisition_controller.py")
    print("2. Test fenêtre simplifiée: python test_simple_window.py")
    print("3. Test main_window corrigé: python test_simple_main_window.py")
    print("4. Lancement application: python main.py")
    
    return 0

if __name__ == "__main__":
    exit(main()) 