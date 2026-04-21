# -*- coding: utf-8 -*-
"""
Main Sidebar Widget - Maritime Theme 2025
Barre latérale de navigation principale simplifiée et robuste.
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtGui import QFont

FIBONACCI_SPACING = [8, 13, 21, 34, 55, 89]


class NavigationButton(QPushButton):
    """Bouton de navigation avec état actif."""

    def __init__(self, text: str, icon_text: str = "", is_active: bool = False, parent=None):
        super().__init__(parent)
        self.button_text = text
        self.icon_text = icon_text
        self.is_active = is_active
        self._setup_ui()
        self.apply_style()

    def _setup_ui(self) -> None:
        self.setObjectName("nav_button")
        self.setMinimumHeight(48)
        self.setCheckable(True)
        self.setChecked(self.is_active)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(13, 10, 13, 10)
        layout.setSpacing(13)

        self.icon_label = QLabel(self.icon_text)
        self.icon_label.setFont(QFont("Segoe UI Emoji", 14))
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_label.setFixedWidth(24)
        layout.addWidget(self.icon_label)

        self.text_label = QLabel(self.button_text)
        self.text_label.setFont(QFont("Inter", 11, QFont.Weight.Medium))
        layout.addWidget(self.text_label)
        layout.addStretch()

    def set_active(self, active: bool) -> None:
        self.is_active = active
        self.setChecked(active)
        self.apply_style()

    def apply_style(self) -> None:
        if self.is_active:
            self.setStyleSheet(
                """
                QPushButton#nav_button {
                    background-color: #00ACC1;
                    color: #F5FBFF;
                    border: none;
                    border-radius: 12px;
                    padding: 8px 13px;
                    text-align: left;
                }
                QLabel {
                    background-color: transparent;
                    color: #F5FBFF;
                }
                """
            )
        else:
            self.setStyleSheet(
                """
                QPushButton#nav_button {
                    background-color: transparent;
                    color: #445868;
                    border: none;
                    border-radius: 12px;
                    padding: 8px 13px;
                    text-align: left;
                }
                QPushButton#nav_button:hover {
                    background-color: rgba(0, 172, 193, 0.10);
                    color: #00ACC1;
                }
                QLabel {
                    background-color: transparent;
                    color: inherit;
                }
                """
            )


class MainSidebar(QFrame):
    """
    Barre latérale principale de navigation.
    """

    navigation_requested = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_view = "welcome"
        self.navigation_buttons = {}
        self.is_collapsed = False

        self.setup_ui()
        self.setup_navigation()

    def setup_ui(self) -> None:
        self.setObjectName("main_sidebar")
        self.setMinimumWidth(230)
        self.setMaximumWidth(280)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        self.setFrameStyle(QFrame.Shape.NoFrame)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.setup_header(main_layout)
        self.setup_navigation_area(main_layout)
        self.setup_footer(main_layout)

        self.setStyleSheet(
            """
            QFrame#main_sidebar {
                background-color: #F5FBFF;
                border-right: 2px solid #E0E7FF;
            }
            """
        )

    def setup_header(self, parent_layout) -> None:
        header_frame = QFrame()
        header_frame.setObjectName("sidebar_header")
        header_frame.setMinimumHeight(89)

        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(21, 21, 21, 13)
        header_layout.setSpacing(8)

        logo_label = QLabel("🌊")
        logo_label.setFont(QFont("Segoe UI Emoji", 28))
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title_label = QLabel("CHNeoWave")
        title_label.setFont(QFont("Inter", 16, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #0A1929;")

        version_label = QLabel("v2025.1")
        version_label.setFont(QFont("Inter", 10))
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version_label.setStyleSheet("color: #445868;")

        header_layout.addWidget(logo_label)
        header_layout.addWidget(title_label)
        header_layout.addWidget(version_label)

        header_frame.setStyleSheet(
            """
            QFrame#sidebar_header {
                background-color: #F5FBFF;
                border-bottom: 1px solid #E0E7FF;
            }
            """
        )
        parent_layout.addWidget(header_frame)

    def setup_navigation_area(self, parent_layout) -> None:
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setFrameStyle(QFrame.Shape.NoFrame)

        nav_widget = QWidget()
        self.nav_layout = QVBoxLayout(nav_widget)
        self.nav_layout.setContentsMargins(13, 21, 13, 13)
        self.nav_layout.setSpacing(8)

        scroll_area.setWidget(nav_widget)
        parent_layout.addWidget(scroll_area)

    def setup_navigation(self) -> None:
        navigation_items = [
            {"name": "welcome", "text": "Accueil", "icon": "🏠", "active": True},
            {"name": "dashboard", "text": "Tableau de Bord", "icon": "📊", "active": False},
            {"name": "calibration", "text": "Calibration", "icon": "⚙️", "active": False},
            {"name": "acquisition", "text": "Acquisition", "icon": "📡", "active": False},
            {"name": "analysis", "text": "Analyse", "icon": "📈", "active": False},
            {"name": "export", "text": "Rapport", "icon": "📋", "active": False},
            {"name": "settings", "text": "Paramètres", "icon": "🛠️", "active": False},
        ]

        main_section = QLabel("NAVIGATION")
        main_section.setFont(QFont("Inter", 10, QFont.Weight.Bold))
        main_section.setStyleSheet("color: #445868; margin: 13px 0 8px 0;")
        self.nav_layout.addWidget(main_section)

        for item in navigation_items:
            button = NavigationButton(
                text=item["text"],
                icon_text=item["icon"],
                is_active=item["active"],
            )
            button.clicked.connect(
                lambda checked=False, name=item["name"]: self.navigate_to(name)
            )
            self.navigation_buttons[item["name"]] = button
            self.nav_layout.addWidget(button)

        self.nav_layout.addSpacerItem(
            QSpacerItem(20, FIBONACCI_SPACING[2], QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        )

        tools_section = QLabel("OUTILS")
        tools_section.setFont(QFont("Inter", 10, QFont.Weight.Bold))
        tools_section.setStyleSheet("color: #445868; margin: 13px 0 8px 0;")
        self.nav_layout.addWidget(tools_section)

        for name, text, icon in (
            ("help", "Aide", "❓"),
            ("about", "À propos", "ℹ️"),
        ):
            button = NavigationButton(text=text, icon_text=icon, is_active=False)
            button.clicked.connect(lambda checked=False, name=name: self.navigate_to(name))
            self.navigation_buttons[name] = button
            self.nav_layout.addWidget(button)

    def setup_footer(self, parent_layout) -> None:
        footer_frame = QFrame()
        footer_frame.setObjectName("sidebar_footer")
        footer_frame.setFixedHeight(55)

        footer_layout = QVBoxLayout(footer_frame)
        footer_layout.setContentsMargins(13, 13, 13, 13)
        footer_layout.setSpacing(8)

        status_layout = QHBoxLayout()
        status_indicator = QLabel("●")
        status_indicator.setFont(QFont("Arial", 11))
        status_indicator.setStyleSheet("color: #4CAF50;")

        self.status_text = QLabel("Système prêt")
        self.status_text.setFont(QFont("Inter", 10))
        self.status_text.setStyleSheet("color: #445868;")

        status_layout.addWidget(status_indicator)
        status_layout.addWidget(self.status_text)
        status_layout.addStretch()
        footer_layout.addLayout(status_layout)

        footer_frame.setStyleSheet(
            """
            QFrame#sidebar_footer {
                background-color: #F5FBFF;
                border-top: 1px solid #E0E7FF;
            }
            """
        )
        parent_layout.addWidget(footer_frame)

    def navigate_to(self, view_name: str) -> None:
        if self.current_view in self.navigation_buttons:
            self.navigation_buttons[self.current_view].set_active(False)

        if view_name in self.navigation_buttons:
            self.navigation_buttons[view_name].set_active(True)

        self.current_view = view_name
        self.navigation_requested.emit(view_name)

    def set_active_view(self, view_name: str) -> None:
        if view_name not in self.navigation_buttons:
            return
        if view_name != self.current_view:
            self.navigate_to(view_name)

    def get_active_view(self) -> str:
        return self.current_view

    def set_theme(self, is_dark: bool) -> None:
        if is_dark:
            self.setStyleSheet(
                """
                QFrame#main_sidebar {
                    background-color: #0A1929;
                    border-right: 2px solid #2B79B6;
                }
                QFrame#sidebar_header {
                    background-color: #0A1929;
                    border-bottom: 1px solid #2B79B6;
                }
                QFrame#sidebar_footer {
                    background-color: #0A1929;
                    border-top: 1px solid #2B79B6;
                }
                QLabel {
                    color: #F5FBFF;
                }
                """
            )
        else:
            self.setStyleSheet(
                """
                QFrame#main_sidebar {
                    background-color: #F5FBFF;
                    border-right: 2px solid #E0E7FF;
                }
                QFrame#sidebar_header {
                    background-color: #F5FBFF;
                    border-bottom: 1px solid #E0E7FF;
                }
                QFrame#sidebar_footer {
                    background-color: #F5FBFF;
                    border-top: 1px solid #E0E7FF;
                }
                """
            )

        for button in self.navigation_buttons.values():
            button.apply_style()

    def collapse_sidebar(self, collapsed: bool) -> None:
        self.is_collapsed = collapsed
        self.setFixedWidth(55 if collapsed else 250)
        for button in self.navigation_buttons.values():
            button.text_label.setVisible(not collapsed)

    def update_connection_status(self, connected: bool, message: str = "") -> None:
        if message:
            self.status_text.setText(message)
        else:
            self.status_text.setText("Système connecté" if connected else "Système hors ligne")
