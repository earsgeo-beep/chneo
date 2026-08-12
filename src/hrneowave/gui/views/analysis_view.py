"""Vue d'analyse CHNeoWave."""

from pathlib import Path

import numpy as np
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
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


class LegacyRawImportDialog(QDialog):
    """Confirme les seules hypotheses que le fichier RAW ne peut pas porter."""

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
        self.setWindowTitle("Interprétation du fichier RAW")
        self.setModal(True)
        self.setMinimumWidth(500)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(10)
        identity = QLabel(
            f"{source_path.name}\n"
            f"{header.sample_rate_hz:g} Hz · {header.declared_duration_s:g} s · "
            f"{header.channel_count} canaux"
        )
        identity.setObjectName("sectionTitle")
        layout.addWidget(identity)

        explanation = QLabel(
            "Le format contient un facteur par canal mais pas son unité. "
            "Pour une conversion traçable, confirmez la relation X = V × facteur "
            "et l'unité physique de X."
        )
        explanation.setWordWrap(True)
        explanation.setObjectName("mutedText")
        layout.addWidget(explanation)

        form = QFormLayout()
        self.sensor_type_combo = QComboBox()
        for label, sensor_type, _unit in self.SENSOR_TYPES:
            self.sensor_type_combo.addItem(label, sensor_type)
        self.physical_unit_combo = QComboBox()
        self.physical_unit_combo.setEditable(True)
        self.physical_unit_combo.addItems(["cm", "m", "mm", "N", "g", "kg", "m/s²", "bar", "°"])
        self.apply_calibration_check = QCheckBox("Appliquer les coefficients de l'en-tête")
        self.apply_calibration_check.setChecked(True)
        self.confirm_calibration_check = QCheckBox(
            "Je confirme le type, l'unité, les facteurs en unité/V et le zéro appliqué"
        )
        form.addRow("TYPE DE SIGNAL", self.sensor_type_combo)
        form.addRow("UNITÉ PHYSIQUE", self.physical_unit_combo)
        form.addRow("CONVERSION", self.apply_calibration_check)
        form.addRow("CONFIRMATION", self.confirm_calibration_check)
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
        enabled = not calibrated or (
            self.confirm_calibration_check.isChecked()
            and bool(self.physical_unit_combo.currentText().strip())
        )
        self.buttons.button(QDialogButtonBox.StandardButton.Ok).setEnabled(enabled)

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


class AnalysisToolsPanel(QFrame):
    """Panneau d'outils pour le chargement et l'analyse."""

    analysis_requested = Signal(str, dict)
    filter_applied = Signal(str, dict)
    export_requested = Signal(str)
    parameters_toggle_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self) -> None:
        self.setObjectName("analysis_tools_panel")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(7)

        source_row = QHBoxLayout()
        source_row.setSpacing(8)
        source_label = QLabel("FICHIER DE DONNÉES")
        source_label.setObjectName("metricLabel")
        self.data_combo = QComboBox()
        self.data_combo.addItem("Aucun fichier sélectionné", None)
        self.data_combo.setMinimumContentsLength(32)
        self.load_button = QPushButton("Ouvrir un fichier")
        self.refresh_button = QPushButton("Actualiser")
        self.load_button.setProperty("kind", "secondary")
        self.refresh_button.setProperty("kind", "secondary")
        self.parameters_toggle_button = QPushButton("Réduire les réglages")
        self.parameters_toggle_button.setProperty("kind", "quiet")
        self.run_button = QPushButton("Lancer l'analyse")
        self.run_button.setProperty("kind", "primaryLarge")
        self.run_button.clicked.connect(self._emit_analysis_request)
        self.parameters_toggle_button.clicked.connect(self.parameters_toggle_requested.emit)
        source_row.addWidget(source_label)
        source_row.addWidget(self.data_combo, 1)
        source_row.addWidget(self.load_button)
        source_row.addWidget(self.refresh_button)
        source_row.addWidget(self.parameters_toggle_button)
        layout.addLayout(source_row)

        self.parameters_panel = QFrame()
        self.parameters_panel.setObjectName("flatPanel")
        parameters_layout = QVBoxLayout(self.parameters_panel)
        parameters_layout.setContentsMargins(0, 7, 0, 0)
        parameters_layout.setSpacing(7)

        method_layout = QGridLayout()
        method_layout.setHorizontalSpacing(10)
        method_layout.setVerticalSpacing(4)
        self.segment_length_combo = QComboBox()
        self.segment_length_combo.addItems(["256", "512", "1024", "2048", "4096", "8192"])
        self.segment_length_combo.setCurrentText("1024")
        self.segment_length_combo.setMinimumWidth(110)
        self.overlap_spin = QSpinBox()
        self.overlap_spin.setRange(0, 90)
        self.overlap_spin.setValue(50)
        self.overlap_spin.setSuffix(" %")
        self.overlap_spin.setMinimumWidth(110)
        self.min_frequency_spin = QDoubleSpinBox()
        self.min_frequency_spin.setRange(0.0, 10000.0)
        self.min_frequency_spin.setDecimals(4)
        self.min_frequency_spin.setSuffix(" Hz")
        self.min_frequency_spin.setMinimumWidth(120)
        self.max_frequency_spin = QDoubleSpinBox()
        self.max_frequency_spin.setRange(0.0, 10000.0)
        self.max_frequency_spin.setDecimals(4)
        self.max_frequency_spin.setSpecialValueText("Nyquist")
        self.max_frequency_spin.setSuffix(" Hz")
        self.max_frequency_spin.setMinimumWidth(120)
        self.window_combo = QComboBox()
        for label, value in (
            ("Hann (recommandée)", "hann"),
            ("Hamming", "hamming"),
            ("Blackman", "blackman"),
            ("Rectangulaire", "boxcar"),
        ):
            self.window_combo.addItem(label, value)
        self.start_time_spin = QDoubleSpinBox()
        self.start_time_spin.setRange(0.0, 10_000_000.0)
        self.start_time_spin.setDecimals(3)
        self.start_time_spin.setSuffix(" s")
        self.end_time_spin = QDoubleSpinBox()
        self.end_time_spin.setRange(0.0, 10_000_000.0)
        self.end_time_spin.setDecimals(3)
        self.end_time_spin.setSpecialValueText("Fin")
        self.end_time_spin.setSuffix(" s")
        self.detrend_check = QCheckBox("Retirer moyenne et dérive linéaire")
        self.detrend_check.setChecked(True)
        fields = (
            ("SEGMENT WELCH", self.segment_length_combo),
            ("RECOUVREMENT", self.overlap_spin),
            ("FRÉQUENCE MIN.", self.min_frequency_spin),
            ("FRÉQUENCE MAX.", self.max_frequency_spin),
        )
        for column, (label, widget) in enumerate(fields):
            label_widget = QLabel(label)
            label_widget.setObjectName("metricLabel")
            method_layout.addWidget(label_widget, 0, column)
            method_layout.addWidget(widget, 1, column)
        method_layout.addWidget(self.detrend_check, 1, len(fields))
        method_layout.setColumnStretch(len(fields), 1)
        secondary_fields = (
            ("FENÊTRE", self.window_combo),
            ("DÉBUT INTERVALLE", self.start_time_spin),
            ("FIN INTERVALLE", self.end_time_spin),
        )
        for column, (label, widget) in enumerate(secondary_fields):
            label_widget = QLabel(label)
            label_widget.setObjectName("metricLabel")
            method_layout.addWidget(label_widget, 2, column)
            method_layout.addWidget(widget, 3, column)
        parameters_layout.addLayout(method_layout)

        actions_row = QHBoxLayout()
        actions_row.setSpacing(6)
        export_label = QLabel("EXPORTER LES RÉSULTATS")
        export_label.setObjectName("metricLabel")
        self.export_format_combo = QComboBox()
        for label, export_type in (
            ("CSV", "csv"),
            ("JSON", "json"),
            ("HDF5", "hdf5"),
            ("Texte", "txt"),
        ):
            self.export_format_combo.addItem(label, export_type)
        self.export_button = QPushButton("Exporter")
        self.export_button.setProperty("kind", "secondary")
        self.export_button.clicked.connect(
            lambda: self.export_requested.emit(str(self.export_format_combo.currentData()))
        )
        actions_row.addWidget(export_label)
        actions_row.addWidget(self.export_format_combo)
        actions_row.addWidget(self.export_button)
        actions_row.addStretch()
        actions_row.addWidget(self.run_button)
        parameters_layout.addLayout(actions_row)
        layout.addWidget(self.parameters_panel)

    def _emit_analysis_request(self) -> None:
        max_frequency = self.max_frequency_spin.value()
        self.analysis_requested.emit(
            "complete",
            {
                "window_size": int(self.segment_length_combo.currentText()),
                "overlap": self.overlap_spin.value() / 100.0,
                "min_frequency": self.min_frequency_spin.value(),
                "max_frequency": max_frequency if max_frequency > 0 else None,
                "detrend": self.detrend_check.isChecked(),
                "window": str(self.window_combo.currentData()),
                "start_time_s": self.start_time_spin.value(),
                "end_time_s": self.end_time_spin.value() or None,
            },
        )

    def set_record_duration(self, duration_s: float) -> None:
        duration = max(0.0, float(duration_s))
        self.start_time_spin.setMaximum(duration)
        self.end_time_spin.setMaximum(duration)
        self.end_time_spin.setValue(0.0)


class AnalysisResultsArea(QFrame):
    """Zone d'affichage des resultats."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self) -> None:
        self.setObjectName("analysis_results_area")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 10)
        layout.setSpacing(8)

        header_layout = QHBoxLayout()
        title = QLabel("Résultats scientifiques")
        title.setObjectName("sectionTitle")
        self.analysis_status_label = QLabel("PRÊT")
        self.analysis_status_label.setProperty("state", "neutral")
        self.analysis_count_label = QLabel("0 analyses")
        self.analysis_count_label.setObjectName("mutedText")
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(self.analysis_status_label)
        header_layout.addWidget(self.analysis_count_label)
        layout.addLayout(header_layout)

        metrics = QHBoxLayout()
        metrics.setSpacing(8)
        self.source_metric = self._metric_card("SOURCE", "Aucune")
        self.channels_metric = self._metric_card("CANAUX", "0")
        self.rate_metric = self._metric_card("ÉCHANTILLONNAGE", "—")
        self.quality_metric = self._metric_card("QUALITÉ", "Non évaluée")
        for metric in (
            self.source_metric,
            self.channels_metric,
            self.rate_metric,
            self.quality_metric,
        ):
            metrics.addWidget(metric)
        layout.addLayout(metrics)

        self.tab_widget = QTabWidget()
        self.tab_widget.setDocumentMode(True)

        self.stats_table = QTableWidget()
        self.stats_table.verticalHeader().setVisible(False)
        self.stats_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.stats_table.horizontalHeader().setStretchLastSection(True)
        self.tab_widget.addTab(self.stats_table, "Synthèse temporelle")

        self.spectral_table = QTableWidget()
        self.spectral_table.verticalHeader().setVisible(False)
        self.spectral_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.spectral_table.horizontalHeader().setStretchLastSection(True)
        self.wave_table = self.spectral_table
        self.tab_widget.addTab(self.spectral_table, "Paramètres spectraux")

        self.quality_table = QTableWidget()
        self.quality_table.verticalHeader().setVisible(False)
        self.quality_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.quality_table.horizontalHeader().setStretchLastSection(True)
        self.tab_widget.addTab(self.quality_table, "Diagnostic qualité")

        self.time_figure = Figure(figsize=(7, 4), tight_layout=True)
        self.time_canvas = FigureCanvas(self.time_figure)
        time_page = QWidget()
        time_layout = QVBoxLayout(time_page)
        time_layout.setContentsMargins(4, 4, 4, 4)
        time_layout.setSpacing(4)
        time_controls = QHBoxLayout()
        self.channel_combo = QComboBox()
        self.channel_combo.setMinimumWidth(160)
        self.overlay_channels_check = QCheckBox("Superposer tous les canaux")
        self.raw_signal_check = QCheckBox("Afficher la tension brute")
        self.raw_signal_check.setVisible(False)
        self.center_signal_check = QCheckBox("Centrer")
        self.std_guides_check = QCheckBox("Repères ±σ")
        self.time_cursor_label = QLabel("Curseur : —")
        self.time_cursor_label.setObjectName("mutedText")
        time_controls.addWidget(QLabel("CANAL"))
        time_controls.addWidget(self.channel_combo)
        time_controls.addWidget(self.overlay_channels_check)
        time_controls.addWidget(self.raw_signal_check)
        time_controls.addWidget(self.center_signal_check)
        time_controls.addWidget(self.std_guides_check)
        time_controls.addStretch()
        time_controls.addWidget(self.time_cursor_label)
        time_layout.addLayout(time_controls)
        time_layout.addWidget(NavigationToolbar(self.time_canvas, time_page))
        time_layout.addWidget(self.time_canvas, 1)
        self.tab_widget.addTab(time_page, "Signal temporel")

        self.spectrum_figure = Figure(figsize=(7, 4), tight_layout=True)
        self.spectrum_canvas = FigureCanvas(self.spectrum_figure)
        spectrum_page = QWidget()
        spectrum_layout = QVBoxLayout(spectrum_page)
        spectrum_layout.setContentsMargins(4, 4, 4, 4)
        spectrum_layout.setSpacing(4)
        spectrum_controls = QHBoxLayout()
        self.spectrum_scale_combo = QComboBox()
        self.spectrum_scale_combo.addItem("Échelle logarithmique", "log")
        self.spectrum_scale_combo.addItem("Échelle linéaire", "linear")
        self.confidence_interval_check = QCheckBox("Intervalle de confiance 95 %")
        self.confidence_interval_check.setChecked(True)
        self.cumulative_energy_check = QCheckBox("Énergie cumulée")
        self.spectrum_readout_label = QLabel("Pic : —")
        self.spectrum_readout_label.setObjectName("mutedText")
        spectrum_controls.addWidget(self.spectrum_scale_combo)
        spectrum_controls.addWidget(self.confidence_interval_check)
        spectrum_controls.addWidget(self.cumulative_energy_check)
        spectrum_controls.addStretch()
        spectrum_controls.addWidget(self.spectrum_readout_label)
        spectrum_layout.addLayout(spectrum_controls)
        spectrum_layout.addWidget(NavigationToolbar(self.spectrum_canvas, spectrum_page))
        spectrum_layout.addWidget(self.spectrum_canvas, 1)
        self.tab_widget.addTab(spectrum_page, "Spectre / PSD")

        self.separation_figure = Figure(figsize=(7, 4), tight_layout=True)
        self.separation_canvas = FigureCanvas(self.separation_figure)
        separation_page = QWidget()
        separation_layout = QVBoxLayout(separation_page)
        separation_layout.setContentsMargins(4, 4, 4, 4)
        separation_layout.addWidget(NavigationToolbar(self.separation_canvas, separation_page))
        separation_layout.addWidget(self.separation_canvas, 1)
        self.tab_widget.addTab(separation_page, "Incidente / réfléchie")

        self.report_text = QTextEdit()
        self.report_text.setReadOnly(True)
        self.tab_widget.addTab(self.report_text, "Rapport")

        layout.addWidget(self.tab_widget)

    @staticmethod
    def _metric_card(label: str, value: str) -> QFrame:
        card = QFrame()
        card.setObjectName("metricCard")
        card.setMinimumHeight(50)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(9, 5, 9, 5)
        card_layout.setSpacing(2)
        label_widget = QLabel(label)
        label_widget.setObjectName("metricLabel")
        value_widget = QLabel(value)
        value_widget.setObjectName("metricValue")
        value_widget.setProperty("metricValue", True)
        card_layout.addWidget(label_widget)
        card_layout.addWidget(value_widget)
        return card

    @staticmethod
    def _set_metric(card: QFrame, value: str) -> None:
        label = card.findChild(QLabel, "metricValue")
        if label is not None:
            label.setText(value)

    def update_analysis_status(self, status: str, count: int = 0) -> None:
        self.analysis_status_label.setText(status)
        self.analysis_count_label.setText(f"{count} analyses")


class AnalysisView(QWidget):
    """Vue principale d'analyse branchee sur le post-traitement."""

    analysis_completed = Signal(str, dict)
    filter_applied = Signal(str, dict)
    data_exported = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_dark_mode = False
        self.analysis_count = 0
        self.post_processor = PostProcessor()
        self.current_project_dir: Path | None = None
        self.current_project_metadata: dict[str, object] = {}
        self.current_data_file: str | None = None
        self.current_analysis_result: dict[str, object] | None = None
        self._tools_panel_expanded = True

        self._build_ui()
        self._setup_connections()

    def _build_ui(self) -> None:
        self.setObjectName("analysis_view")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 10, 16, 12)
        layout.setSpacing(8)
        self.tools_panel = AnalysisToolsPanel()
        self.tools_toggle_button = self.tools_panel.parameters_toggle_button
        self.results_area = AnalysisResultsArea()
        layout.addWidget(self.tools_panel)
        layout.addWidget(self.results_area, 1)

    def _setup_connections(self) -> None:
        self.tools_panel.analysis_requested.connect(self.on_analysis_requested)
        self.tools_panel.filter_applied.connect(self.on_filter_applied)
        self.tools_panel.export_requested.connect(self.on_export_requested)
        self.tools_panel.load_button.clicked.connect(self._load_selected_or_dialog)
        self.tools_panel.refresh_button.clicked.connect(self.refresh_project_files)
        self.tools_panel.data_combo.activated.connect(self._load_selected_from_combo)
        self.tools_panel.parameters_toggle_requested.connect(self._toggle_tools_panel)
        self.results_area.channel_combo.currentTextChanged.connect(self._on_plot_controls_changed)
        self.results_area.overlay_channels_check.toggled.connect(self._on_plot_controls_changed)
        self.results_area.raw_signal_check.toggled.connect(self._update_time_plot)
        self.results_area.center_signal_check.toggled.connect(self._update_time_plot)
        self.results_area.std_guides_check.toggled.connect(self._update_time_plot)
        self.results_area.spectrum_scale_combo.currentIndexChanged.connect(
            self._update_spectrum_plot
        )
        self.results_area.confidence_interval_check.toggled.connect(self._update_spectrum_plot)
        self.results_area.cumulative_energy_check.toggled.connect(self._update_spectrum_plot)
        self.results_area.time_canvas.mpl_connect("motion_notify_event", self._on_time_cursor_moved)

    def _toggle_tools_panel(self) -> None:
        self._set_tools_panel_expanded(not self._tools_panel_expanded)

    def _set_tools_panel_expanded(self, expanded: bool) -> None:
        self._tools_panel_expanded = bool(expanded)
        self.tools_panel.parameters_panel.setVisible(self._tools_panel_expanded)
        self.tools_toggle_button.setText(
            "Réduire les réglages" if self._tools_panel_expanded else "Afficher les réglages"
        )

    def set_project_context(self, project_metadata: dict, project_dir: str) -> None:
        self.current_project_metadata = project_metadata or {}
        self.current_project_dir = Path(project_dir) if project_dir else None
        self.refresh_project_files()

    def refresh_project_files(self) -> None:
        current_file = self.tools_panel.data_combo.currentData()
        self.tools_panel.data_combo.clear()
        self.tools_panel.data_combo.addItem("Aucun fichier sélectionné", None)
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
                if resolved in seen:
                    continue
                seen.add(resolved)
                self._add_or_select_file_item(resolved, select=False)
        if current_file:
            current_index = self.tools_panel.data_combo.findData(current_file)
            if current_index >= 0:
                self.tools_panel.data_combo.setCurrentIndex(current_index)

    def open_file_dialog(self) -> None:
        base_dir = self._get_default_search_directory()
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Charger des donnees",
            str(base_dir),
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
        self._add_or_select_file_item(file_path)
        source_name = Path(file_path).name
        if len(source_name) > 20:
            source_name = f"{source_name[:17]}…"
        self.results_area._set_metric(self.results_area.source_metric, source_name)
        self.results_area._set_metric(
            self.results_area.channels_metric,
            str(len((self.post_processor.current_data or {}).get("channel_keys", []))),
        )
        self.results_area._set_metric(
            self.results_area.rate_metric,
            f"{self.post_processor.sample_rate:g} Hz",
        )
        data = self.post_processor.current_data or {}
        sample_count = int(data.get("metadata", {}).get("n_samples", 0) or 0)
        if not sample_count and data.get("channel_keys"):
            sample_count = self.post_processor._channel_sample_count(data["channel_keys"][0])
        self.tools_panel.set_record_duration(sample_count / self.post_processor.sample_rate)
        self._refresh_channel_selector()
        self._update_time_plot()
        self.results_area.update_analysis_status("DONNÉES CHARGÉES", self.analysis_count)
        return True

    def on_analysis_requested(self, analysis_type: str, params: dict) -> None:
        if self.post_processor.current_data is None:
            QMessageBox.warning(self, "Analyse", "Aucun fichier de donnees n'est charge.")
            return

        self.analysis_count += 1
        self.results_area.update_analysis_status("Analyse en cours...", self.analysis_count)

        self.post_processor.config["analysis"].update(params)

        if not self.post_processor.run_analysis():
            self.analysis_count -= 1
            self.results_area.update_analysis_status("Echec analyse", self.analysis_count)
            QMessageBox.warning(self, "Analyse", "Le post-traitement a echoue.")
            return

        self.current_analysis_result = self.post_processor.current_analysis
        self._update_results_views()
        self._set_tools_panel_expanded(False)
        quality = self.current_analysis_result.get("quality", {})
        channel_warning_count = sum(len(item.get("warnings", [])) for item in quality.values())
        processing_warning_count = len(self.current_analysis_result.get("metadata", {}).get("warnings", []))
        warning_count = channel_warning_count + processing_warning_count
        rejected_count = sum(
            1 for item in quality.values() if item.get("status") == "rejected"
        )
        quality_text = (
            "Validée"
            if warning_count == 0
            else f"{rejected_count} rejeté(s) · {warning_count} alerte(s)"
            if rejected_count
            else f"{warning_count} alerte(s)"
        )
        self.results_area._set_metric(self.results_area.quality_metric, quality_text)
        self.results_area.analysis_status_label.setProperty(
            "state", "success" if warning_count == 0 else "warning"
        )
        self.results_area.analysis_status_label.style().unpolish(self.results_area.analysis_status_label)
        self.results_area.analysis_status_label.style().polish(self.results_area.analysis_status_label)
        self.results_area.update_analysis_status("ANALYSE TERMINÉE", self.analysis_count)
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
            QMessageBox.warning(self, "Export", "Aucun resultat d'analyse a exporter.")
            return

        suffix_map = {"csv": "csv", "json": "json", "hdf5": "h5", "txt": "txt"}
        filters = {
            "csv": "Fichiers CSV (*.csv)",
            "json": "Fichiers JSON (*.json)",
            "hdf5": "Fichiers HDF5 (*.h5 *.hdf5)",
            "txt": "Fichiers texte (*.txt)",
        }
        default_path = (
            self._get_default_export_directory()
            / f"analysis_results.{suffix_map.get(export_type, export_type)}"
        )

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            f"Exporter {export_type.upper()}",
            str(default_path),
            filters.get(export_type, "Tous les fichiers (*)"),
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
            QMessageBox.warning(self, "Export", "L'export des resultats a echoue.")

    def set_theme(self, is_dark: bool) -> None:
        # Le thème de production est centralisé au niveau de l'application.
        self.is_dark_mode = is_dark

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
        self.results_area.stats_table.clearContents()
        self.results_area.stats_table.setRowCount(0)
        self.results_area.wave_table.clearContents()
        self.results_area.wave_table.setRowCount(0)
        self.results_area.quality_table.clearContents()
        self.results_area.quality_table.setRowCount(0)
        self.results_area.time_figure.clear()
        self.results_area.time_canvas.draw_idle()
        self.results_area.spectrum_figure.clear()
        self.results_area.spectrum_canvas.draw_idle()
        self.results_area.separation_figure.clear()
        self.results_area.separation_canvas.draw_idle()
        self.results_area.report_text.clear()
        self.results_area.update_analysis_status("Pret", 0)

    def _load_selected_or_dialog(self) -> None:
        file_path = self.tools_panel.data_combo.currentData()
        if file_path:
            self.load_data_file(str(file_path))
            return
        self.open_file_dialog()

    def _load_selected_from_combo(self, _index: int) -> None:
        file_path = self.tools_panel.data_combo.currentData()
        if file_path:
            self.load_data_file(str(file_path))

    def _get_default_search_directory(self) -> Path:
        if self.current_project_dir:
            export_dir = self.current_project_dir / "exports"
            return export_dir if export_dir.exists() else self.current_project_dir
        return Path.cwd()

    def _get_default_export_directory(self) -> Path:
        if self.current_project_dir:
            analysis_dir = self.current_project_dir / "analysis"
            analysis_dir.mkdir(parents=True, exist_ok=True)
            return analysis_dir
        return Path.cwd()

    def _add_or_select_file_item(self, file_path: str, select: bool = True) -> None:
        target = str(Path(file_path))
        index = self.tools_panel.data_combo.findData(target)
        if index < 0:
            self.tools_panel.data_combo.addItem(Path(target).name, target)
            index = self.tools_panel.data_combo.count() - 1
        if select:
            self.tools_panel.data_combo.setCurrentIndex(index)

    def _refresh_channel_selector(self) -> None:
        data = self.post_processor.current_data or {}
        channels = list(data.get("channel_keys", []))
        current = self.results_area.channel_combo.currentText()
        self.results_area.channel_combo.blockSignals(True)
        self.results_area.channel_combo.clear()
        self.results_area.channel_combo.addItems(channels)
        if current in channels:
            self.results_area.channel_combo.setCurrentText(current)
        self.results_area.channel_combo.blockSignals(False)
        self.results_area.raw_signal_check.setVisible(bool(data.get("raw_channels")))

    def _on_plot_controls_changed(self, *_args) -> None:
        self._update_time_plot()
        self._update_spectrum_plot()

    def _on_time_cursor_moved(self, event) -> None:
        if event.inaxes is None or event.xdata is None or event.ydata is None:
            return
        self.results_area.time_cursor_label.setText(
            f"Curseur : t={event.xdata:.3f} s · y={event.ydata:.6g}"
        )

    def _channel_metadata(self, channel: str) -> dict:
        data = self.post_processor.current_data or {}
        return self.post_processor._channel_metadata_map(
            list(data.get("channel_keys", [])),
            data.get("channel_metadata", {}),
        ).get(channel, {})

    def _channel_unit(self, channel: str) -> str:
        metadata = self._channel_metadata(channel)
        return str(
            metadata.get("physical_unit")
            or metadata.get("physical_units")
            or metadata.get("unit")
            or "unité"
        )

    @staticmethod
    def _quality_label(indicators: dict) -> str:
        return {
            "valid": "VALIDE",
            "warning": "À VÉRIFIER",
            "rejected": "REJETÉ",
        }.get(str(indicators.get("status", "")), "VALIDE" if not indicators.get("warnings") else "À VÉRIFIER")

    def _update_results_views(self) -> None:
        results = self.current_analysis_result or {}
        basic_stats = results.get("basic_stats", {})
        wave_parameters = results.get("wave_parameters", {})
        channels = list(basic_stats.keys())
        self.results_area.stats_table.clearContents()
        stat_columns = (
            ("Canal", None),
            ("Unité", None),
            ("N", "sample_count"),
            ("Moyenne", "mean"),
            ("Écart-type", "std"),
            ("RMS", "rms"),
            ("Minimum", "min"),
            ("Maximum", "max"),
            ("Asymétrie", "skewness"),
            ("Aplatissement", "kurtosis"),
        )
        self.results_area.stats_table.setColumnCount(len(stat_columns))
        self.results_area.stats_table.setHorizontalHeaderLabels([item[0] for item in stat_columns])
        self.results_area.stats_table.setRowCount(len(channels))
        for row, channel in enumerate(channels):
            stats = basic_stats.get(channel, {})
            values = [channel, self._channel_unit(channel)] + [
                stats.get(metric, "") for _, metric in stat_columns[2:]
            ]
            for column, value in enumerate(values):
                if isinstance(value, float):
                    value = f"{value:.6g}"
                self.results_area.stats_table.setItem(row, column, QTableWidgetItem(str(value)))

        spectral = results.get("spectral_analysis", {})
        spectral_headers = [
            "Canal", "Verdict", "Hm0", "H1/3", "fpic (Hz)", "Tp (s)", "Tm01 (s)",
            "Tm02 (s)", "Te (s)", "m0", "Δf (Hz)", "Segments", "DDL ≈",
        ]
        self.results_area.spectral_table.clearContents()
        self.results_area.spectral_table.setColumnCount(len(spectral_headers))
        self.results_area.spectral_table.setHorizontalHeaderLabels(spectral_headers)
        self.results_area.spectral_table.setRowCount(len(channels))
        for row, channel in enumerate(channels):
            spectrum = spectral.get(channel, {})
            waves = wave_parameters.get(channel, {})
            quality = results.get("quality", {}).get(channel, {})
            moments = spectrum.get("spectral_moments", {})
            tp_value = waves.get("Tp", 0.0)
            tp_text = f"{tp_value:.6g}" if quality.get("peak_period_reliable", False) else "NON FIABLE"
            values = (
                channel,
                self._quality_label(quality),
                spectrum.get("Hm0", 0.0),
                waves.get("H1_3", 0.0),
                spectrum.get("peak_frequency", 0.0),
                tp_text,
                spectrum.get("Tm01", 0.0),
                spectrum.get("Tm02", 0.0),
                spectrum.get("Te", 0.0),
                moments.get("m0", 0.0),
                spectrum.get("frequency_resolution", 0.0),
                spectrum.get("segment_count", 0),
                spectrum.get("equivalent_degrees_of_freedom_approx", 0),
            )
            for column, value in enumerate(values):
                if isinstance(value, float):
                    value = f"{value:.6g}"
                self.results_area.spectral_table.setItem(row, column, QTableWidgetItem(str(value)))

        quality_headers = [
            "Canal", "Verdict", "Alertes", "Var. PSD/temps", "Stationnarité",
            "Cycles au pic", "Éch./période", "Plate (%)", "Dérive /s",
        ]
        quality_results = results.get("quality", {})
        self.results_area.quality_table.clearContents()
        self.results_area.quality_table.setColumnCount(len(quality_headers))
        self.results_area.quality_table.setHorizontalHeaderLabels(quality_headers)
        self.results_area.quality_table.setRowCount(len(channels))
        for row, channel in enumerate(channels):
            indicators = quality_results.get(channel, {})
            values = (
                channel,
                self._quality_label(indicators),
                "\n".join(map(str, indicators.get("warnings", []))) or "Aucune",
                indicators.get("spectral_to_time_variance_ratio", 0.0),
                indicators.get("block_variance_ratio", 0.0),
                indicators.get("record_cycles_at_peak", 0.0),
                indicators.get("samples_per_peak_period", 0.0),
                100.0 * indicators.get("longest_flat_run_fraction", 0.0),
                indicators.get("linear_trend_per_second", 0.0),
            )
            for column, value in enumerate(values):
                if isinstance(value, float):
                    value = f"{value:.6g}"
                self.results_area.quality_table.setItem(row, column, QTableWidgetItem(str(value)))
        self.results_area.quality_table.resizeRowsToContents()

        self._update_spectrum_plot()
        self._update_separation_plot()

        self.results_area.report_text.setPlainText(self._build_report_text())

    def _update_time_plot(self, *_args) -> None:
        figure = self.results_area.time_figure
        figure.clear()
        axis = figure.add_subplot(111)
        figure.set_facecolor("#FFFFFF")
        axis.set_facecolor("#FFFFFF")
        data = self.post_processor.current_data or {}
        channel_keys = list(data.get("channel_keys", []))
        selected = self.results_area.channel_combo.currentText()
        plotted_channels = (
            channel_keys if self.results_area.overlay_channels_check.isChecked() else [selected]
        )
        plotted_channels = [channel for channel in plotted_channels if channel in channel_keys]
        raw_channels = data.get("raw_channels", {})
        use_raw = self.results_area.raw_signal_check.isChecked() and bool(raw_channels)
        if plotted_channels:
            for channel in plotted_channels[:24]:
                sampled_time, values = self.post_processor.load_channel_preview(
                    channel,
                    raw=use_raw,
                )
                if self.results_area.center_signal_check.isChecked():
                    values = values - float(np.mean(values))
                axis.plot(sampled_time, values, linewidth=0.8, label=channel)
                if channel == selected and self.results_area.std_guides_check.isChecked():
                    mean = float(np.mean(values))
                    standard_deviation = float(np.std(values))
                    axis.axhline(mean, color="#405965", linewidth=0.8, alpha=0.7)
                    axis.axhline(
                        mean + standard_deviation,
                        color="#C47B18",
                        linewidth=0.8,
                        linestyle="--",
                    )
                    axis.axhline(
                        mean - standard_deviation,
                        color="#C47B18",
                        linewidth=0.8,
                        linestyle="--",
                    )
            if self.current_analysis_result:
                metadata = self.current_analysis_result.get("metadata", {})
                axis.axvspan(
                    float(metadata.get("analysis_start_s", sampled_time[0])),
                    float(metadata.get("analysis_end_s", sampled_time[-1])),
                    color="#1A7188",
                    alpha=0.06,
                    label="Intervalle analysé",
                )
            axis.set_xlabel("Temps (s)", color="#405965")
            unit = "V" if use_raw else self._channel_unit(selected)
            axis.set_ylabel(unit, color="#405965")
            if plotted_channels:
                axis.legend(loc="best", frameon=False, fontsize=7, ncol=2)
        else:
            axis.text(
                0.5,
                0.5,
                "APERÇU TEMPOREL NON CHARGÉ POUR CE FORMAT",
                ha="center",
                va="center",
                transform=axis.transAxes,
                color="#667C88",
            )
        axis.tick_params(colors="#667C88", labelsize=9)
        axis.grid(True, color="#DCE5EA", linewidth=0.7, alpha=0.8)
        axis.spines["top"].set_visible(False)
        axis.spines["right"].set_visible(False)
        self.results_area.time_canvas.draw_idle()

    def _update_spectrum_plot(self, *_args) -> None:
        spectral = (self.current_analysis_result or {}).get("spectral_analysis", {})
        figure = self.results_area.spectrum_figure
        figure.clear()
        axis = figure.add_subplot(111)
        figure.set_facecolor("#FFFFFF")
        axis.set_facecolor("#FFFFFF")
        selected = self.results_area.channel_combo.currentText()
        plotted_channels = (
            list(spectral)
            if self.results_area.overlay_channels_check.isChecked()
            else ([selected] if selected in spectral else [])
        )
        scale = str(self.results_area.spectrum_scale_combo.currentData())
        for channel in plotted_channels:
            values = spectral[channel]
            frequencies = np.asarray(values.get("frequencies", []), dtype=float)
            density = np.asarray(values.get("psd", []), dtype=float)
            valid = (frequencies > 0) & np.isfinite(density)
            if scale == "log":
                valid &= density > 0
            if np.any(valid):
                axis.plot(frequencies[valid], density[valid], label=channel, linewidth=1.35)
                if channel == selected:
                    peak_frequency = float(values.get("peak_frequency", 0.0))
                    peak_psd = float(values.get("peak_psd", 0.0))
                    axis.plot([peak_frequency], [peak_psd], marker="o", color="#D46A1F", markersize=5)
                    if self.results_area.confidence_interval_check.isChecked():
                        factors = values.get("psd_confidence_interval_95_factors_approx", [])
                        if len(factors) == 2:
                            axis.fill_between(
                                frequencies[valid],
                                density[valid] * float(factors[0]),
                                density[valid] * float(factors[1]),
                                color="#1A7188",
                                alpha=0.13,
                                label="IC 95 % approx.",
                            )
                    quality = (self.current_analysis_result or {}).get("quality", {}).get(channel, {})
                    peak_period = float(values.get("peak_period", 0.0))
                    tp_text = (
                        f"Tp={peak_period:.4g} s"
                        if quality.get("peak_period_reliable")
                        else "Tp non fiable"
                    )
                    self.results_area.spectrum_readout_label.setText(
                        f"Pic : {peak_frequency:.5g} Hz · {tp_text} · "
                        f"Δf={values.get('frequency_resolution', 0):.5g} Hz"
                    )
                    if self.results_area.cumulative_energy_check.isChecked():
                        energy_axis = axis.twinx()
                        frequency_step = float(values.get("frequency_resolution", 0.0))
                        cumulative = np.cumsum(np.maximum(density, 0.0)) * frequency_step
                        if cumulative.size and cumulative[-1] > 0:
                            energy_axis.plot(
                                frequencies,
                                100.0 * cumulative / cumulative[-1],
                                color="#C47B18",
                                linewidth=1.0,
                                linestyle="--",
                            )
                            energy_axis.set_ylabel("Énergie cumulée (%)", color="#C47B18")
                            energy_axis.set_ylim(0, 105)
                            energy_axis.tick_params(colors="#C47B18", labelsize=8)
        axis.set_yscale(scale)
        axis.set_xlabel("Fréquence (Hz)", color="#405965")
        axis.set_ylabel("Densité spectrale", color="#405965")
        axis.tick_params(colors="#667C88", labelsize=9)
        axis.grid(True, which="both", color="#DCE5EA", linewidth=0.7, alpha=0.8)
        axis.spines["top"].set_visible(False)
        axis.spines["right"].set_visible(False)
        axis.spines["bottom"].set_color("#B7C6CD")
        axis.spines["left"].set_color("#B7C6CD")
        if plotted_channels:
            axis.legend(loc="best", frameon=False, fontsize=8)
        self.results_area.spectrum_canvas.draw_idle()

    def _update_separation_plot(self) -> None:
        separation = (self.current_analysis_result or {}).get(
            "incident_reflected_analysis",
            {},
        )
        figure = self.results_area.separation_figure
        figure.clear()
        axis = figure.add_subplot(111)
        figure.set_facecolor("#FFFFFF")
        axis.set_facecolor("#FFFFFF")
        if separation.get("status") == "complete":
            frequencies = np.asarray(separation.get("frequencies", []), dtype=float)
            incident = np.asarray(separation.get("incident_psd", []), dtype=float)
            reflected = np.asarray(separation.get("reflected_psd", []), dtype=float)
            valid = np.asarray(
                separation.get("valid_frequency_mask", []),
                dtype=bool,
            )
            if len(valid) == len(frequencies):
                axis.semilogy(
                    frequencies[valid],
                    incident[valid],
                    color="#1A7188",
                    linewidth=1.5,
                    label="Incidente",
                )
                axis.semilogy(
                    frequencies[valid],
                    reflected[valid],
                    color="#C47B18",
                    linewidth=1.5,
                    label="Réfléchie",
                )
                axis.legend(frameon=False, loc="best")
            axis.set_title(
                "Coefficient de réflexion énergétique "
                f"Kr = {separation.get('energy_reflection_coefficient', 0):.4f}",
                color="#203843",
            )
        else:
            axis.text(
                0.5,
                0.5,
                separation.get(
                    "reason",
                    "Configurez au moins trois sondes, leurs positions et la profondeur d'eau.",
                ),
                ha="center",
                va="center",
                wrap=True,
                color="#667C88",
                transform=axis.transAxes,
            )
        axis.set_xlabel("Fréquence (Hz)", color="#405965")
        physical_unit = separation.get("physical_unit", "unité")
        axis.set_ylabel(f"Densité spectrale ({physical_unit}²/Hz)", color="#405965")
        axis.tick_params(colors="#667C88", labelsize=9)
        axis.grid(True, which="both", color="#DCE5EA", linewidth=0.7, alpha=0.8)
        axis.spines["top"].set_visible(False)
        axis.spines["right"].set_visible(False)
        axis.spines["bottom"].set_color("#B7C6CD")
        axis.spines["left"].set_color("#B7C6CD")
        self.results_area.separation_canvas.draw_idle()

    def _build_report_text(self) -> str:
        return build_scientific_report_text(
            self.current_analysis_result or {},
            self.current_data_file,
            self.current_project_metadata,
            {"title": "Rapport scientifique CHNeoWave"},
        )
