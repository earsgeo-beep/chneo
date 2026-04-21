# -*- coding: utf-8 -*-
"""
MaritimeButton - Boutons standardisés maritimes
Design System Maritime 2025 - CHNeoWave

Boutons avec :
- Variantes Primary/Secondary
- États interactifs
- Animations fluides
- Icônes optionnelles
- Accessibilité
"""

import sys
from typing import Optional

try:
    from PySide6.QtWidgets import QPushButton, QHBoxLayout, QLabel, QWidget, QSizePolicy
    from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, Signal, QSize, QTimer
    from PySide6.QtGui import QIcon, QFont, QPainter, QColor, QPen, QBrush
    pyqtSignal = Signal
except ImportError:
    try:
        from PyQt6.QtWidgets import QPushButton, QHBoxLayout, QLabel, QWidget, QSizePolicy
        from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtSignal, QSize, QTimer
        from PyQt6.QtGui import QIcon, QFont, QPainter, QColor, QPen, QBrush
    except ImportError:
        from PyQt5.QtWidgets import QPushButton, QHBoxLayout, QLabel, QWidget, QSizePolicy
        from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtSignal, QSize, QTimer
        from PyQt5.QtGui import QIcon, QFont, QPainter, QColor, QPen, QBrush

# Import du système d'animations Phase 6
try:
    from ...animations.micro_interactions import MaritimeMicroInteractions, InteractionState
    from ...animations.animation_system import MaritimeAnimator, AnimationType
except ImportError:
    # Fallback si le système d'animations n'est pas disponible
    MaritimeMicroInteractions = None
    InteractionState = None
    MaritimeAnimator = None
    AnimationType = None


class MaritimeButton(QPushButton):
    """
    Bouton de base du design system maritime.
    
    Caractéristiques :
    - Animations fluides
    - États interactifs
    - Icônes optionnelles
    - Tailles configurables
    - Accessibilité WCAG 2.1
    """
    
    # Signaux étendus
    long_pressed = pyqtSignal()  # Appui long
    hover_entered = pyqtSignal()  # Survol entré
    hover_left = pyqtSignal()    # Survol quitté
    
    # Tailles disponibles
    SIZE_SMALL = "small"    # 32px height
    SIZE_MEDIUM = "medium"  # 40px height
    SIZE_LARGE = "large"    # 48px height
    
    # Variantes
    VARIANT_PRIMARY = "primary"
    VARIANT_SECONDARY = "secondary"
    VARIANT_OUTLINE = "outline"
    VARIANT_GHOST = "ghost"
    VARIANT_DANGER = "danger"
    
    # Constantes Design System
    FIBONACCI_SPACES = [8, 13, 21, 34, 55, 89, 144]
    GOLDEN_RATIO = 1.618
    
    # Couleurs Maritime
    MARITIME_COLORS = {
        'ocean_deep': '#0A1929',
        'harbor_blue': '#1565C0',
        'steel_blue': '#1976D2',
        'tidal_cyan': '#00BCD4',
        'foam_white': '#FAFBFC',
        'frost_light': '#F5F7FA',
        'storm_gray': '#37474F',
        'slate_gray': '#546E7A',
        'coral_alert': '#FF5722',
        'emerald_success': '#4CAF50',
        'amber_warning': '#FF8F00'
    }
    
    def __init__(self, text: str = "",
                 parent: Optional[QWidget] = None,
                 icon: Optional[QIcon] = None,
                 variant: str = VARIANT_PRIMARY,
                 size: str = SIZE_MEDIUM,
                 full_width: bool = False):
        # Compatibilite avec l'ancienne signature (parent, text, ...).
        if isinstance(text, QWidget):
            legacy_parent = text
            legacy_text = parent if isinstance(parent, str) else ""
            text = legacy_text
            parent = legacy_parent

        super().__init__(text, parent)
        
        self.variant = variant
        self.size = size
        self.full_width = full_width
        self.icon = icon
        
        # État d'animation
        self._hover_progress = 0.0
        self._press_progress = 0.0
        self._is_loading = False
        
        # Système d'animations Phase 6
        if MaritimeMicroInteractions:
            self.micro_interactions = MaritimeMicroInteractions(self)
            self.animator = MaritimeAnimator(self)
        else:
            self.micro_interactions = None
            self.animator = None
        
        # Configuration de base
        self._setup_button()
        self._setup_animations()
        
        # Application du style
        self._apply_maritime_style()
        
        # Configuration des micro-interactions
        if self.micro_interactions:
            self._setup_micro_interactions()
    
    def _setup_button(self):
        """Configure le bouton de base."""
        # Taille selon la configuration
        heights = {
            self.SIZE_SMALL: 32,
            self.SIZE_MEDIUM: 40,
            self.SIZE_LARGE: 48
        }
        
        height = heights.get(self.size, 40)
        min_width = int(height * self.GOLDEN_RATIO)
        
        if self.full_width:
            self_policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

            self.setSizePolicy(self_policy)
        else:
            self.setMinimumWidth(min_width)
            self_policy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)

            self.setSizePolicy(self_policy)
        
        self.setMinimumHeight(height)
        
        # Configuration de l'icône
        if self.icon:
            icon_size = height - self.FIBONACCI_SPACES[1]  # 13px de marge
            self.setIcon(self.icon)
            self.setIconSize(QSize(icon_size, icon_size))
        
        # Curseur
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Focus
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
    
    def _setup_animations(self):
        """Configure les animations du bouton."""
        # Animation de survol
        self.hover_animation = QPropertyAnimation(self, b"hover_progress")
        self.hover_animation.setDuration(200)
        self.hover_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # Animation de pression
        self.press_animation = QPropertyAnimation(self, b"press_progress")
        self.press_animation.setDuration(100)
        self.press_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
    
    def _setup_micro_interactions(self):
        """Configure les micro-interactions Phase 6."""
        if not self.micro_interactions:
            return
            
        # Configuration des interactions pour boutons
        config = {
            'hover_scale': 1.02,
            'press_scale': 0.98,
            'transition_duration': 150,
            'success_duration': 1200,
            'error_shake_intensity': 3
        }
        
        self.micro_interactions.configure_button_interactions(config)
    
    def enterEvent(self, event):
        """Gestion de l'entrée de la souris."""
        super().enterEvent(event)
        self.hover_entered.emit()
        
        if self.micro_interactions:
            self.micro_interactions.trigger_hover_enter()
    
    def leaveEvent(self, event):
        """Gestion de la sortie de la souris."""
        super().leaveEvent(event)
        self.hover_left.emit()
        
        if self.micro_interactions:
            self.micro_interactions.trigger_hover_leave()
    
    def mousePressEvent(self, event):
        """Gestion du clic de souris."""
        super().mousePressEvent(event)
        
        if self.micro_interactions:
            self.micro_interactions.trigger_press()
    
    def mouseReleaseEvent(self, event):
        """Gestion du relâchement de souris."""
        super().mouseReleaseEvent(event)
        
        if self.micro_interactions:
            self.micro_interactions.trigger_release()
    
    def set_loading(self, loading: bool = True):
        """Active/désactive l'état de chargement."""
        self._is_loading = loading
        self.setEnabled(not loading)
        
        if self.micro_interactions:
            if loading:
                self.micro_interactions.trigger_loading_start()
            else:
                self.micro_interactions.trigger_loading_stop()
    
    def trigger_success_feedback(self):
        """Déclenche un feedback de succès."""
        if self.micro_interactions:
            self.micro_interactions.trigger_success_feedback()
    
    def trigger_error_feedback(self):
        """Déclenche un feedback d'erreur."""
        if self.micro_interactions:
            self.micro_interactions.trigger_error_feedback()
    
    def _apply_maritime_style(self):
        """Applique le style maritime selon la variante."""
        # Styles de base
        base_style = f"""
        MaritimeButton {{
            border: none;
            border-radius: {self.FIBONACCI_SPACES[0]}px;
            font-family: 'Segoe UI', 'Roboto', sans-serif;
            font-weight: 600;
            /* text-transform not supported in Qt */

            padding: 0 {self.FIBONACCI_SPACES[2]}px;
        }}
        
        MaritimeButton:focus {{
            outline: 2px solid {self.MARITIME_COLORS['tidal_cyan']};
            /* outline-offset not supported in Qt */
        }}
        
        MaritimeButton:disabled {{

            cursor: not-allowed;
        }}
        """
        
        # Styles spécifiques par variante
        variant_styles = {
            self.VARIANT_PRIMARY: f"""
            MaritimeButton {{
                background-color: {self.MARITIME_COLORS['harbor_blue']};
                color: {self.MARITIME_COLORS['foam_white']};
                font-size: 13px;
            }}
            
            MaritimeButton:hover {{
                background-color: {self.MARITIME_COLORS['steel_blue']};
                /* transform non supporté par Qt - effet géré par padding */
                padding: 11px 20px;
            }}
            
            MaritimeButton:pressed {{
                background-color: {self.MARITIME_COLORS['ocean_deep']};
                /* transform non supporté par Qt - effet géré par padding */
                padding: 13px 22px;
            }}
            """,
            
            self.VARIANT_SECONDARY: f"""
            MaritimeButton {{
                background-color: {self.MARITIME_COLORS['frost_light']};
                color: {self.MARITIME_COLORS['storm_gray']};
                border: 1px solid {self.MARITIME_COLORS['slate_gray']};
                font-size: 13px;
            }}
            
            MaritimeButton:hover {{
                background-color: {self.MARITIME_COLORS['foam_white']};
                border-color: {self.MARITIME_COLORS['harbor_blue']};
                color: {self.MARITIME_COLORS['harbor_blue']};
                /* transform non supporté par Qt - effet géré par padding */
                padding: 11px 20px;
            }}
            
            MaritimeButton:pressed {{
                background-color: {self.MARITIME_COLORS['frost_light']};
                /* transform non supporté par Qt - effet géré par padding */
                padding: 13px 22px;
            }}
            """,
            
            self.VARIANT_OUTLINE: f"""
            MaritimeButton {{
                background-color: transparent;
                color: {self.MARITIME_COLORS['harbor_blue']};
                border: 2px solid {self.MARITIME_COLORS['harbor_blue']};
                font-size: 13px;
            }}
            
            MaritimeButton:hover {{
                background-color: {self.MARITIME_COLORS['harbor_blue']};
                color: {self.MARITIME_COLORS['foam_white']};
                /* transform non supporté par Qt - effet géré par padding */
                padding: 11px 20px;
            }}
            
            MaritimeButton:pressed {{
                background-color: {self.MARITIME_COLORS['ocean_deep']};
                border-color: {self.MARITIME_COLORS['ocean_deep']};
                /* transform non supporté par Qt - effet géré par padding */
                padding: 13px 22px;
            }}
            """,
            
            self.VARIANT_GHOST: f"""
            MaritimeButton {{
                background-color: transparent;
                color: {self.MARITIME_COLORS['harbor_blue']};
                border: none;
                font-size: 13px;
            }}
            
            MaritimeButton:hover {{
                background-color: rgba(21, 101, 192, 0.1);
                /* transform non supporté par Qt - effet géré par padding */
                padding: 11px 20px;
            }}
            
            MaritimeButton:pressed {{
                background-color: rgba(21, 101, 192, 0.2);
                /* transform non supporté par Qt - effet géré par padding */
                padding: 13px 22px;
            }}
            """,
            
            self.VARIANT_DANGER: f"""
            MaritimeButton {{
                background-color: {self.MARITIME_COLORS['coral_alert']};
                color: {self.MARITIME_COLORS['foam_white']};
                font-size: 13px;
            }}
            
            MaritimeButton:hover {{
                background-color: #E64A19;
                /* transform non supporté par Qt - effet géré par padding */
                padding: 11px 20px;
            }}
            
            MaritimeButton:pressed {{
                background-color: #D84315;
                /* transform non supporté par Qt - effet géré par padding */
                padding: 13px 22px;
            }}
            """
        }
        
        # Application du style complet
        full_style = base_style + variant_styles.get(self.variant, variant_styles[self.VARIANT_PRIMARY])
        self.setStyleSheet(full_style)
    
    def enterEvent(self, event):
        """Événement d'entrée de survol."""
        super().enterEvent(event)
        self.hover_animation.setStartValue(self._hover_progress)
        self.hover_animation.setEndValue(1.0)
        self.hover_animation.start()
        self.hover_entered.emit()
    
    def leaveEvent(self, event):
        """Événement de sortie de survol."""
        super().leaveEvent(event)
        self.hover_animation.setStartValue(self._hover_progress)
        self.hover_animation.setEndValue(0.0)
        self.hover_animation.start()
        self.hover_left.emit()
    
    def mousePressEvent(self, event):
        """Événement de pression."""
        super().mousePressEvent(event)
        if event.button() == Qt.MouseButton.LeftButton:
            self.press_animation.setStartValue(self._press_progress)
            self.press_animation.setEndValue(1.0)
            self.press_animation.start()
    
    def mouseReleaseEvent(self, event):
        """Événement de relâchement."""
        super().mouseReleaseEvent(event)
        if event.button() == Qt.MouseButton.LeftButton:
            self.press_animation.setStartValue(self._press_progress)
            self.press_animation.setEndValue(0.0)
            self.press_animation.start()
    
    def set_variant(self, variant: str):
        """Change la variante du bouton."""
        if variant in [self.VARIANT_PRIMARY, self.VARIANT_SECONDARY, 
                      self.VARIANT_OUTLINE, self.VARIANT_GHOST, self.VARIANT_DANGER]:
            self.variant = variant
            self._apply_maritime_style()
    
    def set_size(self, size: str):
        """Change la taille du bouton."""
        if size in [self.SIZE_SMALL, self.SIZE_MEDIUM, self.SIZE_LARGE]:
            self.size = size
            self._setup_button()
    
    def set_icon(self, icon: Optional[QIcon]):
        """Définit l'icône du bouton."""
        self.icon = icon
        if icon:
            icon_size = self.height() - self.FIBONACCI_SPACES[1]
            self.setIcon(icon)
            self.setIconSize(QSize(icon_size, icon_size))
        else:
            self.setIcon(QIcon())
    
    def set_loading(self, loading: bool):
        """Active/désactive l'état de chargement."""
        self.setEnabled(not loading)
        if loading:
            self.setText("Chargement...")
            # TODO: Ajouter une animation de spinner
        # Note: Le texte original devrait être restauré quand loading=False
    
    # Propriétés pour les animations
    def get_hover_progress(self):
        return self._hover_progress
    
    def set_hover_progress(self, progress):
        self._hover_progress = progress
        self.update()
    
    hover_progress = property(get_hover_progress, set_hover_progress)
    
    def get_press_progress(self):
        return self._press_progress
    
    def set_press_progress(self, progress):
        self._press_progress = progress
        self.update()
    
    press_progress = property(get_press_progress, set_press_progress)


class PrimaryButton(MaritimeButton):
    """
    Bouton principal du design system maritime.
    
    Utilisation :
    - Actions principales
    - Validation de formulaires
    - Démarrage de processus
    """
    
    def __init__(self, parent: Optional[QWidget] = None,
                 text: str = "",
                 icon: Optional[QIcon] = None,
                 size: str = MaritimeButton.SIZE_MEDIUM,
                 full_width: bool = False):
        super().__init__(
            parent=parent,
            text=text,
            icon=icon,
            variant=MaritimeButton.VARIANT_PRIMARY,
            size=size,
            full_width=full_width
        )


class SecondaryButton(MaritimeButton):
    """
    Bouton secondaire du design system maritime.
    
    Utilisation :
    - Actions secondaires
    - Annulation
    - Navigation
    """
    
    def __init__(self, parent: Optional[QWidget] = None,
                 text: str = "",
                 icon: Optional[QIcon] = None,
                 size: str = MaritimeButton.SIZE_MEDIUM,
                 full_width: bool = False):
        super().__init__(
            parent=parent,
            text=text,
            icon=icon,
            variant=MaritimeButton.VARIANT_SECONDARY,
            size=size,
            full_width=full_width
        )


class OutlineButton(MaritimeButton):
    """
    Bouton avec contour du design system maritime.
    
    Utilisation :
    - Actions alternatives
    - Boutons de filtre
    - Sélections multiples
    """
    
    def __init__(self, parent: Optional[QWidget] = None,
                 text: str = "",
                 icon: Optional[QIcon] = None,
                 size: str = MaritimeButton.SIZE_MEDIUM,
                 full_width: bool = False):
        super().__init__(
            parent=parent,
            text=text,
            icon=icon,
            variant=MaritimeButton.VARIANT_OUTLINE,
            size=size,
            full_width=full_width
        )


class GhostButton(MaritimeButton):
    """
    Bouton fantôme du design system maritime.
    
    Utilisation :
    - Actions discrètes
    - Liens d'action
    - Boutons dans les barres d'outils
    """
    
    def __init__(self, parent: Optional[QWidget] = None,
                 text: str = "",
                 icon: Optional[QIcon] = None,
                 size: str = MaritimeButton.SIZE_MEDIUM,
                 full_width: bool = False):
        super().__init__(
            parent=parent,
            text=text,
            icon=icon,
            variant=MaritimeButton.VARIANT_GHOST,
            size=size,
            full_width=full_width
        )


class DangerButton(MaritimeButton):
    """
    Bouton de danger du design system maritime.
    
    Utilisation :
    - Actions destructives
    - Suppression
    - Arrêt d'urgence
    """
    
    def __init__(self, parent: Optional[QWidget] = None,
                 text: str = "",
                 icon: Optional[QIcon] = None,
                 size: str = MaritimeButton.SIZE_MEDIUM,
                 full_width: bool = False):
        super().__init__(
            parent=parent,
            text=text,
            icon=icon,
            variant=MaritimeButton.VARIANT_DANGER,
            size=size,
            full_width=full_width
        )
