# -*- coding: utf-8 -*-
"""Vue de generation de rapports CHNeoWave."""

import html
import json
from pathlib import Path
from typing import Dict, Optional

from PySide6.QtCore import Qt, QDate, Signal
from PySide6.QtGui import QTextDocument
from PySide6.QtPrintSupport import QPrinter
from PySide6.QtWidgets import (
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


FIBONACCI_SPACING = [8, 13, 21, 34, 55, 89]
GOLDEN_RATIO = 1.618


class ReportConfigPanel(QFrame):
    """Panneau de configuration du rapport."""

    report_generated = Signal(str, dict)
    template_selected = Signal(str)
    export_requested = Signal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.default_export_dir: Optional[Path] = None
        self._build_ui()

    def _build_ui(self) -> None:
        self.setObjectName("report_config_panel")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(FIBONACCI_SPACING[2], FIBONACCI_SPACING[2], FIBONACCI_SPACING[2], FIBONACCI_SPACING[2])
        layout.setSpacing(FIBONACCI_SPACING[2])

        title = QLabel("Configuration")
        title.setStyleSheet("font-size: 20px; font-weight: 700; color: #0A1929;")
        layout.addWidget(title)

        metadata_group = QGroupBox("Metadonnees")
        metadata_layout = QFormLayout(metadata_group)
        self.template_edit = QLineEdit("Rapport technique")
        self.title_edit = QLineEdit("Rapport CHNeoWave")
        self.author_edit = QLineEdit("")
        self.version_edit = QLineEdit("1.0")
        self.date_edit = QDateEdit(QDate.currentDate())
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(120)

        metadata_layout.addRow("Template:", self.template_edit)
        metadata_layout.addRow("Titre:", self.title_edit)
        metadata_layout.addRow("Auteur:", self.author_edit)
        metadata_layout.addRow("Version:", self.version_edit)
        metadata_layout.addRow("Date:", self.date_edit)
        metadata_layout.addRow("Description:", self.description_edit)
        layout.addWidget(metadata_group)

        actions_group = QGroupBox("Generation et export")
        actions_layout = QVBoxLayout(actions_group)
        self.generate_button = QPushButton("Generer le rapport")
        self.generate_button.clicked.connect(self.generate_report)
        actions_layout.addWidget(self.generate_button)

        export_grid = QGridLayout()
        for index, (label, export_type) in enumerate((
            ("PDF", "pdf"),
            ("HTML", "html"),
            ("JSON", "json"),
            ("TXT", "txt"),
        )):
            button = QPushButton(label)
            button.clicked.connect(lambda checked=False, kind=export_type: self.export_report(kind))
            export_grid.addWidget(button, index // 2, index % 2)
        actions_layout.addLayout(export_grid)
        layout.addWidget(actions_group)
        layout.addStretch()

    def set_default_export_dir(self, export_dir: str) -> None:
        self.default_export_dir = Path(export_dir) if export_dir else None

    def get_report_config(self) -> dict:
        return {
            "template": self.template_edit.text().strip(),
            "title": self.title_edit.text().strip(),
            "author": self.author_edit.text().strip(),
            "date": self.date_edit.date().toString("yyyy-MM-dd"),
            "version": self.version_edit.text().strip(),
            "description": self.description_edit.toPlainText().strip(),
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
        layout.setContentsMargins(FIBONACCI_SPACING[2], FIBONACCI_SPACING[2], FIBONACCI_SPACING[2], FIBONACCI_SPACING[2])
        layout.setSpacing(FIBONACCI_SPACING[2])

        header = QHBoxLayout()
        title = QLabel("Previsualisation")
        title.setStyleSheet("font-size: 22px; font-weight: 700; color: #0A1929;")
        self.generation_status_label = QLabel("Pret")
        self.page_count_label = QLabel("1 page")
        header.addWidget(title)
        header.addStretch()
        header.addWidget(self.generation_status_label)
        header.addWidget(self.page_count_label)
        layout.addLayout(header)

        self.report_text = QTextEdit()
        self.report_text.setReadOnly(True)
        layout.addWidget(self.report_text)

    def update_content(self, content: str) -> None:
        self.report_text.setHtml(content)

    def update_status(self, status: str, page_count: int = 1) -> None:
        self.generation_status_label.setText(status)
        self.page_count_label.setText(f"{page_count} page(s)")


class ReportView(QWidget):
    """Vue principale de generation et d'export de rapports."""

    report_generated = Signal(str, dict)
    report_exported = Signal(str, str)
    template_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_dark_mode = False
        self.current_project_dir: Optional[Path] = None
        self.current_project_metadata: Dict[str, object] = {}
        self.current_analysis_payload: Dict[str, object] = {}
        self.current_report_config: Dict[str, object] = {}
        self.current_report_html = ""
        self.current_report_text = ""

        self._build_ui()
        self._setup_connections()

    def _build_ui(self) -> None:
        self.setObjectName("report_view")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        self.config_panel = ReportConfigPanel()
        self.preview_area = ReportPreviewArea()
        splitter.addWidget(self.config_panel)
        splitter.addWidget(self.preview_area)
        splitter.setSizes([int(280 * GOLDEN_RATIO), int(450 * GOLDEN_RATIO)])
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

    def set_analysis_context(self, source_file: str, analysis_results: dict, extra_metadata: dict = None) -> None:
        self.current_analysis_payload = {
            "source_file": source_file,
            "analysis_results": analysis_results or {},
            "extra_metadata": extra_metadata or {},
        }
        config = self.current_report_config or self.config_panel.get_report_config()
        self.on_report_generated("standard", config)

    def on_report_generated(self, report_type: str, config: dict) -> None:
        self.current_report_config = config
        self.current_report_html = self._build_report_html(config)
        self.current_report_text = self._build_report_text()
        self.preview_area.update_content(self.current_report_html)
        self.preview_area.update_status("Rapport genere", self._estimate_page_count())
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
            document.print(printer)
        else:
            QMessageBox.warning(self, "Export", f"Format non supporte: {export_type}")
            return

        self.preview_area.update_status("Export termine", self._estimate_page_count())
        self.report_exported.emit(export_type, str(output_path))

    def set_theme(self, is_dark: bool) -> None:
        self.is_dark_mode = is_dark
        if is_dark:
            self.setStyleSheet("QWidget#report_view { background-color: #0A1929; color: #F5FBFF; }")
        else:
            self.setStyleSheet("QWidget#report_view { background-color: #F5FBFF; color: #0A1929; }")

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
        source_file = self.current_analysis_payload.get("source_file") or "Non defini"
        basic_stats = analysis_results.get("basic_stats", {})
        goda_metrics = analysis_results.get("goda_metrics", {})

        project_name = self.current_project_metadata.get("name", "CHNeoWave")
        title = config.get("title") or f"Rapport {project_name}"
        author = config.get("author") or self.current_project_metadata.get("manager", "")
        description = config.get("description") or self.current_project_metadata.get("description", "")

        rows = []
        for channel, stats in basic_stats.items():
            rows.append(
                "<tr>"
                f"<td>{html.escape(channel)}</td>"
                f"<td>{stats.get('mean', 0):.6f}</td>"
                f"<td>{stats.get('std', 0):.6f}</td>"
                f"<td>{stats.get('min', 0):.6f}</td>"
                f"<td>{stats.get('max', 0):.6f}</td>"
                "</tr>"
            )

        goda_items = []
        for channel, metrics in goda_metrics.items():
            goda_items.append(
                f"<li><strong>{html.escape(channel)}</strong> - "
                f"Hs={metrics.get('Hs', 0):.6f}, "
                f"Tp={metrics.get('Tp', 0):.6f}, "
                f"Hmax={metrics.get('H_max', 0):.6f}</li>"
            )

        return f"""
<html>
  <body style="font-family: Segoe UI, Arial, sans-serif; color: #102030; line-height: 1.5;">
    <h1>{html.escape(title)}</h1>
    <p><strong>Projet:</strong> {html.escape(str(project_name))}</p>
    <p><strong>Auteur:</strong> {html.escape(str(author))}</p>
    <p><strong>Source:</strong> {html.escape(str(source_file))}</p>
    <p>{html.escape(str(description))}</p>
    <h2>Statistiques</h2>
    <table border="1" cellspacing="0" cellpadding="6" style="border-collapse: collapse; width: 100%;">
      <tr>
        <th>Canal</th>
        <th>Moyenne</th>
        <th>Ecart-type</th>
        <th>Min</th>
        <th>Max</th>
      </tr>
      {''.join(rows) if rows else '<tr><td colspan="5">Aucune statistique disponible</td></tr>'}
    </table>
    <h2>Metriques Goda</h2>
    <ul>
      {''.join(goda_items) if goda_items else '<li>Aucune metrique disponible</li>'}
    </ul>
    <h2>Configuration</h2>
    <pre>{html.escape(json.dumps(config, indent=2, ensure_ascii=False))}</pre>
  </body>
</html>
"""

    def _build_report_text(self) -> str:
        analysis_results = self.current_analysis_payload.get("analysis_results", {})
        source_file = self.current_analysis_payload.get("source_file") or "Non defini"
        basic_stats = analysis_results.get("basic_stats", {})
        goda_metrics = analysis_results.get("goda_metrics", {})

        lines = [
            "Rapport CHNeoWave",
            f"Projet: {self.current_project_metadata.get('name', 'CHNeoWave')}",
            f"Source: {source_file}",
            "",
            "Statistiques",
        ]

        for channel, stats in basic_stats.items():
            lines.append(f"- {channel}")
            lines.append(f"  moyenne: {stats.get('mean', 0):.6f}")
            lines.append(f"  ecart-type: {stats.get('std', 0):.6f}")
            lines.append(f"  min/max: {stats.get('min', 0):.6f} / {stats.get('max', 0):.6f}")

        lines.append("")
        lines.append("Metriques Goda")
        for channel, metrics in goda_metrics.items():
            lines.append(
                f"- {channel}: Hs={metrics.get('Hs', 0):.6f}, "
                f"Tp={metrics.get('Tp', 0):.6f}, Hmax={metrics.get('H_max', 0):.6f}"
            )

        return "\n".join(lines).strip()

    def _estimate_page_count(self) -> int:
        return max(1, (len(self.current_report_text.splitlines()) // 40) + 1)

    def _json_ready(self, value):
        if isinstance(value, dict):
            return {key: self._json_ready(subvalue) for key, subvalue in value.items()}
        if isinstance(value, list):
            return [self._json_ready(item) for item in value]
        if hasattr(value, "tolist"):
            return value.tolist()
        return value
