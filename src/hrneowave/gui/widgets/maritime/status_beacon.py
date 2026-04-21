# -*- coding: utf-8 -*-
"""
StatusBeacon - Indicateur d'état maritime
Design System Maritime 2025 - CHNeoWave

Indicateur d'état avec :
- Animation de pulsation
- Couleurs d'état standardisées
- Label optionnel
- Tailles multiples
- Accessibilité
"""

import sys
from typing import Optional

try:
    from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QFrame, QSizePolicy
    from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, Signal, QTimer, QRect, Property, QSize
    from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QFont
    pyqtSignal = Signal
except ImportError:
    try:
        from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QFrame, QSizePolicy
        from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtSignal, QTimer, QRect, QSize
        from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QFont
    except ImportError:
        from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QFrame, QSizePolicy
        from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtSignal, QTimer, QRect, QSize
        from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QFont


class StatusBeacon(QWidget):
    """
    Indicateur d'état maritime avec animation de pulsation.
    
    Caractéristiques :
    - États prédéfinis (active, warning, error, inactive)
    - Animation de pulsation
    - Label optionnel
    - Tailles configurables
    - Accessibilité WCAG 2.1
    """
    
    # Signaux
    status_changed = pyqtSignal(str)  # Nouvel état
    clicked = pyqtSignal()
    
    # États disponibles
    STATUS_ACTIVE = "active"
    STATUS_WARNING = "warning"
    STATUS_ERROR = "error"
    STATUS_INACTIVE = "inactive"
    STATUS_PENDING = "pending"
    STATUS_CONNECTING = "connecting"
    STATUS_UNKNOWN = "unknown"
    
    # Tailles disponibles
    SIZE_SMALL = "small"    # 8px
    SIZE_MEDIUM = "medium"  # 12px
    SIZE_LARGE = "large"    # 16px
    
    # Constantes Design System
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
        'emerald_success': '#4CAF50',
        'amber_warning': '#FF8F00',
        'purple_unknown': '#9C27B0'
    }
    
    def __init__(self, parent: Optional[QWidget] = None,
                 status: str = STATUS_INACTIVE,
                 label: str = "",
                 size: str = SIZE_MEDIUM,
                 pulse: bool = True,
                 clickable: bool = False):
        super().__init__(parent)
        
        self.status = status
        self.label_text = label
        self.size = size
        self.pulse_enabled = pulse
        self.clickable = clickable
        
        # État d'animation
        self._pulse_opacity = 1.0
        self._is_pulsing = False
        
        # Configuration de base
        self._setup_ui()
        self._setup_animations()
        
        # Démarrage de l'animation si nécessaire
        if self.pulse_enabled and self.status in [self.STATUS_ACTIVE, self.STATUS_CONNECTING]:
            self.start_pulse()
        
        # Styles
        self._apply_beacon_style()
        
        # Événements
        if self.clickable:
            self.setCursor(Qt.CursorShape.PointingHandCursor)
    
    def _setup_ui(self):
        """Configure l'interface du beacon."""
        # Layout horizontal
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(self.FIBONACCI_SPACES[0])  # 8px
        self.layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        
        # Zone du beacon (sera dessinée dans paintEvent)
        self.beacon_size = self._get_beacon_size()
        min_width = self.beacon_size + (100 if self.label_text else 0)
        min_height = self.beacon_size + 4  # Marge pour l'animation
        self.setMinimumSize(min_width, min_height)
        self_policy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

        self.setSizePolicy(self_policy)
        
        # Label optionnel
        if self.label_text:
            self.label_widget = QLabel(self.label_text)
            self.label_widget.setObjectName("beacon_label")
            self.layout.addWidget(self.label_widget)
            
            # Ajustement de la taille avec label
            label_width = self.label_widget.fontMetrics().horizontalAdvance(self.label_text)
            min_width = self.beacon_size + label_width + self.FIBONACCI_SPACES[0] + 10
            min_height = max(self.beacon_size + 4, self.label_widget.sizeHint().height())
            self.setMinimumSize(min_width, min_height)
            self_policy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

            self.setSizePolicy(self_policy)
    
    def _setup_animations(self):
        """Configure les animations du beacon."""
        # Animation de pulsation
        self.pulse_animation = QPropertyAnimation(self, b"pulse_opacity")
        self.pulse_animation.setDuration(1500)
        self.pulse_animation.setEasingCurve(QEasingCurve.Type.InOutSine)
        self.pulse_animation.setStartValue(1.0)
        self.pulse_animation.setEndValue(0.3)
        self.pulse_animation.setLoopCount(-1)  # Infini
        
        # Animation de changement d'état
        self.state_animation = QPropertyAnimation(self, b"geometry")
        self.state_animation.setDuration(200)
        self.state_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
    
    def _get_beacon_size(self) -> int:
        """Retourne la taille du beacon selon la configuration."""
        sizes = {
            self.SIZE_SMALL: 8,
            self.SIZE_MEDIUM: 12,
            self.SIZE_LARGE: 16
        }
        return sizes.get(self.size, 12)
    
    def _get_status_color(self) -> QColor:
        """Retourne la couleur selon l'état."""
        colors = {
            self.STATUS_ACTIVE: QColor(self.MARITIME_COLORS['emerald_success']),
            self.STATUS_WARNING: QColor(self.MARITIME_COLORS['amber_warning']),
            self.STATUS_ERROR: QColor(self.MARITIME_COLORS['coral_alert']),
            self.STATUS_INACTIVE: QColor(self.MARITIME_COLORS['slate_gray']),
            self.STATUS_PENDING: QColor(self.MARITIME_COLORS['slate_gray']),
            self.STATUS_CONNECTING: QColor(self.MARITIME_COLORS['tidal_cyan']),
            self.STATUS_UNKNOWN: QColor(self.MARITIME_COLORS['purple_unknown'])
        }
        return colors.get(self.status, QColor(self.MARITIME_COLORS['slate_gray']))
    
    def _apply_beacon_style(self):
        """Applique le style maritime au beacon."""
        style = f"""
        StatusBeacon {{
            background-color: transparent;
        }}
        
        QLabel#beacon_label {{
            font-size: 12px;
            font-weight: 500;
            color: {self.MARITIME_COLORS['storm_gray']};
            /* text-transform not supported in Qt */

        }}
        """
        
        self.setStyleSheet(style)
    
    def paintEvent(self, event):
        """Rendu personnalisé du beacon."""
        super().paintEvent(event)
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Position du beacon
        beacon_x = 2
        beacon_y = (self.height() - self.beacon_size) // 2
        beacon_rect = QRect(beacon_x, beacon_y, self.beacon_size, self.beacon_size)
        
        # Couleur selon l'état
        color = self._get_status_color()
        
        # Application de l'opacité de pulsation
        if self._is_pulsing:
            color.setAlphaF(self._pulse_opacity)
        
        # Dessin du beacon principal
        painter.setBrush(QBrush(color))
        painter.setPen(QPen(Qt.PenStyle.NoPen))
        painter.drawEllipse(beacon_rect)
        
        # Halo pour les états actifs
        if self.status in [self.STATUS_ACTIVE, self.STATUS_CONNECTING] and self._is_pulsing:
            halo_color = QColor(color)
            halo_color.setAlphaF(0.3 * self._pulse_opacity)
            
            halo_size = int(self.beacon_size * 1.5)
            halo_x = beacon_x - (halo_size - self.beacon_size) // 2
            halo_y = beacon_y - (halo_size - self.beacon_size) // 2
            halo_rect = QRect(halo_x, halo_y, halo_size, halo_size)
            
            painter.setBrush(QBrush(halo_color))
            painter.drawEllipse(halo_rect)
    
    def set_status(self, status: str, animate: bool = True):
        """Définit le statut du beacon."""
        if status == self.status:
            return
        
        old_status = self.status
        self.status = status
        
        # Gestion de l'animation de pulsation
        if self.pulse_enabled:
            if status in [self.STATUS_ACTIVE, self.STATUS_CONNECTING]:
                self.start_pulse()
            else:
                self.stop_pulse()
        
        # Animation de changement d'état
        if animate:
            self._animate_state_change()
        
        # Mise à jour de l'affichage
        self.update()
        
        # Émission du signal
        self.status_changed.emit(status)
    
    def set_label(self, label: str):
        """Définit le label du beacon."""
        self.label_text = label
        if hasattr(self, 'label_widget'):
            self.label_widget.setText(label)
        elif label:
            # Création du label s'il n'existait pas
            self._setup_ui()
    
    def set_size(self, size: str):
        """Définit la taille du beacon."""
        if size in [self.SIZE_SMALL, self.SIZE_MEDIUM, self.SIZE_LARGE]:
            self.size = size
            self.beacon_size = self._get_beacon_size()
            self._setup_ui()  # Reconfiguration de l'UI
    
    def set_pulse_enabled(self, enabled: bool):
        """Active ou désactive la pulsation."""
        self.pulse_enabled = enabled
        if enabled and self.status in [self.STATUS_ACTIVE, self.STATUS_CONNECTING]:
            self.start_pulse()
        else:
            self.stop_pulse()
    
    def start_pulse(self):
        """Démarre l'animation de pulsation."""
        if not self._is_pulsing:
            self._is_pulsing = True
            self.pulse_animation.start()
    
    def stop_pulse(self):
        """Arrête l'animation de pulsation."""
        if self._is_pulsing:
            self._is_pulsing = False
            self.pulse_animation.stop()
            self._pulse_opacity = 1.0
            self.update()
    
    def _animate_state_change(self):
        """Animation lors du changement d'état."""
        # Animation de "rebond"
        current_geometry = self.geometry()
        expanded_geometry = QRect(
            current_geometry.x() - 1,
            current_geometry.y() - 1,
            current_geometry.width() + 2,
            current_geometry.height() + 2
        )
        
        self.state_animation.setStartValue(current_geometry)
        self.state_animation.setKeyValueAt(0.5, expanded_geometry)
        self.state_animation.setEndValue(current_geometry)
        self.state_animation.start()
    
    def mousePressEvent(self, event):
        """Gestion du clic."""
        super().mousePressEvent(event)
        if self.clickable and event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
    
    def get_status(self) -> str:
        """Retourne le statut actuel."""
        return self.status
    
    def is_pulsing(self) -> bool:
        """Retourne True si le beacon pulse."""
        return self._is_pulsing
    
    # Propriété pour l'animation de pulsation
    def get_pulse_opacity(self):
        return self._pulse_opacity
    
    def set_pulse_opacity(self, opacity):
        self._pulse_opacity = opacity
        self.update()
    
    pulse_opacity = Property(float, get_pulse_opacity, set_pulse_opacity)
    
    def sizeHint(self):
        """Taille suggérée du beacon."""
        width = self.beacon_size + 4
        if self.label_text and hasattr(self, 'label_widget'):
            label_width = self.label_widget.fontMetrics().horizontalAdvance(self.label_text)
            width += label_width + self.FIBONACCI_SPACES[0]
        
        height = max(self.beacon_size + 4, 20)
        return super().sizeHint().expandedTo(QSize(width, height))
    
    def minimumSizeHint(self):
        """Taille minimale suggérée."""
        return super().minimumSizeHint()
    
    @staticmethod
    def create_status_group(parent: Optional[QWidget] = None, 
                          statuses: list = None) -> dict:
        """Crée un groupe de beacons pour différents statuts."""
        if statuses is None:
            statuses = [
                (StatusBeacon.STATUS_ACTIVE, "Actif"),
                (StatusBeacon.STATUS_WARNING, "Attention"),
                (StatusBeacon.STATUS_ERROR, "Erreur"),
                (StatusBeacon.STATUS_INACTIVE, "Inactif")
            ]
        
        beacons = {}
        for status, label in statuses:
            beacon = StatusBeacon(
                parent=parent,
                status=status,
                label=label,
                pulse=True
            )
            beacons[status] = beacon
        
        return beacons
