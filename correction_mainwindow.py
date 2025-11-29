#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Correction MainWindow CHNeoWave
Basé sur les diagnostics effectués
"""

import sys
import os
from pathlib import Path

# Ajouter le chemin du projet
sys.path.insert(0, str(Path(__file__).parent / "src"))

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QStackedWidget
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont

class MainWindowCorrigee(QMainWindow):
    """MainWindow CHNeoWave corrigée - Version simplifiée qui fonctionne"""
    
    def __init__(self):
        super().__init__()
        print("🔍 Début construction MainWindow corrigée")
        
        # Configuration de base
        self.setWindowTitle("CHNeoWave - Interface Maritime Corrigée")
        self.setGeometry(100, 100, 1200, 800)
        self.setMinimumSize(800, 600)
        
        # Initialiser les composants étape par étape
        self._init_central_widget()
        self._init_view_manager_simple()
        self._init_navigation()
        self._load_welcome_view_safe()
        
        print("✅ MainWindow corrigée construite")
        
    def _init_central_widget(self):
        """Initialiser le widget central"""
        print("🔄 Initialisation widget central")
        
        # Widget central
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Layout principal
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # Header
        header = QLabel("CHNeoWave - Laboratoire Maritime")
        header.setAlignment(Qt.AlignCenter)
        header.setFont(QFont("Arial", 18, QFont.Bold))
        header.setStyleSheet("""
            QLabel {
                background-color: #1e3a5f;
                color: white;
                padding: 15px;
                border-radius: 5px;
                margin-bottom: 10px;
            }
        """)
        self.main_layout.addWidget(header)
        
        print("✅ Widget central initialisé")
        
    def _init_view_manager_simple(self):
        """Initialiser un gestionnaire de vues simplifié"""
        print("🔄 Initialisation gestionnaire de vues simplifié")
        
        # Navigation simple
        nav_layout = QHBoxLayout()
        
        self.btn_welcome = QPushButton("Accueil")
        self.btn_welcome.clicked.connect(lambda: self._navigate_to('welcome'))
        nav_layout.addWidget(self.btn_welcome)
        
        self.btn_dashboard = QPushButton("Tableau de Bord")
        self.btn_dashboard.clicked.connect(lambda: self._navigate_to('dashboard'))
        nav_layout.addWidget(self.btn_dashboard)
        
        self.btn_calibration = QPushButton("Calibration")
        self.btn_calibration.clicked.connect(lambda: self._navigate_to('calibration'))
        nav_layout.addWidget(self.btn_calibration)
        
        nav_layout.addStretch()
        self.main_layout.addLayout(nav_layout)
        
        # Zone de contenu avec StackedWidget
        self.content_stack = QStackedWidget()
        self.main_layout.addWidget(self.content_stack)
        
        # Dictionnaire des vues
        self.views = {}
        self.current_view = None
        
        print("✅ Gestionnaire de vues simplifié initialisé")
        
    def _init_navigation(self):
        """Initialiser la navigation"""
        print("🔄 Initialisation navigation")
        
        # Créer les vues de base
        self._create_welcome_view_simple()
        self._create_dashboard_view_simple()
        self._create_calibration_view_simple()
        
        print("✅ Navigation initialisée")
        
    def _create_welcome_view_simple(self):
        """Créer une vue d'accueil simplifiée"""
        welcome_widget = QWidget()
        layout = QVBoxLayout(welcome_widget)
        
        title = QLabel("Bienvenue dans CHNeoWave")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Arial", 24, QFont.Bold))
        layout.addWidget(title)
        
        description = QLabel("""
CHNeoWave est un logiciel destiné aux laboratoires d'étude maritime 
sur modèles réduits en Méditerranée (bassins, canaux).

Fonctionnalités principales:
• Acquisition de données de capteurs
• Calibration des instruments
• Analyse des résultats
• Génération de rapports
        """)
        description.setAlignment(Qt.AlignCenter)
        description.setFont(QFont("Arial", 12))
        layout.addWidget(description)
        
        # Bouton de création de projet
        create_btn = QPushButton("Créer un Nouveau Projet")
        create_btn.setFont(QFont("Arial", 14, QFont.Bold))
        create_btn.setStyleSheet("""
            QPushButton {
                background-color: #2c5aa0;
                color: white;
                padding: 15px 30px;
                border-radius: 8px;
                border: none;
            }
            QPushButton:hover {
                background-color: #1e3a5f;
            }
        """)
        create_btn.clicked.connect(self._create_project)
        layout.addWidget(create_btn, alignment=Qt.AlignCenter)
        
        layout.addStretch()
        
        self.views['welcome'] = welcome_widget
        self.content_stack.addWidget(welcome_widget)
        
    def _create_dashboard_view_simple(self):
        """Créer un tableau de bord simplifié"""
        dashboard_widget = QWidget()
        layout = QVBoxLayout(dashboard_widget)
        
        title = QLabel("Tableau de Bord Maritime")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Arial", 20, QFont.Bold))
        layout.addWidget(title)
        
        # Indicateurs KPI simulés
        kpi_layout = QHBoxLayout()
        
        for kpi_name, kpi_value in [("Capteurs Actifs", "12/15"), ("Température", "22.5°C"), ("Pression", "1013 hPa")]:
            kpi_widget = QWidget()
            kpi_widget.setStyleSheet("""
                QWidget {
                    background-color: #f0f8ff;
                    border: 2px solid #2c5aa0;
                    border-radius: 10px;
                    padding: 20px;
                }
            """)
            kpi_layout_inner = QVBoxLayout(kpi_widget)
            
            kpi_label = QLabel(kpi_name)
            kpi_label.setAlignment(Qt.AlignCenter)
            kpi_label.setFont(QFont("Arial", 12, QFont.Bold))
            kpi_layout_inner.addWidget(kpi_label)
            
            kpi_val = QLabel(kpi_value)
            kpi_val.setAlignment(Qt.AlignCenter)
            kpi_val.setFont(QFont("Arial", 16, QFont.Bold))
            kpi_val.setStyleSheet("color: #2c5aa0;")
            kpi_layout_inner.addWidget(kpi_val)
            
            kpi_layout.addWidget(kpi_widget)
        
        layout.addLayout(kpi_layout)
        layout.addStretch()
        
        self.views['dashboard'] = dashboard_widget
        self.content_stack.addWidget(dashboard_widget)
        
    def _create_calibration_view_simple(self):
        """Créer une vue de calibration simplifiée"""
        calibration_widget = QWidget()
        layout = QVBoxLayout(calibration_widget)
        
        title = QLabel("Calibration des Instruments")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Arial", 20, QFont.Bold))
        layout.addWidget(title)
        
        info = QLabel("Module de calibration des capteurs maritimes")
        info.setAlignment(Qt.AlignCenter)
        info.setFont(QFont("Arial", 14))
        layout.addWidget(info)
        
        # Boutons de calibration
        cal_layout = QVBoxLayout()
        
        for cal_type in ["Calibration Température", "Calibration Pression", "Calibration Houle"]:
            cal_btn = QPushButton(cal_type)
            cal_btn.setFont(QFont("Arial", 12))
            cal_btn.setStyleSheet("""
                QPushButton {
                    background-color: #4a90e2;
                    color: white;
                    padding: 10px;
                    border-radius: 5px;
                    margin: 5px;
                }
                QPushButton:hover {
                    background-color: #357abd;
                }
            """)
            cal_layout.addWidget(cal_btn)
        
        layout.addLayout(cal_layout)
        layout.addStretch()
        
        self.views['calibration'] = calibration_widget
        self.content_stack.addWidget(calibration_widget)
        
    def _load_welcome_view_safe(self):
        """Charger la vue d'accueil de manière sécurisée"""
        print("🔄 Chargement vue d'accueil")
        self._navigate_to('welcome')
        print("✅ Vue d'accueil chargée")
        
    def _navigate_to(self, view_name):
        """Naviguer vers une vue"""
        if view_name in self.views:
            self.content_stack.setCurrentWidget(self.views[view_name])
            self.current_view = view_name
            print(f"✅ Navigation vers {view_name}")
            
            # Mettre à jour les boutons
            self.btn_welcome.setStyleSheet("" if view_name != 'welcome' else "background-color: #1e3a5f; color: white;")
            self.btn_dashboard.setStyleSheet("" if view_name != 'dashboard' else "background-color: #1e3a5f; color: white;")
            self.btn_calibration.setStyleSheet("" if view_name != 'calibration' else "background-color: #1e3a5f; color: white;")
        else:
            print(f"❌ Vue {view_name} non trouvée")
            
    def _create_project(self):
        """Créer un nouveau projet"""
        print("🔄 Création d'un nouveau projet")
        self._navigate_to('dashboard')

def main():
    """Lancer l'application corrigée"""
    print("🚀 CHNeoWave - Version Corrigée")
    print("=" * 50)
    
    try:
        # Créer QApplication
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
            app.setApplicationName("CHNeoWave Corrigé")
            app.setApplicationVersion("1.1.0-fixed")
        
        print("✅ QApplication créée")
        
        # Créer MainWindow corrigée
        window = MainWindowCorrigee()
        print("✅ MainWindow corrigée créée")
        
        # Afficher la fenêtre
        window.show()
        window.raise_()
        window.activateWindow()
        
        print(f"✅ Fenêtre affichée")
        print(f"✅ Visible: {window.isVisible()}")
        print(f"✅ Géométrie: {window.geometry()}")
        print("🎉 CHNeoWave Corrigé est opérationnel !")
        print("👀 L'interface devrait maintenant être visible")
        
        # Lancer la boucle d'événements
        exit_code = app.exec()
        print(f"✅ Application terminée (code: {exit_code})")
        return exit_code
        
    except Exception as e:
        print(f"❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())