"""Enhanced Toast Notification System for CHNeoWave

Système de notifications toast amélioré avec Material Design 3,
icônes expressives et animations fluides.
"""

import logging
from typing import Optional, Dict, Any
from enum import Enum

from PySide6.QtWidgets import (
    QWidget, QLabel, QHBoxLayout, QVBoxLayout, 
    QGraphicsOpacityEffect, QApplication, QFrame
)
from PySide6.QtCore import (
    Qt, QTimer, QPropertyAnimation, QEasingCurve, 
    QParallelAnimationGroup, QSequentialAnimationGroup,
    QRect, Signal, QObject
)
from PySide6.QtGui import QFont, QPainter, QPainterPath, QColor

from .material.theme import MaterialTheme, MaterialColor
from ..icons import svg_icon


class ToastLevel(Enum):
    """Niveaux de toast avec icônes Material Design"""
    SUCCESS = "success"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ToastIcon:
    """Icônes Material Design pour les toasts"""
    ICONS = {
        ToastLevel.SUCCESS: "check",
        ToastLevel.INFO: "info",
        ToastLevel.WARNING: "warning",
        ToastLevel.ERROR: "error",
        ToastLevel.CRITICAL: "error",
    }
    
    @classmethod
    def get_icon(cls, level: ToastLevel) -> str:
        return cls.ICONS.get(level, cls.ICONS[ToastLevel.INFO])


class EnhancedToast(QWidget):
    """Toast notification amélioré avec Material Design 3"""
    
    # Signal émis quand le toast se ferme
    closed = Signal()
    
    def __init__(self, 
                 message: str, 
                 level: ToastLevel = ToastLevel.INFO,
                 title: Optional[str] = None,
                 duration: int = 5000,
                 parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self.message = message
        self.level = level
        self.title = title
        self.duration = duration
        self.logger = logging.getLogger(__name__)
        
        # Configuration du widget
        self.setWindowFlags(
            Qt.FramelessWindowHint | 
            Qt.WindowStaysOnTopHint | 
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Taille dynamique basée sur le contenu
        self._calculate_size()
        
        # Interface utilisateur
        self._setup_ui()
        
        # Animations
        self._setup_animations()
        
        # Timer pour masquer automatiquement
        self.hide_timer = QTimer()
        self.hide_timer.setSingleShot(True)
        self.hide_timer.timeout.connect(self.hide_toast)
        
        # Connecter l'animation de sortie à la fermeture
        self.fade_out_group.finished.connect(self._on_animation_finished)
    
    def _calculate_size(self):
        """Calcule la taille optimale du toast"""
        base_width = 320
        base_height = 64
        
        # Ajuster selon le contenu
        if self.title:
            base_height += 20
        
        if len(self.message) > 50:
            base_width = min(400, base_width + len(self.message) * 2)
            base_height += 20
        
        self.setFixedSize(base_width, base_height)
    
    def _setup_ui(self):
        """Configure l'interface utilisateur du toast"""
        # Container principal avec Material Design
        self.container = QFrame(self)
        self.container.setObjectName("toastContainer")
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.container)
        
        # Layout du contenu
        content_layout = QHBoxLayout(self.container)
        content_layout.setContentsMargins(16, 12, 16, 12)
        content_layout.setSpacing(12)
        
        # Icône
        self.icon_label = QLabel()
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.setFixedSize(24, 24)
        
        # Contenu textuel
        text_layout = QVBoxLayout()
        text_layout.setSpacing(4)
        
        # Titre (optionnel)
        if self.title:
            self.title_label = QLabel(self.title)
            self.title_label.setObjectName("toastTitle")
            text_layout.addWidget(self.title_label)
        
        # Message
        self.message_label = QLabel(self.message)
        self.message_label.setObjectName("toastMessage")
        self.message_label.setWordWrap(True)
        text_layout.addWidget(self.message_label)
        
        # Assemblage
        content_layout.addWidget(self.icon_label)
        content_layout.addLayout(text_layout)
        content_layout.addStretch()
        
        # Application du style Material Design
        self._apply_material_style()
    
    def _apply_material_style(self):
        """Applique le style Material Design 3"""
        theme = MaterialTheme.get_current_theme()
        
        # Couleurs selon le niveau
        color_schemes = {
            ToastLevel.SUCCESS: {
                'bg': theme.tertiary,
                'text': theme.on_tertiary,
                'icon': theme.on_tertiary
            },
            ToastLevel.INFO: {
                'bg': theme.primary,
                'text': theme.on_primary,
                'icon': theme.on_primary
            },
            ToastLevel.WARNING: {
                'bg': '#FF9800',  # Material Orange
                'text': '#FFFFFF',
                'icon': '#FFFFFF'
            },
            ToastLevel.ERROR: {
                'bg': theme.error,
                'text': theme.on_error,
                'icon': theme.on_error
            },
            ToastLevel.CRITICAL: {
                'bg': '#9C27B0',  # Material Purple
                'text': '#FFFFFF',
                'icon': '#FFFFFF'
            }
        }
        
        colors = color_schemes.get(self.level, color_schemes[ToastLevel.INFO])
        self.icon_label.setPixmap(
            svg_icon(ToastIcon.get_icon(self.level), colors["icon"], 20).pixmap(20, 20)
        )
        
        # Style du container
        container_style = f"""
        QFrame#toastContainer {{
            background-color: {colors['bg']};
            border-radius: 16px;
            border: none;
        }}
        """
        
        # Style de l'icône
        icon_style = f"""
        QLabel {{
            color: {colors['icon']};
            font-size: 18px;
            font-weight: bold;
        }}
        """
        
        # Style du titre
        title_style = f"""
        QLabel#toastTitle {{
            color: {colors['text']};
            font-size: 16px;
            font-weight: bold;
            margin: 0px;
        }}
        """
        
        # Style du message
        message_style = f"""
        QLabel#toastMessage {{
            color: {colors['text']};
            font-size: 14px;
            font-weight: normal;
            margin: 0px;
            
        }}
        """
        
        # Application des styles
        self.container.setStyleSheet(container_style)
        self.icon_label.setStyleSheet(icon_style)
        
        if hasattr(self, 'title_label'):
            self.title_label.setStyleSheet(title_style)
        
        self.message_label.setStyleSheet(message_style)
    
    def _setup_animations(self):
        """Configure les animations fluides"""
        # Effet d'opacité
        self.opacity_effect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(self.opacity_effect)
        
        # Animation d'entrée (fade + slide)
        self.fade_in_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_in_animation.setDuration(400)
        self.fade_in_animation.setStartValue(0.0)
        self.fade_in_animation.setEndValue(1.0)
        self.fade_in_animation.setEasingCurve(QEasingCurve.OutCubic)
        
        # Animation de sortie (fade + slide)
        self.fade_out_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_out_animation.setDuration(300)
        self.fade_out_animation.setStartValue(1.0)
        self.fade_out_animation.setEndValue(0.0)
        self.fade_out_animation.setEasingCurve(QEasingCurve.InCubic)
        
        # Groupe d'animations d'entrée
        self.fade_in_group = QParallelAnimationGroup()
        self.fade_in_group.addAnimation(self.fade_in_animation)
        
        # Groupe d'animations de sortie
        self.fade_out_group = QParallelAnimationGroup()
        self.fade_out_group.addAnimation(self.fade_out_animation)
    
    def show_toast(self, position: Optional[tuple] = None):
        """Affiche le toast avec animation"""
        if position:
            self.move(*position)
        else:
            self._position_toast()
        
        self.show()
        self.fade_in_group.start()
        
        # Démarrer le timer de masquage
        if self.duration > 0:
            self.hide_timer.start(self.duration)
        
        self.logger.debug(f"Toast affiché: {self.level.value} - {self.message}")
    
    def hide_toast(self):
        """Masque le toast avec animation"""
        self.hide_timer.stop()
        self.fade_out_group.start()
        self.logger.debug(f"Toast masqué: {self.level.value} - {self.message}")
    
    def _position_toast(self):
        """Positionne le toast sur l'écran"""
        if not QApplication.instance():
            return
        
        screen = QApplication.primaryScreen()
        if not screen:
            return
        
        screen_rect = screen.availableGeometry()
        
        # Position en haut à droite avec marge
        x = screen_rect.width() - self.width() - 20
        y = 20
        
        self.move(x, y)
    
    def _on_animation_finished(self):
        """Appelé quand l'animation de sortie se termine"""
        self.closed.emit()
        self.close()
        self.deleteLater()
    
    def mousePressEvent(self, event):
        """Permet de fermer le toast en cliquant dessus"""
        if event.button() == Qt.LeftButton:
            self.hide_toast()
        super().mousePressEvent(event)


class ToastManager(QObject):
    """Gestionnaire de toasts pour éviter la surcharge"""
    
    def __init__(self, max_toasts: int = 3, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.max_toasts = max_toasts
        self.active_toasts = []
        self.logger = logging.getLogger(__name__)
    
    def show_toast(self, 
                   message: str,
                   level: ToastLevel = ToastLevel.INFO,
                   title: Optional[str] = None,
                   duration: int = 5000) -> EnhancedToast:
        """Affiche un nouveau toast"""
        # Limiter le nombre de toasts actifs
        while len(self.active_toasts) >= self.max_toasts:
            oldest_toast = self.active_toasts.pop(0)
            oldest_toast.hide_toast()
        
        # Créer le nouveau toast
        toast = EnhancedToast(message, level, title, duration)
        
        # Positionner en cascade
        self._position_toast_in_stack(toast)
        
        # Connecter le signal de fermeture
        toast.closed.connect(lambda: self._remove_toast(toast))
        
        # Ajouter à la liste et afficher
        self.active_toasts.append(toast)
        toast.show_toast()
        
        self.logger.info(f"Toast créé: {level.value} - {message}")
        return toast
    
    def _position_toast_in_stack(self, toast: EnhancedToast):
        """Positionne le toast dans la pile"""
        if not QApplication.instance():
            return
        
        screen = QApplication.primaryScreen()
        if not screen:
            return
        
        screen_rect = screen.availableGeometry()
        
        # Position de base
        x = screen_rect.width() - toast.width() - 20
        y = 20
        
        # Décaler selon le nombre de toasts actifs
        for i, active_toast in enumerate(self.active_toasts):
            y += active_toast.height() + 10
        
        toast.move(x, y)
    
    def _remove_toast(self, toast: EnhancedToast):
        """Supprime un toast de la liste active"""
        if toast in self.active_toasts:
            self.active_toasts.remove(toast)
            self._reposition_toasts()
    
    def _reposition_toasts(self):
        """Repositionne tous les toasts actifs"""
        if not QApplication.instance():
            return
        
        screen = QApplication.primaryScreen()
        if not screen:
            return
        
        screen_rect = screen.availableGeometry()
        
        x = screen_rect.width() - 20
        y = 20
        
        for toast in self.active_toasts:
            if toast and not toast.isHidden():
                x_pos = x - toast.width()
                toast.move(x_pos, y)
                y += toast.height() + 10
    
    def clear_all_toasts(self):
        """Ferme tous les toasts actifs"""
        for toast in self.active_toasts.copy():
            toast.hide_toast()
        self.active_toasts.clear()
        self.logger.info("Tous les toasts ont été fermés")
    
    # Méthodes de convenance
    def success(self, message: str, title: str = "Succès", duration: int = 3000):
        return self.show_toast(message, ToastLevel.SUCCESS, title, duration)
    
    def info(self, message: str, title: str = "Information", duration: int = 4000):
        return self.show_toast(message, ToastLevel.INFO, title, duration)
    
    def warning(self, message: str, title: str = "Attention", duration: int = 6000):
        return self.show_toast(message, ToastLevel.WARNING, title, duration)
    
    def error(self, message: str, title: str = "Erreur", duration: int = 8000):
        return self.show_toast(message, ToastLevel.ERROR, title, duration)
    
    def critical(self, message: str, title: str = "Critique", duration: int = 10000):
        return self.show_toast(message, ToastLevel.CRITICAL, title, duration)
