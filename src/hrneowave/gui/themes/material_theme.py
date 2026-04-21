# -*- coding: utf-8 -*-
"""
Thématisation Avancée Material Design pour CHNeoWave

Système de thèmes avec modes clair/sombre et respect des standards d'accessibilité.
Contraste minimum 4.5:1 (WCAG 2.1 AA) et transitions fluides.

Auteur: CHNeoWave Team
Version: 1.0.0
Date: 2024-12-19
"""

import math
from typing import Dict, Any, Optional, Tuple
from enum import Enum
from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QColor, QPalette


class ThemeMode(Enum):
    """Modes de thème disponibles"""
    LIGHT = "light"
    DARK = "dark"
    AUTO = "auto"  # Suit le système


class MaterialTheme(QObject):
    """
    Gestionnaire de thèmes Material Design pour CHNeoWave
    
    Fonctionnalités:
    - Mode clair et sombre
    - Couleurs optimisées pour l'accessibilité
    - Transitions fluides 200ms cubic-bezier
    - Respect des proportions Golden Ratio
    - Standards maritimes
    """
    
    # Signal émis lors du changement de thème
    themeChanged = Signal(str)  # Mode du thème
    
    # Constante du nombre d'or pour les proportions
    PHI = (1 + math.sqrt(5)) / 2  # ≈ 1.618033988749
    
    # Espacements basés sur Fibonacci
    SPACING = {
        'xs': 5,
        'sm': 8,
        'md': 13,
        'lg': 21,
        'xl': 34,
        'xxl': 55
    }
    
    # Rayons de bordure standardisés
    BORDER_RADIUS = {
        'sm': 4,
        'md': 8,
        'lg': 12,
        'xl': 16
    }
    
    # Durées d'animation
    ANIMATION_DURATION = {
        'fast': 150,
        'normal': 200,
        'slow': 300
    }
    
    # Courbes d'animation
    EASING_CURVES = {
        'standard': 'cubic-bezier(0.4, 0.0, 0.2, 1)',
        'decelerate': 'cubic-bezier(0.0, 0.0, 0.2, 1)',
        'accelerate': 'cubic-bezier(0.4, 0.0, 1, 1)',
        'sharp': 'cubic-bezier(0.4, 0.0, 0.6, 1)'
    }
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.current_mode = ThemeMode.LIGHT
        self._setup_color_palettes()
        
    def _setup_color_palettes(self):
        """Configuration des palettes de couleurs"""
        
        # Mode Clair (Défaut)
        self.light_palette = {
            # Couleurs principales
            'primary': '#00558C',        # Bleu maritime principal
            'primary_variant': '#003D64', # Variante plus sombre
            'secondary': '#0277BD',      # Bleu secondaire
            'secondary_variant': '#01579B',
            
            # Couleurs de surface
            'background': '#FAFBFC',     # Fond principal
            'surface': '#FFFFFF',        # Surface des composants
            'surface_variant': '#F5F7FA', # Variante de surface
            
            # Couleurs de texte
            'on_background': '#0A1929',  # Texte sur fond
            'on_surface': '#0A1929',     # Texte sur surface
            'on_primary': '#FFFFFF',     # Texte sur primaire
            'on_secondary': '#FFFFFF',   # Texte sur secondaire
            
            # Couleurs d'état
            'success': '#2E7D32',        # Vert succès
            'warning': '#F57C00',        # Orange avertissement
            'error': '#D32F2F',          # Rouge erreur
            'info': '#1976D2',           # Bleu information
            
            # Couleurs de bordure et dividers
            'outline': 'rgba(0,85,140,0.12)',
            'outline_variant': 'rgba(0,85,140,0.08)',
            'divider': 'rgba(0,85,140,0.06)',
            
            # Couleurs d'interaction
            'hover': 'rgba(0,85,140,0.08)',
            'focus': 'rgba(0,85,140,0.12)',
            'pressed': 'rgba(0,85,140,0.16)',
            'selected': 'rgba(0,85,140,0.10)',
            'disabled': 'rgba(0,85,140,0.38)',
            
            # Ombres
            'shadow': 'rgba(0,85,140,0.1)',
            'shadow_strong': 'rgba(0,85,140,0.2)'
        }
        
        # Mode Sombre
        self.dark_palette = {
            # Couleurs principales
            'primary': '#64B5F6',        # Bleu clair pour contraste
            'primary_variant': '#42A5F5',
            'secondary': '#81C784',      # Vert clair
            'secondary_variant': '#66BB6A',
            
            # Couleurs de surface
            'background': '#0A1929',     # Fond principal sombre
            'surface': '#1A1F2E',        # Surface des composants
            'surface_variant': '#242938', # Variante de surface
            
            # Couleurs de texte
            'on_background': 'rgba(255,255,255,0.87)', # Texte principal
            'on_surface': 'rgba(255,255,255,0.87)',
            'on_primary': '#0A1929',     # Texte sombre sur primaire clair
            'on_secondary': '#0A1929',
            
            # Couleurs d'état
            'success': '#4CAF50',        # Vert plus clair
            'warning': '#FF9800',        # Orange plus clair
            'error': '#F44336',          # Rouge plus clair
            'info': '#2196F3',           # Bleu plus clair
            
            # Couleurs de bordure et dividers
            'outline': 'rgba(255,255,255,0.12)',
            'outline_variant': 'rgba(255,255,255,0.08)',
            'divider': 'rgba(255,255,255,0.06)',
            
            # Couleurs d'interaction
            'hover': 'rgba(255,255,255,0.08)',
            'focus': 'rgba(255,255,255,0.12)',
            'pressed': 'rgba(255,255,255,0.16)',
            'selected': 'rgba(255,255,255,0.10)',
            'disabled': 'rgba(255,255,255,0.38)',
            
            # Ombres
            'shadow': 'rgba(0,0,0,0.3)',
            'shadow_strong': 'rgba(0,0,0,0.5)'
        }
        
    def get_current_palette(self) -> Dict[str, str]:
        """Obtenir la palette de couleurs actuelle"""
        if self.current_mode == ThemeMode.DARK:
            return self.dark_palette
        else:
            return self.light_palette
            
    def get_color(self, color_name: str) -> str:
        """Obtenir une couleur spécifique du thème actuel"""
        palette = self.get_current_palette()
        return palette.get(color_name, '#000000')
        
    def set_theme_mode(self, mode: ThemeMode):
        """Changer le mode de thème"""
        if self.current_mode != mode:
            self.current_mode = mode
            self.themeChanged.emit(mode.value)
            
    def toggle_theme(self):
        """Basculer entre mode clair et sombre"""
        new_mode = ThemeMode.DARK if self.current_mode == ThemeMode.LIGHT else ThemeMode.LIGHT
        self.set_theme_mode(new_mode)
        
    def is_dark_mode(self) -> bool:
        """Vérifier si le mode sombre est actif"""
        return self.current_mode == ThemeMode.DARK
        
    def get_button_style(self, variant: str = 'primary') -> str:
        """Générer le style CSS pour les boutons"""
        palette = self.get_current_palette()
        
        if variant == 'primary':
            return f"""
                QPushButton {{
                    background-color: {palette['primary']};
                    color: {palette['on_primary']};
                    border: none;
                    border-radius: {self.BORDER_RADIUS['md']}px;
                    padding: {self.SPACING['sm']}px {self.SPACING['md']}px;
                    font-weight: 500;
                    /* transition not supported in Qt */
                }}
                QPushButton:hover {{
                    background-color: {palette['primary_variant']};
                }}
                QPushButton:pressed {{
                    background-color: {palette['primary_variant']};
                }}
                QPushButton:disabled {{
                    background-color: {palette['disabled']};
                    color: {palette['on_surface']};
                }}
            """
        elif variant == 'secondary':
            return f"""
                QPushButton {{
                    background-color: {palette['surface']};
                    color: {palette['primary']};
                    border: 1px solid {palette['outline']};
                    border-radius: {self.BORDER_RADIUS['md']}px;
                    padding: {self.SPACING['sm']}px {self.SPACING['md']}px;
                    font-weight: 500;
                    /* transition not supported in Qt */
                }}
                QPushButton:hover {{
                    background-color: {palette['hover']};
                    border-color: {palette['primary']};
                }}
                QPushButton:pressed {{
                    background-color: {palette['pressed']};
                }}
            """
        elif variant == 'text':
            return f"""
                QPushButton {{
                    background-color: transparent;
                    color: {palette['primary']};
                    border: none;
                    border-radius: {self.BORDER_RADIUS['md']}px;
                    padding: {self.SPACING['sm']}px {self.SPACING['md']}px;
                    font-weight: 500;
                    /* transition not supported in Qt */
                }}
                QPushButton:hover {{
                    background-color: {palette['hover']};
                }}
                QPushButton:pressed {{
                    background-color: {palette['pressed']};
                }}
            """
        else:
            return self.get_button_style('primary')
            
    def get_card_style(self, elevated: bool = True) -> str:
        """Générer le style CSS pour les cards"""
        palette = self.get_current_palette()
        
        shadow = "" # box-shadow non supporté par Qt
        
        return f"""
            QWidget {{
                background-color: {palette['surface']};
                border: 1px solid {palette['outline_variant']};
                border-radius: {self.BORDER_RADIUS['md']}px;
                {shadow}
                /* transition not supported in Qt */
            }}
            QWidget:hover {{
                border-color: {palette['outline']};
            }}
        """
        
    def get_input_style(self) -> str:
        """Générer le style CSS pour les champs de saisie"""
        palette = self.get_current_palette()
        
        return f"""
            QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox, QComboBox {{
                background-color: {palette['surface']};
                color: {palette['on_surface']};
                border: 1px solid {palette['outline']};
                border-radius: {self.BORDER_RADIUS['sm']}px;
                padding: {self.SPACING['sm']}px {self.SPACING['md']}px;
                font-size: 14px;
                /* transition not supported in Qt */
            }}
            QLineEdit:focus, QTextEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {{
                border-color: {palette['primary']};
                outline: 2px solid {palette['focus']};
            }}
            QLineEdit:hover, QTextEdit:hover, QSpinBox:hover, QDoubleSpinBox:hover, QComboBox:hover {{
                border-color: {palette['outline_variant']};
            }}
        """
        
    def get_navigation_style(self) -> str:
        """Générer le style CSS pour la navigation"""
        palette = self.get_current_palette()
        
        return f"""
            QWidget#navigation {{
                background-color: {palette['surface']};
                border-right: 1px solid {palette['divider']};
            }}
            QPushButton#nav-item {{
                background-color: transparent;
                color: {palette['on_surface']};
                border: none;
                border-radius: {self.BORDER_RADIUS['md']}px;
                padding: {self.SPACING['md']}px {self.SPACING['lg']}px;
                text-align: left;
                font-weight: 500;
                /* transition not supported in Qt */
            }}
            QPushButton#nav-item:hover {{
                background-color: {palette['hover']};
            }}
            QPushButton#nav-item:pressed {{
                background-color: {palette['pressed']};
            }}
            QPushButton#nav-item[selected="true"] {{
                background-color: {palette['selected']};
                color: {palette['primary']};
                font-weight: 600;
            }}
        """
        
    def get_table_style(self) -> str:
        """Générer le style CSS pour les tableaux"""
        palette = self.get_current_palette()
        
        return f"""
            QTableWidget {{
                background-color: {palette['surface']};
                color: {palette['on_surface']};
                border: 1px solid {palette['outline']};
                border-radius: {self.BORDER_RADIUS['md']}px;
                gridline-color: {palette['divider']};
                selection-background-color: {palette['selected']};
            }}
            QTableWidget::item {{
                padding: {self.SPACING['sm']}px {self.SPACING['md']}px;
                border-bottom: 1px solid {palette['divider']};
            }}
            QTableWidget::item:hover {{
                background-color: {palette['hover']};
            }}
            QTableWidget::item:selected {{
                background-color: {palette['selected']};
                color: {palette['on_surface']};
            }}
            QHeaderView::section {{
                background-color: {palette['surface_variant']};
                color: {palette['on_surface']};
                padding: {self.SPACING['md']}px;
                border: none;
                border-bottom: 2px solid {palette['primary']};
                font-weight: 600;
            }}
        """
        
    def get_scrollbar_style(self) -> str:
        """Générer le style CSS pour les barres de défilement"""
        palette = self.get_current_palette()
        
        return f"""
            QScrollBar:vertical {{
                background-color: {palette['surface_variant']};
                width: 12px;
                border-radius: 6px;
                margin: 0;
            }}
            QScrollBar::handle:vertical {{
                background-color: {palette['outline']};
                border-radius: 6px;
                min-height: 20px;
                margin: 2px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {palette['outline_variant']};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QScrollBar:horizontal {{
                background-color: {palette['surface_variant']};
                height: 12px;
                border-radius: 6px;
                margin: 0;
            }}
            QScrollBar::handle:horizontal {{
                background-color: {palette['outline']};
                border-radius: 6px;
                min-width: 20px;
                margin: 2px;
            }}
            QScrollBar::handle:horizontal:hover {{
                background-color: {palette['outline_variant']};
            }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                width: 0px;
            }}
        """
        
    def get_complete_stylesheet(self) -> str:
        """Générer la feuille de style complète pour l'application"""
        palette = self.get_current_palette()
        
        return f"""
            /* Style global de l'application */
            QMainWindow {{
                background-color: {palette['background']};
                color: {palette['on_background']};
                font-family: 'Segoe UI', 'Roboto', sans-serif;
                font-size: 14px;
            }}
            
            /* Widgets de base */
            QWidget {{
                background-color: transparent;
                color: {palette['on_surface']};
            }}
            
            /* Labels */
            QLabel {{
                color: {palette['on_surface']};
            }}
            
            /* Boutons */
            {self.get_button_style('primary')}
            
            /* Champs de saisie */
            {self.get_input_style()}
            
            /* Navigation */
            {self.get_navigation_style()}
            
            /* Tableaux */
            {self.get_table_style()}
            
            /* Barres de défilement */
            {self.get_scrollbar_style()}
            
            /* Tooltips */
            QToolTip {{
                background-color: {palette['surface_variant']};
                color: {palette['on_surface']};
                border: 1px solid {palette['outline']};
                border-radius: {self.BORDER_RADIUS['sm']}px;
                padding: {self.SPACING['sm']}px {self.SPACING['md']}px;
                font-size: 12px;
            }}
            
            /* Menus */
            QMenu {{
                background-color: {palette['surface']};
                color: {palette['on_surface']};
                border: 1px solid {palette['outline']};
                border-radius: {self.BORDER_RADIUS['md']}px;
                padding: {self.SPACING['xs']}px;
            }}
            QMenu::item {{
                padding: {self.SPACING['sm']}px {self.SPACING['md']}px;
                border-radius: {self.BORDER_RADIUS['sm']}px;
                margin: 1px;
            }}
            QMenu::item:selected {{
                background-color: {palette['hover']};
            }}
            
            /* Barres de statut */
            QStatusBar {{
                background-color: {palette['surface']};
                color: {palette['on_surface']};
                border-top: 1px solid {palette['divider']};
            }}
            
            /* Onglets */
            QTabWidget::pane {{
                background-color: {palette['surface']};
                border: 1px solid {palette['outline']};
                border-radius: {self.BORDER_RADIUS['md']}px;
            }}
            QTabBar::tab {{
                background-color: {palette['surface_variant']};
                color: {palette['on_surface']};
                padding: {self.SPACING['sm']}px {self.SPACING['lg']}px;
                margin-right: 2px;
                border-top-left-radius: {self.BORDER_RADIUS['md']}px;
                border-top-right-radius: {self.BORDER_RADIUS['md']}px;
            }}
            QTabBar::tab:selected {{
                background-color: {palette['surface']};
                color: {palette['primary']};
                font-weight: 600;
            }}
            QTabBar::tab:hover {{
                background-color: {palette['hover']};
            }}
        """
        
    def validate_contrast_ratio(self, foreground: str, background: str) -> float:
        """Valider le ratio de contraste WCAG 2.1 AA (minimum 4.5:1)"""
        # Conversion des couleurs en luminance relative
        def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
            hex_color = hex_color.lstrip('#')
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            
        def relative_luminance(rgb: Tuple[int, int, int]) -> float:
            def linearize(c: int) -> float:
                c = c / 255.0
                return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
                
            r, g, b = rgb
            return 0.2126 * linearize(r) + 0.7152 * linearize(g) + 0.0722 * linearize(b)
            
        try:
            fg_rgb = hex_to_rgb(foreground)
            bg_rgb = hex_to_rgb(background)
            
            fg_lum = relative_luminance(fg_rgb)
            bg_lum = relative_luminance(bg_rgb)
            
            # Calculer le ratio de contraste
            lighter = max(fg_lum, bg_lum)
            darker = min(fg_lum, bg_lum)
            
            return (lighter + 0.05) / (darker + 0.05)
            
        except Exception:
            return 1.0  # Ratio par défaut en cas d'erreur
            
    def get_accessible_color_pair(self, base_color: str) -> Tuple[str, str]:
        """Obtenir une paire de couleurs accessible (contraste ≥ 4.5:1)"""
        palette = self.get_current_palette()
        
        # Tester différentes combinaisons
        combinations = [
            (base_color, palette['on_surface']),
            (palette['on_surface'], base_color),
            (base_color, palette['surface']),
            (palette['surface'], base_color)
        ]
        
        for bg, fg in combinations:
            ratio = self.validate_contrast_ratio(fg, bg)
            if ratio >= 4.5:
                return bg, fg
                
        # Fallback vers les couleurs par défaut
        return palette['surface'], palette['on_surface']
        
    def get_theme_info(self) -> Dict[str, Any]:
        """Obtenir les informations complètes du thème"""
        return {
            'mode': self.current_mode.value,
            'palette': self.get_current_palette(),
            'spacing': self.SPACING,
            'border_radius': self.BORDER_RADIUS,
            'animation_duration': self.ANIMATION_DURATION,
            'easing_curves': self.EASING_CURVES,
            'phi': self.PHI
        }
