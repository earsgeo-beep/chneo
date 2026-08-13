"""Vue de rapport scientifique et traçable CHNeoWave."""

import base64
import io
import json
import math
from pathlib import Path

import numpy as np
from matplotlib.figure import Figure
from PySide6.QtCore import QDate, Qt, Signal
from PySide6.QtGui import QPageLayout, QTextDocument
from PySide6.QtPrintSupport import QPrinter
from PySide6.QtWidgets import (
    QCheckBox,
    QDateEdit,
    QFileDialog,
    QFormLayout,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ...core.scientific_report import (
    build_scientific_report_html,
    build_scientific_report_text,
)


class ReportConfigPanel(QFrame):
    """Panneau de configuration du rapport."""

    report_generated = Signal(str, dict)
    template_selected = Signal(str)
    export_requested = Signal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.default_export_dir: Path | None = None
        self._build_ui()

    def _build_ui(self) -> None:
        self.setObjectName("report_config_panel")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 9, 10, 10)
        layout.setSpacing(8)

        title = QLabel("DOSSIER SCIENTIFIQUE")
        title.setObjectName("sectionTitle")
        layout.addWidget(title)

        evidence = QFrame()
        evidence.setObjectName("reportEvidence")
        evidence_layout = QFormLayout(evidence)
        self.source_value = QLabel("Aucune analyse")
        self.method_value = QLabel("—")
        self.channel_value = QLabel("0")
        self.quality_value = QLabel("NON ÉVALUÉE")
        for value in (
            self.source_value,
            self.method_value,
            self.channel_value,
            self.quality_value,
        ):
            value.setObjectName("technicalValue")
            value.setWordWrap(True)
        evidence_layout.addRow("Source", self.source_value)
        evidence_layout.addRow("Méthode", self.method_value)
        evidence_layout.addRow("Voies", self.channel_value)
        evidence_layout.addRow("Qualité", self.quality_value)
        layout.addWidget(evidence)

        metadata_group = QGroupBox("Identification traçable")
        metadata_layout = QFormLayout(metadata_group)
        self.template_edit = QLineEdit("scientific")
        self.template_edit.setVisible(False)
        self.title_edit = QLineEdit("Rapport scientifique CHNeoWave")
        self.test_id_edit = QLineEdit("")
        self.author_edit = QLineEdit("")
        self.version_edit = QLineEdit("1.0")
        self.version_edit.setVisible(False)
        self.date_edit = QDateEdit(QDate.currentDate())
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(90)

        metadata_layout.addRow("Titre", self.title_edit)
        metadata_layout.addRow("Essai / référence", self.test_id_edit)
        metadata_layout.addRow("Opérateur / analyste", self.author_edit)
        metadata_layout.addRow("Date", self.date_edit)
        metadata_layout.addRow("Notes scientifiques", self.description_edit)
        layout.addWidget(metadata_group)

        sections_group = QGroupBox("Preuves incluses")
        sections_layout = QVBoxLayout(sections_group)
        self.include_graphs_check = QCheckBox("Figures spectrales")
        self.include_graphs_check.setChecked(True)
        self.include_quality_check = QCheckBox("Diagnostics et limites d'interprétation")
        self.include_quality_check.setChecked(True)
        self.include_traceability_check = QCheckBox("Méthode, configuration et empreinte SHA-256")
        self.include_traceability_check.setChecked(True)
        sections_layout.addWidget(self.include_graphs_check)
        sections_layout.addWidget(self.include_quality_check)
        sections_layout.addWidget(self.include_traceability_check)
        layout.addWidget(sections_group)

        actions_group = QGroupBox("Production")
        actions_layout = QVBoxLayout(actions_group)
        self.generate_button = QPushButton("RECONSTRUIRE LE DOSSIER")
        self.generate_button.setProperty("kind", "primaryLarge")
        self.generate_button.clicked.connect(self.generate_report)
        actions_layout.addWidget(self.generate_button)

        export_grid = QGridLayout()
        for index, (label, export_type) in enumerate(
            (
                ("PDF", "pdf"),
                ("HTML", "html"),
                ("JSON", "json"),
                ("TXT", "txt"),
            )
        ):
            button = QPushButton(label)
            button.setProperty("kind", "secondary")
            button.clicked.connect(lambda checked=False, kind=export_type: self.export_report(kind))
            export_grid.addWidget(button, index // 2, index % 2)
        actions_layout.addLayout(export_grid)
        layout.addWidget(actions_group)
        layout.addStretch()

    def set_analysis_summary(self, source_file: str | None, results: dict) -> None:
        source_name = Path(source_file).name if source_file else "Aucune analyse"
        configuration = results.get("analysis_configuration", {}) or {}
        metadata = results.get("metadata", {}) or {}
        method = configuration.get("method") or metadata.get("method") or "Welch PSD"
        channel_count = len(results.get("basic_stats", {}) or {})
        quality = results.get("quality", {}) or {}
        warnings = sum(len(item.get("warnings", [])) for item in quality.values())
        decisions = [item.get("engineer_decision", "pending") for item in quality.values()]
        if any(decision == "rejected" for decision in decisions):
            decision_text = "REJET INGÉNIEUR ENREGISTRÉ"
        elif decisions and all(decision == "accepted" for decision in decisions):
            decision_text = "VALIDÉ PAR L’INGÉNIEUR"
        elif quality:
            decision_text = "VALIDATION INGÉNIEUR EN ATTENTE"
        else:
            decision_text = "NON ÉVALUÉ"
        alert_text = f"{warnings} ALERTE" + ("S" if warnings != 1 else "")
        verdict = f"{decision_text} · {alert_text}" if quality else decision_text
        self.source_value.setText(source_name)
        self.method_value.setText(str(method))
        self.channel_value.setText(str(channel_count))
        self.quality_value.setText(verdict)

    def set_default_export_dir(self, export_dir: str) -> None:
        self.default_export_dir = Path(export_dir) if export_dir else None

    def get_report_config(self) -> dict:
        return {
            "template": self.template_edit.text().strip(),
            "title": self.title_edit.text().strip(),
            "test_id": self.test_id_edit.text().strip(),
            "author": self.author_edit.text().strip(),
            "date": self.date_edit.date().toString("yyyy-MM-dd"),
            "version": self.version_edit.text().strip(),
            "description": self.description_edit.toPlainText().strip(),
            "include_graphs": self.include_graphs_check.isChecked(),
            "include_quality": self.include_quality_check.isChecked(),
            "include_traceability": self.include_traceability_check.isChecked(),
        }

    def generate_report(self) -> None:
        config = self.get_report_config()
        self.template_selected.emit(config["template"])
        self.report_generated.emit("standard", config)

    def export_report(self, export_type: str) -> None:
        base_dir = self.default_export_dir if self.default_export_dir else Path.cwd()
        base_dir.mkdir(parents=True, exist_ok=True)
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            f"Exporter en {export_type.upper()}",
            str(base_dir / f"rapport.{export_type}"),
            f"Fichiers {export_type.upper()} (*.{export_type})",
        )
        if file_path:
            self.export_requested.emit(export_type, file_path)


class ReportPreviewArea(QFrame):
    """Zone de previsualisation du rapport."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        self.setObjectName("report_preview_area")
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(14)

        header = QHBoxLayout()
        title = QLabel("Aperçu du livrable")
        title.setObjectName("sectionTitle")
        self.generation_status_label = QLabel("PRÊT")
        self.generation_status_label.setProperty("state", "neutral")
        self.page_count_label = QLabel("1 page")
        self.page_count_label.setObjectName("mutedText")
        header.addWidget(title)
        header.addStretch()
        header.addWidget(self.generation_status_label)
        header.addWidget(self.page_count_label)
        layout.addLayout(header)

        self.report_text = QTextEdit()
        self.report_text.setObjectName("reportDocument")
        self.report_text.setReadOnly(True)
        layout.addWidget(self.report_text)
        self.report_text.setHtml(
            "<h3>Aucun résultat scientifique chargé</h3>"
            "<p>Le dossier sera construit à partir de la source, de la configuration "
            "Welch, des figures, des diagnostics qualité et de l’empreinte de traçabilité.</p>"
        )

    def update_content(self, content: str) -> None:
        self.report_text.setHtml(content)

    def update_status(self, status: str, page_count: int = 1) -> None:
        self.generation_status_label.setText(status)
        self.page_count_label.setText(f"{page_count} page(s)")
        lowered = status.lower()
        state = "success" if "généré" in lowered or "terminé" in lowered else "neutral"
        self.generation_status_label.setProperty("state", state)
        self.generation_status_label.style().unpolish(self.generation_status_label)
        self.generation_status_label.style().polish(self.generation_status_label)


class ReportView(QWidget):
    """Vue principale de generation et d'export de rapports."""

    report_generated = Signal(str, dict)
    report_exported = Signal(str, str)
    template_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_dark_mode = False
        self.current_project_dir: Path | None = None
        self.current_project_metadata: dict[str, object] = {}
        self.current_analysis_payload: dict[str, object] = {}
        self.current_report_config: dict[str, object] = {}
        self.current_report_html = ""
        self.current_report_text = ""

        self._build_ui()
        self._setup_connections()

    def _build_ui(self) -> None:
        self.setObjectName("report_view")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 10)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        self.config_panel = ReportConfigPanel()
        self.preview_area = ReportPreviewArea()
        splitter.addWidget(self.config_panel)
        splitter.addWidget(self.preview_area)
        splitter.setSizes([310, 900])
        layout.addWidget(splitter)

    def _setup_connections(self) -> None:
        self.config_panel.report_generated.connect(self.on_report_generated)
        self.config_panel.template_selected.connect(self.on_template_selected)
        self.config_panel.export_requested.connect(self.on_export_requested)

    def set_project_context(self, project_metadata: dict, project_dir: str) -> None:
        self.current_project_metadata = project_metadata or {}
        self.current_project_dir = Path(project_dir) if project_dir else None
        if self.current_project_dir:
            export_dir = self.current_project_dir / "exports"
            export_dir.mkdir(parents=True, exist_ok=True)
            self.config_panel.set_default_export_dir(str(export_dir))

    def set_analysis_context(
        self, source_file: str, analysis_results: dict, extra_metadata: dict = None
    ) -> None:
        self.current_analysis_payload = {
            "source_file": source_file,
            "analysis_results": analysis_results or {},
            "extra_metadata": extra_metadata or {},
        }
        self.config_panel.set_analysis_summary(source_file, analysis_results or {})
        config = self.config_panel.get_report_config()
        self.on_report_generated("standard", config)

    def on_report_generated(self, report_type: str, config: dict) -> None:
        self.current_report_config = config
        self.current_report_html = self._build_report_html(config)
        self.current_report_text = self._build_report_text()
        self.preview_area.update_content(self.current_report_html)
        self.preview_area.update_status("RAPPORT GÉNÉRÉ", self._estimate_page_count())
        self.report_generated.emit(report_type, config)

    def on_template_selected(self, template: str) -> None:
        self.template_changed.emit(template)

    def on_export_requested(self, export_type: str, filename: str) -> None:
        if not self.current_report_html:
            self.on_report_generated("standard", self.config_panel.get_report_config())

        output_path = Path(filename)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if export_type == "html":
            output_path.write_text(self.current_report_html, encoding="utf-8")
        elif export_type == "txt":
            output_path.write_text(self.current_report_text, encoding="utf-8")
        elif export_type == "json":
            output_path.write_text(
                json.dumps(
                    {
                        "report_config": self.current_report_config,
                        "project_metadata": self.current_project_metadata,
                        "analysis_payload": self._json_ready(self.current_analysis_payload),
                    },
                    indent=2,
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
        elif export_type == "pdf":
            document = QTextDocument()
            document.setHtml(self.current_report_html)
            printer = QPrinter()
            printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
            printer.setOutputFileName(str(output_path))
            printer.setPageOrientation(QPageLayout.Orientation.Landscape)
            print_method = getattr(document, "print_", None) or getattr(document, "print", None)
            if print_method is None:
                raise RuntimeError("Cette version de Qt ne fournit pas l'impression PDF")
            print_method(printer)
        else:
            QMessageBox.warning(self, "Export", f"Format non supporte: {export_type}")
            return

        self.preview_area.update_status("EXPORT TERMINÉ", self._estimate_page_count())
        self.report_exported.emit(export_type, str(output_path))

    def set_theme(self, is_dark: bool) -> None:
        self.is_dark_mode = is_dark

    def load_report_data(self, data_source: str) -> None:
        self.current_analysis_payload["source_file"] = data_source

    def get_current_config(self) -> dict:
        return self.current_report_config

    def set_report_config(self, config: dict) -> None:
        self.current_report_config = config or {}

    def generate_custom_report(self, template: str, sections: list, metadata: dict) -> None:
        config = {
            "template": template,
            "title": metadata.get("title", "Rapport CHNeoWave"),
            "author": metadata.get("author", ""),
            "version": metadata.get("version", "1.0"),
            "date": metadata.get("date", QDate.currentDate().toString("yyyy-MM-dd")),
            "description": metadata.get("description", ""),
            "sections": sections,
        }
        self.on_report_generated("custom", config)

    def _build_report_html(self, config: dict) -> str:
        analysis_results = self.current_analysis_payload.get("analysis_results", {})
        source_file = self.current_analysis_payload.get("source_file")
        include_graphs = config.get("include_graphs", True)
        spectrum_plot = self._spectral_plot_data_uri(analysis_results) if include_graphs else ""
        time_plot = self._time_plot_data_uri(analysis_results) if include_graphs else ""
        return build_scientific_report_html(
            analysis_results,
            source_file,
            self.current_project_metadata,
            config,
            spectral_plot_data_uri=spectrum_plot,
            time_plot_data_uri=time_plot,
        )

    def _build_report_text(self) -> str:
        return build_scientific_report_text(
            self.current_analysis_payload.get("analysis_results", {}),
            self.current_analysis_payload.get("source_file"),
            self.current_project_metadata,
            self.current_report_config,
        )

    @staticmethod
    def _spectral_plot_data_uri(analysis_results: dict) -> str:
        spectra = analysis_results.get("spectral_analysis", {})
        if not spectra:
            return ""
        figure = Figure(figsize=(10, 3.5), tight_layout=True)
        axis = figure.add_subplot(111)
        for channel, spectrum in spectra.items():
            frequencies = np.asarray(spectrum.get("frequencies", []), dtype=float)
            density = np.asarray(spectrum.get("psd", []), dtype=float)
            valid = (frequencies > 0) & np.isfinite(density) & (density > 0)
            if np.any(valid):
                axis.semilogy(frequencies[valid], density[valid], linewidth=1.1, label=channel)
        axis.set_xlabel("Fréquence (Hz)")
        axis.set_ylabel("Densité spectrale")
        axis.grid(True, which="both", color="#DCE5EA", linewidth=0.6)
        axis.legend(loc="best", fontsize=7, frameon=False, ncol=2)
        buffer = io.BytesIO()
        figure.savefig(buffer, format="png", dpi=140, facecolor="white")
        encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
        return f"data:image/png;base64,{encoded}"

    @staticmethod
    def _time_plot_data_uri(analysis_results: dict) -> str:
        previews = analysis_results.get("time_series_preview", {})
        if not previews:
            return ""
        channels = list(previews)
        figure = Figure(figsize=(10, 3.5), tight_layout=True)
        axes = figure.subplots(len(channels), 1, sharex=True, squeeze=False)[:, 0]
        colors = ("#008CAB", "#C97718", "#168262", "#A84652", "#6655B5", "#397FBC")
        for index, (axis, channel) in enumerate(zip(axes, channels, strict=False)):
            preview = previews[channel]
            time_values = np.asarray(preview.get("time_s", []), dtype=float)
            values = np.asarray(preview.get("values", []), dtype=float)
            valid = np.isfinite(time_values) & np.isfinite(values)
            axis.plot(
                time_values[valid],
                values[valid],
                color=colors[index % len(colors)],
                linewidth=0.5,
            )
            axis.set_ylabel(
                f"{channel}  [{preview.get('unit', 'unité')}]",
                fontsize=5.4,
                rotation=0,
                horizontalalignment="right",
                verticalalignment="center",
                labelpad=7,
            )
            axis.grid(True, color="#D6E0E4", linewidth=0.45)
            axis.tick_params(labelsize=6)
            axis.spines["top"].set_visible(False)
            axis.spines["right"].set_visible(False)
        axes[-1].set_xlabel("Temps (s)")
        buffer = io.BytesIO()
        figure.savefig(buffer, format="png", dpi=150, facecolor="white")
        encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
        return f"data:image/png;base64,{encoded}"

    def _estimate_page_count(self) -> int:
        results = self.current_analysis_payload.get("analysis_results", {})
        channel_count = len(results.get("basic_stats", {}))
        page_count = 1 + math.ceil(max(0, channel_count - 1) / 4)
        if results.get("cross_spectral_analysis") or results.get("incident_reflected_analysis"):
            page_count += 1
        if self.current_report_config.get("include_graphs", True) and results.get("spectral_analysis"):
            page_count += 1
        return max(1, page_count)

    def _json_ready(self, value):
        if isinstance(value, dict):
            return {key: self._json_ready(subvalue) for key, subvalue in value.items()}
        if isinstance(value, list):
            return [self._json_ready(item) for item in value]
        if hasattr(value, "tolist"):
            return value.tolist()
        return value
