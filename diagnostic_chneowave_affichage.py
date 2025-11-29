#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Diagnostic Spécifique CHNeoWave - Problème d'Affichage
Qt fonctionne, mais CHNeoWave ne s'affiche pas
"""

import sys
import os
import time

# Ajouter le répertoire src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont

class DiagnosticCHNeoWave(QMainWindow):
    """Diagnostic spécialisé pour CHNeoWave"""
    
    def __init__(self):
        super().__init__()
        self.chneowave_window = None
        self.etape_actuelle = 0
        self.setup_ui()
        
        # Démarrer le diagnostic automatique
        QTimer.singleShot(2000, self.demarrer_diagnostic)
        
    def setup_ui(self):
        """Configuration de l'interface de diagnostic"""
        self.setWindowTitle("🔍 DIAGNOSTIC CHNEOWAVE - PROBLÈME D'AFFICHAGE")
        self.setGeometry(50, 50, 700, 500)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Titre
        titre = QLabel("🔍 DIAGNOSTIC CHNEOWAVE")
        titre.setAlignment(Qt.AlignCenter)
        titre.setFont(QFont("Arial", 16, QFont.Bold))
        titre.setStyleSheet("""
            QLabel {
                background: #2196F3;
                color: white;
                padding: 20px;
                border-radius: 10px;
                margin: 10px;
            }
        """)
        layout.addWidget(titre)
        
        # Statut
        self.statut = QLabel("📊 Initialisation du diagnostic...")
        self.statut.setWordWrap(True)
        self.statut.setAlignment(Qt.AlignCenter)
        self.statut.setFont(QFont("Arial", 12))
        self.statut.setStyleSheet("""
            QLabel {
                background: #e3f2fd;
                border: 2px solid #2196F3;
                border-radius: 8px;
                padding: 20px;
                margin: 10px;
                color: #1976D2;
            }
        """)
        layout.addWidget(self.statut)
        
        # Log détaillé
        self.log_detail = QLabel("📝 Logs détaillés apparaîtront ici...")
        self.log_detail.setWordWrap(True)
        self.log_detail.setFont(QFont("Courier", 9))
        self.log_detail.setStyleSheet("""
            QLabel {
                background: #f5f5f5;
                border: 1px solid #ccc;
                border-radius: 6px;
                padding: 15px;
                margin: 10px;
                max-height: 200px;
            }
        """)
        layout.addWidget(self.log_detail)
        
        # Boutons de contrôle
        boutons_layout = QVBoxLayout()
        
        self.btn_etape_suivante = QPushButton("➡️ Étape Suivante")
        self.btn_etape_suivante.setFont(QFont("Arial", 11))
        self.btn_etape_suivante.clicked.connect(self.etape_suivante)
        boutons_layout.addWidget(self.btn_etape_suivante)
        
        self.btn_forcer_affichage = QPushButton("🔧 Forcer Affichage CHNeoWave")
        self.btn_forcer_affichage.setFont(QFont("Arial", 11))
        self.btn_forcer_affichage.clicked.connect(self.forcer_affichage_chneowave)
        boutons_layout.addWidget(self.btn_forcer_affichage)
        
        self.btn_reset = QPushButton("🔄 Reset Diagnostic")
        self.btn_reset.setFont(QFont("Arial", 11))
        self.btn_reset.clicked.connect(self.reset_diagnostic)
        boutons_layout.addWidget(self.btn_reset)
        
        layout.addLayout(boutons_layout)
        
    def log(self, message):
        """Ajouter un message au log"""
        timestamp = time.strftime("%H:%M:%S")
        log_msg = f"[{timestamp}] {message}"
        print(log_msg)
        
        # Mettre à jour l'affichage
        current_text = self.log_detail.text()
        if "Logs détaillés" in current_text:
            new_text = log_msg
        else:
            lines = current_text.split('\n')
            lines.append(log_msg)
            # Garder seulement les 10 dernières lignes
            if len(lines) > 10:
                lines = lines[-10:]
            new_text = '\n'.join(lines)
        
        self.log_detail.setText(new_text)
        
    def demarrer_diagnostic(self):
        """Démarrer le diagnostic automatique"""
        self.statut.setText("🚀 Diagnostic automatique démarré")
        self.log("=== DÉBUT DIAGNOSTIC CHNEOWAVE ===")
        self.etape_suivante()
        
    def etape_suivante(self):
        """Passer à l'étape suivante du diagnostic"""
        self.etape_actuelle += 1
        
        if self.etape_actuelle == 1:
            self.etape_1_test_imports()
        elif self.etape_actuelle == 2:
            self.etape_2_creation_mainwindow()
        elif self.etape_actuelle == 3:
            self.etape_3_verification_affichage()
        elif self.etape_actuelle == 4:
            self.etape_4_debug_widgets()
        elif self.etape_actuelle == 5:
            self.etape_5_test_show_force()
        else:
            self.diagnostic_termine()
    
    def etape_1_test_imports(self):
        """Étape 1: Test des imports"""
        self.statut.setText("📦 ÉTAPE 1: Test des imports CHNeoWave")
        self.log("Étape 1: Test des imports")
        
        try:
            self.log("Import MainWindow...")
            from hrneowave.gui.main_window import MainWindow
            self.log("✅ MainWindow importé avec succès")
            
            self.log("Import ViewManager...")
            from hrneowave.gui.view_manager import ViewManager
            self.log("✅ ViewManager importé avec succès")
            
            self.log("Import ThemeManager...")
            from hrneowave.gui.theme_manager import ThemeManager
            self.log("✅ ThemeManager importé avec succès")
            
            self.statut.setText("✅ ÉTAPE 1: Tous les imports réussis")
            QTimer.singleShot(2000, self.etape_suivante)
            
        except Exception as e:
            self.log(f"❌ Erreur import: {e}")
            self.statut.setText(f"❌ ÉTAPE 1: Échec import - {e}")
    
    def etape_2_creation_mainwindow(self):
        """Étape 2: Création de MainWindow"""
        self.statut.setText("🏗️ ÉTAPE 2: Création de MainWindow")
        self.log("Étape 2: Création de MainWindow")
        
        try:
            from hrneowave.gui.main_window import MainWindow
            
            self.log("Création de MainWindow...")
            self.chneowave_window = MainWindow()
            self.log("✅ MainWindow créé avec succès")
            
            # Vérifications de base
            self.log(f"Type: {type(self.chneowave_window)}")
            self.log(f"Titre: {self.chneowave_window.windowTitle()}")
            self.log(f"Taille minimale: {self.chneowave_window.minimumSize()}")
            
            self.statut.setText("✅ ÉTAPE 2: MainWindow créé")
            QTimer.singleShot(2000, self.etape_suivante)
            
        except Exception as e:
            self.log(f"❌ Erreur création MainWindow: {e}")
            self.statut.setText(f"❌ ÉTAPE 2: Échec création - {e}")
            import traceback
            self.log(f"Traceback: {traceback.format_exc()[:200]}...")
    
    def etape_3_verification_affichage(self):
        """Étape 3: Vérification de l'affichage"""
        self.statut.setText("👁️ ÉTAPE 3: Vérification affichage")
        self.log("Étape 3: Vérification affichage")
        
        if not self.chneowave_window:
            self.log("❌ Pas de MainWindow à tester")
            self.statut.setText("❌ ÉTAPE 3: Pas de MainWindow")
            return
        
        try:
            # État avant show()
            self.log(f"Avant show() - Visible: {self.chneowave_window.isVisible()}")
            self.log(f"Avant show() - Géométrie: {self.chneowave_window.geometry()}")
            
            # Appeler show()
            self.log("Appel de show()...")
            self.chneowave_window.show()
            
            # État après show()
            self.log(f"Après show() - Visible: {self.chneowave_window.isVisible()}")
            self.log(f"Après show() - Géométrie: {self.chneowave_window.geometry()}")
            self.log(f"Après show() - Actif: {self.chneowave_window.isActiveWindow()}")
            
            if self.chneowave_window.isVisible():
                self.statut.setText("✅ ÉTAPE 3: CHNeoWave visible!")
                self.log("✅ CHNeoWave est marqué comme visible")
            else:
                self.statut.setText("⚠️ ÉTAPE 3: CHNeoWave non visible")
                self.log("⚠️ CHNeoWave n'est pas marqué comme visible")
            
            QTimer.singleShot(3000, self.etape_suivante)
            
        except Exception as e:
            self.log(f"❌ Erreur affichage: {e}")
            self.statut.setText(f"❌ ÉTAPE 3: Erreur - {e}")
    
    def etape_4_debug_widgets(self):
        """Étape 4: Debug des widgets"""
        self.statut.setText("🔧 ÉTAPE 4: Debug widgets internes")
        self.log("Étape 4: Debug widgets internes")
        
        if not self.chneowave_window:
            self.log("❌ Pas de MainWindow à analyser")
            return
        
        try:
            # Analyser la structure
            central = self.chneowave_window.centralWidget()
            self.log(f"Widget central: {type(central) if central else 'None'}")
            
            if central:
                self.log(f"Central visible: {central.isVisible()}")
                self.log(f"Central taille: {central.size()}")
                
                # Enfants du widget central
                children = central.findChildren(QWidget)
                self.log(f"Nombre d'enfants: {len(children)}")
                
                for i, child in enumerate(children[:5]):  # Limiter à 5
                    self.log(f"  Enfant {i}: {type(child).__name__} - Visible: {child.isVisible()}")
            
            # Vérifier le view_manager
            if hasattr(self.chneowave_window, 'view_manager'):
                vm = self.chneowave_window.view_manager
                self.log(f"ViewManager: {type(vm)}")
                if hasattr(vm, 'current_view'):
                    self.log(f"Vue actuelle: {vm.current_view}")
                if hasattr(vm, 'views'):
                    self.log(f"Vues enregistrées: {list(vm.views.keys())}")
            
            QTimer.singleShot(3000, self.etape_suivante)
            
        except Exception as e:
            self.log(f"❌ Erreur debug widgets: {e}")
    
    def etape_5_test_show_force(self):
        """Étape 5: Test show forcé"""
        self.statut.setText("💪 ÉTAPE 5: Test show forcé")
        self.log("Étape 5: Test show forcé")
        
        if not self.chneowave_window:
            self.log("❌ Pas de MainWindow à forcer")
            return
        
        try:
            # Forcer l'affichage avec toutes les méthodes
            self.log("Tentative show() forcé...")
            self.chneowave_window.show()
            
            self.log("Tentative raise_()...")
            self.chneowave_window.raise_()
            
            self.log("Tentative activateWindow()...")
            self.chneowave_window.activateWindow()
            
            self.log("Tentative setWindowState()...")
            from PySide6.QtCore import Qt
            self.chneowave_window.setWindowState(Qt.WindowActive)
            
            # Repositionner
            self.log("Repositionnement...")
            self.chneowave_window.move(800, 100)
            
            # Vérification finale
            self.log(f"Final - Visible: {self.chneowave_window.isVisible()}")
            self.log(f"Final - Position: ({self.chneowave_window.x()}, {self.chneowave_window.y()})")
            self.log(f"Final - Taille: {self.chneowave_window.width()}x{self.chneowave_window.height()}")
            
            QTimer.singleShot(3000, self.etape_suivante)
            
        except Exception as e:
            self.log(f"❌ Erreur show forcé: {e}")
    
    def forcer_affichage_chneowave(self):
        """Forcer l'affichage de CHNeoWave"""
        if self.chneowave_window:
            self.log("🔧 FORÇAGE AFFICHAGE MANUEL")
            try:
                self.chneowave_window.show()
                self.chneowave_window.raise_()
                self.chneowave_window.activateWindow()
                self.chneowave_window.move(800, 50)
                self.log(f"Forcé - Visible: {self.chneowave_window.isVisible()}")
            except Exception as e:
                self.log(f"❌ Erreur forçage: {e}")
        else:
            self.log("❌ Pas de MainWindow à forcer")
    
    def reset_diagnostic(self):
        """Reset du diagnostic"""
        self.etape_actuelle = 0
        if self.chneowave_window:
            self.chneowave_window.close()
            self.chneowave_window = None
        self.log_detail.setText("📝 Diagnostic reset")
        self.statut.setText("🔄 Diagnostic reset - Prêt à redémarrer")
    
    def diagnostic_termine(self):
        """Diagnostic terminé"""
        self.statut.setText("🏁 DIAGNOSTIC TERMINÉ")
        self.log("=== DIAGNOSTIC TERMINÉ ===")
        
        if self.chneowave_window and self.chneowave_window.isVisible():
            self.log("✅ RÉSULTAT: CHNeoWave est visible!")
        else:
            self.log("❌ RÉSULTAT: CHNeoWave n'est PAS visible")
            self.log("🔍 Problème identifié dans CHNeoWave")

def main():
    """Fonction principale"""
    print("\n🔍 === DIAGNOSTIC CHNEOWAVE - PROBLÈME D'AFFICHAGE ===")
    print("🎯 Qt fonctionne, mais CHNeoWave ne s'affiche pas")
    print("🔍 Diagnostic étape par étape en cours...")
    print("")
    
    app = QApplication(sys.argv)
    
    # Créer la fenêtre de diagnostic
    diagnostic = DiagnosticCHNeoWave()
    diagnostic.show()
    
    print("✅ Fenêtre de diagnostic affichée")
    print("🔍 Suivez le diagnostic dans la fenêtre")
    
    return app.exec()

if __name__ == "__main__":
    exit_code = main()
    print(f"🏁 Diagnostic terminé avec code: {exit_code}")
    sys.exit(exit_code)