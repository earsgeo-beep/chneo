#!/usr/bin/env python3
"""Orchestrateur matériel et scientifique des acquisitions CHNeoWave.

Ce contrôleur ne contient aucun générateur de données. Une session ne peut
démarrer qu'avec un backend physique connecté par le registre matériel.
"""

from __future__ import annotations

import logging
import re
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from queue import Queue
from typing import Any

import numpy as np

from hrneowave.core.calibration import CALIBRATION_VALID, CalibrationRecord
from hrneowave.hardware import (
    DeviceDescriptor,
    DiscoveryReport,
    HardwareRegistry,
    VoltageRange,
    build_default_hardware_registry,
)

from .daq_backend import DaqBackend
from .hardware_qualification import (
    HardwareQualificationService,
    QualificationCriteria,
    QualificationReport,
    QualificationReportWriter,
)
from .session_exporter import SessionExporter
from .session_recorder import ContinuousHDF5Recorder, RecordingError

logger = logging.getLogger(__name__)


@dataclass
class MaritimeChannelConfig:
    """Chaîne capteur générique, indépendante du constructeur de la DAQ."""

    channel: int
    sensor_type: str
    label: str
    units: str = "V"
    voltage_range: VoltageRange = VoltageRange.BIPOLAR_10_V
    calibration_offset: float = 0.0
    calibration_scale: float = 1.0
    physical_units: str = "m"
    sensor_sensitivity: float = 1.0
    enabled: bool = True
    sensor_id: str = ""
    probe_position_m: float | None = None
    calibration_id: str = ""
    calibration_status: str = "unverified"
    calibration_record: dict[str, Any] | None = None


@dataclass
class AcquisitionSession:
    """Contrat traçable d'une session physique de laboratoire."""

    session_id: str
    project_name: str
    start_time: datetime
    end_time: datetime | None = None
    sampling_rate: float = 1000.0
    total_samples: int = 0
    channels: list[MaritimeChannelConfig] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    data_file_path: str | None = None


class AcquisitionController:
    """Pilote une session réelle tout en protégeant son intégrité sur disque."""

    def __init__(
        self,
        data_callback: Callable | None = None,
        recorder_factory: Callable[[], ContinuousHDF5Recorder] = ContinuousHDF5Recorder,
        exporter_factory: Callable[[], SessionExporter] = SessionExporter,
        hardware_registry: HardwareRegistry | None = None,
        auto_initialize: bool = True,
        daq_backend: DaqBackend | None = None,
    ) -> None:
        if daq_backend is not None and not bool(getattr(daq_backend, "is_hardware", False)):
            raise TypeError("AcquisitionController refuse les sources non matérielles")

        self.data_callback = data_callback
        self._recorder_factory = recorder_factory
        self._exporter_factory = exporter_factory
        self.hardware_registry = hardware_registry or build_default_hardware_registry()
        self._daq_backend = daq_backend
        self._recorder: ContinuousHDF5Recorder | None = None
        self.available_devices: list[DeviceDescriptor] = []
        self.discovery_errors: dict[str, str] = {}
        self.selected_device: DeviceDescriptor | None = (
            daq_backend.descriptor if daq_backend is not None else None
        )

        self.is_acquiring = False
        self.acquisition_thread: threading.Thread | None = None
        self.data_queue = Queue()
        self.channels_config: dict[int, MaritimeChannelConfig] = {}
        self.current_session: AcquisitionSession | None = None
        self.stats = self._new_statistics()

        self.data_buffer: list[dict[str, Any]] = []
        self.preview_sample_limit = 100_000
        self.buffer_size = 10_000
        self._data_lock = threading.RLock()
        self.last_exported_path: str | None = None
        self.last_qualification_report: QualificationReport | None = None
        self.last_qualification_files: tuple[str, str] | None = None
        self._last_backend_time_seconds: float | None = None
        self._acquisition_started_monotonic: float | None = None
        self._calibration_preview_active = False
        self._calibration_preview_thread: threading.Thread | None = None
        self._calibration_preview_stop = threading.Event()
        self.calibration_preview_error: str | None = None

        if auto_initialize and daq_backend is None:
            self.refresh_hardware()

    @staticmethod
    def _new_statistics() -> dict[str, Any]:
        return {
            "samples_acquired": 0,
            "acquisition_rate": 0.0,
            "last_update": None,
            "errors": 0,
            "buffer_overruns": 0,
            "recording_errors": 0,
            "timing_discontinuities": 0,
            "max_timing_error_seconds": 0.0,
            "backend_blocks": 0,
        }

    def discover_hardware(self) -> DiscoveryReport:
        """Interroge tous les pilotes enregistrés sans fallback logiciel."""

        if self.is_acquiring or self.is_calibration_preview_active:
            raise RuntimeError("Inventaire matériel interdit pendant une lecture active")
        report = self.hardware_registry.discover()
        self.available_devices = list(report.devices)
        self.discovery_errors = dict(report.driver_errors)
        logger.info(
            "Inventaire matériel terminé: %s équipement(s), %s erreur(s) pilote",
            len(self.available_devices),
            len(self.discovery_errors),
        )
        return report

    def connect_hardware(self, device_key: str) -> bool:
        """Sélectionne un équipement physique du dernier inventaire."""

        if self.is_acquiring or self.is_calibration_preview_active:
            logger.error("Changement de matériel interdit pendant une lecture active")
            return False
        try:
            backend = self.hardware_registry.open_device(device_key)
            if self._daq_backend is not None and self._daq_backend is not backend:
                self._daq_backend.close()
            self._daq_backend = backend
            self.selected_device = backend.descriptor
            logger.info("Équipement connecté: %s", self.selected_device.display_name)
            return True
        except Exception as exc:
            logger.exception("Connexion matérielle impossible: %s", exc)
            self._daq_backend = None
            self.selected_device = None
            return False

    def refresh_hardware(self) -> bool:
        """Inventorie les pilotes puis connecte le premier équipement détecté."""

        try:
            report = self.discover_hardware()
        except Exception as exc:
            logger.error("Inventaire matériel impossible: %s", exc)
            return False
        if not report.devices:
            logger.warning("Aucun équipement d'acquisition physique détecté")
            return False
        return self.connect_hardware(report.devices[0].key)

    def get_available_devices(self) -> list[DeviceDescriptor]:
        return list(self.available_devices)

    def get_hardware_capabilities(self):
        return self.selected_device.capabilities if self.selected_device else None

    def get_hardware_status(self) -> dict[str, Any]:
        if not self.is_hardware_available() or self._daq_backend is None:
            return {
                "connected": False,
                "device": None,
                "driver_errors": dict(self.discovery_errors),
            }
        return self._daq_backend.status()

    def is_hardware_available(self) -> bool:
        backend = self._daq_backend
        return bool(
            backend is not None
            and getattr(backend, "is_hardware", False)
            and getattr(backend, "connected", False)
        )

    def configure_maritime_channel(
        self,
        channel: int,
        sensor_type: str,
        label: str,
        range_volts: float = 10.0,
        sensor_sensitivity: float = 1.0,
        physical_units: str = "m",
        probe_position_m: float | None = None,
    ) -> bool:
        if channel < 0:
            logger.error("Numéro de canal négatif: %s", channel)
            return False
        capabilities = self.get_hardware_capabilities()
        if capabilities is not None and channel >= capabilities.analog_input_channels:
            logger.error(
                "Canal %s hors capacité du matériel (%s voies)",
                channel,
                capabilities.analog_input_channels,
            )
            return False
        if not np.isfinite(sensor_sensitivity) or sensor_sensitivity == 0:
            logger.error("Sensibilité invalide sur le canal %s", channel)
            return False
        if probe_position_m is not None and not np.isfinite(probe_position_m):
            logger.error("Position de sonde invalide sur le canal %s", channel)
            return False
        try:
            voltage_range = VoltageRange.from_limit(range_volts)
        except ValueError as exc:
            logger.error("%s", exc)
            return False
        if capabilities is not None and voltage_range not in capabilities.voltage_ranges:
            logger.error("Plage %s non prise en charge par le matériel", voltage_range.label)
            return False

        self.channels_config[channel] = MaritimeChannelConfig(
            channel=int(channel),
            sensor_type=str(sensor_type),
            label=str(label),
            units="V",
            voltage_range=voltage_range,
            physical_units=str(physical_units),
            sensor_sensitivity=float(sensor_sensitivity),
            probe_position_m=(float(probe_position_m) if probe_position_m is not None else None),
        )
        logger.info("Canal %s configuré: %s - %s", channel, sensor_type, label)
        return True

    def get_channel_configuration(self, channel: int) -> dict[str, Any] | None:
        config = self.channels_config.get(channel)
        if config is None:
            return None
        return {
            "channel": config.channel,
            "sensor_type": config.sensor_type,
            "label": config.label,
            "range_volts": config.voltage_range.value,
            "range_label": config.voltage_range.label,
            "physical_units": config.physical_units,
            "sensor_sensitivity": config.sensor_sensitivity,
            "enabled": config.enabled,
            "calibration_offset": config.calibration_offset,
            "calibration_scale": config.calibration_scale,
            "probe_position_m": config.probe_position_m,
        }

    @property
    def is_calibration_preview_active(self) -> bool:
        """Indique si un scan physique temporaire alimente le poste de calibration."""

        thread = self._calibration_preview_thread
        return bool(self._calibration_preview_active and thread is not None and thread.is_alive())

    def start_calibration_preview(
        self,
        channel: int,
        *,
        sample_rate_hz: float = 200.0,
        range_volts: float = 10.0,
        block_size: int | None = None,
        data_callback: Callable[[np.ndarray, float], None] | None = None,
        error_callback: Callable[[str], None] | None = None,
    ) -> float:
        """Démarre une lecture brute réelle, non enregistrée, pour l'étalonnage.

        Ce chemin utilise le même backend physique que l'acquisition principale.
        Il ne crée ni session, ni fichier, ni source de remplacement logicielle.
        """

        if self.is_acquiring:
            raise RuntimeError("Lecture de calibration interdite pendant une acquisition")
        if self.is_calibration_preview_active:
            raise RuntimeError("Une lecture de calibration est déjà active")
        if not self.is_hardware_available() or self._daq_backend is None:
            raise RuntimeError("Aucun équipement physique connecté")

        capabilities = self.get_hardware_capabilities()
        channel_number = int(channel)
        if capabilities is None or not 0 <= channel_number < capabilities.analog_input_channels:
            raise ValueError(f"Canal matériel invalide: {channel_number}")
        voltage_range = VoltageRange.from_limit(float(range_volts))
        if voltage_range not in capabilities.voltage_ranges:
            raise ValueError(f"Plage non prise en charge: {voltage_range.label}")
        rate = float(sample_rate_hz)
        capabilities.validate(rate, 1)
        requested_block_size = int(block_size or max(10, round(rate / 10.0)))
        if requested_block_size <= 0:
            raise ValueError("Taille de bloc de calibration invalide")

        configured = self.channels_config.get(channel_number)
        preview_channel = MaritimeChannelConfig(
            channel=channel_number,
            sensor_type=configured.sensor_type if configured else "calibration",
            label=configured.label if configured else f"Canal {channel_number + 1}",
            voltage_range=voltage_range,
            physical_units="V",
            sensor_sensitivity=1.0,
            sensor_id=configured.sensor_id if configured else "",
        )

        actual_rate = float(
            self._daq_backend.start(
                sample_rate_hz=rate,
                channels=[preview_channel],
                chunk_size=max(requested_block_size, 100),
            )
        )
        if not np.isfinite(actual_rate) or actual_rate <= 0:
            self._daq_backend.stop()
            raise RuntimeError("Le pilote a retourné une fréquence de calibration invalide")
        self.calibration_preview_error = None
        self._calibration_preview_stop.clear()
        self._calibration_preview_active = True
        self._calibration_preview_thread = threading.Thread(
            target=self._calibration_preview_loop,
            args=(
                actual_rate,
                requested_block_size,
                data_callback,
                error_callback,
            ),
            daemon=True,
            name=f"CHNeoWave-calibration-channel-{channel_number}",
        )
        try:
            self._calibration_preview_thread.start()
        except Exception:
            self._calibration_preview_active = False
            self._calibration_preview_thread = None
            self._daq_backend.stop()
            raise
        logger.info(
            "Lecture calibration démarrée: canal=%s, plage=%s, fréquence=%.3f Hz",
            channel_number,
            voltage_range.label,
            actual_rate,
        )
        return actual_rate

    def _calibration_preview_loop(
        self,
        sample_rate_hz: float,
        block_size: int,
        data_callback: Callable[[np.ndarray, float], None] | None,
        error_callback: Callable[[str], None] | None,
    ) -> None:
        minimum_period = block_size / sample_rate_hz
        try:
            while not self._calibration_preview_stop.is_set():
                cycle_started = time.monotonic()
                result = self._daq_backend.read(num_samples=block_size)
                if result is not None:
                    raw = np.asarray(result.raw_data, dtype=np.float64)
                    if raw.ndim != 2 or raw.shape[1] != 1:
                        raise RuntimeError("La lecture de calibration doit retourner un seul canal")
                    if result.backend_name != self._daq_backend.name:
                        raise RuntimeError("Le bloc de calibration ne correspond pas au pilote actif")
                    if data_callback is not None:
                        try:
                            data_callback(raw.copy(), float(result.sample_rate_hz))
                        except Exception as exc:
                            logger.error("Callback de calibration refusé: %s", exc)
                elapsed = time.monotonic() - cycle_started
                self._calibration_preview_stop.wait(max(0.0, minimum_period - elapsed))
        except Exception as exc:
            self.calibration_preview_error = str(exc)
            logger.exception("Lecture de calibration interrompue: %s", exc)
            if error_callback is not None:
                try:
                    error_callback(str(exc))
                except Exception:
                    logger.exception("Impossible de notifier l'erreur de calibration")
        finally:
            if self._daq_backend is not None:
                try:
                    self._daq_backend.stop()
                except Exception:
                    logger.exception("Arrêt du backend après calibration impossible")
            self._calibration_preview_active = False

    def stop_calibration_preview(self) -> bool:
        """Arrête proprement le scan de calibration sans fermer la carte."""

        thread = self._calibration_preview_thread
        if thread is None:
            self._calibration_preview_active = False
            return True
        self._calibration_preview_stop.set()
        if thread is not threading.current_thread() and thread.is_alive():
            thread.join(timeout=2.0)
        stopped = not thread.is_alive()
        if not stopped and self._daq_backend is not None:
            try:
                self._daq_backend.stop()
            except Exception:
                logger.exception("Arrêt forcé de la lecture calibration impossible")
            thread.join(timeout=1.0)
            stopped = not thread.is_alive()
        self._calibration_preview_active = False
        self._calibration_preview_thread = None
        if not stopped:
            logger.error("Le thread de calibration ne s'est pas arrêté")
        return stopped

    def apply_calibration_record(self, record: CalibrationRecord) -> bool:
        if not isinstance(record, CalibrationRecord):
            logger.error("Enregistrement de calibration invalide")
            return False
        if record.validity_status != CALIBRATION_VALID:
            logger.error("Calibration refusée: statut %s", record.validity_status)
            return False
        config = self.channels_config.get(int(record.channel))
        if config is None:
            logger.error("Calibration sans canal configuré: %s", record.channel)
            return False

        config.sensor_id = record.sensor_id
        config.sensor_type = record.sensor_type or config.sensor_type
        config.physical_units = record.physical_unit or config.physical_units
        config.calibration_offset = float(record.offset_volts)
        config.calibration_scale = float(record.scale)
        config.sensor_sensitivity = float(record.sensitivity_v_per_unit)
        config.calibration_id = record.calibration_id
        config.calibration_status = record.validity_status
        config.calibration_record = record.to_dict()
        logger.info("Calibration %s appliquée au canal %s", record.calibration_id, record.channel)
        return True

    def start_acquisition_session(
        self,
        project_name: str,
        sampling_rate: float = 1000.0,
        duration_seconds: float | None = None,
        channels: list[int] | None = None,
        recording_directory: str | None = None,
        water_depth_m: float | None = None,
        session_metadata: dict[str, Any] | None = None,
    ) -> bool:
        if self.is_acquiring:
            logger.error("Acquisition déjà en cours")
            return False
        if self.is_calibration_preview_active:
            logger.error("Acquisition interdite: arrêtez d'abord la lecture de calibration")
            return False
        if not self.is_hardware_available() or self._daq_backend is None:
            logger.error("Acquisition interdite: aucun équipement physique connecté")
            return False
        if recording_directory is None:
            logger.error("Acquisition interdite: répertoire d'enregistrement obligatoire")
            return False
        if not np.isfinite(sampling_rate) or sampling_rate <= 0:
            logger.error("Fréquence d'échantillonnage invalide: %s", sampling_rate)
            return False
        if duration_seconds is not None and (not np.isfinite(duration_seconds) or duration_seconds <= 0):
            logger.error("Durée d'acquisition invalide: %s", duration_seconds)
            return False
        if water_depth_m is not None and (not np.isfinite(water_depth_m) or water_depth_m <= 0):
            logger.error("Profondeur d'eau invalide: %s", water_depth_m)
            return False

        selected_channels = list(self.channels_config) if channels is None else list(channels)
        if not selected_channels:
            logger.error("Aucun canal configuré")
            return False
        missing = [item for item in selected_channels if item not in self.channels_config]
        if missing:
            logger.error("Canaux non configurés: %s", missing)
            return False
        selected_configs = [self.channels_config[item] for item in selected_channels]
        try:
            self._daq_backend.capabilities.validate(sampling_rate, len(selected_configs))
        except ValueError as exc:
            logger.error("Configuration incompatible avec le matériel: %s", exc)
            return False

        with self._data_lock:
            self.data_buffer.clear()
        self.stats = self._new_statistics()
        self._last_backend_time_seconds = None
        self._acquisition_started_monotonic = None
        self.last_qualification_report = None
        self.last_qualification_files = None

        start_time = datetime.now()
        project_slug = re.sub(r"[^A-Za-z0-9._-]+", "_", project_name.strip())
        project_slug = project_slug.strip("._-")[:80] or "Acquisition_Maritime"
        session_id = f"{project_slug}_{start_time.strftime('%Y%m%d_%H%M%S_%f')[:-3]}"
        self.current_session = AcquisitionSession(
            session_id=session_id,
            project_name=project_name,
            start_time=start_time,
            sampling_rate=float(sampling_rate),
            channels=selected_configs,
            metadata={
                **dict(session_metadata or {}),
                "acquisition_source": "physical_hardware",
                "duration_seconds": duration_seconds,
                "selected_channels": selected_channels,
                "hardware_available": True,
                "water_depth_m": float(water_depth_m) if water_depth_m is not None else None,
                **self.selected_device.to_metadata(),
            },
        )

        try:
            actual_rate = self._daq_backend.start(
                sample_rate_hz=float(sampling_rate),
                channels=selected_configs,
                chunk_size=min(self.buffer_size, 1000),
            )
            self.current_session.sampling_rate = float(actual_rate)
            self.current_session.metadata.update(self._daq_backend.metadata())
            self.current_session.metadata["requested_sampling_rate"] = float(sampling_rate)
            self.current_session.metadata["actual_sampling_rate"] = float(actual_rate)
            if duration_seconds is not None:
                self.current_session.metadata["expected_samples"] = max(
                    1,
                    int(round(duration_seconds * actual_rate)),
                )

            recording_path = Path(recording_directory) / f"{session_id}.h5"
            self._recorder = self._recorder_factory()
            resolved = self._recorder.start(recording_path, self.current_session)
            self.current_session.data_file_path = str(resolved)
            self.current_session.metadata["recording_path"] = str(resolved)

            self.is_acquiring = True
            self.acquisition_thread = threading.Thread(
                target=self._acquisition_loop,
                args=(duration_seconds,),
                daemon=True,
                name=f"CHNeoWave-{session_id}",
            )
            self.acquisition_thread.start()
            logger.info("Session physique démarrée: %s", session_id)
            return True
        except Exception as exc:
            logger.exception("Démarrage de session impossible: %s", exc)
            if self._recorder is not None:
                self._recorder.close()
                self._recorder = None
            self._daq_backend.stop()
            self.current_session = None
            return False

    def _acquisition_loop(self, duration_seconds: float | None) -> None:
        start_monotonic = time.monotonic()
        self._acquisition_started_monotonic = start_monotonic
        last_stats_update = start_monotonic
        samples_since_update = 0
        target_samples = (
            int(self.current_session.metadata.get("expected_samples", 0))
            if self.current_session and duration_seconds is not None
            else None
        )
        deadline = (
            start_monotonic + duration_seconds + max(2.0, duration_seconds * 0.1)
            if duration_seconds is not None
            else None
        )

        try:
            while self.is_acquiring:
                if target_samples is not None and self.stats["samples_acquired"] >= target_samples:
                    break
                if deadline is not None and time.monotonic() >= deadline:
                    self.stats["errors"] += 1
                    self.current_session.metadata["incomplete_reason"] = "acquisition_timeout"
                    break

                requested = 100
                if target_samples is not None:
                    requested = min(requested, target_samples - self.stats["samples_acquired"])
                result = self._daq_backend.read(num_samples=requested)
                if result is None:
                    continue
                if result.backend_name != self._daq_backend.name:
                    raise RuntimeError("Le bloc reçu ne correspond pas au pilote actif")
                self._validate_backend_timing(result)
                if result.warnings:
                    self.current_session.metadata.setdefault("warnings", []).extend(result.warnings)
                self._process_acquired_data(result.raw_data)
                samples_since_update += result.raw_data.shape[0]

                now = time.monotonic()
                if now - last_stats_update >= 1.0:
                    self.stats["acquisition_rate"] = samples_since_update / (now - last_stats_update)
                    self.stats["last_update"] = datetime.now()
                    samples_since_update = 0
                    last_stats_update = now
        except Exception as exc:
            logger.exception("Erreur dans la boucle d'acquisition: %s", exc)
            self.stats["errors"] += 1
            if isinstance(exc, RecordingError):
                self.stats["recording_errors"] += 1
            try:
                status = self._daq_backend.status()
                self.stats["buffer_overruns"] = int(status.get("buffer_overruns", 0))
            except Exception:
                pass
        finally:
            self._finalize_acquisition()

    def _process_acquired_data(self, raw_data: np.ndarray) -> None:
        raw = np.asarray(raw_data, dtype=float)
        if raw.ndim != 2 or raw.shape[0] == 0:
            raise ValueError("Bloc matériel vide ou de forme invalide")
        if self.current_session is None or raw.shape[1] != len(self.current_session.channels):
            raise ValueError("Le nombre de colonnes ne correspond pas aux canaux de la session")
        if not np.all(np.isfinite(raw)):
            raise ValueError("Le bloc matériel contient NaN ou Inf")

        processed = self._convert_to_physical_units(raw)
        if self._recorder is None:
            raise RecordingError("Enregistreur maître absent pendant l'acquisition")
        self._recorder.append(raw, processed)

        with self._data_lock:
            self.data_buffer.append(
                {
                    "timestamp": datetime.now(),
                    "raw_data": raw.copy(),
                    "processed_data": processed.copy(),
                    "sample_count": raw.shape[0],
                }
            )
            preview_samples = sum(entry["sample_count"] for entry in self.data_buffer)
            while self.data_buffer and preview_samples > self.preview_sample_limit:
                preview_samples -= self.data_buffer.pop(0)["sample_count"]

        self.stats["samples_acquired"] += raw.shape[0]
        if self.data_callback is not None:
            try:
                self.data_callback(processed, self.current_session)
            except Exception as exc:
                logger.error("Erreur dans le callback d'affichage: %s", exc)

    def _convert_to_physical_units(self, raw_data: np.ndarray) -> np.ndarray:
        if self.current_session is None:
            raise RuntimeError("Conversion impossible sans session")
        processed = np.empty(raw_data.shape, dtype=np.float64)
        for index, config in enumerate(self.current_session.channels):
            if config.sensor_sensitivity == 0:
                raise ValueError(f"Sensibilité nulle sur le canal {config.channel}")
            processed[:, index] = (
                (raw_data[:, index] + config.calibration_offset)
                * config.calibration_scale
                / config.sensor_sensitivity
            )
        return processed

    def stop_acquisition(self) -> bool:
        if not self.is_acquiring:
            logger.warning("Aucune acquisition en cours")
            return False
        self.is_acquiring = False
        if self.acquisition_thread and self.acquisition_thread.is_alive():
            self.acquisition_thread.join(timeout=5.0)
        if self.acquisition_thread and self.acquisition_thread.is_alive():
            logger.error("Le thread d'acquisition ne s'est pas arrêté dans le délai")
            self.stats["errors"] += 1
            return False
        return True

    def _finalize_acquisition(self) -> None:
        final_hardware_status: dict[str, Any] | None = None
        try:
            if self._daq_backend is not None:
                try:
                    final_hardware_status = self._daq_backend.status()
                    self.stats["buffer_overruns"] = max(
                        int(self.stats.get("buffer_overruns", 0)),
                        int(final_hardware_status.get("buffer_overruns", 0)),
                    )
                except Exception as exc:
                    logger.warning("Diagnostic final du pilote indisponible: %s", exc)
                self._daq_backend.stop()
        finally:
            if self.current_session is not None:
                self.current_session.end_time = datetime.now()
                self.current_session.total_samples = int(self.stats["samples_acquired"])
                if self._acquisition_started_monotonic is not None:
                    self.current_session.metadata["acquisition_wall_elapsed_seconds"] = max(
                        0.0,
                        time.monotonic() - self._acquisition_started_monotonic,
                    )
                if final_hardware_status is not None:
                    self.current_session.metadata["final_hardware_status"] = final_hardware_status
                if self._recorder is not None:
                    try:
                        self._recorder.finalize(self.current_session, self.stats)
                    except Exception as exc:
                        self.stats["errors"] += 1
                        self.stats["recording_errors"] += 1
                        logger.exception("Finalisation HDF5 impossible: %s", exc)
                    finally:
                        self._recorder = None
            self._acquisition_started_monotonic = None
            self.is_acquiring = False

    def _validate_backend_timing(self, result) -> None:
        """Vérifie la cadence interne et la continuité entre deux blocs DAQ."""

        if self.current_session is None:
            raise RuntimeError("Bloc matériel reçu sans session active")
        sample_rate = float(self.current_session.sampling_rate)
        relative_rate_error = abs(float(result.sample_rate_hz) - sample_rate) / sample_rate
        if relative_rate_error > 1e-6:
            self.stats["timing_discontinuities"] += 1
            raise RuntimeError("La fréquence annoncée par le bloc diffère de la fréquence de session")

        time_values = np.asarray(result.time, dtype=np.float64)
        expected_interval = 1.0 / sample_rate
        intervals: list[np.ndarray] = []
        if time_values.size > 1:
            intervals.append(np.diff(time_values))
        if self._last_backend_time_seconds is not None and time_values.size:
            intervals.append(
                np.asarray(
                    [time_values[0] - self._last_backend_time_seconds],
                    dtype=np.float64,
                )
            )

        maximum_error = 0.0
        if intervals:
            maximum_error = max(
                float(np.max(np.abs(values - expected_interval))) for values in intervals if values.size
            )
        self.stats["max_timing_error_seconds"] = max(
            float(self.stats["max_timing_error_seconds"]),
            maximum_error,
        )
        self.stats["backend_blocks"] += 1
        if time_values.size:
            if self._last_backend_time_seconds is None:
                self.current_session.metadata["backend_time_start_seconds"] = float(time_values[0])
            self._last_backend_time_seconds = float(time_values[-1])
            self.current_session.metadata["backend_time_end_seconds"] = float(time_values[-1])

        if maximum_error > expected_interval * 0.05:
            self.stats["timing_discontinuities"] += 1
            raise RuntimeError(
                "Discontinuité temporelle du pilote: "
                f"erreur={maximum_error:.9g} s, limite={expected_interval * 0.05:.9g} s"
            )

    def get_acquisition_status(self) -> dict[str, Any]:
        status: dict[str, Any] = {
            "is_acquiring": self.is_acquiring,
            "hardware_available": self.is_hardware_available(),
            "statistics": self.stats.copy(),
            "session": None,
            "channels_configured": len(self.channels_config),
            "preview_buffer_blocks": len(self.data_buffer),
            "recording_path": self.current_session.data_file_path if self.current_session else None,
            "device": self.selected_device.to_metadata() if self.selected_device else None,
        }
        if self.current_session is not None:
            status["session"] = {
                "session_id": self.current_session.session_id,
                "project_name": self.current_session.project_name,
                "start_time": self.current_session.start_time.isoformat(),
                "sampling_rate": self.current_session.sampling_rate,
                "channels_count": len(self.current_session.channels),
                "duration_seconds": (datetime.now() - self.current_session.start_time).total_seconds(),
            }
        if self.is_hardware_available():
            try:
                status["hardware_status"] = self.get_hardware_status()
            except Exception as exc:
                status["hardware_status"] = {"connected": False, "error": str(exc)}
        return status

    def get_recent_data(self, num_samples: int = 1000) -> dict[str, Any] | None:
        with self._data_lock:
            if not self.data_buffer:
                return None
            snapshot = list(self.data_buffer)
        chunks: list[np.ndarray] = []
        total = 0
        for entry in reversed(snapshot):
            if total >= num_samples:
                break
            chunks.append(entry["processed_data"])
            total += entry["sample_count"]
        if not chunks or self.current_session is None:
            return None
        data = np.vstack(chunks[::-1])[-num_samples:]
        first_index = max(0, self.stats["samples_acquired"] - data.shape[0])
        interval = timedelta(seconds=1.0 / self.current_session.sampling_rate)
        timestamps = [
            self.current_session.start_time + (first_index + index) * interval
            for index in range(data.shape[0])
        ]
        return {
            "data": data,
            "timestamps": timestamps,
            "channels": [item.label for item in self.current_session.channels],
            "units": [item.physical_units for item in self.current_session.channels],
            "sample_count": data.shape[0],
        }

    def export_session_data(self, file_path: str, format: str = "csv") -> bool:
        if self.is_acquiring:
            logger.error("Export interdit pendant l'acquisition")
            return False
        if self.current_session is None or not self.current_session.data_file_path:
            logger.error("Aucun fichier HDF5 maître disponible")
            return False
        try:
            output = self._exporter_factory().export(
                self.current_session.data_file_path,
                file_path,
                format,
            )
            self.last_exported_path = str(output)
            logger.info("Session complète exportée: %s", output)
            return True
        except Exception as exc:
            logger.exception("Export intègre impossible: %s", exc)
            return False

    def qualify_current_session(
        self,
        criteria: QualificationCriteria | None = None,
        output_directory: str | None = None,
    ) -> QualificationReport:
        """Qualifie la dernière session terminée et écrit ses rapports autonomes."""

        if self.is_acquiring:
            raise RuntimeError("Qualification interdite pendant l'acquisition")
        if self.current_session is None or not self.current_session.data_file_path:
            raise RuntimeError("Aucun fichier HDF5 maître à qualifier")
        selected_criteria = criteria or QualificationCriteria.quick_functional()
        source = Path(self.current_session.data_file_path)
        report = HardwareQualificationService().evaluate(source, selected_criteria)
        target_directory = (
            Path(output_directory)
            if output_directory is not None
            else source.parent / "qualification_reports"
        )
        json_path, hdf5_path = QualificationReportWriter().write_bundle(
            report,
            target_directory,
        )
        self.last_qualification_report = report
        self.last_qualification_files = (str(json_path), str(hdf5_path))
        logger.info(
            "Qualification %s: %s (%s)",
            report.qualification_id,
            report.verdict,
            source,
        )
        return report

    def _build_time_vector(self, sample_count: int) -> np.ndarray:
        if sample_count <= 0:
            return np.array([])
        sample_rate = self.current_session.sampling_rate if self.current_session else 0.0
        if sample_rate <= 0:
            raise ValueError("Fréquence d'échantillonnage invalide")
        return np.arange(sample_count, dtype=float) / sample_rate

    def calibrate_system(self) -> dict[str, Any]:
        """Retourne l'état réel des certificats; aucune calibration n'est inventée."""

        records = {}
        for channel, config in self.channels_config.items():
            records[channel] = {
                "channel": channel,
                "label": config.label,
                "sensor_type": config.sensor_type,
                "calibration_status": config.calibration_status,
                "calibration_id": config.calibration_id,
                "sensitivity_v_per_unit": config.sensor_sensitivity,
            }
        all_valid = bool(records) and all(
            item["calibration_status"] == CALIBRATION_VALID for item in records.values()
        )
        return {
            "timestamp": datetime.now().isoformat(),
            "channels": records,
            "system_status": "calibrated" if all_valid else "not_calibrated",
            "calibration_status": "valid" if all_valid else "not_performed",
            "calibration_valid": all_valid,
            "hardware_connected": self.is_hardware_available(),
        }

    def close(self) -> None:
        self.stop_calibration_preview()
        if self.is_acquiring:
            self.stop_acquisition()
        if self._daq_backend is not None:
            self._daq_backend.close()
        if self._recorder is not None:
            self._recorder.close()
            self._recorder = None
        logger.info("Contrôleur d'acquisition fermé")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def create_default_maritime_config(channel_count: int = 8) -> dict[int, MaritimeChannelConfig]:
    """Crée un preset capteurs; le nombre de voies vient ensuite du matériel."""

    if channel_count <= 0:
        raise ValueError("channel_count doit être positif")
    templates = [
        ("wave_height", "Capteur Houle #1", VoltageRange.BIPOLAR_10_V, "m", 2.0),
        ("wave_height", "Capteur Houle #2", VoltageRange.BIPOLAR_10_V, "m", 2.0),
        ("pressure", "Capteur Pression", VoltageRange.BIPOLAR_5_V, "hPa", 0.01),
        ("accelerometer", "Accéléromètre X", VoltageRange.BIPOLAR_10_V, "m/s²", 1.0),
        ("accelerometer", "Accéléromètre Y", VoltageRange.BIPOLAR_10_V, "m/s²", 1.0),
        ("accelerometer", "Accéléromètre Z", VoltageRange.BIPOLAR_10_V, "m/s²", 1.0),
        ("temperature", "Température Eau", VoltageRange.BIPOLAR_2_V, "°C", 0.1),
        ("wave_height", "Référence Houle", VoltageRange.BIPOLAR_10_V, "m", 2.0),
    ]
    result: dict[int, MaritimeChannelConfig] = {}
    for channel in range(channel_count):
        if channel < len(templates):
            sensor_type, label, voltage_range, physical_units, sensitivity = templates[channel]
        else:
            sensor_type = "generic"
            label = f"Canal {channel}"
            voltage_range = VoltageRange.BIPOLAR_10_V
            physical_units = "V"
            sensitivity = 1.0
        result[channel] = MaritimeChannelConfig(
            channel=channel,
            sensor_type=sensor_type,
            label=label,
            voltage_range=voltage_range,
            physical_units=physical_units,
            sensor_sensitivity=sensitivity,
        )
    return result
