#!/usr/bin/env python3
"""
CHNeoWave - User Preferences System
Système de préférences utilisateur avec sauvegarde persistante

Auteur: Architecte Logiciel en Chef (ALC)
Date: 2024
Version: 1.0.0
"""

import json
import logging
from enum import Enum
from typing import Any

from PySide6.QtCore import QObject, QSettings, Signal
from PySide6.QtWidgets import QApplication


class ThemeMode(Enum):
    """Modes de thème disponibles"""
    LIGHT = "light"
    DARK = "dark"
    AUTO = "auto"  # Suit le système
    HIGH_CONTRAST = "high_contrast"


class Language(Enum):
    """Langues supportées"""
    FRENCH = "fr"
    ENGLISH = "en"
    SPANISH = "es"


class UserPreferences(QObject):
    """Gestionnaire des préférences utilisateur"""
    
    # Signaux émis lors des changements
    theme_changed = Signal(str)  # nouveau thème
    language_changed = Signal(str)  # nouvelle langue
    shortcuts_changed = Signal(dict)  # nouveaux raccourcis
    preferences_reset = Signal()  # préférences réinitialisées
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        
        # Configuration Qt Settings
        self.settings = QSettings("CHNeoWave", "UserPreferences")
        
        # Préférences par défaut
        self._default_preferences = {
            "theme": {
                "mode": ThemeMode.LIGHT.value,
                "custom_colors": {
                    "primary": "#087F99",
                    "secondary": "#25B3CD",
                    "accent": "#A66B16"
                },
                "font_size": 10,
                "font_family": "Segoe UI"
            },
            "interface": {
                "language": Language.FRENCH.value,
                "show_tooltips": True,
                "show_animations": True,
                "compact_mode": False,
                "sidebar_width": 280,
                "window_state": {
                    "maximized": False,
                    "width": 1024,
                    "height": 768,
                    "x": 100,
                    "y": 100
                }
            },
            "shortcuts": {
                "file": {
                    "new_project": "Ctrl+N",
                    "open_project": "Ctrl+O",
                    "save_project": "Ctrl+S",
                    "export_data": "Ctrl+E",
                    "quit": "Ctrl+Q"
                },
                "view": {
                    "toggle_sidebar": "F9",
                    "fullscreen": "F11",
                    "zoom_in": "Ctrl++",
                    "zoom_out": "Ctrl+-",
                    "reset_zoom": "Ctrl+0"
                },
                "acquisition": {
                    "start_acquisition": "F5",
                    "stop_acquisition": "F6",
                    "pause_acquisition": "Space",
                    "calibrate": "F7"
                },
                "analysis": {
                    "run_analysis": "F8",
                    "export_results": "Ctrl+Shift+E",
                    "clear_results": "Ctrl+Shift+C"
                }
            },
            "acquisition": {
                "auto_save": True,
                "save_interval": 300,  # secondes
                "backup_count": 5,
                "default_duration": 60,
                "default_frequency": 1000
            },
            "analysis": {
                "auto_process": False,
                "show_progress": True,
                "parallel_processing": True,
                "cache_results": True
            },
            "accessibility": {
                "high_contrast": False,
                "large_fonts": False,
                "screen_reader": False,
                "keyboard_navigation": True
            }
        }
        
        # Charger les préférences
        self._load_preferences()
    
    def _load_preferences(self):
        """Charge les préférences depuis le stockage persistant"""
        try:
            # Charger depuis QSettings
            self.preferences = {}
            
            for category, settings in self._default_preferences.items():
                self.preferences[category] = {}
                
                for key, default_value in settings.items():
                    if isinstance(default_value, dict):
                        # Gérer les sous-dictionnaires
                        self.preferences[category][key] = {}
                        for subkey, subdefault in default_value.items():
                            setting_key = f"{category}/{key}/{subkey}"
                            self.preferences[category][key][subkey] = self.settings.value(
                                setting_key, subdefault
                            )
                    else:
                        setting_key = f"{category}/{key}"
                        self.preferences[category][key] = self.settings.value(
                            setting_key, default_value
                        )
            
            self.logger.info("Préférences utilisateur chargées avec succès")
            
        except Exception as e:
            self.logger.error(f"Erreur lors du chargement des préférences: {e}")
            self.preferences = self._default_preferences.copy()
    
    def save_preferences(self):
        """Sauvegarde les préférences dans le stockage persistant"""
        try:
            for category, settings in self.preferences.items():
                for key, value in settings.items():
                    if isinstance(value, dict):
                        # Gérer les sous-dictionnaires
                        for subkey, subvalue in value.items():
                            setting_key = f"{category}/{key}/{subkey}"
                            self.settings.setValue(setting_key, subvalue)
                    else:
                        setting_key = f"{category}/{key}"
                        self.settings.setValue(setting_key, value)
            
            self.settings.sync()
            self.logger.info("Préférences utilisateur sauvegardées avec succès")
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la sauvegarde des préférences: {e}")
    
    def get_preference(self, category: str, key: str, subkey: str = None) -> Any:
        """Récupère une préférence spécifique"""
        try:
            if subkey:
                return self.preferences[category][key][subkey]
            else:
                return self.preferences[category][key]
        except KeyError:
            self.logger.warning(f"Préférence non trouvée: {category}.{key}.{subkey or ''}")
            return None
    
    def set_preference(self, category: str, key: str, value: Any, subkey: str = None):
        """Définit une préférence et sauvegarde automatiquement"""
        try:
            if subkey:
                if category not in self.preferences:
                    self.preferences[category] = {}
                if key not in self.preferences[category]:
                    self.preferences[category][key] = {}
                self.preferences[category][key][subkey] = value
            else:
                if category not in self.preferences:
                    self.preferences[category] = {}
                self.preferences[category][key] = value
            
            # Sauvegarder automatiquement
            self.save_preferences()
            
            # Émettre les signaux appropriés
            self._emit_change_signals(category, key, value)
            
            self.logger.debug(f"Préférence mise à jour: {category}.{key} = {value}")
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la définition de la préférence: {e}")
    
    def _emit_change_signals(self, category: str, key: str, value: Any):
        """Émet les signaux appropriés selon le type de changement"""
        if category == "theme" and key == "mode":
            self.theme_changed.emit(value)
        elif category == "interface" and key == "language":
            self.language_changed.emit(value)
        elif category == "shortcuts":
            self.shortcuts_changed.emit(self.preferences["shortcuts"])
    
    def get_theme_mode(self) -> str:
        """Récupère le mode de thème actuel"""
        return self.get_preference("theme", "mode")
    
    def set_theme_mode(self, mode: str):
        """Définit le mode de thème"""
        if mode in [m.value for m in ThemeMode]:
            self.set_preference("theme", "mode", mode)
        else:
            self.logger.warning(f"Mode de thème invalide: {mode}")
    
    def get_language(self) -> str:
        """Récupère la langue actuelle"""
        return self.get_preference("interface", "language")
    
    def set_language(self, language: str):
        """Définit la langue"""
        if language in [item.value for item in Language]:
            self.set_preference("interface", "language", language)
        else:
            self.logger.warning(f"Langue invalide: {language}")
    
    def get_shortcuts(self) -> dict[str, dict[str, str]]:
        """Récupère tous les raccourcis clavier"""
        return self.preferences.get("shortcuts", {})
    
    def set_shortcut(self, category: str, action: str, shortcut: str):
        """Définit un raccourci clavier spécifique"""
        self.set_preference("shortcuts", category, {action: shortcut})
    
    def get_window_state(self) -> dict[str, Any]:
        """Récupère l'état de la fenêtre"""
        return self.get_preference("interface", "window_state")
    
    def set_window_state(self, state: dict[str, Any]):
        """Sauvegarde l'état de la fenêtre"""
        for key, value in state.items():
            self.set_preference("interface", "window_state", value, key)
    
    def reset_to_defaults(self):
        """Remet toutes les préférences aux valeurs par défaut"""
        self.preferences = self._default_preferences.copy()
        self.save_preferences()
        self.preferences_reset.emit()
        self.logger.info("Préférences réinitialisées aux valeurs par défaut")
    
    def export_preferences(self, file_path: str) -> bool:
        """Exporte les préférences vers un fichier JSON"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.preferences, f, indent=2, ensure_ascii=False)
            self.logger.info(f"Préférences exportées vers: {file_path}")
            return True
        except Exception as e:
            self.logger.error(f"Erreur lors de l'export des préférences: {e}")
            return False
    
    def import_preferences(self, file_path: str) -> bool:
        """Importe les préférences depuis un fichier JSON"""
        try:
            with open(file_path, encoding='utf-8') as f:
                imported_prefs = json.load(f)
            
            # Valider et fusionner avec les préférences actuelles
            self._merge_preferences(imported_prefs)
            self.save_preferences()
            
            self.logger.info(f"Préférences importées depuis: {file_path}")
            return True
        except Exception as e:
            self.logger.error(f"Erreur lors de l'import des préférences: {e}")
            return False
    
    def _merge_preferences(self, imported_prefs: dict[str, Any]):
        """Fusionne les préférences importées avec les actuelles"""
        for category, settings in imported_prefs.items():
            if category in self._default_preferences:
                if category not in self.preferences:
                    self.preferences[category] = {}
                
                for key, value in settings.items():
                    if key in self._default_preferences[category]:
                        self.preferences[category][key] = value


# Instance globale des préférences
_user_preferences = None


def get_user_preferences() -> UserPreferences:
    """Récupère l'instance globale des préférences utilisateur"""
    global _user_preferences
    if _user_preferences is None:
        _user_preferences = UserPreferences()
    return _user_preferences


def initialize_preferences(app: QApplication = None):
    """Initialise le système de préférences"""
    global _user_preferences
    if _user_preferences is None:
        _user_preferences = UserPreferences(app)
    return _user_preferences
