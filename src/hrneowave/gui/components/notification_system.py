#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CHNeoWave - Système de notifications améliorées
Fournit des notifications toast, des alertes et des messages système

Auteur: Architecte Logiciel en Chef (ALC)
Date: 2024
Version: 1.0.0
"""

import logging
from typing import Optional, Dict, Any, List
from enum import Enum
from datetime import datetime

from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton,
    QFrame, QScrollArea, QApplication, QGraphicsOpacityEffect,
    QSizePolicy, QTextEdit, QDialog, QDialogButtonBox
)
from PySide6.QtCore import (
    Qt, Signal, QTimer, QPropertyAnimation, QEasingCurve, 
    QParallelAnimationGroup, QSequentialAnimationGroup, Property
)
from PySide6.QtGui import QFont, QPixmap, QIcon, QPainter, QPen, QBrush, QColor

from .material_components import MaterialButton, MaterialCard
from .status_indicators import StatusLevel
from ..icons import svg_icon


class NotificationType(Enum):
    """Types de notifications"""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class NotificationPriority(Enum):
    """Priorités des notifications"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4


class NotificationAction:
    """Action associée à une notification"""
    
    def __init__(self, label: str, callback, primary: bool = False):
        self.label = label
        self.callback = callback
        self.primary = primary


class Notification:
    """Modèle de notification"""
    
    def __init__(self, 
                 title: str,
                 message: str,
                 notification_type: NotificationType = NotificationType.INFO,
                 priority: NotificationPriority = NotificationPriority.NORMAL,
                 duration: int = 5000,  # ms
                 persistent: bool = False,
                 actions: List[NotificationAction] = None):
        self.id = f"notif_{datetime.now().timestamp()}"
        self.title = title
        self.message = message
        self.type = notification_type
        self.priority = priority
        self.duration = duration
        self.persistent = persistent
        self.actions = actions or []
        self.timestamp = datetime.now()
        self.read = False
        self.dismissed = False


class ToastNotification(QWidget):
    """Widget de notification toast avec Material Design"""
    
    dismissed = Signal(str)  # notification_id
    action_triggered = Signal(str, str)  # notification_id, action_label
    
    def __init__(self, notification: Notification, parent=None):
        super().__init__(parent)
        self.notification = notification
        self._opacity = 1.0
        
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self._setup_ui()
        self._setup_animations()
        self._apply_style()
        
        # Auto-dismiss timer
        if not notification.persistent and notification.duration > 0:
            QTimer.singleShot(notification.duration, self._auto_dismiss)
    
    def _setup_ui(self):
        """Configure l'interface du toast"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)
        
        # En-tête avec icône et titre
        header_layout = QHBoxLayout()
        
        # Icône selon le type
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(24, 24)
        self._set_icon()
        header_layout.addWidget(self.icon_label)
        
        # Titre
        self.title_label = QLabel(self.notification.title)
        title_font = QFont()
        title_font.setPointSize(10)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        header_layout.addWidget(self.title_label)
        
        header_layout.addStretch()
        
        # Bouton de fermeture
        self.close_button = QPushButton("×")
        self.close_button.setFixedSize(20, 20)
        self.close_button.setStyleSheet("""
            QPushButton {
                border: none;
                background: transparent;
                font-size: 16px;
                font-weight: bold;
                color: #666;
            }
            QPushButton:hover {
                background: rgba(0, 0, 0, 0.1);
                border-radius: 10px;
            }
        """)
        self.close_button.clicked.connect(self._dismiss)
        header_layout.addWidget(self.close_button)
        
        layout.addLayout(header_layout)
        
        # Message
        self.message_label = QLabel(self.notification.message)
        self.message_label.setWordWrap(True)
        self.message_label.setStyleSheet("color: #424242;")
        layout.addWidget(self.message_label)
        
        # Actions
        if self.notification.actions:
            actions_layout = QHBoxLayout()
            actions_layout.addStretch()
            
            for action in self.notification.actions:
                btn = MaterialButton(
                    action.label,
                    style=MaterialButton.Style.FILLED if action.primary else MaterialButton.Style.TEXT
                )
                btn.clicked.connect(lambda checked, a=action: self._trigger_action(a))
                actions_layout.addWidget(btn)
            
            layout.addLayout(actions_layout)
    
    def _set_icon(self):
        """Définit l'icône selon le type de notification"""
        icons = {
            NotificationType.INFO: ("info", "#137E92"),
            NotificationType.SUCCESS: ("check", "#126A56"),
            NotificationType.WARNING: ("warning", "#C47B18"),
            NotificationType.ERROR: ("error", "#A23F45"),
            NotificationType.CRITICAL: ("error", "#A23F45"),
        }

        icon_name, color = icons.get(self.notification.type, icons[NotificationType.INFO])
        self.icon_label.setPixmap(svg_icon(icon_name, color, 20).pixmap(20, 20))
        self.icon_label.setAlignment(Qt.AlignCenter)
    
    def _apply_style(self):
        """Applique le style basé sur le type de notification"""
        colors = {
            NotificationType.INFO: {
                'bg': '#E3F2FD',
                'border': '#2196F3',
                'text': '#1565C0'
            },
            NotificationType.SUCCESS: {
                'bg': '#E8F5E8',
                'border': '#4CAF50',
                'text': '#2E7D32'
            },
            NotificationType.WARNING: {
                'bg': '#FFF3E0',
                'border': '#FF9800',
                'text': '#F57C00'
            },
            NotificationType.ERROR: {
                'bg': '#FFEBEE',
                'border': '#F44336',
                'text': '#C62828'
            },
            NotificationType.CRITICAL: {
                'bg': '#FCE4EC',
                'border': '#E91E63',
                'text': '#AD1457'
            }
        }
        
        color_scheme = colors.get(self.notification.type, colors[NotificationType.INFO])
        
        style = f"""
            ToastNotification {{
                background-color: {color_scheme['bg']};
                border: 2px solid {color_scheme['border']};
                border-radius: 8px;
            }}
        """
        self.setStyleSheet(style)
        
        self.title_label.setStyleSheet(f"color: {color_scheme['text']};")
    
    def _setup_animations(self):
        """Configure les animations d'entrée et de sortie"""
        # Animation d'entrée (slide + fade)
        self.slide_in = QPropertyAnimation(self, b"pos")
        self.slide_in.setDuration(300)
        self.slide_in.setEasingCurve(QEasingCurve.OutCubic)
        
        self.fade_in = QPropertyAnimation(self, b"windowOpacity")
        self.fade_in.setDuration(300)
        self.fade_in.setStartValue(0.0)
        self.fade_in.setEndValue(1.0)
        
        self.enter_animation = QParallelAnimationGroup()
        self.enter_animation.addAnimation(self.slide_in)
        self.enter_animation.addAnimation(self.fade_in)
        
        # Animation de sortie
        self.fade_out = QPropertyAnimation(self, b"windowOpacity")
        self.fade_out.setDuration(200)
        self.fade_out.setStartValue(1.0)
        self.fade_out.setEndValue(0.0)
        self.fade_out.finished.connect(self._on_fade_out_finished)
    
    def show_animated(self, start_pos, end_pos):
        """Affiche le toast avec animation"""
        self.move(start_pos)
        self.slide_in.setStartValue(start_pos)
        self.slide_in.setEndValue(end_pos)
        
        self.show()
        self.enter_animation.start()
    
    def _dismiss(self):
        """Ferme le toast avec animation"""
        self.fade_out.start()
    
    def _auto_dismiss(self):
        """Fermeture automatique"""
        if not self.notification.persistent:
            self._dismiss()
    
    def _trigger_action(self, action: NotificationAction):
        """Déclenche une action de notification"""
        self.action_triggered.emit(self.notification.id, action.label)
        if action.callback:
            action.callback()
        self._dismiss()
    
    def _on_fade_out_finished(self):
        """Appelé quand l'animation de sortie est terminée"""
        self.dismissed.emit(self.notification.id)
        self.close()
        self.deleteLater()


class NotificationCenter(QWidget):
    """Centre de notifications avec historique"""
    
    notification_clicked = Signal(str)  # notification_id
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.notifications: Dict[str, Notification] = {}
        self.active_toasts: Dict[str, ToastNotification] = {}
        self.max_toasts = 5
        self.toast_spacing = 10
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Configure l'interface du centre de notifications"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # En-tête
        header_layout = QHBoxLayout()
        
        title_label = QLabel("Notifications")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Bouton pour marquer tout comme lu
        self.mark_all_read_btn = MaterialButton("Tout marquer comme lu", style=MaterialButton.Style.TEXT)
        self.mark_all_read_btn.clicked.connect(self._mark_all_read)
        header_layout.addWidget(self.mark_all_read_btn)
        
        # Bouton pour effacer tout
        self.clear_all_btn = MaterialButton("Effacer tout", style=MaterialButton.Style.TEXT)
        self.clear_all_btn.clicked.connect(self._clear_all)
        header_layout.addWidget(self.clear_all_btn)
        
        layout.addLayout(header_layout)
        
        # Zone de notifications avec scroll
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        self.notifications_widget = QWidget()
        self.notifications_layout = QVBoxLayout(self.notifications_widget)
        self.notifications_layout.setContentsMargins(0, 0, 0, 0)
        self.notifications_layout.addStretch()
        
        scroll_area.setWidget(self.notifications_widget)
        layout.addWidget(scroll_area)
    
    def add_notification(self, notification: Notification, show_toast: bool = True):
        """Ajoute une nouvelle notification"""
        self.notifications[notification.id] = notification
        
        # Ajouter à l'historique
        self._add_to_history(notification)
        
        # Afficher le toast si demandé
        if show_toast and len(self.active_toasts) < self.max_toasts:
            self._show_toast(notification)
        
        self.logger.info(f"Notification ajoutée: {notification.title}")
    
    def _add_to_history(self, notification: Notification):
        """Ajoute la notification à l'historique"""
        # Créer une carte pour l'historique
        card = MaterialCard()
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(12, 8, 12, 8)
        
        # En-tête avec titre et timestamp
        header_layout = QHBoxLayout()
        
        title_label = QLabel(notification.title)
        title_font = QFont()
        title_font.setBold(True)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        time_label = QLabel(notification.timestamp.strftime("%H:%M"))
        time_label.setStyleSheet("color: #666; font-size: 11px;")
        header_layout.addWidget(time_label)
        
        card_layout.addLayout(header_layout)
        
        # Message
        message_label = QLabel(notification.message)
        message_label.setWordWrap(True)
        message_label.setStyleSheet("color: #424242;")
        card_layout.addWidget(message_label)
        
        # Insérer au début de la liste
        self.notifications_layout.insertWidget(0, card)
        
        # Limiter le nombre de notifications dans l'historique
        if self.notifications_layout.count() > 50:  # Garder les 50 dernières
            old_widget = self.notifications_layout.itemAt(self.notifications_layout.count() - 2).widget()
            if old_widget:
                old_widget.setParent(None)
    
    def _show_toast(self, notification: Notification):
        """Affiche un toast pour la notification"""
        toast = ToastNotification(notification)
        toast.dismissed.connect(self._on_toast_dismissed)
        toast.action_triggered.connect(self._on_toast_action)
        
        # Calculer la position
        screen = QApplication.primaryScreen().geometry()
        toast_size = toast.sizeHint()
        
        # Position de départ (hors écran à droite)
        start_x = screen.width()
        start_y = screen.height() - 100 - (len(self.active_toasts) * (toast_size.height() + self.toast_spacing))
        
        # Position finale
        end_x = screen.width() - toast_size.width() - 20
        end_y = start_y
        
        toast.show_animated(
            toast.pos().__class__(start_x, start_y),
            toast.pos().__class__(end_x, end_y)
        )
        
        self.active_toasts[notification.id] = toast
    
    def _on_toast_dismissed(self, notification_id: str):
        """Gestionnaire de fermeture de toast"""
        if notification_id in self.active_toasts:
            del self.active_toasts[notification_id]
        
        # Réorganiser les toasts restants
        self._reorganize_toasts()
    
    def _on_toast_action(self, notification_id: str, action_label: str):
        """Gestionnaire d'action de toast"""
        self.logger.info(f"Action '{action_label}' déclenchée pour notification {notification_id}")
    
    def _reorganize_toasts(self):
        """Réorganise les toasts après fermeture"""
        screen = QApplication.primaryScreen().geometry()
        
        for i, toast in enumerate(self.active_toasts.values()):
            new_y = screen.height() - 100 - (i * (toast.height() + self.toast_spacing))
            
            # Animation de repositionnement
            animation = QPropertyAnimation(toast, b"pos")
            animation.setDuration(200)
            animation.setStartValue(toast.pos())
            animation.setEndValue(toast.pos().__class__(toast.x(), new_y))
            animation.setEasingCurve(QEasingCurve.OutCubic)
            animation.start()
    
    def _mark_all_read(self):
        """Marque toutes les notifications comme lues"""
        for notification in self.notifications.values():
            notification.read = True
        self.logger.info("Toutes les notifications marquées comme lues")
    
    def _clear_all(self):
        """Efface toutes les notifications"""
        # Fermer tous les toasts actifs
        for toast in list(self.active_toasts.values()):
            toast._dismiss()
        
        # Effacer l'historique
        for i in reversed(range(self.notifications_layout.count() - 1)):  # -1 pour garder le stretch
            widget = self.notifications_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        
        self.notifications.clear()
        self.logger.info("Toutes les notifications effacées")


# Instance globale du centre de notifications
_notification_center = None

def get_notification_center() -> NotificationCenter:
    """Retourne l'instance globale du centre de notifications"""
    global _notification_center
    if _notification_center is None:
        _notification_center = NotificationCenter()
    return _notification_center

def show_notification(title: str, 
                     message: str, 
                     notification_type: NotificationType = NotificationType.INFO,
                     duration: int = 5000,
                     persistent: bool = False,
                     actions: List[NotificationAction] = None):
    """Fonction utilitaire pour afficher une notification"""
    notification = Notification(
        title=title,
        message=message,
        notification_type=notification_type,
        duration=duration,
        persistent=persistent,
        actions=actions
    )
    
    center = get_notification_center()
    center.add_notification(notification)

def show_success(title: str, message: str, duration: int = 3000):
    """Affiche une notification de succès"""
    show_notification(title, message, NotificationType.SUCCESS, duration)

def show_error(title: str, message: str, persistent: bool = True):
    """Affiche une notification d'erreur"""
    show_notification(title, message, NotificationType.ERROR, persistent=persistent)

def show_warning(title: str, message: str, duration: int = 7000):
    """Affiche une notification d'avertissement"""
    show_notification(title, message, NotificationType.WARNING, duration)

def show_info(title: str, message: str, duration: int = 5000):
    """Affiche une notification d'information"""
    show_notification(title, message, NotificationType.INFO, duration)
