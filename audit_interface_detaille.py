#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUDIT DÉTAILLÉ INTERFACE CHNEOWAVE
Diagnostic professionnel et systématique du problème d'affichage
"""

import sys
import os
import time
import traceback
from pathlib import Path

# Configuration du chemin
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, 
    QHBoxLayout, QPushButton, QStackedWidget, QSplitter
)
from PySide6.QtCore import Qt, QTimer, QThread, QObject, Signal
from PySide6.QtGui import QFont, QPixmap, QPainter

class AuditInterface:
    """Classe d'audit professionnel de l'interface CHNeoWave"""
    
    def __init__(self):
        self.app = None
        self.results = {
            'qt_environment': {},
            'basic_qt': {},
            'chneowave_imports': {},
            'chneowave_construction': {},
            'display_analysis': {},
            'recommendations': []
        }
        
    def run_complete_audit(self):
        """Exécute l'audit complet de l'interface"""
        print("🔍 AUDIT DÉTAILLÉ INTERFACE CHNEOWAVE")
        print("=" * 60)
        print("Analyse professionnelle du problème d'affichage")
        print("=" * 60)
        
        try:
            # Phase 1: Environnement Qt
            self._audit_qt_environment()
            
            # Phase 2: Test Qt basique
            self._audit_basic_qt()
            
            # Phase 3: Imports CHNeoWave
            self._audit_chneowave_imports()
            
            # Phase 4: Construction CHNeoWave
            self._audit_chneowave_construction()
            
            # Phase 5: Analyse d'affichage
            self._audit_display_analysis()
            
            # Phase 6: Rapport final
            self._generate_final_report()
            
        except Exception as e:
            print(f"❌ ERREUR CRITIQUE AUDIT: {e}")
            traceback.print_exc()
            
    def _audit_qt_environment(self):
        """Audit de l'environnement Qt"""
        print("\n📋 PHASE 1: AUDIT ENVIRONNEMENT QT")
        print("-" * 40)
        
        # Variables d'environnement critiques
        env_vars = {
            'QT_QPA_PLATFORM': os.getenv('QT_QPA_PLATFORM'),
            'DISPLAY': os.getenv('DISPLAY'),
            'QT_SCALE_FACTOR': os.getenv('QT_SCALE_FACTOR'),
            'QT_AUTO_SCREEN_SCALE_FACTOR': os.getenv('QT_AUTO_SCREEN_SCALE_FACTOR'),
            'QT_DEVICE_PIXEL_RATIO': os.getenv('QT_DEVICE_PIXEL_RATIO')
        }
        
        print("🔍 Variables d'environnement Qt:")
        for var, value in env_vars.items():
            status = "✅" if value else "⚠️"
            print(f"   {status} {var}: {value or 'Non défini'}")
            
        self.results['qt_environment'] = env_vars
        
        # Test QApplication basique
        try:
            self.app = QApplication.instance() or QApplication([])
            print(f"✅ QApplication créée: {type(self.app).__name__}")
            print(f"✅ Plateforme: {self.app.platformName()}")
            print(f"✅ Nombre d'écrans: {len(self.app.screens())}")
            
            for i, screen in enumerate(self.app.screens()):
                geom = screen.geometry()
                dpi = screen.logicalDotsPerInch()
                print(f"   📺 Écran {i}: {geom.width()}x{geom.height()} - DPI: {dpi}")
                
            self.results['qt_environment']['app_created'] = True
            self.results['qt_environment']['platform'] = self.app.platformName()
            self.results['qt_environment']['screens'] = len(self.app.screens())
            
        except Exception as e:
            print(f"❌ Erreur QApplication: {e}")
            self.results['qt_environment']['app_created'] = False
            self.results['qt_environment']['error'] = str(e)
            
    def _audit_basic_qt(self):
        """Test Qt basique pour vérifier le fonctionnement"""
        print("\n📋 PHASE 2: TEST QT BASIQUE")
        print("-" * 40)
        
        try:
            # Fenêtre Qt ultra-simple
            test_window = QMainWindow()
            test_window.setWindowTitle("Test Qt Basique - CHNeoWave Audit")
            test_window.setGeometry(100, 100, 400, 300)
            
            # Widget central simple
            central = QWidget()
            layout = QVBoxLayout(central)
            label = QLabel("Test Qt Fonctionnel")
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("font-size: 16px; color: blue; padding: 20px;")
            layout.addWidget(label)
            test_window.setCentralWidget(central)
            
            # Test d'affichage
            test_window.show()
            test_window.raise_()
            test_window.activateWindow()
            
            # Traitement des événements
            self.app.processEvents()
            
            # Vérifications
            is_visible = test_window.isVisible()
            geometry = test_window.geometry()
            is_active = test_window.isActiveWindow()
            
            print(f"✅ Fenêtre test créée")
            print(f"✅ Visible: {is_visible}")
            print(f"✅ Géométrie: {geometry}")
            print(f"✅ Active: {is_active}")
            
            # Test de capture
            try:
                pixmap = test_window.grab()
                capture_ok = not pixmap.isNull()
                print(f"✅ Capture d'écran: {'Réussie' if capture_ok else 'Échouée'}")
                
                if capture_ok:
                    pixmap.save("audit_qt_basic_test.png")
                    print("✅ Capture sauvegardée: audit_qt_basic_test.png")
                    
            except Exception as e:
                print(f"⚠️ Erreur capture: {e}")
                capture_ok = False
                
            self.results['basic_qt'] = {
                'window_created': True,
                'visible': is_visible,
                'geometry': f"{geometry.width()}x{geometry.height()}",
                'active': is_active,
                'capture_ok': capture_ok
            }
            
            # Fermer la fenêtre test
            test_window.close()
            
            if is_visible:
                print("🎯 Qt fonctionne correctement")
            else:
                print("❌ Problème Qt détecté")
                self.results['recommendations'].append(
                    "Problème dans l'environnement Qt de base"
                )
                
        except Exception as e:
            print(f"❌ Erreur test Qt basique: {e}")
            self.results['basic_qt'] = {'error': str(e)}
            
    def _audit_chneowave_imports(self):
        """Audit des imports CHNeoWave"""
        print("\n📋 PHASE 3: AUDIT IMPORTS CHNEOWAVE")
        print("-" * 40)
        
        imports_to_test = [
            ('MainWindow', 'hrneowave.gui.main_window', 'MainWindow'),
            ('ViewManager', 'hrneowave.gui.view_manager', 'ViewManager'),
            ('ThemeManager', 'hrneowave.gui.styles.theme_manager', 'ThemeManager'),
            ('WelcomeView', 'hrneowave.gui.views', 'WelcomeView'),
            ('DashboardViewMaritime', 'hrneowave.gui.views', 'DashboardViewMaritime'),
            ('MainSidebar', 'hrneowave.gui.widgets.main_sidebar', 'MainSidebar'),
            ('BreadcrumbsWidget', 'hrneowave.gui.components.breadcrumbs', 'BreadcrumbsWidget')
        ]
        
        import_results = {}
        
        for name, module, class_name in imports_to_test:
            try:
                exec(f"from {module} import {class_name}")
                print(f"✅ {name}: Import réussi")
                import_results[name] = {'success': True}
            except Exception as e:
                print(f"❌ {name}: Import échoué - {e}")
                import_results[name] = {'success': False, 'error': str(e)}
                
        self.results['chneowave_imports'] = import_results
        
        # Vérifier si tous les imports critiques sont OK
        critical_imports = ['MainWindow', 'ViewManager']
        critical_ok = all(import_results.get(imp, {}).get('success', False) 
                         for imp in critical_imports)
        
        if not critical_ok:
            self.results['recommendations'].append(
                "Imports critiques échoués - Vérifier les dépendances"
            )
            
    def _audit_chneowave_construction(self):
        """Audit de la construction CHNeoWave"""
        print("\n📋 PHASE 4: AUDIT CONSTRUCTION CHNEOWAVE")
        print("-" * 40)
        
        try:
            # Import MainWindow
            from hrneowave.gui.main_window import MainWindow
            
            print("🔄 Création MainWindow CHNeoWave...")
            
            # Capturer les prints de debug
            import io
            from contextlib import redirect_stdout, redirect_stderr
            
            stdout_capture = io.StringIO()
            stderr_capture = io.StringIO()
            
            with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                main_window = MainWindow()
                
            # Analyser les sorties de debug
            stdout_content = stdout_capture.getvalue()
            stderr_content = stderr_capture.getvalue()
            
            print("✅ MainWindow créée")
            
            if stdout_content:
                print("📋 Messages de debug capturés:")
                for line in stdout_content.strip().split('\n'):
                    if line.strip():
                        print(f"   🔍 {line}")
                        
            if stderr_content:
                print("⚠️ Erreurs capturées:")
                for line in stderr_content.strip().split('\n'):
                    if line.strip():
                        print(f"   ❌ {line}")
            
            # Tests de la MainWindow
            print("\n🔄 Tests MainWindow:")
            print(f"   📊 Type: {type(main_window).__name__}")
            print(f"   📊 Titre: {main_window.windowTitle()}")
            print(f"   📊 Taille: {main_window.size()}")
            print(f"   📊 Minimum: {main_window.minimumSize()}")
            
            # Vérifier les composants
            components = {
                'view_manager': hasattr(main_window, 'view_manager'),
                'stack_widget': hasattr(main_window, 'stack_widget'),
                'sidebar': hasattr(main_window, 'sidebar'),
                'breadcrumbs': hasattr(main_window, 'breadcrumbs'),
                'central_widget': main_window.centralWidget() is not None
            }
            
            print("\n🔄 Composants internes:")
            for comp, exists in components.items():
                status = "✅" if exists else "❌"
                print(f"   {status} {comp}: {'Présent' if exists else 'Absent'}")
                
            # Test d'affichage
            print("\n🔄 Test d'affichage MainWindow:")
            main_window.setWindowTitle("CHNeoWave - Audit Interface")
            main_window.resize(1000, 700)
            main_window.show()
            main_window.raise_()
            main_window.activateWindow()
            
            # Traitement des événements
            self.app.processEvents()
            time.sleep(0.5)  # Attendre un peu
            self.app.processEvents()
            
            # Vérifications finales
            is_visible = main_window.isVisible()
            geometry = main_window.geometry()
            is_active = main_window.isActiveWindow()
            
            print(f"   📊 Visible: {is_visible}")
            print(f"   📊 Géométrie: {geometry}")
            print(f"   📊 Active: {is_active}")
            
            # Test de capture
            try:
                pixmap = main_window.grab()
                capture_ok = not pixmap.isNull()
                print(f"   📊 Capture: {'Réussie' if capture_ok else 'Échouée'}")
                
                if capture_ok:
                    pixmap.save("audit_chneowave_mainwindow.png")
                    print("   ✅ Capture sauvegardée: audit_chneowave_mainwindow.png")
                    
            except Exception as e:
                print(f"   ⚠️ Erreur capture: {e}")
                capture_ok = False
                
            self.results['chneowave_construction'] = {
                'created': True,
                'components': components,
                'visible': is_visible,
                'geometry': f"{geometry.width()}x{geometry.height()}",
                'active': is_active,
                'capture_ok': capture_ok,
                'debug_output': stdout_content,
                'errors': stderr_content
            }
            
            # Maintenir ouvert pour observation
            print("\n⏰ Maintien de la fenêtre pendant 10 secondes...")
            print("   Vérifiez visuellement si CHNeoWave apparaît à l'écran")
            
            # Timer pour fermeture
            timer = QTimer()
            timer.timeout.connect(lambda: main_window.close())
            timer.start(10000)
            
            # Boucle d'événements temporaire
            start_time = time.time()
            while time.time() - start_time < 10:
                self.app.processEvents()
                time.sleep(0.1)
                
            main_window.close()
            
        except Exception as e:
            print(f"❌ Erreur construction CHNeoWave: {e}")
            traceback.print_exc()
            self.results['chneowave_construction'] = {'error': str(e)}
            
    def _audit_display_analysis(self):
        """Analyse approfondie des problèmes d'affichage"""
        print("\n📋 PHASE 5: ANALYSE AFFICHAGE")
        print("-" * 40)
        
        analysis = {
            'qt_basic_works': self.results.get('basic_qt', {}).get('visible', False),
            'chneowave_visible': self.results.get('chneowave_construction', {}).get('visible', False),
            'imports_ok': all(r.get('success', False) for r in self.results.get('chneowave_imports', {}).values()),
            'components_ok': all(self.results.get('chneowave_construction', {}).get('components', {}).values())
        }
        
        print("🔍 Analyse des résultats:")
        for key, value in analysis.items():
            status = "✅" if value else "❌"
            print(f"   {status} {key}: {value}")
            
        # Diagnostic
        if analysis['qt_basic_works'] and not analysis['chneowave_visible']:
            print("\n🎯 DIAGNOSTIC: Problème spécifique à CHNeoWave")
            self.results['recommendations'].extend([
                "Qt fonctionne mais CHNeoWave ne s'affiche pas",
                "Vérifier les styles CSS/QSS",
                "Vérifier la construction de l'interface",
                "Vérifier les signaux et slots"
            ])
        elif not analysis['qt_basic_works']:
            print("\n🎯 DIAGNOSTIC: Problème environnement Qt")
            self.results['recommendations'].extend([
                "Problème dans l'environnement Qt",
                "Vérifier l'installation PySide6",
                "Vérifier les variables d'environnement"
            ])
        elif analysis['chneowave_visible']:
            print("\n🎯 DIAGNOSTIC: CHNeoWave fonctionne correctement")
            self.results['recommendations'].append(
                "Interface fonctionne - Problème peut-être intermittent"
            )
            
        self.results['display_analysis'] = analysis
        
    def _generate_final_report(self):
        """Génère le rapport final d'audit"""
        print("\n" + "=" * 60)
        print("📊 RAPPORT FINAL AUDIT INTERFACE CHNEOWAVE")
        print("=" * 60)
        
        # Résumé exécutif
        qt_ok = self.results.get('basic_qt', {}).get('visible', False)
        chneowave_ok = self.results.get('chneowave_construction', {}).get('visible', False)
        
        if qt_ok and chneowave_ok:
            status = "🟢 FONCTIONNEL"
        elif qt_ok and not chneowave_ok:
            status = "🟡 PROBLÈME CHNEOWAVE"
        else:
            status = "🔴 PROBLÈME CRITIQUE"
            
        print(f"\n📋 STATUT GLOBAL: {status}")
        
        # Détails par phase
        print("\n📋 DÉTAILS PAR PHASE:")
        
        # Environnement Qt
        env_ok = self.results.get('qt_environment', {}).get('app_created', False)
        print(f"   🔍 Environnement Qt: {'✅ OK' if env_ok else '❌ PROBLÈME'}")
        
        # Qt basique
        print(f"   🔍 Qt basique: {'✅ OK' if qt_ok else '❌ PROBLÈME'}")
        
        # Imports
        imports = self.results.get('chneowave_imports', {})
        imports_ok = all(r.get('success', False) for r in imports.values()) if imports else False
        print(f"   🔍 Imports CHNeoWave: {'✅ OK' if imports_ok else '❌ PROBLÈME'}")
        
        # Construction
        construction_ok = self.results.get('chneowave_construction', {}).get('created', False)
        print(f"   🔍 Construction CHNeoWave: {'✅ OK' if construction_ok else '❌ PROBLÈME'}")
        
        # Affichage
        print(f"   🔍 Affichage CHNeoWave: {'✅ OK' if chneowave_ok else '❌ PROBLÈME'}")
        
        # Recommandations
        if self.results['recommendations']:
            print("\n📋 RECOMMANDATIONS:")
            for i, rec in enumerate(self.results['recommendations'], 1):
                print(f"   {i}. {rec}")
                
        # Actions prioritaires
        print("\n📋 ACTIONS PRIORITAIRES:")
        if not qt_ok:
            print("   🔥 URGENT: Réparer l'environnement Qt")
            print("      - Réinstaller PySide6")
            print("      - Vérifier les variables d'environnement")
        elif not chneowave_ok:
            print("   🔥 URGENT: Déboguer CHNeoWave")
            print("      - Examiner les styles CSS/QSS")
            print("      - Vérifier la construction UI")
            print("      - Tester sans ThemeManager")
        else:
            print("   ✅ Interface fonctionnelle")
            
        # Sauvegarde du rapport
        self._save_report()
        
    def _save_report(self):
        """Sauvegarde le rapport d'audit"""
        try:
            import json
            with open('audit_interface_rapport.json', 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)
            print("\n✅ Rapport sauvegardé: audit_interface_rapport.json")
        except Exception as e:
            print(f"\n⚠️ Erreur sauvegarde rapport: {e}")

def main():
    """Point d'entrée principal"""
    audit = AuditInterface()
    audit.run_complete_audit()
    
    print("\n" + "=" * 60)
    print("🏁 AUDIT TERMINÉ")
    print("=" * 60)
    
if __name__ == "__main__":
    main()