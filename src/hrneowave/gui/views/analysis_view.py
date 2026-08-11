"""Vue d'analyse CHNeoWave."""

from pathlib import Path

import numpy as np
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFileDialog,
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

from ...core.post_processor import PostProcessor


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
            },
        )


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
        self.stats_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tab_widget.addTab(self.stats_table, "Statistiques")

        self.wave_table = QTableWidget()
        self.wave_table.verticalHeader().setVisible(False)
        self.wave_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tab_widget.addTab(self.wave_table, "Parametres de houle")

        self.spectrum_figure = Figure(figsize=(7, 4), tight_layout=True)
        self.spectrum_canvas = FigureCanvas(self.spectrum_figure)
        self.tab_widget.addTab(self.spectrum_canvas, "Spectres")

        self.separation_figure = Figure(figsize=(7, 4), tight_layout=True)
        self.separation_canvas = FigureCanvas(self.separation_figure)
        self.tab_widget.addTab(
            self.separation_canvas,
            "Incidente / réfléchie",
        )

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
                if file_path.suffix.lower() not in {".csv", ".json", ".h5", ".hdf5"}:
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
            "Donnees (*.csv *.json *.h5 *.hdf5)",
        )
        if file_path:
            self.load_data_file(file_path)

    def load_data_file(self, file_path: str) -> bool:
        if not file_path:
            return False

        if not self.post_processor.load_data_file(file_path):
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
        warning_count = sum(len(item.get("warnings", [])) for item in quality.values())
        quality_text = "Validée" if warning_count == 0 else f"{warning_count} alerte(s)"
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

    def _update_results_views(self) -> None:
        results = self.current_analysis_result or {}
        basic_stats = results.get("basic_stats", {})
        wave_parameters = results.get("wave_parameters", {})
        channels = list(basic_stats.keys())
        metrics = (
            ("mean", "Moyenne"),
            ("std", "Écart-type"),
            ("min", "Minimum"),
            ("max", "Maximum"),
            ("rms", "Valeur RMS"),
            ("skewness", "Asymétrie"),
            ("kurtosis", "Aplatissement"),
        )

        self.results_area.stats_table.clearContents()
        self.results_area.stats_table.setColumnCount(len(channels) + 1)
        self.results_area.stats_table.setHorizontalHeaderLabels(["Parametre"] + channels)
        self.results_area.stats_table.setRowCount(len(metrics))

        for row, (metric, metric_label) in enumerate(metrics):
            self.results_area.stats_table.setItem(row, 0, QTableWidgetItem(metric_label))
            for col, channel in enumerate(channels, start=1):
                value = basic_stats.get(channel, {}).get(metric, "")
                if isinstance(value, float):
                    value = f"{value:.6f}"
                self.results_area.stats_table.setItem(row, col, QTableWidgetItem(str(value)))

        wave_metrics = (
            ("H1_3", "H1/3 temporel"),
            ("Hm0", "Hm0 spectral"),
            ("H_max", "Hauteur maximale"),
            ("Tp", "Période de pic Tp (s)"),
            ("Tm01", "Période Tm01 (s)"),
            ("Tm02", "Période Tm02 (s)"),
            ("T_mean", "Période moyenne (s)"),
            ("n_waves", "Vagues détectées"),
        )
        self.results_area.wave_table.clearContents()
        self.results_area.wave_table.setColumnCount(len(channels) + 1)
        self.results_area.wave_table.setHorizontalHeaderLabels(["Parametre"] + channels)
        self.results_area.wave_table.setRowCount(len(wave_metrics))
        for row, (metric, metric_label) in enumerate(wave_metrics):
            self.results_area.wave_table.setItem(row, 0, QTableWidgetItem(metric_label))
            for col, channel in enumerate(channels, start=1):
                value = wave_parameters.get(channel, {}).get(metric, "")
                if isinstance(value, float):
                    value = f"{value:.6f}"
                self.results_area.wave_table.setItem(row, col, QTableWidgetItem(str(value)))

        self._update_spectrum_plot()
        self._update_separation_plot()

        self.results_area.report_text.setPlainText(self._build_report_text())

    def _update_spectrum_plot(self) -> None:
        spectral = (self.current_analysis_result or {}).get("spectral_analysis", {})
        figure = self.results_area.spectrum_figure
        figure.clear()
        axis = figure.add_subplot(111)
        figure.set_facecolor("#FFFFFF")
        axis.set_facecolor("#FFFFFF")
        for channel, values in spectral.items():
            frequencies = np.asarray(values.get("frequencies", []), dtype=float)
            density = np.asarray(values.get("psd", []), dtype=float)
            valid = (frequencies > 0) & np.isfinite(density) & (density > 0)
            if np.any(valid):
                axis.semilogy(
                    frequencies[valid],
                    density[valid],
                    label=channel,
                    linewidth=1.35,
                )
        axis.set_xlabel("Fréquence (Hz)", color="#405965")
        axis.set_ylabel("Densité spectrale", color="#405965")
        axis.tick_params(colors="#667C88", labelsize=9)
        axis.grid(True, which="both", color="#DCE5EA", linewidth=0.7, alpha=0.8)
        axis.spines["top"].set_visible(False)
        axis.spines["right"].set_visible(False)
        axis.spines["bottom"].set_color("#B7C6CD")
        axis.spines["left"].set_color("#B7C6CD")
        if spectral:
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
        results = self.current_analysis_result or {}
        basic_stats = results.get("basic_stats", {})
        spectral = results.get("spectral_analysis", {})
        waves = results.get("wave_parameters", {})
        quality = results.get("quality", {})
        cross_spectral = results.get("cross_spectral_analysis", {})
        separation = results.get("incident_reflected_analysis", {})

        lines = ["Rapport d'analyse CHNeoWave"]
        if self.current_data_file:
            lines.append(f"Fichier: {self.current_data_file}")
        lines.append(f"Frequence d'echantillonnage: {self.post_processor.sample_rate} Hz")
        lines.append("")

        for channel, stats in basic_stats.items():
            lines.append(f"[{channel}]")
            lines.append(f"  moyenne: {stats.get('mean', 0):.6f}")
            lines.append(f"  ecart-type: {stats.get('std', 0):.6f}")
            lines.append(f"  min/max: {stats.get('min', 0):.6f} / {stats.get('max', 0):.6f}")
            if channel in spectral:
                lines.append(f"  frequence pic: {spectral[channel].get('peak_frequency', 0):.6f} Hz")
                lines.append(f"  resolution: {spectral[channel].get('frequency_resolution', 0):.6f} Hz")
            if channel in waves:
                lines.append(f"  H1/3 temporel: {waves[channel].get('H1_3', 0):.6f}")
                lines.append(f"  Hm0 spectral: {waves[channel].get('Hm0', 0):.6f}")
                lines.append(f"  Hmax: {waves[channel].get('H_max', 0):.6f}")
                lines.append(f"  Tp: {waves[channel].get('Tp', 0):.6f} s")
                tm01 = waves[channel].get("Tm01", 0)
                tm02 = waves[channel].get("Tm02", 0)
                lines.append(f"  Tm01/Tm02: {tm01:.6f} / {tm02:.6f} s")
                lines.append(f"  vagues detectees: {waves[channel].get('n_waves', 0)}")
            channel_warnings = quality.get(channel, {}).get("warnings", [])
            for warning in channel_warnings:
                lines.append(f"  ATTENTION: {warning}")
            lines.append("")

        if cross_spectral:
            lines.append("Analyse croisee par rapport au canal de reference")
            for pair, metrics in cross_spectral.items():
                lines.append(
                    f"  {pair}: coherence={metrics.get('coherence_at_reference_peak', 0):.4f}, "
                    f"phase={metrics.get('phase_at_reference_peak_degrees', 0):.2f} deg"
                )

        if separation.get("status") == "complete":
            separation_unit = separation.get("physical_unit", "unité")
            lines.extend(
                [
                    "",
                    "Separation multi-sondes incidente/reflechie",
                    f"  sondes: {separation.get('probe_count', 0)}",
                    f"  profondeur: {separation.get('configuration', {}).get('water_depth_m', 0):.6g} m",
                    f"  Hm0 incident: {separation.get('incident_Hm0', 0):.6f} {separation_unit}",
                    f"  Hm0 reflechi: {separation.get('reflected_Hm0', 0):.6f} {separation_unit}",
                    "  coefficient de reflexion energetique Kr: "
                    f"{separation.get('energy_reflection_coefficient', 0):.6f}",
                ]
            )

        return "\n".join(lines).strip()
