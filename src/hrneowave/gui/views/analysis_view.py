"""Scientific signal and spectrum workbench for CHNeoWave."""

from __future__ import annotations

from pathlib import Path

import numpy as np
from PySide6.QtCore import QModelIndex, Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QListView,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QSplitter,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ...core.legacy_raw import (
    LegacyRawError,
    LegacyRawHeader,
    LegacyRawImportOptions,
    read_legacy_raw_header,
)
from ...core.post_processor import PostProcessor
from ...core.scientific_report import build_scientific_report_text
from ...core.wave_analysis import WaveAnalyzer
from ..workbench.channel_delegate import ChannelDelegate
from ..workbench.channel_model import ChannelItem, ChannelListModel
from ..workbench.icons import line_icon
from ..workbench.metric_strip import MetricStrip
from ..workbench.plot_widget import ScientificPlotWidget

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


class LegacyRawImportDialog(QDialog):
    """Confirm physical information absent from a legacy RAW header."""

    SENSOR_TYPES = (
        ("Élévation de houle", "wave_height", "cm"),
        ("Déplacement", "displacement", "mm"),
        ("Force", "force", "N"),
        ("Accélération", "accelerometer", "m/s²"),
        ("Pression", "pressure", "bar"),
        ("Angle", "inclination", "°"),
        ("Signal générique", "generic", "unité"),
    )

    def __init__(self, source_path: Path, header: LegacyRawHeader, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Interprétation physique du RAW")
        self.setModal(True)
        self.setMinimumWidth(480)
        layout = QVBoxLayout(self)
        identity = QLabel(
            f"{source_path.name}\n{header.sample_rate_hz:g} Hz · "
            f"{header.declared_duration_s:g} s · {header.channel_count} voies"
        )
        identity.setObjectName("sectionTitle")
        layout.addWidget(identity)
        note = QLabel(
            "Le RAW ne porte pas l’unité physique. Confirmez X = V × facteur "
            "avant toute interprétation scientifique."
        )
        note.setWordWrap(True)
        note.setObjectName("mutedText")
        layout.addWidget(note)
        form = QFormLayout()
        self.sensor_type_combo = QComboBox()
        for label, sensor_type, _unit in self.SENSOR_TYPES:
            self.sensor_type_combo.addItem(label, sensor_type)
        self.physical_unit_combo = QComboBox()
        self.physical_unit_combo.setEditable(True)
        self.physical_unit_combo.addItems(["cm", "m", "mm", "N", "g", "kg", "m/s²", "bar", "°"])
        self.apply_calibration_check = QCheckBox("Appliquer les facteurs de l’en-tête")
        self.apply_calibration_check.setChecked(True)
        self.confirm_calibration_check = QCheckBox("Conversion et unité vérifiées")
        form.addRow("Signal", self.sensor_type_combo)
        form.addRow("Unité", self.physical_unit_combo)
        form.addRow("Conversion", self.apply_calibration_check)
        form.addRow("Attestation", self.confirm_calibration_check)
        layout.addLayout(form)
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)
        self.sensor_type_combo.currentIndexChanged.connect(self._apply_default_unit)
        self.apply_calibration_check.toggled.connect(self._refresh_state)
        self.confirm_calibration_check.toggled.connect(self._refresh_state)
        self.physical_unit_combo.currentTextChanged.connect(self._refresh_state)
        self._apply_default_unit(0)
        self._refresh_state()

    def _apply_default_unit(self, index: int) -> None:
        self.physical_unit_combo.setCurrentText(self.SENSOR_TYPES[index][2])

    def _refresh_state(self, *_args) -> None:
        calibrated = self.apply_calibration_check.isChecked()
        self.physical_unit_combo.setEnabled(calibrated)
        self.confirm_calibration_check.setEnabled(calibrated)
        valid = not calibrated or (
            self.confirm_calibration_check.isChecked()
            and bool(self.physical_unit_combo.currentText().strip())
        )
        self.buttons.button(QDialogButtonBox.StandardButton.Ok).setEnabled(valid)

    def import_options(self) -> LegacyRawImportOptions:
        return LegacyRawImportOptions(
            sensor_type=str(self.sensor_type_combo.currentData()),
            physical_unit=self.physical_unit_combo.currentText().strip(),
            apply_calibration=self.apply_calibration_check.isChecked(),
            calibration_confirmed=(
                self.confirm_calibration_check.isChecked()
                if self.apply_calibration_check.isChecked()
                else False
            ),
        )


class SourceChannelPane(QFrame):
    """Horizontal source and channel command bar for multi-probe campaigns."""

    file_open_requested = Signal()
    refresh_requested = Signal()
    file_selected = Signal(str)
    channel_selected = Signal(str)
    visibility_changed = Signal(str, bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sourceChannelBar")
        self.channel_model = ChannelListModel(parent=self)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(4)

        source_row = QHBoxLayout()
        source_row.setSpacing(5)
        source_label = QLabel("SOURCE")
        source_label.setObjectName("commandCaption")
        source_row.addWidget(source_label)
        self.data_combo = QComboBox()
        self.data_combo.setObjectName("sourceCombo")
        self.data_combo.setMinimumWidth(220)
        self.data_combo.addItem("Aucun fichier", None)
        source_row.addWidget(self.data_combo)
        self.load_button = QPushButton("Ouvrir…")
        self.load_button.setObjectName("commandButton")
        self.load_button.setIcon(line_icon("folder", "#78919C"))
        self.refresh_button = self._tool("fit", "Actualiser les fichiers")
        source_row.addWidget(self.load_button)
        source_row.addWidget(self.refresh_button)
        self.source_name = QLabel("AUCUNE SOURCE")
        self.source_name.hide()
        self.source_meta = QLabel("— Hz · — pts · — s")
        self.source_meta.setObjectName("sourceMeta")
        source_row.addWidget(self.source_meta)
        source_row.addStretch()
        self.raw_signal_check = QCheckBox("Tension brute")
        self.raw_signal_check.setVisible(False)
        self.center_signal_check = QCheckBox("Centrer")
        self.overlay_channels_check = QCheckBox("Comparer")
        self.overlay_channels_check.setChecked(True)
        self.overlay_channels_check.hide()
        source_row.addWidget(self.raw_signal_check)
        source_row.addWidget(self.center_signal_check)
        layout.addLayout(source_row)

        channel_row = QHBoxLayout()
        channel_row.setSpacing(4)
        label = QLabel("VOIES")
        label.setObjectName("commandCaption")
        channel_row.addWidget(label)
        self.channel_count = QLabel("0 / 0 visibles")
        self.channel_count.setObjectName("channelVisibleCount")
        channel_row.addWidget(self.channel_count)
        self.show_all_button = QPushButton("Toutes")
        self.hide_all_button = QPushButton("Aucune")
        self.isolate_button = QPushButton("Isoler")
        for button in (self.show_all_button, self.hide_all_button, self.isolate_button):
            button.setObjectName("channelCommand")
            channel_row.addWidget(button)
        self.channel_list = QListView()
        self.channel_list.setObjectName("channelRibbon")
        self.channel_list.setModel(self.channel_model)
        self.channel_list.setItemDelegate(ChannelDelegate(self.channel_list))
        self.channel_list.setSelectionMode(QListView.SelectionMode.SingleSelection)
        self.channel_list.setFlow(QListView.Flow.LeftToRight)
        self.channel_list.setWrapping(False)
        self.channel_list.setHorizontalScrollMode(QListView.ScrollMode.ScrollPerPixel)
        self.channel_list.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.channel_list.setFixedHeight(38)
        channel_row.addWidget(self.channel_list, 1)
        layout.addLayout(channel_row)

        self.load_button.clicked.connect(self.file_open_requested.emit)
        self.refresh_button.clicked.connect(self.refresh_requested.emit)
        self.data_combo.activated.connect(self._emit_file)
        self.channel_list.selectionModel().currentChanged.connect(self._emit_channel)
        self.channel_model.channel_visibility_changed.connect(self._on_visibility_changed)
        self.show_all_button.clicked.connect(lambda: self.channel_model.set_all_visible(True))
        self.hide_all_button.clicked.connect(lambda: self.channel_model.set_all_visible(False))
        self.isolate_button.clicked.connect(self._isolate_current)

    @staticmethod
    def _tool(icon: str, tooltip: str) -> QPushButton:
        button = QPushButton()
        button.setObjectName("iconTool")
        button.setFixedSize(25, 24)
        button.setIcon(line_icon(icon, "#78919C"))
        button.setToolTip(tooltip)
        return button

    def _emit_file(self, _index: int) -> None:
        path = self.data_combo.currentData()
        if path:
            self.file_selected.emit(str(path))

    def _emit_channel(self, current: QModelIndex, _previous: QModelIndex) -> None:
        if current.isValid():
            self.channel_selected.emit(str(current.data(ChannelListModel.KeyRole)))

    def _isolate_current(self) -> None:
        current = self.channel_list.currentIndex()
        if current.isValid():
            self.channel_model.set_only_visible(str(current.data(ChannelListModel.KeyRole)))

    def _on_visibility_changed(self, channel: str, visible: bool) -> None:
        self._update_visible_count()
        self.visibility_changed.emit(channel, visible)

    def _update_visible_count(self) -> None:
        total = self.channel_model.rowCount()
        visible = len(self.channel_model.visible_keys())
        self.channel_count.setText(f"{visible} / {total} visibles")

    def set_source(self, name: str, rate: float, samples: int, duration: float) -> None:
        self.source_name.setText(name.upper())
        self.source_meta.setText(
            f"{rate:g} Hz · {samples:,} pts · {duration:.3f} s".replace(",", " ")
        )

    def set_channels(self, channels: list[ChannelItem]) -> None:
        self.channel_model.set_channels(channels)
        self._update_visible_count()
        if channels:
            self.channel_list.setCurrentIndex(self.channel_model.index(0, 0))


class ScientificInspector(QFrame):
    """Contextual controls that map one-to-one to analysis parameters."""

    analysis_requested = Signal(str, dict)
    export_requested = Signal(str)
    details_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("scientificInspector")
        self.setMinimumWidth(252)
        self.setMaximumWidth(310)
        self._build_ui()

    @staticmethod
    def _section(title: str) -> tuple[QFrame, QFormLayout]:
        frame = QFrame()
        frame.setObjectName("inspectorSection")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(9, 7, 9, 8)
        layout.setSpacing(5)
        label = QLabel(title.upper())
        label.setObjectName("inspectorSectionTitle")
        layout.addWidget(label)
        form = QFormLayout()
        form.setHorizontalSpacing(8)
        form.setVerticalSpacing(5)
        layout.addLayout(form)
        return frame, form

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        header = QFrame()
        header.setObjectName("paneHeader")
        row = QHBoxLayout(header)
        row.setContentsMargins(9, 5, 8, 5)
        title = QLabel("ANALYSE")
        title.setObjectName("paneTitle")
        self.analysis_status_label = QLabel("PRÊT")
        self.analysis_status_label.setObjectName("analysisState")
        row.addWidget(title)
        row.addStretch()
        row.addWidget(self.analysis_status_label)
        root.addWidget(header)
        scroll = QScrollArea()
        scroll.setObjectName("inspectorScroll")
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.parameters_panel = QWidget()
        panel = QVBoxLayout(self.parameters_panel)
        panel.setContentsMargins(0, 0, 0, 0)
        panel.setSpacing(0)
        interval, form = self._section("Intervalle")
        self.interval_preset_combo = QComboBox()
        for label, seconds in (
            ("Tout le signal", 0.0),
            ("30 secondes", 30.0),
            ("1 minute", 60.0),
            ("5 minutes", 300.0),
            ("10 minutes", 600.0),
            ("Personnalisé", -1.0),
        ):
            self.interval_preset_combo.addItem(label, seconds)
        self.start_time_spin = self._time_spin(False)
        self.end_time_spin = self._time_spin(True)
        self.duration_value = self._technical("—")
        self.samples_value = self._technical("—")
        form.addRow("Fenêtre", self.interval_preset_combo)
        form.addRow("Début", self.start_time_spin)
        form.addRow("Fin", self.end_time_spin)
        form.addRow("Durée", self.duration_value)
        self.samples_value.setToolTip("N = nombre total d’échantillons analysés par voie")
        form.addRow("Échantillons N", self.samples_value)
        panel.addWidget(interval)
        welch, form = self._section("Welch PSD")
        self.window_combo = QComboBox()
        for label, value in (
            ("Hann", "hann"),
            ("Hamming", "hamming"),
            ("Blackman", "blackman"),
            ("Blackman-Harris", "blackmanharris"),
            ("Flattop", "flattop"),
            ("Rectangulaire", "boxcar"),
        ):
            self.window_combo.addItem(label, value)
        self.segment_length_combo = QComboBox()
        self.segment_length_combo.addItems(["256", "512", "1024", "2048", "4096", "8192"])
        self.segment_length_combo.setCurrentText("1024")
        self.overlap_spin = QSpinBox()
        self.overlap_spin.setRange(0, 90)
        self.overlap_spin.setValue(50)
        self.overlap_spin.setSuffix(" %")
        self.average_combo = QComboBox()
        self.average_combo.addItem("Moyenne", "mean")
        self.average_combo.addItem("Médiane robuste", "median")
        self.zero_padding_combo = QComboBox()
        for label, factor in (("Aucun", 1), ("×2", 2), ("×4", 4), ("×8", 8)):
            self.zero_padding_combo.addItem(label, factor)
        self.resolution_value = self._technical("—")
        form.addRow("Fenêtre", self.window_combo)
        form.addRow("Segment", self.segment_length_combo)
        form.addRow("Recouvrement", self.overlap_spin)
        form.addRow("Agrégation", self.average_combo)
        form.addRow("Zéro-padding", self.zero_padding_combo)
        form.addRow("Résolution", self.resolution_value)
        panel.addWidget(welch)
        conditioning, form = self._section("Conditionnement")
        self.detrend_combo = QComboBox()
        self.detrend_combo.addItem("Aucun", "none")
        self.detrend_combo.addItem("Retirer moyenne", "constant")
        self.detrend_combo.addItem("Retirer dérive linéaire", "linear")
        self.detrend_combo.setCurrentIndex(2)
        self.filter_combo = QComboBox()
        for label, value in (
            ("Aucun", "none"),
            ("Passe-bas Butterworth", "lowpass"),
            ("Passe-haut Butterworth", "highpass"),
            ("Passe-bande Butterworth", "bandpass"),
            ("Coupe-bande Butterworth", "bandstop"),
        ):
            self.filter_combo.addItem(label, value)
        self.filter_low_spin = self._frequency_spin(False)
        self.filter_high_spin = self._frequency_spin(False)
        self.filter_order_spin = QSpinBox()
        self.filter_order_spin.setRange(1, 10)
        self.filter_order_spin.setValue(4)
        form.addRow("Dérive", self.detrend_combo)
        form.addRow("Filtre", self.filter_combo)
        form.addRow("Coupure basse", self.filter_low_spin)
        form.addRow("Coupure haute", self.filter_high_spin)
        form.addRow("Ordre", self.filter_order_spin)
        panel.addWidget(conditioning)
        band, form = self._section("Bande utile")
        self.min_frequency_spin = self._frequency_spin(False)
        self.max_frequency_spin = self._frequency_spin(True)
        form.addRow("f min", self.min_frequency_spin)
        form.addRow("f max", self.max_frequency_spin)
        panel.addWidget(band)
        reading, form = self._section("Lecture")
        self.confidence_interval_check = QCheckBox("IC PSD 95 %")
        self.confidence_interval_check.setChecked(True)
        self.cursor_value = self._technical("t —   y —")
        form.addRow("Incertitude", self.confidence_interval_check)
        form.addRow("Curseur", self.cursor_value)
        panel.addWidget(reading)
        panel.addStretch()
        scroll.setWidget(self.parameters_panel)
        root.addWidget(scroll, 1)
        actions = QFrame()
        actions.setObjectName("inspectorActions")
        action_layout = QVBoxLayout(actions)
        action_layout.setContentsMargins(8, 7, 8, 8)
        action_layout.setSpacing(5)
        self.run_button = QPushButton("CALCULER")
        self.run_button.setObjectName("runAnalysis")
        self.run_button.setIcon(line_icon("run", "#071A24"))
        action_layout.addWidget(self.run_button)
        utility = QHBoxLayout()
        utility.setSpacing(4)
        self.export_format_combo = QComboBox()
        for label, value in (("CSV", "csv"), ("JSON", "json"), ("HDF5", "hdf5"), ("Texte", "txt")):
            self.export_format_combo.addItem(label, value)
        self.export_button = QPushButton("Exporter")
        self.export_button.setObjectName("compactAction")
        self.details_button = QPushButton("Résultats")
        self.details_button.setObjectName("compactAction")
        self.details_button.setCheckable(True)
        utility.addWidget(self.export_format_combo)
        utility.addWidget(self.export_button)
        utility.addWidget(self.details_button)
        action_layout.addLayout(utility)
        root.addWidget(actions)
        self.run_button.clicked.connect(self._emit_analysis_request)
        self.export_button.clicked.connect(
            lambda: self.export_requested.emit(str(self.export_format_combo.currentData()))
        )
        self.details_button.clicked.connect(self.details_requested.emit)
        self.interval_preset_combo.currentIndexChanged.connect(self._apply_interval_preset)
        self.start_time_spin.valueChanged.connect(self._refresh_interval_readout)
        self.end_time_spin.valueChanged.connect(self._refresh_interval_readout)
        self.filter_combo.currentIndexChanged.connect(self._update_filter_controls)
        self._record_duration = 0.0
        self._record_samples = 0
        self._sample_rate = 0.0
        self._update_filter_controls()

    @staticmethod
    def _technical(text: str) -> QLabel:
        label = QLabel(text)
        label.setObjectName("technicalValue")
        return label

    @staticmethod
    def _time_spin(end: bool) -> QDoubleSpinBox:
        spin = QDoubleSpinBox()
        spin.setRange(0, 10_000_000)
        spin.setDecimals(3)
        spin.setSuffix(" s")
        if end:
            spin.setSpecialValueText("Fin")
        return spin

    @staticmethod
    def _frequency_spin(maximum: bool) -> QDoubleSpinBox:
        spin = QDoubleSpinBox()
        spin.setRange(0, 10000)
        spin.setDecimals(4)
        spin.setSuffix(" Hz")
        if maximum:
            spin.setSpecialValueText("Nyquist")
        return spin

    def _emit_analysis_request(self) -> None:
        self.analysis_requested.emit("complete", self.parameters())

    def parameters(self) -> dict:
        maximum = self.max_frequency_spin.value()
        segment = int(self.segment_length_combo.currentText())
        padding_factor = int(self.zero_padding_combo.currentData())
        filter_type = str(self.filter_combo.currentData())
        return {
            "window_size": segment,
            "overlap": self.overlap_spin.value() / 100.0,
            "fft_length": segment * padding_factor if padding_factor > 1 else None,
            "average": str(self.average_combo.currentData()),
            "min_frequency": self.min_frequency_spin.value(),
            "max_frequency": maximum if maximum > 0 else None,
            "detrend": str(self.detrend_combo.currentData()),
            "filter_type": filter_type,
            "filter_low_frequency": (
                self.filter_low_spin.value()
                if filter_type in {"highpass", "bandpass", "bandstop"}
                else None
            ),
            "filter_high_frequency": (
                self.filter_high_spin.value()
                if filter_type in {"lowpass", "bandpass", "bandstop"}
                else None
            ),
            "filter_order": self.filter_order_spin.value(),
            "window": str(self.window_combo.currentData()),
            "start_time_s": self.start_time_spin.value(),
            "end_time_s": self.end_time_spin.value() or None,
        }

    def set_record(self, duration: float, samples: int, rate: float) -> None:
        duration = max(0.0, float(duration))
        self._record_duration = duration
        self._record_samples = int(samples)
        self._sample_rate = float(rate)
        self.start_time_spin.setMaximum(duration)
        self.end_time_spin.setMaximum(duration)
        self.end_time_spin.setValue(0.0)
        self.duration_value.setText(f"{duration:.3f} s")
        self.samples_value.setText(f"N = {samples:,}".replace(",", " "))
        segment = int(self.segment_length_combo.currentText())
        self.resolution_value.setText(
            f"Rayleigh {rate / segment:.5g} Hz" if rate else "—"
        )
        nyquist = rate / 2.0 if rate else 0.0
        for spin in (
            self.min_frequency_spin,
            self.max_frequency_spin,
            self.filter_low_spin,
            self.filter_high_spin,
        ):
            spin.setMaximum(nyquist)
        if nyquist > 0:
            self.filter_low_spin.setValue(max(0.0001, nyquist * 0.01))
            self.filter_high_spin.setValue(nyquist * 0.8)
        default_interval = 300.0 if duration > 600.0 else 0.0
        default_index = self.interval_preset_combo.findData(default_interval)
        self.interval_preset_combo.setCurrentIndex(max(0, default_index))
        self._update_filter_controls()
        self._refresh_interval_readout()

    def set_record_duration(self, duration_s: float) -> None:
        self.set_record(duration_s, 0, 0.0)

    def _apply_interval_preset(self, _index: int) -> None:
        seconds = float(self.interval_preset_combo.currentData())
        if seconds < 0 or self._record_duration <= 0:
            return
        if seconds == 0 or seconds >= self._record_duration:
            self.start_time_spin.setValue(0.0)
            self.end_time_spin.setValue(0.0)
            return
        start = min(self.start_time_spin.value(), self._record_duration - seconds)
        self.start_time_spin.setValue(start)
        self.end_time_spin.setValue(start + seconds)

    def shift_interval(self, direction: int) -> None:
        start = self.start_time_spin.value()
        end = self.end_time_spin.value()
        if end <= start:
            return
        span = end - start
        new_start = min(max(0.0, start + int(direction) * span), self._record_duration - span)
        self.start_time_spin.setValue(new_start)
        self.end_time_spin.setValue(new_start + span)

    def set_interval_custom(self) -> None:
        custom = self.interval_preset_combo.findData(-1.0)
        if custom >= 0 and self.interval_preset_combo.currentIndex() != custom:
            self.interval_preset_combo.blockSignals(True)
            self.interval_preset_combo.setCurrentIndex(custom)
            self.interval_preset_combo.blockSignals(False)

    def _update_filter_controls(self, *_args) -> None:
        filter_type = str(self.filter_combo.currentData())
        self.filter_low_spin.setEnabled(filter_type in {"highpass", "bandpass", "bandstop"})
        self.filter_high_spin.setEnabled(filter_type in {"lowpass", "bandpass", "bandstop"})
        self.filter_order_spin.setEnabled(filter_type != "none")

    def _refresh_interval_readout(self, *_args) -> None:
        if not hasattr(self, "_record_duration"):
            return
        start = self.start_time_spin.value()
        end = self.end_time_spin.value()
        selected_duration = end - start if end > start else self._record_duration
        selected_samples = (
            int(round(selected_duration * self._sample_rate))
            if self._sample_rate > 0
            else self._record_samples
        )
        self.duration_value.setText(f"{selected_duration:.3f} s")
        self.samples_value.setText(f"N = {selected_samples:,}".replace(",", " "))


class AnalysisDetailsDrawer(QFrame):
    """Secondary evidence tables kept out of the signal workspace."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("detailsDrawer")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        modes = QFrame()
        modes.setObjectName("detailsModes")
        row = QHBoxLayout(modes)
        row.setContentsMargins(6, 3, 6, 3)
        row.setSpacing(3)
        self.stack = QStackedWidget()
        self.mode_buttons = []
        for index, label in enumerate(("TEMPOREL", "SPECTRAL", "QUALITÉ", "RAPPORT")):
            button = QPushButton(label)
            button.setObjectName("drawerMode")
            button.setCheckable(True)
            button.setChecked(index == 0)
            button.clicked.connect(lambda _checked=False, target=index: self.set_mode(target))
            self.mode_buttons.append(button)
            row.addWidget(button)
        row.addStretch()
        layout.addWidget(modes)
        self.stats_table = self._table()
        self.spectral_table = self._table()
        self.wave_table = self.spectral_table
        self.quality_table = self._table()
        self.report_text = QTextEdit()
        self.report_text.setReadOnly(True)
        for widget in (
            self.stats_table,
            self.spectral_table,
            self.quality_table,
            self.report_text,
        ):
            self.stack.addWidget(widget)
        layout.addWidget(self.stack, 1)

    @staticmethod
    def _table() -> QTableWidget:
        table = QTableWidget()
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        table.horizontalHeader().setStretchLastSection(True)
        return table

    def set_mode(self, index: int) -> None:
        self.stack.setCurrentIndex(index)
        for current, button in enumerate(self.mode_buttons):
            button.setChecked(current == index)


class AnalysisResultsArea(QFrame):
    """One maximised scientific scene with switchable representations."""

    inspector_visibility_requested = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("analysisWorkbench")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        status = QFrame()
        status.setObjectName("workbenchStatus")
        row = QHBoxLayout(status)
        row.setContentsMargins(9, 3, 8, 3)
        self.analysis_status_label = QLabel("AUCUNE DONNÉE")
        self.analysis_status_label.setObjectName("analysisState")
        self.analysis_count_label = QLabel("0 calcul")
        self.analysis_count_label.setObjectName("plotMeta")
        self.plot_mode_buttons: dict[str, QPushButton] = {}
        for mode, caption in (
            ("time", "SIGNAL TEMPOREL"),
            ("spectrum", "SPECTRE"),
            ("spectrogram", "TEMPS–FRÉQUENCE"),
        ):
            button = QPushButton(caption)
            button.setObjectName("plotModeButton")
            button.setCheckable(True)
            button.setAutoExclusive(True)
            button.clicked.connect(
                lambda _checked=False, selected_mode=mode: self.set_plot_mode(selected_mode)
            )
            self.plot_mode_buttons[mode] = button
        self.time_cursor_label = QLabel("t —   y —")
        self.time_cursor_label.setObjectName("plotMeta")
        self.spectrum_readout_label = QLabel("pic —   Δf —")
        self.spectrum_readout_label.setObjectName("plotMeta")
        self.spectrogram_readout_label = QLabel("voie —   plage — dB")
        self.spectrogram_readout_label.setObjectName("plotMeta")
        row.addWidget(self.analysis_status_label)
        row.addWidget(self.analysis_count_label)
        row.addStretch()
        for button in self.plot_mode_buttons.values():
            row.addWidget(button)
        self.inspector_toggle_button = QPushButton("PARAMÈTRES")
        self.inspector_toggle_button.setObjectName("inspectorToggle")
        self.inspector_toggle_button.setCheckable(True)
        self.inspector_toggle_button.setChecked(True)
        self.inspector_toggle_button.toggled.connect(self.inspector_visibility_requested.emit)
        row.addWidget(self.inspector_toggle_button)
        row.addSpacing(10)
        row.addWidget(self.time_cursor_label)
        row.addSpacing(12)
        row.addWidget(self.spectrum_readout_label)
        row.addSpacing(12)
        row.addWidget(self.spectrogram_readout_label)
        layout.addWidget(status)
        controls = QFrame()
        controls.setObjectName("analysisViewControls")
        controls_layout = QHBoxLayout(controls)
        controls_layout.setContentsMargins(8, 3, 8, 3)
        controls_layout.setSpacing(5)
        self.context_controls = QStackedWidget()
        self.context_controls.setObjectName("analysisContextControls")

        time_controls = QWidget()
        time_row = QHBoxLayout(time_controls)
        time_row.setContentsMargins(0, 0, 0, 0)
        time_row.setSpacing(5)
        time_row.addWidget(QLabel("INTERVALLE"))
        self.time_window_combo = QComboBox()
        for label, seconds in (
            ("Tout", 0.0),
            ("30 s", 30.0),
            ("1 min", 60.0),
            ("5 min", 300.0),
            ("10 min", 600.0),
            ("Personnalisé", -1.0),
        ):
            self.time_window_combo.addItem(label, seconds)
        self.time_previous_button = QPushButton("PRÉC.")
        self.time_next_button = QPushButton("SUIV.")
        time_row.addWidget(self.time_window_combo)
        time_row.addWidget(self.time_previous_button)
        time_row.addWidget(self.time_next_button)
        time_row.addSpacing(10)
        time_row.addWidget(QLabel("AFFICHAGE"))
        self.time_display_combo = QComboBox()
        self.time_display_combo.addItem("Amplitude physique", "physical")
        self.time_display_combo.addItem("Centré", "centered")
        self.time_display_combo.addItem("Signal analysé", "analysis")
        self.time_display_combo.addItem("Normalisé — visuel", "normalized")
        time_row.addWidget(self.time_display_combo)
        time_row.addStretch()
        self.context_controls.addWidget(time_controls)

        spectrum_controls = QWidget()
        spectrum_row = QHBoxLayout(spectrum_controls)
        spectrum_row.setContentsMargins(0, 0, 0, 0)
        spectrum_row.setSpacing(5)
        spectrum_row.addWidget(QLabel("ORDONNÉE"))
        self.spectrum_representation_combo = QComboBox()
        self.spectrum_representation_combo.addItem("PSD", "psd")
        self.spectrum_representation_combo.addItem("ASD", "asd")
        self.spectrum_representation_combo.addItem("PSD en dB", "db")
        self.spectrum_representation_combo.addItem("Énergie cumulée", "energy")
        spectrum_row.addWidget(self.spectrum_representation_combo)
        spectrum_row.addWidget(QLabel("AXES"))
        self.spectrum_axes_combo = QComboBox()
        self.spectrum_axes_combo.addItem("f linéaire · Y log", (False, True))
        self.spectrum_axes_combo.addItem("f linéaire · Y linéaire", (False, False))
        self.spectrum_axes_combo.addItem("f log · Y log", (True, True))
        spectrum_row.addWidget(self.spectrum_axes_combo)
        self.spectrum_band_only_check = QCheckBox("Bande utile")
        self.spectrum_band_only_check.setChecked(True)
        self.spectrum_confidence_check = QCheckBox("IC 95 %")
        self.spectrum_confidence_check.setChecked(True)
        spectrum_row.addWidget(self.spectrum_band_only_check)
        spectrum_row.addWidget(self.spectrum_confidence_check)
        spectrum_row.addStretch()
        self.context_controls.addWidget(spectrum_controls)

        spectrogram_controls = QWidget()
        spectrogram_row = QHBoxLayout(spectrogram_controls)
        spectrogram_row.setContentsMargins(0, 0, 0, 0)
        spectrogram_row.setSpacing(5)
        spectrogram_row.addWidget(QLabel("DYNAMIQUE"))
        self.spectrogram_range_combo = QComboBox()
        for label, value in (("40 dB", 40.0), ("60 dB", 60.0), ("80 dB", 80.0), ("100 dB", 100.0)):
            self.spectrogram_range_combo.addItem(label, value)
        self.spectrogram_range_combo.setCurrentIndex(1)
        spectrogram_row.addWidget(self.spectrogram_range_combo)
        spectrogram_row.addWidget(QLabel("PALETTE"))
        self.spectrogram_palette_combo = QComboBox()
        for label, value in (
            ("Viridis", "viridis"),
            ("Cividis", "cividis"),
            ("Plasma", "plasma"),
            ("Inferno", "inferno"),
        ):
            self.spectrogram_palette_combo.addItem(label, value)
        spectrogram_row.addWidget(self.spectrogram_palette_combo)
        self.spectrogram_channel_label = QLabel("VOIE ACTIVE —")
        self.spectrogram_channel_label.setObjectName("plotMeta")
        spectrogram_row.addWidget(self.spectrogram_channel_label)
        spectrogram_row.addStretch()
        self.context_controls.addWidget(spectrogram_controls)
        controls_layout.addWidget(self.context_controls)
        layout.addWidget(controls)
        self.time_plot = ScientificPlotWidget("Signal temporel", "Temps (s)", "Amplitude")
        self.spectrum_plot = ScientificPlotWidget(
            "Densité spectrale de puissance",
            "Fréquence (Hz)",
            "PSD",
            logarithmic_y=True,
        )
        self.spectrogram_plot = ScientificPlotWidget(
            "Spectrogramme",
            "Temps (s)",
            "Fréquence (Hz)",
        )
        self.plot_stack = QStackedWidget()
        self.plot_stack.setObjectName("plotSceneStack")
        self.plot_stack.addWidget(self.time_plot)
        self.plot_stack.addWidget(self.spectrum_plot)
        self.plot_stack.addWidget(self.spectrogram_plot)
        layout.addWidget(self.plot_stack, 1)
        self.metric_strip = MetricStrip()
        layout.addWidget(self.metric_strip)
        self.details_drawer = AnalysisDetailsDrawer()
        self.details_drawer.setVisible(False)
        self.details_drawer.setMinimumHeight(180)
        layout.addWidget(self.details_drawer)
        self.stats_table = self.details_drawer.stats_table
        self.spectral_table = self.details_drawer.spectral_table
        self.wave_table = self.spectral_table
        self.quality_table = self.details_drawer.quality_table
        self.report_text = self.details_drawer.report_text
        self.set_plot_mode("time")

    def set_plot_mode(self, mode: str) -> None:
        """Switch the representation while preserving the whole plotting area."""

        targets = {
            "time": (self.time_plot, 0),
            "spectrum": (self.spectrum_plot, 1),
            "spectrogram": (self.spectrogram_plot, 2),
        }
        mode = mode if mode in targets else "time"
        target, control_index = targets[mode]
        self.plot_stack.setCurrentWidget(target)
        self.context_controls.setCurrentIndex(control_index)
        for name, button in self.plot_mode_buttons.items():
            button.setChecked(name == mode)
        self.time_cursor_label.setVisible(mode == "time")
        self.spectrum_readout_label.setVisible(mode == "spectrum")
        self.spectrogram_readout_label.setVisible(mode == "spectrogram")

    def update_analysis_status(self, status: str, count: int = 0) -> None:
        self.analysis_status_label.setText(status.upper())
        self.analysis_count_label.setText(f"{count} calcul" + ("s" if count != 1 else ""))


class AnalysisView(QWidget):
    """High-density laboratory view backed by the validated post-processor."""

    analysis_completed = Signal(str, dict)
    filter_applied = Signal(str, dict)
    data_exported = Signal(str)
    source_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_dark_mode = False
        self.analysis_count = 0
        self.post_processor = PostProcessor()
        self.current_project_dir: Path | None = None
        self.current_project_metadata: dict[str, object] = {}
        self.current_data_file: str | None = None
        self.current_analysis_result: dict[str, object] | None = None
        self._tools_panel_expanded = False
        self._selected_channel = ""
        self._setting_region = False
        self._build_ui()
        self._setup_connections()

    def _build_ui(self) -> None:
        self.setObjectName("analysisWorkspace")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.source_pane = SourceChannelPane()
        self.results_area = AnalysisResultsArea()
        self.inspector = ScientificInspector()
        self.tools_panel = self.inspector
        self.tools_toggle_button = self.inspector.details_button
        layout.addWidget(self.source_pane)
        work_area = QSplitter(Qt.Orientation.Horizontal)
        work_area.setObjectName("analysisHorizontalSplitter")
        work_area.addWidget(self.results_area)
        work_area.addWidget(self.inspector)
        work_area.setSizes([1040, 280])
        work_area.setStretchFactor(0, 1)
        work_area.setStretchFactor(1, 0)
        layout.addWidget(work_area, 1)

    def _setup_connections(self) -> None:
        self.source_pane.file_open_requested.connect(self.open_file_dialog)
        self.source_pane.refresh_requested.connect(self.refresh_project_files)
        self.source_pane.file_selected.connect(self.load_data_file)
        self.source_pane.channel_selected.connect(self._select_channel)
        self.source_pane.visibility_changed.connect(self._on_plot_controls_changed)
        self.source_pane.raw_signal_check.toggled.connect(self._update_time_plot)
        self.source_pane.overlay_channels_check.toggled.connect(self._on_plot_controls_changed)
        self.inspector.analysis_requested.connect(self.on_analysis_requested)
        self.inspector.export_requested.connect(self.on_export_requested)
        self.inspector.details_requested.connect(self._toggle_tools_panel)
        self.inspector.segment_length_combo.currentTextChanged.connect(self._update_resolution_preview)
        self.inspector.zero_padding_combo.currentIndexChanged.connect(self._update_resolution_preview)
        self.inspector.start_time_spin.valueChanged.connect(self._sync_region_from_controls)
        self.inspector.end_time_spin.valueChanged.connect(self._sync_region_from_controls)
        self.inspector.interval_preset_combo.currentIndexChanged.connect(
            self.results_area.time_window_combo.setCurrentIndex
        )
        self.results_area.time_window_combo.currentIndexChanged.connect(
            self.inspector.interval_preset_combo.setCurrentIndex
        )
        self.results_area.time_previous_button.clicked.connect(
            lambda: self.inspector.shift_interval(-1)
        )
        self.results_area.time_next_button.clicked.connect(
            lambda: self.inspector.shift_interval(1)
        )
        self.results_area.time_display_combo.currentIndexChanged.connect(self._update_time_plot)
        self.results_area.spectrum_representation_combo.currentIndexChanged.connect(
            self._update_spectrum_plot
        )
        self.results_area.spectrum_axes_combo.currentIndexChanged.connect(
            self._update_spectrum_plot
        )
        self.results_area.spectrum_band_only_check.toggled.connect(self._update_spectrum_plot)
        self.results_area.spectrum_confidence_check.toggled.connect(self._update_spectrum_plot)
        self.results_area.spectrum_confidence_check.toggled.connect(
            self.inspector.confidence_interval_check.setChecked
        )
        self.inspector.confidence_interval_check.toggled.connect(
            self.results_area.spectrum_confidence_check.setChecked
        )
        self.results_area.spectrogram_range_combo.currentIndexChanged.connect(
            self._update_spectrogram_plot
        )
        self.results_area.spectrogram_palette_combo.currentIndexChanged.connect(
            self._update_spectrogram_plot
        )
        self.results_area.plot_mode_buttons["spectrogram"].clicked.connect(
            self._update_spectrogram_plot
        )
        self.results_area.time_plot.region_changed.connect(self._sync_controls_from_region)
        self.results_area.time_plot.cursor_moved.connect(self._on_time_cursor_moved)
        self.results_area.spectrum_plot.cursor_moved.connect(self._on_spectrum_cursor_moved)
        self.results_area.inspector_visibility_requested.connect(self.inspector.setVisible)
        self.source_pane.center_signal_check.hide()

    def _toggle_tools_panel(self) -> None:
        self._set_tools_panel_expanded(not self._tools_panel_expanded)

    def _set_tools_panel_expanded(self, expanded: bool) -> None:
        self._tools_panel_expanded = bool(expanded)
        self.results_area.details_drawer.setVisible(self._tools_panel_expanded)
        self.inspector.details_button.setChecked(self._tools_panel_expanded)
        self.inspector.details_button.setText(
            "Fermer" if self._tools_panel_expanded else "Résultats"
        )

    def set_project_context(self, project_metadata: dict, project_dir: str) -> None:
        self.current_project_metadata = project_metadata or {}
        self.current_project_dir = Path(project_dir) if project_dir else None
        self.refresh_project_files()

    def refresh_project_files(self) -> None:
        combo = self.source_pane.data_combo
        current_file = combo.currentData()
        combo.clear()
        combo.addItem("Aucun fichier", None)
        if not self.current_project_dir:
            return
        seen = set()
        for folder_name in ("exports", "data", "analysis"):
            folder = self.current_project_dir / folder_name
            if not folder.exists():
                continue
            for file_path in sorted(folder.glob("*")):
                if file_path.suffix.lower() not in {".csv", ".json", ".h5", ".hdf5", ".raw"}:
                    continue
                resolved = str(file_path.resolve())
                if resolved not in seen:
                    seen.add(resolved)
                    self._add_or_select_file_item(resolved, select=False)
        if current_file:
            index = combo.findData(current_file)
            if index >= 0:
                combo.setCurrentIndex(index)

    def open_file_dialog(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Charger des données",
            str(self._get_default_search_directory()),
            "Données laboratoire (*.raw *.csv *.json *.h5 *.hdf5)",
        )
        if file_path:
            self.load_data_file(file_path)

    def load_data_file(
        self,
        file_path: str,
        *,
        raw_options: LegacyRawImportOptions | None = None,
    ) -> bool:
        if not file_path:
            return False
        source_path = Path(file_path)
        if source_path.suffix.lower() == ".raw" and raw_options is None:
            try:
                header = read_legacy_raw_header(source_path)
            except LegacyRawError as exc:
                QMessageBox.warning(self, "Fichier RAW invalide", str(exc))
                return False
            dialog = LegacyRawImportDialog(source_path, header, self)
            if dialog.exec() != QDialog.DialogCode.Accepted:
                return False
            raw_options = dialog.import_options()
        if not self.post_processor.load_data_file(file_path, raw_options=raw_options):
            QMessageBox.warning(self, "Chargement", f"Impossible de charger:\n{file_path}")
            return False
        self.current_data_file = file_path
        self.source_changed.emit(source_path.name)
        self.current_analysis_result = None
        self._add_or_select_file_item(file_path)
        data = self.post_processor.current_data or {}
        channel_keys = list(data.get("channel_keys", []))
        sample_count = int(data.get("metadata", {}).get("n_samples", 0) or 0)
        if not sample_count and channel_keys:
            sample_count = self.post_processor._channel_sample_count(channel_keys[0])
        rate = self.post_processor.sample_rate
        duration = sample_count / rate if rate else 0.0
        self.source_pane.set_source(source_path.name, rate, sample_count, duration)
        self.inspector.set_record(duration, sample_count, rate)
        sensor_names = {
            "wave_height": "Élévation de houle",
            "accelerometer": "Accélération",
            "pressure": "Pression",
            "force": "Force",
            "inclination": "Angle",
        }
        channels = []
        for index, key in enumerate(channel_keys):
            metadata = self._channel_metadata(key)
            sensor = str(metadata.get("sensor_type") or metadata.get("type") or "Signal")
            channels.append(
                ChannelItem(
                    key=key,
                    name=str(metadata.get("name") or f"S{index + 1:02d}"),
                    sensor=sensor_names.get(sensor, sensor.replace("_", " ").title()),
                    unit=self._channel_unit(key),
                    color=CHANNEL_COLORS[index % len(CHANNEL_COLORS)],
                    visible=True,
                )
            )
        self.source_pane.set_channels(channels)
        if channel_keys:
            # Start with one readable trace; "Toutes" remains available for
            # explicit multi-channel comparison.
            self.source_pane.channel_model.set_only_visible(channel_keys[0])
        self.source_pane.raw_signal_check.setVisible(bool(data.get("raw_channels")))
        self._selected_channel = channel_keys[0] if channel_keys else ""
        self.results_area.metric_strip.clear()
        self._update_time_plot()
        self._update_spectrum_plot()
        self.results_area.spectrogram_plot.clear_series()
        self.results_area.update_analysis_status("DONNÉES CHARGÉES", self.analysis_count)
        self.inspector.analysis_status_label.setText("SOURCE PRÊTE")
        self.results_area.time_plot.set_title_metadata(
            f"{rate:g} Hz · {sample_count:,} points".replace(",", " ")
        )
        self.results_area.spectrum_plot.set_title_metadata("Welch · en attente de calcul")
        self.results_area.spectrogram_plot.set_title_metadata("Calculé à la demande · voie active")
        return True

    def on_analysis_requested(self, analysis_type: str, params: dict) -> None:
        if self.post_processor.current_data is None:
            QMessageBox.warning(self, "Analyse", "Aucun fichier de données n’est chargé.")
            return
        self.analysis_count += 1
        self.results_area.update_analysis_status("CALCUL EN COURS", self.analysis_count)
        self.inspector.analysis_status_label.setText("CALCUL…")
        self.post_processor.config["analysis"].update(params)
        if not self.post_processor.run_analysis():
            self.analysis_count -= 1
            self.results_area.update_analysis_status("ÉCHEC", self.analysis_count)
            self.inspector.analysis_status_label.setText("ÉCHEC")
            QMessageBox.warning(self, "Analyse", "Le post-traitement a échoué.")
            return
        self.current_analysis_result = self.post_processor.current_analysis
        self._attach_time_series_previews()
        self._update_results_views()
        self._update_time_plot()
        self.results_area.set_plot_mode("spectrum")
        self._set_tools_panel_expanded(False)
        quality = self.current_analysis_result.get("quality", {})
        warning_count = sum(len(item.get("warnings", [])) for item in quality.values())
        warning_count += len(self.current_analysis_result.get("metadata", {}).get("warnings", []))
        state = "SANS ALERTE" if warning_count == 0 else f"{warning_count} ALERTES À EXAMINER"
        self.results_area.update_analysis_status("ANALYSE TERMINÉE", self.analysis_count)
        self.inspector.analysis_status_label.setText(state)
        self.analysis_completed.emit(
            analysis_type,
            {
                "source_file": self.current_data_file,
                "results": self.current_analysis_result,
                "project_metadata": self.current_project_metadata,
                "analysis_params": params,
            },
        )

    def on_filter_applied(self, filter_type: str, params: dict) -> None:
        self.filter_applied.emit(filter_type, params)

    def on_export_requested(self, export_type: str) -> None:
        if self.current_analysis_result is None:
            QMessageBox.warning(self, "Export", "Aucun résultat d’analyse à exporter.")
            return
        suffix = {"csv": "csv", "json": "json", "hdf5": "h5", "txt": "txt"}.get(export_type, export_type)
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            f"Exporter {export_type.upper()}",
            str(self._get_default_export_directory() / f"analysis_results.{suffix}"),
            {
                "csv": "Fichiers CSV (*.csv)",
                "json": "Fichiers JSON (*.json)",
                "hdf5": "Fichiers HDF5 (*.h5 *.hdf5)",
                "txt": "Fichiers texte (*.txt)",
            }.get(export_type, "Tous les fichiers (*)"),
        )
        if not file_path:
            return
        if export_type == "txt":
            Path(file_path).write_text(self.results_area.report_text.toPlainText(), encoding="utf-8")
            self.data_exported.emit(file_path)
            return
        if self.post_processor.export_results(file_path, export_type):
            self.data_exported.emit(file_path)
        else:
            QMessageBox.warning(self, "Export", "L’export des résultats a échoué.")

    def set_theme(self, is_dark: bool) -> None:
        self.is_dark_mode = is_dark
        theme = "dark" if is_dark else "light"
        self.results_area.time_plot.apply_theme(theme)
        self.results_area.spectrum_plot.apply_theme(theme)
        self.results_area.spectrogram_plot.apply_theme(theme)

    def get_analysis_results(self) -> dict:
        return {
            "analysis_count": self.analysis_count,
            "current_data_file": self.current_data_file,
            "project_dir": str(self.current_project_dir) if self.current_project_dir else None,
            "analysis_results": self.current_analysis_result,
        }

    def clear_results(self) -> None:
        self.analysis_count = 0
        self.current_analysis_result = None
        self.results_area.time_plot.clear_series()
        self.results_area.spectrum_plot.clear_series()
        self.results_area.spectrogram_plot.clear_series()
        self.results_area.metric_strip.clear()
        self.results_area.report_text.clear()
        for table in (
            self.results_area.stats_table,
            self.results_area.spectral_table,
            self.results_area.quality_table,
        ):
            table.clearContents()
            table.setRowCount(0)
        self.results_area.update_analysis_status("AUCUNE DONNÉE", 0)

    def _get_default_search_directory(self) -> Path:
        if self.current_project_dir:
            exports = self.current_project_dir / "exports"
            return exports if exports.exists() else self.current_project_dir
        return Path.cwd()

    def _get_default_export_directory(self) -> Path:
        if self.current_project_dir:
            directory = self.current_project_dir / "analysis"
            directory.mkdir(parents=True, exist_ok=True)
            return directory
        return Path.cwd()

    def _add_or_select_file_item(self, file_path: str, select: bool = True) -> None:
        target = str(Path(file_path))
        combo = self.source_pane.data_combo
        index = combo.findData(target)
        if index < 0:
            combo.addItem(Path(target).name, target)
            index = combo.count() - 1
        if select:
            combo.setCurrentIndex(index)

    def _select_channel(self, channel: str) -> None:
        self._selected_channel = channel
        self._update_time_plot()
        self._update_spectrum_plot()
        self._update_spectrogram_plot()
        self._update_metric_strip()

    def _on_plot_controls_changed(self, *_args) -> None:
        self._update_time_plot()
        self._update_spectrum_plot()

    def _channel_metadata(self, channel: str) -> dict:
        data = self.post_processor.current_data or {}
        return self.post_processor._channel_metadata_map(
            list(data.get("channel_keys", [])),
            data.get("channel_metadata", {}),
        ).get(channel, {})

    def _channel_unit(self, channel: str) -> str:
        metadata = self._channel_metadata(channel)
        return str(
            metadata.get("physical_unit") or metadata.get("physical_units") or metadata.get("unit") or "unité"
        )

    @staticmethod
    def _quality_label(indicators: dict) -> str:
        return {
            "nominal": "AUCUNE ALERTE",
            "valid": "AUCUNE ALERTE",
            "warning": "À EXAMINER",
            "critical": "ALERTE CRITIQUE",
            "rejected": "ALERTE CRITIQUE",
        }.get(
            str(indicators.get("diagnostic_level") or indicators.get("status", "")),
            "AUCUNE ALERTE" if not indicators.get("warnings") else "À EXAMINER",
        )

    @staticmethod
    def _decision_label(indicators: dict) -> str:
        return {
            "accepted": "ACCEPTÉ",
            "rejected": "REJETÉ",
            "pending": "NON ÉVALUÉ",
        }.get(str(indicators.get("engineer_decision", "pending")), "NON ÉVALUÉ")

    def _visible_channels(self, available: list[str]) -> list[str]:
        visible = self.source_pane.channel_model.visible_keys()
        return [key for key in visible if key in available]

    def _color_for_channel(self, channel: str) -> str:
        for row in range(self.source_pane.channel_model.rowCount()):
            item = self.source_pane.channel_model.channel(row)
            if item and item.key == channel:
                return item.color
        return CHANNEL_COLORS[0]

    def _display_name_for_channel(self, channel: str) -> str:
        for row in range(self.source_pane.channel_model.rowCount()):
            item = self.source_pane.channel_model.channel(row)
            if item and item.key == channel:
                return item.name
        return channel

    def _update_time_plot(self, *_args) -> None:
        data = self.post_processor.current_data or {}
        available = list(data.get("channel_keys", []))
        raw = self.source_pane.raw_signal_check.isChecked() and bool(data.get("raw_channels"))
        start = self.inspector.start_time_spin.value()
        selected_end = self.inspector.end_time_spin.value()
        end = selected_end if selected_end > start else None
        display_mode = str(self.results_area.time_display_combo.currentData())
        series = {}
        for channel in self._visible_channels(available):
            time_values, values = self.post_processor.load_channel_window(
                channel,
                start,
                end,
                raw=raw,
            )
            if display_mode == "analysis":
                values, _ = WaveAnalyzer(self.post_processor._wave_config()).prepare_signal(
                    values,
                    self.post_processor.sample_rate,
                )
            elif display_mode == "centered":
                values = values - float(np.mean(values))
            elif display_mode == "normalized":
                values = values - float(np.mean(values))
                scale = float(np.std(values))
                values = values / scale if scale > np.finfo(float).tiny else values
            series[self._display_name_for_channel(channel)] = (
                time_values,
                values,
                self._color_for_channel(channel),
            )
        self.results_area.time_plot.set_series(series)
        unit = (
            "V"
            if raw
            else "z = (x−μ)/σ [affichage]"
            if display_mode == "normalized"
            else self._channel_unit(self._selected_channel)
            if self._selected_channel
            else "Amplitude"
        )
        self.results_area.time_plot.set_axis_labels(y_label=unit)
        if series:
            first = next(iter(series.values()))[0]
            if len(first):
                left = float(first[0])
                right = float(first[-1])
                self.results_area.time_plot.set_x_range(left, right)
                self.results_area.time_plot.set_region(
                    left,
                    right,
                    visible=selected_end > start,
                )
                points = sum(len(values[0]) for values in series.values())
                mode_label = {
                    "physical": "amplitude physique",
                    "centered": "centré pour affichage",
                    "analysis": "signal conditionné pour analyse",
                    "normalized": "normalisé uniquement pour affichage",
                }.get(display_mode, display_mode)
                self.results_area.time_plot.set_title_metadata(
                    f"{right - left:.3f} s · {points:,} points tracés · {mode_label}".replace(
                        ",", " "
                    )
                )

    def _update_spectrum_plot(self, *_args) -> None:
        spectral = (self.current_analysis_result or {}).get("spectral_analysis", {})
        representation = str(self.results_area.spectrum_representation_combo.currentData())
        axes = self.results_area.spectrum_axes_combo.currentData() or (False, True)
        logarithmic_x, logarithmic_y = bool(axes[0]), bool(axes[1])
        if representation in {"db", "energy"}:
            logarithmic_y = False
        self.results_area.spectrum_plot.set_log_mode(logarithmic_x, logarithmic_y)
        band_only = self.results_area.spectrum_band_only_check.isChecked()
        series = {}
        for channel in self._visible_channels(list(spectral)):
            values = spectral[channel]
            frequencies = np.asarray(values.get("frequencies", []), dtype=float)
            density = np.asarray(values.get("psd", []), dtype=float)
            mask = np.isfinite(frequencies) & np.isfinite(density)
            if logarithmic_x:
                mask &= frequencies > 0
            if band_only and len(values.get("analysis_band_hz", [])) == 2:
                low, high = values["analysis_band_hz"]
                mask &= (frequencies >= float(low)) & (frequencies <= float(high))
            frequencies = frequencies[mask]
            density = density[mask]
            displayed = self._spectral_display_values(frequencies, density, representation)
            series[self._display_name_for_channel(channel)] = (
                frequencies,
                displayed,
                self._color_for_channel(channel),
            )
        self.results_area.spectrum_plot.set_series(series)
        unit = self._channel_unit(self._selected_channel) if self._selected_channel else "unité"
        y_label = {
            "psd": f"PSD ({unit}²/Hz)",
            "asd": f"ASD ({unit}/√Hz)",
            "db": f"PSD (dB re 1 {unit}²/Hz)",
            "energy": "Énergie cumulée (%)",
        }.get(representation, "PSD")
        self.results_area.spectrum_plot.set_axis_labels(
            x_label="Fréquence (Hz)",
            y_label=y_label,
        )
        selected = self._selected_channel
        if selected in spectral:
            values = spectral[selected]
            peak = float(values.get("peak_frequency", 0))
            peak_psd = float(values.get("peak_psd", 0))
            peak_display = self._spectral_display_values(
                np.asarray([peak]),
                np.asarray([peak_psd]),
                representation,
            )
            if representation != "energy" and len(peak_display):
                self.results_area.spectrum_plot.add_marker(peak, float(peak_display[0]))
            self._add_selected_psd_confidence_band(values, representation, logarithmic_x)
            resolution = float(values.get("frequency_resolution", 0))
            bin_spacing = float(values.get("frequency_bin_spacing", resolution))
            self.results_area.spectrum_readout_label.setText(
                f"pic {peak:.5g} Hz   Rayleigh {resolution:.5g} Hz   grille {bin_spacing:.5g} Hz"
            )
            self.results_area.spectrum_plot.set_title_metadata(
                f"Welch {values.get('average', 'mean')} · {values.get('window', 'hann')} · "
                f"{values.get('segment_count', 0)} segments · NFFT {values.get('fft_length', 0)}"
            )

    @staticmethod
    def _spectral_display_values(
        frequencies: np.ndarray,
        density: np.ndarray,
        representation: str,
    ) -> np.ndarray:
        density = np.maximum(np.asarray(density, dtype=float), np.finfo(float).tiny)
        if representation == "asd":
            return np.sqrt(density)
        if representation == "db":
            return 10.0 * np.log10(density)
        if representation == "energy":
            if len(density) < 2:
                return np.zeros_like(density)
            increments = 0.5 * (density[:-1] + density[1:]) * np.diff(frequencies)
            cumulative = np.concatenate(([0.0], np.cumsum(increments)))
            return 100.0 * cumulative / cumulative[-1] if cumulative[-1] > 0 else cumulative
        return density

    def _add_selected_psd_confidence_band(
        self,
        spectrum: dict,
        representation: str,
        logarithmic_x: bool,
    ) -> None:
        if (
            not self.results_area.spectrum_confidence_check.isChecked()
            or representation == "energy"
            or spectrum.get("average", "mean") != "mean"
        ):
            return
        factors = spectrum.get("psd_confidence_interval_95_factors_approx")
        if not isinstance(factors, list) or len(factors) != 2:
            return
        frequencies = np.asarray(spectrum.get("frequencies", []), dtype=float)
        density = np.asarray(spectrum.get("psd", []), dtype=float)
        mask = np.isfinite(frequencies) & np.isfinite(density)
        if logarithmic_x:
            mask &= frequencies > 0
        if self.results_area.spectrum_band_only_check.isChecked():
            low, high = spectrum.get("analysis_band_hz", (0.0, np.inf))
            mask &= (frequencies >= float(low)) & (frequencies <= float(high))
        frequencies = frequencies[mask]
        density = density[mask]
        lower = self._spectral_display_values(
            frequencies,
            density * float(factors[0]),
            representation,
        )
        upper = self._spectral_display_values(
            frequencies,
            density * float(factors[1]),
            representation,
        )
        self.results_area.spectrum_plot.add_confidence_band(
            frequencies,
            lower,
            upper,
            self._color_for_channel(self._selected_channel),
        )

    def _update_spectrogram_plot(self, *_args) -> None:
        if self.current_analysis_result is None or not self._selected_channel:
            self.results_area.spectrogram_plot.clear_series()
            return
        try:
            spectrogram = self.post_processor.compute_spectrogram(self._selected_channel)
        except Exception as exc:
            self.results_area.spectrogram_plot.clear_series()
            self.results_area.spectrogram_plot.set_title_metadata(str(exc))
            return
        times = np.asarray(spectrogram.get("times", []), dtype=float)
        frequencies = np.asarray(spectrogram.get("frequencies", []), dtype=float)
        density = np.asarray(spectrogram.get("psd", []), dtype=float)
        dynamic_range = float(self.results_area.spectrogram_range_combo.currentData())
        palette = str(self.results_area.spectrogram_palette_combo.currentData())
        self.results_area.spectrogram_plot.set_spectrogram(
            times,
            frequencies,
            density,
            dynamic_range_db=dynamic_range,
            color_map=palette,
            color_label=f"PSD dB · {spectrogram.get('psd_units', '')}",
        )
        name = self._display_name_for_channel(self._selected_channel)
        self.results_area.spectrogram_channel_label.setText(f"VOIE ACTIVE {name}")
        self.results_area.spectrogram_readout_label.setText(
            f"{name}   dynamique {dynamic_range:g} dB"
        )
        self.results_area.spectrogram_plot.set_title_metadata(
            f"{name} · {spectrogram.get('segment_count', 0)} fenêtres · "
            f"Rayleigh {float(spectrogram.get('frequency_resolution', 0)):.5g} Hz"
        )

    def _update_results_views(self) -> None:
        results = self.current_analysis_result or {}
        basic = results.get("basic_stats", {})
        spectral = results.get("spectral_analysis", {})
        waves = results.get("wave_parameters", {})
        quality = results.get("quality", {})
        channels = list(basic)
        self._fill_table(
            self.results_area.stats_table,
            [
                "Voie",
                "Unité",
                "N échantillons",
                "Moyenne",
                "σ (écart-type)",
                "RMS (efficace)",
                "Min",
                "Max",
            ],
            [
                [
                    ch,
                    self._channel_unit(ch),
                    basic[ch].get("sample_count", ""),
                    basic[ch].get("mean", ""),
                    basic[ch].get("std", ""),
                    basic[ch].get("rms", ""),
                    basic[ch].get("min", ""),
                    basic[ch].get("max", ""),
                ]
                for ch in channels
            ],
        )
        rows = []
        for channel in channels:
            spectrum = spectral.get(channel, {})
            wave = waves.get(channel, {})
            status = quality.get(channel, {})
            rows.append(
                [
                    channel,
                    self._quality_label(status),
                    self._decision_label(status),
                    spectrum.get("Hm0", 0),
                    wave.get("H1_3", 0),
                    spectrum.get("peak_frequency", 0),
                    spectrum.get("peak_period", 0) if status.get("peak_period_reliable") else "À CONFIRMER",
                    spectrum.get("Tm01", 0),
                    spectrum.get("Tm02", 0),
                    spectrum.get("frequency_resolution", 0),
                    spectrum.get("segment_count", 0),
                ]
            )
        self._fill_table(
            self.results_area.spectral_table,
            [
                "Voie",
                "Diagnostic auto",
                "Décision ingénieur",
                "Hm0",
                "H1/3",
                "fpic",
                "Tp",
                "Tm01",
                "Tm02",
                "Δf",
                "Segments",
            ],
            rows,
        )
        self._fill_quality_table(channels, quality)
        self.results_area.quality_table.resizeRowsToContents()
        for channel, indicators in quality.items():
            self.source_pane.channel_model.set_quality(channel, str(indicators.get("status", "unknown")))
        self.results_area.report_text.setPlainText(self._build_report_text())
        self._update_spectrum_plot()
        self._update_metric_strip()

    def _fill_quality_table(self, channels: list[str], quality: dict) -> None:
        """Render diagnostics separately from the engineer's explicit decision."""

        table = self.results_area.quality_table
        headers = [
            "Voie",
            "Diagnostic automatique",
            "Décision ingénieur",
            "Alertes et observations",
            "Var. PSD/temps",
            "Stationnarité",
            "Cycles/pic",
            "Éch./période",
        ]
        table.clearContents()
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        definitions = {
            "N échantillons": "Nombre de valeurs analysées par voie : N = fréquence × durée.",
            "σ (écart-type)": "Dispersion des échantillons autour de leur moyenne.",
            "RMS (efficace)": "Valeur efficace : racine de la moyenne des carrés du signal.",
        }
        for column, header in enumerate(headers):
            item = table.horizontalHeaderItem(column)
            if item and header in definitions:
                item.setToolTip(definitions[header])
        table.setRowCount(len(channels))
        for row, channel in enumerate(channels):
            indicators = quality.get(channel, {})
            values = [
                channel,
                self._quality_label(indicators),
                None,
                "\n".join(map(str, indicators.get("warnings", [])))
                or "Aucune alerte automatique",
                indicators.get("spectral_to_time_variance_ratio", 0),
                indicators.get("block_variance_ratio", 0),
                indicators.get("record_cycles_at_peak", 0),
                indicators.get("samples_per_peak_period", 0),
            ]
            for column, value in enumerate(values):
                if column == 2:
                    continue
                text = f"{value:.6g}" if isinstance(value, float) else str(value)
                table.setItem(row, column, QTableWidgetItem(text))
            decision_combo = QComboBox()
            decision_combo.setObjectName("engineerDecision")
            decision_combo.addItem("Non évalué", "pending")
            decision_combo.addItem("Accepté", "accepted")
            decision_combo.addItem("Rejeté", "rejected")
            current = str(indicators.get("engineer_decision", "pending"))
            index = decision_combo.findData(current)
            decision_combo.setCurrentIndex(max(0, index))
            decision_combo.currentIndexChanged.connect(
                lambda _index, key=channel, widget=decision_combo: self._set_engineer_decision(
                    key, str(widget.currentData())
                )
            )
            table.setCellWidget(row, 2, decision_combo)
        table.resizeRowsToContents()

    def _set_engineer_decision(self, channel: str, decision: str) -> None:
        if self.current_analysis_result is None:
            return
        indicators = self.current_analysis_result.setdefault("quality", {}).setdefault(channel, {})
        indicators["engineer_decision"] = decision
        self.results_area.report_text.setPlainText(self._build_report_text())
        self._update_metric_strip()

    def _attach_time_series_previews(self) -> None:
        """Persist bounded, physical-unit traces needed by the scientific report."""

        if self.current_analysis_result is None:
            return
        data = self.post_processor.current_data or {}
        previews = {}
        metadata = self.current_analysis_result.get("metadata", {})
        start_time = float(metadata.get("analysis_start_s", 0.0))
        end_time = metadata.get("analysis_end_s")
        for channel in data.get("channel_keys", []):
            time_values, values = self.post_processor.load_channel_window(
                channel,
                start_time,
                float(end_time) if end_time is not None else None,
                maximum_points=2500,
            )
            previews[channel] = {
                "time_s": time_values.tolist(),
                "values": values.tolist(),
                "unit": self._channel_unit(channel),
            }
        self.current_analysis_result["time_series_preview"] = previews

    @staticmethod
    def _fill_table(table: QTableWidget, headers: list[str], rows: list[list[object]]) -> None:
        table.clearContents()
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setRowCount(len(rows))
        for row_index, values in enumerate(rows):
            for column, value in enumerate(values):
                text = f"{value:.6g}" if isinstance(value, float) else str(value)
                table.setItem(row_index, column, QTableWidgetItem(text))

    def _update_metric_strip(self) -> None:
        channel = self._selected_channel
        results = self.current_analysis_result or {}
        basic = results.get("basic_stats", {}).get(channel, {})
        spectrum = results.get("spectral_analysis", {}).get(channel, {})
        status = results.get("quality", {}).get(channel, {})
        if not spectrum:
            self.results_area.metric_strip.clear()
            return
        reliable = bool(status.get("peak_period_reliable"))
        state = {
            "nominal": "success",
            "valid": "success",
            "warning": "warning",
            "critical": "danger",
            "rejected": "danger",
        }.get(
            str(status.get("diagnostic_level") or status.get("status")), "neutral"
        )
        strip = self.results_area.metric_strip
        physical_unit = self._channel_unit(channel)
        strip.set_metric("hm0", f"{float(spectrum.get('Hm0', 0)):.5g}", channel, unit=physical_unit)
        strip.set_metric(
            "tp",
            f"{float(spectrum.get('peak_period', 0)):.5g}" if reliable else "—",
            "pic spectral" if reliable else "non fiable",
            state,
        )
        strip.set_metric("tm01", f"{float(spectrum.get('Tm01', 0)):.5g}", "moment m0/m1")
        strip.set_metric("rms", f"{float(basic.get('rms', 0)):.5g}", channel, unit=physical_unit)
        strip.set_metric(
            "df",
            f"{float(spectrum.get('frequency_resolution', 0)):.5g}",
            f"{spectrum.get('segment_count', 0)} segments",
        )
        strip.set_metric(
            "quality",
            self._quality_label(status),
            f"{len(status.get('warnings', []))} alerte(s)",
            state,
        )
        decision = self._decision_label(status)
        decision_state = (
            "success" if decision == "ACCEPTÉ" else "danger" if decision == "REJETÉ" else "neutral"
        )
        strip.set_metric("verdict", decision, "décision ingénieur", decision_state)

    def _sync_controls_from_region(self, start: float, end: float) -> None:
        self._setting_region = True
        self.inspector.start_time_spin.setValue(start)
        self.inspector.end_time_spin.setValue(end)
        self._setting_region = False
        self.inspector.set_interval_custom()
        custom = self.results_area.time_window_combo.findData(-1.0)
        if custom >= 0:
            self.results_area.time_window_combo.setCurrentIndex(custom)
        self._update_time_plot()

    def _sync_region_from_controls(self, *_args) -> None:
        if self._setting_region:
            return
        start = self.inspector.start_time_spin.value()
        end = self.inspector.end_time_spin.value()
        if end > start:
            self.results_area.time_plot.set_region(start, end, visible=True)
        self._update_time_plot()

    def _update_resolution_preview(self, *_args) -> None:
        rate = self.post_processor.sample_rate or 0.0
        segment = int(self.inspector.segment_length_combo.currentText())
        padding = int(self.inspector.zero_padding_combo.currentData())
        self.inspector.resolution_value.setText(
            f"Rayleigh {rate / segment:.5g} Hz · grille {rate / (segment * padding):.5g} Hz"
            if rate
            else "—"
        )

    def _on_time_cursor_moved(self, time_s: float, value: float) -> None:
        text = f"t {time_s:.4g} s   y {value:.5g}"
        self.results_area.time_cursor_label.setText(text)
        self.inspector.cursor_value.setText(text)

    def _on_spectrum_cursor_moved(self, frequency: float, density: float) -> None:
        self.results_area.spectrum_readout_label.setText(f"f {frequency:.5g} Hz   PSD {density:.4g}")

    def _build_report_text(self) -> str:
        return build_scientific_report_text(
            self.current_analysis_result or {},
            self.current_data_file,
            self.current_project_metadata,
            {"title": "Rapport scientifique CHNeoWave"},
        )
