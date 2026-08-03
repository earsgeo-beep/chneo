"""Vue de generation de rapports CHNeoWave."""

import html
import json
from pathlib import Path

from PySide6.QtCore import QDate, Qt, Signal
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
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(14)

        title = QLabel("Composition du rapport")
        title.setObjectName("sectionTitle")
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
        self.generate_button = QPushButton("Générer le rapport")
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
        layout.setContentsMargins(20, 20, 20, 20)

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
        config = self.current_report_config or self.config_panel.get_report_config()
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
            document.print(printer)
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
        source_file = self.current_analysis_payload.get("source_file") or "Non defini"
        basic_stats = analysis_results.get("basic_stats", {})
        wave_parameters = analysis_results.get("wave_parameters", {})
        quality = analysis_results.get("quality", {})

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

        wave_items = []
        for channel, metrics in wave_parameters.items():
            wave_items.append(
                f"<li><strong>{html.escape(channel)}</strong> - "
                f"H1/3={metrics.get('H1_3', 0):.6f}, "
                f"Hm0={metrics.get('Hm0', 0):.6f}, "
                f"Tp={metrics.get('Tp', 0):.6f}, "
                f"Tm02={metrics.get('Tm02', 0):.6f}, "
                f"Hmax={metrics.get('H_max', 0):.6f}</li>"
            )

        quality_items = []
        for channel, indicators in quality.items():
            warnings = indicators.get("warnings", [])
            state = "Valide" if not warnings else "; ".join(map(str, warnings))
            quality_items.append(f"<li><strong>{html.escape(channel)}</strong> - {html.escape(state)}</li>")

        section_style = (
            "font-size: 16px; color: #203843; border-bottom: 1px solid #DCE5EA; padding-bottom: 6px"
        )
        spaced_section_style = f"{section_style}; margin-top: 24px"
        table_style = "border-collapse: collapse; width: 100%; border: 1px solid #DCE5EA"
        config_style = "background-color: #F5F8F9; border: 1px solid #DCE5EA; padding: 12px"
        config_text = html.escape(json.dumps(config, indent=2, ensure_ascii=False))

        return f"""
<html>
  <body style="font-family: 'Segoe UI', Arial, sans-serif; color: #172B35; line-height: 1.45; margin: 32px;">
    <div style="border-bottom: 3px solid #1A7188; padding-bottom: 14px; margin-bottom: 20px;">
      <p style="color: #1A7188; font-size: 10px; font-weight: 700; letter-spacing: 1px; margin: 0;">
        CHNEOWAVE · RAPPORT TECHNIQUE
      </p>
      <h1 style="font-size: 25px; font-weight: 650; margin: 5px 0 8px 0;">{html.escape(title)}</h1>
      <p style="color: #667C88; margin: 0;">{html.escape(str(description))}</p>
    </div>
    <table cellspacing="0" cellpadding="5" style="width: 100%; color: #405965; margin-bottom: 22px;">
      <tr><td><strong>Projet</strong></td><td>{html.escape(str(project_name))}</td></tr>
      <tr><td><strong>Auteur</strong></td><td>{html.escape(str(author))}</td></tr>
      <tr><td><strong>Source</strong></td><td>{html.escape(str(source_file))}</td></tr>
      <tr><td><strong>Date</strong></td><td>{html.escape(str(config.get("date", "")))}</td></tr>
    </table>
    <h2 style="{section_style};">Statistiques</h2>
    <table cellspacing="0" cellpadding="7" style="{table_style};">
      <tr style="background-color: #EEF3F5; color: #304A56;">
        <th>Canal</th><th>Moyenne</th><th>Écart-type</th><th>Min</th><th>Max</th>
      </tr>
      {"".join(rows) if rows else '<tr><td colspan="5">Aucune statistique disponible</td></tr>'}
    </table>
    <h2 style="{spaced_section_style};">Paramètres de houle</h2>
    <ul>{"".join(wave_items) if wave_items else "<li>Aucun paramètre disponible</li>"}</ul>
    <h2 style="{spaced_section_style};">Qualité de l'analyse</h2>
    <ul>{"".join(quality_items) if quality_items else "<li>Aucun indicateur disponible</li>"}</ul>
    <h2 style="{spaced_section_style};">Configuration scientifique</h2>
    <pre style="{config_style}; color: #405965;">{config_text}</pre>
  </body>
</html>
"""

    def _build_report_text(self) -> str:
        analysis_results = self.current_analysis_payload.get("analysis_results", {})
        source_file = self.current_analysis_payload.get("source_file") or "Non defini"
        basic_stats = analysis_results.get("basic_stats", {})
        wave_parameters = analysis_results.get("wave_parameters", {})
        quality = analysis_results.get("quality", {})

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
        lines.append("Parametres de houle")
        for channel, metrics in wave_parameters.items():
            lines.append(
                f"- {channel}: H1/3={metrics.get('H1_3', 0):.6f}, "
                f"Hm0={metrics.get('Hm0', 0):.6f}, "
                f"Tp={metrics.get('Tp', 0):.6f}, "
                f"Tm02={metrics.get('Tm02', 0):.6f}, "
                f"Hmax={metrics.get('H_max', 0):.6f}"
            )

        lines.append("")
        lines.append("Qualite de l'analyse")
        for channel, indicators in quality.items():
            warnings = indicators.get("warnings", [])
            state = "Valide" if not warnings else "; ".join(map(str, warnings))
            lines.append(f"- {channel}: {state}")

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
