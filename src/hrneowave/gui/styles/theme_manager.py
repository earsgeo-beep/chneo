"""Light/dark scientific themes for the CHNeoWave instrument shell."""

import logging
from pathlib import Path

from PySide6.QtCore import QObject, QSettings, Signal
from PySide6.QtWidgets import QApplication

PALETTES = {
    "light": {
        "BG": "#F3F5F6",
        "TOPBAR": "#F8FAFA",
        "PANEL": "#FFFFFF",
        "PANEL_ALT": "#F6F8F9",
        "HEADER": "#F1F4F5",
        "CANVAS": "#FCFDFD",
        "TEXT": "#263840",
        "TEXT_STRONG": "#102B35",
        "MUTED": "#647781",
        "BORDER": "#DCE3E6",
        "BORDER_STRONG": "#BCC9CE",
        "INPUT": "#FFFFFF",
        "BUTTON": "#F5F8F9",
        "HOVER": "#E8F0F2",
        "DISABLED": "#E7ECEE",
        "ACCENT": "#087F99",
        "ACCENT_HOVER": "#056B81",
        "ACCENT_SOFT": "#DCEEF2",
        "ACCENT_TEXT": "#FFFFFF",
        "SUCCESS": "#1B7B5E",
        "WARNING": "#A66B16",
        "DANGER": "#A9434D",
        "TOOLTIP": "#F7FAFB",
        "CHROME": "#0B1820",
        "CHROME_TEXT": "#D7E1E5",
        "CHROME_MUTED": "#9EB0B8",
        "CHROME_BORDER": "#263A44",
        "CHROME_HOVER": "#172B35",
        "CHROME_ACTIVE": "#12313E",
        "MEASURE": "#25B3CD",
    },
    "dark": {
        "BG": "#08141B",
        "TOPBAR": "#0E1C24",
        "PANEL": "#0F2029",
        "PANEL_ALT": "#0B1A22",
        "HEADER": "#132731",
        "CANVAS": "#071820",
        "TEXT": "#CDD7DB",
        "TEXT_STRONG": "#F1F5F6",
        "MUTED": "#8FA1A9",
        "BORDER": "#20343E",
        "BORDER_STRONG": "#38505B",
        "INPUT": "#0A1921",
        "BUTTON": "#172A34",
        "HOVER": "#1C3540",
        "DISABLED": "#14242C",
        "ACCENT": "#32AEC5",
        "ACCENT_HOVER": "#49BCD1",
        "ACCENT_SOFT": "#163D48",
        "ACCENT_TEXT": "#071A24",
        "SUCCESS": "#4BC39B",
        "WARNING": "#E0A044",
        "DANGER": "#E16670",
        "TOOLTIP": "#102A34",
        "CHROME": "#06131A",
        "CHROME_TEXT": "#DCE5E8",
        "CHROME_MUTED": "#96A9B1",
        "CHROME_BORDER": "#213943",
        "CHROME_HOVER": "#122A34",
        "CHROME_ACTIVE": "#12313E",
        "MEASURE": "#35BCD5",
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
