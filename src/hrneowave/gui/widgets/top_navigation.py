"""Horizontal desktop navigation for the CHNeoWave laboratory workstation."""

from __future__ import annotations

from PySide6.QtCore import QSize, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton

from ..workbench.icons import line_icon


class WorkspaceButton(QPushButton):
    """One stable destination in the laboratory workflow."""

    def __init__(self, icon_name: str, caption: str, parent=None):
        super().__init__(caption, parent)
        self.icon_name = icon_name
        self.setObjectName("workspaceNavButton")
        self.setCheckable(True)
        self.setAutoExclusive(True)
        self.setIcon(line_icon(icon_name, "#9CB0BA"))
        self.setIconSize(QSize(16, 16))
        self.setMinimumWidth(82)
        self.setFixedHeight(38)

    def set_active(self, active: bool) -> None:
        self.setChecked(active)
        self.setProperty("active", "true" if active else "false")
        self.setIcon(line_icon(self.icon_name, "#FFFFFF" if active else "#9CB0BA"))
        self.style().unpolish(self)
        self.style().polish(self)


class TopNavigationBar(QFrame):
    """Global navigation and compact campaign/hardware context."""

    navigation_requested = Signal(str)
    theme_toggle_requested = Signal()

    NAVIGATION = (
        ("welcome", "projects", "Projet"),
        ("dashboard", "dashboard", "Système"),
        ("calibration", "calibration", "Calibration"),
        ("acquisition", "acquisition", "Acquisition"),
        ("analysis", "analysis", "Analyse"),
        ("export", "report", "Rapport"),
    )

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("topNavigation")
        self.setFixedHeight(48)
        self.current_view = "welcome"
        self.navigation_buttons: dict[str, WorkspaceButton] = {}
        self._build_ui()
        self.set_active_view("welcome")

    def _build_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 8, 0)
        layout.setSpacing(2)

        brand = QFrame()
        brand.setObjectName("horizontalBrand")
        brand_layout = QHBoxLayout(brand)
        brand_layout.setContentsMargins(0, 0, 14, 0)
        brand_layout.setSpacing(7)
        mark = QLabel()
        mark.setObjectName("horizontalBrandMark")
        mark.setPixmap(line_icon("brand", "#31B8D0").pixmap(24, 24))
        copy = QLabel("CHNeoWave")
        copy.setObjectName("horizontalBrandCopy")
        copy.setToolTip("Laboratoire maritime")
        brand_layout.addWidget(mark)
        brand_layout.addWidget(copy)
        layout.addWidget(brand)

        for name, icon_name, caption in self.NAVIGATION:
            button = WorkspaceButton(icon_name, caption)
            button.clicked.connect(
                lambda _checked=False, view_name=name: self.navigate_to(view_name)
            )
            self.navigation_buttons[name] = button
            layout.addWidget(button)

        layout.addStretch(1)
        self.project_label = QLabel("PROJET · AUCUN")
        self.project_label.setObjectName("navigationContext")
        self.source_label = QLabel("SOURCE · —")
        self.source_label.setObjectName("navigationContext")
        self.source_label.hide()
        self.hardware_label = QLabel("MATÉRIEL · DÉCONNECTÉ")
        self.hardware_label.setObjectName("navigationHardware")
        self.hardware_label.setProperty("connected", "false")
        layout.addWidget(self.project_label)
        layout.addWidget(self.source_label)
        layout.addWidget(self.hardware_label)

        self.theme_button = QPushButton()
        self.theme_button.setObjectName("navigationTheme")
        self.theme_button.setFixedSize(34, 34)
        self.theme_button.setIcon(line_icon("theme", "#A5BAC3"))
        self.theme_button.setToolTip("Thème clair / sombre")
        self.theme_button.clicked.connect(self.theme_toggle_requested.emit)
        layout.addWidget(self.theme_button)

    def navigate_to(self, view_name: str) -> None:
        if view_name in self.navigation_buttons:
            self.set_active_view(view_name)
            self.navigation_requested.emit(view_name)

    def set_active_view(self, view_name: str) -> None:
        if view_name not in self.navigation_buttons:
            return
        for name, button in self.navigation_buttons.items():
            button.set_active(name == view_name)
        self.current_view = view_name

    def set_project(self, project_name: str) -> None:
        value = project_name.strip() if project_name else "Aucun"
        self.project_label.setText(f"PROJET · {value}")
        self.project_label.setToolTip(value)

    def set_source(self, source_name: str) -> None:
        value = source_name.strip() if source_name else "—"
        self.source_label.setText(f"SOURCE · {value}")
        self.source_label.setToolTip(value)

    def set_hardware(self, connected: bool, message: str = "") -> None:
        value = message or ("Connecté" if connected else "Déconnecté")
        self.hardware_label.setText(f"MATÉRIEL · {value}")
        self.hardware_label.setToolTip(value)
        self.hardware_label.setProperty("connected", "true" if connected else "false")
        self.hardware_label.style().unpolish(self.hardware_label)
        self.hardware_label.style().polish(self.hardware_label)

    def update_connection_status(self, connected: bool, message: str = "") -> None:
        self.set_hardware(connected, message)
