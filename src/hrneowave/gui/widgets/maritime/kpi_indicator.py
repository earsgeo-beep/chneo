# -*- coding: utf-8 -*-
"""
KPI indicator widget for the CHNeoWave maritime design system.
"""

from typing import Optional, Union

try:
    from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
    from PySide6.QtCore import Qt, Signal, QTimer, QSize
    from PySide6.QtGui import QPixmap
except ImportError:
    try:
        from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
        from PyQt6.QtCore import Qt, pyqtSignal as Signal, QTimer, QSize
        from PyQt6.QtGui import QPixmap
    except ImportError:
        from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
        from PyQt5.QtCore import Qt, pyqtSignal as Signal, QTimer, QSize
        from PyQt5.QtGui import QPixmap

from .maritime_card import MaritimeCard


class KPIIndicator(MaritimeCard):
    """Card-based KPI widget with optional icon and animated numeric updates."""

    value_changed = Signal(float)
    threshold_exceeded = Signal(str, float)

    STATE_NORMAL = "normal"
    STATE_WARNING = "warning"
    STATE_ERROR = "error"
    STATE_SUCCESS = "success"

    _VALID_STATES = {
        STATE_NORMAL,
        STATE_WARNING,
        STATE_ERROR,
        STATE_SUCCESS,
    }

    def __init__(self, *args, **kwargs):
        parent, label, value, unit, icon_path, precision, state = self._parse_arguments(
            *args, **kwargs
        )

        super().__init__(parent=parent)

        self.label_text = label
        self.unit = unit
        self.icon_path = icon_path
        self.precision = max(0, int(precision))
        self.state = state

        self.warning_threshold = None
        self.error_threshold = None

        self._raw_value = value
        numeric_value = self._coerce_numeric_value(value)
        self._current_value = numeric_value if numeric_value is not None else 0.0
        self._target_value = self._current_value
        self.animation_steps = 0
        self.animation_total_steps = 20
        self.animation_start_value = self._current_value
        self.animation_end_value = self._current_value

        self._setup_value_animation()
        self._setup_ui()
        self._apply_kpi_style()
        self._update_display_value()

    def _parse_arguments(self, *args, **kwargs):
        """Support both legacy and current constructor calling styles."""
        parent = kwargs.pop("parent", None)
        label = kwargs.pop("label", "Metric")
        value = kwargs.pop("value", 0)
        unit = kwargs.pop("unit", "")
        icon_path = kwargs.pop("icon_path", None)
        precision = kwargs.pop("precision", 1)
        state = kwargs.pop("state", self.STATE_NORMAL)

        remaining = list(args)

        if remaining and isinstance(remaining[0], QWidget):
            parent = remaining.pop(0)

        if remaining:
            label = remaining.pop(0)
        if remaining:
            value = remaining.pop(0)
        if remaining:
            third = remaining.pop(0)
            if isinstance(third, str) and third in self._VALID_STATES:
                state = third
            else:
                unit = third
        if remaining:
            icon_path = remaining.pop(0)
        if remaining:
            precision = remaining.pop(0)
        if remaining:
            state = remaining.pop(0)
        if remaining:
            raise TypeError("Too many positional arguments for KPIIndicator")
        if kwargs:
            unknown = ", ".join(sorted(kwargs.keys()))
            raise TypeError(f"Unexpected keyword arguments for KPIIndicator: {unknown}")

        if state not in self._VALID_STATES:
            state = self.STATE_NORMAL

        return parent, str(label), value, str(unit), icon_path, precision, state

    def _setup_value_animation(self):
        self.value_animation = QTimer()
        self.value_animation.timeout.connect(self._animate_step)

    def _setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(self.FIBONACCI_SPACES[0])
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        if self.icon_path:
            self.icon_label = QLabel()
            self.icon_label.setObjectName("kpi_icon")
            self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._load_icon()
            main_layout.addWidget(self.icon_label)

        self.value_label = QLabel()
        self.value_label.setObjectName("kpi_value")
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.value_label)

        self.label_widget = QLabel(self.label_text)
        self.label_widget.setObjectName("kpi_label")
        self.label_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_widget.setWordWrap(True)
        main_layout.addWidget(self.label_widget)

        content_widget = QWidget()
        content_widget.setLayout(main_layout)
        self.add_widget(content_widget)

    def _load_icon(self):
        if not (self.icon_path and hasattr(self, "icon_label")):
            return

        pixmap = QPixmap(self.icon_path)
        if pixmap.isNull():
            return

        icon_size = self.FIBONACCI_SPACES[2]
        scaled_pixmap = pixmap.scaled(
            icon_size,
            icon_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.icon_label.setPixmap(scaled_pixmap)

    def _coerce_numeric_value(self, value) -> Optional[float]:
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    def _format_numeric_value(self, value: float) -> str:
        if self.precision == 0:
            formatted = f"{int(value)}"
        else:
            formatted = f"{value:.{self.precision}f}"
        return f"{formatted} {self.unit}".strip()

    def _apply_kpi_style(self):
        value_color = self.MARITIME_COLORS["harbor_blue"]
        if self.state == self.STATE_SUCCESS:
            value_color = self.MARITIME_COLORS["emerald_success"]
        elif self.state == self.STATE_WARNING:
            value_color = "#FF8F00"
        elif self.state == self.STATE_ERROR:
            value_color = self.MARITIME_COLORS["coral_alert"]

        self.setStyleSheet(
            f"""
            QLabel#kpi_value {{
                font-size: 32px;
                font-weight: 600;
                color: {value_color};
                margin: {self.FIBONACCI_SPACES[0]}px 0;
            }}

            QLabel#kpi_label {{
                font-size: 12px;
                font-weight: 400;
                color: {self.MARITIME_COLORS['slate_gray']};
            }}
            """
        )

    def _update_display_value(self, animated_value: Optional[float] = None):
        if animated_value is not None:
            text = self._format_numeric_value(animated_value)
        else:
            numeric_value = self._coerce_numeric_value(self._raw_value)
            if numeric_value is None:
                text = str(self._raw_value)
            else:
                text = self._format_numeric_value(self._current_value)

        if hasattr(self, "value_label"):
            self.value_label.setText(text)

    def _animate_step(self):
        if self.animation_steps >= self.animation_total_steps:
            self.value_animation.stop()
            self._current_value = self.animation_end_value
            self._update_display_value()
            return

        progress = self.animation_steps / self.animation_total_steps
        eased_progress = 1 - pow(1 - progress, 3)
        interpolated_value = self.animation_start_value + (
            (self.animation_end_value - self.animation_start_value) * eased_progress
        )
        self._update_display_value(interpolated_value)
        self.animation_steps += 1

    def set_value(self, value: Union[int, float, str], animate: bool = True):
        self._raw_value = value
        numeric_value = self._coerce_numeric_value(value)

        if numeric_value is None:
            self.value_animation.stop()
            self._current_value = 0.0
            self._target_value = 0.0
            self._update_display_value()
            return

        if animate and abs(numeric_value - self._current_value) > 0.001:
            self._target_value = numeric_value
            self.animation_start_value = self._current_value
            self.animation_end_value = numeric_value
            self.animation_steps = 0
            self.value_animation.start(40)
        else:
            self._current_value = numeric_value
            self._target_value = numeric_value
            self._update_display_value()

        self._check_thresholds(numeric_value)
        self._update_state_from_value(numeric_value)
        self.value_changed.emit(numeric_value)

    def _check_thresholds(self, value: float):
        if self.error_threshold is not None and value >= self.error_threshold:
            self.threshold_exceeded.emit("error", value)
        elif self.warning_threshold is not None and value >= self.warning_threshold:
            self.threshold_exceeded.emit("warning", value)

    def _update_state_from_value(self, value: float):
        old_state = self.state

        if self.error_threshold is not None and value >= self.error_threshold:
            self.state = self.STATE_ERROR
        elif self.warning_threshold is not None and value >= self.warning_threshold:
            self.state = self.STATE_WARNING
        elif old_state not in {self.STATE_SUCCESS, self.STATE_NORMAL}:
            self.state = self.STATE_NORMAL

        if old_state != self.state:
            self._apply_kpi_style()

    def set_label(self, label: str):
        self.label_text = label
        if hasattr(self, "label_widget"):
            self.label_widget.setText(label)

    def set_unit(self, unit: str):
        self.unit = unit
        self._update_display_value()

    def set_precision(self, precision: int):
        self.precision = max(0, precision)
        self._update_display_value()

    def set_state(self, state: str):
        if state in self._VALID_STATES:
            self.state = state
            self._apply_kpi_style()

    def set_thresholds(self, warning: Optional[float] = None, error: Optional[float] = None):
        self.warning_threshold = warning
        self.error_threshold = error
        numeric_value = self._coerce_numeric_value(self._raw_value)
        if numeric_value is not None:
            self._update_state_from_value(numeric_value)

    def set_icon(self, icon_path: Optional[str]):
        self.icon_path = icon_path
        if hasattr(self, "icon_label"):
            if icon_path:
                self._load_icon()
            else:
                self.icon_label.clear()

    def get_value(self):
        numeric_value = self._coerce_numeric_value(self._raw_value)
        return numeric_value if numeric_value is not None else self._raw_value

    def get_state(self) -> str:
        return self.state

    def reset(self):
        self.set_value(0, animate=True)
        self.set_state(self.STATE_NORMAL)

    def get_animated_value(self):
        return self._current_value

    def set_animated_value(self, value):
        self._current_value = float(value)
        self._update_display_value(float(value))

    animated_value = property(get_animated_value, set_animated_value)

    def sizeHint(self):
        base_width = 200
        base_height = int(base_width / self.GOLDEN_RATIO)
        return super().sizeHint().expandedTo(QSize(base_width, base_height))
