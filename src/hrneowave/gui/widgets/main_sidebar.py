"""Primary application navigation for CHNeoWave."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout


class NavigationButton(QPushButton):
    """Compact navigation row whose state is controlled by the global QSS."""

    def __init__(self, index: str, text: str, parent=None):
        self.index = index
        self.label = text
        super().__init__(self._expanded_text(), parent)
        self.setObjectName("navButton")
        self.setCheckable(True)
        self.setProperty("active", "false")
        self.setToolTip(text)

    def _expanded_text(self) -> str:
        return f"{self.index}    {self.label}" if self.index else self.label

    def set_collapsed(self, collapsed: bool) -> None:
        self.setText(self.index or "S")
        self.setProperty("collapsed", "true" if collapsed else "false")
        if not collapsed:
            self.setText(self._expanded_text())
        self.style().unpolish(self)
        self.style().polish(self)

    def set_active(self, active: bool) -> None:
        self.setChecked(active)
        self.setProperty("active", "true" if active else "false")
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()


class MainSidebar(QFrame):
    """Single, restrained navigation rail for the laboratory workflow."""

    navigation_requested = Signal(str)

    NAVIGATION = (
        ("welcome", "01", "Projets"),
        ("dashboard", "02", "Vue système"),
        ("calibration", "03", "Calibration"),
        ("acquisition", "04", "Acquisition"),
        ("analysis", "05", "Analyse"),
        ("export", "06", "Rapport"),
    )

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("main_sidebar")
        self.current_view = "welcome"
        self.navigation_buttons = {}
        self.is_collapsed = False
        self._build_ui()
        self.collapse_sidebar(False)
        self.set_active_view("welcome")

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        header = QFrame()
        header.setObjectName("sidebar_header")
        header.setFixedHeight(78)
        self.header_layout = QHBoxLayout(header)
        self.header_layout.setContentsMargins(18, 16, 14, 14)
        header_layout = self.header_layout
        header_layout.setSpacing(11)

        mark = QLabel("CN")
        mark.setObjectName("brandMark")
        mark.setFixedSize(36, 36)
        mark.setAlignment(Qt.AlignmentFlag.AlignCenter)

        brand_layout = QVBoxLayout()
        brand_layout.setSpacing(1)
        self.brand = QLabel("CHNeoWave")
        self.brand.setObjectName("brandName")
        self.descriptor = QLabel("MARITIME LAB")
        self.descriptor.setObjectName("brandDescriptor")
        brand_layout.addWidget(self.brand)
        brand_layout.addWidget(self.descriptor)

        header_layout.addWidget(mark)
        header_layout.addLayout(brand_layout)
        header_layout.addStretch()
        root.addWidget(header)

        nav_container = QFrame()
        nav_layout = QVBoxLayout(nav_container)
        nav_layout.setContentsMargins(0, 18, 0, 12)
        nav_layout.setSpacing(2)

        self.workflow_section = QLabel("FLUX DE TRAVAIL")
        self.workflow_section.setObjectName("navSection")
        self.workflow_section.setContentsMargins(18, 0, 0, 8)
        nav_layout.addWidget(self.workflow_section)

        for name, index, label in self.NAVIGATION:
            button = NavigationButton(index, label)
            button.clicked.connect(lambda checked=False, view_name=name: self.navigate_to(view_name))
            self.navigation_buttons[name] = button
            nav_layout.addWidget(button)

        nav_layout.addSpacing(16)
        self.support_section = QLabel("SYSTÈME")
        self.support_section.setObjectName("navSection")
        self.support_section.setContentsMargins(18, 0, 0, 8)
        nav_layout.addWidget(self.support_section)

        settings = NavigationButton("", "Paramètres")
        settings.clicked.connect(lambda: self.navigate_to("settings"))
        self.navigation_buttons["settings"] = settings
        nav_layout.addWidget(settings)
        nav_layout.addStretch()
        root.addWidget(nav_container, 1)

        footer = QFrame()
        footer.setObjectName("sidebar_footer")
        footer.setFixedHeight(62)
        self.footer_layout = QHBoxLayout(footer)
        self.footer_layout.setContentsMargins(18, 10, 14, 10)
        footer_layout = self.footer_layout
        footer_layout.setSpacing(8)
        self.status_dot = QLabel("●")
        self.status_dot.setObjectName("sidebarStatusDot")
        self.status_dot.setProperty("connected", "false")
        self.status_text = QLabel("Système prêt · hors ligne")
        self.status_text.setObjectName("sidebarStatus")
        self.version = QLabel("v1.1")
        self.version.setObjectName("sidebarVersion")
        footer_layout.addWidget(self.status_dot)
        footer_layout.addWidget(self.status_text)
        footer_layout.addStretch()
        footer_layout.addWidget(self.version)
        root.addWidget(footer)

    def navigate_to(self, view_name: str) -> None:
        if view_name not in self.navigation_buttons:
            return
        self._apply_active_state(view_name)
        self.navigation_requested.emit(view_name)

    def _apply_active_state(self, view_name: str) -> None:
        for name, button in self.navigation_buttons.items():
            button.set_active(name == view_name)
        self.current_view = view_name

    def set_active_view(self, view_name: str) -> None:
        """Synchronise l'état visuel sans réémettre une navigation."""

        if view_name in self.navigation_buttons:
            self._apply_active_state(view_name)

    def get_active_view(self) -> str:
        return self.current_view

    def set_theme(self, is_dark: bool) -> None:
        del is_dark

    def collapse_sidebar(self, collapsed: bool) -> None:
        self.is_collapsed = bool(collapsed)
        self.setProperty("collapsed", "true" if self.is_collapsed else "false")
        self.setFixedWidth(72 if self.is_collapsed else 248)

        self.brand.setVisible(not self.is_collapsed)
        self.descriptor.setVisible(not self.is_collapsed)
        self.workflow_section.setVisible(not self.is_collapsed)
        self.support_section.setVisible(not self.is_collapsed)
        self.status_text.setVisible(not self.is_collapsed)
        self.version.setVisible(not self.is_collapsed)

        self.header_layout.setContentsMargins(18, 16, 14 if not self.is_collapsed else 18, 14)
        self.footer_layout.setContentsMargins(
            18 if not self.is_collapsed else 28,
            10,
            14 if not self.is_collapsed else 28,
            10,
        )
        for button in self.navigation_buttons.values():
            button.set_collapsed(self.is_collapsed)

        self.style().unpolish(self)
        self.style().polish(self)

    def update_connection_status(self, connected: bool, message: str = "") -> None:
        self.status_dot.setProperty("connected", "true" if connected else "false")
        self.status_dot.style().unpolish(self.status_dot)
        self.status_dot.style().polish(self.status_dot)
        if message:
            self.status_text.setText(message)
        else:
            state = "connecté" if connected else "hors ligne"
            self.status_text.setText(f"Système prêt · {state}")
