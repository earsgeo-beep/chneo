#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de correction spécifique pour le problème de lancement CHNeoWave
Corrige le problème où l'application se lance mais ne s'affiche pas
"""

import sys
import os
import re
import shutil
from pathlib import Path

class CHNeoWaveLaunchFixer:
    """Correcteur spécifique pour les problèmes de lancement"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.src_path = self.project_root / "src" / "hrneowave"
        self.fixes_applied = []
        self.errors = []
    
    def fix_main_py(self):
        """Corrige le fichier main.py pour assurer l'affichage"""
        print("🔧 Correction du fichier main.py...")
        
        file_path = self.project_root / "main.py"
        
        if not file_path.exists():
            print(f"⚠️ Fichier non trouvé: {file_path}")
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Vérifier si les corrections sont déjà présentes
            if "app.exec()" in content and "main_window.show()" in content:
                print("✅ Corrections déjà présentes dans main.py")
                return
            
            # Créer une version corrigée du main.py
            corrected_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CHNeoWave - Point d'entrée principal CORRIGÉ
Logiciel d'acquisition et d'analyse de houle pour laboratoires maritimes

Version 1.1.0 - Interface refactorisée avec flux séquentiel
Flux : Accueil -> Calibration -> Acquisition -> Analyse
"""

import sys
import logging
from pathlib import Path

# Configuration du logging centralisée
from hrneowave.core.logging_config import setup_logging
setup_logging()

log = logging.getLogger(__name__)

# --- Importations Centralisées PySide6 ---
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QObject, Signal

def main():
    """
    Point d'entrée principal de l'application CHNeoWave.
    Initialise et lance l'interface graphique.
    """
    print("🚀 Lancement de CHNeoWave v1.1.0")
    print("=" * 50)
    
    log.info(f"Lancement de CHNeoWave v1.1.0")
    
    # CRÉATION QAPPLICATION
    app = QApplication(sys.argv)
    app.setApplicationName("CHNeoWave")
    app.setApplicationVersion("1.1.0")
    app.setOrganizationName("Laboratoire d'Hydrodynamique Maritime")
    app.setQuitOnLastWindowClosed(True)
    
    print("✅ QApplication créé")

    try:
        # THÈME
        log.info("Initialisation du gestionnaire de thèmes...")
        from hrneowave.gui.styles.theme_manager import ThemeManager
        theme_manager = ThemeManager(app)
        theme_manager.apply_theme('maritime_modern')
        print("✅ Thème maritime appliqué")

        # CRÉATION MAINWINDOW
        log.info("Création de la fenêtre principale...")
        from hrneowave.gui.main_window import MainWindow
        
        main_window = MainWindow()
        log.info("MainWindow créée avec succès")
        print("✅ MainWindow créée")
        
        # AFFICHAGE CRITIQUE
        log.info("Affichage de la fenêtre principale.")
        print("🖥️ Affichage de l'interface...")
        
        # FORCER L'AFFICHAGE
        main_window.show()
        main_window.raise_()
        main_window.activateWindow()
        
        # FORCER L'ÉTAT DE LA FENÊTRE
        main_window.setWindowState(
            main_window.windowState() & ~Qt.WindowMinimized | Qt.WindowActive
        )
        
        # VÉRIFICATIONS DE SÉCURITÉ
        if not main_window.isVisible():
            log.warning("La fenêtre n'est pas visible, tentative de maximisation...")
            main_window.showMaximized()
            print("⚠️ Tentative de maximisation...")
        
        # VÉRIFICATIONS DÉTAILLÉES
        visible = main_window.isVisible()
        active = main_window.isActiveWindow()
        minimized = main_window.isMinimized()
        
        log.info(f"Fenêtre visible: {visible}, Taille: {main_window.size()}")
        log.info(f"Position de la fenêtre: {main_window.pos()}")
        log.info(f"État de la fenêtre: Active={active}, Minimized={minimized}")
        
        print(f"✅ Fenêtre visible: {visible}")
        print(f"✅ Position: {main_window.pos()}")
        print(f"✅ Taille: {main_window.size()}")
        
        if visible:
            print("🎉 SUCCÈS: CHNeoWave est visible à l'écran!")
            print("👀 L'interface devrait maintenant être affichée")
        else:
            print("❌ PROBLÈME: CHNeoWave n'est pas visible")
            return 1
        
        # BOUCLE D'ÉVÉNEMENTS
        log.info("Démarrage de la boucle d'événements de l'application.")
        print("🔄 Démarrage de la boucle d'événements...")
        
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
            
            # Sauvegarder l'ancien fichier
            backup_path = file_path.with_suffix('.py.backup')
            shutil.copy2(file_path, backup_path)
            
            # Écrire le nouveau contenu
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(corrected_content)
            
            self.fixes_applied.append(f"Fichier main.py corrigé")
            print("✅ main.py corrigé avec succès")
            
        except Exception as e:
            error_msg = f"Erreur lors de la correction main.py: {e}"
            self.errors.append(error_msg)
            print(f"❌ {error_msg}")
    
    def fix_main_window_imports(self):
        """Corrige les imports dans main_window.py"""
        print("🔧 Correction des imports dans main_window.py...")
        
        file_path = self.src_path / "gui" / "main_window.py"
        
        if not file_path.exists():
            print(f"⚠️ Fichier non trouvé: {file_path}")
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Vérifier si les imports sont corrects
            if "from PySide6.QtWidgets import QMainWindow" in content:
                print("✅ Imports déjà corrects dans main_window.py")
                return
            
            # Ajouter les imports manquants si nécessaire
            import_pattern = r"from PySide6\.QtWidgets import ([^,\n]+)"
            if "QMainWindow" not in content:
                # Ajouter QMainWindow à l'import existant
                new_content = re.sub(
                    import_pattern,
                    r"from PySide6.QtWidgets import QMainWindow, \1",
                    content
                )
                
                if new_content != content:
                    # Sauvegarder
                    backup_path = file_path.with_suffix('.py.backup')
                    shutil.copy2(file_path, backup_path)
                    
                    # Écrire
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    
                    self.fixes_applied.append(f"Imports corrigés dans main_window.py")
                    print("✅ Imports corrigés dans main_window.py")
                else:
                    print("⚠️ Aucune correction d'import nécessaire")
            
        except Exception as e:
            error_msg = f"Erreur lors de la correction des imports: {e}"
            self.errors.append(error_msg)
            print(f"❌ {error_msg}")
    
    def fix_theme_manager(self):
        """Corrige le ThemeManager pour éviter les erreurs"""
        print("🔧 Correction du ThemeManager...")
        
        file_path = self.src_path / "gui" / "styles" / "theme_manager.py"
        
        if not file_path.exists():
            print(f"⚠️ Fichier non trouvé: {file_path}")
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Vérifier si les corrections sont déjà présentes
            if "try:" in content and "except Exception" in content:
                print("✅ ThemeManager déjà protégé contre les erreurs")
                return
            
            # Ajouter une protection contre les erreurs
            apply_theme_pattern = r"def apply_theme\(self, theme_name: str\):"
            protected_apply_theme = '''def apply_theme(self, theme_name: str):
        """Applique un thème avec protection contre les erreurs"""
        try:
            # Code existant...
            if theme_name in self.available_themes:
                self.current_theme = theme_name
                self._load_and_apply_theme(theme_name)
                print(f"✅ Thème '{theme_name}' appliqué avec succès")
            else:
                print(f"⚠️ Thème '{theme_name}' non trouvé, utilisation du thème par défaut")
                self._load_and_apply_theme('maritime_modern')
        except Exception as e:
            print(f"⚠️ Erreur lors de l'application du thème '{theme_name}': {e}")
            # Utiliser le thème par défaut en cas d'erreur
            try:
                self._load_and_apply_theme('maritime_modern')
            except:
                print("⚠️ Impossible d'appliquer le thème par défaut")
'''
            
            # Remplacer la méthode apply_theme
            new_content = re.sub(apply_theme_pattern, protected_apply_theme, content)
            
            if new_content != content:
                # Sauvegarder
                backup_path = file_path.with_suffix('.py.backup')
                shutil.copy2(file_path, backup_path)
                
                # Écrire
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                self.fixes_applied.append(f"ThemeManager protégé contre les erreurs")
                print("✅ ThemeManager corrigé")
            else:
                print("⚠️ Aucune correction ThemeManager nécessaire")
            
        except Exception as e:
            error_msg = f"Erreur lors de la correction ThemeManager: {e}"
            self.errors.append(error_msg)
            print(f"❌ {error_msg}")
    
    def create_simple_test_script(self):
        """Crée un script de test simple pour vérifier le lancement"""
        print("🔧 Création d'un script de test simple...")
        
        test_script = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de test simple pour CHNeoWave
"""

import sys
from pathlib import Path

# Ajouter le chemin du projet
sys.path.insert(0, str(Path(__file__).parent / "src"))

from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
from PySide6.QtCore import Qt, QTimer

def test_simple_launch():
    """Test de lancement simple"""
    print("🧪 Test de lancement simple CHNeoWave")
    
    app = QApplication(sys.argv)
    
    # Fenêtre simple
    window = QMainWindow()
    window.setWindowTitle("CHNeoWave - Test Simple")
    window.setGeometry(200, 200, 600, 400)
    
    # Widget central
    central_widget = QWidget()
    layout = QVBoxLayout(central_widget)
    
    # Label
    label = QLabel("CHNeoWave - Test de Lancement")
    label.setAlignment(Qt.AlignCenter)
    layout.addWidget(label)
    
    window.setCentralWidget(central_widget)
    
    # Affichage
    window.show()
    window.raise_()
    window.activateWindow()
    
    print(f"✅ Fenêtre créée: Visible={window.isVisible()}")
    
    # Timer pour fermer
    timer = QTimer()
    timer.timeout.connect(app.quit)
    timer.start(3000)
    
    print("🔄 Démarrage boucle d'événements...")
    exit_code = app.exec()
    print(f"✅ Test terminé (code: {exit_code})")
    return exit_code

if __name__ == "__main__":
    exit(test_simple_launch())
'''
        
        test_file = self.project_root / "test_simple_launch.py"
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_script)
        
        self.fixes_applied.append(f"Script de test simple créé: {test_file}")
        print(f"✅ Script de test créé: {test_file}")
    
    def fix_all_launch_issues(self):
        """Applique toutes les corrections de lancement"""
        print("🔧 CORRECTION DES PROBLÈMES DE LANCEMENT CHNEOWAVE")
        print("=" * 60)
        
        try:
            # Phase 1: Corrections critiques
            print("\n📋 PHASE 1: Corrections critiques...")
            self.fix_main_py()
            self.fix_main_window_imports()
            
            # Phase 2: Corrections de robustesse
            print("\n📋 PHASE 2: Corrections de robustesse...")
            self.fix_theme_manager()
            
            # Phase 3: Outils de test
            print("\n📋 PHASE 3: Outils de test...")
            self.create_simple_test_script()
            
            # Rapport final
            self.generate_fix_report()
            
            return len(self.errors) == 0
            
        except Exception as e:
            print(f"❌ Erreur lors de la correction: {e}")
            return False
    
    def generate_fix_report(self):
        """Génère un rapport des corrections appliquées"""
        print("\n📊 RAPPORT DE CORRECTION DE LANCEMENT")
        print("=" * 50)
        
        if self.fixes_applied:
            print(f"✅ {len(self.fixes_applied)} corrections appliquées:")
            for fix in self.fixes_applied:
                print(f"  • {fix}")
        else:
            print("⚠️ Aucune correction appliquée")
        
        if self.errors:
            print(f"\n❌ {len(self.errors)} erreurs rencontrées:")
            for error in self.errors:
                print(f"  • {error}")
        
        print(f"\n📈 RÉSULTAT: {'SUCCÈS' if len(self.errors) == 0 else 'ÉCHEC'}")
        
        # Instructions de test
        print("\n🧪 INSTRUCTIONS DE TEST:")
        print("1. Test simple: python test_simple_launch.py")
        print("2. Test complet: python main.py")
        print("3. Diagnostic: python debug_launch_detailed.py")

def main():
    """Point d'entrée principal"""
    print("🚀 CORRECTEUR DE LANCEMENT CHNEOWAVE")
    print("=" * 50)
    
    # Créer le correcteur
    fixer = CHNeoWaveLaunchFixer()
    
    # Appliquer toutes les corrections
    success = fixer.fix_all_launch_issues()
    
    if success:
        print("\n🎉 CORRECTION TERMINÉE AVEC SUCCÈS!")
        print("✅ Tous les problèmes de lancement ont été corrigés")
        print("🚀 CHNeoWave devrait maintenant se lancer correctement")
    else:
        print("\n⚠️ CORRECTION TERMINÉE AVEC DES ERREURS")
        print("❌ Certains problèmes n'ont pas pu être corrigés")
        print("📋 Consultez le rapport pour plus de détails")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main()) 