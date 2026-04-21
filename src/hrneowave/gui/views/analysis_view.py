# -*- coding: utf-8 -*-
"""Vue d'analyse CHNeoWave."""

from pathlib import Path
from typing import Dict, Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QHeaderView,
)

from ...core.post_processor import PostProcessor


FIBONACCI_SPACING = [8, 13, 21, 34, 55, 89]
GOLDEN_RATIO = 1.618


class AnalysisToolsPanel(QFrame):
    """Panneau d'outils pour le chargement et l'analyse."""

    analysis_requested = Signal(str, dict)
    filter_applied = Signal(str, dict)
    export_requested = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self) -> None:
        self.setObjectName("analysis_tools_panel")
        self.setMinimumWidth(320)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(FIBONACCI_SPACING[2], FIBONACCI_SPACING[2], FIBONACCI_SPACING[2], FIBONACCI_SPACING[2])
        layout.setSpacing(FIBONACCI_SPACING[2])

        title = QLabel("Outils d'analyse")
        title.setStyleSheet("font-size: 20px; font-weight: 700; color: #0A1929;")
        layout.addWidget(title)

        files_group = QGroupBox("Fichiers de donnees")
        files_layout = QVBoxLayout(files_group)
        self.data_list = QListWidget()
        self.load_button = QPushButton("Charger")
        self.refresh_button = QPushButton("Actualiser")

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.load_button)
        buttons_layout.addWidget(self.refresh_button)
        files_layout.addWidget(self.data_list)
        files_layout.addLayout(buttons_layout)
        layout.addWidget(files_group)

        analysis_group = QGroupBox("Analyses")
        analysis_layout = QVBoxLayout(analysis_group)
        self.analysis_type_combo = QComboBox()
        self.analysis_type_combo.addItems([
            "statistics",
            "spectral",
            "temporal",
            "correlation",
        ])
        self.run_button = QPushButton("Lancer l'analyse")
        self.run_button.clicked.connect(self._emit_analysis_request)
        analysis_layout.addWidget(self.analysis_type_combo)
        analysis_layout.addWidget(self.run_button)
        layout.addWidget(analysis_group)

        export_group = QGroupBox("Exports")
        export_layout = QVBoxLayout(export_group)
        for label, export_type in (
            ("Export CSV", "csv"),
            ("Export JSON", "json"),
            ("Export HDF5", "hdf5"),
            ("Rapport TXT", "txt"),
        ):
            button = QPushButton(label)
            button.clicked.connect(lambda checked=False, kind=export_type: self.export_requested.emit(kind))
            export_layout.addWidget(button)
        layout.addWidget(export_group)
        layout.addStretch()

        self.setStyleSheet("""
            QFrame#analysis_tools_panel {
                background-color: #F5FBFF;
                border-right: 1px solid #D7E3EE;
            }
            QGroupBox {
                font-weight: 600;
            }
            QPushButton {
                min-height: 34px;
            }
        """)

    def _emit_analysis_request(self) -> None:
        self.analysis_requested.emit(self.analysis_type_combo.currentText(), {})


class AnalysisResultsArea(QFrame):
    """Zone d'affichage des resultats."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self) -> None:
        self.setObjectName("analysis_results_area")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(FIBONACCI_SPACING[2], FIBONACCI_SPACING[2], FIBONACCI_SPACING[2], FIBONACCI_SPACING[2])
        layout.setSpacing(FIBONACCI_SPACING[2])

        header_layout = QHBoxLayout()
        title = QLabel("Resultats d'analyse")
        title.setStyleSheet("font-size: 22px; font-weight: 700; color: #0A1929;")
        self.analysis_status_label = QLabel("Pret")
        self.analysis_count_label = QLabel("0 analyses")
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(self.analysis_status_label)
        header_layout.addWidget(self.analysis_count_label)
        layout.addLayout(header_layout)

        self.tab_widget = QTabWidget()

        self.stats_table = QTableWidget()
        self.stats_table.verticalHeader().setVisible(False)
        self.stats_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tab_widget.addTab(self.stats_table, "Statistiques")

        self.report_text = QTextEdit()
        self.report_text.setReadOnly(True)
        self.tab_widget.addTab(self.report_text, "Rapport")

        layout.addWidget(self.tab_widget)

        self.setStyleSheet("""
            QFrame#analysis_results_area {
                background-color: white;
            }
        """)

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
        self.current_project_dir: Optional[Path] = None
        self.current_project_metadata: Dict[str, object] = {}
        self.current_data_file: Optional[str] = None
        self.current_analysis_result: Optional[Dict[str, object]] = None

        self._build_ui()
        self._setup_connections()

    def _build_ui(self) -> None:
        self.setObjectName("analysis_view")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        self.tools_panel = AnalysisToolsPanel()
        self.results_area = AnalysisResultsArea()
        splitter.addWidget(self.tools_panel)
        splitter.addWidget(self.results_area)
        splitter.setSizes([int(280 * GOLDEN_RATIO), int(450 * GOLDEN_RATIO)])
        layout.addWidget(splitter)

    def _setup_connections(self) -> None:
        self.tools_panel.analysis_requested.connect(self.on_analysis_requested)
        self.tools_panel.filter_applied.connect(self.on_filter_applied)
        self.tools_panel.export_requested.connect(self.on_export_requested)
        self.tools_panel.load_button.clicked.connect(self._load_selected_or_dialog)
        self.tools_panel.refresh_button.clicked.connect(self.refresh_project_files)
        self.tools_panel.data_list.itemDoubleClicked.connect(self._load_item_from_list)

    def set_project_context(self, project_metadata: dict, project_dir: str) -> None:
        self.current_project_metadata = project_metadata or {}
        self.current_project_dir = Path(project_dir) if project_dir else None
        self.refresh_project_files()

    def refresh_project_files(self) -> None:
        self.tools_panel.data_list.clear()
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
        self.results_area.update_analysis_status(f"Fichier charge: {Path(file_path).name}", self.analysis_count)
        return True

    def on_analysis_requested(self, analysis_type: str, params: dict) -> None:
        if self.post_processor.current_data is None:
            QMessageBox.warning(self, "Analyse", "Aucun fichier de donnees n'est charge.")
            return

        self.analysis_count += 1
        self.results_area.update_analysis_status("Analyse en cours...", self.analysis_count)

        if not self.post_processor.run_analysis():
            self.analysis_count -= 1
            self.results_area.update_analysis_status("Echec analyse", self.analysis_count)
            QMessageBox.warning(self, "Analyse", "Le post-traitement a echoue.")
            return

        self.current_analysis_result = self.post_processor.current_analysis
        self._update_results_views()
        self.results_area.update_analysis_status("Analyse terminee", self.analysis_count)
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
        default_path = self._get_default_export_directory() / f"analysis_results.{suffix_map.get(export_type, export_type)}"

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
        self.is_dark_mode = is_dark
        if is_dark:
            self.setStyleSheet("QWidget#analysis_view { background-color: #0A1929; color: #F5FBFF; }")
        else:
            self.setStyleSheet("QWidget#analysis_view { background-color: #F5FBFF; color: #0A1929; }")

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
        self.results_area.report_text.clear()
        self.results_area.update_analysis_status("Pret", 0)

    def _load_selected_or_dialog(self) -> None:
        item = self.tools_panel.data_list.currentItem()
        if item and item.data(Qt.ItemDataRole.UserRole):
            self.load_data_file(item.data(Qt.ItemDataRole.UserRole))
            return
        self.open_file_dialog()

    def _load_item_from_list(self, item: QListWidgetItem) -> None:
        file_path = item.data(Qt.ItemDataRole.UserRole)
        if file_path:
            self.load_data_file(file_path)

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

    def _find_file_item(self, file_path: str) -> Optional[QListWidgetItem]:
        target = str(Path(file_path))
        for index in range(self.tools_panel.data_list.count()):
            item = self.tools_panel.data_list.item(index)
            if item.data(Qt.ItemDataRole.UserRole) == target:
                return item
        return None

    def _add_or_select_file_item(self, file_path: str, select: bool = True) -> None:
        target = str(Path(file_path))
        item = self._find_file_item(target)
        if item is None:
            item = QListWidgetItem(Path(target).name)
            item.setData(Qt.ItemDataRole.UserRole, target)
            self.tools_panel.data_list.addItem(item)
        if select:
            self.tools_panel.data_list.setCurrentItem(item)

    def _update_results_views(self) -> None:
        results = self.current_analysis_result or {}
        basic_stats = results.get("basic_stats", {})
        channels = list(basic_stats.keys())
        metrics = ["mean", "std", "min", "max", "rms", "skewness", "kurtosis"]

        self.results_area.stats_table.clearContents()
        self.results_area.stats_table.setColumnCount(len(channels) + 1)
        self.results_area.stats_table.setHorizontalHeaderLabels(["Parametre"] + channels)
        self.results_area.stats_table.setRowCount(len(metrics))

        for row, metric in enumerate(metrics):
            self.results_area.stats_table.setItem(row, 0, QTableWidgetItem(metric))
            for col, channel in enumerate(channels, start=1):
                value = basic_stats.get(channel, {}).get(metric, "")
                if isinstance(value, float):
                    value = f"{value:.6f}"
                self.results_area.stats_table.setItem(row, col, QTableWidgetItem(str(value)))

        self.results_area.report_text.setPlainText(self._build_report_text())

    def _build_report_text(self) -> str:
        results = self.current_analysis_result or {}
        basic_stats = results.get("basic_stats", {})
        spectral = results.get("spectral_analysis", {})
        goda = results.get("goda_metrics", {})

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
            if channel in goda:
                lines.append(f"  Hs: {goda[channel].get('Hs', 0):.6f}")
                lines.append(f"  Tp: {goda[channel].get('Tp', 0):.6f}")
            lines.append("")

        return "\n".join(lines).strip()
