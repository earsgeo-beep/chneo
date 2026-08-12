#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CHNeoWave - Système d'aide contextuelle
Fournit une aide contextuelle et des tooltips améliorés

Auteur: Architecte Logiciel en Chef (ALC)
Date: 2024
Version: 1.0.0
"""

import logging
from typing import Dict, Optional, Any
from enum import Enum

from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton,
    QFrame, QScrollArea, QTextEdit, QSplitter, QTreeWidget,
    QTreeWidgetItem, QApplication, QToolTip
)
from PySide6.QtCore import Qt, Signal, QTimer, QPoint, QRect, QObject, QEvent
from PySide6.QtGui import QFont, QPixmap, QIcon, QPainter, QPen

from .material_components import MaterialButton, MaterialCard


class HelpLevel(Enum):
    """Niveaux d'aide disponibles"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class HelpCategory(Enum):
    """Catégories d'aide"""
    GENERAL = "general"
    PROJECT = "project"
    ACQUISITION = "acquisition"
    ANALYSIS = "analysis"
    CALIBRATION = "calibration"
    EXPORT = "export"


class ContextualHelp:
    """Gestionnaire d'aide contextuelle"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.help_data = self._load_help_data()
        self.current_context = None
        self.help_level = HelpLevel.INTERMEDIATE
    
    def _load_help_data(self) -> Dict[str, Any]:
        """Charge les données d'aide"""
        return {
            "welcome": {
                "title": "Écran d'accueil",
                "description": "Créez un nouveau projet ou ouvrez un projet existant",
                "tips": [
                    "Renseignez soigneusement les métadonnées du projet",
                    "Le type de bassin influence les paramètres d'acquisition",
                    "L'opérateur sera associé à toutes les acquisitions"
                ],
                "shortcuts": {
                    "Ctrl+N": "Nouveau projet",
                    "Ctrl+O": "Ouvrir projet"
                }
            },
            "dashboard": {
                "title": "Tableau de bord",
                "description": "Vue d'ensemble du projet et navigation principale",
                "tips": [
                    "Vérifiez l'état des capteurs avant l'acquisition",
                    "Consultez les paramètres du projet si nécessaire",
                    "La calibration est recommandée avant la première acquisition"
                ],
                "shortcuts": {
                    "Ctrl+A": "Aller à l'acquisition",
                    "Ctrl+S": "Paramètres du projet"
                }
            },
            "acquisition": {
                "title": "Acquisition de données",
                "description": "Configuration et lancement des acquisitions",
                "tips": [
                    "Vérifiez la fréquence d'échantillonnage",
                    "Surveillez la qualité du signal en temps réel",
                    "Utilisez la pause pour ajuster les paramètres",
                    "Sauvegardez régulièrement vos données"
                ],
                "shortcuts": {
                    "Space": "Démarrer/Arrêter acquisition",
                    "P": "Pause/Reprendre",
                    "Ctrl+E": "Exporter données"
                }
            },
            "analysis": {
                "title": "Analyse des données",
                "description": "Traitement et analyse des signaux acquis",
                "tips": [
                    "Sélectionnez la plage de données à analyser",
                    "Appliquez les filtres appropriés",
                    "Comparez les résultats avec les références",
                    "Exportez les graphiques pour vos rapports"
                ],
                "shortcuts": {
                    "Ctrl+R": "Lancer l'analyse",
                    "Ctrl+F": "Appliquer filtres",
                    "Ctrl+G": "Générer graphiques"
                }
            },
            "calibration": {
                "title": "Calibration des capteurs",
                "description": "Étalonnage et vérification des capteurs",
                "tips": [
                    "Effectuez la calibration dans des conditions stables",
                    "Utilisez des références connues",
                    "Vérifiez la linéarité des capteurs",
                    "Documentez les paramètres de calibration"
                ],
                "shortcuts": {
                    "Ctrl+C": "Démarrer calibration",
                    "Ctrl+V": "Valider calibration"
                }
            }
        }
    
    def get_help_for_context(self, context: str) -> Optional[Dict[str, Any]]:
        """Retourne l'aide pour un contexte donné"""
        return self.help_data.get(context)
    
    def set_help_level(self, level: HelpLevel):
        """Définit le niveau d'aide"""
        self.help_level = level
        self.logger.info(f"Niveau d'aide défini à: {level.value}")
    
    def get_tooltip_for_widget(self, widget_name: str, context: str = None) -> str:
        """Génère un tooltip contextuel pour un widget"""
        tooltips = {
            "btn_start_acquisition": "Démarre l'acquisition de données (Espace)",
            "btn_stop_acquisition": "Arrête l'acquisition en cours (Espace)",
            "btn_pause_acquisition": "Met en pause l'acquisition (P)",
            "btn_export_data": "Exporte les données acquises (Ctrl+E)",
            "btn_calibrate": "Lance la calibration des capteurs (Ctrl+C)",
            "btn_analyze": "Démarre l'analyse des données (Ctrl+R)",
            "spin_sample_rate": "Fréquence d'échantillonnage en Hz",
            "spin_duration": "Durée d'acquisition en secondes",
            "combo_acquisition_mode": "Équipement physique et pilote sélectionnés",
            "progress_acquisition": "Progression de l'acquisition en cours",
            "chart_realtime": "Affichage temps réel des signaux",
            "list_sensors": "Liste des capteurs connectés",
            "btn_new_project": "Crée un nouveau projet (Ctrl+N)",
            "btn_open_project": "Ouvre un projet existant (Ctrl+O)",
            "btn_save_project": "Sauvegarde le projet (Ctrl+S)"
        }
        
        base_tooltip = tooltips.get(widget_name, "")
        
        # Ajouter des informations contextuelles selon le niveau d'aide
        if self.help_level == HelpLevel.BEGINNER and context:
            context_help = self.get_help_for_context(context)
            if context_help and 'tips' in context_help:
                relevant_tips = [tip for tip in context_help['tips'] if widget_name.split('_')[-1] in tip.lower()]
                if relevant_tips:
                    base_tooltip += f"\n\nConseil : {relevant_tips[0]}"
        
        return base_tooltip


class HelpPanel(QWidget):
    """Panneau d'aide contextuelle"""
    
    help_requested = Signal(str)  # Émis quand l'utilisateur demande de l'aide
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.help_system = ContextualHelp()
        self.current_context = None
        
        self._setup_ui()
        self._setup_connections()
    
    def _setup_ui(self):
        """Configure l'interface du panneau d'aide"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # En-tête
        header_layout = QHBoxLayout()
        
        self.title_label = QLabel("Aide")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        header_layout.addWidget(self.title_label)
        
        header_layout.addStretch()
        
        # Bouton de niveau d'aide
        self.level_button = MaterialButton("Intermédiaire", style=MaterialButton.Style.TEXT)
        self.level_button.clicked.connect(self._toggle_help_level)
        header_layout.addWidget(self.level_button)
        
        layout.addLayout(header_layout)
        
        # Séparateur
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator)
        
        # Zone de contenu avec scroll
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        
        scroll_area.setWidget(self.content_widget)
        layout.addWidget(scroll_area)
        
        # Zone de raccourcis
        self.shortcuts_card = MaterialCard()
        self.shortcuts_layout = QVBoxLayout(self.shortcuts_card)
        
        shortcuts_title = QLabel("Raccourcis clavier")
        shortcuts_font = QFont()
        shortcuts_font.setBold(True)
        shortcuts_title.setFont(shortcuts_font)
        self.shortcuts_layout.addWidget(shortcuts_title)
        
        self.shortcuts_content = QLabel()
        self.shortcuts_content.setWordWrap(True)
        self.shortcuts_layout.addWidget(self.shortcuts_content)
        
        layout.addWidget(self.shortcuts_card)
        
        # Initialiser avec l'aide générale
        self.update_context("general")
    
    def _setup_connections(self):
        """Configure les connexions de signaux"""
        pass
    
    def _toggle_help_level(self):
        """Bascule entre les niveaux d'aide"""
        current_level = self.help_system.help_level
        
        if current_level == HelpLevel.BEGINNER:
            new_level = HelpLevel.INTERMEDIATE
            self.level_button.setText("Intermédiaire")
        elif current_level == HelpLevel.INTERMEDIATE:
            new_level = HelpLevel.ADVANCED
            self.level_button.setText("Avancé")
        else:
            new_level = HelpLevel.BEGINNER
            self.level_button.setText("Débutant")
        
        self.help_system.set_help_level(new_level)
        self.update_context(self.current_context)  # Rafraîchir l'affichage
    
    def update_context(self, context: str):
        """Met à jour l'aide pour un nouveau contexte"""
        self.current_context = context
        help_data = self.help_system.get_help_for_context(context)
        
        if not help_data:
            self._show_general_help()
            return
        
        # Effacer le contenu précédent
        for i in reversed(range(self.content_layout.count())):
            item = self.content_layout.itemAt(i)
            if item and item.widget():
                item.widget().setParent(None)
        
        # Titre du contexte
        context_title = QLabel(help_data.get('title', context.title()))
        context_font = QFont()
        context_font.setPointSize(12)
        context_font.setBold(True)
        context_title.setFont(context_font)
        self.content_layout.addWidget(context_title)
        
        # Description
        description = QLabel(help_data.get('description', ''))
        description.setWordWrap(True)
        description.setStyleSheet("color: #666;")
        self.content_layout.addWidget(description)
        
        # Conseils
        tips = help_data.get('tips', [])
        if tips:
            tips_title = QLabel("Conseils techniques")
            tips_font = QFont()
            tips_font.setBold(True)
            tips_title.setFont(tips_font)
            self.content_layout.addWidget(tips_title)
            
            for tip in tips:
                tip_label = QLabel(f"• {tip}")
                tip_label.setWordWrap(True)
                tip_label.setStyleSheet("color: #666;")
                self.content_layout.addWidget(tip_label)
        
        # Raccourcis clavier
        shortcuts = help_data.get('shortcuts', {})
        if shortcuts:
            shortcuts_text = ""
            for key, action in shortcuts.items():
                shortcuts_text += f"<b>{key}</b>: {action}<br>"
            self.shortcuts_content.setText(shortcuts_text)
            self.shortcuts_card.show()
        else:
            self.shortcuts_card.hide()
        
        self.content_layout.addStretch()
    
    def _show_general_help(self):
        """Affiche l'aide générale"""
        # Effacer le contenu précédent
        for i in reversed(range(self.content_layout.count())):
            item = self.content_layout.itemAt(i)
            if item and item.widget():
                item.widget().setParent(None)
        
        general_title = QLabel("Aide générale")
        general_font = QFont()
        general_font.setPointSize(12)
        general_font.setBold(True)
        general_title.setFont(general_font)
        self.content_layout.addWidget(general_title)
        
        general_text = QLabel(
            "Bienvenue dans CHNeoWave !\n\n"
            "Utilisez la navigation latérale pour accéder aux différentes fonctionnalités. "
            "L'aide contextuelle s'adapte automatiquement à votre position dans l'application.\n\n"
            "Vous pouvez ajuster le niveau d'aide selon votre expérience."
        )
        general_text.setWordWrap(True)
        self.content_layout.addWidget(general_text)
        
        self.content_layout.addStretch()
        self.shortcuts_card.hide()


class SmartTooltip(QObject):
    """Système de tooltips intelligents"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.help_system = ContextualHelp()
        self.tooltip_timer = QTimer(self)
        self.tooltip_timer.setSingleShot(True)
        self.tooltip_timer.timeout.connect(self._show_enhanced_tooltip)
        self.current_widget = None
        self.current_context = None
    
    def install_on_widget(self, widget: QWidget, widget_name: str, context: str = None):
        """Installe un tooltip intelligent sur un widget"""
        tooltip_text = self.help_system.get_tooltip_for_widget(widget_name, context)
        widget.setToolTip(tooltip_text)
        
        # Installer un filtre d'événements pour les tooltips avancés
        widget.installEventFilter(self)
        widget.setProperty("tooltip_widget_name", widget_name)
        widget.setProperty("tooltip_context", context)
    
    def eventFilter(self, obj, event):
        """Filtre les événements pour gérer les tooltips avancés"""
        if event.type() == QEvent.Enter:
            self.current_widget = obj
            self.current_context = obj.property("tooltip_context")
            # Démarrer un timer pour afficher un tooltip enrichi après un délai
            self.tooltip_timer.start(1000)  # 1 seconde
        elif event.type() == QEvent.Leave:
            self.tooltip_timer.stop()
            self.current_widget = None
            self.current_context = None
        
        return False
    
    def _show_enhanced_tooltip(self):
        """Affiche un tooltip enrichi"""
        if not self.current_widget:
            return
        
        widget_name = self.current_widget.property("tooltip_widget_name")
        context = self.current_widget.property("tooltip_context")
        
        if not widget_name:
            return
        
        # Créer un tooltip enrichi avec plus d'informations
        enhanced_text = self.help_system.get_tooltip_for_widget(widget_name, context)
        
        # Afficher le tooltip à la position de la souris
        from PySide6.QtGui import QCursor
        cursor_pos = QCursor.pos()
        QToolTip.showText(cursor_pos, enhanced_text, self.current_widget)


# Instance globale du système d'aide
_help_system = None
_smart_tooltip = None

def get_help_system() -> ContextualHelp:
    """Retourne l'instance globale du système d'aide"""
    global _help_system
    if _help_system is None:
        _help_system = ContextualHelp()
    return _help_system

def get_smart_tooltip() -> SmartTooltip:
    """Retourne l'instance globale du système de tooltips"""
    global _smart_tooltip
    if _smart_tooltip is None:
        _smart_tooltip = SmartTooltip()
    return _smart_tooltip

def install_help_on_widget(widget: QWidget, widget_name: str, context: str = None):
    """Fonction utilitaire pour installer l'aide sur un widget"""
    smart_tooltip = get_smart_tooltip()
    smart_tooltip.install_on_widget(widget, widget_name, context)
