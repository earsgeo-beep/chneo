"""Application-wide CHNeoWave light/dark instrument theme manager."""

from __future__ import annotations

import logging
import re
from pathlib import Path

from PySide6.QtCore import QObject, QSettings, Qt, Signal
from PySide6.QtWidgets import QApplication


class ThemeManager(QObject):
    """Apply and persist one of the two supported laboratory themes."""

    theme_changed = Signal(str)
    CANONICAL_THEME = "light"
    THEMES = ("light", "dark")
    _ALIASES = {
        "laboratory": "light",
        "maritime_modern": "light",
        "professional": "light",
        "high_contrast": "dark",
    }

    # The production QSS is authored as the light theme. Dark mode keeps the
    # same dimensions and hierarchy while translating only semantic colours.
    _DARK_COLORS = {
        "#FFFFFF": "#081820",
        "#F8FAFB": "#0C222C",
        "#F7F9FA": "#0C222C",
        "#F6F9FA": "#0C222C",
        "#F4F8FA": "#E8F1F4",
        "#F3F7F8": "#102B36",
        "#F3F6F8": "#061219",
        "#EEF3F5": "#132B34",
        "#EEF2F4": "#132B34",
        "#EDF3F5": "#132B34",
        "#ECF7F9": "#0F2C36",
        "#EAF6F8": "#0F2C36",
        "#E8FBFD": "#12343E",
        "#E8EEF1": "#132B34",
        "#E6F4EF": "#102E29",
        "#E5ECEF": "#1D3A46",
        "#E4EFF2": "#17323D",
        "#E3E9EC": "#17323D",
        "#E2EAEE": "#1D3A46",
        "#DCEEF2": "#153846",
        "#DCE5EA": "#1D3A46",
        "#D9EBEF": "#17323D",
        "#D8E9EE": "#17323D",
        "#D7E0E4": "#274A57",
        "#D3DEE3": "#274A57",
        "#D2DDE2": "#274A57",
        "#CBD8DE": "#274A57",
        "#C9D6DC": "#315563",
        "#B7C6CD": "#315563",
        "#FFF3DE": "#352915",
        "#F0D19C": "#6B4C1D",
        "#FCEBEC": "#351B1E",
        "#EFC8CB": "#6C3036",
        "#BFE4D7": "#245C4E",
        "#172B35": "#E8F1F4",
        "#203843": "#D9E6EB",
        "#203A45": "#D9E6EB",
        "#38515D": "#C4D4DB",
        "#405965": "#AEC2CB",
        "#4E6673": "#9DB3BD",
        "#54717C": "#9DB3BD",
        "#56707C": "#9DB3BD",
        "#667C88": "#8FAAB5",
        "#76939E": "#8FAAB5",
        "#7F9AA5": "#A8BCC5",
        "#8699A3": "#76939E",
        "#8798A1": "#76939E",
        "#88ADB9": "#2B8298",
        "#8EA6B2": "#8FAAB5",
        "#8FA4AE": "#8FAAB5",
        "#B9C9D1": "#C4D4DB",
        "#1A7188": "#2B9EB2",
        "#2B8298": "#35A9BC",
        "#137E92": "#45D4E7",
        "#145E72": "#45D4E7",
        "#0F4B5C": "#45D4E7",
        "#42B8C6": "#45D4E7",
        "#126A56": "#53C6A0",
        "#8B570F": "#E5A84B",
        "#C47B18": "#E5A84B",
        "#99383F": "#EF8189",
        "#A23F45": "#EF8189",
        "#DCA9AD": "#6C3036",
    }

    ICON_COLORS = {
        "light": {"normal": "#667C88", "active": "#E9FBFD", "header": "#405965"},
        "dark": {"normal": "#8FAAB5", "active": "#E9FBFD", "header": "#B9C9D1"},
    }

    _DARK_OVERRIDES = """
QPushButton#navButton[active="true"] {
    color: #E9FBFD;
}
QPushButton#navButton:hover {
    color: #E9FBFD;
}
QLabel#brandName {
    color: #F4F8FA;
}
QLabel#sidebarStatus,
QLabel#sidebarVersion {
    color: #B9C9D1;
}
"""

    def __init__(self, app: QApplication):
        super().__init__(app)
        self.app = app
        self._styles_dir = Path(__file__).parent
        self._logger = logging.getLogger(__name__)
        self._current_theme = ""
        self._settings = QSettings("CHNeoWave", "Interface")
        self.available_themes = list(self.THEMES)

    def _load_stylesheet(self) -> str:
        theme_path = self._styles_dir / "maritime_modern.qss"
        try:
            return theme_path.read_text(encoding="utf-8")
        except OSError as exc:
            self._logger.error("Impossible de charger le theme %s: %s", theme_path, exc)
            return ""

    def preferred_theme(self) -> str:
        saved = str(self._settings.value("theme", self.CANONICAL_THEME))
        return saved if saved in self.THEMES else self.CANONICAL_THEME

    def _resolve_theme(self, theme_name: str | None) -> str:
        name = theme_name or self.preferred_theme()
        name = self._ALIASES.get(name, name)
        if name == "auto":
            hints = self.app.styleHints()
            color_scheme = getattr(hints, "colorScheme", lambda: None)()
            color_scheme_enum = getattr(Qt, "ColorScheme", None)
            dark_scheme = getattr(color_scheme_enum, "Dark", None)
            return "dark" if dark_scheme is not None and color_scheme == dark_scheme else "light"
        if name not in self.THEMES:
            self._logger.warning("Theme inconnu '%s'; theme clair utilise", name)
            return self.CANONICAL_THEME
        return name

    def _stylesheet_for(self, theme: str) -> str:
        stylesheet = self._load_stylesheet()
        if theme != "dark" or not stylesheet:
            return stylesheet
        color_pattern = re.compile(r"#[0-9A-Fa-f]{6}")
        translated = color_pattern.sub(
            lambda match: self._DARK_COLORS.get(match.group(0).upper(), match.group(0)),
            stylesheet,
        )
        return translated + self._DARK_OVERRIDES

    def apply_theme(self, theme_name: str | None = None) -> None:
        theme = self._resolve_theme(theme_name)
        stylesheet = self._stylesheet_for(theme)
        if not stylesheet:
            return

        self.app.setProperty("chneoTheme", theme)
        self.app.setStyleSheet(stylesheet)
        self._settings.setValue("theme", theme)
        self._settings.sync()
        if self._current_theme != theme:
            self._current_theme = theme
            self.theme_changed.emit(theme)
        self._logger.info("Theme instrument CHNeoWave applique: %s", theme)

    def toggle_theme(self) -> None:
        self.apply_theme("light" if self._current_theme == "dark" else "dark")

    def apply_maritime_modern_theme(self) -> None:
        self.apply_theme(self.preferred_theme())

    def get_current_theme(self) -> str:
        return self._current_theme or self.preferred_theme()

    def icon_colors(self) -> dict[str, str]:
        return dict(self.ICON_COLORS[self.get_current_theme()])
