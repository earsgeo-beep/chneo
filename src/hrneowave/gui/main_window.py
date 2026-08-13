#!/usr/bin/env python3
"""Fenetre principale de CHNeoWave."""

import logging
from pathlib import Path

from PySide6.QtCore import Signal, Slot
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QMessageBox,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from hrneowave.core.project_manager import get_project_manager

from .components.help_system import HelpPanel, install_help_on_widget
from .components.notification_system import show_error, show_info, show_success
from .components.status_indicators import StatusLevel, SystemStatusWidget
from .preferences import get_user_preferences
from .view_manager import ViewManager
from .views import VIEWS_CONFIG, DashboardViewMaritime, WelcomeView
from .widgets.top_navigation import TopNavigationBar

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Fenetre principale de l'application."""

    projectCreated = Signal()

    def __init__(self, config=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("CHNeoWave")
        self.setMinimumSize(1060, 680)

        self.config = config or {}
        self.user_preferences = get_user_preferences()
        self.project_manager = get_project_manager()

        self.project_meta: dict[str, object] = {}
        self.project_dir: Path | None = None

        self._build_ui()
        self._create_and_register_views()
        self._setup_connections()
        self._apply_current_theme_to_views()
        self._setup_status_indicators()
        self._install_contextual_help()

        self.application_header.navigation_requested.connect(self._on_navigation_requested)
        self.application_header.theme_toggle_requested.connect(self._toggle_theme)

        self.show()
        self.raise_()
        self.activateWindow()

        logger.info("MainWindow initialisee")

    def _build_ui(self) -> None:
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.application_header = TopNavigationBar()
        main_layout.addWidget(self.application_header)

        self.stack_widget = QStackedWidget()
        self.stack_widget.setObjectName("mainContent")
        main_layout.addWidget(self.stack_widget, 1)

        self.help_panel = HelpPanel()
        self.status_widget = SystemStatusWidget()
        self.status_widget.status_updated.connect(self._on_system_status_updated)
        self.view_manager = ViewManager(self.stack_widget)
        self._build_desktop_menus()

    def _build_desktop_menus(self) -> None:
        """Create conventional desktop menus for repeatable laboratory actions."""

        menu_bar = self.menuBar()
        menu_bar.setObjectName("desktopMenuBar")
        menu_bar.setNativeMenuBar(False)

        file_menu = menu_bar.addMenu("Fichier")
        new_project = self._menu_action(
            "Nouveau projet", "Ctrl+N", lambda: self._on_navigation_requested("welcome")
        )
        open_data = self._menu_action("Ouvrir des données…", "Ctrl+O", self._open_analysis_file)
        report = self._menu_action(
            "Préparer le rapport scientifique", "Ctrl+R", lambda: self._on_navigation_requested("export")
        )
        quit_action = self._menu_action("Quitter", "Ctrl+Q", QApplication.instance().quit)
        file_menu.addActions((new_project, open_data))
        file_menu.addSeparator()
        file_menu.addAction(report)
        file_menu.addSeparator()
        file_menu.addAction(quit_action)

        tools_menu = menu_bar.addMenu("Outils")
        tools_menu.addAction(
            self._menu_action(
                "Configuration matérielle", "Ctrl+M", lambda: self._on_navigation_requested("acquisition")
            )
        )
        tools_menu.addAction(
            self._menu_action(
                "Calibration des capteurs", "Ctrl+L", lambda: self._on_navigation_requested("calibration")
            )
        )
        tools_menu.addAction(
            self._menu_action(
                "Traitement scientifique", "Ctrl+T", lambda: self._on_navigation_requested("analysis")
            )
        )
        tools_menu.addSeparator()
        tools_menu.addAction(
            self._menu_action("Préférences", "Ctrl+,", lambda: self._on_navigation_requested("settings"))
        )

        display_menu = menu_bar.addMenu("Affichage")
        display_menu.addAction(self._menu_action("Thème clair / sombre", "Ctrl+D", self._toggle_theme))
        display_menu.addAction(
            self._menu_action("Ajuster les graphes", "F", self._fit_analysis_plots)
        )
        display_menu.addAction(
            self._menu_action("Afficher les résultats détaillés", "F9", self._toggle_analysis_details)
        )

        help_menu = menu_bar.addMenu("Aide")
        help_menu.addAction(self._menu_action("Guide d’utilisation", "F1", self._show_quick_help))
        help_menu.addAction(self._menu_action("À propos de CHNeoWave", None, self._show_about))

    def _menu_action(self, text: str, shortcut: str | None, callback) -> QAction:
        action = QAction(text, self)
        if shortcut:
            action.setShortcut(QKeySequence(shortcut))
        action.triggered.connect(callback)
        return action

    def _open_analysis_file(self) -> None:
        self._on_navigation_requested("analysis")
        view = self.view_manager.get_view_widget("analysis")
        if view and hasattr(view, "open_file_dialog"):
            view.open_file_dialog()

    def _fit_analysis_plots(self) -> None:
        view = self.view_manager.get_view_widget("analysis")
        if not view or not hasattr(view, "results_area"):
            return
        view.results_area.time_plot.fit_data()
        view.results_area.spectrum_plot.fit_data()

    def _toggle_analysis_details(self) -> None:
        view = self.view_manager.get_view_widget("analysis")
        if view and hasattr(view, "_toggle_tools_panel"):
            view._toggle_tools_panel()

    def _show_quick_help(self) -> None:
        QMessageBox.information(
            self,
            "Guide CHNeoWave",
            "Workflow laboratoire : Projet → Calibration → Acquisition → Traitement → Rapport.\n\n"
            "Dans Traitement, cochez plusieurs voies pour les comparer. Les alertes automatiques "
            "ne remplacent jamais la décision de l’ingénieur.",
        )

    def _show_about(self) -> None:
        QMessageBox.about(
            self,
            "À propos de CHNeoWave",
            "CHNeoWave\nPoste d’acquisition et d’analyse scientifique pour laboratoire maritime.",
        )

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
        self._update_header_for_view("welcome")

    def _setup_connections(self) -> None:
        self.view_manager.view_changed.connect(self._update_header_for_view)
        self.view_manager.view_changed.connect(self.application_header.set_active_view)

    def _setup_status_indicators(self) -> None:
        self.status_widget.hide()

    def _install_contextual_help(self) -> None:
        install_help_on_widget(self.application_header, "navigation-workspaces")

    def _wire_runtime_flow(self) -> None:
        calibration_view = self.view_manager.get_view_widget("calibration")
        acquisition_view = self.view_manager.get_view_widget("acquisition")
        analysis_view = self.view_manager.get_view_widget("analysis")
        dashboard_view = self.view_manager.get_view_widget("dashboard")

        if acquisition_view and hasattr(acquisition_view, "data_exported"):
            acquisition_view.data_exported.connect(self._on_data_exported)
        if acquisition_view and hasattr(acquisition_view, "calibration_completed"):
            acquisition_view.calibration_completed.connect(self._on_calibration_completed)
        if acquisition_view and hasattr(acquisition_view, "calibration_requested"):
            acquisition_view.calibration_requested.connect(
                lambda: self._on_navigation_requested("calibration")
            )
        if acquisition_view and hasattr(acquisition_view, "hardware_state_changed"):
            acquisition_view.hardware_state_changed.connect(self.application_header.set_hardware)
        if (
            acquisition_view
            and calibration_view
            and hasattr(acquisition_view, "hardware_channels_changed")
            and hasattr(calibration_view, "set_channel_count")
        ):
            acquisition_view.hardware_channels_changed.connect(calibration_view.set_channel_count)
        if (
            acquisition_view
            and calibration_view
            and hasattr(
                calibration_view,
                "bind_acquisition_controller",
            )
        ):
            calibration_view.bind_acquisition_controller(acquisition_view.controller)
        if (
            acquisition_view
            and calibration_view
            and hasattr(acquisition_view, "hardware_state_changed")
            and hasattr(calibration_view, "update_hardware_state")
        ):
            acquisition_view.hardware_state_changed.connect(calibration_view.update_hardware_state)
        if calibration_view and hasattr(calibration_view, "hardware_setup_requested"):
            calibration_view.hardware_setup_requested.connect(self._open_hardware_setup)
        if calibration_view and hasattr(calibration_view, "calibration_completed"):
            calibration_view.calibration_completed.connect(self._on_calibration_completed)
        if analysis_view and hasattr(analysis_view, "analysis_completed"):
            analysis_view.analysis_completed.connect(self._on_analysis_completed)
        if analysis_view and hasattr(analysis_view, "source_changed"):
            analysis_view.source_changed.connect(self.application_header.set_source)
        if dashboard_view and hasattr(dashboard_view, "navigation_requested"):
            dashboard_view.navigation_requested.connect(self._on_navigation_requested)

    def _push_project_context(self) -> None:
        if not self.project_meta or not self.project_dir:
            return

        project_dir = str(self.project_dir)
        for view_name in ("dashboard", "acquisition", "analysis", "export"):
            view = self.view_manager.get_view_widget(view_name)
            if view and hasattr(view, "set_project_context"):
                view.set_project_context(self.project_meta, project_dir)

    @Slot(str)
    def _on_navigation_requested(self, view_name: str) -> None:
        if not self.view_manager.has_view(view_name):
            logger.warning("Tentative de navigation vers une vue inconnue: '%s'", view_name)
            return
        self.view_manager.switch_to_view(view_name)

    def _update_header_for_view(self, view_name: str) -> None:
        self.application_header.set_active_view(view_name)
        calibration_view = self.view_manager.get_view_widget("calibration")
        if calibration_view and hasattr(calibration_view, "set_workspace_active"):
            calibration_view.set_workspace_active(view_name == "calibration")

    def _open_hardware_setup(self) -> None:
        acquisition_view = self.view_manager.get_view_widget("acquisition")
        if acquisition_view and hasattr(acquisition_view, "config_tabs"):
            acquisition_view.config_tabs.setCurrentIndex(0)
        self._on_navigation_requested("acquisition")

    def _toggle_theme(self) -> None:
        app = QApplication.instance()
        manager = getattr(app, "theme_manager", None) if app else None
        if manager is not None:
            manager.toggle_theme()
            is_dark = manager.get_current_theme() == "dark"
            for view in self.view_manager.views.values():
                if view and hasattr(view, "set_theme"):
                    view.set_theme(is_dark)

    def _apply_current_theme_to_views(self) -> None:
        app = QApplication.instance()
        manager = getattr(app, "theme_manager", None) if app else None
        is_dark = bool(manager and manager.get_current_theme() == "dark")
        for view in self.view_manager.views.values():
            if hasattr(view, "set_theme"):
                view.set_theme(is_dark)

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
                water_depth=float(metadata.get("water_depth_m") or 0.0),
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
            self.application_header.set_project(project_name)

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
        record_payload = payload.get("record")
        acquisition_view = self.view_manager.get_view_widget("acquisition")
        registered = False
        if (
            record_payload
            and acquisition_view
            and hasattr(
                acquisition_view,
                "register_calibration_record",
            )
        ):
            registered = acquisition_view.register_calibration_record(record_payload)

        channel_number = int(payload.get("channel", 0)) + 1
        if registered:
            show_success(
                "Calibration",
                f"Canal {channel_number} validé et transmis à l'acquisition.",
            )
        else:
            show_info("Calibration", f"Calibration reçue sur {len(channels)} canal(aux)")

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
