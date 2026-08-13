#!/usr/bin/env python3
"""
CHNeoWave - Preferences Dialog
Interface de configuration des préférences utilisateur

Auteur: Architecte Logiciel en Chef (ALC)
Date: 2024
Version: 1.0.0
"""

import logging

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QKeySequence
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFontDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QKeySequenceEdit,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSlider,
    QSpinBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from .user_preferences import Language, ThemeMode, get_user_preferences


class PreferencesDialog(QDialog):
    """Dialog de configuration des préférences utilisateur"""
    
    preferences_applied = Signal(dict)  # Émis quand les préférences sont appliquées
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.preferences = get_user_preferences()
        
        self.setWindowTitle("Préférences CHNeoWave")
        self.setModal(True)
        self.setMinimumSize(600, 500)
        self.resize(800, 600)
        
        self._setup_ui()
        self._load_current_preferences()
        self._setup_connections()
    
    def _setup_ui(self):
        """Configure l'interface utilisateur"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)
        
        # Titre
        title_label = QLabel("Préférences")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # Onglets
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Créer les onglets
        self._create_appearance_tab()
        self._create_interface_tab()
        self._create_shortcuts_tab()
        self._create_acquisition_tab()
        self._create_accessibility_tab()
        
        # Boutons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.reset_button = QPushButton("Réinitialiser")
        self.cancel_button = QPushButton("Annuler")
        self.apply_button = QPushButton("Appliquer")
        self.ok_button = QPushButton("OK")
        for button in (self.apply_button, self.ok_button):
            button.setProperty("kind", "primary")
        
        button_layout.addWidget(self.reset_button)
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.apply_button)
        button_layout.addWidget(self.ok_button)
        
        layout.addLayout(button_layout)
    
    def _create_appearance_tab(self):
        """Crée l'onglet Apparence"""
        tab = QWidget()
        scroll = QScrollArea()
        scroll.setWidget(tab)
        scroll.setWidgetResizable(True)
        self.tab_widget.addTab(scroll, "Apparence")
        
        layout = QVBoxLayout(tab)
        layout.setSpacing(16)
        
        # Thème
        theme_group = QGroupBox("Thème")
        theme_layout = QFormLayout(theme_group)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Clair", "Sombre"])
        theme_layout.addRow("Mode:", self.theme_combo)
        
        # Palette certifiée : les rôles sémantiques restent identiques partout.
        colors_layout = QHBoxLayout()
        self.primary_color_button = QPushButton("Action · pétrole")
        colors_layout.addWidget(self.primary_color_button)
        self.secondary_color_button = QPushButton("Mesure · cyan")
        colors_layout.addWidget(self.secondary_color_button)
        self.accent_color_button = QPushButton("Alerte · ambre")
        colors_layout.addWidget(self.accent_color_button)
        for button in (
            self.primary_color_button,
            self.secondary_color_button,
            self.accent_color_button,
        ):
            button.setEnabled(False)
        theme_layout.addRow("Palette:", colors_layout)
        
        layout.addWidget(theme_group)
        
        # Police
        font_group = QGroupBox("Police")
        font_layout = QFormLayout(font_group)
        
        self.font_family_button = QPushButton("Choisir la police")
        self.font_family_button.clicked.connect(self._choose_font)
        font_layout.addRow("Famille:", self.font_family_button)
        
        self.font_size_spinbox = QSpinBox()
        self.font_size_spinbox.setRange(8, 24)
        self.font_size_spinbox.setSuffix(" pt")
        font_layout.addRow("Taille:", self.font_size_spinbox)
        
        layout.addWidget(font_group)
        
        layout.addStretch()
    
    def _create_interface_tab(self):
        """Crée l'onglet Interface"""
        tab = QWidget()
        scroll = QScrollArea()
        scroll.setWidget(tab)
        scroll.setWidgetResizable(True)
        self.tab_widget.addTab(scroll, "Interface")
        
        layout = QVBoxLayout(tab)
        layout.setSpacing(16)
        
        # Langue
        language_group = QGroupBox("Langue")
        language_layout = QFormLayout(language_group)
        
        self.language_combo = QComboBox()
        self.language_combo.addItems(["Français", "English", "Español"])
        language_layout.addRow("Langue:", self.language_combo)
        
        layout.addWidget(language_group)
        
        # Comportement
        behavior_group = QGroupBox("Comportement")
        behavior_layout = QFormLayout(behavior_group)
        
        self.tooltips_checkbox = QCheckBox("Afficher les info-bulles")
        behavior_layout.addRow(self.tooltips_checkbox)
        
        self.animations_checkbox = QCheckBox("Activer les animations")
        behavior_layout.addRow(self.animations_checkbox)
        
        self.compact_mode_checkbox = QCheckBox("Mode compact")
        behavior_layout.addRow(self.compact_mode_checkbox)
        
        layout.addWidget(behavior_group)
        
        # Navigation principale
        sidebar_group = QGroupBox("Navigation")
        sidebar_layout = QFormLayout(sidebar_group)
        
        self.sidebar_width_slider = QSlider(Qt.Horizontal)
        self.sidebar_width_slider.setRange(200, 400)
        self.sidebar_width_slider.setValue(280)
        self.sidebar_width_label = QLabel("280 px")
        self.sidebar_width_slider.valueChanged.connect(
            lambda v: self.sidebar_width_label.setText(f"{v} px")
        )
        self.sidebar_width_slider.hide()
        self.sidebar_width_label.hide()
        
        sidebar_width_layout = QHBoxLayout()
        sidebar_width_layout.addWidget(self.sidebar_width_slider)
        sidebar_width_layout.addWidget(self.sidebar_width_label)
        
        navigation_description = QLabel(
            "Bandeau horizontal permanent : Projets, Système, Calibration, "
            "Acquisition, Analyse et Rapport."
        )
        navigation_description.setWordWrap(True)
        sidebar_layout.addRow("Disposition:", navigation_description)
        
        layout.addWidget(sidebar_group)
        
        layout.addStretch()
    
    def _create_shortcuts_tab(self):
        """Crée l'onglet Raccourcis clavier"""
        tab = QWidget()
        scroll = QScrollArea()
        scroll.setWidget(tab)
        scroll.setWidgetResizable(True)
        self.tab_widget.addTab(scroll, "Raccourcis")
        
        layout = QVBoxLayout(tab)
        layout.setSpacing(16)
        
        # Stockage des widgets de raccourcis
        self.shortcut_widgets = {}
        
        # Raccourcis par catégorie
        categories = {
            "Fichier": "file",
            "Affichage": "view",
            "Acquisition": "acquisition",
            "Analyse": "analysis"
        }
        
        for category_name, category_key in categories.items():
            group = QGroupBox(category_name)
            group_layout = QFormLayout(group)
            
            self.shortcut_widgets[category_key] = {}
            
            # Actions par défaut pour chaque catégorie
            actions = self._get_default_actions(category_key)
            
            for action_key, action_name in actions.items():
                shortcut_edit = QKeySequenceEdit()
                shortcut_edit.setMaximumSequenceLength(1)
                group_layout.addRow(f"{action_name}:", shortcut_edit)
                
                self.shortcut_widgets[category_key][action_key] = shortcut_edit
            
            layout.addWidget(group)
        
        # Bouton de réinitialisation des raccourcis
        reset_shortcuts_button = QPushButton("Réinitialiser les raccourcis")
        reset_shortcuts_button.clicked.connect(self._reset_shortcuts)
        layout.addWidget(reset_shortcuts_button)
        
        layout.addStretch()
    
    def _create_acquisition_tab(self):
        """Crée l'onglet Acquisition"""
        tab = QWidget()
        scroll = QScrollArea()
        scroll.setWidget(tab)
        scroll.setWidgetResizable(True)
        self.tab_widget.addTab(scroll, "Acquisition")
        
        layout = QVBoxLayout(tab)
        layout.setSpacing(16)
        
        # Sauvegarde automatique
        autosave_group = QGroupBox("Sauvegarde automatique")
        autosave_layout = QFormLayout(autosave_group)
        
        self.autosave_checkbox = QCheckBox("Activer la sauvegarde automatique")
        autosave_layout.addRow(self.autosave_checkbox)
        
        self.save_interval_spinbox = QSpinBox()
        self.save_interval_spinbox.setRange(30, 3600)
        self.save_interval_spinbox.setSuffix(" secondes")
        autosave_layout.addRow("Intervalle:", self.save_interval_spinbox)
        
        self.backup_count_spinbox = QSpinBox()
        self.backup_count_spinbox.setRange(1, 20)
        autosave_layout.addRow("Nombre de sauvegardes:", self.backup_count_spinbox)
        
        layout.addWidget(autosave_group)
        
        # Paramètres par défaut
        defaults_group = QGroupBox("Paramètres par défaut")
        defaults_layout = QFormLayout(defaults_group)
        
        self.default_duration_spinbox = QSpinBox()
        self.default_duration_spinbox.setRange(1, 3600)
        self.default_duration_spinbox.setSuffix(" secondes")
        defaults_layout.addRow("Durée d'acquisition:", self.default_duration_spinbox)
        
        self.default_frequency_spinbox = QSpinBox()
        self.default_frequency_spinbox.setRange(1, 10000)
        self.default_frequency_spinbox.setSuffix(" Hz")
        defaults_layout.addRow("Fréquence d'échantillonnage:", self.default_frequency_spinbox)
        
        layout.addWidget(defaults_group)
        
        layout.addStretch()
    
    def _create_accessibility_tab(self):
        """Crée l'onglet Accessibilité"""
        tab = QWidget()
        scroll = QScrollArea()
        scroll.setWidget(tab)
        scroll.setWidgetResizable(True)
        self.tab_widget.addTab(scroll, "Accessibilité")
        
        layout = QVBoxLayout(tab)
        layout.setSpacing(16)
        
        # Options d'accessibilité
        accessibility_group = QGroupBox("Options d'accessibilité")
        accessibility_layout = QFormLayout(accessibility_group)
        
        self.high_contrast_checkbox = QCheckBox("Mode contraste élevé")
        accessibility_layout.addRow(self.high_contrast_checkbox)
        
        self.large_fonts_checkbox = QCheckBox("Grandes polices")
        accessibility_layout.addRow(self.large_fonts_checkbox)
        
        self.screen_reader_checkbox = QCheckBox("Support lecteur d'écran")
        accessibility_layout.addRow(self.screen_reader_checkbox)
        
        self.keyboard_nav_checkbox = QCheckBox("Navigation au clavier")
        accessibility_layout.addRow(self.keyboard_nav_checkbox)
        
        layout.addWidget(accessibility_group)
        
        layout.addStretch()
    
    def _get_default_actions(self, category: str) -> dict[str, str]:
        """Retourne les actions par défaut pour une catégorie"""
        actions = {
            "file": {
                "new_project": "Nouveau projet",
                "open_project": "Ouvrir projet",
                "save_project": "Sauvegarder projet",
                "export_data": "Exporter données",
                "quit": "Quitter"
            },
            "view": {
                "toggle_sidebar": "Afficher les résultats détaillés",
                "fullscreen": "Plein écran",
                "zoom_in": "Zoom avant",
                "zoom_out": "Zoom arrière",
                "reset_zoom": "Réinitialiser zoom"
            },
            "acquisition": {
                "start_acquisition": "Démarrer acquisition",
                "stop_acquisition": "Arrêter acquisition",
                "pause_acquisition": "Pause acquisition",
                "calibrate": "Calibrer"
            },
            "analysis": {
                "run_analysis": "Lancer analyse",
                "export_results": "Exporter résultats",
                "clear_results": "Effacer résultats"
            }
        }
        return actions.get(category, {})
    
    def _setup_connections(self):
        """Configure les connexions des signaux"""
        self.reset_button.clicked.connect(self._reset_preferences)
        self.cancel_button.clicked.connect(self.reject)
        self.apply_button.clicked.connect(self._apply_preferences)
        self.ok_button.clicked.connect(self._ok_clicked)
        
        # Connexions pour aperçu en temps réel
        self.theme_combo.currentTextChanged.connect(self._preview_theme)
    
    def _load_current_preferences(self):
        """Charge les préférences actuelles dans l'interface"""
        # Thème
        theme_mode = self.preferences.get_theme_mode()
        theme_index = {
            ThemeMode.LIGHT.value: 0,
            ThemeMode.DARK.value: 1,
        }.get(theme_mode, 0)
        self.theme_combo.setCurrentIndex(theme_index)
        
        # Police
        font_size = self.preferences.get_preference("theme", "font_size")
        if font_size:
            self.font_size_spinbox.setValue(font_size)
        
        # Interface
        language = self.preferences.get_language()
        language_index = {
            Language.FRENCH.value: 0,
            Language.ENGLISH.value: 1,
            Language.SPANISH.value: 2
        }.get(language, 0)
        self.language_combo.setCurrentIndex(language_index)
        
        # Comportement
        self.tooltips_checkbox.setChecked(
            self.preferences.get_preference("interface", "show_tooltips")
        )
        self.animations_checkbox.setChecked(
            self.preferences.get_preference("interface", "show_animations")
        )
        self.compact_mode_checkbox.setChecked(
            self.preferences.get_preference("interface", "compact_mode")
        )
        
        # Barre latérale
        sidebar_width = self.preferences.get_preference("interface", "sidebar_width")
        if sidebar_width:
            self.sidebar_width_slider.setValue(sidebar_width)
        
        # Raccourcis
        shortcuts = self.preferences.get_shortcuts()
        for category, actions in shortcuts.items():
            if category in self.shortcut_widgets:
                for action, shortcut in actions.items():
                    if action in self.shortcut_widgets[category]:
                        widget = self.shortcut_widgets[category][action]
                        widget.setKeySequence(QKeySequence(shortcut))
        
        # Acquisition
        self.autosave_checkbox.setChecked(
            self.preferences.get_preference("acquisition", "auto_save")
        )
        self.save_interval_spinbox.setValue(
            self.preferences.get_preference("acquisition", "save_interval")
        )
        self.backup_count_spinbox.setValue(
            self.preferences.get_preference("acquisition", "backup_count")
        )
        self.default_duration_spinbox.setValue(
            self.preferences.get_preference("acquisition", "default_duration")
        )
        self.default_frequency_spinbox.setValue(
            self.preferences.get_preference("acquisition", "default_frequency")
        )
        
        # Accessibilité
        self.high_contrast_checkbox.setChecked(
            self.preferences.get_preference("accessibility", "high_contrast")
        )
        self.large_fonts_checkbox.setChecked(
            self.preferences.get_preference("accessibility", "large_fonts")
        )
        self.screen_reader_checkbox.setChecked(
            self.preferences.get_preference("accessibility", "screen_reader")
        )
        self.keyboard_nav_checkbox.setChecked(
            self.preferences.get_preference("accessibility", "keyboard_navigation")
        )
    
    def _choose_font(self):
        """Ouvre un sélecteur de police"""
        current_family = self.preferences.get_preference("theme", "font_family")
        current_size = self.preferences.get_preference("theme", "font_size")
        
        current_font = QFont(current_family, current_size)
        font, ok = QFontDialog.getFont(current_font, self)
        
        if ok:
            self.preferences.set_preference("theme", "font_family", font.family())
            self.preferences.set_preference("theme", "font_size", font.pointSize())
            self.font_size_spinbox.setValue(font.pointSize())
            self.font_family_button.setText(f"{font.family()} {font.pointSize()}pt")
    
    def _preview_theme(self, theme_name: str):
        """Aperçu du thème en temps réel"""
        # Implémentation de l'aperçu en temps réel
        pass
    
    def _reset_shortcuts(self):
        """Réinitialise tous les raccourcis aux valeurs par défaut"""
        reply = QMessageBox.question(
            self, "Réinitialiser les raccourcis",
            "Êtes-vous sûr de vouloir réinitialiser tous les raccourcis aux valeurs par défaut?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Réinitialiser dans les préférences
            default_shortcuts = self.preferences._default_preferences["shortcuts"]
            self.preferences.preferences["shortcuts"] = default_shortcuts.copy()
            
            # Mettre à jour l'interface
            for category, actions in default_shortcuts.items():
                if category in self.shortcut_widgets:
                    for action, shortcut in actions.items():
                        if action in self.shortcut_widgets[category]:
                            widget = self.shortcut_widgets[category][action]
                            widget.setKeySequence(QKeySequence(shortcut))
    
    def _reset_preferences(self):
        """Réinitialise toutes les préférences"""
        reply = QMessageBox.question(
            self, "Réinitialiser les préférences",
            "Êtes-vous sûr de vouloir réinitialiser toutes les préférences aux valeurs par défaut?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.preferences.reset_to_defaults()
            self._load_current_preferences()
    
    def _apply_preferences(self):
        """Applique les préférences sans fermer le dialog"""
        self._save_preferences()
        self.preferences_applied.emit(self.preferences.preferences)
    
    def _ok_clicked(self):
        """Applique les préférences et ferme le dialog"""
        self._save_preferences()
        self.preferences_applied.emit(self.preferences.preferences)
        self.accept()
    
    def _save_preferences(self):
        """Sauvegarde toutes les préférences depuis l'interface"""
        # Thème
        theme_modes = [ThemeMode.LIGHT.value, ThemeMode.DARK.value]
        theme_mode = theme_modes[self.theme_combo.currentIndex()]
        self.preferences.set_theme_mode(theme_mode)
        
        # Police
        self.preferences.set_preference("theme", "font_size", self.font_size_spinbox.value())
        
        # Interface
        languages = [Language.FRENCH.value, Language.ENGLISH.value, Language.SPANISH.value]
        language = languages[self.language_combo.currentIndex()]
        self.preferences.set_language(language)
        
        self.preferences.set_preference("interface", "show_tooltips", self.tooltips_checkbox.isChecked())
        self.preferences.set_preference("interface", "show_animations", self.animations_checkbox.isChecked())
        self.preferences.set_preference("interface", "compact_mode", self.compact_mode_checkbox.isChecked())
        self.preferences.set_preference("interface", "sidebar_width", self.sidebar_width_slider.value())
        
        # Raccourcis
        for category, widgets in self.shortcut_widgets.items():
            for action, widget in widgets.items():
                shortcut = widget.keySequence().toString()
                if shortcut:
                    self.preferences.set_preference("shortcuts", category, {action: shortcut})
        
        # Acquisition
        self.preferences.set_preference("acquisition", "auto_save", self.autosave_checkbox.isChecked())
        self.preferences.set_preference("acquisition", "save_interval", self.save_interval_spinbox.value())
        self.preferences.set_preference("acquisition", "backup_count", self.backup_count_spinbox.value())
        self.preferences.set_preference(
            "acquisition", "default_duration", self.default_duration_spinbox.value()
        )
        self.preferences.set_preference(
            "acquisition", "default_frequency", self.default_frequency_spinbox.value()
        )
        
        # Accessibilité
        self.preferences.set_preference(
            "accessibility", "high_contrast", self.high_contrast_checkbox.isChecked()
        )
        self.preferences.set_preference("accessibility", "large_fonts", self.large_fonts_checkbox.isChecked())
        self.preferences.set_preference(
            "accessibility", "screen_reader", self.screen_reader_checkbox.isChecked()
        )
        self.preferences.set_preference(
            "accessibility", "keyboard_navigation", self.keyboard_nav_checkbox.isChecked()
        )
        
        self.logger.info("Préférences sauvegardées depuis l'interface")
