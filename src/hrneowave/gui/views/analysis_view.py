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
        layout.setContentsMargins(10, 7, 10, 7)
        layout.setSpacing(6)

        source_row = QHBoxLayout()
        source_row.setSpacing(6)
        source_label = QLabel("SOURCE")
        source_label.setObjectName("commandCaption")
        source_row.addWidget(source_label)
        self.data_combo = QComboBox()
        self.data_combo.setObjectName("sourceCombo")
        self.data_combo.setMinimumWidth(240)
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
        self.source_meta = QLabel("— Hz  ·  — échantillons  ·  — s")
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
        channel_row.setSpacing(6)
        label = QLabel("VOIES")
        label.setObjectName("commandCaption")
        channel_row.addWidget(label)
        self.channel_count = QLabel("0 / 0 visibles")
        self.channel_count.setObjectName("channelVisibleCount")
        channel_row.addWidget(self.channel_count)
        self.show_all_button = QPushButton("Tout afficher")
        self.hide_all_button = QPushButton("Tout masquer")
        self.isolate_button = QPushButton("Isoler la voie active")
        for button in (self.show_all_button, self.hide_all_button, self.isolate_button):
            button.setObjectName("channelCommand")
            channel_row.addWidget(button)
        channel_row.addStretch()
        hint = QLabel("Cochez plusieurs voies pour comparer les courbes")
        hint.setObjectName("commandHint")
        channel_row.addWidget(hint)
        layout.addLayout(channel_row)

        self.channel_list = QListView()
        self.channel_list.setObjectName("channelRibbon")
        self.channel_list.setModel(self.channel_model)
        self.channel_list.setItemDelegate(ChannelDelegate(self.channel_list))
        self.channel_list.setSelectionMode(QListView.SelectionMode.SingleSelection)
        self.channel_list.setFlow(QListView.Flow.LeftToRight)
        self.channel_list.setWrapping(False)
        self.channel_list.setHorizontalScrollMode(QListView.ScrollMode.ScrollPerPixel)
        self.channel_list.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.channel_list.setFixedHeight(48)
        layout.addWidget(self.channel_list)

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
            f"{rate:g} Hz  ·  {samples:,} échantillons  ·  {duration:.3f} s".replace(",", " ")
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
        self.start_time_spin = self._time_spin(False)
        self.end_time_spin = self._time_spin(True)
        self.duration_value = self._technical("—")
        self.samples_value = self._technical("—")
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
        self.detrend_check = QCheckBox("Moyenne + dérive")
        self.detrend_check.setChecked(True)
        self.resolution_value = self._technical("—")
        form.addRow("Fenêtre", self.window_combo)
        form.addRow("Segment", self.segment_length_combo)
        form.addRow("Recouvrement", self.overlap_spin)
        form.addRow("Débruitage", self.detrend_check)
        form.addRow("Δf", self.resolution_value)
        panel.addWidget(welch)
        band, form = self._section("Bande utile")
        self.min_frequency_spin = self._frequency_spin(False)
        self.max_frequency_spin = self._frequency_spin(True)
        form.addRow("f min", self.min_frequency_spin)
        form.addRow("f max", self.max_frequency_spin)
        panel.addWidget(band)
        reading, form = self._section("Lecture")
        self.confidence_interval_check = QCheckBox("IC PSD 95 %")
        self.confidence_interval_check.setChecked(True)
        self.cumulative_energy_check = QCheckBox("Énergie cumulée")
        self.cursor_value = self._technical("t —   y —")
        form.addRow("Incertitude", self.confidence_interval_check)
        form.addRow("Intégrale", self.cumulative_energy_check)
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
        return {
            "window_size": int(self.segment_length_combo.currentText()),
            "overlap": self.overlap_spin.value() / 100.0,
            "min_frequency": self.min_frequency_spin.value(),
            "max_frequency": maximum if maximum > 0 else None,
            "detrend": self.detrend_check.isChecked(),
            "window": str(self.window_combo.currentData()),
            "start_time_s": self.start_time_spin.value(),
            "end_time_s": self.end_time_spin.value() or None,
        }

    def set_record(self, duration: float, samples: int, rate: float) -> None:
        duration = max(0.0, float(duration))
        self.start_time_spin.setMaximum(duration)
        self.end_time_spin.setMaximum(duration)
        self.end_time_spin.setValue(0.0)
        self.duration_value.setText(f"{duration:.3f} s")
        self.samples_value.setText(f"N = {samples:,}".replace(",", " "))
        segment = int(self.segment_length_combo.currentText())
        self.resolution_value.setText(f"{rate / segment:.5g} Hz" if rate else "—")

    def set_record_duration(self, duration_s: float) -> None:
        self.set_record(duration_s, 0, 0.0)


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
    """Two simultaneous plots, readouts and an optional evidence drawer."""

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
        self.time_cursor_label = QLabel("t —   y —")
        self.time_cursor_label.setObjectName("plotMeta")
        self.spectrum_readout_label = QLabel("pic —   Δf —")
        self.spectrum_readout_label.setObjectName("plotMeta")
        row.addWidget(self.analysis_status_label)
        row.addWidget(self.analysis_count_label)
        row.addStretch()
        row.addWidget(self.time_cursor_label)
        row.addSpacing(12)
        row.addWidget(self.spectrum_readout_label)
        layout.addWidget(status)
        self.plot_splitter = QSplitter(Qt.Orientation.Vertical)
        self.time_plot = ScientificPlotWidget("Signal temporel", "Temps (s)", "Amplitude")
        self.spectrum_plot = ScientificPlotWidget(
            "Densité spectrale de puissance",
            "Fréquence (Hz)",
            "PSD",
            logarithmic_y=True,
        )
        self.plot_splitter.addWidget(self.time_plot)
        self.plot_splitter.addWidget(self.spectrum_plot)
        self.plot_splitter.setSizes([390, 280])
        layout.addWidget(self.plot_splitter, 1)
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
        self.source_pane.center_signal_check.toggled.connect(self._update_time_plot)
        self.source_pane.overlay_channels_check.toggled.connect(self._on_plot_controls_changed)
        self.inspector.analysis_requested.connect(self.on_analysis_requested)
        self.inspector.export_requested.connect(self.on_export_requested)
        self.inspector.details_requested.connect(self._toggle_tools_panel)
        self.inspector.segment_length_combo.currentTextChanged.connect(self._update_resolution_preview)
        self.inspector.start_time_spin.valueChanged.connect(self._sync_region_from_controls)
        self.inspector.end_time_spin.valueChanged.connect(self._sync_region_from_controls)
        self.results_area.time_plot.region_changed.connect(self._sync_controls_from_region)
        self.results_area.time_plot.cursor_moved.connect(self._on_time_cursor_moved)
        self.results_area.spectrum_plot.cursor_moved.connect(self._on_spectrum_cursor_moved)

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
                    name=f"{key}  {metadata.get('name', '')}".strip(),
                    sensor=sensor_names.get(sensor, sensor.replace("_", " ").title()),
                    unit=self._channel_unit(key),
                    color=CHANNEL_COLORS[index % len(CHANNEL_COLORS)],
                    visible=True,
                )
            )
        self.source_pane.set_channels(channels)
        self.source_pane.raw_signal_check.setVisible(bool(data.get("raw_channels")))
        self._selected_channel = channel_keys[0] if channel_keys else ""
        self.results_area.metric_strip.clear()
        self._update_time_plot()
        self._update_spectrum_plot()
        self.results_area.update_analysis_status("DONNÉES CHARGÉES", self.analysis_count)
        self.inspector.analysis_status_label.setText("SOURCE PRÊTE")
        self.results_area.time_plot.set_title_metadata(
            f"{rate:g} Hz · {sample_count:,} points".replace(",", " ")
        )
        self.results_area.spectrum_plot.set_title_metadata("Welch · en attente de calcul")
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

    def _update_time_plot(self, *_args) -> None:
        data = self.post_processor.current_data or {}
        available = list(data.get("channel_keys", []))
        raw = self.source_pane.raw_signal_check.isChecked() and bool(data.get("raw_channels"))
        series = {}
        for channel in self._visible_channels(available):
            time_values, values = self.post_processor.load_channel_preview(channel, raw=raw)
            if self.source_pane.center_signal_check.isChecked():
                values = values - float(np.mean(values))
            series[channel] = (time_values, values, self._color_for_channel(channel))
        self.results_area.time_plot.set_series(series)
        unit = (
            "V"
            if raw
            else self._channel_unit(self._selected_channel)
            if self._selected_channel
            else "Amplitude"
        )
        self.results_area.time_plot.set_axis_labels(y_label=unit)
        if series and not self.results_area.time_plot.region.isVisible():
            first = next(iter(series.values()))[0]
            if len(first):
                self.results_area.time_plot.set_region(float(first[0]), float(first[-1]), visible=False)

    def _update_spectrum_plot(self, *_args) -> None:
        spectral = (self.current_analysis_result or {}).get("spectral_analysis", {})
        series = {}
        for channel in self._visible_channels(list(spectral)):
            values = spectral[channel]
            series[channel] = (
                np.asarray(values.get("frequencies", []), dtype=float),
                np.asarray(values.get("psd", []), dtype=float),
                self._color_for_channel(channel),
            )
        self.results_area.spectrum_plot.set_series(series)
        selected = self._selected_channel
        if selected in spectral:
            values = spectral[selected]
            peak = float(values.get("peak_frequency", 0))
            peak_psd = float(values.get("peak_psd", 0))
            self.results_area.spectrum_plot.add_marker(peak, peak_psd)
            resolution = float(values.get("frequency_resolution", 0))
            self.results_area.spectrum_readout_label.setText(f"pic {peak:.5g} Hz   Δf {resolution:.5g} Hz")
            self.results_area.spectrum_plot.set_title_metadata(
                f"Welch · {values.get('segment_count', 0)} segments · Δf {resolution:.5g} Hz"
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
        for channel in data.get("channel_keys", []):
            time_values, values = self.post_processor.load_channel_preview(channel, maximum_points=2500)
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

    def _sync_region_from_controls(self, *_args) -> None:
        if self._setting_region:
            return
        start = self.inspector.start_time_spin.value()
        end = self.inspector.end_time_spin.value()
        if end > start:
            self.results_area.time_plot.set_region(start, end, visible=True)

    def _update_resolution_preview(self, *_args) -> None:
        rate = self.post_processor.sample_rate or 0.0
        segment = int(self.inspector.segment_length_combo.currentText())
        self.inspector.resolution_value.setText(f"{rate / segment:.5g} Hz" if rate else "—")

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
