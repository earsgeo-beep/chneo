"""Application-wide visual theme loader.

CHNeoWave deliberately ships one production theme.  Keeping a single QSS
source prevents view-specific theme stacks from fighting each other.
"""

import logging
from pathlib import Path

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QApplication


class ThemeManager(QObject):
    """Load the canonical laboratory stylesheet."""

    theme_changed = Signal(str)
    CANONICAL_THEME = "laboratory"
    _ALIASES = {"light", "dark", "maritime_modern", "professional", "laboratory"}

    def __init__(self, app: QApplication):
        super().__init__(app)
        self.app = app
        self._styles_dir = Path(__file__).parent
        self._logger = logging.getLogger(__name__)
        self._current_theme = ""
        self.available_themes = sorted(self._ALIASES)

    def _load_stylesheet(self) -> str:
        theme_path = self._styles_dir / "maritime_modern.qss"
        try:
            return theme_path.read_text(encoding="utf-8")
        except OSError as exc:
            self._logger.error("Impossible de charger le theme %s: %s", theme_path, exc)
            return ""

    def apply_theme(self, theme_name: str = CANONICAL_THEME) -> None:
        """Apply the only supported production theme.

        Historical names remain accepted so old preferences cannot break the
        application, but they all resolve to the same visual system.
        """

        if theme_name not in self._ALIASES:
            self._logger.warning("Theme inconnu '%s'; theme laboratoire utilise", theme_name)

        stylesheet = self._load_stylesheet()
        if not stylesheet:
            return

        self.app.setStyleSheet(stylesheet)
        if self._current_theme != self.CANONICAL_THEME:
            self._current_theme = self.CANONICAL_THEME
            self.theme_changed.emit(self.CANONICAL_THEME)
        self._logger.info("Theme laboratoire applique")

    def toggle_theme(self) -> None:
        """Compatibility hook: CHNeoWave intentionally keeps one theme."""

        self.apply_theme(self.CANONICAL_THEME)

    def apply_maritime_modern_theme(self) -> None:
        self.apply_theme(self.CANONICAL_THEME)

    def get_current_theme(self) -> str:
        return self._current_theme
