#!/usr/bin/env python3
"""Fenetre principale de CHNeoWave."""

import logging
from pathlib import Path

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
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
from .widgets.main_sidebar import MainSidebar

logger = logging.getLogger(__name__)


class ApplicationHeader(QFrame):
    """Stable page context bar; navigation remains solely in the sidebar."""

    sidebar_toggle_requested = Signal()

    PAGE_CONTEXT = {
        "welcome": (
            "PROJETS",
            "Préparer une campagne",
            "Créer le dossier d'essai et son contexte laboratoire.",
        ),
        "dashboard": (
            "VUE SYSTÈME",
            "Pilotage de la campagne",
            "Suivre l'avancement, le matériel et les prochaines actions.",
        ),
        "calibration": (
            "ÉTAPE 01",
            "Calibration des capteurs",
            "Tracer et valider la chaîne de mesure avant l'acquisition.",
        ),
        "acquisition": (
            "ÉTAPE 02",
            "Acquisition du laboratoire",
            "Sélectionner un équipement physique et enregistrer une session traçable.",
        ),
        "analysis": (
            "ÉTAPE 03",
            "Traitement des données",
            "Contrôler la qualité et interpréter les résultats spectraux.",
        ),
        "export": (
            "ÉTAPE 04",
            "Rapport technique",
            "Consolider les résultats et produire un livrable vérifiable.",
        ),
        "settings": ("SYSTÈME", "Paramètres", "Configurer le projet et le comportement de l'application."),
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("applicationHeader")
        self.setFixedHeight(66)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(18, 7, 18, 7)
        layout.setSpacing(12)

        self.sidebar_toggle_button = QPushButton("←")
        self.sidebar_toggle_button.setObjectName("sidebarToggleButton")
        self.sidebar_toggle_button.setFixedSize(32, 32)
        self.sidebar_toggle_button.setToolTip("Replier la navigation (F9)")
        self.sidebar_toggle_button.clicked.connect(self.sidebar_toggle_requested.emit)
        layout.addWidget(self.sidebar_toggle_button, 0, Qt.AlignmentFlag.AlignVCenter)

        title_stack = QVBoxLayout()
        title_stack.setSpacing(1)
        self.eyebrow = QLabel()
        self.eyebrow.setObjectName("pageEyebrow")
        self.title = QLabel()
        self.title.setObjectName("pageTitle")
        self.subtitle = QLabel()
        self.subtitle.setObjectName("pageSubtitle")
        title_stack.addWidget(self.eyebrow)
        title_stack.addWidget(self.title)
        title_stack.addWidget(self.subtitle)

        layout.addLayout(title_stack, 1)
        self.mode_badge = QLabel("TRAITEMENT LOCAL")
        self.mode_badge.setObjectName("offlineBadge")
        layout.addWidget(self.mode_badge, 0, Qt.AlignmentFlag.AlignVCenter)
        self.set_view("welcome")

    def set_view(self, view_name: str) -> None:
        eyebrow, title, subtitle = self.PAGE_CONTEXT.get(
            view_name,
            ("CHNEOWAVE", view_name.replace("_", " ").title(), ""),
        )
        self.eyebrow.setText(eyebrow)
        self.title.setText(title)
        self.subtitle.setText(subtitle)


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
        self._setup_status_indicators()
        self._install_contextual_help()

        self.sidebar.navigation_requested.connect(self._on_navigation_requested)
        self.application_header.sidebar_toggle_requested.connect(self._toggle_sidebar)
        self.sidebar_shortcut = QShortcut(QKeySequence("F9"), self)
        self.sidebar_shortcut.activated.connect(self._toggle_sidebar)

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

        self.sidebar = MainSidebar()
        main_layout.addWidget(self.sidebar)

        content_widget = QWidget()
        content_widget.setObjectName("workspace")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        self.application_header = ApplicationHeader()
        content_layout.addWidget(self.application_header)

        self.stack_widget = QStackedWidget()
        self.stack_widget.setObjectName("mainContent")
        content_layout.addWidget(self.stack_widget)

        main_layout.addWidget(content_widget, 1)

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
        self._update_header_for_view("welcome")

    def _setup_connections(self) -> None:
        self.view_manager.view_changed.connect(self._update_header_for_view)
        self.view_manager.view_changed.connect(self.sidebar.set_active_view)

    def _setup_status_indicators(self) -> None:
        self.status_widget.hide()

    def _install_contextual_help(self) -> None:
        install_help_on_widget(self.sidebar, "navigation-sidebar")

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
            acquisition_view.hardware_state_changed.connect(self.sidebar.update_connection_status)
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
        self.application_header.set_view(view_name)
        calibration_view = self.view_manager.get_view_widget("calibration")
        if calibration_view and hasattr(calibration_view, "set_workspace_active"):
            calibration_view.set_workspace_active(view_name == "calibration")

    def _open_hardware_setup(self) -> None:
        acquisition_view = self.view_manager.get_view_widget("acquisition")
        if acquisition_view and hasattr(acquisition_view, "config_tabs"):
            acquisition_view.config_tabs.setCurrentIndex(0)
        self._on_navigation_requested("acquisition")

    def _toggle_sidebar(self) -> None:
        collapsed = not self.sidebar.is_collapsed
        self.sidebar.collapse_sidebar(collapsed)
        self.application_header.sidebar_toggle_button.setText("☰" if collapsed else "←")
        self.application_header.sidebar_toggle_button.setToolTip(
            "Ouvrir la navigation (F9)" if collapsed else "Replier la navigation (F9)"
        )

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
