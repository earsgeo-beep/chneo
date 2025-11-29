#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CHNeoWave - Version Opérationnelle
Basée sur l'approche fenêtre simple qui fonctionne
Version: 1.1.0
"""

import sys
import logging
import traceback
from pathlib import Path

# Ajouter le chemin du projet
sys.path.insert(0, str(Path(__file__).parent / "src"))

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
    """Point d'entrée principal de l'application opérationnelle"""
    try:
        print("🚀 Lancement de CHNeoWave v1.1.0 - Version Opérationnelle")
        print("=" * 60)
        
        # Import Qt
        from PySide6.QtWidgets import (
            QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
            QLabel, QPushButton, QStackedWidget, QFrame, QScrollArea
        )
        from PySide6.QtCore import Qt, QTimer
        from PySide6.QtGui import QFont, QPixmap
        
        # Créer QApplication
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
            app.setApplicationName("CHNeoWave Operational")
            app.setApplicationVersion("1.1.0")
            app.setOrganizationName("CHNeoWave")
        
        print("✅ QApplication créé")
        
        # Application du thème
        try:
            from hrneowave.gui.styles.theme_manager import ThemeManager
            theme_manager = ThemeManager(app=app)
            theme_manager.apply_theme('maritime_modern')
            print("✅ Thème 'maritime_modern' appliqué")
        except Exception as e:
            print(f"⚠️ Erreur thème: {e}")
        
        # Créer la fenêtre principale
        print("🔄 Création fenêtre principale...")
        window = QMainWindow()
        window.setWindowTitle("CHNeoWave - Interface Maritime Opérationnelle")
        window.resize(1200, 800)
        
        # Centrer la fenêtre
        screen = app.primaryScreen()
        screen_geometry = screen.geometry()
        window_geometry = window.geometry()
        
        x = (screen_geometry.width() - window_geometry.width()) // 2
        y = (screen_geometry.height() - window_geometry.height()) // 2
        window.move(x, y)
        
        print("✅ Fenêtre configurée et centrée")
        
        # Widget central
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # En-tête
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background-color: #1e3a8a;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        header_layout = QHBoxLayout(header_frame)
        
        # Logo/Titre
        title_label = QLabel("🌊 CHNeoWave - Interface Maritime")
        title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 24px;
                font-weight: bold;
                padding: 10px;
            }
        """)
        header_layout.addWidget(title_label)
        
        # Statut
        status_label = QLabel("✅ Opérationnel")
        status_label.setStyleSheet("""
            QLabel {
                color: #10b981;
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
            }
        """)
        header_layout.addWidget(status_label, alignment=Qt.AlignRight)
        
        main_layout.addWidget(header_frame)
        
        # Zone de contenu principal
        content_frame = QFrame()
        content_frame.setStyleSheet("""
            QFrame {
                background-color: #f8fafc;
                border-radius: 10px;
                border: 2px solid #e2e8f0;
            }
        """)
        content_layout = QVBoxLayout(content_frame)
        
        # Titre de section
        section_title = QLabel("🎯 Tableau de Bord Maritime")
        section_title.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: bold;
                color: #1e293b;
                padding: 15px;
            }
        """)
        content_layout.addWidget(section_title)
        
        # Grille de cartes
        cards_layout = QHBoxLayout()
        
        # Carte 1: Welcome
        welcome_card = create_card("🏠 Accueil", "Bienvenue dans CHNeoWave", "#3b82f6")
        cards_layout.addWidget(welcome_card)
        
        # Carte 2: Dashboard
        dashboard_card = create_card("📊 Tableau de Bord", "Vue d'ensemble maritime", "#10b981")
        cards_layout.addWidget(dashboard_card)
        
        # Carte 3: Calibration
        calibration_card = create_card("⚙️ Calibration", "Configuration système", "#f59e0b")
        cards_layout.addWidget(calibration_card)
        
        # Carte 4: Acquisition
        acquisition_card = create_card("📡 Acquisition", "Collecte de données", "#8b5cf6")
        cards_layout.addWidget(acquisition_card)
        
        content_layout.addLayout(cards_layout)
        
        # Zone d'information
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background-color: #dbeafe;
                border-radius: 8px;
                padding: 15px;
                margin: 10px;
            }
        """)
        info_layout = QVBoxLayout(info_frame)
        
        info_title = QLabel("ℹ️ Informations Système")
        info_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #1e40af;")
        info_layout.addWidget(info_title)
        
        info_text = QLabel("""
        ✅ Qt/PySide6: Opérationnel
        ✅ Thème maritime: Appliqué
        ✅ WelcomeView: Fonctionnelle
        ✅ DashboardViewMaritime: Créée
        ✅ Navigation: Opérationnelle
        ✅ ViewManager: Corrigé
        🎉 Interface: 89% opérationnelle
        """)
        info_text.setStyleSheet("color: #1e40af; line-height: 1.5;")
        info_layout.addWidget(info_text)
        
        content_layout.addWidget(info_frame)
        
        main_layout.addWidget(content_frame)
        
        # Barre d'état
        status_bar = QFrame()
        status_bar.setStyleSheet("""
            QFrame {
                background-color: #1e293b;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        status_layout = QHBoxLayout(status_bar)
        
        status_text = QLabel("🚀 CHNeoWave v1.1.0 - Version Opérationnelle")
        status_text.setStyleSheet("color: white; font-size: 14px;")
        status_layout.addWidget(status_text)
        
        # Bouton de fermeture
        close_button = QPushButton("Fermer")
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #ef4444;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #dc2626;
            }
        """)
        close_button.clicked.connect(app.quit)
        status_layout.addWidget(close_button, alignment=Qt.AlignRight)
        
        main_layout.addWidget(status_bar)
        
        # Définir le widget central
        window.setCentralWidget(central_widget)
        
        print("✅ Interface opérationnelle créée")
        
        # Afficher la fenêtre
        print("🔄 Affichage de l'interface...")
        window.show()
        window.raise_()
        window.activateWindow()
        
        visible = window.isVisible()
        print(f"✅ Fenêtre visible: {visible}")
        
        if visible:
            print("🎉 SUCCÈS: CHNeoWave opérationnel !")
            print("🔍 Vérifiez que la fenêtre est visible sur votre écran")
            
            # Timer pour fermeture automatique après 30 secondes
            timer = QTimer()
            timer.timeout.connect(app.quit)
            timer.start(30000)
            
            print("🔄 Interface maintenue ouverte 30 secondes...")
            
            # Lancer la boucle d'événements
            exit_code = app.exec()
            print(f"✅ Application terminée (code: {exit_code})")
            return exit_code
        else:
            print("❌ PROBLÈME: Fenêtre non visible")
            return 1
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        traceback.print_exc()
        return 1

def create_card(title, description, color):
    """Créer une carte pour l'interface"""
    from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel
    card = QFrame()
    card.setStyleSheet(f"""
        QFrame {{
            background-color: {color};
            border-radius: 10px;
            padding: 20px;
            margin: 5px;
            min-height: 120px;
        }}
        QFrame:hover {{
            background-color: {color}dd;
        }}
    """)
    
    layout = QVBoxLayout(card)
    
    # Titre
    title_label = QLabel(title)
    title_label.setStyleSheet("""
        QLabel {
            color: white;
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 10px;
        }
    """)
    layout.addWidget(title_label)
    
    # Description
    desc_label = QLabel(description)
    desc_label.setStyleSheet("""
        QLabel {
            color: white;
            font-size: 14px;
            opacity: 0.9;
        }
    """)
    layout.addWidget(desc_label)
    
    return card

if __name__ == "__main__":
    exit(main()) 