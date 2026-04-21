#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CHNeoWave - Material Theme Manager v2.0
Gestionnaire de thèmes Material Design 3

Auteur: Architecte Logiciel en Chef (ALC)
Date: 2024
Version: 2.0.0
"""

import logging
from typing import Dict, Optional
from dataclasses import dataclass
from enum import Enum

try:
    from PyQt6.QtCore import QObject, pyqtSignal
    from PyQt6.QtGui import QColor, QPalette
    from PyQt6.QtWidgets import QApplication
except ImportError:
    # Fallback pour la transition
    from PySide6.QtCore import QObject, Signal
    from PySide6.QtGui import QColor, QPalette
    from PySide6.QtWidgets import QApplication

    pyqtSignal = Signal

from ..components.material_components import MaterialTheme, MaterialColor

logger = logging.getLogger(__name__)

class ThemeMode(Enum):
    """Modes de thème"""
    LIGHT = "light"
    DARK = "dark"
    AUTO = "auto"

class MaterialThemeManager(QObject):
    """Gestionnaire de thèmes Material Design 3"""
    
    theme_changed = pyqtSignal(MaterialTheme)
    
    def __init__(self):
        super().__init__()
        self._current_theme = MaterialTheme()
        self._theme_mode = ThemeMode.AUTO
        self._custom_themes: Dict[str, MaterialTheme] = {}
        
        # Thèmes prédéfinis
        self._setup_predefined_themes()
        
    def _setup_predefined_themes(self):
        """Configure les thèmes prédéfinis"""
        # Thème clair par défaut
        self._custom_themes['default_light'] = MaterialTheme()
        
        # Thème sombre par défaut
        self._custom_themes['default_dark'] = MaterialTheme().to_dark_theme()
        
        # Thème CHNeoWave (bleu océan)
        self._custom_themes['chneowave'] = MaterialTheme(
            primary="#0277BD",  # Bleu océan
            secondary="#00ACC1",  # Cyan
            tertiary="#26A69A",  # Teal
            surface="#F8FDFF",  # Bleu très clair
            background="#F8FDFF"
        )
        
        # Thème CHNeoWave sombre
        self._custom_themes['chneowave_dark'] = MaterialTheme(
            primary="#4FC3F7",
            secondary="#4DD0E1",
            tertiary="#4DB6AC",
            surface="#0D1B2A",
            background="#0D1B2A",
            on_surface="#E1F5FE",
            on_background="#E1F5FE",
            is_dark=True
        )
        
        # Thème laboratoire (vert scientifique)
        self._custom_themes['laboratory'] = MaterialTheme(
            primary="#2E7D32",  # Vert foncé
            secondary="#388E3C",  # Vert
            tertiary="#689F38",  # Vert clair
            surface="#F1F8E9",
            background="#F1F8E9"
        )
        
    def get_current_theme(self) -> MaterialTheme:
        """Retourne le thème actuel"""
        return self._current_theme
        
    def set_theme_mode(self, mode: ThemeMode):
        """Définit le mode de thème"""
        self._theme_mode = mode
        self._update_theme()
        
    def set_custom_theme(self, theme_name: str):
        """Applique un thème personnalisé"""
        if theme_name in self._custom_themes:
            self._current_theme = self._custom_themes[theme_name]
            self.theme_changed.emit(self._current_theme)
            logger.info(f"Thème appliqué: {theme_name}")
        else:
            logger.warning(f"Thème inconnu: {theme_name}")
            
    def register_custom_theme(self, name: str, theme: MaterialTheme):
        """Enregistre un thème personnalisé"""
        self._custom_themes[name] = theme
        logger.info(f"Thème personnalisé enregistré: {name}")
        
    def get_available_themes(self) -> Dict[str, str]:
        """Retourne la liste des thèmes disponibles"""
        return {
            'default_light': 'Défaut Clair',
            'default_dark': 'Défaut Sombre',
            'chneowave': 'CHNeoWave Océan',
            'chneowave_dark': 'CHNeoWave Océan Sombre',
            'laboratory': 'Laboratoire'
        }
        
    def _update_theme(self):
        """Met à jour le thème selon le mode"""
        if self._theme_mode == ThemeMode.LIGHT:
            self._current_theme = self._custom_themes['chneowave']
        elif self._theme_mode == ThemeMode.DARK:
            self._current_theme = self._custom_themes['chneowave_dark']
        else:  # AUTO
            # Détection automatique (pour l'instant, utilise le thème clair)
            self._current_theme = self._custom_themes['chneowave']
            
        self.theme_changed.emit(self._current_theme)
        
    def apply_to_application(self, app: QApplication):
        """Applique le thème à l'application"""
        if app is None:
            app = QApplication.instance()
        
        if app:
            # Applique le CSS global
            app.setStyleSheet(self.get_theme_css())
            
            # Applique la palette
            app.setPalette(self.create_palette())
            
            logger.info(f"Thème appliqué à l'application: {self._current_theme}")
        
    def create_palette(self) -> QPalette:
        """Crée une palette Qt à partir du thème actuel"""
        palette = QPalette()
        
        # Couleurs de base
        palette.setColor(QPalette.ColorRole.Window, QColor(self._current_theme.background))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(self._current_theme.on_background))
        palette.setColor(QPalette.ColorRole.Base, QColor(self._current_theme.surface))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(self._current_theme.surface_variant))
        palette.setColor(QPalette.ColorRole.Text, QColor(self._current_theme.on_surface))
        palette.setColor(QPalette.ColorRole.Button, QColor(self._current_theme.primary))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(self._current_theme.on_primary))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(self._current_theme.primary))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(self._current_theme.on_primary))
        
        return palette
        
    def get_theme_stylesheet(self, theme_mode: Optional[ThemeMode] = None) -> str:
        """Retourne la feuille de style CSS pour un mode donné"""
        if theme_mode:
            old_mode = self._theme_mode
            self._theme_mode = theme_mode
            self._update_theme()
            css = self.get_theme_css()
            self._theme_mode = old_mode
            self._update_theme()
            return css
        return self.get_theme_css()
    
    def apply_theme(self, theme_mode: ThemeMode, app: Optional[QApplication] = None):
        """Applique un thème avec le mode spécifié"""
        self.set_theme_mode(theme_mode)
        self.apply_to_application(app)
    
    def get_theme_css(self) -> str:
        """Génère le CSS global pour le thème actuel"""
        return f"""
        QMainWindow {{
            background-color: {self._current_theme.background};
            color: {self._current_theme.on_background};
        }}
        
        QWidget {{
            background-color: {self._current_theme.surface};
            color: {self._current_theme.on_surface};
        }}
        
        QMenuBar {{
            background-color: {self._current_theme.surface};
            color: {self._current_theme.on_surface};
            border-bottom: 1px solid {self._current_theme.outline_variant};
        }}
        
        QMenuBar::item {{
            background-color: transparent;
            padding: 8px 12px;
        }}
        
        QMenuBar::item:selected {{
            background-color: {self._current_theme.primary_container};
            color: {self._current_theme.on_primary_container};
        }}
        
        QMenu {{
            background-color: {self._current_theme.surface};
            color: {self._current_theme.on_surface};
            border: 1px solid {self._current_theme.outline_variant};
        }}
        
        QMenu::item {{
            padding: 8px 16px;
        }}
        
        QMenu::item:selected {{
            background-color: {self._current_theme.primary_container};
            color: {self._current_theme.on_primary_container};
        }}
        
        QStatusBar {{
            background-color: {self._current_theme.surface_variant};
            color: {self._current_theme.on_surface_variant};
            border-top: 1px solid {self._current_theme.outline_variant};
        }}
        
        QToolBar {{
            background-color: {self._current_theme.surface};
            border: 1px solid {self._current_theme.outline_variant};
        }}
        
        QDockWidget {{
            background-color: {self._current_theme.surface};
            color: {self._current_theme.on_surface};
        }}
        
        QDockWidget::title {{
            background-color: {self._current_theme.surface_variant};
            color: {self._current_theme.on_surface_variant};
            padding: 8px;
        }}
        
        /* Classes Material-3 personnalisées */
        .btn-accent {{
            background-color: {self._current_theme.primary};
            color: {self._current_theme.on_primary};
            border: none;
            border-radius: 8px;
            padding: 12px 24px;
            font-weight: 500;
        }}
        
        .btn-accent:hover {{
            background-color: {self._current_theme.primary_container};
            color: {self._current_theme.on_primary_container};
        }}
        
        .btn-accent:pressed {{
            background-color: {self._current_theme.primary};
            color: {self._current_theme.on_primary};
        }}
        
        .dock-card {{
            background-color: {self._current_theme.surface};
            color: {self._current_theme.on_surface};
            border: 1px solid {self._current_theme.outline_variant};
            border-radius: 8px;
            padding: 16px;
        }}
        
        .dock-card:hover {{
            /* Effet de survol sans box-shadow */
        }}
        """

# Instance globale du gestionnaire de thèmes
_theme_manager = None

def get_theme_manager() -> MaterialThemeManager:
    """Retourne l'instance globale du gestionnaire de thèmes"""
    global _theme_manager
    if _theme_manager is None:
        _theme_manager = MaterialThemeManager()
    return _theme_manager

def apply_theme_to_widget(widget, theme: Optional[MaterialTheme] = None):
    """Applique un thème à un widget spécifique"""
    if theme is None:
        theme = get_theme_manager().get_current_theme()
        
    # Applique le style de base
    widget.setStyleSheet(f"""
    QWidget {{
        background-color: {theme.surface};
        color: {theme.on_surface};
    }}
    """)
    
    # Si le widget a une méthode set_theme, l'utilise
    if hasattr(widget, 'set_theme'):
        widget.set_theme(theme)
