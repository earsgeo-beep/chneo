"""
Calibration View - Maritime Design System 2025
Vue de calibration unifiée avec design maritime industriel et Golden Ratio
Architecture: Sidebar étapes (20%) + Zone principale (80%) selon spécifications maritimes

Auteur: Architecte Logiciel en Chef - CHNeoWave
Date: 2025-01-28
Version: 3.0.0 Maritime Unified
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QSizePolicy,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from ..styles.maritime_theme import MaritimeTheme
from ..widgets.maritime.kpi_indicator import KPIIndicator
from ..widgets.maritime.maritime_button import MaritimeButton
from ..widgets.maritime.maritime_card import MaritimeCard
from ..widgets.maritime.progress_stepper import ProgressStepper
from ..widgets.maritime.status_beacon import StatusBeacon

# Configuration logger
logger = logging.getLogger(__name__)

# Design System Maritime - Constantes 2025
GOLDEN_RATIO = 1.618
FIBONACCI_SPACES = [8, 13, 21, 34, 55, 89, 144]  # Suite Fibonacci pour espacements

# Palette Maritime Professionnelle
MARITIME_COLORS = {
    'ocean_deep': '#172B35',
    'harbor_blue': '#1A7188',
    'steel_blue': '#145E72',
    'tidal_cyan': '#42B8C6',
    'foam_white': '#FFFFFF',
    'frost_light': '#F3F6F8',
    'storm_gray': '#304A56',
    'slate_gray': '#667C88',
    'coral_alert': '#C54B4B',
    'emerald_success': '#16876C',
    'amber_warning': '#C47B18',
    'azure_info': '#2B8298'
}

class CalibrationStep:
    """Modèle de données pour une étape de calibration"""
    
    def __init__(self, step_id: str, title: str, description: str = "", required: bool = True):
        self.step_id = step_id
        self.title = title
        self.description = description
        self.required = required
        self.status = 'pending'  # pending, active, completed, error, skipped
        self.progress = 0.0
        self.data = {}
        self.validation_errors = []
        
    def is_completed(self) -> bool:
        return self.status == 'completed'
        
    def is_active(self) -> bool:
        return self.status == 'active'
        
    def can_proceed(self) -> bool:
        return self.is_completed() or not self.required

class CalibrationSidebar(QFrame):
    """Sidebar de navigation des étapes de calibration maritime"""
    
    step_selected = Signal(str)  # step_id
    step_status_changed = Signal(str, str)  # step_id, status
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.steps: List[CalibrationStep] = []
        self.current_step_id: Optional[str] = None
        self.setup_ui()
        self.setup_default_steps()
        
    def setup_ui(self):
        """Configure l'interface de la sidebar"""
        self.setObjectName("calibration_sidebar")
        
        # Politique de taille : largeur fixe 20% selon Golden Ratio
        self.setMinimumWidth(280)
        self.setMaximumWidth(350)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # En-tête maritime
        self.create_header(main_layout)
        
        # Zone de défilement pour les étapes
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setFrameStyle(QFrame.Shape.NoFrame)
        
        # Widget conteneur des étapes
        self.steps_container = QWidget()
        self.steps_layout = QVBoxLayout(self.steps_container)
        self.steps_layout.setContentsMargins(MaritimeTheme.SPACE_MD, MaritimeTheme.SPACE_SM, 
                                           MaritimeTheme.SPACE_MD, MaritimeTheme.SPACE_MD)
        self.steps_layout.setSpacing(MaritimeTheme.SPACE_SM)
        
        scroll_area.setWidget(self.steps_container)
        main_layout.addWidget(scroll_area)
        
        # Pied de page avec actions globales
        self.create_footer(main_layout)
        
        # Styles de la sidebar
        self.apply_styles()
        
    def create_header(self, parent_layout):
        """Crée l'en-tête maritime de la sidebar"""
        header = QFrame()
        header.setObjectName("sidebar_header")
        header.setMinimumHeight(62)
        
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(MaritimeTheme.SPACE_MD, MaritimeTheme.SPACE_MD,
                                        MaritimeTheme.SPACE_MD, MaritimeTheme.SPACE_SM)
        header_layout.setSpacing(MaritimeTheme.SPACE_XS)
        
        # Titre principal
        title = QLabel("Calibration")
        title.setObjectName("sidebar_title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Sous-titre
        subtitle = QLabel("Maritime System")
        subtitle.setObjectName("sidebar_subtitle")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Progress stepper global
        self.global_progress = ProgressStepper(
            parent=header,
            steps=["Setup", "Calibrate", "Validate", "Complete"]
        )
        
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        header_layout.addWidget(self.global_progress)
        
        parent_layout.addWidget(header)
        
    def create_footer(self, parent_layout):
        """Crée le pied de page avec actions globales"""
        footer = QFrame()
        footer.setObjectName("sidebar_footer")
        footer.setMinimumHeight(89)  # Fibonacci
        
        footer_layout = QVBoxLayout(footer)
        footer_layout.setContentsMargins(MaritimeTheme.SPACE_MD, MaritimeTheme.SPACE_SM,
                                        MaritimeTheme.SPACE_MD, MaritimeTheme.SPACE_MD)
        footer_layout.setSpacing(MaritimeTheme.SPACE_SM)
        
        # Boutons d'action
        self.save_button = MaritimeButton("Save Progress", variant="secondary")
        self.reset_button = MaritimeButton("Reset All", variant="outline")
        self.export_button = MaritimeButton("Export Config", variant="outline")
        
        footer_layout.addWidget(self.save_button)
        footer_layout.addWidget(self.reset_button)
        footer_layout.addWidget(self.export_button)
        
        parent_layout.addWidget(footer)
        
    def setup_default_steps(self):
        """Configure les étapes par défaut de calibration"""
        default_steps = [
            CalibrationStep("sensor_setup", "Sensor Setup", "Configure sensors and connections"),
            CalibrationStep("zero_calibration", "Zero Calibration", "Set zero reference points"),
            CalibrationStep("span_calibration", "Span Calibration", "Calibrate measurement range"),
            CalibrationStep("linearity_check", "Linearity Check", "Verify linear response"),
            CalibrationStep("validation", "Validation", "Final validation and testing"),
            CalibrationStep("documentation", "Documentation", "Generate calibration report", False)
        ]
        
        for step in default_steps:
            self.add_step(step)
            
        # Activer la première étape
        if self.steps:
            self.set_active_step(self.steps[0].step_id)
            
    def add_step(self, step: CalibrationStep):
        """Ajoute une étape à la sidebar"""
        self.steps.append(step)
        step_widget = self.create_step_widget(step)
        self.steps_layout.addWidget(step_widget)
        
    def create_step_widget(self, step: CalibrationStep) -> QWidget:
        """Crée le widget pour une étape"""
        step_frame = QFrame()
        step_frame.setObjectName(f"step_{step.step_id}")
        step_frame.setMinimumHeight(55)  # Fibonacci
        step_frame.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Layout de l'étape
        step_layout = QHBoxLayout(step_frame)
        step_layout.setContentsMargins(MaritimeTheme.SPACE_SM, MaritimeTheme.SPACE_SM,
                                      MaritimeTheme.SPACE_SM, MaritimeTheme.SPACE_SM)
        step_layout.setSpacing(MaritimeTheme.SPACE_SM)
        
        # Status beacon
        status_beacon = StatusBeacon(
            parent=step_frame,
            status=StatusBeacon.STATUS_PENDING,
            label=""
        )
        
        # Contenu de l'étape
        content_layout = QVBoxLayout()
        content_layout.setSpacing(MaritimeTheme.SPACE_XS)
        
        # Titre de l'étape
        title_label = QLabel(step.title)
        title_label.setObjectName("step_title")
        
        # Description (optionnelle)
        if step.description:
            desc_label = QLabel(step.description)
            desc_label.setObjectName("step_description")
            desc_label.setWordWrap(True)
            content_layout.addWidget(desc_label)
            
        content_layout.addWidget(title_label)
        
        # Assemblage
        step_layout.addWidget(status_beacon)
        step_layout.addLayout(content_layout)
        step_layout.addStretch()
        
        # Événement de clic
        step_frame.mousePressEvent = lambda event, step_id=step.step_id: self.on_step_clicked(step_id)
        
        return step_frame
        
    def on_step_clicked(self, step_id: str):
        """Gère le clic sur une étape"""
        self.set_active_step(step_id)
        self.step_selected.emit(step_id)
        
    def set_active_step(self, step_id: str):
        """Active une étape spécifique"""
        # Désactiver l'étape précédente
        if self.current_step_id:
            prev_step = self.get_step(self.current_step_id)
            if prev_step and prev_step.status == 'active':
                prev_step.status = 'pending'
                
        # Activer la nouvelle étape
        current_step = self.get_step(step_id)
        if current_step:
            current_step.status = 'active'
            self.current_step_id = step_id
            
        # Mettre à jour l'affichage
        self.update_steps_display()
        
    def get_step(self, step_id: str) -> Optional[CalibrationStep]:
        """Récupère une étape par son ID"""
        for step in self.steps:
            if step.step_id == step_id:
                return step
        return None
        
    def update_steps_display(self):
        """Met à jour l'affichage des étapes"""
        # Mise à jour des styles selon le statut
        for i, step in enumerate(self.steps):
            step_widget = self.steps_layout.itemAt(i).widget()
            if step_widget:
                self.update_step_widget_style(step_widget, step)
                
    def update_step_widget_style(self, widget: QWidget, step: CalibrationStep):
        """Met à jour le style d'un widget d'étape"""
        if step.status == 'active':
            widget.setProperty("status", "active")
        elif step.status == 'completed':
            widget.setProperty("status", "completed")
        elif step.status == 'error':
            widget.setProperty("status", "error")
        else:
            widget.setProperty("status", "pending")
            
        widget.style().unpolish(widget)
        widget.style().polish(widget)
        
    def apply_styles(self):
        """Applique les styles maritimes à la sidebar"""
        self.setStyleSheet(f"""
            QFrame#calibration_sidebar {{
                background-color: {MARITIME_COLORS['frost_light']};
                border-right: 2px solid {MARITIME_COLORS['tidal_cyan']};
            }}
            
            QFrame#sidebar_header {{
                background-color: {MARITIME_COLORS['foam_white']};
                border-bottom: 1px solid {MARITIME_COLORS['tidal_cyan']};
            }}
            
            QLabel#sidebar_title {{
                font-size: 18px;
                font-weight: bold;
                color: {MARITIME_COLORS['ocean_deep']};
            }}
            
            QLabel#sidebar_subtitle {{
                font-size: 12px;
                color: {MARITIME_COLORS['slate_gray']};
            }}
            
            QFrame#sidebar_footer {{
                background-color: {MARITIME_COLORS['foam_white']};
                border-top: 1px solid {MARITIME_COLORS['tidal_cyan']};
            }}
            
            /* Styles des étapes */
            QFrame[objectName^="step_"] {{
                background-color: {MARITIME_COLORS['foam_white']};
                border: 1px solid transparent;
                border-radius: 8px;
                margin: 2px;
            }}
            
            QFrame[objectName^="step_"]:hover {{
                background-color: #E3F2FD;
                border-color: {MARITIME_COLORS['tidal_cyan']};
            }}
            
            QFrame[objectName^="step_"][status="active"] {{
                background-color: {MARITIME_COLORS['tidal_cyan']};
                border-color: {MARITIME_COLORS['harbor_blue']};
            }}
            
            QFrame[objectName^="step_"][status="completed"] {{
                background-color: {MARITIME_COLORS['emerald_success']};
                border-color: {MARITIME_COLORS['emerald_success']};
            }}
            
            QFrame[objectName^="step_"][status="error"] {{
                background-color: {MARITIME_COLORS['coral_alert']};
                border-color: {MARITIME_COLORS['coral_alert']};
            }}
            
            QLabel#step_title {{
                font-size: 14px;
                font-weight: 600;
                color: {MARITIME_COLORS['storm_gray']};
            }}
            
            QLabel#step_description {{
                font-size: 11px;
                color: {MARITIME_COLORS['slate_gray']};
            }}
        """)

class CalibrationMainArea(QFrame):
    """Zone principale de calibration maritime (80% largeur)"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_step_id: Optional[str] = None
        self.setup_ui()
        
    def setup_ui(self):
        """Configure l'interface de la zone principale"""
        self.setObjectName("calibration_main_area")
        
        # Politique de taille : zone principale expansive
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(MaritimeTheme.SPACE_MD, MaritimeTheme.SPACE_MD,
                                      MaritimeTheme.SPACE_MD, MaritimeTheme.SPACE_MD)
        main_layout.setSpacing(MaritimeTheme.SPACE_MD)
        
        # En-tête de la zone principale
        self.create_main_header(main_layout)
        
        # Zone de contenu avec stack widget
        self.content_stack = QStackedWidget()
        self.content_stack.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # Créer les pages pour chaque étape
        self.create_step_pages()
        
        main_layout.addWidget(self.content_stack)
        
        # Barre d'actions en bas
        self.create_action_bar(main_layout)
        
        # Styles de la zone principale
        self.apply_styles()
        
    def create_main_header(self, parent_layout):
        """Crée l'en-tête de la zone principale"""
        header = QFrame()
        header.setObjectName("main_header")
        header.setMinimumHeight(89)  # Fibonacci
        
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(MaritimeTheme.SPACE_MD, MaritimeTheme.SPACE_MD,
                                        MaritimeTheme.SPACE_MD, MaritimeTheme.SPACE_MD)
        header_layout.setSpacing(MaritimeTheme.SPACE_MD)
        
        # Titre dynamique
        self.main_title = QLabel("Calibration Setup")
        self.main_title.setObjectName("main_title")
        
        # Status indicator
        self.main_status = StatusBeacon(
            parent=header,
            status=StatusBeacon.STATUS_PENDING,
            label="Ready"
        )
        
        # Spacer
        header_layout.addWidget(self.main_title)
        header_layout.addStretch()
        header_layout.addWidget(self.main_status)
        
        parent_layout.addWidget(header)
        
    def create_step_pages(self):
        """Crée les pages pour chaque étape de calibration"""
        # Page 1: Sensor Setup
        sensor_page = self.create_sensor_setup_page()
        self.content_stack.addWidget(sensor_page)
        
        # Page 2: Zero Calibration
        zero_page = self.create_zero_calibration_page()
        self.content_stack.addWidget(zero_page)
        
        # Page 3: Span Calibration
        span_page = self.create_span_calibration_page()
        self.content_stack.addWidget(span_page)
        
        # Page 4: Linearity Check
        linearity_page = self.create_linearity_check_page()
        self.content_stack.addWidget(linearity_page)
        
        # Page 5: Validation
        validation_page = self.create_validation_page()
        self.content_stack.addWidget(validation_page)
        
        # Page 6: Documentation
        documentation_page = self.create_documentation_page()
        self.content_stack.addWidget(documentation_page)
        
    def create_sensor_setup_page(self) -> QWidget:
        """Crée la page de configuration des capteurs"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(MaritimeTheme.SPACE_MD)
        
        # Titre de la page
        title = QLabel("Sensor Configuration")
        title.setObjectName("page_title")
        layout.addWidget(title)
        
        # Configuration des capteurs dans une carte maritime
        sensor_card = MaritimeCard("Sensor Settings")
        sensor_content = QWidget()
        sensor_layout = QGridLayout(sensor_content)
        sensor_layout.setSpacing(MaritimeTheme.SPACE_SM)
        
        # Champs de configuration
        sensor_layout.addWidget(QLabel("Sensor Type:"), 0, 0)
        sensor_type_combo = QComboBox()
        sensor_type_combo.addItems(["Pressure", "Temperature", "Flow", "Level"])
        sensor_layout.addWidget(sensor_type_combo, 0, 1)
        
        sensor_layout.addWidget(QLabel("Range Min:"), 1, 0)
        range_min_spin = QDoubleSpinBox()
        range_min_spin.setRange(-1000, 1000)
        sensor_layout.addWidget(range_min_spin, 1, 1)
        
        sensor_layout.addWidget(QLabel("Range Max:"), 2, 0)
        range_max_spin = QDoubleSpinBox()
        range_max_spin.setRange(-1000, 1000)
        range_max_spin.setValue(100)
        sensor_layout.addWidget(range_max_spin, 2, 1)
        
        sensor_card.add_content(sensor_content)
        layout.addWidget(sensor_card)
        
        layout.addStretch()
        return page
        
    def create_zero_calibration_page(self) -> QWidget:
        """Crée la page de calibration zéro"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(MaritimeTheme.SPACE_MD)
        
        title = QLabel("Zero Point Calibration")
        title.setObjectName("page_title")
        layout.addWidget(title)
        
        # Instructions
        instructions = QLabel("Set the sensor to zero reference condition and click 'Set Zero'.")
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        # Carte de calibration zéro
        zero_card = MaritimeCard("Zero Calibration")
        zero_content = QWidget()
        zero_layout = QVBoxLayout(zero_content)
        
        # Affichage de la valeur actuelle
        current_value = QLabel("Current Value: 0.000")
        current_value.setObjectName("current_value")
        zero_layout.addWidget(current_value)
        
        # Bouton de calibration
        set_zero_btn = MaritimeButton("Set Zero Point", variant="primary")
        zero_layout.addWidget(set_zero_btn)
        
        zero_card.add_content(zero_content)
        layout.addWidget(zero_card)
        
        layout.addStretch()
        return page
        
    def create_span_calibration_page(self) -> QWidget:
        """Crée la page de calibration d'étendue"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(MaritimeTheme.SPACE_MD)
        
        title = QLabel("Span Calibration")
        title.setObjectName("page_title")
        layout.addWidget(title)
        
        # Carte de calibration d'étendue
        span_card = MaritimeCard("Span Settings")
        span_content = QWidget()
        span_layout = QGridLayout(span_content)
        
        span_layout.addWidget(QLabel("Reference Value:"), 0, 0)
        ref_value_spin = QDoubleSpinBox()
        ref_value_spin.setRange(0, 1000)
        ref_value_spin.setValue(100)
        span_layout.addWidget(ref_value_spin, 0, 1)
        
        span_layout.addWidget(QLabel("Current Reading:"), 1, 0)
        current_reading = QLabel("95.234")
        span_layout.addWidget(current_reading, 1, 1)
        
        set_span_btn = MaritimeButton("Set Span", variant="primary")
        span_layout.addWidget(set_span_btn, 2, 0, 1, 2)
        
        span_card.add_content(span_content)
        layout.addWidget(span_card)
        
        layout.addStretch()
        return page
        
    def create_linearity_check_page(self) -> QWidget:
        """Crée la page de vérification de linéarité"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(MaritimeTheme.SPACE_MD)
        
        title = QLabel("Linearity Verification")
        title.setObjectName("page_title")
        layout.addWidget(title)
        
        # Graphique de linéarité (placeholder)
        linearity_card = MaritimeCard("Linearity Graph")
        linearity_content = QWidget()
        linearity_layout = QVBoxLayout(linearity_content)
        
        # Placeholder pour le graphique
        graph_placeholder = QLabel("[Linearity Graph Placeholder]")
        graph_placeholder.setMinimumHeight(300)
        graph_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        graph_placeholder.setStyleSheet("background-color: #F0F0F0; border: 1px dashed #CCC;")
        linearity_layout.addWidget(graph_placeholder)
        
        # Résultats de linéarité
        results_layout = QGridLayout()
        results_layout.addWidget(QLabel("R² Coefficient:"), 0, 0)
        results_layout.addWidget(QLabel("0.9987"), 0, 1)
        results_layout.addWidget(QLabel("Max Error:"), 1, 0)
        results_layout.addWidget(QLabel("±0.05%"), 1, 1)
        
        linearity_layout.addLayout(results_layout)
        
        linearity_card.add_content(linearity_content)
        layout.addWidget(linearity_card)
        
        layout.addStretch()
        return page
        
    def create_validation_page(self) -> QWidget:
        """Crée la page de validation"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(MaritimeTheme.SPACE_MD)
        
        title = QLabel("Calibration Validation")
        title.setObjectName("page_title")
        layout.addWidget(title)
        
        # Résumé de validation
        validation_card = MaritimeCard("Validation Summary")
        validation_content = QWidget()
        validation_layout = QVBoxLayout(validation_content)
        
        # KPIs de validation
        kpi_layout = QGridLayout()
        
        accuracy_kpi = KPIIndicator("Accuracy", "±0.1%", "success")
        repeatability_kpi = KPIIndicator("Repeatability", "±0.05%", "success")
        stability_kpi = KPIIndicator("Stability", "±0.02%", "success")
        
        kpi_layout.addWidget(accuracy_kpi, 0, 0)
        kpi_layout.addWidget(repeatability_kpi, 0, 1)
        kpi_layout.addWidget(stability_kpi, 0, 2)
        
        validation_layout.addLayout(kpi_layout)
        
        # Bouton de validation finale
        validate_btn = MaritimeButton("Validate Calibration", variant="primary")
        validation_layout.addWidget(validate_btn)
        
        validation_card.add_content(validation_content)
        layout.addWidget(validation_card)
        
        layout.addStretch()
        return page
        
    def create_documentation_page(self) -> QWidget:
        """Crée la page de documentation"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(MaritimeTheme.SPACE_MD)
        
        title = QLabel("Calibration Documentation")
        title.setObjectName("page_title")
        layout.addWidget(title)
        
        # Génération de rapport
        doc_card = MaritimeCard("Report Generation")
        doc_content = QWidget()
        doc_layout = QVBoxLayout(doc_content)
        
        # Options de rapport
        options_layout = QGridLayout()
        options_layout.addWidget(QLabel("Report Format:"), 0, 0)
        format_combo = QComboBox()
        format_combo.addItems(["PDF", "HTML", "CSV"])
        options_layout.addWidget(format_combo, 0, 1)
        
        options_layout.addWidget(QLabel("Include Graphs:"), 1, 0)
        include_graphs = QCheckBox()
        include_graphs.setChecked(True)
        options_layout.addWidget(include_graphs, 1, 1)
        
        doc_layout.addLayout(options_layout)
        
        # Boutons d'action
        actions_layout = QHBoxLayout()
        preview_btn = MaritimeButton("Preview Report", variant="secondary")
        generate_btn = MaritimeButton("Generate Report", variant="primary")
        
        actions_layout.addWidget(preview_btn)
        actions_layout.addWidget(generate_btn)
        doc_layout.addLayout(actions_layout)
        
        doc_card.add_content(doc_content)
        layout.addWidget(doc_card)
        
        layout.addStretch()
        return page
        
    def create_action_bar(self, parent_layout):
        """Crée la barre d'actions en bas"""
        action_bar = QFrame()
        action_bar.setObjectName("action_bar")
        action_bar.setMinimumHeight(55)  # Fibonacci
        
        action_layout = QHBoxLayout(action_bar)
        action_layout.setContentsMargins(MaritimeTheme.SPACE_MD, MaritimeTheme.SPACE_SM,
                                        MaritimeTheme.SPACE_MD, MaritimeTheme.SPACE_SM)
        action_layout.setSpacing(MaritimeTheme.SPACE_SM)
        
        # Boutons de navigation
        self.prev_button = MaritimeButton("← Previous", variant="outline")
        self.next_button = MaritimeButton("Next →", variant="primary")
        self.complete_button = MaritimeButton("Complete Step", variant="secondary")
        
        action_layout.addWidget(self.prev_button)
        action_layout.addStretch()
        action_layout.addWidget(self.complete_button)
        action_layout.addWidget(self.next_button)
        
        parent_layout.addWidget(action_bar)
        
    def show_step(self, step_id: str):
        """Affiche une étape spécifique"""
        step_mapping = {
            "sensor_setup": 0,
            "zero_calibration": 1,
            "span_calibration": 2,
            "linearity_check": 3,
            "validation": 4,
            "documentation": 5
        }
        
        if step_id in step_mapping:
            self.content_stack.setCurrentIndex(step_mapping[step_id])
            self.current_step_id = step_id
            self.update_main_title(step_id)
            
    def update_main_title(self, step_id: str):
        """Met à jour le titre principal selon l'étape"""
        titles = {
            "sensor_setup": "Sensor Configuration",
            "zero_calibration": "Zero Point Calibration",
            "span_calibration": "Span Calibration",
            "linearity_check": "Linearity Verification",
            "validation": "Calibration Validation",
            "documentation": "Documentation & Reports"
        }
        
        if step_id in titles:
            self.main_title.setText(titles[step_id])
            
    def apply_styles(self):
        """Applique les styles maritimes à la zone principale"""
        self.setStyleSheet(f"""
            QFrame#calibration_main_area {{
                background-color: {MARITIME_COLORS['foam_white']};
            }}
            
            QFrame#main_header {{
                background-color: {MARITIME_COLORS['frost_light']};
                border-bottom: 1px solid {MARITIME_COLORS['tidal_cyan']};
                border-radius: 8px 8px 0 0;
            }}
            
            QLabel#main_title {{
                font-size: 24px;
                font-weight: bold;
                color: {MARITIME_COLORS['ocean_deep']};
            }}
            
            QLabel#page_title {{
                font-size: 20px;
                font-weight: 600;
                color: {MARITIME_COLORS['storm_gray']};
    
            }}
            
            QFrame#action_bar {{
                background-color: {MARITIME_COLORS['frost_light']};
                border-top: 1px solid {MARITIME_COLORS['tidal_cyan']};
                border-radius: 0 0 8px 8px;
            }}
            
            QLabel#current_value {{
                font-size: 18px;
                font-weight: bold;
                color: {MARITIME_COLORS['harbor_blue']};
                padding: 8px;
                background-color: {MARITIME_COLORS['frost_light']};
                border-radius: 4px;
            }}
        """)

class CalibrationViewMaritime(QWidget):
    """Vue de calibration maritime unifiée avec design industriel 2025"""
    
    # Signaux
    calibration_started = Signal()
    calibration_completed = Signal(dict)
    step_changed = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_connections()
        
    def setup_ui(self):
        """Configure l'interface principale"""
        self.setObjectName("calibration_view_maritime")
        
        # Layout principal horizontal (Golden Ratio)
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(14)
        
        # Sidebar de navigation (20%)
        self.sidebar = CalibrationSidebar()
        
        # Zone principale (80%)
        self.main_area = CalibrationMainArea()
        
        # Assemblage avec proportions Golden Ratio
        main_layout.addWidget(self.sidebar, 1)  # 20%
        main_layout.addWidget(self.main_area, 4)  # 80% (1:4 ≈ Golden Ratio)
        
        # Styles globaux
        self.apply_global_styles()
        
    def setup_connections(self):
        """Configure les connexions entre composants"""
        # Connexion sidebar → main area
        self.sidebar.step_selected.connect(self.main_area.show_step)
        self.sidebar.step_selected.connect(self.step_changed.emit)
        
        # Connexions des boutons de navigation
        self.main_area.prev_button.clicked.connect(self.go_to_previous_step)
        self.main_area.next_button.clicked.connect(self.go_to_next_step)
        self.main_area.complete_button.clicked.connect(self.complete_current_step)
        
    def go_to_previous_step(self):
        """Navigue vers l'étape précédente"""
        current_index = self.get_current_step_index()
        if current_index > 0:
            prev_step = self.sidebar.steps[current_index - 1]
            self.sidebar.set_active_step(prev_step.step_id)
            self.main_area.show_step(prev_step.step_id)
            
    def go_to_next_step(self):
        """Navigue vers l'étape suivante"""
        current_index = self.get_current_step_index()
        if current_index < len(self.sidebar.steps) - 1:
            next_step = self.sidebar.steps[current_index + 1]
            self.sidebar.set_active_step(next_step.step_id)
            self.main_area.show_step(next_step.step_id)
            
    def complete_current_step(self):
        """Marque l'étape actuelle comme complétée"""
        if self.sidebar.current_step_id:
            current_step = self.sidebar.get_step(self.sidebar.current_step_id)
            if current_step:
                current_step.status = 'completed'
                current_step.progress = 100.0
                self.sidebar.update_steps_display()
                
                # Auto-navigation vers l'étape suivante
                self.go_to_next_step()
                
    def get_current_step_index(self) -> int:
        """Retourne l'index de l'étape actuelle"""
        if self.sidebar.current_step_id:
            for i, step in enumerate(self.sidebar.steps):
                if step.step_id == self.sidebar.current_step_id:
                    return i
        return 0
        
    def apply_global_styles(self):
        """Applique les styles globaux à la vue"""
        self.setStyleSheet(f"""
            QWidget#calibration_view_maritime {{
                background-color: {MARITIME_COLORS['foam_white']};
            }}
        """)
        
    def get_calibration_data(self) -> Dict[str, Any]:
        """Retourne les données de calibration"""
        data = {
            'timestamp': datetime.now().isoformat(),
            'steps': [],
            'completed': False
        }
        
        for step in self.sidebar.steps:
            step_data = {
                'step_id': step.step_id,
                'title': step.title,
                'status': step.status,
                'progress': step.progress,
                'data': step.data
            }
            data['steps'].append(step_data)
            
        # Vérifier si toutes les étapes requises sont complétées
        required_steps = [s for s in self.sidebar.steps if s.required]
        completed_required = [s for s in required_steps if s.is_completed()]
        data['completed'] = len(completed_required) == len(required_steps)
        
        return data
        
    def load_calibration_data(self, data: Dict[str, Any]):
        """Charge des données de calibration"""
        if 'steps' in data:
            for step_data in data['steps']:
                step = self.sidebar.get_step(step_data['step_id'])
                if step:
                    step.status = step_data.get('status', 'pending')
                    step.progress = step_data.get('progress', 0.0)
                    step.data = step_data.get('data', {})
                    
            self.sidebar.update_steps_display()

# Alias pour compatibilité
CalibrationView = CalibrationViewMaritime

if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # Test de la vue de calibration
    calibration_view = CalibrationViewMaritime()
    calibration_view.setWindowTitle("CHNeoWave - Calibration Maritime")
    calibration_view.resize(1200, 800)
    calibration_view.show()
    
    sys.exit(app.exec())
