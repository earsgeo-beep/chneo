"""Professional, channel-by-channel sensor calibration workspace."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

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
    QVBoxLayout,
    QWidget,
)

from ...core.calibration import CalibrationError, CalibrationPoint, CalibrationRecord


class CalibrationMetric(QFrame):
    """Compact result metric used below the scientific workspace."""

    def __init__(self, label: str, value: str = "—", parent=None):
        super().__init__(parent)
        self.setObjectName("metricCard")
        self.setMinimumHeight(58)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(1)

        label_widget = QLabel(label)
        label_widget.setObjectName("metricLabel")
        self.value_widget = QLabel(value)
        self.value_widget.setObjectName("metricValue")
        layout.addWidget(label_widget)
        layout.addWidget(self.value_widget)

    def set_value(self, value: str) -> None:
        self.value_widget.setText(value)


class CalibrationView(QWidget):
    """Calibration linéaire réelle avec une grande zone de travail unique."""

    calibration_started = Signal()
    calibration_completed = Signal(dict)
    step_changed = Signal(str)

    CHANNEL_COUNT = 8
    DEFAULT_POINT_COUNT = 3

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("calibrationWorkspace")

        self._active_channel = 0
        self._channel_points: dict[int, list[tuple[float, float] | None]] = {}
        self._channel_records: dict[int, CalibrationRecord] = {}
        self._channel_metadata: dict[int, dict[str, str]] = {}

        self._build_ui()
        self._setup_connections()
        self._load_channel(0)

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 14, 20, 16)
        root.setSpacing(10)

        root.addWidget(self._create_configuration_strip())

        self.workspace_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.workspace_splitter.setChildrenCollapsible(False)
        self.workspace_splitter.addWidget(self._create_plot_panel())
        self.workspace_splitter.addWidget(self._create_points_panel())
        self.workspace_splitter.setStretchFactor(0, 5)
        self.workspace_splitter.setStretchFactor(1, 3)
        self.workspace_splitter.setSizes([720, 500])
        root.addWidget(self.workspace_splitter, 1)

        metrics = QHBoxLayout()
        metrics.setSpacing(10)
        self.sensitivity_metric = CalibrationMetric("SENSIBILITÉ", "— V/unité")
        self.intercept_metric = CalibrationMetric("ORDONNÉE b", "— V")
        self.r_squared_metric = CalibrationMetric("LINÉARITÉ R²", "Non calculée")
        self.residual_metric = CalibrationMetric("ERREUR RMS", "—")
        for metric in (
            self.sensitivity_metric,
            self.intercept_metric,
            self.r_squared_metric,
            self.residual_metric,
        ):
            metrics.addWidget(metric)
        root.addLayout(metrics)

        root.addLayout(self._create_action_bar())

    def _create_configuration_strip(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("surface")
        outer_layout = QVBoxLayout(frame)
        outer_layout.setContentsMargins(16, 10, 16, 12)
        outer_layout.setSpacing(9)

        toolbar = QHBoxLayout()
        toolbar.setSpacing(8)
        self.channel_progress_label = QLabel("CANAL 1 / 8")
        self.channel_progress_label.setObjectName("pageEyebrow")
        context = QLabel("Configuration du capteur et traçabilité de l'étalonnage")
        context.setObjectName("sectionTitle")
        self.previous_channel_button = QPushButton("Précédent")
        self.previous_channel_button.setProperty("kind", "secondary")
        self.next_channel_button = QPushButton("Suivant")
        self.next_channel_button.setProperty("kind", "secondary")
        self.calibration_status_label = QLabel("À CALIBRER")
        self.calibration_status_label.setProperty("state", "neutral")
        toolbar.addWidget(self.channel_progress_label)
        toolbar.addWidget(context)
        toolbar.addStretch()
        toolbar.addWidget(self.previous_channel_button)
        toolbar.addWidget(self.next_channel_button)
        toolbar.addWidget(self.calibration_status_label)
        outer_layout.addLayout(toolbar)

        layout = QGridLayout()
        layout.setHorizontalSpacing(12)
        layout.setVerticalSpacing(5)

        self.channel_combo = QComboBox()
        for channel in range(self.CHANNEL_COUNT):
            self.channel_combo.addItem(f"Canal {channel + 1}", channel)

        self.sensor_id_edit = QLineEdit("CAP-01")
        self.sensor_type_combo = QComboBox()
        self.sensor_type_combo.addItems(
            ["force", "wave_height", "pressure", "displacement", "inclination", "generic"]
        )
        self.unit_combo = QComboBox()
        self.unit_combo.setEditable(True)
        self.unit_combo.addItems(["g", "kg", "N", "mm", "cm", "m", "°", "bar"])
        self.point_count_spin = QSpinBox()
        self.point_count_spin.setRange(2, 12)
        self.point_count_spin.setValue(self.DEFAULT_POINT_COUNT)
        self.point_count_spin.setSuffix(" points")
        self.operator_edit = QLineEdit()
        self.operator_edit.setPlaceholderText("Nom de l'opérateur")
        self.reference_equipment_edit = QLineEdit()
        self.reference_equipment_edit.setPlaceholderText("Masses, règle étalon, banc...")

        primary_fields = (
            ("Canal", self.channel_combo),
            ("Identifiant capteur", self.sensor_id_edit),
            ("Type", self.sensor_type_combo),
            ("Unité physique", self.unit_combo),
            ("Nombre de points", self.point_count_spin),
        )
        for column, (label, widget) in enumerate(primary_fields):
            label_widget = QLabel(label.upper())
            label_widget.setObjectName("metricLabel")
            layout.addWidget(label_widget, 0, column)
            layout.addWidget(widget, 1, column)

        operator_label = QLabel("OPÉRATEUR")
        operator_label.setObjectName("metricLabel")
        reference_label = QLabel("RÉFÉRENCE MÉTROLOGIQUE UTILISÉE")
        reference_label.setObjectName("metricLabel")
        layout.addWidget(operator_label, 2, 0, 1, 2)
        layout.addWidget(reference_label, 2, 2, 1, 3)
        layout.addWidget(self.operator_edit, 3, 0, 1, 2)
        layout.addWidget(self.reference_equipment_edit, 3, 2, 1, 3)

        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 2)
        layout.setColumnStretch(2, 1)
        layout.setColumnStretch(3, 1)
        layout.setColumnStretch(4, 1)
        outer_layout.addLayout(layout)
        return frame

    def _create_plot_panel(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("surface")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(8)

        header = QHBoxLayout()
        title = QLabel("Courbe de linéarité")
        title.setObjectName("sectionTitle")
        self.formula_label = QLabel("V = m × référence + b")
        self.formula_label.setObjectName("mutedText")
        header.addWidget(title)
        header.addStretch()
        header.addWidget(self.formula_label)
        layout.addLayout(header)

        self.figure = Figure(figsize=(7.5, 4.8), tight_layout=True)
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.canvas.setMinimumSize(400, 230)
        layout.addWidget(self.canvas, 1)
        self._draw_empty_plot()
        return panel

    def _create_points_panel(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("surface")
        panel.setMinimumWidth(400)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(10)

        header = QHBoxLayout()
        title = QLabel("Points de mesure")
        title.setObjectName("sectionTitle")
        mode = QLabel("SAISIE MANUELLE")
        mode.setProperty("state", "neutral")
        header.addWidget(title)
        header.addStretch()
        header.addWidget(mode)
        layout.addLayout(header)

        instructions = QLabel(
            "Sélectionnez une ligne, indiquez la référence appliquée et la tension lue. "
            "Le premier point sert normalement au zéro."
        )
        instructions.setWordWrap(True)
        instructions.setObjectName("mutedText")
        layout.addWidget(instructions)

        self.points_table = QTableWidget(0, 4)
        self.points_table.setHorizontalHeaderLabels(["Point", "Référence", "Tension (V)", "État"])
        self.points_table.verticalHeader().setVisible(False)
        self.points_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.points_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.points_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.points_table.setAlternatingRowColors(True)
        self.points_table.verticalHeader().setDefaultSectionSize(32)
        self.points_table.setMinimumHeight(150)
        layout.addWidget(self.points_table, 1)

        entry_frame = QFrame()
        entry_frame.setObjectName("quietSurface")
        entry_layout = QGridLayout(entry_frame)
        entry_layout.setContentsMargins(12, 10, 12, 10)
        entry_layout.setHorizontalSpacing(10)
        entry_layout.setVerticalSpacing(5)
        self.selected_point_label = QLabel("Point 1 · zéro")
        self.selected_point_label.setObjectName("sectionTitle")
        self.reference_spin = QDoubleSpinBox()
        self.reference_spin.setRange(-1_000_000.0, 1_000_000.0)
        self.reference_spin.setDecimals(6)
        self.reference_spin.setMinimumWidth(150)
        self.measured_voltage_spin = QDoubleSpinBox()
        self.measured_voltage_spin.setRange(-100.0, 100.0)
        self.measured_voltage_spin.setDecimals(8)
        self.measured_voltage_spin.setSuffix(" V")
        self.measured_voltage_spin.setMinimumWidth(150)
        reference_label = QLabel("VALEUR DE RÉFÉRENCE")
        reference_label.setObjectName("metricLabel")
        voltage_label = QLabel("TENSION MESURÉE")
        voltage_label.setObjectName("metricLabel")
        entry_layout.addWidget(self.selected_point_label, 0, 0, 1, 2)
        entry_layout.addWidget(reference_label, 1, 0)
        entry_layout.addWidget(voltage_label, 1, 1)
        entry_layout.addWidget(self.reference_spin, 2, 0)
        entry_layout.addWidget(self.measured_voltage_spin, 2, 1)
        entry_layout.setColumnStretch(0, 1)
        entry_layout.setColumnStretch(1, 1)
        layout.addWidget(entry_frame)

        buttons = QHBoxLayout()
        self.clear_point_button = QPushButton("Effacer le point")
        self.clear_point_button.setProperty("kind", "quiet")
        self.record_point_button = QPushButton("Enregistrer la mesure")
        self.record_point_button.setProperty("kind", "secondary")
        buttons.addWidget(self.clear_point_button)
        buttons.addStretch()
        buttons.addWidget(self.record_point_button)
        layout.addLayout(buttons)
        return panel

    def _create_action_bar(self) -> QHBoxLayout:
        layout = QHBoxLayout()
        self.reset_channel_button = QPushButton("Réinitialiser ce canal")
        self.reset_channel_button.setProperty("kind", "quiet")
        self.fit_button = QPushButton("Calculer et valider la calibration")
        self.fit_button.setProperty("kind", "primaryLarge")
        layout.addWidget(self.reset_channel_button)
        layout.addStretch()
        layout.addWidget(self.fit_button)
        return layout

    def _setup_connections(self) -> None:
        self.channel_combo.currentIndexChanged.connect(self._on_channel_changed)
        self.point_count_spin.valueChanged.connect(self._on_point_count_changed)
        self.points_table.currentCellChanged.connect(self._on_point_selected)
        self.points_table.itemChanged.connect(self._on_table_point_edited)
        self.record_point_button.clicked.connect(self._record_selected_point)
        self.clear_point_button.clicked.connect(self._clear_selected_point)
        self.reset_channel_button.clicked.connect(self._reset_active_channel)
        self.fit_button.clicked.connect(self._fit_active_channel)
        self.previous_channel_button.clicked.connect(lambda: self._change_channel(-1))
        self.next_channel_button.clicked.connect(lambda: self._change_channel(1))

    def _change_channel(self, offset: int) -> None:
        target = max(0, min(self.CHANNEL_COUNT - 1, self._active_channel + offset))
        self.channel_combo.setCurrentIndex(target)

    def _on_channel_changed(self, index: int) -> None:
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
        self.channel_progress_label.setText(f"CANAL {channel + 1} / {self.CHANNEL_COUNT}")
        self.previous_channel_button.setEnabled(channel > 0)
        self.next_channel_button.setEnabled(channel < self.CHANNEL_COUNT - 1)

        points = self._channel_points.get(channel)
        if points is None:
            points = [None] * self.point_count_spin.value()
            self._channel_points[channel] = points

        self.point_count_spin.blockSignals(True)
        self.point_count_spin.setValue(len(points))
        self.point_count_spin.blockSignals(False)
        metadata = self._channel_metadata.get(
            channel,
            {
                "sensor_id": f"CAP-{channel + 1:02d}",
                "sensor_type": "force",
                "physical_unit": "g",
                "operator": "",
                "reference_equipment": "",
            },
        )
        self.sensor_id_edit.setText(metadata["sensor_id"])
        self.sensor_type_combo.setCurrentText(metadata["sensor_type"])
        self.unit_combo.setCurrentText(metadata["physical_unit"])
        self.operator_edit.setText(metadata["operator"])
        self.reference_equipment_edit.setText(metadata["reference_equipment"])
        self._populate_points_table()

        record = self._channel_records.get(channel)
        if record is None:
            self._reset_result_display()
        else:
            self._show_record(record)
        self.step_changed.emit(f"channel_{channel}")

    def _populate_points_table(self) -> None:
        points = self._channel_points.get(self._active_channel, [])
        self.points_table.blockSignals(True)
        self.points_table.setRowCount(len(points))
        for row, point in enumerate(points):
            point_label = "Zéro" if row == 0 else f"P{row + 1}"
            point_item = QTableWidgetItem(point_label)
            point_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            self.points_table.setItem(row, 0, point_item)

            if point is None:
                reference_item = QTableWidgetItem("0" if row == 0 else "")
                voltage_item = QTableWidgetItem("")
                status_item = QTableWidgetItem("À mesurer")
            else:
                reference_item = QTableWidgetItem(f"{point[0]:.8g}")
                voltage_item = QTableWidgetItem(f"{point[1]:.10g}")
                status_item = QTableWidgetItem("Enregistré")
            status_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            self.points_table.setItem(row, 1, reference_item)
            self.points_table.setItem(row, 2, voltage_item)
            self.points_table.setItem(row, 3, status_item)
        self.points_table.blockSignals(False)

        if points:
            self.points_table.selectRow(0)
            self._load_entry_controls(0)

    def _save_active_points(self) -> None:
        if not hasattr(self, "points_table"):
            return
        points: list[tuple[float, float] | None] = []
        for row in range(self.points_table.rowCount()):
            reference_text = self._table_text(row, 1)
            voltage_text = self._table_text(row, 2)
            try:
                point = (float(reference_text), float(voltage_text))
            except (TypeError, ValueError):
                point = None
            points.append(point)
        self._channel_points[self._active_channel] = points

    def _save_active_metadata(self) -> None:
        if not hasattr(self, "sensor_id_edit"):
            return
        self._channel_metadata[self._active_channel] = {
            "sensor_id": self.sensor_id_edit.text().strip() or f"CAP-{self._active_channel + 1:02d}",
            "sensor_type": self.sensor_type_combo.currentText(),
            "physical_unit": self.unit_combo.currentText().strip() or "unité",
            "operator": self.operator_edit.text().strip(),
            "reference_equipment": self.reference_equipment_edit.text().strip(),
        }

    def _on_table_point_edited(self, item: QTableWidgetItem) -> None:
        if item.column() not in {1, 2}:
            return
        self._save_active_points()
        self._invalidate_active_fit()

    def _on_point_selected(self, current_row: int, _current_column: int, *_args) -> None:
        if current_row >= 0:
            self._load_entry_controls(current_row)

    def _load_entry_controls(self, row: int) -> None:
        self.selected_point_label.setText("Point 1 · zéro" if row == 0 else f"Point {row + 1}")
        reference_text = self._table_text(row, 1)
        voltage_text = self._table_text(row, 2)
        try:
            self.reference_spin.setValue(float(reference_text))
        except (TypeError, ValueError):
            self.reference_spin.setValue(0.0)
        try:
            self.measured_voltage_spin.setValue(float(voltage_text))
        except (TypeError, ValueError):
            self.measured_voltage_spin.setValue(0.0)

    def _record_selected_point(self) -> None:
        row = self.points_table.currentRow()
        if row < 0:
            return
        self.points_table.setItem(row, 1, QTableWidgetItem(f"{self.reference_spin.value():.10g}"))
        self.points_table.setItem(
            row,
            2,
            QTableWidgetItem(f"{self.measured_voltage_spin.value():.12g}"),
        )
        status_item = QTableWidgetItem("Enregistré")
        status_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
        self.points_table.setItem(row, 3, status_item)
        self._save_active_points()
        self._invalidate_active_fit()

        if row + 1 < self.points_table.rowCount():
            self.points_table.selectRow(row + 1)
            self._load_entry_controls(row + 1)

    def _clear_selected_point(self) -> None:
        row = self.points_table.currentRow()
        if row < 0:
            return
        self.points_table.setItem(row, 1, QTableWidgetItem("0" if row == 0 else ""))
        self.points_table.setItem(row, 2, QTableWidgetItem(""))
        status_item = QTableWidgetItem("À mesurer")
        status_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
        self.points_table.setItem(row, 3, status_item)
        self._save_active_points()
        self._invalidate_active_fit()
        self._load_entry_controls(row)

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
                "Tous les points doivent contenir une référence et une tension mesurée.",
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
        payload = {
            "timestamp": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            "channel": self._active_channel,
            "record": record.to_dict(),
            "channels": {str(self._active_channel): record.to_dict()},
        }
        self.calibration_completed.emit(payload)

    def _show_record(self, record: CalibrationRecord) -> None:
        unit = record.physical_unit
        self.sensitivity_metric.set_value(f"{record.sensitivity_v_per_unit:.8g} V/{unit}")
        self.intercept_metric.set_value(f"{record.intercept_volts:.8g} V")
        self.r_squared_metric.set_value(
            f"{record.r_squared:.7f}" if record.linearity_assessable else "Non évaluable (2 points)"
        )
        self.residual_metric.set_value(f"{record.residual_rms:.6g} {unit}")
        self.formula_label.setText(
            f"V = {record.sensitivity_v_per_unit:.6g} × référence {record.intercept_volts:+.6g}"
        )
        self._set_status(
            "CALIBRATION VALIDÉE" if record.linearity_assessable else "FONCTION DE TRANSFERT VALIDÉE",
            "success",
        )
        self._draw_record(record)

    def _invalidate_active_fit(self) -> None:
        self._channel_records.pop(self._active_channel, None)
        self._reset_result_display()

    def _reset_result_display(self) -> None:
        self.sensitivity_metric.set_value("— V/unité")
        self.intercept_metric.set_value("— V")
        self.r_squared_metric.set_value("Non calculée")
        self.residual_metric.set_value("—")
        self.formula_label.setText("V = m × référence + b")
        self._set_status("À CALIBRER", "neutral")
        self._draw_empty_plot()

    def _set_status(self, text: str, state: str) -> None:
        self.calibration_status_label.setText(text)
        self.calibration_status_label.setProperty("state", state)
        self.calibration_status_label.style().unpolish(self.calibration_status_label)
        self.calibration_status_label.style().polish(self.calibration_status_label)

    def _draw_empty_plot(self) -> None:
        self.figure.clear()
        axis = self.figure.add_subplot(111)
        self._style_axis(axis)
        axis.text(
            0.5,
            0.5,
            "Enregistrez les points pour tracer la courbe de linéarité",
            ha="center",
            va="center",
            color="#667C88",
            transform=axis.transAxes,
        )
        self.canvas.draw_idle()

    def _draw_record(self, record: CalibrationRecord) -> None:
        references = np.asarray([point.reference_value for point in record.points], dtype=float)
        voltages = np.asarray([point.measured_voltage for point in record.points], dtype=float)
        fit_reference = np.linspace(float(references.min()), float(references.max()), 200)
        fit_voltage = record.sensitivity_v_per_unit * fit_reference + record.intercept_volts

        self.figure.clear()
        axis = self.figure.add_subplot(111)
        self._style_axis(axis)
        axis.scatter(
            references,
            voltages,
            s=48,
            color="#1A7188",
            edgecolor="#FFFFFF",
            linewidth=1.0,
            zorder=3,
            label="Mesures",
        )
        axis.plot(fit_reference, fit_voltage, color="#C47B18", linewidth=1.8, label="Régression")
        axis.legend(frameon=False, loc="best")
        self.canvas.draw_idle()

    def _style_axis(self, axis) -> None:
        self.figure.set_facecolor("#FFFFFF")
        axis.set_facecolor("#FFFFFF")
        axis.set_xlabel(f"Référence ({self.unit_combo.currentText() or 'unité'})", color="#405965")
        axis.set_ylabel("Tension mesurée (V)", color="#405965")
        axis.tick_params(colors="#667C88", labelsize=9)
        axis.grid(True, color="#DCE5EA", linewidth=0.7, alpha=0.85)
        axis.spines["top"].set_visible(False)
        axis.spines["right"].set_visible(False)
        axis.spines["bottom"].set_color("#B7C6CD")
        axis.spines["left"].set_color("#B7C6CD")

    def _table_text(self, row: int, column: int) -> str:
        item = self.points_table.item(row, column)
        return item.text().strip() if item is not None else ""

    def get_calibration_data(self) -> dict[str, Any]:
        self._save_active_points()
        return {
            "timestamp": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            "active_channel": self._active_channel,
            "completed": len(self._channel_records) == self.CHANNEL_COUNT,
            "completed_channels": sorted(self._channel_records),
            "channels": {str(channel): record.to_dict() for channel, record in self._channel_records.items()},
        }

    def load_calibration_data(self, data: dict[str, Any]) -> None:
        records = data.get("channels", {})
        for channel_key, payload in records.items():
            try:
                channel = int(channel_key)
                record = CalibrationRecord.from_dict(payload)
            except (KeyError, TypeError, ValueError):
                continue
            self._channel_records[channel] = record
            self._channel_points[channel] = [
                (point.reference_value, point.measured_voltage) for point in record.points
            ]
            self._channel_metadata[channel] = {
                "sensor_id": record.sensor_id,
                "sensor_type": record.sensor_type,
                "physical_unit": record.physical_unit,
                "operator": record.operator,
                "reference_equipment": record.reference_equipment,
            }
        active_channel = int(data.get("active_channel", self._active_channel))
        self.channel_combo.blockSignals(True)
        self.channel_combo.setCurrentIndex(active_channel)
        self.channel_combo.blockSignals(False)
        self._load_channel(active_channel)


# Historical class name kept for imports outside the active GUI.
CalibrationViewMaritime = CalibrationView
