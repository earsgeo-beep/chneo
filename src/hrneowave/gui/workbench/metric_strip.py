"""Dense scalar readout strip for scientific results."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout


class _Readout(QFrame):
    def __init__(self, key: str, label: str, unit: str = "", parent=None):
        super().__init__(parent)
        self.key = key
        self.setObjectName("resultReadout")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(0)
        caption = QLabel(label.upper())
        caption.setObjectName("readoutCaption")
        value_row = QHBoxLayout()
        value_row.setSpacing(4)
        self.value_label = QLabel("—")
        self.value_label.setObjectName("readoutValue")
        self.unit_label = QLabel(unit)
        self.unit_label.setObjectName("readoutUnit")
        value_row.addWidget(self.value_label)
        value_row.addWidget(self.unit_label, 0, Qt.AlignmentFlag.AlignBottom)
        value_row.addStretch()
        self.detail_label = QLabel("non calculé")
        self.detail_label.setObjectName("readoutDetail")
        layout.addWidget(caption)
        layout.addLayout(value_row)
        layout.addWidget(self.detail_label)

    def set_value(
        self, value: str, detail: str = "", state: str = "neutral", unit: str | None = None
    ) -> None:
        self.value_label.setText(value)
        self.detail_label.setText(detail)
        if unit is not None:
            self.unit_label.setText(unit)
        self.setProperty("state", state)
        self.style().unpolish(self)
        self.style().polish(self)


class MetricStrip(QFrame):
    DEFINITIONS = (
        ("hm0", "Hm0", "m"),
        ("tp", "Tp", "s"),
        ("tm01", "Tm01", "s"),
        ("rms", "RMS", ""),
        ("df", "Δf", "Hz"),
        ("quality", "Diagnostic auto", ""),
        ("verdict", "Décision ingénieur", ""),
    )

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("metricStrip")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.readouts = {}
        for key, label, unit in self.DEFINITIONS:
            readout = _Readout(key, label, unit)
            self.readouts[key] = readout
            layout.addWidget(readout, 1)

    def set_metric(
        self,
        key: str,
        value: str,
        detail: str = "",
        state: str = "neutral",
        unit: str | None = None,
    ) -> None:
        if key in self.readouts:
            self.readouts[key].set_value(value, detail, state, unit)

    def clear(self) -> None:
        for readout in self.readouts.values():
            readout.set_value("—", "non calculé", "neutral")
