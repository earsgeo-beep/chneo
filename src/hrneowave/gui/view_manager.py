# -*- coding: utf-8 -*-
"""
Gestionnaire de vues pour CHNeoWave

Ce module gère l'affichage et la navigation entre les différentes vues de l'application.
Il utilise des imports conditionnels pour éviter la création de widgets avant l'initialisation de QApplication.
"""

import logging
from typing import Dict, Optional, List

from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QApplication,
    QStackedWidget, QGraphicsOpacityEffect
)
from PySide6.QtCore import (
    QPropertyAnimation, QEasingCurve, QTimer, QObject, Signal, QRect, Qt, Slot
)
from PySide6.QtGui import QScreen

# Import du système de toast amélioré
from .components.enhanced_toast import ToastManager, ToastLevel

# Essayer d'importer les signaux unifiés
try:
    from hrneowave.core.unified_signals import ErrorLevel
    UNIFIED_SIGNALS_AVAILABLE = True
except ImportError:
    UNIFIED_SIGNALS_AVAILABLE = False
    # Créer un ErrorLevel de base si non disponible
    class ErrorLevel:
        INFO = "INFO"
        WARNING = "WARNING"
        ERROR = "ERROR"
        CRITICAL = "CRITICAL"

class ToastNotification(QWidget):
    """Widget de notification toast pour afficher des messages temporaires"""

    def __init__(self, message: str, level: str = "INFO", parent=None):
        super().__init__(parent)
        self.message = message
        self.level = level
        self.logger = logging.getLogger(__name__)
        
        # Configuration du widget
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(300, 80)
        
        # Interface utilisateur
        self._setup_ui()
        
        # Animation de fondu
        self.opacity_effect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(self.opacity_effect)
        
        self.fade_in_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_in_animation.setDuration(300)
        self.fade_in_animation.setStartValue(0.0)
        self.fade_in_animation.setEndValue(0.9)
        self.fade_in_animation.setEasingCurve(QEasingCurve.OutCubic)

        self.fade_out_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_out_animation.setDuration(300)
        self.fade_out_animation.setStartValue(0.9)
        self.fade_out_animation.setEndValue(0.0)
        self.fade_out_animation.setEasingCurve(QEasingCurve.InCubic)
        
        # Timer pour masquer automatiquement
        self.hide_timer = QTimer()
        self.hide_timer.setSingleShot(True)
        self.hide_timer.timeout.connect(self.hide_toast)
        
        # Connecter l'animation de sortie à la fermeture
        self.fade_out_animation.finished.connect(self.close)

    def _setup_ui(self):
        """Configure l'interface utilisateur du toast"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Label pour le message
        self.message_label = QLabel(self.message)
        self.message_label.setWordWrap(True)
        
        # Style selon le niveau
        styles = {
            "INFO": "background-color: #2196F3; color: white; border-radius: 5px; padding: 10px;",
            "WARNING": "background-color: #FF9800; color: white; border-radius: 5px; padding: 10px;",
            "ERROR": "background-color: #F44336; color: white; border-radius: 5px; padding: 10px;",
            "CRITICAL": "background-color: #9C27B0; color: white; border-radius: 5px; padding: 10px;"
        }
        
        style = styles.get(self.level, styles["INFO"])
        self.message_label.setStyleSheet(style)
        
        layout.addWidget(self.message_label)
        
    def show_toast(self, duration: int = 5000):
        """Affiche le toast avec une animation de fondu"""
        self.show()
        self.fade_in_animation.start()
        self.hide_timer.start(duration)
        self.logger.debug(f"Toast affiché: {self.level} - {self.message}")

    def hide_toast(self):
        """Masque le toast avec une animation de fondu"""
        self.hide_timer.stop()
        self.fade_out_animation.start()
        self.logger.debug(f"Toast masqué: {self.level} - {self.message}")


class ViewManager(QObject):
        """Gestionnaire de vues pour l'application CHNeoWave"""
        
        # Signaux de classe
        view_changed = Signal(str)
        error_displayed = Signal(object)
        
        # Signaux pour le workflow
        projectSelected = Signal(str)
        calibrationFinished = Signal(dict)
        acquisitionFinished = Signal(dict)
        analysisFinished = Signal(dict)
        exportFinished = Signal(str)
        
        def __init__(self, stacked_widget: QStackedWidget = None):
            super().__init__()
            self.logger = logging.getLogger(__name__)
            self.stacked_widget = stacked_widget
            self.views: Dict[str, QWidget] = {}
            self.current_view: Optional[str] = None
            
            # Gestionnaire de toasts amélioré
            self.toast_manager = ToastManager(max_toasts=3, parent=self)
            
            # Ancienne gestion des toasts (pour compatibilité)
            self.active_toasts: List = []
            self.max_toasts = 3
            
            # Bus d'erreurs unifié (optionnel)
            self.error_bus = None
            
            # Connecter aux signaux unifiés si disponibles
            self._connect_unified_signals()
            
            self.logger.info("ViewManager initialisé")
        
        def register_view(self, name: str, widget: QWidget) -> None:
            """Enregistre une vue dans le gestionnaire"""
            if name in self.views:
                self.logger.warning(f"Vue '{name}' déjà enregistrée, remplacement")
                old_widget = self.views[name]
                self.stacked_widget.removeWidget(old_widget)
            
            # Détacher le widget de son parent actuel s'il en a un
            if widget.parent() is not None:
                widget.setParent(None)
            
            # Ajouter le widget au QStackedWidget
            self.views[name] = widget
            index = self.stacked_widget.addWidget(widget)
            self.logger.info(f"Vue '{name}' enregistrée avec succès dans le QStackedWidget à l'index {index}")

        @Slot(str)
        def change_view_by_name(self, name: str):
            """Slot public pour changer de vue par son nom."""
            self.change_view(name)

        def change_view(self, name: str) -> None:
            """Change la vue affichée dans le QStackedWidget"""
            if name not in self.views:
                self.logger.error(f"Tentative d'affichage d'une vue non enregistrée: {name}")
                return

            widget_to_show = self.views[name]
            previous_view = self.current_view
            self.stacked_widget.setCurrentWidget(widget_to_show)
            self.current_view = name
            self.view_changed.emit(name)
            self.logger.info(f"[NAV SUCCESS] Navigation reussie: {previous_view} -> {name}")
            self.logger.info(f"Vue '{name}' activee")
        
        def _connect_unified_signals(self):
            """Connecte aux signaux unifiés si disponibles"""
            if not UNIFIED_SIGNALS_AVAILABLE:
                self.logger.info("Signaux unifiés non disponibles")
                return
            
            try:
                from hrneowave.core.unified_signals import get_unified_signals
                unified_signals = get_unified_signals()
                
                if unified_signals and hasattr(unified_signals, 'error_bus'):
                    self.error_bus = unified_signals.error_bus
                    # Connecter aux signaux d'erreur pour afficher les toasts
                    if hasattr(self.error_bus, 'error_occurred'):
                        self.error_bus.error_occurred.connect(self.show_error_toast)
                    if hasattr(self.error_bus, 'warning_occurred'):
                        self.error_bus.warning_occurred.connect(self.show_error_toast)
                    if hasattr(self.error_bus, 'info_occurred'):
                        self.error_bus.info_occurred.connect(self.show_error_toast)
                    
                    self.logger.info("Connecté au bus d'erreurs unifié")
                
            except Exception as e:
                self.logger.warning(f"Impossible de se connecter aux signaux unifiés: {e}")
            
            self.logger.info("Signaux unifiés connectés au ViewManager")
        
        def display_error_toast(self, error_msg):
            """Affiche un toast de notification pour une erreur"""
            # Vérifier que QApplication existe avant de créer des widgets
            if not QApplication.instance():
                self.logger.warning("QApplication non disponible, impossible d'afficher le toast")
                return
            
            # Créer la classe ToastNotification si nécessaire
            global ToastNotification
            if ToastNotification is None:
                ToastNotification = _create_toast_notification_class()
            
            # Limiter le nombre de toasts affichés simultanément
            if len(self.active_toasts) >= self.max_toasts:
                oldest_toast = self.active_toasts.pop(0)
                oldest_toast.hide_toast()
            
            toast = ToastNotification(error_msg.message, error_msg.level, self.stacked_widget.parent())
            self.active_toasts.append(toast)
            toast.show_toast()
            self.error_displayed.emit(error_msg)
            
            # Nettoyer la liste des toasts lorsque l'animation est terminée
            toast.fade_out_animation.finished.connect(lambda: self._remove_toast(toast))
        
        def _remove_toast(self, toast):
            """Supprime un toast de la liste active"""
            if toast in self.active_toasts:
                self.active_toasts.remove(toast)
        
        def switch_to_view(self, view_name: str) -> bool:
            """Change vers la vue spécifiée"""
            # 🔍 TRAÇAGE FIN - Ajouté pour diagnostic navigation
            self.logger.debug(f"[NAV] {self.current_view} -> {view_name}")
            
            if view_name not in self.views:
                self.logger.error(f"Vue '{view_name}' non trouvée")
                self.logger.error(
                    f"[NAV ERROR] Vue '{view_name}' non trouvee dans {list(self.views.keys())}"
                )
                if self.error_bus and UNIFIED_SIGNALS_AVAILABLE:
                    self.error_bus.emit_error(
                        ErrorLevel.ERROR,
                        f"Vue '{view_name}' non trouvée",
                        "ViewManager"
                    )
                return False
            
            # Vérifications de sécurité pour éviter les violations d'accès
            if not self.stacked_widget:
                self.logger.error("StackedWidget non initialisé")
                return False
                
            try:
                widget = self.views[view_name]
                if not widget:
                    self.logger.error(f"Widget pour la vue '{view_name}' est None")
                    return False
                    
                previous_view = self.current_view
                
                # Vérifier que le widget est valide avant de l'utiliser
                if hasattr(widget, 'isValid') and not widget.isValid():
                    self.logger.error(f"Widget pour la vue '{view_name}' n'est pas valide")
                    return False
                    
                self.stacked_widget.setCurrentWidget(widget)
                self.current_view = view_name
                
                self.logger.info(f"[NAV SUCCESS] Navigation reussie: {previous_view} -> {view_name}")
                
                self.view_changed.emit(view_name)
                self.logger.info(f"Changement vers la vue '{view_name}'")
                
                if self.error_bus and UNIFIED_SIGNALS_AVAILABLE:
                    self.error_bus.emit_info(
                        f"Changement vers la vue '{view_name}'",
                        "ViewManager",
                        {'previous_view': previous_view}
                    )
                
                return True
            
            except Exception as e:
                self.logger.error(f"Erreur lors du changement de vue: {e}")
                self.logger.exception(f"[NAV EXCEPTION] Erreur lors du changement de vue: {e}")
                if self.error_bus and UNIFIED_SIGNALS_AVAILABLE:
                    self.error_bus.emit_error(
                        ErrorLevel.ERROR,
                        f"Erreur lors du changement de vue: {e}",
                        "ViewManager",
                        exception=e
                    )
                return False
        
        def get_current_view(self) -> Optional[str]:
            """Retourne le nom de la vue actuelle"""
            return self.current_view
        
        def get_view_widget(self, view_name: str):
            """Retourne le widget d'une vue"""
            return self.views.get(view_name)
        
        def has_view(self, view_name: str) -> bool:
            """Vérifie si une vue est enregistrée"""
            return view_name in self.views
        
        def show_error_toast(self, error_msg) -> None:
            """Affiche un toast d'erreur avec le système amélioré"""
            # Vérifier que QApplication existe
            if not QApplication.instance():
                self.logger.warning("QApplication non disponible, impossible d'afficher le toast")
                return
            
            try:
                # Extraire les informations du message d'erreur
                message = error_msg.message if hasattr(error_msg, 'message') else str(error_msg)
                
                # Mapper les niveaux d'erreur vers les niveaux de toast
                if hasattr(error_msg, 'level'):
                    if UNIFIED_SIGNALS_AVAILABLE:
                        level_mapping = {
                            ErrorLevel.INFO: ToastLevel.INFO,
                            ErrorLevel.WARNING: ToastLevel.WARNING,
                            ErrorLevel.ERROR: ToastLevel.ERROR,
                            ErrorLevel.CRITICAL: ToastLevel.CRITICAL
                        }
                        toast_level = level_mapping.get(error_msg.level, ToastLevel.INFO)
                    else:
                        # Mapping pour les niveaux string
                        level_str = str(error_msg.level).upper()
                        if level_str in ['SUCCESS', 'OK']:
                            toast_level = ToastLevel.SUCCESS
                        elif level_str in ['WARNING', 'WARN']:
                            toast_level = ToastLevel.WARNING
                        elif level_str in ['ERROR', 'ERR']:
                            toast_level = ToastLevel.ERROR
                        elif level_str in ['CRITICAL', 'CRIT', 'FATAL']:
                            toast_level = ToastLevel.CRITICAL
                        else:
                            toast_level = ToastLevel.INFO
                else:
                    toast_level = ToastLevel.INFO
                
                # Titre selon le niveau
                titles = {
                    ToastLevel.SUCCESS: "Succès",
                    ToastLevel.INFO: "Information",
                    ToastLevel.WARNING: "Attention",
                    ToastLevel.ERROR: "Erreur",
                    ToastLevel.CRITICAL: "Critique"
                }
                title = titles.get(toast_level, "Notification")
                
                # Durée selon le niveau
                durations = {
                    ToastLevel.SUCCESS: 3000,
                    ToastLevel.INFO: 4000,
                    ToastLevel.WARNING: 6000,
                    ToastLevel.ERROR: 8000,
                    ToastLevel.CRITICAL: 10000
                }
                duration = durations.get(toast_level, 5000)
                
                # Afficher le toast avec le gestionnaire amélioré
                toast = self.toast_manager.show_toast(
                    message=message,
                    level=toast_level,
                    title=title,
                    duration=duration
                )
                
                # Émettre le signal pour compatibilité
                self.error_displayed.emit(error_msg)
                
                self.logger.info(f"Toast amélioré affiché: {toast_level.value} - {message}")
                
            except Exception as e:
                self.logger.error(f"Erreur lors de l'affichage du toast amélioré: {e}")
                # Fallback vers l'ancien système si nécessaire
                self._show_fallback_toast(error_msg)
        
        def _on_session_finished(self) -> None:
            """P0: Gestionnaire pour sessionFinished() - change automatiquement vers AnalysisView"""
            self.logger.info("Session terminée, changement automatique vers AnalysisView")
            
            # P0: AnalysisView apparaît quand sessionFinished est reçu
            QTimer.singleShot(1000, lambda: self.switch_to_view("AnalysisView"))
            
            # Afficher une notification de succès
            if self.error_bus and UNIFIED_SIGNALS_AVAILABLE:
                self.error_bus.emit_info(
                    "Session d'acquisition terminée",
                    "ViewManager"
                )
        
        def cleanup_toasts(self) -> None:
            """Nettoie tous les toasts actifs"""
            # Nettoyer les nouveaux toasts
            self.toast_manager.clear_all_toasts()
            
            # Nettoyer les anciens toasts (compatibilité)
            for toast in self.active_toasts:
                if hasattr(toast, 'hide_toast'):
                    toast.hide_toast()
            self.active_toasts.clear()
            
            self.logger.info("Tous les toasts ont été nettoyés")
        
        def _show_fallback_toast(self, error_msg):
            """Système de toast de secours en cas d'erreur"""
            try:
                message = error_msg.message if hasattr(error_msg, 'message') else str(error_msg)
                level = error_msg.level if hasattr(error_msg, 'level') else 'INFO'
                
                # Toast simple de secours
                self.toast_manager.info(f"[Fallback] {message}", "Notification")
                
            except Exception as e:
                self.logger.error(f"Erreur dans le système de toast de secours: {e}")
        
        # Méthodes de convenance pour les toasts
        def show_success_toast(self, message: str, title: str = "Succès"):
            """Affiche un toast de succès"""
            return self.toast_manager.success(message, title)
        
        def show_info_toast(self, message: str, title: str = "Information"):
            """Affiche un toast d'information"""
            return self.toast_manager.info(message, title)
        
        def show_warning_toast(self, message: str, title: str = "Attention"):
            """Affiche un toast d'avertissement"""
            return self.toast_manager.warning(message, title)
        
        def show_critical_toast(self, message: str, title: str = "Critique"):
            """Affiche un toast critique"""
            return self.toast_manager.critical(message, title)
