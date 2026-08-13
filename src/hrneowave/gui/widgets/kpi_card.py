"""Small numerical readout retained for the project settings workspace."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout


class KPICard(QFrame):
    """A restrained status readout with no embedded theme or animation."""

    clicked = Signal(str)
    value_changed = Signal(str, str)

    def __init__(
        self,
        title: str,
        value: str,
        unit: str = "",
        status: str = "normal",
        parent=None,
    ):
        super().__init__(parent)
        self.title = title
        self.current_value = value
        self.unit = unit
        self.status = status
        self.setObjectName("settingsReadout")
        self.setProperty("status", status)
        self.setMinimumSize(150, 72)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(3)
        self.title_label = QLabel(title.upper())
        self.title_label.setObjectName("readoutCaption")
        value_row = QHBoxLayout()
        value_row.setSpacing(5)
        self.value_label = QLabel(value)
        self.value_label.setObjectName("readoutValue")
        self.unit_label = QLabel(unit)
        self.unit_label.setObjectName("readoutUnit")
        value_row.addWidget(self.value_label)
        value_row.addWidget(self.unit_label)
        value_row.addStretch()
        layout.addWidget(self.title_label)
        layout.addLayout(value_row)

    def update_value(self, new_value: str, new_status: str | None = None) -> None:
        self.current_value = str(new_value)
        self.value_label.setText(self.current_value)
        if new_status:
            self.set_status(new_status)
        self.value_changed.emit(self.title, self.current_value)

    def set_status(self, new_status: str) -> None:
        self.status = new_status
        self.setProperty("status", new_status)
        self.style().unpolish(self)
        self.style().polish(self)

    def set_theme(self, is_dark: bool) -> None:
        del is_dark

    def get_value(self) -> str:
        return self.current_value

    def get_status(self) -> str:
        return self.status

    def set_clickable(self, clickable: bool) -> None:
        self.setCursor(
            Qt.CursorShape.PointingHandCursor if clickable else Qt.CursorShape.ArrowCursor
        )

    def mousePressEvent(self, event) -> None:  # noqa: N802
        super().mousePressEvent(event)
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.title)
