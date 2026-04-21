#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fenetre principale de CHNeoWave."""

import logging
from pathlib import Path
from typing import Dict, Optional

from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QMainWindow,
    QSplitter,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from hrneowave.core.project_manager import get_project_manager

from .components.breadcrumbs import BreadcrumbsWidget, WorkflowStep
from .components.help_system import HelpPanel, install_help_on_widget
from .components.notification_system import show_error, show_info, show_success
from .components.status_indicators import StatusLevel, SystemStatusWidget
from .preferences import get_user_preferences
from .view_manager import ViewManager
from .views import DashboardViewMaritime, VIEWS_CONFIG, WelcomeView
from .widgets.main_sidebar import MainSidebar

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Fenetre principale de l'application."""

    projectCreated = Signal()

    def __init__(self, config=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("CHNeoWave")
        self.setMinimumSize(1024, 768)

        self.config = config or {}
        self.user_preferences = get_user_preferences()
        self.project_manager = get_project_manager()

        self.project_meta: Dict[str, object] = {}
        self.project_dir: Optional[Path] = None

        self._build_ui()
        self._create_and_register_views()
        self._setup_connections()
        self._setup_status_indicators()
        self._install_contextual_help()

        self.sidebar.navigation_requested.connect(self._on_navigation_requested)

        self.show()
        self.raise_()
        self.activateWindow()

        logger.info("MainWindow initialisee")

    def _build_ui(self) -> None:
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        splitter = QSplitter()
        main_layout.addWidget(splitter)

        self.sidebar = MainSidebar()
        self.sidebar.setFixedWidth(280)
        splitter.addWidget(self.sidebar)

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        self.breadcrumbs = BreadcrumbsWidget()
        self.breadcrumbs.setFixedHeight(48)
        self.breadcrumbs.step_selected.connect(self._on_breadcrumb_step_selected)
        content_layout.addWidget(self.breadcrumbs)

        self.stack_widget = QStackedWidget()
        self.stack_widget.setObjectName("mainContent")
        content_layout.addWidget(self.stack_widget)

        splitter.addWidget(content_widget)
        splitter.setSizes([280, 1200])

        self.help_panel = HelpPanel()
        self.status_widget = SystemStatusWidget()
        self.status_widget.status_updated.connect(self._on_system_status_updated)
        self.view_manager = ViewManager(self.stack_widget)

    def _create_and_register_views(self) -> None:
        logger.info("Creation et enregistrement des vues")

        welcome_view = WelcomeView(parent=None)
        welcome_view.projectCreationRequested.connect(self._handle_project_creation)
        self.view_manager.register_view("welcome", welcome_view)

        dashboard_view = DashboardViewMaritime(parent=None)
        self.view_manager.register_view("dashboard", dashboard_view)

        for view_name, view_config in VIEWS_CONFIG.items():
            if view_name in {"welcome", "dashboard"}:
                continue

            loader = view_config.get("loader")
            if loader is None:
                continue

            try:
                self.view_manager.register_view(view_name, loader(parent=None))
            except Exception as exc:
                logger.exception("Impossible d'instancier la vue '%s': %s", view_name, exc)

        self._wire_runtime_flow()
        self.view_manager.switch_to_view("welcome")
        self._update_breadcrumbs_for_view("welcome")

    def _setup_connections(self) -> None:
        self.view_manager.view_changed.connect(self._update_breadcrumbs_for_view)
        self.view_manager.view_changed.connect(self.sidebar.set_active_view)

    def _setup_status_indicators(self) -> None:
        self.status_widget.hide()

    def _install_contextual_help(self) -> None:
        install_help_on_widget(self.sidebar, "navigation-sidebar")

    def _wire_runtime_flow(self) -> None:
        acquisition_view = self.view_manager.get_view_widget("acquisition")
        analysis_view = self.view_manager.get_view_widget("analysis")

        if acquisition_view and hasattr(acquisition_view, "data_exported"):
            acquisition_view.data_exported.connect(self._on_data_exported)
        if acquisition_view and hasattr(acquisition_view, "calibration_completed"):
            acquisition_view.calibration_completed.connect(self._on_calibration_completed)
        if analysis_view and hasattr(analysis_view, "analysis_completed"):
            analysis_view.analysis_completed.connect(self._on_analysis_completed)

    def _push_project_context(self) -> None:
        if not self.project_meta or not self.project_dir:
            return

        project_dir = str(self.project_dir)
        for view_name in ("acquisition", "analysis", "export"):
            view = self.view_manager.get_view_widget(view_name)
            if view and hasattr(view, "set_project_context"):
                view.set_project_context(self.project_meta, project_dir)

    @Slot(str)
    def _on_navigation_requested(self, view_name: str) -> None:
        if not self.view_manager.has_view(view_name):
            logger.warning("Tentative de navigation vers une vue inconnue: '%s'", view_name)
            return
        self.view_manager.switch_to_view(view_name)

    def _update_breadcrumbs_for_view(self, view_name: str) -> None:
        view_to_step = {
            "welcome": WorkflowStep.WELCOME,
            "dashboard": WorkflowStep.PROJECT,
            "calibration": WorkflowStep.CALIBRATION,
            "acquisition": WorkflowStep.ACQUISITION,
            "analysis": WorkflowStep.ANALYSIS,
            "export": WorkflowStep.EXPORT,
        }
        workflow_step = view_to_step.get(view_name)
        if workflow_step is not None:
            self.breadcrumbs.set_current_step(workflow_step)

    @Slot(object, str)
    def _on_breadcrumb_step_selected(self, workflow_step, view_name) -> None:
        step_to_view = {
            WorkflowStep.WELCOME: "welcome",
            WorkflowStep.PROJECT: "dashboard",
            WorkflowStep.CALIBRATION: "calibration",
            WorkflowStep.ACQUISITION: "acquisition",
            WorkflowStep.ANALYSIS: "analysis",
            WorkflowStep.EXPORT: "export",
        }
        target_view = step_to_view.get(workflow_step)
        if target_view is None:
            logger.warning("Etape de breadcrumb inconnue: %s", workflow_step)
            return
        self.view_manager.switch_to_view(target_view)

    def _handle_project_creation(self, project_metadata=None) -> None:
        metadata = dict(project_metadata or {})
        project_name = (metadata.get("name") or "Projet_CHNeoWave").strip()
        description = (metadata.get("description") or "").strip()
        manager = (metadata.get("manager") or "").strip()
        laboratory = (metadata.get("laboratory") or "").strip()

        try:
            project_id = self.project_manager.create_project(
                name=project_name,
                description=description,
                author=manager,
                tags=[laboratory] if laboratory else [],
            )
            if not self.project_manager.load_project(project_id):
                raise RuntimeError("Le projet cree n'a pas pu etre recharge.")

            self.project_dir = self.project_manager.get_project_directory(project_id)
            self.project_meta = {
                **metadata,
                "project_id": project_id,
                "project_dir": str(self.project_dir),
                "author": manager,
            }

            self._push_project_context()
            self.projectCreated.emit()
            self.view_manager.switch_to_view("dashboard")
            show_success("Projet", f"Projet cree: {project_name}")

        except Exception as exc:
            logger.exception("Erreur creation projet: %s", exc)
            show_error("Projet", f"Creation projet impossible: {exc}")

    @Slot(str)
    def _on_data_exported(self, file_path: str) -> None:
        analysis_view = self.view_manager.get_view_widget("analysis")
        if analysis_view and hasattr(analysis_view, "load_data_file"):
            if analysis_view.load_data_file(file_path):
                self.view_manager.switch_to_view("analysis")
                show_info("Analyse", f"Donnees chargees pour analyse: {file_path}")

    @Slot(str, dict)
    def _on_analysis_completed(self, analysis_type: str, payload: dict) -> None:
        report_view = self.view_manager.get_view_widget("export")
        if report_view and hasattr(report_view, "set_analysis_context"):
            report_view.set_analysis_context(
                payload.get("source_file"),
                payload.get("results"),
                extra_metadata={
                    "analysis_type": analysis_type,
                    "project_metadata": self.project_meta,
                },
            )
            show_info("Rapport", "Rapport alimente avec les derniers resultats d'analyse")

    @Slot(dict)
    def _on_calibration_completed(self, payload: dict) -> None:
        channels = payload.get("channels", {})
        show_info("Calibration", f"Calibration terminee sur {len(channels)} canaux")

    @Slot(StatusLevel)
    def _on_system_status_updated(self, status_level) -> None:
        logger.debug("Mise a jour du statut systeme: %s", status_level)
        if status_level == StatusLevel.ERROR:
            show_error("Erreur systeme", "Une erreur systeme est survenue")
        elif status_level == StatusLevel.WARNING:
            show_info("Attention", "Le systeme necessite votre attention")
        elif status_level == StatusLevel.OK:
            show_success("Systeme", "Le systeme fonctionne normalement")

    def show_and_exec(self) -> int:
        self.show()
        self.raise_()
        self.activateWindow()

        app = QApplication.instance()
        if app is None:
            return 0

        exec_fn = getattr(app, "exec", None) or getattr(app, "exec_", None)
        return exec_fn() if exec_fn else 0
