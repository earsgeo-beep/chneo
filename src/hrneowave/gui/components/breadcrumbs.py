"""Breadcrumbs Navigation Component for CHNeoWave

Composant de navigation en fil d'Ariane pour améliorer l'UX
du workflow d'acquisition et d'analyse.
"""

import logging
from typing import List, Optional, Dict, Any
from enum import Enum

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QPushButton, 
    QFrame, QSizePolicy, QSpacerItem
)
from PySide6.QtCore import (
    Qt, Signal, QPropertyAnimation, QEasingCurve,
    QParallelAnimationGroup, QRect
)
from PySide6.QtGui import QFont, QPainter, QPainterPath, QColor

from .material.theme import MaterialTheme, MaterialColor


class WorkflowStep(Enum):
    """Étapes du workflow CHNeoWave"""
    WELCOME = "welcome"
    PROJECT = "project"
    CALIBRATION = "calibration"
    ACQUISITION = "acquisition"
    ANALYSIS = "analysis"
    EXPORT = "export"


class BreadcrumbStep:
    """Représente une étape dans le breadcrumb"""
    
    def __init__(self, 
                 step: WorkflowStep,
                 title: str,
                 view_name: str,
                 is_completed: bool = False,
                 is_current: bool = False,
                 is_accessible: bool = True):
        self.step = step
        self.title = title
        self.view_name = view_name
        self.is_completed = is_completed
        self.is_current = is_current
        self.is_accessible = is_accessible
    
    def __repr__(self):
        return f"BreadcrumbStep({self.step.value}, {self.title}, completed={self.is_completed})"


class BreadcrumbButton(QPushButton):
    """Bouton personnalisé pour les étapes du breadcrumb"""
    
    # Signal émis quand l'étape est cliquée
    step_clicked = Signal(WorkflowStep)
    
    def __init__(self, step: BreadcrumbStep, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self.step_data = step
        self.logger = logging.getLogger(__name__)
        
        # Configuration du bouton
        self.setText(step.title)
        self.setEnabled(step.is_accessible)
        self.setCursor(Qt.PointingHandCursor if step.is_accessible else Qt.ForbiddenCursor)
        
        # Connecter le signal
        self.clicked.connect(lambda: self.step_clicked.emit(step.step))
        
        # Appliquer le style
        self._apply_style()
        
        # Animation au survol
        self._setup_hover_animation()
    
    def _apply_style(self):
        """Applique le style Material Design selon l'état"""
        theme = MaterialTheme.get_current_theme()
        
        if self.step_data.is_current:
            # Étape actuelle - style primaire
            bg_color = theme.primary
            text_color = theme.on_primary
            border_color = theme.primary
        elif self.step_data.is_completed:
            # Étape complétée - style tertiaire
            bg_color = theme.tertiary_container
            text_color = theme.on_tertiary_container
            border_color = theme.tertiary
        elif self.step_data.is_accessible:
            # Étape accessible - style surface
            bg_color = theme.surface_variant
            text_color = theme.on_surface_variant
            border_color = theme.outline
        else:
            # Étape non accessible - style désactivé
            bg_color = theme.surface
            text_color = theme.on_surface
            border_color = theme.outline_variant
        
        style = f"""
        QPushButton {{
            background-color: {bg_color};
            color: {text_color};
            border: 2px solid {border_color};
            border-radius: 12px;
            padding: 8px 16px;
            font-size: 14px;
            font-weight: bold;
            min-width: 80px;
        }}
        
        QPushButton:hover:enabled {{
            background-color: {self._lighten_color(bg_color)};
            border-color: {theme.primary};
        }}
        
        QPushButton:pressed:enabled {{
            background-color: {self._darken_color(bg_color)};
        }}
        
        QPushButton:disabled {{
            opacity: 0.6;
        }}
        """
        
        self.setStyleSheet(style)
    
    def _lighten_color(self, color: str) -> str:
        """Éclaircit une couleur pour l'effet hover"""
        # Conversion simple - dans un vrai projet, utiliser QColor
        if color.startswith('#'):
            return color  # Retourner la même couleur pour simplifier
        return color
    
    def _darken_color(self, color: str) -> str:
        """Assombrit une couleur pour l'effet pressed"""
        # Conversion simple - dans un vrai projet, utiliser QColor
        if color.startswith('#'):
            return color  # Retourner la même couleur pour simplifier
        return color
    
    def _setup_hover_animation(self):
        """Configure l'animation au survol"""
        # Animation d'élévation réservée à une évolution ultérieure.
        pass
    
    def update_step_state(self, 
                         is_completed: bool = None,
                         is_current: bool = None,
                         is_accessible: bool = None):
        """Met à jour l'état de l'étape"""
        if is_completed is not None:
            self.step_data.is_completed = is_completed
        
        if is_current is not None:
            self.step_data.is_current = is_current
        
        if is_accessible is not None:
            self.step_data.is_accessible = is_accessible
            self.setEnabled(is_accessible)
        
        # Réappliquer le style
        self._apply_style()


class BreadcrumbSeparator(QLabel):
    """Séparateur entre les étapes du breadcrumb"""
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        # Icône de séparation Material Design
        self.setText("›")
        self.setAlignment(Qt.AlignCenter)
        
        # Style
        theme = MaterialTheme.get_current_theme()
        style = f"""
        QLabel {{
            color: {theme.outline};
            font-size: 16px;
            font-weight: bold;
            margin: 0px 8px;
        }}
        """
        self.setStyleSheet(style)
        self.setFixedSize(20, 32)


class BreadcrumbsWidget(QWidget):
    """Widget de navigation breadcrumbs pour CHNeoWave"""
    
    # Signal émis quand une étape est sélectionnée
    step_selected = Signal(WorkflowStep, str)  # step, view_name
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self.logger = logging.getLogger(__name__)
        self.steps: List[BreadcrumbStep] = []
        self.step_buttons: Dict[WorkflowStep, BreadcrumbButton] = {}
        
        # Configuration du widget
        self.setFixedHeight(50)
        self_policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.setSizePolicy(self_policy)
        
        # Layout principal
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(16, 8, 16, 8)
        self.layout.setSpacing(0)
        
        # Initialiser les étapes par défaut
        self._initialize_default_steps()
        
        # Construire l'interface
        self._build_breadcrumbs()
        
        # Style du container
        self._apply_container_style()
    
    def _initialize_default_steps(self):
        """Initialise les étapes par défaut du workflow"""
        default_steps = [
            BreadcrumbStep(
                WorkflowStep.WELCOME,
                "Accueil",
                "WelcomeView",
                is_completed=False,
                is_current=True,
                is_accessible=True
            ),
            BreadcrumbStep(
                WorkflowStep.PROJECT,
                "Projet",
                "DashboardViewGolden",
                is_completed=False,
                is_current=False,
                is_accessible=False
            ),
            BreadcrumbStep(
                WorkflowStep.CALIBRATION,
                "Calibration",
                "CalibrationView",
                is_completed=False,
                is_current=False,
                is_accessible=False
            ),
            BreadcrumbStep(
                WorkflowStep.ACQUISITION,
                "Acquisition",
                "AcquisitionView",
                is_completed=False,
                is_current=False,
                is_accessible=False
            ),
            BreadcrumbStep(
                WorkflowStep.ANALYSIS,
                "Analyse",
                "AnalysisView",
                is_completed=False,
                is_current=False,
                is_accessible=False
            ),
            BreadcrumbStep(
                WorkflowStep.EXPORT,
                "Export",
                "ExportView",
                is_completed=False,
                is_current=False,
                is_accessible=False
            )
        ]
        
        self.steps = default_steps
    
    def _build_breadcrumbs(self):
        """Construit l'interface des breadcrumbs"""
        # Nettoyer le layout existant
        self._clear_layout()
        
        for i, step in enumerate(self.steps):
            # Créer le bouton pour l'étape
            button = BreadcrumbButton(step, self)
            button.step_clicked.connect(self._on_step_clicked)
            
            # Stocker la référence
            self.step_buttons[step.step] = button
            
            # Ajouter au layout
            self.layout.addWidget(button)
            
            # Ajouter un séparateur (sauf pour la dernière étape)
            if i < len(self.steps) - 1:
                separator = BreadcrumbSeparator(self)
                self.layout.addWidget(separator)
        
        # Spacer pour pousser vers la gauche
        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.layout.addItem(spacer)
    
    def _clear_layout(self):
        """Nettoie le layout existant"""
        while self.layout.count():
            child = self.layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
    
    def _apply_container_style(self):
        """Applique le style du container"""
        theme = MaterialTheme.get_current_theme()
        
        style = f"""
        BreadcrumbsWidget {{
            background-color: {theme.surface};
            border-bottom: 1px solid {theme.outline_variant};
        }}
        """
        
        self.setStyleSheet(style)
    
    def _on_step_clicked(self, step: WorkflowStep):
        """Gestionnaire de clic sur une étape"""
        step_data = next((s for s in self.steps if s.step == step), None)
        if step_data and step_data.is_accessible:
            self.step_selected.emit(step, step_data.view_name)
            self.logger.info(f"Étape sélectionnée: {step.value} -> {step_data.view_name}")
    
    def set_current_step(self, step: WorkflowStep):
        """Définit l'étape actuelle"""
        # Réinitialiser tous les états 'current'
        for s in self.steps:
            s.is_current = False
        
        # Définir la nouvelle étape actuelle
        current_step = next((s for s in self.steps if s.step == step), None)
        if current_step:
            current_step.is_current = True
            
            # Mettre à jour les boutons
            for step_enum, button in self.step_buttons.items():
                button.update_step_state(is_current=(step_enum == step))
            
            self.logger.info(f"Étape actuelle mise à jour: {step.value}")
    
    def mark_step_completed(self, step: WorkflowStep):
        """Marque une étape comme complétée"""
        step_data = next((s for s in self.steps if s.step == step), None)
        if step_data:
            step_data.is_completed = True
            
            # Mettre à jour le bouton
            if step in self.step_buttons:
                self.step_buttons[step].update_step_state(is_completed=True)
            
            # Rendre accessible l'étape suivante
            self._unlock_next_step(step)
            
            self.logger.info(f"Étape marquée comme complétée: {step.value}")
    
    def _unlock_next_step(self, completed_step: WorkflowStep):
        """Déverrouille l'étape suivante après completion"""
        step_order = list(WorkflowStep)
        
        try:
            current_index = step_order.index(completed_step)
            if current_index + 1 < len(step_order):
                next_step = step_order[current_index + 1]
                
                # Trouver et déverrouiller l'étape suivante
                next_step_data = next((s for s in self.steps if s.step == next_step), None)
                if next_step_data:
                    next_step_data.is_accessible = True
                    
                    # Mettre à jour le bouton
                    if next_step in self.step_buttons:
                        self.step_buttons[next_step].update_step_state(is_accessible=True)
                    
                    self.logger.info(f"Étape suivante déverrouillée: {next_step.value}")
        
        except ValueError:
            self.logger.warning(f"Étape inconnue: {completed_step}")
    
    def reset_workflow(self):
        """Remet à zéro le workflow"""
        # Réinitialiser tous les états
        for step in self.steps:
            step.is_completed = False
            step.is_current = False
            step.is_accessible = (step.step == WorkflowStep.WELCOME)
        
        # Définir l'accueil comme étape actuelle
        self.steps[0].is_current = True
        
        # Reconstruire l'interface
        self._build_breadcrumbs()
        
        self.logger.info("Workflow réinitialisé")
    
    def get_current_step(self) -> Optional[WorkflowStep]:
        """Retourne l'étape actuelle"""
        current = next((s for s in self.steps if s.is_current), None)
        return current.step if current else None
    
    def get_completed_steps(self) -> List[WorkflowStep]:
        """Retourne la liste des étapes complétées"""
        return [s.step for s in self.steps if s.is_completed]
    
    def is_step_accessible(self, step: WorkflowStep) -> bool:
        """Vérifie si une étape est accessible"""
        step_data = next((s for s in self.steps if s.step == step), None)
        return step_data.is_accessible if step_data else False
