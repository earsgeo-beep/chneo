# -*- coding: utf-8 -*-
"""
MaritimeCard - Composant Card avec élévation
Design System Maritime 2025 - CHNeoWave

Card standardisée avec :
- Élévation et ombres
- Animations hover fluides
- Proportions Golden Ratio
- Conformité accessibilité
"""

import sys
from typing import Optional, Union

try:
    from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
    from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, Signal, QRect, QSize
    from PySide6.QtGui import QPainter, QPainterPath, QColor, QPen
    pyqtSignal = Signal
except ImportError:
    try:
        from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
        from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtSignal, QRect, QSize
        from PyQt6.QtGui import QPainter, QPainterPath, QColor, QPen
    except ImportError:
        from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
        from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtSignal, QRect, QSize
        from PyQt5.QtGui import QPainter, QPainterPath, QColor, QPen

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


class MaritimeCard(QFrame):
    """
    Card maritime avec élévation et animations.
    
    Caractéristiques :
    - Élévation avec ombres
    - Animation hover fluide
    - Proportions Golden Ratio
    - Styles personnalisables
    """
    
    # Signaux
    clicked = pyqtSignal()
    hovered = pyqtSignal(bool)  # True = enter, False = leave
    
    # Constantes Design System
    GOLDEN_RATIO = 1.618
    FIBONACCI_SPACES = [8, 13, 21, 34, 55, 89, 144]
    
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
        'emerald_success': '#4CAF50'
    }
    
    def __init__(self, title: str = "",
                 parent: Optional[QWidget] = None,
                 elevated: bool = True,
                 clickable: bool = False):
        # Compatibilite avec l'ancienne signature (parent, title, ...).
        if isinstance(title, QWidget):
            legacy_parent = title
            legacy_title = parent if isinstance(parent, str) else ""
            title = legacy_title
            parent = legacy_parent

        super().__init__(parent)
        
        self.title = title
        self.elevated = elevated
        self.clickable = clickable
        self._is_hovered = False
        
        # Système d'animations Phase 6
        if MaritimeMicroInteractions:
            self.micro_interactions = MaritimeMicroInteractions(self)
            self.animator = MaritimeAnimator(self)
        else:
            self.micro_interactions = None
            self.animator = None
        
        # Configuration de base
        self.setFrameStyle(QFrame.Shape.NoFrame)
        self.setLineWidth(0)
        
        # Animations
        self._setup_animations()
        
        # Layout principal
        self._setup_layout()
        
        # Styles
        self._apply_maritime_style()
        
        # Configuration des micro-interactions
        if self.micro_interactions:
            self._setup_micro_interactions()
        
        # Événements
        if self.clickable:
            self.setCursor(Qt.CursorShape.PointingHandCursor)
    
    def _setup_animations(self):
        """Configure les animations de la card."""
        # Animation d'élévation
        self.elevation_animation = QPropertyAnimation(self, b"geometry")
        self.elevation_animation.setDuration(150)
        self.elevation_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # Animation d'opacité
        self.opacity_animation = QPropertyAnimation(self, b"windowOpacity")
        self.opacity_animation.setDuration(300)
        self.opacity_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
    
    def _setup_micro_interactions(self):
        """Configure les micro-interactions Phase 6."""
        if not self.micro_interactions:
            return
            
        # Configuration des interactions pour cartes
        config = {
            'hover_scale': 1.01,
            'press_scale': 0.99,
            'transition_duration': 200,
            'elevation_offset': 2
        }
        
        if hasattr(self.micro_interactions, 'configure_card_interactions'):
            self.micro_interactions.configure_card_interactions(config)
        else:
            # Fallback si la méthode n'existe pas
            pass
    
    def enterEvent(self, event):
        """Gestion de l'entrée de la souris."""
        super().enterEvent(event)
        self._is_hovered = True
        self.hovered.emit(True)
        
        if self.micro_interactions:
            self.micro_interactions.trigger_hover_enter()
    
    def leaveEvent(self, event):
        """Gestion de la sortie de la souris."""
        super().leaveEvent(event)
        self._is_hovered = False
        self.hovered.emit(False)
        
        if self.micro_interactions:
            self.micro_interactions.trigger_hover_leave()
    
    def mousePressEvent(self, event):
        """Gestion du clic de souris."""
        if self.clickable:
            super().mousePressEvent(event)
            
            if self.micro_interactions:
                self.micro_interactions.trigger_press()
    
    def mouseReleaseEvent(self, event):
        """Gestion du relâchement de souris."""
        if self.clickable:
            super().mouseReleaseEvent(event)
            self.clicked.emit()
            
            if self.micro_interactions:
                self.micro_interactions.trigger_release()
    
    def _setup_layout(self):
        """Configure le layout principal de la card."""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(
            self.FIBONACCI_SPACES[2],  # 21px
            self.FIBONACCI_SPACES[2],  # 21px
            self.FIBONACCI_SPACES[2],  # 21px
            self.FIBONACCI_SPACES[2]   # 21px
        )
        self.main_layout.setSpacing(self.FIBONACCI_SPACES[1])  # 13px
        
        # En-tête avec titre si fourni
        if self.title:
            self.title_label = QLabel(self.title)
            self.title_label.setObjectName("maritime_card_title")
            self.main_layout.addWidget(self.title_label)
        
        # Zone de contenu
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(self.FIBONACCI_SPACES[0])  # 8px
        
        self.main_layout.addWidget(self.content_widget)
    
    def _apply_maritime_style(self):
        """Applique le style maritime à la card."""
        elevation_class = "elevated" if self.elevated else "flat"
        clickable_class = "clickable" if self.clickable else ""
        
        style = f"""
        MaritimeCard {{
            background-color: {self.MARITIME_COLORS['foam_white']};
            border: 1px solid {self.MARITIME_COLORS['frost_light']};
            border-radius: {self.FIBONACCI_SPACES[0]}px;
            padding: 0px;
        }}
        
        MaritimeCard[class="{elevation_class}"] {{
            border: 2px solid rgba(10, 25, 41, 0.15);
        }}
        
        MaritimeCard[class="{clickable_class}"] {{
            /* cursor: pointer; géré par setCursor() */
        }}
        
        MaritimeCard:hover {{
            border-color: {self.MARITIME_COLORS['tidal_cyan']};
            border: 2px solid rgba(10, 25, 41, 0.2);
        }}
        
        QLabel#maritime_card_title {{
            font-size: 20px;
            font-weight: 600;
            color: {self.MARITIME_COLORS['storm_gray']};

        }}
        """
        
        self.setStyleSheet(style)
        
        # Propriétés pour le CSS
        if self.elevated:
            self.setProperty("class", "elevated")
        if self.clickable:
            self.setProperty("class", "clickable")
    
    def add_widget(self, widget: QWidget):
        """Ajoute un widget au contenu de la card."""
        self.content_layout.addWidget(widget)

    def add_content(self, widget: QWidget):
        """Alias de compatibilite pour les vues existantes."""
        self.add_widget(widget)
    
    def add_layout(self, layout):
        """Ajoute un layout au contenu de la card."""
        self.content_layout.addLayout(layout)

    def add_content_layout(self, layout):
        """Alias de compatibilite pour les vues existantes."""
        self.add_layout(layout)

    def set_content_widget(self, widget: QWidget):
        """Remplace la zone de contenu interne par un widget fourni."""
        if widget is self.content_widget:
            return

        self.main_layout.removeWidget(self.content_widget)
        self.content_widget.deleteLater()
        self.content_widget = widget
        self.content_layout = widget.layout()
        self.main_layout.addWidget(self.content_widget)
    
    def set_title(self, title: str):
        """Définit ou met à jour le titre de la card."""
        self.title = title
        if hasattr(self, 'title_label'):
            self.title_label.setText(title)
        else:
            self.title_label = QLabel(title)
            self.title_label.setObjectName("maritime_card_title")
            self.main_layout.insertWidget(0, self.title_label)
    
    def set_elevated(self, elevated: bool):
        """Active ou désactive l'élévation."""
        self.elevated = elevated
        self._apply_maritime_style()
    
    def set_clickable(self, clickable: bool):
        """Active ou désactive le mode cliquable."""
        self.clickable = clickable
        if clickable:
            self.setCursor(Qt.CursorShape.PointingHandCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)
        self._apply_maritime_style()
    
    def enterEvent(self, event):
        """Gestion de l'entrée de la souris."""
        super().enterEvent(event)
        self._is_hovered = True
        self.hovered.emit(True)
        
        if self.clickable or self.elevated:
            # Animation d'élévation
            current_geometry = self.geometry()
            target_geometry = QRect(
                current_geometry.x(),
                current_geometry.y() - 2,
                current_geometry.width(),
                current_geometry.height()
            )
            
            self.elevation_animation.setStartValue(current_geometry)
            self.elevation_animation.setEndValue(target_geometry)
            self.elevation_animation.start()
    
    def leaveEvent(self, event):
        """Gestion de la sortie de la souris."""
        super().leaveEvent(event)
        self._is_hovered = False
        self.hovered.emit(False)
        
        if self.clickable or self.elevated:
            # Animation de retour
            current_geometry = self.geometry()
            target_geometry = QRect(
                current_geometry.x(),
                current_geometry.y() + 2,
                current_geometry.width(),
                current_geometry.height()
            )
            
            self.elevation_animation.setStartValue(current_geometry)
            self.elevation_animation.setEndValue(target_geometry)
            self.elevation_animation.start()
    
    def mousePressEvent(self, event):
        """Gestion du clic."""
        super().mousePressEvent(event)
        if self.clickable and event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
    
    def paintEvent(self, event):
        """Rendu personnalisé avec ombres."""
        super().paintEvent(event)
        
        if not self.elevated:
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Ombre
        shadow_color = QColor(10, 25, 41, 38)  # rgba(10, 25, 41, 0.15)
        if self._is_hovered:
            shadow_color = QColor(10, 25, 41, 51)  # rgba(10, 25, 41, 0.2)
        
        # Chemin arrondi pour l'ombre
        shadow_rect = self.rect().adjusted(2, 4, -2, -2)
        shadow_path = QPainterPath()
        shadow_path.addRoundedRect(shadow_rect, self.FIBONACCI_SPACES[0], self.FIBONACCI_SPACES[0])
        
        painter.fillPath(shadow_path, shadow_color)
    
    def sizeHint(self):
        """Taille suggérée basée sur le Golden Ratio."""
        base_width = 323  # Basé sur Golden Ratio
        base_height = int(base_width / self.GOLDEN_RATIO)
        return super().sizeHint().expandedTo(QSize(base_width, base_height))
    
    def minimumSizeHint(self):
        """Taille minimale suggérée."""
        return super().minimumSizeHint()
    
    @property
    def is_hovered(self) -> bool:
        """Retourne True si la card est survolée."""
        return self._is_hovered
    
    def fade_in(self, duration: int = 300):
        """Animation de fondu d'entrée."""
        self.setWindowOpacity(0.0)
        self.show()
        
        self.opacity_animation.setDuration(duration)
        self.opacity_animation.setStartValue(0.0)
        self.opacity_animation.setEndValue(1.0)
        self.opacity_animation.start()
    
    def fade_out(self, duration: int = 300):
        """Animation de fondu de sortie."""
        self.opacity_animation.setDuration(duration)
        self.opacity_animation.setStartValue(1.0)
        self.opacity_animation.setEndValue(0.0)
        self.opacity_animation.finished.connect(self.hide)
        self.opacity_animation.start()
