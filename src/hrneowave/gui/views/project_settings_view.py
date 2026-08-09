# -*- coding: utf-8 -*-
"""
Vue des paramètres de projet CHNeoWave - Interface Moderne
Configuration et gestion des paramètres de projet

Auteur: Architecte Logiciel en Chef (ALC)
Date: 2025-01-26
Version: 1.1.0
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QLineEdit, 
    QSpinBox, QDoubleSpinBox, QComboBox, QCheckBox, QTabWidget, QScrollArea, QFrame, QSlider
)
from PySide6.QtCore import Signal, Qt, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont

# Import des composants modernes
from ..components.modern_card import ModernCard
from ..components.animated_button import AnimatedButton
from ..widgets.kpi_card import KPICard
from ..layouts.golden_ratio_layout import GoldenRatioLayout
from ..styles.maritime_theme import MaritimeTheme


class ProjectSettingsView(QWidget):
    """
    Vue des paramètres de projet moderne pour CHNeoWave
    Utilise le design system avec nombre d'or et thème maritime
    """
    
    # Signaux
    settingsChanged = Signal(dict)  # Paramètres modifiés
    settingsSaved = Signal(dict)    # Paramètres sauvegardés
    settingsReset = Signal()        # Réinitialisation
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Thème maritime
        self.theme = MaritimeTheme()
        
        # Paramètres du projet
        self.project_settings = {}
        self.default_settings = self._get_default_settings()
        
        # Configuration de l'interface
        self._setup_ui()
        self._setup_connections()
        self._apply_theme()
        
        # Animation d'entrée
        self._animate_entrance()
    
    def _setup_ui(self):
        """Configuration de l'interface utilisateur moderne"""
        # Layout principal standard
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(14)
        
        # En-tête
        self._create_header(main_layout)
        
        # Zone de défilement avec onglets
        self._create_tabs_area(main_layout)
        
        # Barre d'actions
        self._create_action_bar(main_layout)
    
    def _create_header(self, layout):
        """Crée l'en-tête avec titre et KPIs"""
        header_frame = QFrame()
        header_frame.setObjectName("operationalHeader")
        header_layout = QHBoxLayout(header_frame)
        
        # Titre et description
        title_layout = QVBoxLayout()
        
        title_label = QLabel("Paramètres du Projet")
        title_label.setObjectName("viewTitle")
        title_font = QFont("Segoe UI", 24, QFont.Bold)
        title_label.setFont(title_font)
        
        subtitle_label = QLabel("Configuration avancée de l'acquisition maritime")
        subtitle_label.setObjectName("mutedText")
        subtitle_font = QFont("Segoe UI", 12)
        subtitle_label.setFont(subtitle_font)
        
        title_layout.addWidget(title_label)
        title_layout.addWidget(subtitle_label)
        title_layout.setSpacing(5)
        
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        
        # KPIs de statut
        self._create_status_kpis(header_layout)
        
        layout.addWidget(header_frame)
    
    def _create_status_kpis(self, layout):
        """Crée les KPIs de statut"""
        kpi_layout = QHBoxLayout()
        kpi_layout.setSpacing(15)
        
        # KPI Paramètres modifiés
        self.modified_kpi = KPICard("Modifiés", "0", "paramètres")
        self.modified_kpi.set_status("normal")
        kpi_layout.addWidget(self.modified_kpi)
        
        # KPI Validation
        self.validation_kpi = KPICard("Validation", "OK", "statut")
        self.validation_kpi.set_status("success")
        kpi_layout.addWidget(self.validation_kpi)
        
        # KPI Dernière sauvegarde
        self.save_kpi = KPICard("Sauvegarde", "Jamais", "dernière")
        self.save_kpi.set_status("warning")
        kpi_layout.addWidget(self.save_kpi)
        
        layout.addLayout(kpi_layout)
    
    def _create_tabs_area(self, layout):
        """Crée la zone d'onglets avec paramètres"""
        # Widget d'onglets
        self.tabs = QTabWidget()
        self.tabs.setObjectName("settingsTabs")
        
        # Onglet Acquisition
        self._create_acquisition_tab()
        
        # Onglet Capteurs
        self._create_sensors_tab()
        
        # Onglet Traitement
        self._create_processing_tab()
        
        # Onglet Export
        self._create_export_tab()
        
        # Onglet Avancé
        self._create_advanced_tab()
        
        layout.addWidget(self.tabs)
    
    def _create_acquisition_tab(self):
        """Crée l'onglet des paramètres d'acquisition"""
        tab_widget = QWidget()
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(20)
        
        # Carte Fréquence d'échantillonnage
        sampling_card = ModernCard("Fréquence d'Échantillonnage")
        sampling_layout = QFormLayout(sampling_card.content_widget)
        
        self.sampling_rate = QSpinBox()
        self.sampling_rate.setRange(1, 10000)
        self.sampling_rate.setValue(1000)
        self.sampling_rate.setSuffix(" Hz")
        self.sampling_rate.setObjectName("modernSpinBox")
        sampling_layout.addRow("Fréquence:", self.sampling_rate)
        
        self.buffer_size = QSpinBox()
        self.buffer_size.setRange(64, 8192)
        self.buffer_size.setValue(1024)
        self.buffer_size.setSuffix(" échantillons")
        self.buffer_size.setObjectName("modernSpinBox")
        sampling_layout.addRow("Taille du buffer:", self.buffer_size)
        
        content_layout.addWidget(sampling_card)
        
        # Carte Durée d'acquisition
        duration_card = ModernCard("Durée d'Acquisition")
        duration_layout = QFormLayout(duration_card.content_widget)
        
        self.acquisition_duration = QSpinBox()
        self.acquisition_duration.setRange(1, 3600)
        self.acquisition_duration.setValue(60)
        self.acquisition_duration.setSuffix(" secondes")
        self.acquisition_duration.setObjectName("modernSpinBox")
        duration_layout.addRow("Durée:", self.acquisition_duration)
        
        self.auto_stop = QCheckBox("Arrêt automatique")
        self.auto_stop.setChecked(True)
        self.auto_stop.setObjectName("modernCheckBox")
        duration_layout.addRow("", self.auto_stop)
        
        content_layout.addWidget(duration_card)
        
        content_layout.addStretch()
        scroll_area.setWidget(content_widget)
        
        tab_layout = QVBoxLayout(tab_widget)
        tab_layout.addWidget(scroll_area)
        
        self.tabs.addTab(tab_widget, "Acquisition")
    
    def _create_sensors_tab(self):
        """Crée l'onglet des paramètres de capteurs"""
        tab_widget = QWidget()
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(20)
        
        # Carte Capteurs actifs
        sensors_card = ModernCard("Capteurs Actifs")
        sensors_layout = QVBoxLayout(sensors_card.content_widget)
        
        self.sensor_pressure = QCheckBox("Capteur de pression")
        self.sensor_pressure.setChecked(True)
        self.sensor_pressure.setObjectName("modernCheckBox")
        sensors_layout.addWidget(self.sensor_pressure)
        
        self.sensor_wave = QCheckBox("Capteur de vagues")
        self.sensor_wave.setChecked(True)
        self.sensor_wave.setObjectName("modernCheckBox")
        sensors_layout.addWidget(self.sensor_wave)
        
        self.sensor_current = QCheckBox("Capteur de courant")
        self.sensor_current.setChecked(False)
        self.sensor_current.setObjectName("modernCheckBox")
        sensors_layout.addWidget(self.sensor_current)
        
        content_layout.addWidget(sensors_card)
        
        # Carte Calibration
        calibration_card = ModernCard("Calibration")
        calibration_layout = QFormLayout(calibration_card.content_widget)
        
        self.calibration_factor = QDoubleSpinBox()
        self.calibration_factor.setRange(0.1, 10.0)
        self.calibration_factor.setValue(1.0)
        self.calibration_factor.setDecimals(3)
        self.calibration_factor.setObjectName("modernDoubleSpinBox")
        calibration_layout.addRow("Facteur de calibration:", self.calibration_factor)
        
        self.offset_correction = QDoubleSpinBox()
        self.offset_correction.setRange(-100.0, 100.0)
        self.offset_correction.setValue(0.0)
        self.offset_correction.setDecimals(2)
        self.offset_correction.setObjectName("modernDoubleSpinBox")
        calibration_layout.addRow("Correction d'offset:", self.offset_correction)
        
        content_layout.addWidget(calibration_card)
        
        content_layout.addStretch()
        scroll_area.setWidget(content_widget)
        
        tab_layout = QVBoxLayout(tab_widget)
        tab_layout.addWidget(scroll_area)
        
        self.tabs.addTab(tab_widget, "Capteurs")
    
    def _create_processing_tab(self):
        """Crée l'onglet des paramètres de traitement"""
        tab_widget = QWidget()
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(20)
        
        # Carte Filtrage
        filter_card = ModernCard("Filtrage des Données")
        filter_layout = QFormLayout(filter_card.content_widget)
        
        self.enable_filter = QCheckBox("Activer le filtrage")
        self.enable_filter.setChecked(True)
        self.enable_filter.setObjectName("modernCheckBox")
        filter_layout.addRow("", self.enable_filter)
        
        self.filter_type = QComboBox()
        self.filter_type.addItems(["Passe-bas", "Passe-haut", "Passe-bande", "Butterworth"])
        self.filter_type.setObjectName("modernComboBox")
        filter_layout.addRow("Type de filtre:", self.filter_type)
        
        self.cutoff_frequency = QDoubleSpinBox()
        self.cutoff_frequency.setRange(0.1, 500.0)
        self.cutoff_frequency.setValue(50.0)
        self.cutoff_frequency.setSuffix(" Hz")
        self.cutoff_frequency.setObjectName("modernDoubleSpinBox")
        filter_layout.addRow("Fréquence de coupure:", self.cutoff_frequency)
        
        content_layout.addWidget(filter_card)
        
        # Carte FFT
        fft_card = ModernCard("Analyse Spectrale (FFT)")
        fft_layout = QFormLayout(fft_card.content_widget)
        
        self.fft_window_size = QComboBox()
        self.fft_window_size.addItems(["512", "1024", "2048", "4096", "8192"])
        self.fft_window_size.setCurrentText("1024")
        self.fft_window_size.setObjectName("modernComboBox")
        fft_layout.addRow("Taille de fenêtre:", self.fft_window_size)
        
        self.fft_overlap = QSlider(Qt.Horizontal)
        self.fft_overlap.setRange(0, 90)
        self.fft_overlap.setValue(50)
        self.fft_overlap.setObjectName("modernSlider")
        fft_layout.addRow("Recouvrement (%):", self.fft_overlap)
        
        content_layout.addWidget(fft_card)
        
        content_layout.addStretch()
        scroll_area.setWidget(content_widget)
        
        tab_layout = QVBoxLayout(tab_widget)
        tab_layout.addWidget(scroll_area)
        
        self.tabs.addTab(tab_widget, "Traitement")
    
    def _create_export_tab(self):
        """Crée l'onglet des paramètres d'export"""
        tab_widget = QWidget()
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(20)
        
        # Carte Format d'export
        export_card = ModernCard("Format d'Export")
        export_layout = QFormLayout(export_card.content_widget)
        
        self.export_format = QComboBox()
        self.export_format.addItems(["CSV", "HDF5", "MAT", "JSON", "Excel"])
        self.export_format.setObjectName("modernComboBox")
        export_layout.addRow("Format:", self.export_format)
        
        self.include_metadata = QCheckBox("Inclure les métadonnées")
        self.include_metadata.setChecked(True)
        self.include_metadata.setObjectName("modernCheckBox")
        export_layout.addRow("", self.include_metadata)
        
        self.compress_data = QCheckBox("Compresser les données")
        self.compress_data.setChecked(False)
        self.compress_data.setObjectName("modernCheckBox")
        export_layout.addRow("", self.compress_data)
        
        content_layout.addWidget(export_card)
        
        # Carte Répertoire de sortie
        output_card = ModernCard("Répertoire de Sortie")
        output_layout = QFormLayout(output_card.content_widget)
        
        self.output_directory = QLineEdit()
        self.output_directory.setPlaceholderText("Chemin du répertoire de sortie")
        self.output_directory.setObjectName("modernInput")
        output_layout.addRow("Répertoire:", self.output_directory)
        
        browse_button = AnimatedButton("Parcourir...")
        browse_button.setObjectName("secondaryButton")
        output_layout.addRow("", browse_button)
        
        content_layout.addWidget(output_card)
        
        content_layout.addStretch()
        scroll_area.setWidget(content_widget)
        
        tab_layout = QVBoxLayout(tab_widget)
        tab_layout.addWidget(scroll_area)
        
        self.tabs.addTab(tab_widget, "Export")
    
    def _create_advanced_tab(self):
        """Crée l'onglet des paramètres avancés"""
        tab_widget = QWidget()
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(20)
        
        # Carte Performance
        perf_card = ModernCard("Performance")
        perf_layout = QFormLayout(perf_card.content_widget)
        
        self.thread_count = QSpinBox()
        self.thread_count.setRange(1, 16)
        self.thread_count.setValue(4)
        self.thread_count.setObjectName("modernSpinBox")
        perf_layout.addRow("Nombre de threads:", self.thread_count)
        
        self.memory_limit = QSpinBox()
        self.memory_limit.setRange(128, 8192)
        self.memory_limit.setValue(1024)
        self.memory_limit.setSuffix(" MB")
        self.memory_limit.setObjectName("modernSpinBox")
        perf_layout.addRow("Limite mémoire:", self.memory_limit)
        
        content_layout.addWidget(perf_card)
        
        # Carte Debug
        debug_card = ModernCard("Débogage")
        debug_layout = QFormLayout(debug_card.content_widget)
        
        self.debug_mode = QCheckBox("Mode débogage")
        self.debug_mode.setChecked(False)
        self.debug_mode.setObjectName("modernCheckBox")
        debug_layout.addRow("", self.debug_mode)
        
        self.log_level = QComboBox()
        self.log_level.addItems(["ERROR", "WARNING", "INFO", "DEBUG"])
        self.log_level.setCurrentText("INFO")
        self.log_level.setObjectName("modernComboBox")
        debug_layout.addRow("Niveau de log:", self.log_level)
        
        content_layout.addWidget(debug_card)
        
        content_layout.addStretch()
        scroll_area.setWidget(content_widget)
        
        tab_layout = QVBoxLayout(tab_widget)
        tab_layout.addWidget(scroll_area)
        
        self.tabs.addTab(tab_widget, "Avancé")
    
    def _create_action_bar(self, layout):
        """Crée la barre d'actions"""
        action_frame = QFrame()
        action_frame.setObjectName("surface")
        action_layout = QHBoxLayout(action_frame)
        action_layout.setSpacing(15)
        
        # Bouton de réinitialisation
        self.reset_button = AnimatedButton("Réinitialiser")
        self.reset_button.setObjectName("warningButton")
        self.reset_button.setProperty("kind", "danger")
        action_layout.addWidget(self.reset_button)
        
        # Espacement
        action_layout.addStretch()
        
        # Indicateur de modifications
        self.changes_indicator = QLabel("Aucune modification")
        self.changes_indicator.setObjectName("changesIndicator")
        action_layout.addWidget(self.changes_indicator)
        
        # Bouton d'annulation
        self.cancel_button = AnimatedButton("Annuler")
        self.cancel_button.setObjectName("secondaryButton")
        self.cancel_button.setProperty("kind", "secondary")
        action_layout.addWidget(self.cancel_button)
        
        # Bouton de sauvegarde
        self.save_button = AnimatedButton("Sauvegarder")
        self.save_button.setObjectName("primaryButton")
        self.save_button.setProperty("kind", "primaryLarge")
        self.save_button.setEnabled(False)
        action_layout.addWidget(self.save_button)
        
        layout.addWidget(action_frame)
    
    def _setup_connections(self):
        """Configuration des connexions de signaux"""
        # Boutons d'action - connexion sécurisée
        try:
            if hasattr(self, 'save_button') and self.save_button is not None:
                self.save_button.clicked.connect(self._save_settings)
        except RuntimeError:
            pass  # Signal source deleted
            
        try:
            if hasattr(self, 'reset_button') and self.reset_button is not None:
                self.reset_button.clicked.connect(self._reset_settings)
        except RuntimeError:
            pass  # Signal source deleted
            
        try:
            if hasattr(self, 'cancel_button') and self.cancel_button is not None:
                self.cancel_button.clicked.connect(self._cancel_changes)
        except RuntimeError:
            pass  # Signal source deleted
        
        # Surveillance des modifications
        self._connect_change_signals()
    
    def _connect_change_signals(self):
        """Connecte les signaux de modification"""
        # Acquisition
        self.sampling_rate.valueChanged.connect(self._on_settings_changed)
        self.buffer_size.valueChanged.connect(self._on_settings_changed)
        self.acquisition_duration.valueChanged.connect(self._on_settings_changed)
        self.auto_stop.toggled.connect(self._on_settings_changed)
        
        # Capteurs
        self.sensor_pressure.toggled.connect(self._on_settings_changed)
        self.sensor_wave.toggled.connect(self._on_settings_changed)
        self.sensor_current.toggled.connect(self._on_settings_changed)
        self.calibration_factor.valueChanged.connect(self._on_settings_changed)
        self.offset_correction.valueChanged.connect(self._on_settings_changed)
        
        # Traitement
        self.enable_filter.toggled.connect(self._on_settings_changed)
        self.filter_type.currentTextChanged.connect(self._on_settings_changed)
        self.cutoff_frequency.valueChanged.connect(self._on_settings_changed)
        self.fft_window_size.currentTextChanged.connect(self._on_settings_changed)
        self.fft_overlap.valueChanged.connect(self._on_settings_changed)
        
        # Export
        self.export_format.currentTextChanged.connect(self._on_settings_changed)
        self.include_metadata.toggled.connect(self._on_settings_changed)
        self.compress_data.toggled.connect(self._on_settings_changed)
        self.output_directory.textChanged.connect(self._on_settings_changed)
        
        # Avancé
        self.thread_count.valueChanged.connect(self._on_settings_changed)
        self.memory_limit.valueChanged.connect(self._on_settings_changed)
        self.debug_mode.toggled.connect(self._on_settings_changed)
        self.log_level.currentTextChanged.connect(self._on_settings_changed)
    
    def _apply_theme(self):
        """Applique le thème maritime moderne"""
        # La palette de production est centralisée dans ThemeManager.
        self.setStyleSheet("")
        return
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {self.theme.colors['background']};
                color: {self.theme.colors['on_surface']};
                font-family: 'Segoe UI', sans-serif;
            }}
            
            #settingsHeader {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {self.theme.colors['primary']},
                    stop:1 {self.theme.colors['secondary']});
                border-radius: 15px;
                padding: 25px;
                margin-bottom: 15px;
            }}
            
            #settingsTitle {{
                color: white;
                font-weight: bold;
            }}
            
            #settingsSubtitle {{
                color: rgba(255, 255, 255, 0.8);
                font-style: italic;
            }}
            
            #settingsTabs {{
                background-color: {self.theme.colors['surface']};
                border-radius: 10px;
            }}
            
            #settingsTabs::pane {{
                border: 2px solid {self.theme.colors['border']};
                border-radius: 10px;
                background-color: {self.theme.colors['background']};
            }}
            
            #settingsTabs::tab-bar {{
                alignment: center;
            }}
            
            QTabBar::tab {{
                background-color: {self.theme.colors['surface']};
                color: {self.theme.colors['on_surface']};
                padding: 12px 20px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                min-width: 100px;
            }}
            
            QTabBar::tab:selected {{
                background-color: {self.theme.colors['primary']};
                color: white;
            }}
            
            QTabBar::tab:hover {{
                background-color: {self.theme.colors['surface_variant']};
            }}
            
            #modernSpinBox, #modernDoubleSpinBox {{
                background-color: {self.theme.colors['surface']};
                border: 2px solid {self.theme.colors['border']};
                border-radius: 6px;
                padding: 8px;
                font-size: 13px;
                min-height: 20px;
            }}
            
            #modernSpinBox:focus, #modernDoubleSpinBox:focus {{
                border-color: {self.theme.colors['primary']};
            }}
            
            #modernComboBox {{
                background-color: {self.theme.colors['surface']};
                border: 2px solid {self.theme.colors['border']};
                border-radius: 6px;
                padding: 8px;
                font-size: 13px;
                min-height: 20px;
            }}
            
            #modernComboBox:focus {{
                border-color: {self.theme.colors['primary']};
            }}
            
            #modernComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            
            #modernCheckBox {{
                font-size: 13px;
                spacing: 8px;
            }}
            
            #modernCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border-radius: 3px;
                border: 2px solid {self.theme.colors['border']};
                background-color: {self.theme.colors['surface']};
            }}
            
            #modernCheckBox::indicator:checked {{
                background-color: {self.theme.colors['primary']};
                border-color: {self.theme.colors['primary']};
            }}
            
            #modernSlider::groove:horizontal {{
                height: 6px;
                background-color: {self.theme.colors['border']};
                border-radius: 3px;
            }}
            
            #modernSlider::handle:horizontal {{
                background-color: {self.theme.colors['primary']};
                width: 18px;
                height: 18px;
                border-radius: 9px;
                margin: -6px 0;
            }}
            
            #modernInput {{
                background-color: {self.theme.colors['surface']};
                border: 2px solid {self.theme.colors['border']};
                border-radius: 6px;
                padding: 8px;
                font-size: 13px;
                min-height: 20px;
            }}
            
            #modernInput:focus {{
                border-color: {self.theme.colors['primary']};
            }}
            
            #actionBar {{
                background-color: {self.theme.colors['surface']};
                border-radius: 10px;
                padding: 20px;
                border: 1px solid {self.theme.colors['border']};
            }}
            
            #primaryButton {{
                background-color: {self.theme.colors['primary']};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 25px;
                font-weight: bold;
                font-size: 13px;
                min-width: 120px;
            }}
            
            #primaryButton:hover {{
                background-color: {self.theme.colors['primary_dark']};
            }}
            
            #primaryButton:disabled {{
                background-color: {self.theme.colors['surface_dim']};
                color: {self.theme.colors['on_surface_variant']};
            }}
            
            #secondaryButton {{
                background-color: {self.theme.colors['surface']};
                color: {self.theme.colors['on_surface']};
                border: 2px solid {self.theme.colors['border']};
                border-radius: 8px;
                padding: 12px 25px;
                font-size: 13px;
                min-width: 120px;
            }}
            
            #secondaryButton:hover {{
                background-color: {self.theme.colors['surface_variant']};
                border-color: {self.theme.colors['primary']};
            }}
            
            #warningButton {{
                background-color: {self.theme.colors['warning']};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 25px;
                font-weight: bold;
                font-size: 13px;
                min-width: 120px;
            }}
            
            #warningButton:hover {{
                background-color: {self.theme.colors['accent_dark']};
            }}
            
            #changesIndicator {{
                color: {self.theme.colors['on_surface_variant']};
                font-size: 12px;
                font-style: italic;
            }}
        """)
    
    def _get_default_settings(self):
        """Retourne les paramètres par défaut"""
        return {
            # Acquisition
            'sampling_rate': 1000,
            'buffer_size': 1024,
            'acquisition_duration': 60,
            'auto_stop': True,
            
            # Capteurs
            'sensor_pressure': True,
            'sensor_wave': True,
            'sensor_current': False,
            'calibration_factor': 1.0,
            'offset_correction': 0.0,
            
            # Traitement
            'enable_filter': True,
            'filter_type': 'Passe-bas',
            'cutoff_frequency': 50.0,
            'fft_window_size': '1024',
            'fft_overlap': 50,
            
            # Export
            'export_format': 'CSV',
            'include_metadata': True,
            'compress_data': False,
            'output_directory': '',
            
            # Avancé
            'thread_count': 4,
            'memory_limit': 1024,
            'debug_mode': False,
            'log_level': 'INFO'
        }
    
    def _on_settings_changed(self):
        """Gère les modifications de paramètres"""
        # Compter les modifications
        current_settings = self._get_current_settings()
        changes = 0
        
        for key, value in current_settings.items():
            if key in self.default_settings and self.default_settings[key] != value:
                changes += 1
        
        # Mettre à jour les KPIs
        self.modified_kpi.update_value(str(changes))
        if changes > 0:
            self.modified_kpi.set_status("warning")
            self.save_button.setEnabled(True)
            self.changes_indicator.setText(f"{changes} modification(s) en attente")
        else:
            self.modified_kpi.set_status("normal")
            self.save_button.setEnabled(False)
            self.changes_indicator.setText("Aucune modification")
        
        # Émettre le signal
        self.settingsChanged.emit(current_settings)
    
    def _get_current_settings(self):
        """Récupère les paramètres actuels"""
        return {
            # Acquisition
            'sampling_rate': self.sampling_rate.value(),
            'buffer_size': self.buffer_size.value(),
            'acquisition_duration': self.acquisition_duration.value(),
            'auto_stop': self.auto_stop.isChecked(),
            
            # Capteurs
            'sensor_pressure': self.sensor_pressure.isChecked(),
            'sensor_wave': self.sensor_wave.isChecked(),
            'sensor_current': self.sensor_current.isChecked(),
            'calibration_factor': self.calibration_factor.value(),
            'offset_correction': self.offset_correction.value(),
            
            # Traitement
            'enable_filter': self.enable_filter.isChecked(),
            'filter_type': self.filter_type.currentText(),
            'cutoff_frequency': self.cutoff_frequency.value(),
            'fft_window_size': self.fft_window_size.currentText(),
            'fft_overlap': self.fft_overlap.value(),
            
            # Export
            'export_format': self.export_format.currentText(),
            'include_metadata': self.include_metadata.isChecked(),
            'compress_data': self.compress_data.isChecked(),
            'output_directory': self.output_directory.text(),
            
            # Avancé
            'thread_count': self.thread_count.value(),
            'memory_limit': self.memory_limit.value(),
            'debug_mode': self.debug_mode.isChecked(),
            'log_level': self.log_level.currentText()
        }
    
    def _save_settings(self):
        """Sauvegarde les paramètres"""
        self.project_settings = self._get_current_settings()
        
        # Mettre à jour les KPIs
        self.save_kpi.update_value("Maintenant")
        self.save_kpi.set_status("success")
        self.modified_kpi.update_value("0")
        self.modified_kpi.set_status("normal")
        
        self.save_button.setEnabled(False)
        self.changes_indicator.setText("Paramètres sauvegardés")
        
        # Émettre le signal
        self.settingsSaved.emit(self.project_settings)
    
    def _reset_settings(self):
        """Réinitialise les paramètres"""
        self._load_settings(self.default_settings)
        self.settingsReset.emit()
    
    def _cancel_changes(self):
        """Annule les modifications"""
        if self.project_settings:
            self._load_settings(self.project_settings)
        else:
            self._load_settings(self.default_settings)
    
    def _load_settings(self, settings):
        """Charge les paramètres dans l'interface"""
        # Acquisition
        self.sampling_rate.setValue(settings.get('sampling_rate', 1000))
        self.buffer_size.setValue(settings.get('buffer_size', 1024))
        self.acquisition_duration.setValue(settings.get('acquisition_duration', 60))
        self.auto_stop.setChecked(settings.get('auto_stop', True))
        
        # Capteurs
        self.sensor_pressure.setChecked(settings.get('sensor_pressure', True))
        self.sensor_wave.setChecked(settings.get('sensor_wave', True))
        self.sensor_current.setChecked(settings.get('sensor_current', False))
        self.calibration_factor.setValue(settings.get('calibration_factor', 1.0))
        self.offset_correction.setValue(settings.get('offset_correction', 0.0))
        
        # Traitement
        self.enable_filter.setChecked(settings.get('enable_filter', True))
        self.filter_type.setCurrentText(settings.get('filter_type', 'Passe-bas'))
        self.cutoff_frequency.setValue(settings.get('cutoff_frequency', 50.0))
        self.fft_window_size.setCurrentText(settings.get('fft_window_size', '1024'))
        self.fft_overlap.setValue(settings.get('fft_overlap', 50))
        
        # Export
        self.export_format.setCurrentText(settings.get('export_format', 'CSV'))
        self.include_metadata.setChecked(settings.get('include_metadata', True))
        self.compress_data.setChecked(settings.get('compress_data', False))
        self.output_directory.setText(settings.get('output_directory', ''))
        
        # Avancé
        self.thread_count.setValue(settings.get('thread_count', 4))
        self.memory_limit.setValue(settings.get('memory_limit', 1024))
        self.debug_mode.setChecked(settings.get('debug_mode', False))
        self.log_level.setCurrentText(settings.get('log_level', 'INFO'))
    
    def _animate_entrance(self):
        """Animation d'entrée de la vue"""
        self.setProperty("opacity", 0.0)
        
        self.fade_animation = QPropertyAnimation(self, b"opacity")
        self.fade_animation.setDuration(600)
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)
        self.fade_animation.setEasingCurve(QEasingCurve.OutCubic)
        self.fade_animation.start()
    
    def load_project_settings(self, settings):
        """Charge les paramètres d'un projet"""
        self.project_settings = settings
        self._load_settings(settings)
    
    def get_project_settings(self):
        """Retourne les paramètres du projet"""
        return self.project_settings
    
    def validate_settings(self):
        """Valide les paramètres actuels"""
        current = self._get_current_settings()
        
        # Validation basique
        if current['sampling_rate'] <= 0:
            self.validation_kpi.update_value("Erreur")
            self.validation_kpi.set_status("error")
            return False
        
        if current['buffer_size'] <= 0:
            self.validation_kpi.update_value("Erreur")
            self.validation_kpi.set_status("error")
            return False
        
        self.validation_kpi.update_value("OK")
        self.validation_kpi.set_status("success")
        return True
