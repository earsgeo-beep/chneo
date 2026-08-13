"""Poste d'instrumentation pour la calibration réelle des capteurs."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

import numpy as np
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QDoubleSpinBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QSpinBox,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from ...acquisition import MARITIME_SENSOR_TYPES
from ...core.calibration import CalibrationError, CalibrationPoint, CalibrationRecord
from ...core.live_signal import LiveSignalMetrics, analyze_live_voltage

if TYPE_CHECKING:
    from ...acquisition.acquisition_controller import AcquisitionController


class CalibrationMetric(QFrame):
    """Résultat métrologique compact, sans carte décorative."""

    def __init__(self, label: str, value: str = "—", parent=None):
        super().__init__(parent)
        self.setObjectName("calibrationMetric")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 3, 8, 3)
        layout.setSpacing(0)
        label_widget = QLabel(label)
        label_widget.setObjectName("technicalLabel")
        self.value_widget = QLabel(value)
        self.value_widget.setObjectName("calibrationMetricValue")
        layout.addWidget(label_widget)
        layout.addWidget(self.value_widget)

    def set_value(self, value: str) -> None:
        self.value_widget.setText(value)


class CalibrationView(QWidget):
    """Lit un canal physique, contrôle sa stabilité puis capture les points."""

    calibration_started = Signal()
    calibration_completed = Signal(dict)
    step_changed = Signal(str)
    hardware_setup_requested = Signal()
    preview_block_received = Signal(object, float)
    preview_error_received = Signal(str)

    DEFAULT_POINT_COUNT = 3
    LIVE_WINDOW_SECONDS = 5.0

    def __init__(self, parent=None, channel_count: int = 1):
        super().__init__(parent)
        self.setObjectName("calibrationWorkspace")
        self.channel_count = max(1, int(channel_count))
        self._active_channel = 0
        self._channel_points: dict[int, list[tuple[float, float] | None]] = {}
        self._channel_records: dict[int, CalibrationRecord] = {}
        self._channel_metadata: dict[int, dict[str, Any]] = {}
        self._controller: AcquisitionController | None = None
        self._workspace_active = False
        self._live_values = np.empty(0, dtype=np.float64)
        self._live_times = np.empty(0, dtype=np.float64)
        self._live_sample_index = 0
        self._live_rate_hz = 0.0
        self._last_live_metrics: LiveSignalMetrics | None = None
        self.is_dark_mode = False

        self._build_ui()
        self._setup_connections()
        self._load_channel(0)
        self._set_live_state(False)

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 8, 12, 10)
        root.setSpacing(7)
        root.addWidget(self._create_command_bar())
        self.sensor_settings_panel = self._create_settings_panel()
        self.sensor_settings_panel.setVisible(False)
        root.addWidget(self.sensor_settings_panel)

        self.workspace_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.workspace_splitter.setChildrenCollapsible(False)
        self.workspace_splitter.setHandleWidth(6)
        self.workspace_splitter.addWidget(self._create_plot_workspace())
        self.workspace_splitter.addWidget(self._create_instrument_panel())
        self.workspace_splitter.setStretchFactor(0, 7)
        self.workspace_splitter.setStretchFactor(1, 3)
        self.workspace_splitter.setSizes([850, 360])
        root.addWidget(self.workspace_splitter, 1)
        root.addWidget(self._create_result_strip())

    def _create_command_bar(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("calibrationCommandBar")
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(10, 6, 10, 6)
        layout.setSpacing(6)

        self.previous_channel_button = QPushButton("‹")
        self.next_channel_button = QPushButton("›")
        for button in (self.previous_channel_button, self.next_channel_button):
            button.setProperty("kind", "secondary")
            button.setFixedWidth(32)

        self.channel_progress_label = QLabel(f"CANAL 1 / {self.channel_count}")
        self.channel_progress_label.setObjectName("technicalLabel")
        self.channel_combo = QComboBox()
        self.channel_combo.setMinimumWidth(100)
        for channel in range(self.channel_count):
            self.channel_combo.addItem(f"Canal {channel + 1}", channel)

        self.sensor_identity_label = QLabel("CAP-01 · force · g")
        self.sensor_identity_label.setObjectName("sensorIdentity")
        self.hardware_status_label = QLabel("CARTE ABSENTE")
        self.hardware_status_label.setProperty("state", "danger")
        self.hardware_setup_button = QPushButton("Matériel")
        self.hardware_setup_button.setProperty("kind", "secondary")
        self.settings_toggle_button = QPushButton("Réglages")
        self.settings_toggle_button.setProperty("kind", "quiet")
        self.live_toggle_button = QPushButton("Démarrer lecture")
        self.live_toggle_button.setProperty("kind", "primaryLarge")

        layout.addWidget(self.previous_channel_button)
        layout.addWidget(self.next_channel_button)
        layout.addWidget(self.channel_progress_label)
        layout.addWidget(self.channel_combo)
        layout.addWidget(self.sensor_identity_label)
        layout.addStretch()
        layout.addWidget(self.hardware_status_label)
        layout.addWidget(self.hardware_setup_button)
        layout.addWidget(self.settings_toggle_button)
        layout.addWidget(self.live_toggle_button)
        return frame

    def _create_settings_panel(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("calibrationSettingsPanel")
        layout = QGridLayout(frame)
        layout.setContentsMargins(10, 7, 10, 8)
        layout.setHorizontalSpacing(9)
        layout.setVerticalSpacing(3)

        self.sensor_id_edit = QLineEdit("CAP-01")
        self.sensor_type_combo = QComboBox()
        self.sensor_type_combo.addItems(list(MARITIME_SENSOR_TYPES))
        self.unit_combo = QComboBox()
        self.unit_combo.setEditable(True)
        self.unit_combo.addItems(["g", "kg", "N", "mm", "cm", "m", "°", "bar"])
        self.point_count_spin = QSpinBox()
        self.point_count_spin.setRange(2, 12)
        self.point_count_spin.setValue(self.DEFAULT_POINT_COUNT)
        self.point_count_spin.setSuffix(" points")
        self.voltage_range_combo = QComboBox()
        for limit in (1.0, 2.0, 5.0, 10.0):
            self.voltage_range_combo.addItem(f"±{limit:g} V", limit)
        self.voltage_range_combo.setCurrentIndex(3)
        self.preview_rate_spin = QSpinBox()
        self.preview_rate_spin.setRange(1, 50_000)
        self.preview_rate_spin.setValue(200)
        self.preview_rate_spin.setSuffix(" Hz")
        self.stability_limit_spin = QDoubleSpinBox()
        self.stability_limit_spin.setRange(0.000001, 1.0)
        self.stability_limit_spin.setDecimals(6)
        self.stability_limit_spin.setValue(0.002)
        self.stability_limit_spin.setSuffix(" V RMS")
        self.operator_edit = QLineEdit()
        self.operator_edit.setPlaceholderText("Opérateur")
        self.reference_equipment_edit = QLineEdit()
        self.reference_equipment_edit.setPlaceholderText("Équipement de référence")

        fields = (
            ("CAPTEUR", self.sensor_id_edit),
            ("TYPE", self.sensor_type_combo),
            ("UNITÉ", self.unit_combo),
            ("POINTS", self.point_count_spin),
            ("PLAGE ENTRÉE", self.voltage_range_combo),
            ("LECTURE", self.preview_rate_spin),
            ("STABILITÉ MAX.", self.stability_limit_spin),
            ("OPÉRATEUR", self.operator_edit),
        )
        for index, (label, widget) in enumerate(fields):
            column = index % 4
            row = (index // 4) * 2
            label_widget = QLabel(label)
            label_widget.setObjectName("technicalLabel")
            layout.addWidget(label_widget, row, column)
            layout.addWidget(widget, row + 1, column)
            layout.setColumnStretch(column, 1)

        reference_label = QLabel("RÉFÉRENCE MÉTROLOGIQUE")
        reference_label.setObjectName("technicalLabel")
        layout.addWidget(reference_label, 4, 0)
        layout.addWidget(self.reference_equipment_edit, 5, 0, 1, 4)
        return frame

    def _create_plot_workspace(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("technicalSurface")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        self.plot_tabs = QTabWidget()
        self.plot_tabs.setObjectName("calibrationPlotTabs")
        self.plot_tabs.setDocumentMode(True)

        live_page = QWidget()
        live_layout = QVBoxLayout(live_page)
        live_layout.setContentsMargins(0, 0, 0, 0)
        self.signal_figure = Figure(figsize=(8, 4.8), tight_layout=True)
        self.signal_canvas = FigureCanvas(self.signal_figure)
        self.signal_canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.signal_canvas.setMinimumSize(420, 260)
        live_layout.addWidget(self.signal_canvas)
        self.plot_tabs.addTab(live_page, "Signal live")

        curve_page = QWidget()
        curve_layout = QVBoxLayout(curve_page)
        curve_layout.setContentsMargins(0, 0, 0, 0)
        self.figure = Figure(figsize=(8, 4.8), tight_layout=True)
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.canvas.setMinimumSize(420, 260)
        curve_layout.addWidget(self.canvas)
        self.plot_tabs.addTab(curve_page, "Linéarité")

        layout.addWidget(self.plot_tabs)
        self._initialize_live_plot()
        self._draw_empty_plot()
        return panel

    def _create_instrument_panel(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("instrumentPanel")
        panel.setMinimumWidth(330)
        panel.setMaximumWidth(430)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(11, 9, 11, 9)
        layout.setSpacing(7)

        live_header = QHBoxLayout()
        self.live_state_label = QLabel("HORS LECTURE")
        self.live_state_label.setProperty("state", "neutral")
        self.sample_rate_label = QLabel("— S/s")
        self.sample_rate_label.setObjectName("instrumentRate")
        live_header.addWidget(self.live_state_label)
        live_header.addStretch()
        live_header.addWidget(self.sample_rate_label)
        layout.addLayout(live_header)

        self.live_voltage_label = QLabel("— V")
        self.live_voltage_label.setObjectName("liveVoltage")
        self.live_voltage_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.live_voltage_label)

        self.signal_verdict_label = QLabel("EN ATTENTE DU SIGNAL")
        self.signal_verdict_label.setProperty("state", "neutral")
        self.signal_verdict_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.signal_verdict_label)

        metrics_grid = QGridLayout()
        metrics_grid.setHorizontalSpacing(6)
        metrics_grid.setVerticalSpacing(5)
        self.mean_value_label = self._instrument_metric(metrics_grid, 0, 0, "MOYENNE")
        self.noise_value_label = self._instrument_metric(metrics_grid, 0, 1, "BRUIT RMS")
        self.peak_to_peak_value_label = self._instrument_metric(metrics_grid, 1, 0, "CRÊTE-CRÊTE")
        self.drift_value_label = self._instrument_metric(metrics_grid, 1, 1, "DÉRIVE")
        self.range_value_label = self._instrument_metric(metrics_grid, 2, 0, "MIN / MAX", column_span=2)
        layout.addLayout(metrics_grid)

        divider = QFrame()
        divider.setObjectName("instrumentDivider")
        layout.addWidget(divider)

        reference_header = QHBoxLayout()
        reference_label = QLabel("RÉFÉRENCE APPLIQUÉE")
        reference_label.setObjectName("technicalLabel")
        self.reference_unit_label = QLabel("g")
        self.reference_unit_label.setObjectName("instrumentRate")
        reference_header.addWidget(reference_label)
        reference_header.addStretch()
        reference_header.addWidget(self.reference_unit_label)
        layout.addLayout(reference_header)
        self.reference_spin = QDoubleSpinBox()
        self.reference_spin.setRange(-1_000_000.0, 1_000_000.0)
        self.reference_spin.setDecimals(6)
        layout.addWidget(self.reference_spin)

        capture_actions = QHBoxLayout()
        self.zero_button = QPushButton("Capturer zéro")
        self.zero_button.setProperty("kind", "secondary")
        self.record_point_button = QPushButton("Capturer point")
        self.record_point_button.setProperty("kind", "primary")
        capture_actions.addWidget(self.zero_button)
        capture_actions.addWidget(self.record_point_button, 1)
        layout.addLayout(capture_actions)

        points_header = QHBoxLayout()
        points_label = QLabel("POINTS")
        points_label.setObjectName("technicalLabel")
        self.point_progress_label = QLabel("0 / 3")
        self.point_progress_label.setObjectName("instrumentRate")
        points_header.addWidget(points_label)
        points_header.addStretch()
        points_header.addWidget(self.point_progress_label)
        layout.addLayout(points_header)

        self.points_table = QTableWidget(0, 3)
        self.points_table.setHorizontalHeaderLabels(["Point", "Réf.", "Tension (V)"])
        self.points_table.verticalHeader().setVisible(False)
        self.points_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.points_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.points_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.points_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.points_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.points_table.setAlternatingRowColors(True)
        self.points_table.verticalHeader().setDefaultSectionSize(27)
        self.points_table.setMinimumHeight(105)
        layout.addWidget(self.points_table, 1)

        self.clear_point_button = QPushButton("Effacer le point sélectionné")
        self.clear_point_button.setProperty("kind", "quiet")
        layout.addWidget(self.clear_point_button)

        # Compatibilité de l'API historique: la tension est désormais imposée
        # par la moyenne du signal matériel et n'est plus un champ opérateur.
        self.selected_point_label = QLabel("Point 1 · zéro", self)
        self.selected_point_label.hide()
        self.measured_voltage_spin = QDoubleSpinBox(self)
        self.measured_voltage_spin.setRange(-100.0, 100.0)
        self.measured_voltage_spin.setDecimals(8)
        self.measured_voltage_spin.hide()
        return panel

    @staticmethod
    def _instrument_metric(
        layout: QGridLayout,
        row: int,
        column: int,
        label: str,
        *,
        column_span: int = 1,
    ) -> QLabel:
        frame = QFrame()
        frame.setObjectName("instrumentMetric")
        frame_layout = QVBoxLayout(frame)
        frame_layout.setContentsMargins(7, 4, 7, 4)
        frame_layout.setSpacing(0)
        title = QLabel(label)
        title.setObjectName("technicalLabel")
        value = QLabel("—")
        value.setObjectName("instrumentMetricValue")
        frame_layout.addWidget(title)
        frame_layout.addWidget(value)
        layout.addWidget(frame, row, column, 1, column_span)
        return value

    def _create_result_strip(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("calibrationResultStrip")
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(5)
        self.calibration_status_label = QLabel("À CALIBRER")
        self.calibration_status_label.setProperty("state", "neutral")
        self.sensitivity_metric = CalibrationMetric("SENSIBILITÉ", "— V/unité")
        self.intercept_metric = CalibrationMetric("OFFSET b", "— V")
        self.r_squared_metric = CalibrationMetric("R²", "—")
        self.residual_metric = CalibrationMetric("RMS RÉSIDUEL", "—")
        self.formula_label = QLabel("V = m × référence + b")
        self.formula_label.hide()
        self.reset_channel_button = QPushButton("Réinitialiser")
        self.reset_channel_button.setProperty("kind", "quiet")
        self.fit_button = QPushButton("Valider m×x+b")
        self.fit_button.setProperty("kind", "primaryLarge")

        layout.addWidget(self.calibration_status_label)
        for metric in (
            self.sensitivity_metric,
            self.intercept_metric,
            self.r_squared_metric,
            self.residual_metric,
        ):
            layout.addWidget(metric, 1)
        layout.addWidget(self.reset_channel_button)
        layout.addWidget(self.fit_button)
        return frame

    def _setup_connections(self) -> None:
        self.channel_combo.currentIndexChanged.connect(self._on_channel_changed)
        self.point_count_spin.valueChanged.connect(self._on_point_count_changed)
        self.points_table.currentCellChanged.connect(self._on_point_selected)
        self.record_point_button.clicked.connect(self._record_selected_point)
        self.zero_button.clicked.connect(self._capture_zero)
        self.clear_point_button.clicked.connect(self._clear_selected_point)
        self.reset_channel_button.clicked.connect(self._reset_active_channel)
        self.fit_button.clicked.connect(self._fit_active_channel)
        self.previous_channel_button.clicked.connect(lambda: self._change_channel(-1))
        self.next_channel_button.clicked.connect(lambda: self._change_channel(1))
        self.settings_toggle_button.clicked.connect(self._toggle_settings)
        self.hardware_setup_button.clicked.connect(self.hardware_setup_requested.emit)
        self.live_toggle_button.clicked.connect(self._toggle_live_preview)
        self.preview_block_received.connect(self._on_preview_block)
        self.preview_error_received.connect(self._on_preview_error)
        self.sensor_id_edit.textChanged.connect(self._update_sensor_identity)
        self.sensor_type_combo.currentTextChanged.connect(self._update_sensor_identity)
        self.unit_combo.currentTextChanged.connect(self._update_sensor_identity)

    def bind_acquisition_controller(self, controller: AcquisitionController | None) -> None:
        """Partage l'unique contrôleur physique détenu par la vue Acquisition."""

        if self._controller is not None and self._controller is not controller:
            self._stop_live_preview()
        self._controller = controller
        self._refresh_hardware_state()

    def set_workspace_active(self, active: bool) -> None:
        self._workspace_active = bool(active)
        if not active:
            self._stop_live_preview()
        else:
            self._refresh_hardware_state()

    def update_hardware_state(self, connected: bool, message: str = "") -> None:
        del message
        if not connected:
            self._stop_live_preview()
        self._refresh_hardware_state()

    def _refresh_hardware_state(self) -> None:
        controller = self._controller
        connected = bool(controller and controller.is_hardware_available())
        if connected and controller and controller.selected_device:
            descriptor = controller.selected_device
            text = descriptor.model.upper()
            state = "success"
            self.set_channel_count(descriptor.capabilities.analog_input_channels)
            selected_limit = self.voltage_range_combo.currentData()
            self.voltage_range_combo.blockSignals(True)
            self.voltage_range_combo.clear()
            for voltage_range in descriptor.capabilities.voltage_ranges:
                self.voltage_range_combo.addItem(voltage_range.label, voltage_range.value)
            if selected_limit is not None:
                self._set_combo_data(self.voltage_range_combo, float(selected_limit))
            if self.voltage_range_combo.currentIndex() < 0 and self.voltage_range_combo.count() > 0:
                self.voltage_range_combo.setCurrentIndex(0)
            self.voltage_range_combo.blockSignals(False)
        else:
            text = "CARTE ABSENTE"
            state = "danger"
        self.hardware_status_label.setText(text)
        self.hardware_status_label.setProperty("state", state)
        self._repolish(self.hardware_status_label)
        self.live_toggle_button.setEnabled(connected)
        self.hardware_setup_button.setVisible(not connected)

    def _toggle_settings(self) -> None:
        visible = not self.sensor_settings_panel.isVisible()
        self.sensor_settings_panel.setVisible(visible)
        self.settings_toggle_button.setText("Fermer réglages" if visible else "Réglages")

    def _toggle_live_preview(self) -> None:
        if self._controller and self._controller.is_calibration_preview_active:
            self._stop_live_preview()
        else:
            self._start_live_preview()

    def _start_live_preview(self) -> None:
        controller = self._controller
        if controller is None or not controller.is_hardware_available():
            QMessageBox.warning(self, "Lecture matérielle", "Connectez d'abord une carte physique.")
            return
        self._save_active_metadata()
        self._reset_live_buffer()
        range_data = self.voltage_range_combo.currentData()
        range_volts = float(range_data) if range_data is not None else 10.0
        try:
            actual_rate = controller.start_calibration_preview(
                self._active_channel,
                sample_rate_hz=float(self.preview_rate_spin.value()),
                range_volts=range_volts,
                data_callback=lambda block, rate: self.preview_block_received.emit(block, rate),
                error_callback=self.preview_error_received.emit,
            )
        except (RuntimeError, ValueError) as exc:
            self._set_live_state(False, error=str(exc))
            QMessageBox.warning(self, "Lecture matérielle impossible", str(exc))
            return
        self._live_rate_hz = actual_rate
        self.sample_rate_label.setText(f"{actual_rate:g} S/s")
        self._set_live_state(True)

    def _stop_live_preview(self) -> None:
        controller = self._controller
        if controller is not None:
            controller.stop_calibration_preview()
        self._set_live_state(False)

    def _set_live_state(self, active: bool, error: str | None = None) -> None:
        if error:
            text, state = "ERREUR PILOTE", "danger"
        elif active:
            text, state = "LECTURE LIVE", "success"
        else:
            text, state = "HORS LECTURE", "neutral"
        self.live_state_label.setText(text)
        self.live_state_label.setProperty("state", state)
        self._repolish(self.live_state_label)
        self.live_toggle_button.setText("Arrêter lecture" if active else "Démarrer lecture")
        self.live_toggle_button.setProperty("kind", "danger" if active else "primaryLarge")
        self._repolish(self.live_toggle_button)
        self.record_point_button.setEnabled(active and bool(self._last_live_metrics))
        self.zero_button.setEnabled(active and bool(self._last_live_metrics))
        if not active:
            self.sample_rate_label.setText("— S/s")
            if not error:
                self.signal_verdict_label.setText("EN ATTENTE DU SIGNAL")
                self.signal_verdict_label.setProperty("state", "neutral")
                self._repolish(self.signal_verdict_label)

    def _on_preview_block(self, block: object, sample_rate_hz: float) -> None:
        data = np.asarray(block, dtype=np.float64)
        if data.ndim != 2 or data.shape[1] != 1 or data.shape[0] == 0:
            self._on_preview_error("Bloc matériel invalide")
            return
        values = data[:, 0]
        start_index = self._live_sample_index
        indices = start_index + np.arange(values.size, dtype=np.float64)
        times = indices / float(sample_rate_hz)
        self._live_sample_index += values.size
        self._live_rate_hz = float(sample_rate_hz)
        self._live_values = np.concatenate((self._live_values, values))
        self._live_times = np.concatenate((self._live_times, times))
        cutoff = times[-1] - self.LIVE_WINDOW_SECONDS
        keep = self._live_times >= cutoff
        self._live_times = self._live_times[keep]
        self._live_values = self._live_values[keep]

        analysis_count = max(20, int(round(sample_rate_hz)))
        analysis_values = self._live_values[-analysis_count:]
        metrics = analyze_live_voltage(
            analysis_values,
            voltage_limit=float(self.voltage_range_combo.currentData()),
            stability_limit_voltage=float(self.stability_limit_spin.value()),
        )
        self._last_live_metrics = metrics
        self._update_live_readout(metrics)
        self._update_live_plot()

    def _on_preview_error(self, message: str) -> None:
        self._set_live_state(False, error=message)
        self.signal_verdict_label.setText("LECTURE INTERROMPUE")
        self.signal_verdict_label.setProperty("state", "danger")
        self.signal_verdict_label.setToolTip(message)
        self._repolish(self.signal_verdict_label)

    def _update_live_readout(self, metrics: LiveSignalMetrics) -> None:
        self.live_voltage_label.setText(f"{metrics.latest_voltage:+.6f} V")
        self.mean_value_label.setText(f"{metrics.mean_voltage:+.6f} V")
        self.noise_value_label.setText(f"{metrics.noise_rms_voltage:.6f} V")
        self.peak_to_peak_value_label.setText(f"{metrics.peak_to_peak_voltage:.6f} V")
        self.drift_value_label.setText(f"{metrics.drift_voltage:.6f} V")
        self.range_value_label.setText(f"{metrics.minimum_voltage:+.5f} / {metrics.maximum_voltage:+.5f} V")
        self.measured_voltage_spin.setValue(metrics.mean_voltage)
        mapping = {
            "stable": ("SIGNAL STABLE · CAPTURE AUTORISÉE", "success"),
            "unstable": ("SIGNAL INSTABLE", "warning"),
            "saturation": ("SATURATION · CHANGEZ LA PLAGE", "danger"),
            "settling": ("ACQUISITION EN COURS", "neutral"),
            "invalid": ("DONNÉES INVALIDES", "danger"),
        }
        text, state = mapping[metrics.verdict]
        self.signal_verdict_label.setText(text)
        self.signal_verdict_label.setProperty("state", state)
        self._repolish(self.signal_verdict_label)
        capture_enabled = metrics.capturable
        self.record_point_button.setEnabled(capture_enabled)
        self.zero_button.setEnabled(capture_enabled)

    def _reset_live_buffer(self) -> None:
        self._live_values = np.empty(0, dtype=np.float64)
        self._live_times = np.empty(0, dtype=np.float64)
        self._live_sample_index = 0
        self._last_live_metrics = None
        self.live_voltage_label.setText("— V")
        for label in (
            self.mean_value_label,
            self.noise_value_label,
            self.peak_to_peak_value_label,
            self.drift_value_label,
            self.range_value_label,
        ):
            label.setText("—")
        self._initialize_live_plot()

    def _initialize_live_plot(self) -> None:
        palette = self._plot_palette()
        self.signal_figure.clear()
        self.signal_figure.set_facecolor(palette["background"])
        self.signal_axis = self.signal_figure.add_subplot(111)
        self.signal_axis.set_facecolor(palette["background"])
        (self.signal_line,) = self.signal_axis.plot([], [], color=palette["measure"], linewidth=1.25)
        self.signal_axis.set_xlabel("Temps relatif (s)", color=palette["foreground"])
        self.signal_axis.set_ylabel("Tension brute (V)", color=palette["foreground"])
        self.signal_axis.tick_params(colors=palette["foreground"], labelsize=9)
        self.signal_axis.grid(True, color=palette["grid"], linewidth=0.65, alpha=0.8)
        for spine in self.signal_axis.spines.values():
            spine.set_color(palette["spine"])
        self.signal_axis.set_xlim(-self.LIVE_WINDOW_SECONDS, 0.0)
        self.signal_axis.set_ylim(-0.01, 0.01)
        self.signal_axis.text(
            0.5,
            0.5,
            "DÉMARREZ LA LECTURE MATÉRIELLE",
            color=palette["muted"],
            ha="center",
            va="center",
            transform=self.signal_axis.transAxes,
        )
        self.signal_canvas.draw_idle()

    def _update_live_plot(self) -> None:
        if self._live_values.size == 0:
            return
        for artist in list(self.signal_axis.texts):
            artist.remove()
        latest_time = float(self._live_times[-1])
        x = self._live_times - latest_time
        self.signal_line.set_data(x, self._live_values)
        self.signal_axis.set_xlim(-self.LIVE_WINDOW_SECONDS, 0.0)
        minimum = float(np.min(self._live_values))
        maximum = float(np.max(self._live_values))
        center = (minimum + maximum) / 2.0
        span = max(
            maximum - minimum,
            float(self.stability_limit_spin.value()) * 10.0,
            0.002,
        )
        self.signal_axis.set_ylim(center - span * 0.65, center + span * 0.65)
        self.signal_canvas.draw_idle()

    def _capture_zero(self) -> None:
        self.points_table.selectRow(0)
        self.reference_spin.setValue(0.0)
        self._record_selected_point()

    def _record_selected_point(self) -> None:
        metrics = self._last_live_metrics
        if (
            self._controller is None
            or not self._controller.is_calibration_preview_active
            or metrics is None
            or metrics.verdict != "stable"
        ):
            QMessageBox.warning(
                self,
                "Capture refusée",
                "La capture exige une lecture physique active et un signal stable.",
            )
            return
        row = self.points_table.currentRow()
        if row < 0:
            row = self._first_empty_point_row()
            self.points_table.selectRow(row)
        self.points_table.blockSignals(True)
        self.points_table.setItem(row, 1, QTableWidgetItem(f"{self.reference_spin.value():.10g}"))
        self.points_table.setItem(row, 2, QTableWidgetItem(f"{metrics.mean_voltage:.12g}"))
        self.points_table.blockSignals(False)
        self._save_active_points()
        self._invalidate_active_fit()
        self._update_point_progress()
        if row + 1 < self.points_table.rowCount():
            self.points_table.selectRow(row + 1)
            self._load_entry_controls(row + 1)

    def _first_empty_point_row(self) -> int:
        for row in range(self.points_table.rowCount()):
            if not self._table_text(row, 2):
                return row
        return max(0, self.points_table.rowCount() - 1)

    def set_channel_count(self, channel_count: int) -> None:
        requested_count = int(channel_count)
        if requested_count < 1 or requested_count == self.channel_count:
            return
        self._save_active_points()
        self._save_active_metadata()
        self.channel_count = requested_count
        self._channel_points = {
            channel: points for channel, points in self._channel_points.items() if channel < requested_count
        }
        self._channel_metadata = {
            channel: metadata
            for channel, metadata in self._channel_metadata.items()
            if channel < requested_count
        }
        self._channel_records = {
            channel: record for channel, record in self._channel_records.items() if channel < requested_count
        }
        self.channel_combo.blockSignals(True)
        self.channel_combo.clear()
        for channel in range(requested_count):
            self.channel_combo.addItem(f"Canal {channel + 1}", channel)
        self._active_channel = min(self._active_channel, requested_count - 1)
        self.channel_combo.setCurrentIndex(self._active_channel)
        self.channel_combo.blockSignals(False)
        self._load_channel(self._active_channel)

    def _change_channel(self, offset: int) -> None:
        target = max(0, min(self.channel_count - 1, self._active_channel + offset))
        self.channel_combo.setCurrentIndex(target)

    def _on_channel_changed(self, index: int) -> None:
        self._stop_live_preview()
        self._save_active_points()
        self._save_active_metadata()
        self._load_channel(int(self.channel_combo.itemData(index)))

    def _on_point_count_changed(self, count: int) -> None:
        self._save_active_points()
        points = list(self._channel_points.get(self._active_channel, []))
        if len(points) < count:
            points.extend([None] * (count - len(points)))
        self._channel_points[self._active_channel] = points[:count]
        self._populate_points_table()
        self._invalidate_active_fit()

    def _load_channel(self, channel: int) -> None:
        self._active_channel = channel
        self.channel_progress_label.setText(f"CANAL {channel + 1} / {self.channel_count}")
        self.previous_channel_button.setEnabled(channel > 0)
        self.next_channel_button.setEnabled(channel < self.channel_count - 1)
        points = self._channel_points.get(channel)
        if points is None:
            points = [None] * self.point_count_spin.value()
            self._channel_points[channel] = points
        self.point_count_spin.blockSignals(True)
        self.point_count_spin.setValue(len(points))
        self.point_count_spin.blockSignals(False)
        metadata = self._channel_metadata.get(channel, self._default_channel_metadata(channel))
        self.sensor_id_edit.setText(str(metadata["sensor_id"]))
        self.sensor_type_combo.setCurrentText(str(metadata["sensor_type"]))
        self.unit_combo.setCurrentText(str(metadata["physical_unit"]))
        self.operator_edit.setText(str(metadata.get("operator", "")))
        self.reference_equipment_edit.setText(str(metadata.get("reference_equipment", "")))
        self._set_combo_data(self.voltage_range_combo, float(metadata.get("range_volts", 10.0)))
        self.preview_rate_spin.setValue(int(metadata.get("preview_rate_hz", 200)))
        self.stability_limit_spin.setValue(float(metadata.get("stability_limit_voltage", 0.002)))
        self._update_reference_unit()
        self._update_sensor_identity()
        self._populate_points_table()
        record = self._channel_records.get(channel)
        if record is None:
            self._reset_result_display()
        else:
            self._show_record(record)
        self._reset_live_buffer()
        self.step_changed.emit(f"channel_{channel}")

    def _default_channel_metadata(self, channel: int) -> dict[str, Any]:
        metadata: dict[str, Any] = {
            "sensor_id": f"CAP-{channel + 1:02d}",
            "sensor_type": "force",
            "physical_unit": "g",
            "operator": "",
            "reference_equipment": "",
            "range_volts": 10.0,
            "preview_rate_hz": 200,
            "stability_limit_voltage": 0.002,
        }
        if self._controller is not None:
            configured = self._controller.get_channel_configuration(channel)
            if configured:
                metadata.update(
                    sensor_type=configured["sensor_type"],
                    physical_unit=configured["physical_units"],
                    range_volts=configured["range_volts"],
                )
        return metadata

    def _save_active_metadata(self) -> None:
        if not hasattr(self, "sensor_id_edit"):
            return
        self._channel_metadata[self._active_channel] = {
            "sensor_id": self.sensor_id_edit.text().strip() or f"CAP-{self._active_channel + 1:02d}",
            "sensor_type": self.sensor_type_combo.currentText(),
            "physical_unit": self.unit_combo.currentText().strip() or "unité",
            "operator": self.operator_edit.text().strip(),
            "reference_equipment": self.reference_equipment_edit.text().strip(),
            "range_volts": float(self.voltage_range_combo.currentData()),
            "preview_rate_hz": int(self.preview_rate_spin.value()),
            "stability_limit_voltage": float(self.stability_limit_spin.value()),
        }

    def _update_sensor_identity(self, *_args) -> None:
        if not hasattr(self, "sensor_identity_label"):
            return
        sensor_id = self.sensor_id_edit.text().strip() or f"CAP-{self._active_channel + 1:02d}"
        sensor_type = self.sensor_type_combo.currentText() or "capteur"
        unit = self.unit_combo.currentText().strip() or "unité"
        self.sensor_identity_label.setText(f"{sensor_id} · {sensor_type} · {unit}")
        self._update_reference_unit()

    def _update_reference_unit(self) -> None:
        unit = self.unit_combo.currentText().strip() or "unité"
        self.reference_unit_label.setText(unit)
        self.reference_spin.setSuffix(f" {unit}")

    def _populate_points_table(self) -> None:
        points = self._channel_points.get(self._active_channel, [])
        self.points_table.blockSignals(True)
        self.points_table.setRowCount(len(points))
        for row, point in enumerate(points):
            point_item = QTableWidgetItem("Zéro" if row == 0 else f"P{row + 1}")
            point_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            self.points_table.setItem(row, 0, point_item)
            reference_text = "0" if point is None and row == 0 else ""
            voltage_text = ""
            if point is not None:
                reference_text = f"{point[0]:.8g}"
                voltage_text = f"{point[1]:.10g}"
            for column, text in ((1, reference_text), (2, voltage_text)):
                item = QTableWidgetItem(text)
                item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
                self.points_table.setItem(row, column, item)
        self.points_table.blockSignals(False)
        if points:
            self.points_table.selectRow(0)
            self._load_entry_controls(0)
        self._update_point_progress()

    def _update_point_progress(self) -> None:
        points = self._channel_points.get(self._active_channel, [])
        captured = sum(point is not None for point in points)
        self.point_progress_label.setText(f"{captured} / {len(points)}")

    def _save_active_points(self) -> None:
        if not hasattr(self, "points_table"):
            return
        points: list[tuple[float, float] | None] = []
        for row in range(self.points_table.rowCount()):
            try:
                point = (float(self._table_text(row, 1)), float(self._table_text(row, 2)))
            except (TypeError, ValueError):
                point = None
            points.append(point)
        self._channel_points[self._active_channel] = points

    def _on_point_selected(self, current_row: int, _current_column: int, *_args) -> None:
        if current_row >= 0:
            self._load_entry_controls(current_row)

    def _load_entry_controls(self, row: int) -> None:
        self.selected_point_label.setText("Point 1 · zéro" if row == 0 else f"Point {row + 1}")
        try:
            self.reference_spin.setValue(float(self._table_text(row, 1)))
        except (TypeError, ValueError):
            self.reference_spin.setValue(0.0)
        try:
            self.measured_voltage_spin.setValue(float(self._table_text(row, 2)))
        except (TypeError, ValueError):
            self.measured_voltage_spin.setValue(0.0)

    def _clear_selected_point(self) -> None:
        row = self.points_table.currentRow()
        if row < 0:
            return
        self.points_table.blockSignals(True)
        self.points_table.setItem(row, 1, QTableWidgetItem("0" if row == 0 else ""))
        self.points_table.setItem(row, 2, QTableWidgetItem(""))
        self.points_table.blockSignals(False)
        self._save_active_points()
        self._invalidate_active_fit()
        self._load_entry_controls(row)
        self._update_point_progress()

    def _reset_active_channel(self) -> None:
        self._channel_points[self._active_channel] = [None] * self.point_count_spin.value()
        self._channel_records.pop(self._active_channel, None)
        self._populate_points_table()
        self._reset_result_display()

    def _fit_active_channel(self) -> None:
        self._save_active_points()
        self._save_active_metadata()
        points = self._channel_points.get(self._active_channel, [])
        if any(point is None for point in points):
            QMessageBox.information(
                self,
                "Calibration incomplète",
                "Capturez tous les points depuis le signal matériel avant validation.",
            )
            return
        self.calibration_started.emit()
        try:
            record = CalibrationRecord.fit_linear(
                sensor_id=self.sensor_id_edit.text().strip() or f"CAP-{self._active_channel + 1:02d}",
                channel=self._active_channel,
                sensor_type=self.sensor_type_combo.currentText(),
                physical_unit=self.unit_combo.currentText().strip() or "unité",
                points=[
                    CalibrationPoint(reference_value=point[0], measured_voltage=point[1])
                    for point in points
                    if point is not None
                ],
                operator=self.operator_edit.text().strip(),
                reference_equipment=self.reference_equipment_edit.text().strip(),
            )
        except CalibrationError as exc:
            self._set_status("CALIBRATION REFUSÉE", "danger")
            QMessageBox.warning(self, "Calibration refusée", str(exc))
            return
        self._channel_records[self._active_channel] = record
        self._show_record(record)
        self.calibration_completed.emit(
            {
                "timestamp": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
                "channel": self._active_channel,
                "record": record.to_dict(),
                "channels": {str(self._active_channel): record.to_dict()},
            }
        )

    def _show_record(self, record: CalibrationRecord) -> None:
        unit = record.physical_unit
        self.sensitivity_metric.set_value(f"{record.sensitivity_v_per_unit:.8g} V/{unit}")
        self.intercept_metric.set_value(f"{record.intercept_volts:.8g} V")
        self.r_squared_metric.set_value(
            f"{record.r_squared:.7f}" if record.linearity_assessable else "2 points"
        )
        self.residual_metric.set_value(f"{record.residual_rms:.6g} {unit}")
        self.formula_label.setText(
            f"V = {record.sensitivity_v_per_unit:.6g} × référence {record.intercept_volts:+.6g}"
        )
        self._set_status(
            "CALIBRATION VALIDÉE" if record.linearity_assessable else "TRANSFERT VALIDÉ",
            "success",
        )
        self._draw_record(record)
        self.plot_tabs.setCurrentIndex(1)

    def _invalidate_active_fit(self) -> None:
        self._channel_records.pop(self._active_channel, None)
        self._reset_result_display()

    def _reset_result_display(self) -> None:
        self.sensitivity_metric.set_value("— V/unité")
        self.intercept_metric.set_value("— V")
        self.r_squared_metric.set_value("—")
        self.residual_metric.set_value("—")
        self.formula_label.setText("V = m × référence + b")
        self._set_status("À CALIBRER", "neutral")
        self._draw_empty_plot()

    def _set_status(self, text: str, state: str) -> None:
        self.calibration_status_label.setText(text)
        self.calibration_status_label.setProperty("state", state)
        self._repolish(self.calibration_status_label)

    def _draw_empty_plot(self) -> None:
        palette = self._plot_palette()
        self.figure.clear()
        axis = self.figure.add_subplot(111)
        self._style_calibration_axis(axis)
        axis.text(
            0.5,
            0.5,
            "AUCUN POINT VALIDÉ",
            ha="center",
            va="center",
            color=palette["muted"],
            transform=axis.transAxes,
        )
        self.canvas.draw_idle()

    def _draw_record(self, record: CalibrationRecord) -> None:
        palette = self._plot_palette()
        references = np.asarray([point.reference_value for point in record.points], dtype=float)
        voltages = np.asarray([point.measured_voltage for point in record.points], dtype=float)
        fit_reference = np.linspace(float(references.min()), float(references.max()), 200)
        fit_voltage = record.sensitivity_v_per_unit * fit_reference + record.intercept_volts
        self.figure.clear()
        axis = self.figure.add_subplot(111)
        self._style_calibration_axis(axis)
        axis.scatter(
            references,
            voltages,
            s=46,
            color=palette["measure"],
            edgecolor=palette["background"],
            linewidth=1.0,
            zorder=3,
            label="Mesures",
        )
        axis.plot(
            fit_reference,
            fit_voltage,
            color=palette["reference"],
            linewidth=1.8,
            label="m×x+b",
        )
        legend = axis.legend(frameon=False, loc="best")
        for text in legend.get_texts():
            text.set_color(palette["foreground"])
        self.canvas.draw_idle()

    def _style_calibration_axis(self, axis) -> None:
        palette = self._plot_palette()
        self.figure.set_facecolor(palette["background"])
        axis.set_facecolor(palette["background"])
        axis.set_xlabel(
            f"Référence ({self.unit_combo.currentText() or 'unité'})",
            color=palette["foreground"],
        )
        axis.set_ylabel("Tension mesurée (V)", color=palette["foreground"])
        axis.tick_params(colors=palette["foreground"], labelsize=9)
        axis.grid(True, color=palette["grid"], linewidth=0.65, alpha=0.8)
        for spine in axis.spines.values():
            spine.set_color(palette["spine"])

    def _plot_palette(self) -> dict[str, str]:
        if self.is_dark_mode:
            return {
                "background": "#071820",
                "foreground": "#9DB0B8",
                "grid": "#203943",
                "spine": "#38535E",
                "measure": "#35BCD5",
                "reference": "#E2A14B",
                "muted": "#708B96",
            }
        return {
            "background": "#FCFDFD",
            "foreground": "#526A75",
            "grid": "#D8E1E4",
            "spine": "#B9C8CE",
            "measure": "#087F99",
            "reference": "#B87523",
            "muted": "#71838B",
        }

    def set_theme(self, is_dark: bool) -> None:
        """Keep calibration plots coherent with the application theme."""

        self.is_dark_mode = bool(is_dark)
        self._initialize_live_plot()
        record = self._channel_records.get(self._active_channel)
        if record is None:
            self._draw_empty_plot()
        else:
            self._draw_record(record)

    @staticmethod
    def _set_combo_data(combo: QComboBox, value: float) -> None:
        for index in range(combo.count()):
            if float(combo.itemData(index)) == float(value):
                combo.setCurrentIndex(index)
                return

    @staticmethod
    def _repolish(widget: QWidget) -> None:
        widget.style().unpolish(widget)
        widget.style().polish(widget)

    def _table_text(self, row: int, column: int) -> str:
        item = self.points_table.item(row, column)
        return item.text().strip() if item is not None else ""

    def get_calibration_data(self) -> dict[str, Any]:
        self._save_active_points()
        self._save_active_metadata()
        return {
            "timestamp": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            "active_channel": self._active_channel,
            "channel_count": self.channel_count,
            "completed": len(self._channel_records) == self.channel_count,
            "completed_channels": sorted(self._channel_records),
            "channels": {str(channel): record.to_dict() for channel, record in self._channel_records.items()},
        }

    def load_calibration_data(self, data: dict[str, Any]) -> None:
        channel_count = int(data.get("channel_count", self.channel_count))
        self.set_channel_count(max(channel_count, 1))
        for channel_key, payload in data.get("channels", {}).items():
            try:
                channel = int(channel_key)
                record = CalibrationRecord.from_dict(payload)
            except (KeyError, TypeError, ValueError):
                continue
            if not 0 <= channel < self.channel_count:
                continue
            self._channel_records[channel] = record
            self._channel_points[channel] = [
                (point.reference_value, point.measured_voltage) for point in record.points
            ]
            metadata = self._default_channel_metadata(channel)
            metadata.update(
                sensor_id=record.sensor_id,
                sensor_type=record.sensor_type,
                physical_unit=record.physical_unit,
                operator=record.operator,
                reference_equipment=record.reference_equipment,
            )
            self._channel_metadata[channel] = metadata
        active_channel = min(
            max(int(data.get("active_channel", self._active_channel)), 0),
            self.channel_count - 1,
        )
        self.channel_combo.blockSignals(True)
        self.channel_combo.setCurrentIndex(active_channel)
        self.channel_combo.blockSignals(False)
        self._load_channel(active_channel)

    def closeEvent(self, event) -> None:
        self._stop_live_preview()
        event.accept()


CalibrationViewMaritime = CalibrationView
