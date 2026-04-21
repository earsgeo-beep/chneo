# -*- coding: utf-8 -*-
"""
Thème maritime pour CHNeoWave
Définit les couleurs, polices et styles du thème maritime

Auteur: Architecte Logiciel en Chef (ALC)
Date: 2025-01-26
Version: 1.1.0
"""

from PySide6.QtGui import QColor, QPalette, QFont
from PySide6.QtCore import QObject, Signal
from typing import Dict, Any
import math


class MaritimeTheme(QObject):
    """
    Gestionnaire de thème maritime avec support du mode sombre/clair
    """
    
    # Signal émis lors du changement de thème
    themeChanged = Signal(bool)  # True pour sombre, False pour clair
    
    # Constante du nombre d'or
    PHI = (1 + math.sqrt(5)) / 2

    # Compatibilite avec les vues qui utilisent MaritimeTheme comme namespace.
    SPACE_XS = 8
    SPACE_SM = 13
    SPACE_MD = 21
    SPACE_LG = 34
    SPACE_XL = 55
    SPACE_XXL = 89

    OCEAN_DEEP = "#0A1929"
    HARBOR_BLUE = "#1565C0"
    STEEL_BLUE = "#1976D2"
    TIDAL_CYAN = "#00BCD4"
    FOAM_WHITE = "#FAFBFC"
    FROST_LIGHT = "#F5F7FA"
    STORM_GRAY = "#37474F"
    SLATE_GRAY = "#546E7A"
    CORAL_ALERT = "#FF5722"
    EMERALD_SUCCESS = "#4CAF50"
    AMBER_WARNING = "#FF9800"
    AZURE_INFO = "#2196F3"
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # État du thème (False = clair, True = sombre)
        self._is_dark = False
        
        # Définition des couleurs
        self._define_colors()
        
        # Définition des polices
        self._define_fonts()
        
        # Définition des espacements
        self._define_spacing()
    
    def _define_colors(self):
        """Définit les palettes de couleurs maritime"""
        
        # Palette claire (thème par défaut)
        self.light_colors = {
            # Couleurs primaires maritimes
            'primary': '#2c5aa0',           # Bleu océan profond
            'primary_light': '#4a7bc8',     # Bleu océan clair
            'primary_dark': '#1e3d72',      # Bleu marine
            'primary_variant': '#3d6bb3',   # Variante bleu
            
            # Couleurs secondaires
            'secondary': '#0891b2',         # Bleu turquoise
            'secondary_light': '#22d3ee',   # Cyan clair
            'secondary_dark': '#0e7490',    # Bleu-vert foncé
            
            # Couleurs d'accent
            'accent': '#f59e0b',            # Orange maritime
            'accent_light': '#fbbf24',      # Orange clair
            'accent_dark': '#d97706',       # Orange foncé
            
            # Couleurs de surface
            'surface': '#ffffff',           # Blanc pur
            'surface_variant': '#f8fafc',   # Gris très clair
            'surface_container': '#f1f5f9', # Gris clair
            'surface_dim': '#e2e8f0',       # Gris moyen
            
            # Couleurs de fond
            'background': '#ffffff',        # Fond principal
            'background_variant': '#f8fafc', # Fond alternatif
            
            # Couleurs de texte
            'on_primary': '#ffffff',        # Texte sur primaire
            'on_secondary': '#ffffff',      # Texte sur secondaire
            'on_surface': '#1e293b',        # Texte principal
            'on_surface_variant': '#475569', # Texte secondaire
            'on_background': '#1e293b',     # Texte sur fond
            
            # Couleurs d'état
            'success': '#10b981',           # Vert succès
            'warning': '#f59e0b',           # Orange avertissement
            'error': '#ef4444',             # Rouge erreur
            'info': '#3b82f6',              # Bleu information
            
            # Couleurs de bordure
            'border': '#e2e8f0',            # Bordure normale
            'border_variant': '#cbd5e1',    # Bordure accentuée
            'divider': '#f1f5f9',           # Séparateur
            
            # Couleurs d'ombre
            'shadow': 'rgba(0, 0, 0, 0.1)', # Ombre légère
            'shadow_strong': 'rgba(0, 0, 0, 0.2)', # Ombre forte
        }
        
        # Palette sombre
        self.dark_colors = {
            # Couleurs primaires maritimes (adaptées)
            'primary': '#4a7bc8',           # Bleu plus clair pour le sombre
            'primary_light': '#6b93db',     # Bleu très clair
            'primary_dark': '#2c5aa0',      # Bleu standard
            'primary_variant': '#5a84c7',   # Variante
            
            # Couleurs secondaires
            'secondary': '#22d3ee',         # Cyan vif
            'secondary_light': '#67e8f9',   # Cyan très clair
            'secondary_dark': '#0891b2',    # Bleu-vert
            
            # Couleurs d'accent
            'accent': '#fbbf24',            # Orange vif
            'accent_light': '#fcd34d',      # Orange très clair
            'accent_dark': '#f59e0b',       # Orange standard
            
            # Couleurs de surface
            'surface': '#1e293b',           # Gris foncé
            'surface_variant': '#334155',   # Gris moyen-foncé
            'surface_container': '#475569', # Gris moyen
            'surface_dim': '#0f172a',       # Gris très foncé
            
            # Couleurs de fond
            'background': '#0f172a',        # Fond très sombre
            'background_variant': '#1e293b', # Fond alternatif
            
            # Couleurs de texte
            'on_primary': '#ffffff',        # Texte sur primaire
            'on_secondary': '#0f172a',      # Texte sur secondaire
            'on_surface': '#f8fafc',        # Texte principal
            'on_surface_variant': '#cbd5e1', # Texte secondaire
            'on_background': '#f8fafc',     # Texte sur fond
            
            # Couleurs d'état
            'success': '#34d399',           # Vert succès clair
            'warning': '#fbbf24',           # Orange avertissement
            'error': '#f87171',             # Rouge erreur clair
            'info': '#60a5fa',              # Bleu information clair
            
            # Couleurs de bordure
            'border': '#475569',            # Bordure normale
            'border_variant': '#64748b',    # Bordure accentuée
            'divider': '#334155',           # Séparateur
            
            # Couleurs d'ombre
            'shadow': 'rgba(0, 0, 0, 0.3)', # Ombre légère
            'shadow_strong': 'rgba(0, 0, 0, 0.5)', # Ombre forte
        }
    
    def _define_fonts(self):
        """Définit les polices du thème"""
        
        # Polices principales
        self.fonts = {
            'primary': 'Segoe UI',          # Police principale
            'secondary': 'Roboto',          # Police secondaire
            'monospace': 'Consolas',        # Police monospace
            'display': 'Segoe UI Light',    # Police d'affichage
        }
        
        # Tailles de police basées sur le nombre d'or
        base_size = 14
        self.font_sizes = {
            'xs': int(base_size / (self.PHI * self.PHI)),    # ~5px
            'sm': int(base_size / self.PHI),                 # ~9px
            'base': base_size,                               # 14px
            'md': int(base_size * self.PHI / 2),            # ~11px
            'lg': int(base_size * self.PHI),                # ~23px
            'xl': int(base_size * self.PHI * self.PHI),     # ~37px
            'xxl': int(base_size * self.PHI * self.PHI * self.PHI), # ~60px
        }
        
        # Poids de police
        self.font_weights = {
            'light': 300,
            'normal': 400,
            'medium': 500,
            'semibold': 600,
            'bold': 700,
            'extrabold': 800,
        }
    
    def _define_spacing(self):
        """Définit les espacements basés sur le nombre d'or"""
        
        self.spacing = {
            'xs': self.SPACE_XS,
            'sm': self.SPACE_SM,
            'base': self.SPACE_XS,
            'md': self.SPACE_MD,
            'lg': self.SPACE_LG,
            'xl': self.SPACE_XL,
            'xxl': self.SPACE_XXL,
        }
        
        # Rayons de bordure
        self.border_radius = {
            'none': 0,
            'sm': 4,
            'base': 8,
            'md': 12,
            'lg': 16,
            'xl': 24,
            'full': 9999,
        }
        
        # Épaisseurs de bordure
        self.border_width = {
            'none': 0,
            'thin': 1,
            'base': 2,
            'thick': 4,
        }
    
    @property
    def is_dark(self) -> bool:
        """Retourne True si le thème sombre est actif"""
        return self._is_dark
    
    @property
    def colors(self) -> Dict[str, str]:
        """Retourne la palette de couleurs actuelle"""
        return self.dark_colors if self._is_dark else self.light_colors
    
    def set_dark_theme(self, dark: bool = True):
        """Active/désactive le thème sombre"""
        if self._is_dark != dark:
            self._is_dark = dark
            self.themeChanged.emit(dark)
    
    def toggle_theme(self):
        """Bascule entre les thèmes"""
        self.set_dark_theme(not self._is_dark)
    
    def get_color(self, color_name: str, alpha: float = 1.0) -> str:
        """Récupère une couleur avec transparence optionnelle"""
        color = self.colors.get(color_name, '#000000')
        
        if alpha < 1.0 and not color.startswith('rgba'):
            # Convertir en RGBA
            if color.startswith('#'):
                hex_color = color[1:]
                if len(hex_color) == 6:
                    r = int(hex_color[0:2], 16)
                    g = int(hex_color[2:4], 16)
                    b = int(hex_color[4:6], 16)
                    return f'rgba({r}, {g}, {b}, {alpha})'
        
        return color
    
    def get_font(self, size_key: str = 'base', weight_key: str = 'normal', 
                 family_key: str = 'primary') -> QFont:
        """Crée un objet QFont avec les paramètres spécifiés"""
        font = QFont()
        font.setFamily(self.fonts.get(family_key, 'Segoe UI'))
        font.setPointSize(self.font_sizes.get(size_key, 14))
        font.setWeight(self.font_weights.get(weight_key, 400))
        return font
    
    def get_spacing(self, size_key: str = 'base') -> int:
        """Récupère un espacement"""
        return self.spacing.get(size_key, 8)
    
    def get_border_radius(self, size_key: str = 'base') -> int:
        """Récupère un rayon de bordure"""
        return self.border_radius.get(size_key, 8)
    
    def get_border_width(self, size_key: str = 'base') -> int:
        """Récupère une épaisseur de bordure"""
        return self.border_width.get(size_key, 2)
    
    def create_stylesheet(self, component_type: str = 'general') -> str:
        """Crée une feuille de style pour un type de composant"""
        
        if component_type == 'general':
            return self._create_general_stylesheet()
        elif component_type == 'button':
            return self._create_button_stylesheet()
        elif component_type == 'card':
            return self._create_card_stylesheet()
        elif component_type == 'input':
            return self._create_input_stylesheet()
        else:
            return self._create_general_stylesheet()
    
    def _create_general_stylesheet(self) -> str:
        """Crée la feuille de style générale"""
        colors = self.colors
        
        return f"""
            QWidget {{
                background-color: {colors['background']};
                color: {colors['on_background']};
                font-family: {self.fonts['primary']};
                font-size: {self.font_sizes['base']}px;
            }}
            
            QMainWindow {{
                background-color: {colors['background']};
            }}
            
            QFrame {{
                background-color: {colors['surface']};
                border: {self.border_width['thin']}px solid {colors['border']};
                border-radius: {self.border_radius['base']}px;
            }}
        """
    
    def _create_button_stylesheet(self) -> str:
        """Crée la feuille de style pour les boutons"""
        colors = self.colors
        
        return f"""
            QPushButton {{
                background-color: {colors['primary']};
                color: {colors['on_primary']};
                border: none;
                border-radius: {self.border_radius['base']}px;
                padding: {self.spacing['md']}px {self.spacing['lg']}px;
                font-weight: {self.font_weights['medium']};
                font-size: {self.font_sizes['base']}px;
            }}
            
            QPushButton:hover {{
                background-color: {colors['primary_light']};
            }}
            
            QPushButton:pressed {{
                background-color: {colors['primary_dark']};
            }}
            
            QPushButton:disabled {{
                background-color: {colors['surface_dim']};
                color: {colors['on_surface_variant']};
            }}
        """
    
    def _create_card_stylesheet(self) -> str:
        """Crée la feuille de style pour les cartes"""
        colors = self.colors
        
        return f"""
            .card {{
                background-color: {colors['surface']};
                border: {self.border_width['thin']}px solid {colors['border']};
                border-radius: {self.border_radius['lg']}px;
                padding: {self.spacing['lg']}px;
            }}
            
            .card:hover {
                border-color: {colors['border_variant']};
            }
        """
    
    def _create_input_stylesheet(self) -> str:
        """Crée la feuille de style pour les champs de saisie"""
        colors = self.colors
        
        return f"""
            QLineEdit, QTextEdit, QComboBox {{
                background-color: {colors['surface']};
                color: {colors['on_surface']};
                border: {self.border_width['base']}px solid {colors['border']};
                border-radius: {self.border_radius['base']}px;
                padding: {self.spacing['sm']}px {self.spacing['md']}px;
                font-size: {self.font_sizes['base']}px;
            }}
            
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus {{
                border-color: {colors['primary']};
                outline: none;
            }}
            
            QLineEdit:disabled, QTextEdit:disabled, QComboBox:disabled {{
                background-color: {colors['surface_dim']};
                color: {colors['on_surface_variant']};
                border-color: {colors['border']};
            }}
        """
    
    def apply_to_widget(self, widget, component_type: str = 'general'):
        """Applique le thème à un widget"""
        stylesheet = self.create_stylesheet(component_type)
        widget.setStyleSheet(stylesheet)
    
    def create_palette(self) -> QPalette:
        """Crée une palette Qt avec les couleurs du thème"""
        palette = QPalette()
        colors = self.colors
        
        # Couleurs de base
        palette.setColor(QPalette.Window, QColor(colors['background']))
        palette.setColor(QPalette.WindowText, QColor(colors['on_background']))
        palette.setColor(QPalette.Base, QColor(colors['surface']))
        palette.setColor(QPalette.AlternateBase, QColor(colors['surface_variant']))
        palette.setColor(QPalette.Text, QColor(colors['on_surface']))
        palette.setColor(QPalette.Button, QColor(colors['primary']))
        palette.setColor(QPalette.ButtonText, QColor(colors['on_primary']))
        palette.setColor(QPalette.Highlight, QColor(colors['primary_light']))
        palette.setColor(QPalette.HighlightedText, QColor(colors['on_primary']))
        
        return palette


# Instance globale du thème
_maritime_theme_instance = None

def get_maritime_theme() -> MaritimeTheme:
    """Récupère l'instance globale du thème maritime"""
    global _maritime_theme_instance
    if _maritime_theme_instance is None:
        _maritime_theme_instance = MaritimeTheme()
    return _maritime_theme_instance


def apply_maritime_theme_to_app(app):
    """Applique le thème maritime à l'application"""
    theme = get_maritime_theme()
    palette = theme.create_palette()
    app.setPalette(palette)
    
    # Style global
    global_style = theme.create_stylesheet('general')
    app.setStyleSheet(global_style)
