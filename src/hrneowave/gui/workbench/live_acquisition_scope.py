"""Oscilloscope roulant pour les acquisitions matérielles CHNeoWave."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import numpy as np
from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
)

from .plot_widget import ScientificPlotWidget

if TYPE_CHECKING:
    from ...acquisition.acquisition_controller import AcquisitionController, AcquisitionSession


CHANNEL_COLORS = (
    "#19B5CF",
    "#E4A03A",
    "#53C49B",
    "#D56B76",
    "#8779D8",
    "#62A1E8",
    "#C57CB4",
    "#A6B84D",
    "#E17E45",
    "#5EC2B7",
    "#B09562",
    "#7B9BB0",
)


class LiveAcquisitionScope(QFrame):
    """Affiche une copie du tampon récent sans intervenir sur l'enregistrement.

    Le widget ne démarre, n'arrête et ne configure jamais le matériel. Il lit
    uniquement les instantanés publiés par :class:`AcquisitionController`.
    """

    latest_values_changed = Signal(object, object, object)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("liveAcquisitionScope")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._controller: AcquisitionController | None = None
        self._session: AcquisitionSession | None = None
        self._theme = "light"
        self._last_snapshot: dict[str, Any] | None = None
        self._last_render_key: tuple[Any, ...] | None = None
        self._build_ui()
        self._connect_controls()
        self._set_session_controls_enabled(False)

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        controls = QFrame()
        controls.setObjectName("liveScopeControls")
        controls_layout = QHBoxLayout(controls)
        controls_layout.setContentsMargins(8, 4, 8, 4)
        controls_layout.setSpacing(6)

        self.state_label = QLabel("PRÊT · AUCUNE SESSION")
        self.state_label.setObjectName("liveScopeState")
        self.state_label.setProperty("state", "neutral")
        controls_layout.addWidget(self.state_label)
        controls_layout.addSpacing(8)

        self.channel_combo = QComboBox()
        self.channel_combo.setObjectName("liveScopeChannel")
        self.channel_combo.setMinimumWidth(135)
        self.channel_combo.setToolTip("Voie affichée")
        controls_layout.addWidget(self.channel_combo)

        self.measure_combo = QComboBox()
        self.measure_combo.addItem("BRUT · V", "raw")
        self.measure_combo.addItem("PHYSIQUE", "processed")
        self.measure_combo.setToolTip("Tension mesurée ou grandeur calibrée")
        controls_layout.addWidget(self.measure_combo)

        controls_layout.addWidget(self._caption("Fenêtre"))
        self.window_combo = QComboBox()
        for seconds in (2, 5, 10, 30, 60):
            self.window_combo.addItem(f"{seconds} s", seconds)
        self.window_combo.setCurrentIndex(2)
        controls_layout.addWidget(self.window_combo)

        self.auto_y_check = QCheckBox("Y auto")
        self.auto_y_check.setChecked(True)
        controls_layout.addWidget(self.auto_y_check)
        self.y_min_spin = self._range_spin("Y min")
        self.y_min_spin.setValue(-1.0)
        self.y_max_spin = self._range_spin("Y max")
        self.y_max_spin.setValue(1.0)
        controls_layout.addWidget(self.y_min_spin)
        controls_layout.addWidget(self.y_max_spin)

        controls_layout.addStretch()
        self.pause_button = QPushButton("PAUSE AFFICHAGE")
        self.pause_button.setObjectName("liveScopePause")
        self.pause_button.setCheckable(True)
        self.pause_button.setToolTip(
            "Fige uniquement le graphe; l'acquisition et l'enregistrement HDF5 continuent."
        )
        controls_layout.addWidget(self.pause_button)
        layout.addWidget(controls)

        self.plot = ScientificPlotWidget(
            "Oscilloscope acquisition",
            "Temps session (s)",
            "Tension brute (V)",
        )
        self.plot.tool_buttons["region"].hide()
        self.plot.tool_buttons["legend"].setChecked(False)
        self.plot.set_legend_visible(False)
        self.plot.set_title_metadata("AUCUN BLOC MATÉRIEL")
        layout.addWidget(self.plot, 1)

        readouts = QFrame()
        readouts.setObjectName("liveScopeReadouts")
        readout_layout = QHBoxLayout(readouts)
        readout_layout.setContentsMargins(9, 3, 9, 3)
        readout_layout.setSpacing(0)
        self.latest_readout = self._readout(readout_layout, "DERNIÈRE", "—")
        self.minimum_readout = self._readout(readout_layout, "MIN", "—")
        self.maximum_readout = self._readout(readout_layout, "MAX", "—")
        self.peak_to_peak_readout = self._readout(readout_layout, "CRÊTE-À-CRÊTE", "—")
        self.points_readout = self._readout(readout_layout, "POINTS VISIBLES", "0")
        layout.addWidget(readouts)

    @staticmethod
    def _caption(text: str) -> QLabel:
        label = QLabel(text.upper())
        label.setObjectName("liveScopeCaption")
        return label

    @staticmethod
    def _range_spin(prefix: str) -> QDoubleSpinBox:
        spin = QDoubleSpinBox()
        spin.setObjectName("liveScopeRange")
        spin.setRange(-1_000_000_000.0, 1_000_000_000.0)
        spin.setDecimals(4)
        spin.setSingleStep(0.1)
        spin.setPrefix(f"{prefix}  ")
        spin.setMaximumWidth(110)
        return spin

    @staticmethod
    def _readout(layout: QHBoxLayout, caption: str, value: str) -> QLabel:
        cell = QFrame()
        cell.setObjectName("liveScopeReadout")
        cell_layout = QHBoxLayout(cell)
        cell_layout.setContentsMargins(9, 2, 9, 2)
        cell_layout.setSpacing(6)
        caption_label = QLabel(caption)
        caption_label.setObjectName("liveScopeReadoutCaption")
        value_label = QLabel(value)
        value_label.setObjectName("liveScopeReadoutValue")
        cell_layout.addWidget(caption_label)
        cell_layout.addWidget(value_label)
        cell_layout.addStretch()
        layout.addWidget(cell, 1)
        return value_label

    def _connect_controls(self) -> None:
        self.channel_combo.currentIndexChanged.connect(self._channel_selection_changed)
        self.measure_combo.currentIndexChanged.connect(self.refresh)
        self.window_combo.currentIndexChanged.connect(self.refresh)
        self.auto_y_check.toggled.connect(self._set_manual_y_enabled)
        self.y_min_spin.valueChanged.connect(self.refresh)
        self.y_max_spin.valueChanged.connect(self.refresh)
        self.pause_button.toggled.connect(self._set_paused)
        self._set_manual_y_enabled(True)

    def bind_controller(self, controller: AcquisitionController | None) -> None:
        self._controller = controller

    def configure_session(self, session: AcquisitionSession | None) -> None:
        self._session = session
        self._last_snapshot = None
        self._last_render_key = None
        self.plot.clear_series()
        self.channel_combo.blockSignals(True)
        self.channel_combo.clear()
        if session is not None:
            self.channel_combo.addItem("Toutes les voies", "all")
            for column, channel in enumerate(session.channels):
                self.channel_combo.addItem(
                    f"CH{channel.channel + 1:02d} · {channel.label}",
                    column,
                )
            if session.channels:
                self.channel_combo.setCurrentIndex(1)
        self.channel_combo.blockSignals(False)
        self.pause_button.setChecked(False)
        self._set_session_controls_enabled(session is not None)
        if session is None:
            self._show_waiting_state()
        else:
            self.state_label.setText("EN ATTENTE DU PREMIER BLOC")
            self.state_label.setProperty("state", "warning")
            self.plot.set_title_metadata(
                f"SOURCE PHYSIQUE · {session.sampling_rate:g} Hz · HDF5 CONTINU"
            )
            self._repolish_state()
            self.refresh()

    def uses_session(self, session: AcquisitionSession | None) -> bool:
        return self._session is session

    def _set_session_controls_enabled(self, enabled: bool) -> None:
        for widget in (
            self.channel_combo,
            self.measure_combo,
            self.window_combo,
            self.auto_y_check,
            self.pause_button,
        ):
            widget.setEnabled(enabled)
        manual_enabled = bool(enabled and not self.auto_y_check.isChecked())
        self.y_min_spin.setEnabled(manual_enabled)
        self.y_max_spin.setEnabled(manual_enabled)
        self.y_min_spin.setVisible(manual_enabled)
        self.y_max_spin.setVisible(manual_enabled)

    def _set_manual_y_enabled(self, automatic: bool) -> None:
        enabled = bool(self._session is not None and not automatic)
        self.y_min_spin.setEnabled(enabled)
        self.y_max_spin.setEnabled(enabled)
        self.y_min_spin.setVisible(enabled)
        self.y_max_spin.setVisible(enabled)
        if automatic:
            self.plot.plot.enableAutoRange(axis="y")
        self.refresh()

    def _channel_selection_changed(self, *_args) -> None:
        all_channels = self.channel_combo.currentData() == "all"
        self.plot.set_legend_visible(all_channels)
        self._last_render_key = None
        self.refresh()

    def _set_paused(self, paused: bool) -> None:
        self.pause_button.setText("REPRENDRE L’AFFICHAGE" if paused else "PAUSE AFFICHAGE")
        if paused:
            recording = bool(self._controller and self._controller.is_acquiring)
            self.state_label.setText(
                "AFFICHAGE FIGÉ · HDF5 ACTIF"
                if recording
                else "AFFICHAGE FIGÉ"
            )
            self.state_label.setProperty("state", "warning")
            self._repolish_state()
        else:
            self._last_render_key = None
            self.refresh()

    def refresh(self, *_args) -> None:
        if self.pause_button.isChecked() or self._controller is None or self._session is None:
            return
        sample_rate = float(self._session.sampling_rate)
        window_seconds = float(self.window_combo.currentData() or 10.0)
        requested_samples = min(
            int(getattr(self._controller, "preview_sample_limit", 100_000)),
            max(2, int(round(window_seconds * sample_rate))),
        )
        selected = self.channel_combo.currentData()
        columns = None if selected == "all" else [int(selected)]
        raw_mode = self.measure_combo.currentData() == "raw"
        try:
            snapshot = self._controller.get_recent_data(
                requested_samples,
                raw=raw_mode,
                channel_indices=columns,
            )
        except (RuntimeError, TypeError, ValueError):
            self.state_label.setText("AFFICHAGE INDISPONIBLE")
            self.state_label.setProperty("state", "danger")
            self._repolish_state()
            return
        if not snapshot or not snapshot.get("sample_count"):
            return

        render_key = (
            snapshot.get("stop_sample_index"),
            selected,
            raw_mode,
            window_seconds,
            self.auto_y_check.isChecked(),
            self.y_min_spin.value(),
            self.y_max_spin.value(),
            bool(getattr(self._controller, "is_acquiring", False)),
        )
        if render_key == self._last_render_key:
            return
        self._last_render_key = render_key

        self._last_snapshot = snapshot
        data = np.asarray(snapshot["data"], dtype=float)
        time_values = np.asarray(snapshot["time_seconds"], dtype=float)
        labels = list(snapshot.get("channels", []))
        units = list(snapshot.get("units", []))
        series: dict[str, tuple[np.ndarray, np.ndarray, str]] = {}
        for column in range(data.shape[1]):
            reduced_time, reduced_values = self._peak_preserving_view(
                time_values,
                data[:, column],
            )
            label = labels[column] if column < len(labels) else f"Canal {column + 1}"
            source_column = columns[column] if columns is not None else column
            series[label] = (
                reduced_time,
                reduced_values,
                CHANNEL_COLORS[source_column % len(CHANNEL_COLORS)],
            )
        self.plot.update_series(series, fit=False)

        right = float(time_values[-1])
        left = max(0.0, right - window_seconds)
        if right <= left:
            right = left + max(1.0 / sample_rate, 1e-6)
        self.plot.set_x_range(left, right, padding=0.0)
        if self.auto_y_check.isChecked():
            self.plot.plot.enableAutoRange(axis="y")
        elif self.y_max_spin.value() > self.y_min_spin.value():
            self.plot.plot.setYRange(
                self.y_min_spin.value(),
                self.y_max_spin.value(),
                padding=0.0,
            )

        unit = "V" if raw_mode else self._axis_unit(units)
        y_label = "Tension brute (V)" if raw_mode else f"Grandeur physique ({unit})"
        self.plot.set_axis_labels("Temps session (s)", y_label)
        kind = "TENSION BRUTE" if raw_mode else "GRANDEUR PHYSIQUE"
        self.plot.set_title_metadata(
            f"{kind} · {sample_rate:g} Hz · N={snapshot['sample_count']} · HDF5 CONTINU"
        )
        self._update_readouts(data[:, 0], units[0] if units else unit)
        self.latest_values_changed.emit(data[-1], labels, units)
        if bool(getattr(self._controller, "is_acquiring", False)):
            self.state_label.setText("ACQUISITION ACTIVE")
            self.state_label.setProperty("state", "success")
        else:
            self.state_label.setText("SESSION TERMINÉE")
            self.state_label.setProperty("state", "neutral")
        self._repolish_state()

    @staticmethod
    def _axis_unit(units: list[str]) -> str:
        normalized = {unit.strip() for unit in units if unit and unit.strip()}
        if len(normalized) == 1:
            return next(iter(normalized))
        return "unités mixtes"

    @staticmethod
    def _peak_preserving_view(
        time_values: np.ndarray,
        signal_values: np.ndarray,
        maximum_points: int = 12_000,
    ) -> tuple[np.ndarray, np.ndarray]:
        """Réduit le coût graphique en conservant les extrema de chaque bloc."""

        count = signal_values.size
        if count <= maximum_points:
            return time_values, signal_values
        block_size = max(2, int(np.ceil(count / (maximum_points / 2))))
        block_count = count // block_size
        usable = block_count * block_size
        blocks = signal_values[:usable].reshape(block_count, block_size)
        minima = np.argmin(blocks, axis=1)
        maxima = np.argmax(blocks, axis=1)
        base = np.arange(block_count) * block_size
        pair_indices = np.column_stack((base + minima, base + maxima))
        pair_indices.sort(axis=1)
        indices = pair_indices.reshape(-1)
        if usable < count:
            indices = np.concatenate((indices, np.asarray([count - 1], dtype=int)))
        return time_values[indices], signal_values[indices]

    def _update_readouts(self, values: np.ndarray, unit: str) -> None:
        finite = values[np.isfinite(values)]
        if not finite.size:
            return
        suffix = f" {unit}" if unit else ""
        self.latest_readout.setText(f"{finite[-1]:.6g}{suffix}")
        self.minimum_readout.setText(f"{np.min(finite):.6g}{suffix}")
        self.maximum_readout.setText(f"{np.max(finite):.6g}{suffix}")
        self.peak_to_peak_readout.setText(f"{np.ptp(finite):.6g}{suffix}")
        self.points_readout.setText(str(finite.size))

    def _show_waiting_state(self) -> None:
        self.plot.clear_series()
        self.plot.set_title_metadata("AUCUN BLOC MATÉRIEL")
        self.state_label.setText("PRÊT · AUCUNE SESSION")
        self.state_label.setProperty("state", "neutral")
        for label in (
            self.latest_readout,
            self.minimum_readout,
            self.maximum_readout,
            self.peak_to_peak_readout,
        ):
            label.setText("—")
        self.points_readout.setText("0")
        self._repolish_state()

    def _repolish_state(self) -> None:
        self.state_label.style().unpolish(self.state_label)
        self.state_label.style().polish(self.state_label)

    def set_theme(self, is_dark: bool) -> None:
        self._theme = "dark" if is_dark else "light"
        self.plot.apply_theme(self._theme)
