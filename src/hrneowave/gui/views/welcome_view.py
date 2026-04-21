# -*- coding: utf-8 -*-
"""
Vue d'accueil CHNeoWave - Interface Moderne
Étape 1 : Créer ou ouvrir un projet

Auteur: Architecte Logiciel en Chef (ALC)
Date: 2025-01-26
Version: 1.1.0
"""

import logging

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QLineEdit, 
    QPushButton, QDateEdit, QTextEdit, QFrame, QScrollArea, QGridLayout
)
from PySide6.QtCore import Signal, QDate, Qt, QPropertyAnimation, QEasingCurve, QRect, QTimer
from PySide6.QtGui import QFont, QPainter, QLinearGradient, QColor, QPalette

# Import des composants modernes
from ..components.modern_card import ModernCard
from ..components.animated_button import AnimatedButton
from ..components.theme_toggle import ThemeToggle
from ..layouts.golden_ratio_layout import GoldenRatioLayout
from ..styles.maritime_theme import MaritimeTheme


logger = logging.getLogger(__name__)


class WelcomeView(QWidget):
    """
    Vue d'accueil moderne pour CHNeoWave
    Utilise le design system avec nombre d'or et thème maritime
    """
    
    # Signaux
    projectSelected = Signal(str)  # Chemin du projet
    projectCreationRequested = Signal(dict)  # Métadonnées du projet
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Thème maritime
        self.theme = MaritimeTheme()
        
        # Métadonnées du projet
        self.project_metadata = {}
        
        # Configuration de l'interface
        self._setup_ui()
        self._apply_theme()
        
        # Configuration des connexions avec un délai pour s'assurer que tout est initialisé
        QTimer.singleShot(100, self._setup_connections)
        
        # Animation d'entrée
        self._animate_entrance()
    
    def _setup_ui(self):
        """Configuration de l'interface utilisateur moderne"""
        # Layout principal avec Golden Ratio
        main_layout = GoldenRatioLayout(self)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(30)
        
        # Zone de défilement
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Widget de contenu
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(30)
        
        # En-tête avec titre et logo
        self._create_header(content_layout)
        
        # Carte principale de création de projet
        self._create_project_card(content_layout)
        
        # Actions rapides
        self._create_quick_actions(content_layout)
        
        # Informations système
        self._create_system_info(content_layout)
        
        # Espacement flexible
        content_layout.addStretch()
        
        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)
    
    def _create_header(self, layout):
        """Crée l'en-tête avec titre et navigation"""
        header_frame = QFrame()
        header_frame.setObjectName("welcomeHeader")
        header_layout = QHBoxLayout(header_frame)
        
        # Titre principal
        title_label = QLabel("CHNeoWave")
        title_label.setObjectName("mainTitle")
        title_font = QFont("Segoe UI", 32, QFont.Bold)
        title_label.setFont(title_font)
        
        # Sous-titre
        subtitle_label = QLabel("Système d'Acquisition Maritime Avancé")
        subtitle_label.setObjectName("subtitle")
        subtitle_font = QFont("Segoe UI", 14)
        subtitle_label.setFont(subtitle_font)
        
        # Layout du titre
        title_layout = QVBoxLayout()
        title_layout.addWidget(title_label)
        title_layout.addWidget(subtitle_label)
        title_layout.setSpacing(5)
        
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        
        # Toggle de thème
        self.theme_toggle = ThemeToggle()
        header_layout.addWidget(self.theme_toggle)
        
        layout.addWidget(header_frame)
    
    def _create_project_card(self, layout):
        """Crée la carte principale de création de projet"""
        # Utiliser un QFrame simple pour éviter les problèmes de layout
        self.project_card = QFrame()
        self.project_card.setObjectName("projectCard")
        self.project_card.setMinimumHeight(400)
        self.project_card.setFrameShape(QFrame.Box)
        self.project_card.setStyleSheet("""
            #projectCard {
                background-color: #ffffff;
                border: 1px solid #e0e6ed;
                border-radius: 12px;
                margin: 5px;
            }
        """)
        
        # Layout de la carte
        card_layout = QVBoxLayout(self.project_card)
        card_layout.setSpacing(20)
        card_layout.setContentsMargins(20, 20, 20, 20)
        
        # Titre de la carte
        title_label = QLabel("Nouveau Projet")
        title_label.setObjectName("cardTitle")
        title_label.setStyleSheet("""
            #cardTitle {
                font-size: 18px;
                font-weight: bold;
                color: #2c5aa0;

            }
        """)
        card_layout.addWidget(title_label)
        
        # Description
        desc_label = QLabel("Créez un nouveau projet d'acquisition maritime")
        desc_label.setObjectName("cardDescription")
        desc_label.setWordWrap(True)
        card_layout.addWidget(desc_label)
        
        # Formulaire avec Golden Ratio
        form_widget = QWidget()
        form_layout = QFormLayout(form_widget)
        form_layout.setSpacing(15)
        
        # Champs du formulaire
        self.project_name = QLineEdit()
        self.project_name.setPlaceholderText("Nom du projet d'essai")
        self.project_name.setObjectName("modernInput")
        form_layout.addRow("Nom du Projet *:", self.project_name)
        
        self.project_manager = QLineEdit()
        self.project_manager.setPlaceholderText("Chef de projet")
        self.project_manager.setObjectName("modernInput")
        form_layout.addRow("Chef de Projet *:", self.project_manager)
        
        self.laboratory = QLineEdit()
        self.laboratory.setPlaceholderText("Laboratoire d'origine")
        self.laboratory.setObjectName("modernInput")
        form_layout.addRow("Laboratoire *:", self.laboratory)
        
        self.project_date = QDateEdit()
        self.project_date.setDate(QDate.currentDate())
        self.project_date.setObjectName("modernInput")
        form_layout.addRow("Date de l'Essai:", self.project_date)
        
        self.description = QTextEdit()
        self.description.setPlaceholderText("Description de l'essai (optionnel)")
        self.description.setMaximumHeight(100)
        self.description.setObjectName("modernTextArea")
        form_layout.addRow("Description:", self.description)
        
        card_layout.addWidget(form_widget)
        
        # Bouton de validation animé
        self.create_button = AnimatedButton("Créer le Projet")
        self.create_button.setObjectName("primaryButton")
        self.create_button.setMinimumHeight(50)
        self.create_button.setEnabled(False)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.create_button)
        card_layout.addLayout(button_layout)
        
        layout.addWidget(self.project_card)
    
    def _create_quick_actions(self, layout):
        """Crée les actions rapides"""
        actions_frame = QFrame()
        actions_frame.setObjectName("quickActions")
        actions_layout = QHBoxLayout(actions_frame)
        actions_layout.setSpacing(20)
        
        # Bouton ouvrir projet existant
        open_button = AnimatedButton("Ouvrir un Projet")
        open_button.setObjectName("secondaryButton")
        open_button.setMinimumHeight(45)
        open_button.clicked.connect(self._open_existing_project)
        
        # Bouton documentation
        docs_button = AnimatedButton("Documentation")
        docs_button.setObjectName("secondaryButton")
        docs_button.setMinimumHeight(45)
        docs_button.clicked.connect(self._open_documentation)
        
        # Bouton exemples
        examples_button = AnimatedButton("Projets Exemples")
        examples_button.setObjectName("secondaryButton")
        examples_button.setMinimumHeight(45)
        examples_button.clicked.connect(self._load_examples)
        
        actions_layout.addWidget(open_button)
        actions_layout.addWidget(docs_button)
        actions_layout.addWidget(examples_button)
        actions_layout.addStretch()
        
        layout.addWidget(actions_frame)
    
    def _create_system_info(self, layout):
        """Crée les informations système"""
        info_card = ModernCard("Informations Système")
        info_card.setMaximumHeight(200)
        
        info_layout = QGridLayout(info_card.content_widget)
        info_layout.setSpacing(10)
        
        # Version
        version_label = QLabel("Version: CHNeoWave v1.1.0")
        version_label.setObjectName("systemInfo")
        info_layout.addWidget(version_label, 0, 0)
        
        # Statut
        status_label = QLabel("Statut: Prêt")
        status_label.setObjectName("systemInfo")
        info_layout.addWidget(status_label, 0, 1)
        
        # Dernière mise à jour
        update_label = QLabel("Dernière MAJ: 26/01/2025")
        update_label.setObjectName("systemInfo")
        info_layout.addWidget(update_label, 1, 0)
        
        # Licence
        license_label = QLabel("Licence: Propriétaire")
        license_label.setObjectName("systemInfo")
        info_layout.addWidget(license_label, 1, 1)
        
        layout.addWidget(info_card)
    
    def _setup_connections(self):
        """Configuration des connexions de signaux"""
        def safe_connect(widget_name, signal_name, handler):
            widget = getattr(self, widget_name, None)
            if widget is None:
                return

            try:
                signal = getattr(widget, signal_name, None)
                if signal is not None:
                    signal.connect(handler)
            except RuntimeError as exc:
                # Un QTimer peut se declencher apres destruction de la vue.
                logger.debug("Connexion ignoree sur widget supprime %s: %s", widget_name, exc)

        safe_connect("project_name", "textChanged", self._validate_form)
        safe_connect("project_manager", "textChanged", self._validate_form)
        safe_connect("laboratory", "textChanged", self._validate_form)
        safe_connect("create_button", "clicked", self._create_project)
        safe_connect("theme_toggle", "theme_changed", self._on_theme_changed)
    
    def _apply_theme(self):
        """Applique le thème maritime moderne"""
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {self.theme.colors['background']};
                color: {self.theme.colors['on_background']};
                font-family: 'Segoe UI', sans-serif;
            }}
            
            #welcomeHeader {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {self.theme.colors['primary']},
                    stop:1 {self.theme.colors['secondary']});
                border-radius: 15px;
                padding: 20px;

            }}
            
            #mainTitle {{
                color: white;
                font-weight: bold;
            }}
            
            #subtitle {{
                color: rgba(255, 255, 255, 0.8);
                font-style: italic;
            }}
            
            #cardDescription {{
                color: {self.theme.colors['on_surface']};
                font-size: 14px;

            }}
            
            #modernInput {{
                background-color: {self.theme.colors['surface']};
                border: 2px solid {self.theme.colors['border']};
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
                min-height: 20px;
            }}
            
            #modernInput:focus {{
                border-color: {self.theme.colors['primary']};
                background-color: {self.theme.colors['background']};
            }}
            
            #modernTextArea {{
                background-color: {self.theme.colors['surface']};
                border: 2px solid {self.theme.colors['border']};
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
            }}
            
            #primaryButton {{
                background-color: {self.theme.colors['primary']};
                color: white;
                border: none;
                border-radius: 10px;
                padding: 15px 30px;
                font-weight: bold;
                font-size: 14px;
            }}
            
            #primaryButton:hover {{
                background-color: {self.theme.colors['primary_variant']};
            }}
            
            #primaryButton:disabled {{
                background-color: {self.theme.colors['surface_dim']};
                color: {self.theme.colors['on_surface_variant']};
            }}
            
            #secondaryButton {{
                background-color: {self.theme.colors['surface']};
                color: {self.theme.colors['on_surface']};
                border: 2px solid {self.theme.colors['border']};
                border-radius: 8px;
                padding: 12px 20px;
                font-size: 13px;
            }}
            
            #secondaryButton:hover {{
                background-color: {self.theme.colors['surface_variant']};
                border-color: {self.theme.colors['primary']};
            }}
            
            #systemInfo {{
                color: {self.theme.colors['on_surface_variant']};
                font-size: 12px;
                padding: 5px;
            }}
            
            #quickActions {{
                background-color: {self.theme.colors['surface']};
                border-radius: 10px;
                padding: 20px;
            }}
        """)
    
    def _validate_form(self):
        """Valide le formulaire et active/désactive le bouton"""
        name_valid = len(self.project_name.text().strip()) >= 3
        manager_valid = len(self.project_manager.text().strip()) >= 2
        lab_valid = len(self.laboratory.text().strip()) >= 2
        
        self.create_button.setEnabled(name_valid and manager_valid and lab_valid)
    
    def _create_project(self):
        """Crée un nouveau projet avec les données saisies"""
        self.project_metadata = {
            'name': self.project_name.text().strip(),
            'manager': self.project_manager.text().strip(),
            'laboratory': self.laboratory.text().strip(),
            'date': self.project_date.date().toString(Qt.ISODate),
            'description': self.description.toPlainText().strip(),
            'created_at': QDate.currentDate().toString(Qt.ISODate)
        }
        
        # Émettre le signal
        self.projectCreationRequested.emit(self.project_metadata)
    
    def _open_existing_project(self):
        """Ouvre un projet existant"""
        # TODO: Implémenter l'ouverture de projet
        pass
    
    def _open_documentation(self):
        """Ouvre la documentation"""
        # TODO: Implémenter l'ouverture de la documentation
        pass
    
    def _load_examples(self):
        """Charge des projets exemples"""
        # TODO: Implémenter le chargement d'exemples
        pass
    
    def _on_theme_changed(self, is_dark):
        """Gère le changement de thème"""
        if is_dark:
            self.theme.set_dark_mode()
        else:
            self.theme.set_light_mode()
        self._apply_theme()
    
    def _animate_entrance(self):
        """Animation d'entrée de la vue"""
        self.setProperty("opacity", 0.0)
        
        self.fade_animation = QPropertyAnimation(self, b"opacity")
        self.fade_animation.setDuration(800)
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)
        self.fade_animation.setEasingCurve(QEasingCurve.OutCubic)
        self.fade_animation.start()
    
    def reset_view(self):
        """Réinitialise la vue"""
        self.project_name.clear()
        self.project_manager.clear()
        self.laboratory.clear()
        self.description.clear()
        self.project_date.setDate(QDate.currentDate())
        self.create_button.setEnabled(False)
    
    def get_project_metadata(self):
        """Retourne les métadonnées du projet"""
        return self.project_metadata
