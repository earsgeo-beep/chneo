#!/usr/bin/env python3
"""
Contrôleur d'acquisition pour CHNeoWave
Module d'interface pour l'acquisition de données maritime avec MCC DAQ USB-1608FS

Auteur: CHNeoWave Development Team
Version: 1.0.0
"""

import json
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
from hrneowave.core.session_schema import (
    DATA_KIND_PHYSICAL,
    build_channel_metadata,
    build_csv_metadata_row,
    build_session_metadata,
)

from .daq_backend import DaqBackend
from .mcc_daq_wrapper import (
    MCCDAQ_USB1608FS,
    MCCBackendError,
    MCCRanges,
    scan_available_boards,
)
from .session_recorder import ContinuousHDF5Recorder, RecordingError

# Configuration du logging
logger = logging.getLogger(__name__)

@dataclass
class MaritimeChannelConfig:
    """Configuration d'un canal pour l'acquisition maritime"""
    channel: int
    sensor_type: str  # 'pressure', 'accelerometer', 'wave_height', 'temperature'
    label: str
    units: str
    range_type: MCCRanges
    calibration_offset: float = 0.0
    calibration_scale: float = 1.0
    physical_units: str = "m"  # Unités physiques finales
    sensor_sensitivity: float = 1.0  # V/unité physique
    enabled: bool = True
    sensor_id: str = ""
    calibration_id: str = ""
    calibration_status: str = "unverified"
    calibration_record: dict[str, Any] | None = None

@dataclass
class AcquisitionSession:
    """Session d'acquisition de données maritimes"""
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
    """
    Contrôleur principal pour l'acquisition de données maritime
    
    Gère l'interface entre l'interface utilisateur CHNeoWave et la carte MCC DAQ,
    avec des fonctionnalités spécialisées pour l'acquisition de houle maritime.
    """
    
    def __init__(
        self,
        data_callback: Callable | None = None,
        daq_factory: Callable[[], MCCDAQ_USB1608FS] = MCCDAQ_USB1608FS,
        board_scanner: Callable[[], list[int]] = scan_available_boards,
        recorder_factory: Callable[[], ContinuousHDF5Recorder] = ContinuousHDF5Recorder,
        auto_initialize: bool = True,
        daq_backend: DaqBackend | None = None,
    ):
        """
        Initialise le contrôleur d'acquisition
        
        Args:
            data_callback: Fonction appelée lors de nouveaux données
        """
        self.daq = None
        self.data_callback = data_callback
        self._daq_factory = daq_factory
        self._board_scanner = board_scanner
        self._recorder_factory = recorder_factory
        self._daq_backend = daq_backend
        self._recorder: ContinuousHDF5Recorder | None = None
        self.is_acquiring = False
        self.acquisition_thread = None
        self.data_queue = Queue()
        
        # Configuration
        self.channels_config = {}
        self.current_session = None
        self.available_boards = []
        
        # Statistiques en temps réel
        self.stats = {
            'samples_acquired': 0,
            'acquisition_rate': 0.0,
            'last_update': None,
            'errors': 0,
            'buffer_overruns': 0,
            'recording_errors': 0,
        }
        
        # Buffer pour données
        self.data_buffer = []
        self.buffer_size = 10000
        self._data_lock = threading.RLock()
        self._simulation_sample_index = 0
        self.last_exported_path: str | None = None
        
        if auto_initialize and self._daq_backend is None:
            self._initialize_system()
        
    def _initialize_system(self):
        """Initialise le système d'acquisition"""
        return self.refresh_hardware()

    def refresh_hardware(self) -> bool:
        """Detecte puis initialise explicitement la premiere carte MCC.

        La vue graphique appelle cette methode uniquement a la demande de
        l'operateur. Ainsi, un probleme dans la bibliotheque native MCC ne peut
        plus interrompre la construction de la fenetre principale.
        """
        if self.is_acquiring:
            logger.warning("Scan MCC refuse pendant une acquisition")
            return False

        try:
            if self.daq is not None:
                self.daq.close()
                self.daq = None

            # Scan des cartes disponibles
            self.available_boards = self._board_scanner()
            logger.info(f"Cartes MCC détectées: {self.available_boards}")
            
            if self.available_boards:
                # Initialisation avec la première carte
                self.daq = self._daq_factory()
                if self.daq.initialize(self.available_boards[0]):
                    logger.info("Système d'acquisition initialisé")
                    return True
                else:
                    logger.error("Erreur d'initialisation de la carte")
                    self.daq = None
            else:
                logger.warning("Aucune carte MCC détectée - Mode simulation")
                
        except Exception as e:
            logger.error(f"Erreur d'initialisation du système: {e}")
            self.available_boards = []
            self.daq = None
        return False
            
    def get_available_boards(self) -> list[int]:
        """Retourne la liste des cartes disponibles"""
        return self.available_boards.copy()
        
    def is_hardware_available(self) -> bool:
        """Vérifie si le matériel est disponible"""
        daq_backend = getattr(self, "_daq_backend", None)
        if daq_backend is not None:
            return bool(getattr(daq_backend, "is_hardware", False))
        return self.daq is not None and self.daq.is_initialized
        
    def configure_maritime_channel(self, 
                                 channel: int,
                                 sensor_type: str,
                                 label: str,
                                 range_volts: float = 10.0,
                                 sensor_sensitivity: float = 1.0,
                                 physical_units: str = "m") -> bool:
        """
        Configure un canal pour l'acquisition maritime
        
        Args:
            channel: Numéro du canal (0-7)
            sensor_type: Type de capteur ('pressure', 'accelerometer', 'wave_height', 'temperature')
            label: Étiquette du canal
            range_volts: Plage de tension (1, 2, 5, 10)
            sensor_sensitivity: Sensibilité du capteur (V/unité physique)
            physical_units: Unités physiques
            
        Returns:
            True si la configuration réussit
        """
        if not (0 <= channel <= 7):
            logger.error(f"Numéro de canal invalide: {channel}")
            return False
        if sensor_sensitivity == 0:
            logger.error("La sensibilite du canal %s ne peut pas etre nulle", channel)
            return False
            
        # Conversion de la plage de tension
        range_mapping = {
            10.0: MCCRanges.BIP10VOLTS,
            5.0: MCCRanges.BIP5VOLTS,
            2.0: MCCRanges.BIP2VOLTS,
            1.0: MCCRanges.BIP1VOLTS
        }
        
        range_type = range_mapping.get(range_volts, MCCRanges.BIP10VOLTS)
        
        # Configuration du canal maritime
        config = MaritimeChannelConfig(
            channel=channel,
            sensor_type=sensor_type,
            label=label,
            units="V",
            range_type=range_type,
            physical_units=physical_units,
            sensor_sensitivity=sensor_sensitivity
        )
        
        self.channels_config[channel] = config
        
        # Configuration de la carte si disponible
        if self.daq:
            self.daq.configure_channel(channel, range_type, label, "V")
            
        logger.info(f"Canal maritime {channel} configuré: {sensor_type} - {label}")
        return True
        
    def get_channel_configuration(self, channel: int) -> dict[str, Any] | None:
        """
        Récupère la configuration d'un canal
        
        Args:
            channel: Numéro du canal
            
        Returns:
            Dictionnaire avec la configuration
        """
        config = self.channels_config.get(channel)
        if not config:
            return None
            
        return {
            'channel': config.channel,
            'sensor_type': config.sensor_type,
            'label': config.label,
            'range_volts': config.range_type.name,
            'physical_units': config.physical_units,
            'sensor_sensitivity': config.sensor_sensitivity,
            'enabled': config.enabled,
            'calibration_offset': config.calibration_offset,
            'calibration_scale': config.calibration_scale
        }

    def apply_calibration_record(self, record: CalibrationRecord) -> bool:
        """Applique uniquement un certificat metrologique valide au canal vise."""

        if not isinstance(record, CalibrationRecord):
            logger.error("Enregistrement de calibration invalide")
            return False
        if record.validity_status != CALIBRATION_VALID:
            logger.error("Calibration refusee: statut %s", record.validity_status)
            return False
        config = self.channels_config.get(int(record.channel))
        if config is None:
            logger.error("Calibration sans canal configure: %s", record.channel)
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
        logger.info("Calibration %s appliquee au canal %s", record.calibration_id, record.channel)
        return True
        
    def start_acquisition_session(self,
                                project_name: str,
                                sampling_rate: float = 1000.0,
                                duration_seconds: float | None = None,
                                channels: list[int] | None = None,
                                recording_directory: str | None = None) -> bool:
        """
        Démarre une session d'acquisition
        
        Args:
            project_name: Nom du projet
            sampling_rate: Fréquence d'échantillonnage (Hz)
            duration_seconds: Durée d'acquisition (None = continue)
            channels: Liste des canaux à acquérir (None = tous configurés)
            recording_directory: Repertoire du fichier HDF5 alimente en continu
            
        Returns:
            True si l'acquisition démarre
        """
        if self.is_acquiring:
            logger.error("Acquisition déjà en cours")
            return False
        if sampling_rate <= 0:
            logger.error("Frequence d'echantillonnage invalide: %s", sampling_rate)
            return False
            
        if not self.is_hardware_available() and not self._simulation_mode():
            logger.error("Matériel non disponible")
            return False
            
        # Détermination des canaux à utiliser
        if channels is None:
            channels = list(self.channels_config.keys())
            
        if not channels:
            logger.error("Aucun canal configuré")
            return False
        missing_channels = [channel for channel in channels if channel not in self.channels_config]
        if missing_channels:
            logger.error("Canaux non configures: %s", missing_channels)
            return False

        selected_configs = [self.channels_config[channel] for channel in channels]

        with self._data_lock:
            self.data_buffer.clear()
        self._simulation_sample_index = 0
        self.stats = {
            'samples_acquired': 0,
            'acquisition_rate': 0.0,
            'last_update': None,
            'errors': 0,
            'buffer_overruns': 0,
            'recording_errors': 0,
        }
            
        # Création de la session
        session_start = datetime.now()
        project_slug = re.sub(r"[^A-Za-z0-9._-]+", "_", project_name.strip())
        project_slug = project_slug.strip("._-")[:80] or "Acquisition_Maritime"
        session_id = f"{project_slug}_{session_start.strftime('%Y%m%d_%H%M%S_%f')[:-3]}"
        self.current_session = AcquisitionSession(
            session_id=session_id,
            project_name=project_name,
            start_time=session_start,
            sampling_rate=sampling_rate,
            channels=selected_configs,
            metadata={
                'duration_seconds': duration_seconds,
                'selected_channels': channels,
                'hardware_available': self.is_hardware_available()
            }
        )
        
        # Démarrage de l'acquisition
        try:
            if self._daq_backend is not None:
                actual_rate = self._daq_backend.start(
                    sample_rate_hz=sampling_rate,
                    channels=selected_configs,
                    chunk_size=min(self.buffer_size, 1000),
                )
                self.current_session.sampling_rate = float(actual_rate)
                self.current_session.metadata.update(self._daq_backend.metadata())
                self.current_session.metadata['requested_sampling_rate'] = sampling_rate
                self.current_session.metadata['actual_sampling_rate'] = float(actual_rate)
            elif self.daq:
                # Configuration matérielle
                self.daq.clear_channels()
                for channel_config in selected_configs:
                    self.daq.configure_channel(
                        channel_config.channel,
                        channel_config.range_type,
                        channel_config.label,
                        "V",
                    )
                low_chan = min(channels)
                high_chan = max(channels)
                
                success = self.daq.start_continuous_acquisition(
                    low_chan=low_chan,
                    high_chan=high_chan,
                    rate=sampling_rate,
                    buffer_size=self.buffer_size
                )
                
                if not success:
                    logger.error("Erreur de démarrage de l'acquisition matérielle")
                    self.current_session = None
                    return False
                self.current_session.sampling_rate = self.daq.acquisition_config.rate
                self.current_session.metadata['requested_sampling_rate'] = sampling_rate
                self.current_session.metadata['actual_sampling_rate'] = self.daq.acquisition_config.rate

            if duration_seconds is not None:
                self.current_session.metadata['expected_samples'] = max(
                    1,
                    int(round(duration_seconds * self.current_session.sampling_rate)),
                )

            if recording_directory:
                recording_path = Path(recording_directory) / f"{session_id}.h5"
                self._recorder = self._recorder_factory()
                resolved_path = self._recorder.start(recording_path, self.current_session)
                self.current_session.data_file_path = str(resolved_path)
                self.current_session.metadata['recording_path'] = str(resolved_path)
                logger.info("Enregistrement continu active: %s", resolved_path)
                    
            # Démarrage du thread d'acquisition
            self.is_acquiring = True
            self.acquisition_thread = threading.Thread(
                target=self._acquisition_loop,
                args=(duration_seconds,),
                daemon=True
            )
            self.acquisition_thread.start()
            
            logger.info(f"Session d'acquisition démarrée: {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors du démarrage: {e}")
            if self._recorder:
                self._recorder.close()
                self._recorder = None
            if self.daq:
                self.daq.stop_acquisition()
            self.current_session = None
            return False
            
    def _acquisition_loop(self, duration_seconds: float | None):
        """Boucle principale d'acquisition"""
        start_time = time.monotonic()
        last_stats_update = start_time
        samples_since_last_update = 0
        next_simulation_deadline = start_time
        target_samples = (
            int(self.current_session.metadata.get('expected_samples', 0))
            if self.current_session and duration_seconds is not None
            else None
        )
        acquisition_deadline = (
            start_time + duration_seconds + max(2.0, duration_seconds * 0.1)
            if duration_seconds is not None
            else None
        )
        
        try:
            while self.is_acquiring:
                if target_samples is not None and self.stats['samples_acquired'] >= target_samples:
                    logger.info("Durée d'acquisition atteinte")
                    break
                if acquisition_deadline and time.monotonic() >= acquisition_deadline:
                    logger.error(
                        "Acquisition incomplete: %s/%s echantillons",
                        self.stats['samples_acquired'],
                        target_samples,
                    )
                    self.stats['errors'] += 1
                    self.current_session.metadata['incomplete_reason'] = 'acquisition_timeout'
                    break

                block_samples = 100
                if target_samples is not None:
                    block_samples = min(
                        block_samples,
                        target_samples - self.stats['samples_acquired'],
                    )
                    
                # Acquisition des données
                if self._daq_backend is not None:
                    result = self._daq_backend.read(num_samples=block_samples)
                    if result is None:
                        break
                    data = result.raw_data
                    if result.warnings and self.current_session:
                        self.current_session.metadata.setdefault('warnings', []).extend(
                            result.warnings
                        )
                    self._process_acquired_data(data)
                    samples_since_last_update += data.shape[0]
                elif self.daq:
                    # Acquisition matérielle
                    data = self.daq.wait_for_data(num_samples=block_samples, timeout=0.25)
                    if data is not None:
                        self._process_acquired_data(data)
                        samples_since_last_update += data.shape[0]
                else:
                    # Mode simulation
                    data = self._generate_simulation_data(block_samples)
                    self._process_acquired_data(data)
                    samples_since_last_update += data.shape[0]
                    next_simulation_deadline += data.shape[0] / self.current_session.sampling_rate
                    sleep_duration = next_simulation_deadline - time.monotonic()
                    if sleep_duration > 0:
                        time.sleep(sleep_duration)
                    
                # Mise à jour des statistiques
                current_time = time.monotonic()
                if current_time - last_stats_update >= 1.0:  # Chaque seconde
                    self.stats['acquisition_rate'] = samples_since_last_update / (
                        current_time - last_stats_update
                    )
                    self.stats['last_update'] = datetime.now()
                    samples_since_last_update = 0
                    last_stats_update = current_time
                    
        except MCCBackendError as e:
            logger.error("Erreur MCC dans la boucle d'acquisition: %s", e)
            self.stats['errors'] += 1
            if self.daq:
                self.stats['buffer_overruns'] = self.daq.buffer_overruns
        except Exception as e:
            logger.error(f"Erreur dans la boucle d'acquisition: {e}")
            self.stats['errors'] += 1
            if isinstance(e, RecordingError):
                self.stats['recording_errors'] += 1
            
        finally:
            self._finalize_acquisition()
            
    def _process_acquired_data(self, raw_data: np.ndarray):
        """
        Traite les données acquises
        
        Args:
            raw_data: Données brutes [samples, channels]
        """
        if raw_data is None or raw_data.size == 0:
            return
            
        # Conversion en unités physiques
        processed_data = self._convert_to_physical_units(raw_data)

        # Le disque est la source complete. Une erreur d'ecriture interrompt la
        # session afin de ne jamais annoncer une acquisition non sauvegardee.
        if self._recorder:
            self._recorder.append(raw_data, processed_data)
        
        # Ajout au buffer
        with self._data_lock:
            self.data_buffer.append({
                'timestamp': datetime.now(),
                'raw_data': raw_data.copy(),
                'processed_data': processed_data,
                'sample_count': raw_data.shape[0]
            })

            # Buffer d'aperçu temporaire pour l'affichage en temps reel.
            if len(self.data_buffer) > 1000:
                self.data_buffer.pop(0)
            
        # Mise à jour des statistiques
        self.stats['samples_acquired'] += raw_data.shape[0]
        
        # Callback utilisateur
        if self.data_callback:
            try:
                self.data_callback(processed_data, self.current_session)
            except Exception as e:
                logger.error(f"Erreur dans le callback utilisateur: {e}")
                
    def _convert_to_physical_units(self, raw_data: np.ndarray) -> np.ndarray:
        """Convertit les données en unités physiques"""
        if self.current_session is None:
            return raw_data
            
        processed_data = np.zeros(raw_data.shape, dtype=np.float64)
        
        for i, channel_config in enumerate(self.current_session.channels):
            if i < raw_data.shape[1]:
                # Application de la calibration et de la sensibilité
                channel_data = raw_data[:, i]
                channel_data = (
                    channel_data + channel_config.calibration_offset
                ) * channel_config.calibration_scale
                channel_data = channel_data / channel_config.sensor_sensitivity
                processed_data[:, i] = channel_data
                
        return processed_data
        
    def _generate_simulation_data(self, num_samples: int = 100) -> np.ndarray:
        """Génère des données de simulation pour les tests"""
        if not self.current_session:
            return np.array([])
            
        num_channels = len(self.current_session.channels)
        # Axe temporel continu respectant exactement la frequence demandee.
        sample_rate = self.current_session.sampling_rate
        sample_indices = self._simulation_sample_index + np.arange(num_samples)
        t = sample_indices / sample_rate
        data = np.zeros((num_samples, num_channels))
        
        for i, channel_config in enumerate(self.current_session.channels):
            if channel_config.sensor_type == 'wave_height':
                # Signal de houle sinusoïdal avec bruit
                frequency = 0.2 + 0.05 * i
                physical_signal = 0.5 * np.sin(2 * np.pi * frequency * t)
                noise = 0.005 * np.random.normal(0, 1, num_samples)
                data[:, i] = physical_signal * channel_config.sensor_sensitivity + noise
                
            elif channel_config.sensor_type == 'pressure':
                # Signal de pression hydrostatique
                physical_signal = 10 * np.sin(2 * np.pi * 0.05 * t)
                noise = 0.002 * np.random.normal(0, 1, num_samples)
                data[:, i] = physical_signal * channel_config.sensor_sensitivity + noise
                
            elif channel_config.sensor_type == 'accelerometer':
                # Signal d'accélération
                physical_signal = 0.5 * np.sin(2 * np.pi * 2.0 * t)
                noise = 0.002 * np.random.normal(0, 1, num_samples)
                data[:, i] = physical_signal * channel_config.sensor_sensitivity + noise
                
            else:
                # Signal générique
                data[:, i] = 0.1 * np.sin(2 * np.pi * (0.5 + i * 0.1) * t)

        self._simulation_sample_index += num_samples
                
        return data
        
    def stop_acquisition(self) -> bool:
        """
        Arrête l'acquisition en cours
        
        Returns:
            True si l'arrêt réussit
        """
        if not self.is_acquiring:
            logger.warning("Aucune acquisition en cours")
            return False
            
        logger.info("Arrêt de l'acquisition demandé")
        self.is_acquiring = False
        
        # Attente de la fin du thread
        if self.acquisition_thread and self.acquisition_thread.is_alive():
            self.acquisition_thread.join(timeout=5.0)
            
        return True
        
    def _finalize_acquisition(self):
        """Finalise la session d'acquisition"""
        if self._daq_backend is not None:
            self._daq_backend.stop()
        elif self.daq:
            self.daq.stop_acquisition()
            
        if self.current_session:
            self.current_session.end_time = datetime.now()
            self.current_session.total_samples = self.stats['samples_acquired']

            if self._recorder:
                try:
                    self._recorder.finalize(self.current_session, self.stats)
                except Exception as exc:
                    self.stats['errors'] += 1
                    self.stats['recording_errors'] += 1
                    logger.error("Erreur de finalisation HDF5: %s", exc)
                finally:
                    self._recorder = None
            
            logger.info(f"Session terminée: {self.current_session.session_id}")
            logger.info(f"Échantillons acquis: {self.current_session.total_samples}")
            
        self.is_acquiring = False
        
    def get_acquisition_status(self) -> dict[str, Any]:
        """
        Récupère le statut de l'acquisition
        
        Returns:
            Dictionnaire avec le statut complet
        """
        status = {
            'is_acquiring': self.is_acquiring,
            'hardware_available': self.is_hardware_available(),
            'statistics': self.stats.copy(),
            'session': None,
            'channels_configured': len(self.channels_config),
            'data_buffer_size': len(self.data_buffer),
            'recording_path': self.current_session.data_file_path
            if self.current_session
            else None,
        }
        
        if self.current_session:
            status['session'] = {
                'session_id': self.current_session.session_id,
                'project_name': self.current_session.project_name,
                'start_time': self.current_session.start_time.isoformat(),
                'sampling_rate': self.current_session.sampling_rate,
                'channels_count': len(self.current_session.channels),
                'duration_seconds': (datetime.now() - self.current_session.start_time).total_seconds()
            }
            
        # Statut matériel
        if self.daq:
            hw_status = self.daq.get_acquisition_status()
            status['hardware_status'] = hw_status
            
        return status
        
    def get_recent_data(self, num_samples: int = 1000) -> dict[str, Any] | None:
        """
        Récupère les données récentes
        
        Args:
            num_samples: Nombre d'échantillons à récupérer
            
        Returns:
            Dictionnaire avec les données
        """
        with self._data_lock:
            if not self.data_buffer:
                return None
            buffer_snapshot = list(self.data_buffer)
            
        # Agrégation des données récentes
        recent_samples = []
        total_samples = 0
        
        for entry in reversed(buffer_snapshot):
            if total_samples >= num_samples:
                break
                
            recent_samples.append(entry['processed_data'])
            total_samples += entry['sample_count']
            
        if not recent_samples:
            return None
            
        # Concaténation des données
        all_data = np.vstack(recent_samples[::-1])  # Ordre chronologique
        
        # Limitation au nombre demandé
        if all_data.shape[0] > num_samples:
            all_data = all_data[-num_samples:]
            
        first_sample_index = max(0, self.stats['samples_acquired'] - all_data.shape[0])
        time_interval = timedelta(seconds=1.0 / self.current_session.sampling_rate)
        timestamps = [
            self.current_session.start_time + (first_sample_index + i) * time_interval
            for i in range(all_data.shape[0])
        ]
        
        return {
            'data': all_data,
            'timestamps': timestamps,
            'channels': (
                [ch.label for ch in self.current_session.channels]
                if self.current_session
                else []
            ),
            'units': (
                [ch.physical_units for ch in self.current_session.channels]
                if self.current_session
                else []
            ),
            'sample_count': all_data.shape[0]
        }
        
    def export_session_data(self, file_path: str, format: str = 'csv') -> bool:
        """
        Exporte les données de la session
        
        Args:
            file_path: Chemin du fichier de sortie
            format: Format d'export ('csv', 'json', 'hdf5')
            
        Returns:
            True si l'export réussit
        """
        if not self.current_session or not self.data_buffer:
            logger.error("Pas de données à exporter")
            return False
            
        try:
            if format.lower() == 'csv':
                success = self._export_csv(file_path)
            elif format.lower() == 'json':
                success = self._export_json(file_path)
            elif format.lower() == 'hdf5':
                success = self._export_hdf5(file_path)
            else:
                logger.error(f"Format d'export non supporté: {format}")
                return False

            if success:
                self.last_exported_path = file_path
            return success
        except Exception as e:
            logger.error(f"Erreur lors de l'export: {e}")
            return False

    def _build_export_matrix(self) -> np.ndarray:
        """Construit une matrice [samples, channels] à partir du buffer courant."""
        if not self.data_buffer:
            return np.empty((0, 0))

        lock = getattr(self, "_data_lock", None)
        if lock is None:
            chunks = [
                entry['processed_data'].copy()
                for entry in self.data_buffer
                if 'processed_data' in entry
            ]
        else:
            with lock:
                chunks = [
                    entry['processed_data'].copy()
                    for entry in self.data_buffer
                    if 'processed_data' in entry
                ]
        if not chunks:
            return np.empty((0, 0))

        return np.vstack(chunks)

    def _build_time_vector(self, sample_count: int) -> np.ndarray:
        """Construit l'axe temporel associé aux échantillons exportés."""
        if sample_count <= 0:
            return np.array([])

        sample_rate = self.current_session.sampling_rate if self.current_session else 1.0
        if sample_rate <= 0:
            sample_rate = 1.0

        return np.arange(sample_count, dtype=float) / sample_rate

    def _export_csv(self, file_path: str) -> bool:
        """Exporte en format CSV compatible avec le post-traitement."""
        import csv

        data_matrix = self._build_export_matrix()
        if data_matrix.size == 0:
            logger.error("Aucune donnée consolidée disponible pour l'export CSV")
            return False

        time_vector = self._build_time_vector(data_matrix.shape[0])
        channel_keys = [f"channel_{config.channel:02d}" for config in self.current_session.channels]
        metadata_row = build_csv_metadata_row(
            self.current_session.sampling_rate,
            DATA_KIND_PHYSICAL,
            data_matrix.shape[0],
        )

        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)

            headers = ['time', 'sample_rate'] + list(metadata_row) + channel_keys
            writer.writerow(headers)

            for index, row in enumerate(data_matrix):
                writer.writerow(
                    [float(time_vector[index]), float(self.current_session.sampling_rate)]
                    + list(metadata_row.values())
                    + row.tolist()
                )

        sidecar = {
            'metadata': build_session_metadata(
                self.current_session,
                hardware_available=self.is_hardware_available(),
                sample_count=data_matrix.shape[0],
            ),
            'channel_metadata': build_channel_metadata(self.current_session.channels),
        }
        with open(f"{file_path}.metadata.json", 'w', encoding='utf-8') as handle:
            json.dump(sidecar, handle, indent=2, ensure_ascii=False)

        logger.info(f"Données exportées en CSV: {file_path}")
        return True

    def _export_json(self, file_path: str) -> bool:
        """Exporte en format JSON compatible avec le post-traitement."""
        data_matrix = self._build_export_matrix()
        if data_matrix.size == 0:
            logger.error("Aucune donnée consolidée disponible pour l'export JSON")
            return False

        time_vector = self._build_time_vector(data_matrix.shape[0])
        channels_payload = {}

        for index, channel in enumerate(self.current_session.channels):
            channel_key = f"channel_{channel.channel:02d}"
            channels_payload[channel_key] = data_matrix[:, index].tolist()

        metadata = build_session_metadata(
            self.current_session,
            hardware_available=self.is_hardware_available(),
            sample_count=data_matrix.shape[0],
        )
        metadata['channel_labels'] = [ch.label for ch in self.current_session.channels]
        metadata['channel_units'] = [ch.physical_units for ch in self.current_session.channels]

        export_data = {
            'metadata': metadata,
            'time': time_vector.tolist(),
            'channels': channels_payload,
            'session': {
                'session_id': self.current_session.session_id,
                'project_name': self.current_session.project_name,
                'start_time': self.current_session.start_time.isoformat(),
                'end_time': (
                    self.current_session.end_time.isoformat()
                    if self.current_session.end_time
                    else None
                ),
                'sampling_rate': self.current_session.sampling_rate,
                'total_samples': self.current_session.total_samples
            },
            'channel_metadata': build_channel_metadata(self.current_session.channels),
            'statistics': {
                **self.stats,
                'last_update': self.stats['last_update'].isoformat()
                if self.stats.get('last_update')
                else None,
            },
            'data_entries': len(self.data_buffer)
        }

        with open(file_path, 'w', encoding='utf-8') as jsonfile:
            json.dump(export_data, jsonfile, indent=2, ensure_ascii=False)

        logger.info(f"Données exportées en JSON: {file_path}")
        return True

    def _export_hdf5(self, file_path: str) -> bool:
        """Exporte un HDF5 auto-descriptif avec metadonnees metrologiques."""
        try:
            import h5py
        except ImportError:
            logger.error("h5py requis pour l'export HDF5")
            return False

        data_matrix = self._build_export_matrix()
        if data_matrix.size == 0:
            logger.error("Aucune donnée consolidée disponible pour l'export HDF5")
            return False

        metadata = build_session_metadata(
            self.current_session,
            hardware_available=self.is_hardware_available(),
            sample_count=data_matrix.shape[0],
        )
        metadata['recording_status'] = 'complete'
        metadata['errors'] = int(self.stats.get('errors', 0))
        metadata['buffer_overruns'] = int(self.stats.get('buffer_overruns', 0))
        channel_metadata = build_channel_metadata(self.current_session.channels)

        with h5py.File(file_path, 'w') as handle:
            for key, value in metadata.items():
                if value is None:
                    continue
                if isinstance(value, (str, int, float, bool, np.integer, np.floating)):
                    handle.attrs[key] = value
                else:
                    handle.attrs[key] = json.dumps(value, ensure_ascii=False)

            acquisition = handle.create_group('acquisition_data')
            for index, config in enumerate(self.current_session.channels):
                acquisition.create_dataset(
                    f"channel_{config.channel:02d}",
                    data=data_matrix[:, index],
                    compression='gzip',
                )

            metadata_group = handle.create_group('metadata')
            session_group = metadata_group.create_group('session')
            for key, value in metadata.items():
                if value is None:
                    continue
                session_group.attrs[key] = (
                    value
                    if isinstance(value, (str, int, float, bool, np.integer, np.floating))
                    else json.dumps(value, ensure_ascii=False)
                )
            channels_group = metadata_group.create_group('channels')
            for item in channel_metadata:
                channel_group = channels_group.create_group(item['key'])
                for key, value in item.items():
                    if value is None:
                        continue
                    channel_group.attrs[key] = (
                        value
                        if isinstance(value, (str, int, float, bool, np.integer, np.floating))
                        else json.dumps(value, ensure_ascii=False)
                    )

        logger.info("Donnees exportees en HDF5: %s", file_path)
        return True

    def _simulation_mode(self) -> bool:
        """Vérifie si on est en mode simulation"""
        return not self.is_hardware_available()
        
    def calibrate_system(self) -> dict[str, Any]:
        """
        Lance une calibration du système
        
        Returns:
            Résultats de calibration
        """
        if not self.is_hardware_available():
            logger.warning("Calibration en mode simulation")
            
        results = {
            'timestamp': datetime.now().isoformat(),
            'channels': {},
            'system_status': 'not_calibrated',
            'calibration_status': 'not_performed',
            'calibration_valid': False,
        }
        
        for channel, config in self.channels_config.items():
            results['channels'][channel] = {
                'channel': channel,
                'label': config.label,
                'sensor_type': config.sensor_type,
                'calibration_status': 'not_performed',
                'sensitivity_v_per_unit': config.sensor_sensitivity,
            }
            
        logger.info("Calibration système terminée")
        return results
        
    def close(self):
        """Ferme le contrôleur et libère les ressources"""
        if self.is_acquiring:
            self.stop_acquisition()
            
        if self._daq_backend is not None:
            self._daq_backend.close()
        if self.daq:
            self.daq.close()

        if self._recorder:
            self._recorder.close()
            self._recorder = None
            
        logger.info("Contrôleur d'acquisition fermé")
        
    def __enter__(self):
        """Support du context manager"""
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Support du context manager"""
        self.close()

# Fonctions utilitaires pour l'interface
def create_default_maritime_config() -> dict[int, MaritimeChannelConfig]:
    """
    Crée une configuration par défaut pour l'acquisition maritime
    
    Returns:
        Dictionnaire avec la configuration des 8 canaux
    """
    default_config = {
        0: MaritimeChannelConfig(
            channel=0,
            sensor_type='wave_height',
            label='Capteur Houle #1',
            units='V',
            range_type=MCCRanges.BIP10VOLTS,
            physical_units='m',
            sensor_sensitivity=2.0  # 2V/m
        ),
        1: MaritimeChannelConfig(
            channel=1,
            sensor_type='wave_height',
            label='Capteur Houle #2',
            units='V',
            range_type=MCCRanges.BIP10VOLTS,
            physical_units='m',
            sensor_sensitivity=2.0
        ),
        2: MaritimeChannelConfig(
            channel=2,
            sensor_type='pressure',
            label='Capteur Pression',
            units='V',
            range_type=MCCRanges.BIP5VOLTS,
            physical_units='hPa',
            sensor_sensitivity=0.01  # 0.01V/hPa
        ),
        3: MaritimeChannelConfig(
            channel=3,
            sensor_type='accelerometer',
            label='Accéléromètre X',
            units='V',
            range_type=MCCRanges.BIP10VOLTS,
            physical_units='m/s²',
            sensor_sensitivity=1.0  # 1V/(m/s²)
        ),
        4: MaritimeChannelConfig(
            channel=4,
            sensor_type='accelerometer',
            label='Accéléromètre Y',
            units='V',
            range_type=MCCRanges.BIP10VOLTS,
            physical_units='m/s²',
            sensor_sensitivity=1.0
        ),
        5: MaritimeChannelConfig(
            channel=5,
            sensor_type='accelerometer',
            label='Accéléromètre Z',
            units='V',
            range_type=MCCRanges.BIP10VOLTS,
            physical_units='m/s²',
            sensor_sensitivity=1.0
        ),
        6: MaritimeChannelConfig(
            channel=6,
            sensor_type='temperature',
            label='Température Eau',
            units='V',
            range_type=MCCRanges.BIP2VOLTS,
            physical_units='°C',
            sensor_sensitivity=0.1  # 0.1V/°C
        ),
        7: MaritimeChannelConfig(
            channel=7,
            sensor_type='wave_height',
            label='Référence Houle',
            units='V',
            range_type=MCCRanges.BIP10VOLTS,
            physical_units='m',
            sensor_sensitivity=2.0
        )
    }
    
    return default_config
    
if __name__ == "__main__":
    # Test du contrôleur d'acquisition
    print("Test du contrôleur d'acquisition maritime")
    print("=" * 50)
    
    def data_callback(data, session):
        print(f"Nouvelles données: {data.shape} - Session: {session.session_id}")
        
    with AcquisitionController(data_callback) as controller:
        print(f"Matériel disponible: {controller.is_hardware_available()}")
        print(f"Cartes détectées: {controller.get_available_boards()}")
        
        # Configuration des canaux
        controller.configure_maritime_channel(0, 'wave_height', 'Houle #1', 10.0, 2.0, 'm')
        controller.configure_maritime_channel(1, 'pressure', 'Pression', 5.0, 0.01, 'hPa')
        
        # Test d'acquisition courte
        if controller.start_acquisition_session("Test_Project", 1000.0, 5.0, [0, 1]):
            print("Acquisition démarrée...")
            time.sleep(6)  # Laisser tourner 6 secondes
            
            status = controller.get_acquisition_status()
            print(f"Statut: {status}")
            
            recent_data = controller.get_recent_data(100)
            if recent_data:
                print(f"Données récentes: {recent_data['sample_count']} échantillons")
                
        controller.stop_acquisition()
        print("Test terminé")
