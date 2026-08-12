"""Primary instrument navigation for CHNeoWave."""

from __future__ import annotations

from PySide6.QtCore import QSize, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from ..icons import BrandMark, svg_icon


class NavigationButton(QPushButton):
    """Compact navigation row with a stable vector symbol."""

    def __init__(self, icon_name: str, text: str, parent=None):
        self.icon_name = icon_name
        self.label = text
        self._collapsed = False
        self._active = False
        super().__init__(text, parent)
        self.setObjectName("navButton")
        self.setCheckable(True)
        self.setProperty("active", "false")
        self.setToolTip(text)
        self.setIconSize(QSize(18, 18))
        self._update_icon()

    def set_collapsed(self, collapsed: bool) -> None:
        self._collapsed = bool(collapsed)
        self.setText("" if self._collapsed else self.label)
        self.setProperty("collapsed", "true" if self._collapsed else "false")
        self.style().unpolish(self)
        self.style().polish(self)

    def set_active(self, active: bool) -> None:
        self._active = bool(active)
        self.setChecked(self._active)
        self.setProperty("active", "true" if self._active else "false")
        self._update_icon()
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    def _update_icon(self) -> None:
        color = "#E9FBFD" if self._active else "#8EA6B2"
        self.setIcon(svg_icon(self.icon_name, color, 18))


class MainSidebar(QFrame):
    """Collapsible navigation rail for the laboratory workflow."""

    navigation_requested = Signal(str)

    NAVIGATION = (
        ("welcome", "project", "Projets"),
        ("dashboard", "system", "Vue système"),
        ("calibration", "calibration", "Calibration"),
        ("acquisition", "acquisition", "Acquisition"),
        ("analysis", "analysis", "Traitement"),
        ("export", "report", "Rapport"),
    )

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("main_sidebar")
        self.current_view = "welcome"
        self.navigation_buttons: dict[str, NavigationButton] = {}
        self.is_collapsed = False
        self._theme = "light"
        self._build_ui()
        self.collapse_sidebar(False)
        self.set_active_view("welcome")

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        header = QFrame()
        header.setObjectName("sidebar_header")
        header.setFixedHeight(60)
        self.header_layout = QHBoxLayout(header)
        self.header_layout.setContentsMargins(14, 8, 12, 8)
        self.header_layout.setSpacing(10)

        self.mark = BrandMark(size=34)
        brand_layout = QVBoxLayout()
        brand_layout.setSpacing(0)
        self.brand = QLabel("CHNeoWave")
        self.brand.setObjectName("brandName")
        self.descriptor = QLabel("MARITIME INSTRUMENTS")
        self.descriptor.setObjectName("brandDescriptor")
        brand_layout.addWidget(self.brand)
        brand_layout.addWidget(self.descriptor)

        self.header_layout.addWidget(self.mark)
        self.header_layout.addLayout(brand_layout)
        self.header_layout.addStretch()
        root.addWidget(header)

        nav_container = QFrame()
        nav_layout = QVBoxLayout(nav_container)
        nav_layout.setContentsMargins(0, 12, 0, 8)
        nav_layout.setSpacing(2)

        self.workflow_section = QLabel("CHAÎNE DE MESURE")
        self.workflow_section.setObjectName("navSection")
        self.workflow_section.setContentsMargins(14, 0, 0, 7)
        nav_layout.addWidget(self.workflow_section)

        for name, icon_name, label in self.NAVIGATION:
            button = NavigationButton(icon_name, label)
            button.clicked.connect(lambda checked=False, view_name=name: self.navigate_to(view_name))
            self.navigation_buttons[name] = button
            nav_layout.addWidget(button)

        nav_layout.addStretch()
        self.support_section = QLabel("SYSTÈME")
        self.support_section.setObjectName("navSection")
        self.support_section.setContentsMargins(14, 0, 0, 7)
        nav_layout.addWidget(self.support_section)

        settings = NavigationButton("settings", "Paramètres")
        settings.clicked.connect(lambda: self.navigate_to("settings"))
        self.navigation_buttons["settings"] = settings
        nav_layout.addWidget(settings)
        root.addWidget(nav_container, 1)

        footer = QFrame()
        footer.setObjectName("sidebar_footer")
        footer.setFixedHeight(48)
        self.footer_layout = QHBoxLayout(footer)
        self.footer_layout.setContentsMargins(15, 8, 12, 8)
        self.footer_layout.setSpacing(9)
        self.status_dot = QFrame()
        self.status_dot.setObjectName("sidebarStatusDot")
        self.status_dot.setProperty("connected", "false")
        self.status_dot.setFixedSize(8, 8)
        self.status_text = QLabel("Local · matériel non connecté")
        self.status_text.setObjectName("sidebarStatus")
        self.version = QLabel("v1.1")
        self.version.setObjectName("sidebarVersion")
        self.footer_layout.addWidget(self.status_dot)
        self.footer_layout.addWidget(self.status_text)
        self.footer_layout.addStretch()
        self.footer_layout.addWidget(self.version)
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
        if view_name in self.navigation_buttons:
            self._apply_active_state(view_name)

    def get_active_view(self) -> str:
        return self.current_view

    def set_theme(self, theme: str | bool) -> None:
        self._theme = "dark" if theme is True or theme == "dark" else "light"
        self.mark.set_theme(self._theme)
        for button in self.navigation_buttons.values():
            button._update_icon()

    def collapse_sidebar(self, collapsed: bool) -> None:
        self.is_collapsed = bool(collapsed)
        self.setProperty("collapsed", "true" if self.is_collapsed else "false")
        self.setFixedWidth(58 if self.is_collapsed else 224)

        self.brand.setVisible(not self.is_collapsed)
        self.descriptor.setVisible(not self.is_collapsed)
        self.workflow_section.setVisible(not self.is_collapsed)
        self.support_section.setVisible(not self.is_collapsed)
        self.status_text.setVisible(not self.is_collapsed)
        self.version.setVisible(not self.is_collapsed)

        self.header_layout.setContentsMargins(12 if self.is_collapsed else 14, 8, 12, 8)
        self.header_layout.setSpacing(0 if self.is_collapsed else 10)
        self.footer_layout.setContentsMargins(
            25 if self.is_collapsed else 15,
            8,
            25 if self.is_collapsed else 12,
            8,
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
            state = "matériel connecté" if connected else "matériel non connecté"
            self.status_text.setText(f"Local · {state}")
