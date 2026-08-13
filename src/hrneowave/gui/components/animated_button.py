"""Compatibility button with native Qt interaction and global styling."""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QPushButton


class AnimatedButton(QPushButton):
    """Historical name retained; animations and embedded styles were removed."""

    hoverEntered = Signal()
    hoverLeft = Signal()

    def enterEvent(self, event) -> None:  # noqa: N802
        super().enterEvent(event)
        self.hoverEntered.emit()

    def leaveEvent(self, event) -> None:  # noqa: N802
        super().leaveEvent(event)
        self.hoverLeft.emit()
