#!/usr/bin/env python3
"""Vue de configuration et de pilotage de l'acquisition."""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QProgressBar,
    QPushButton,
    QSpinBox,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ...acquisition.acquisition_controller import AcquisitionController, create_default_maritime_config

logger = logging.getLogger(__name__)


class AcquisitionConfigView(QWidget):
    """Vue principale d'acquisition avec exports reels."""

    data_exported = Signal(str)
    calibration_completed = Signal(dict)
    data_block_received = Signal(object, object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.controller: AcquisitionController | None = None
        self.update_timer = QTimer(self)
        self.project_metadata: dict[str, Any] = {}
        self.project_dir: Path | None = None

        self._build_ui()
        self._setup_connections()
        self.initialize_controller()

    def _build_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(14)
        main_layout.addWidget(self._create_header())

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self._create_config_panel())
        splitter.addWidget(self._create_monitor_panel())
        splitter.setSizes([760, 420])
        main_layout.addWidget(splitter)

    def _create_header(self) -> QWidget:
        frame = QFrame()
        frame.setObjectName("operationalHeader")
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(18, 12, 18, 12)

        title_layout = QVBoxLayout()
        title = QLabel("MCC USB-1608FS · 8 voies analogiques")
        title.setObjectName("sectionTitle")
        subtitle = QLabel("Session locale continue avec contrôle de traçabilité HDF5")
        subtitle.setObjectName("mutedText")
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)
        layout.addLayout(title_layout)
        layout.addStretch()

        self.hardware_status_label = QLabel("VÉRIFICATION")
        self.hardware_status_label.setProperty("state", "warning")
        layout.addWidget(self.hardware_status_label)
        return frame

    def _create_config_panel(self) -> QWidget:
        widget = QWidget()
        widget.setObjectName("contentCanvas")
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 14, 0)

        tabs = QTabWidget()
        tabs.addTab(self._create_hardware_tab(), "Materiel")
        tabs.addTab(self._create_channels_tab(), "Canaux")
        tabs.addTab(self._create_acquisition_tab(), "Acquisition")
        layout.addWidget(tabs)

        buttons_layout = QHBoxLayout()
        self.load_config_btn = QPushButton("Charger config")
        self.save_config_btn = QPushButton("Sauver config")
        self.reset_config_btn = QPushButton("Reset")
        self.test_connection_btn = QPushButton("Test connexion")
        for button in (
            self.load_config_btn,
            self.save_config_btn,
            self.reset_config_btn,
            self.test_connection_btn,
        ):
            button.setProperty("kind", "secondary")
        buttons_layout.addWidget(self.load_config_btn)
        buttons_layout.addWidget(self.save_config_btn)
        buttons_layout.addWidget(self.reset_config_btn)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.test_connection_btn)
        layout.addLayout(buttons_layout)
        return widget

    def _create_hardware_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)

        detection_group = QGroupBox("Detection du materiel")
        detection_layout = QFormLayout(detection_group)
        self.board_combo = QComboBox()
        self.scan_boards_btn = QPushButton("Scanner les cartes")
        self.scan_boards_btn.setProperty("kind", "secondary")
        detection_layout.addRow("Carte selectionnee:", self.board_combo)
        detection_layout.addRow("", self.scan_boards_btn)

        info_group = QGroupBox("Informations carte")
        info_layout = QFormLayout(info_group)
        self.board_name_label = QLabel("Non detectee")
        self.dll_path_label = QLabel("Non trouve")
        self.version_label = QLabel("Inconnue")
        info_layout.addRow("Nom:", self.board_name_label)
        info_layout.addRow("DLL:", self.dll_path_label)
        info_layout.addRow("Version:", self.version_label)

        layout.addWidget(detection_group)
        layout.addWidget(info_group)
        layout.addStretch()
        return widget

    def _create_channels_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)

        actions = QHBoxLayout()
        self.load_preset_btn = QPushButton("Preset maritime")
        self.clear_channels_btn = QPushButton("Effacer")
        self.load_preset_btn.setProperty("kind", "secondary")
        self.clear_channels_btn.setProperty("kind", "quiet")
        actions.addWidget(self.load_preset_btn)
        actions.addWidget(self.clear_channels_btn)
        actions.addStretch()
        layout.addLayout(actions)

        self.channels_table = QTableWidget(8, 7)
        self.channels_table.setHorizontalHeaderLabels(
            [
                "Canal",
                "Actif",
                "Type capteur",
                "Etiquette",
                "Plage",
                "Sensibilite",
                "Unites",
            ]
        )
        self.channels_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._initialize_channels_table()
        layout.addWidget(self.channels_table)
        return widget

    def _create_acquisition_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)

        params_group = QGroupBox("Parametres d'acquisition")
        params_layout = QFormLayout(params_group)
        self.sampling_rate_spin = QDoubleSpinBox()
        # Le USB-1608FS classique scanne toujours huit canaux et accepte au
        # maximum 100 kS/s agreges, soit 12.5 kS/s par canal.
        self.sampling_rate_spin.setRange(1.0, 12500.0)
        self.sampling_rate_spin.setValue(1000.0)
        self.sampling_rate_spin.setSuffix(" Hz")
        self.duration_spin = QDoubleSpinBox()
        self.duration_spin.setRange(0.1, 3600.0)
        self.duration_spin.setValue(60.0)
        self.duration_spin.setSuffix(" s")
        self.continuous_check = QCheckBox("Acquisition continue")
        self.buffer_size_spin = QSpinBox()
        self.buffer_size_spin.setRange(1000, 100000)
        self.buffer_size_spin.setValue(10000)
        self.buffer_size_spin.setSuffix(" echantillons")
        params_layout.addRow("Frequence:", self.sampling_rate_spin)
        params_layout.addRow("Duree:", self.duration_spin)
        params_layout.addRow("", self.continuous_check)
        params_layout.addRow("Taille buffer:", self.buffer_size_spin)
        layout.addWidget(params_group)

        controls_group = QGroupBox("Controles")
        controls_layout = QHBoxLayout(controls_group)
        self.start_acquisition_btn = QPushButton("Demarrer")
        self.start_acquisition_btn.setText("Démarrer l'acquisition")
        self.start_acquisition_btn.setProperty("kind", "primaryLarge")
        self.stop_acquisition_btn = QPushButton("Arreter")
        self.stop_acquisition_btn.setText("Arrêter")
        self.stop_acquisition_btn.setProperty("kind", "danger")
        self.stop_acquisition_btn.setEnabled(False)
        self.test_acquisition_btn = QPushButton("Test rapide")
        self.calibrate_btn = QPushButton("Calibration")
        self.test_acquisition_btn.setProperty("kind", "secondary")
        self.calibrate_btn.setProperty("kind", "secondary")
        controls_layout.addWidget(self.start_acquisition_btn)
        controls_layout.addWidget(self.stop_acquisition_btn)
        controls_layout.addStretch()
        controls_layout.addWidget(self.test_acquisition_btn)
        controls_layout.addWidget(self.calibrate_btn)
        layout.addWidget(controls_group)

        project_group = QGroupBox("Projet et export")
        project_layout = QFormLayout(project_group)
        self.project_name_edit = QLineEdit("Acquisition_Maritime")
        project_layout.addRow("Nom du projet:", self.project_name_edit)
        export_layout = QHBoxLayout()
        self.export_csv_btn = QPushButton("CSV")
        self.export_json_btn = QPushButton("JSON")
        self.export_hdf5_btn = QPushButton("HDF5")
        for button in (self.export_csv_btn, self.export_json_btn, self.export_hdf5_btn):
            button.setProperty("kind", "secondary")
        export_layout.addWidget(self.export_csv_btn)
        export_layout.addWidget(self.export_json_btn)
        export_layout.addWidget(self.export_hdf5_btn)
        export_layout.addStretch()
        project_layout.addRow("Export:", export_layout)
        layout.addWidget(project_group)
        layout.addStretch()

        return widget

    def _create_monitor_panel(self) -> QWidget:
        widget = QFrame()
        widget.setObjectName("surface")
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)

        status_group = QGroupBox("Statut acquisition")
        status_layout = QFormLayout(status_group)
        self.acquisition_status_label = QLabel("Arretee")
        self.samples_count_label = QLabel("0")
        self.acquisition_rate_label = QLabel("0.0 Hz")
        self.errors_count_label = QLabel("0")
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        status_layout.addRow("Statut:", self.acquisition_status_label)
        status_layout.addRow("Echantillons:", self.samples_count_label)
        status_layout.addRow("Taux reel:", self.acquisition_rate_label)
        status_layout.addRow("Erreurs:", self.errors_count_label)
        status_layout.addRow("Progression:", self.progress_bar)
        layout.addWidget(status_group)

        log_group = QGroupBox("Journal")
        log_layout = QVBoxLayout(log_group)
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(220)
        clear_log_btn = QPushButton("Effacer le journal")
        clear_log_btn.setProperty("kind", "quiet")
        clear_log_btn.clicked.connect(self.clear_log)
        log_layout.addWidget(self.log_text)
        log_layout.addWidget(clear_log_btn)
        layout.addWidget(log_group)

        data_group = QGroupBox("Apercu temps reel")
        data_layout = QVBoxLayout(data_group)
        self.data_table = QTableWidget(0, 3)
        self.data_table.setHorizontalHeaderLabels(["Canal", "Valeur", "Unite"])
        self.data_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        data_layout.addWidget(self.data_table)
        layout.addWidget(data_group)
        return widget

    def _setup_connections(self) -> None:
        self.scan_boards_btn.clicked.connect(self.scan_boards)
        self.test_connection_btn.clicked.connect(self.test_connection)
        self.load_preset_btn.clicked.connect(self.load_maritime_preset)
        self.clear_channels_btn.clicked.connect(self.clear_channels)
        self.load_config_btn.clicked.connect(self.load_configuration)
        self.save_config_btn.clicked.connect(self.save_configuration)
        self.reset_config_btn.clicked.connect(self.reset_configuration)
        self.start_acquisition_btn.clicked.connect(self.start_acquisition)
        self.stop_acquisition_btn.clicked.connect(self.stop_acquisition)
        self.test_acquisition_btn.clicked.connect(self.test_acquisition)
        self.calibrate_btn.clicked.connect(self.calibrate_system)
        self.export_csv_btn.clicked.connect(self.export_csv)
        self.export_json_btn.clicked.connect(self.export_json)
        self.export_hdf5_btn.clicked.connect(self.export_hdf5)
        self.update_timer.timeout.connect(self.update_display)
        self.data_block_received.connect(self._display_received_data)
        self.update_timer.start(1000)

    def _initialize_channels_table(self) -> None:
        sensor_types = ["wave_height", "pressure", "accelerometer", "temperature", "generic"]
        voltage_ranges = ["±1V", "±2V", "±5V", "±10V"]

        for row in range(8):
            channel_item = QTableWidgetItem(str(row))
            channel_item.setFlags(Qt.ItemIsEnabled)
            self.channels_table.setItem(row, 0, channel_item)

            enabled = QCheckBox()
            enabled.setChecked(row < 4)
            self.channels_table.setCellWidget(row, 1, enabled)

            sensor_combo = QComboBox()
            sensor_combo.addItems(sensor_types)
            sensor_combo.setCurrentText(
                sensor_types[min(row, len(sensor_types) - 1)] if row < len(sensor_types) else "generic"
            )
            self.channels_table.setCellWidget(row, 2, sensor_combo)

            self.channels_table.setItem(row, 3, QTableWidgetItem(f"Canal {row}"))

            range_combo = QComboBox()
            range_combo.addItems(voltage_ranges)
            range_combo.setCurrentText("±10V")
            self.channels_table.setCellWidget(row, 4, range_combo)

            self.channels_table.setItem(row, 5, QTableWidgetItem("1.0"))
            self.channels_table.setItem(row, 6, QTableWidgetItem("V"))

    def initialize_controller(self) -> None:
        try:
            self.controller = AcquisitionController(
                self.data_received_callback,
                auto_initialize=False,
            )
            self.log_message("Controleur prêt - cliquez sur Scanner les cartes")
            self.board_combo.clear()
            self.board_combo.addItem("Scan matériel non lancé")
            self.board_name_label.setText("En attente du scan")
            self.update_hardware_status()
        except Exception as exc:
            self.log_message(f"Erreur d'initialisation: {exc}")

    def set_project_context(self, project_metadata: dict[str, Any], project_dir: str | None = None) -> None:
        self.project_metadata = project_metadata or {}
        self.project_dir = Path(project_dir) if project_dir else None
        project_name = self.project_metadata.get("name") or self.project_metadata.get("project_name")
        if project_name:
            self.project_name_edit.setText(str(project_name))
            self.log_message(f"Projet actif: {project_name}")

    def scan_boards(self) -> None:
        if not self.controller:
            return
        self.scan_boards_btn.setEnabled(False)
        self.hardware_status_label.setText("DÉTECTION USB...")
        self.log_message("Scan USB direct MCC DAQ (sans InstaCal)...")
        try:
            connected = self.controller.refresh_hardware()
            boards = self.controller.get_available_boards()
            self.board_combo.clear()
            if connected and boards:
                for board in boards:
                    self.board_combo.addItem(f"Carte {board}")
                board_name = getattr(self.controller.daq, "board_name", "USB-1608FS")
                self.board_name_label.setText(str(board_name))
                self.log_message(f"Carte MCC connectée directement: {board_name}")
            else:
                self.board_combo.addItem("Aucune USB-1608FS détectée")
                self.board_name_label.setText("Mode simulation")
                self.log_message("Aucune USB-1608FS détectée - simulation disponible")
        except Exception as exc:
            logger.exception("Scan MCC impossible")
            self.board_combo.clear()
            self.board_combo.addItem("Erreur de détection")
            self.board_name_label.setText("Consultez chneowave_debug.log")
            self.log_message(f"Erreur de détection MCC: {exc}")
        finally:
            self.scan_boards_btn.setEnabled(True)
            self.update_hardware_status()

    def update_hardware_status(self) -> None:
        if self.controller and self.controller.is_hardware_available():
            self.hardware_status_label.setText("MATÉRIEL OPÉRATIONNEL")
            self.hardware_status_label.setProperty("state", "success")
        else:
            self.hardware_status_label.setText("MODE SIMULATION")
            self.hardware_status_label.setProperty("state", "warning")
        self.hardware_status_label.style().unpolish(self.hardware_status_label)
        self.hardware_status_label.style().polish(self.hardware_status_label)

    def test_connection(self) -> None:
        if not self.controller:
            self.log_message("Pas de controleur disponible")
            return
        if self.controller.is_hardware_available():
            self.log_message("Connexion materielle OK")
        else:
            self.log_message("Materiel non detecte - simulation active")

    def load_maritime_preset(self) -> None:
        if not self.controller:
            return

        default_config = create_default_maritime_config()
        for row, (_, config) in enumerate(default_config.items()):
            if row >= self.channels_table.rowCount():
                break
            self.controller.configure_maritime_channel(
                config.channel,
                config.sensor_type,
                config.label,
                10.0,
                config.sensor_sensitivity,
                config.physical_units,
            )

            enabled = self.channels_table.cellWidget(row, 1)
            sensor_combo = self.channels_table.cellWidget(row, 2)
            self.channels_table.setItem(row, 3, QTableWidgetItem(config.label))
            self.channels_table.setItem(row, 5, QTableWidgetItem(str(config.sensor_sensitivity)))
            self.channels_table.setItem(row, 6, QTableWidgetItem(config.physical_units))
            if enabled:
                enabled.setChecked(config.enabled)
            if sensor_combo:
                sensor_combo.setCurrentText(config.sensor_type)

        self.log_message("Preset maritime charge")

    def clear_channels(self) -> None:
        for row in range(self.channels_table.rowCount()):
            enabled = self.channels_table.cellWidget(row, 1)
            if enabled:
                enabled.setChecked(False)
            self.channels_table.setItem(row, 3, QTableWidgetItem(f"Canal {row}"))
            self.channels_table.setItem(row, 5, QTableWidgetItem("1.0"))
            self.channels_table.setItem(row, 6, QTableWidgetItem("V"))
        self.log_message("Configuration des canaux effacee")

    def apply_channels_configuration(self) -> None:
        if not self.controller:
            return

        for row in range(self.channels_table.rowCount()):
            enabled = self.channels_table.cellWidget(row, 1)
            if not enabled or not enabled.isChecked():
                continue

            sensor_combo = self.channels_table.cellWidget(row, 2)
            range_combo = self.channels_table.cellWidget(row, 4)

            sensor_type = sensor_combo.currentText() if sensor_combo else "generic"
            range_text = range_combo.currentText() if range_combo else "±10V"
            label = (
                self.channels_table.item(row, 3).text()
                if self.channels_table.item(row, 3)
                else f"Canal {row}"
            )
            sensitivity = (
                float(self.channels_table.item(row, 5).text()) if self.channels_table.item(row, 5) else 1.0
            )
            units = self.channels_table.item(row, 6).text() if self.channels_table.item(row, 6) else "V"

            range_volts = 10.0
            if "±1V" in range_text:
                range_volts = 1.0
            elif "±2V" in range_text:
                range_volts = 2.0
            elif "±5V" in range_text:
                range_volts = 5.0

            self.controller.configure_maritime_channel(
                row, sensor_type, label, range_volts, sensitivity, units
            )

    def start_acquisition(self) -> None:
        if not self.controller:
            self.log_message("Pas de controleur disponible")
            return

        self.apply_channels_configuration()
        active_channels = self._get_active_channels()
        if not active_channels:
            self.log_message("Aucun canal actif")
            return

        project_name = self.project_name_edit.text().strip() or "Acquisition_Maritime"
        duration = None if self.continuous_check.isChecked() else self.duration_spin.value()
        success = self.controller.start_acquisition_session(
            project_name,
            sampling_rate=self.sampling_rate_spin.value(),
            duration_seconds=duration,
            channels=active_channels,
            recording_directory=str(self._get_default_data_directory()),
        )
        if not success:
            self.log_message("Erreur de demarrage d'acquisition")
            return

        self.log_message(f"Acquisition demarree: {project_name}")
        if self.controller.current_session.data_file_path:
            self.log_message(f"Enregistrement continu: {self.controller.current_session.data_file_path}")
        self.start_acquisition_btn.setEnabled(False)
        self.stop_acquisition_btn.setEnabled(True)
        self.progress_bar.setVisible(duration is not None)
        if duration is not None:
            self.progress_bar.setMaximum(max(1, int(duration)))
            self.progress_bar.setValue(0)

    def stop_acquisition(self) -> None:
        if self.controller and self.controller.is_acquiring:
            self.controller.stop_acquisition()
            self.log_message("Acquisition arretee")
        self._reset_acquisition_controls()

    def test_acquisition(self) -> None:
        original_duration = self.duration_spin.value()
        original_continuous = self.continuous_check.isChecked()
        self.duration_spin.setValue(3.0)
        self.continuous_check.setChecked(False)
        self.log_message("Test rapide lance")
        self.start_acquisition()
        self.duration_spin.setValue(original_duration)
        self.continuous_check.setChecked(original_continuous)

    def calibrate_system(self) -> None:
        if not self.controller:
            self.log_message("Pas de controleur disponible")
            return

        try:
            results = self.controller.calibrate_system()
            channels = results.get("channels", {})
            self.log_message(f"Calibration terminee: {len(channels)} canaux")
            self.calibration_completed.emit(results)
        except Exception as exc:
            self.log_message(f"Erreur calibration: {exc}")

    def update_display(self) -> None:
        if not self.controller:
            return

        status = self.controller.get_acquisition_status()
        stats = status.get("statistics", {})
        session = status.get("session") or {}

        self.acquisition_status_label.setText("En cours" if status.get("is_acquiring") else "Arretee")
        self.samples_count_label.setText(str(stats.get("samples_acquired", 0)))
        self.acquisition_rate_label.setText(f"{stats.get('acquisition_rate', 0):.1f} Hz")
        self.errors_count_label.setText(str(stats.get("errors", 0)))

        if self.progress_bar.isVisible():
            elapsed = int(session.get("duration_seconds", 0))
            self.progress_bar.setValue(min(elapsed, self.progress_bar.maximum()))

        recent_data = self.controller.get_recent_data(1)
        if recent_data and "data" in recent_data and len(recent_data["data"]) > 0:
            self._update_realtime_table(
                recent_data["data"][-1], recent_data.get("channels", []), recent_data.get("units", [])
            )

        if not status.get("is_acquiring") and self.stop_acquisition_btn.isEnabled():
            self._reset_acquisition_controls()

    def export_csv(self) -> None:
        self._export_data("csv", "Fichiers CSV (*.csv)", "csv")

    def export_json(self) -> None:
        self._export_data("json", "Fichiers JSON (*.json)", "json")

    def export_hdf5(self) -> None:
        self._export_data("hdf5", "Fichiers HDF5 (*.h5 *.hdf5)", "h5")

    def load_configuration(self) -> None:
        self.log_message("Chargement de configuration non implemente")

    def save_configuration(self) -> None:
        self.log_message("Sauvegarde de configuration non implementee")

    def reset_configuration(self) -> None:
        self.clear_channels()
        self.project_name_edit.setText("Acquisition_Maritime")
        self.sampling_rate_spin.setValue(1000.0)
        self.duration_spin.setValue(60.0)
        self.continuous_check.setChecked(False)
        self.log_message("Configuration reinitialisee")

    def clear_log(self) -> None:
        self.log_text.clear()

    def log_message(self, message: str) -> None:
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")

    def data_received_callback(self, data, session) -> None:
        """Relaye le bloc vers le thread Qt au lieu de modifier l'UI ici."""
        self.data_block_received.emit(data, session)

    def _display_received_data(self, data, session) -> None:
        try:
            if hasattr(data, "shape") and data.shape[0] > 0:
                latest_sample = data[-1]
                labels = [channel.label for channel in session.channels] if session else []
                units = [channel.physical_units for channel in session.channels] if session else []
                self._update_realtime_table(latest_sample, labels, units)
        except Exception as exc:
            self.log_message(f"Erreur callback donnees: {exc}")

    def closeEvent(self, event) -> None:
        if self.controller and self.controller.is_acquiring:
            self.controller.stop_acquisition()
        if self.controller:
            self.controller.close()
        event.accept()

    def _get_active_channels(self):
        active_channels = []
        for row in range(self.channels_table.rowCount()):
            enabled = self.channels_table.cellWidget(row, 1)
            if enabled and enabled.isChecked():
                active_channels.append(row)
        return active_channels

    def _update_realtime_table(self, sample_row, labels, units) -> None:
        self.data_table.setRowCount(len(sample_row))
        for index, value in enumerate(sample_row):
            label = labels[index] if index < len(labels) else f"Canal {index}"
            unit = units[index] if index < len(units) else "V"
            self.data_table.setItem(index, 0, QTableWidgetItem(label))
            self.data_table.setItem(index, 1, QTableWidgetItem(f"{float(value):.6f}"))
            self.data_table.setItem(index, 2, QTableWidgetItem(unit))

    def _reset_acquisition_controls(self) -> None:
        self.start_acquisition_btn.setEnabled(True)
        self.stop_acquisition_btn.setEnabled(False)
        self.progress_bar.setVisible(False)

    def _get_default_export_directory(self) -> Path:
        if self.project_dir:
            export_dir = self.project_dir / "exports"
            export_dir.mkdir(parents=True, exist_ok=True)
            return export_dir
        return Path.cwd()

    def _get_default_data_directory(self) -> Path:
        data_dir = self.project_dir / "data" if self.project_dir else Path.cwd() / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        return data_dir

    def _export_data(self, format_type: str, file_filter: str, suffix: str) -> None:
        if not self.controller or not self.controller.current_session:
            self.log_message("Pas de session active a exporter")
            return

        default_path = (
            self._get_default_export_directory() / f"{self.controller.current_session.session_id}.{suffix}"
        )
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            f"Exporter {format_type.upper()}",
            str(default_path),
            file_filter,
        )
        if not file_path:
            return

        success = self.controller.export_session_data(file_path, format_type)
        if success:
            self.log_message(f"Export {format_type.upper()} reussi: {file_path}")
            self.data_exported.emit(file_path)
        else:
            self.log_message(f"Erreur export {format_type.upper()}")
