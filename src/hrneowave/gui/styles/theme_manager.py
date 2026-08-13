"""Light/dark scientific themes for the CHNeoWave instrument shell."""

import logging
from pathlib import Path

from PySide6.QtCore import QObject, QSettings, Signal
from PySide6.QtWidgets import QApplication

PALETTES = {
    "light": {
        "BG": "#E9EEF1",
        "TOPBAR": "#F7F9FA",
        "PANEL": "#FFFFFF",
        "PANEL_ALT": "#F3F6F7",
        "HEADER": "#EEF2F4",
        "CANVAS": "#FCFDFD",
        "TEXT": "#24363E",
        "TEXT_STRONG": "#102A34",
        "MUTED": "#627781",
        "BORDER": "#D4DEE2",
        "BORDER_STRONG": "#B8C7CD",
        "INPUT": "#FFFFFF",
        "BUTTON": "#F5F8F9",
        "HOVER": "#E0EBEE",
        "DISABLED": "#E2E8EA",
        "ACCENT": "#006F8C",
        "ACCENT_HOVER": "#005F78",
        "ACCENT_SOFT": "#D4E9EE",
        "ACCENT_TEXT": "#FFFFFF",
        "SUCCESS": "#137A5B",
        "WARNING": "#9A651A",
        "DANGER": "#A63E49",
        "TOOLTIP": "#F7FAFB",
    },
    "dark": {
        "BG": "#11191E",
        "TOPBAR": "#172128",
        "PANEL": "#18242A",
        "PANEL_ALT": "#141F25",
        "HEADER": "#1D2B32",
        "CANVAS": "#101B21",
        "TEXT": "#C7D2D6",
        "TEXT_STRONG": "#F0F4F5",
        "MUTED": "#8B9CA4",
        "BORDER": "#293A42",
        "BORDER_STRONG": "#40545D",
        "INPUT": "#111D23",
        "BUTTON": "#213139",
        "HOVER": "#293D46",
        "DISABLED": "#1B282E",
        "ACCENT": "#2AA9C2",
        "ACCENT_HOVER": "#46B9CF",
        "ACCENT_SOFT": "#1D4854",
        "ACCENT_TEXT": "#071A24",
        "SUCCESS": "#4BC39B",
        "WARNING": "#E0A044",
        "DANGER": "#E16670",
        "TOOLTIP": "#142F3A",
    },
}


class ThemeManager(QObject):
    """Apply and persist the two production themes."""

    theme_changed = Signal(str)
    CANONICAL_THEME = "light"
    _ALIASES = {"laboratory", "maritime_modern", "professional"}

    def __init__(self, app: QApplication):
        super().__init__(app)
        self.app = app
        self._logger = logging.getLogger(__name__)
        self._settings = QSettings("CHNeoWave", "CHNeoWave")
        self._template_path = Path(__file__).with_name("instrument.qss")
        self._current_theme = ""
        self.available_themes = ["light", "dark"]

    def _stylesheet(self, theme_name: str) -> str:
        try:
            stylesheet = self._template_path.read_text(encoding="utf-8")
        except OSError as exc:
            self._logger.error("Impossible de charger %s: %s", self._template_path, exc)
            return ""
        for token, value in PALETTES[theme_name].items():
            stylesheet = stylesheet.replace(f"@{token}@", value)
        return stylesheet

    def apply_theme(self, theme_name: str = "laboratory") -> None:
        if theme_name in self._ALIASES:
            theme_name = str(self._settings.value("interface/theme", "light"))
        if theme_name not in PALETTES:
            theme_name = "light"
        stylesheet = self._stylesheet(theme_name)
        if not stylesheet:
            return
        self.app.setStyleSheet(stylesheet)
        self.app.setProperty("chneowaveTheme", theme_name)
        self._settings.setValue("interface/theme", theme_name)
        changed = self._current_theme != theme_name
        self._current_theme = theme_name
        if changed:
            self.theme_changed.emit(theme_name)
        self._logger.info("Theme instrumental %s applique", theme_name)

    def toggle_theme(self) -> None:
        self.apply_theme("light" if self._current_theme == "dark" else "dark")

    def apply_maritime_modern_theme(self) -> None:
        self.apply_theme("laboratory")

    def get_current_theme(self) -> str:
        return self._current_theme or "light"
