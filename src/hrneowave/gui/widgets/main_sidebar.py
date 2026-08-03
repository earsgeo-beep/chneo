"""Primary application navigation for CHNeoWave."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout


class NavigationButton(QPushButton):
    """Compact navigation row whose state is controlled by the global QSS."""

    def __init__(self, index: str, text: str, parent=None):
        super().__init__(f"{index}    {text}" if index else text, parent)
        self.setObjectName("navButton")
        self.setCheckable(True)
        self.setProperty("active", "false")

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
        self.set_active_view("welcome")

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        header = QFrame()
        header.setObjectName("sidebar_header")
        header.setFixedHeight(78)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(18, 16, 14, 14)
        header_layout.setSpacing(11)

        mark = QLabel("CN")
        mark.setObjectName("brandMark")
        mark.setFixedSize(36, 36)
        mark.setAlignment(Qt.AlignmentFlag.AlignCenter)

        brand_layout = QVBoxLayout()
        brand_layout.setSpacing(1)
        brand = QLabel("CHNeoWave")
        brand.setObjectName("brandName")
        descriptor = QLabel("MARITIME LAB")
        descriptor.setObjectName("brandDescriptor")
        brand_layout.addWidget(brand)
        brand_layout.addWidget(descriptor)

        header_layout.addWidget(mark)
        header_layout.addLayout(brand_layout)
        header_layout.addStretch()
        root.addWidget(header)

        nav_container = QFrame()
        nav_layout = QVBoxLayout(nav_container)
        nav_layout.setContentsMargins(0, 18, 0, 12)
        nav_layout.setSpacing(2)

        section = QLabel("FLUX DE TRAVAIL")
        section.setObjectName("navSection")
        section.setContentsMargins(18, 0, 0, 8)
        nav_layout.addWidget(section)

        for name, index, label in self.NAVIGATION:
            button = NavigationButton(index, label)
            button.clicked.connect(lambda checked=False, view_name=name: self.navigate_to(view_name))
            self.navigation_buttons[name] = button
            nav_layout.addWidget(button)

        nav_layout.addSpacing(16)
        support = QLabel("SYSTÈME")
        support.setObjectName("navSection")
        support.setContentsMargins(18, 0, 0, 8)
        nav_layout.addWidget(support)

        settings = NavigationButton("", "Paramètres")
        settings.clicked.connect(lambda: self.navigate_to("settings"))
        self.navigation_buttons["settings"] = settings
        nav_layout.addWidget(settings)
        nav_layout.addStretch()
        root.addWidget(nav_container, 1)

        footer = QFrame()
        footer.setObjectName("sidebar_footer")
        footer.setFixedHeight(62)
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(18, 10, 14, 10)
        footer_layout.setSpacing(8)
        dot = QLabel("●")
        dot.setObjectName("sidebarStatusDot")
        self.status_text = QLabel("Système prêt · hors ligne")
        self.status_text.setObjectName("sidebarStatus")
        version = QLabel("v1.1")
        version.setObjectName("sidebarVersion")
        footer_layout.addWidget(dot)
        footer_layout.addWidget(self.status_text)
        footer_layout.addStretch()
        footer_layout.addWidget(version)
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
        self.is_collapsed = collapsed
        self.setFixedWidth(64 if collapsed else 248)

    def update_connection_status(self, connected: bool, message: str = "") -> None:
        if message:
            self.status_text.setText(message)
        else:
            state = "connecté" if connected else "hors ligne"
            self.status_text.setText(f"Système prêt · {state}")
