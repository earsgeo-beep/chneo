#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Contrôleur d'acquisition pour CHNeoWave
Module d'interface pour l'acquisition de données maritime avec MCC DAQ USB-1608FS

Auteur: CHNeoWave Development Team
Version: 1.0.0
"""

import logging
import json
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime
from queue import Queue
from typing import Optional, Dict, List, Callable, Any

import numpy as np

from .mcc_daq_wrapper import MCCDAQ_USB1608FS, MCCRanges, scan_available_boards

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

@dataclass
class AcquisitionSession:
    """Session d'acquisition de données maritimes"""
    session_id: str
    project_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    sampling_rate: float = 1000.0
    total_samples: int = 0
    channels: List[MaritimeChannelConfig] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    data_file_path: Optional[str] = None
    
class AcquisitionController:
    """
    Contrôleur principal pour l'acquisition de données maritime
    
    Gère l'interface entre l'interface utilisateur CHNeoWave et la carte MCC DAQ,
    avec des fonctionnalités spécialisées pour l'acquisition de houle maritime.
    """
    
    def __init__(self, data_callback: Optional[Callable] = None):
        """
        Initialise le contrôleur d'acquisition
        
        Args:
            data_callback: Fonction appelée lors de nouveaux données
        """
        self.daq = None
        self.data_callback = data_callback
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
            'buffer_overruns': 0
        }
        
        # Buffer pour données
        self.data_buffer = []
        self.buffer_size = 10000
        self.last_exported_path: Optional[str] = None
        
        self._initialize_system()
        
    def _initialize_system(self):
        """Initialise le système d'acquisition"""
        try:
            # Scan des cartes disponibles
            self.available_boards = scan_available_boards()
            logger.info(f"Cartes MCC détectées: {self.available_boards}")
            
            if self.available_boards:
                # Initialisation avec la première carte
                self.daq = MCCDAQ_USB1608FS()
                if self.daq.initialize(self.available_boards[0]):
                    logger.info("Système d'acquisition initialisé")
                else:
                    logger.error("Erreur d'initialisation de la carte")
                    self.daq = None
            else:
                logger.warning("Aucune carte MCC détectée - Mode simulation")
                
        except Exception as e:
            logger.error(f"Erreur d'initialisation du système: {e}")
            
    def get_available_boards(self) -> List[int]:
        """Retourne la liste des cartes disponibles"""
        return self.available_boards.copy()
        
    def is_hardware_available(self) -> bool:
        """Vérifie si le matériel est disponible"""
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
        
    def get_channel_configuration(self, channel: int) -> Optional[Dict[str, Any]]:
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
        
    def start_acquisition_session(self,
                                project_name: str,
                                sampling_rate: float = 1000.0,
                                duration_seconds: Optional[float] = None,
                                channels: Optional[List[int]] = None) -> bool:
        """
        Démarre une session d'acquisition
        
        Args:
            project_name: Nom du projet
            sampling_rate: Fréquence d'échantillonnage (Hz)
            duration_seconds: Durée d'acquisition (None = continue)
            channels: Liste des canaux à acquérir (None = tous configurés)
            
        Returns:
            True si l'acquisition démarre
        """
        if self.is_acquiring:
            logger.error("Acquisition déjà en cours")
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
            
        # Création de la session
        session_id = f"{project_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.current_session = AcquisitionSession(
            session_id=session_id,
            project_name=project_name,
            start_time=datetime.now(),
            sampling_rate=sampling_rate,
            channels=[self.channels_config[ch] for ch in channels if ch in self.channels_config],
            metadata={
                'duration_seconds': duration_seconds,
                'selected_channels': channels,
                'hardware_available': self.is_hardware_available()
            }
        )
        
        # Démarrage de l'acquisition
        try:
            if self.daq:
                # Configuration matérielle
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
                    return False
                    
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
            self.current_session = None
            return False
            
    def _acquisition_loop(self, duration_seconds: Optional[float]):
        """Boucle principale d'acquisition"""
        start_time = time.time()
        last_stats_update = start_time
        samples_since_last_update = 0
        
        try:
            while self.is_acquiring:
                # Vérification de la durée
                if duration_seconds and (time.time() - start_time) >= duration_seconds:
                    logger.info("Durée d'acquisition atteinte")
                    break
                    
                # Acquisition des données
                if self.daq:
                    # Acquisition matérielle
                    data = self.daq.get_data(num_samples=100)
                    if data is not None:
                        self._process_acquired_data(data)
                        samples_since_last_update += data.shape[0]
                else:
                    # Mode simulation
                    data = self._generate_simulation_data()
                    self._process_acquired_data(data)
                    samples_since_last_update += data.shape[0]
                    time.sleep(0.01)  # Simulation du timing
                    
                # Mise à jour des statistiques
                current_time = time.time()
                if current_time - last_stats_update >= 1.0:  # Chaque seconde
                    self.stats['acquisition_rate'] = samples_since_last_update / (current_time - last_stats_update)
                    self.stats['last_update'] = datetime.now()
                    samples_since_last_update = 0
                    last_stats_update = current_time
                    
        except Exception as e:
            logger.error(f"Erreur dans la boucle d'acquisition: {e}")
            self.stats['errors'] += 1
            
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
        
        # Ajout au buffer
        self.data_buffer.append({
            'timestamp': datetime.now(),
            'raw_data': raw_data,
            'processed_data': processed_data,
            'sample_count': raw_data.shape[0]
        })
        
        # Limitation de la taille du buffer
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
            
        processed_data = np.zeros_like(raw_data)
        
        for i, channel_config in enumerate(self.current_session.channels):
            if i < raw_data.shape[1]:
                # Application de la calibration et de la sensibilité
                channel_data = raw_data[:, i]
                channel_data = (channel_data + channel_config.calibration_offset) * channel_config.calibration_scale
                channel_data = channel_data / channel_config.sensor_sensitivity
                processed_data[:, i] = channel_data
                
        return processed_data
        
    def _generate_simulation_data(self) -> np.ndarray:
        """Génère des données de simulation pour les tests"""
        if not self.current_session:
            return np.array([])
            
        num_channels = len(self.current_session.channels)
        num_samples = 100
        
        # Génération de signaux simulés
        t = np.linspace(0, 1, num_samples)
        data = np.zeros((num_samples, num_channels))
        
        for i, channel_config in enumerate(self.current_session.channels):
            if channel_config.sensor_type == 'wave_height':
                # Signal de houle sinusoïdal avec bruit
                frequency = 0.1 + np.random.random() * 0.5  # 0.1-0.6 Hz
                amplitude = 0.5 + np.random.random() * 1.5   # 0.5-2.0 m
                phase = np.random.random() * 2 * np.pi
                wave_signal = amplitude * np.sin(2 * np.pi * frequency * t + phase)
                noise = 0.1 * np.random.normal(0, 1, num_samples)
                data[:, i] = wave_signal + noise
                
            elif channel_config.sensor_type == 'pressure':
                # Signal de pression hydrostatique
                base_pressure = 1013.25  # hPa
                variation = 10 * np.sin(2 * np.pi * 0.05 * t)  # Variation lente
                noise = 0.5 * np.random.normal(0, 1, num_samples)
                data[:, i] = base_pressure + variation + noise
                
            elif channel_config.sensor_type == 'accelerometer':
                # Signal d'accélération
                gravity = 9.81
                vibration = 0.5 * np.sin(2 * np.pi * 2.0 * t)  # Vibration 2 Hz
                noise = 0.1 * np.random.normal(0, 1, num_samples)
                data[:, i] = gravity + vibration + noise
                
            else:
                # Signal générique
                data[:, i] = np.random.normal(0, 1, num_samples)
                
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
        if self.daq:
            self.daq.stop_acquisition()
            
        if self.current_session:
            self.current_session.end_time = datetime.now()
            self.current_session.total_samples = self.stats['samples_acquired']
            
            logger.info(f"Session terminée: {self.current_session.session_id}")
            logger.info(f"Échantillons acquis: {self.current_session.total_samples}")
            
        self.is_acquiring = False
        
    def get_acquisition_status(self) -> Dict[str, Any]:
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
            'data_buffer_size': len(self.data_buffer)
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
        
    def get_recent_data(self, num_samples: int = 1000) -> Optional[Dict[str, Any]]:
        """
        Récupère les données récentes
        
        Args:
            num_samples: Nombre d'échantillons à récupérer
            
        Returns:
            Dictionnaire avec les données
        """
        if not self.data_buffer:
            return None
            
        # Agrégation des données récentes
        recent_samples = []
        total_samples = 0
        
        for entry in reversed(self.data_buffer):
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
            
        # Création des timestamps avec timedelta
        from datetime import timedelta
        base_time = datetime.now()
        time_interval = timedelta(seconds=1.0 / self.current_session.sampling_rate)
        timestamps = [base_time - i * time_interval for i in range(all_data.shape[0])]
        
        return {
            'data': all_data,
            'timestamps': timestamps,
            'channels': [ch.label for ch in self.current_session.channels] if self.current_session else [],
            'units': [ch.physical_units for ch in self.current_session.channels] if self.current_session else [],
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

        chunks = [entry['processed_data'] for entry in self.data_buffer if 'processed_data' in entry]
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

        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)

            headers = ['time'] + channel_keys
            writer.writerow(headers)

            for index, row in enumerate(data_matrix):
                writer.writerow([float(time_vector[index])] + row.tolist())

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

        export_data = {
            'metadata': {
                'sample_rate': self.current_session.sampling_rate,
                'project_name': self.current_session.project_name,
                'session_id': self.current_session.session_id,
                'channel_labels': [ch.label for ch in self.current_session.channels],
                'channel_units': [ch.physical_units for ch in self.current_session.channels],
                'hardware_available': self.is_hardware_available()
            },
            'time': time_vector.tolist(),
            'channels': channels_payload,
            'session': {
                'session_id': self.current_session.session_id,
                'project_name': self.current_session.project_name,
                'start_time': self.current_session.start_time.isoformat(),
                'end_time': self.current_session.end_time.isoformat() if self.current_session.end_time else None,
                'sampling_rate': self.current_session.sampling_rate,
                'total_samples': self.current_session.total_samples
            },
            'channel_metadata': [
                {
                    'channel': ch.channel,
                    'sensor_type': ch.sensor_type,
                    'label': ch.label,
                    'physical_units': ch.physical_units,
                    'sensor_sensitivity': ch.sensor_sensitivity
                }
                for ch in self.current_session.channels
            ],
            'statistics': self.stats,
            'data_entries': len(self.data_buffer)
        }

        with open(file_path, 'w', encoding='utf-8') as jsonfile:
            json.dump(export_data, jsonfile, indent=2, ensure_ascii=False)

        logger.info(f"Données exportées en JSON: {file_path}")
        return True

    def _export_hdf5(self, file_path: str) -> bool:
        """Exporte en HDF5 via ExportManager avec contrat aligné sur le post-traitement."""
        from hrneowave.core.export_manager import create_export_config, create_export_manager

        data_matrix = self._build_export_matrix()
        if data_matrix.size == 0:
            logger.error("Aucune donnée consolidée disponible pour l'export HDF5")
            return False

        export_manager = create_export_manager()
        session_info = {
            'session_id': self.current_session.session_id,
            'project_name': self.current_session.project_name,
            'sample_rate': self.current_session.sampling_rate,
            'sampling_rate': self.current_session.sampling_rate,
            'start_time': self.current_session.start_time.isoformat(),
            'end_time': self.current_session.end_time.isoformat() if self.current_session.end_time else "",
            'channels_count': len(self.current_session.channels),
        }
        metadata = {
            'channel_labels': json.dumps([ch.label for ch in self.current_session.channels], ensure_ascii=False),
            'channel_units': json.dumps([ch.physical_units for ch in self.current_session.channels], ensure_ascii=False),
            'sensor_types': json.dumps([ch.sensor_type for ch in self.current_session.channels], ensure_ascii=False),
        }
        calibration_info = {
            f"channel_{config.channel:02d}": {
                'offset': config.calibration_offset,
                'scale': config.calibration_scale,
                'sensitivity': config.sensor_sensitivity,
            }
            for config in self.current_session.channels
        }

        config = create_export_config(
            'hdf5',
            file_path,
            session_info=session_info,
            metadata=metadata,
        )
        config.calibration_info = calibration_info

        # ExportManager attend [n_channels, n_samples]
        return export_manager.export_session_data(data_matrix.T, config)

    def _simulation_mode(self) -> bool:
        """Vérifie si on est en mode simulation"""
        return not self.is_hardware_available()
        
    def calibrate_system(self) -> Dict[str, Any]:
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
            'system_status': 'ok'
        }
        
        for channel, config in self.channels_config.items():
            # Simulation de calibration
            results['channels'][channel] = {
                'channel': channel,
                'label': config.label,
                'sensor_type': config.sensor_type,
                'calibration_status': 'ok',
                'offset_correction': np.random.normal(0, 0.001),
                'scale_correction': 1.0 + np.random.normal(0, 0.01),
                'noise_level': np.random.uniform(0.001, 0.01)
            }
            
        logger.info("Calibration système terminée")
        return results
        
    def close(self):
        """Ferme le contrôleur et libère les ressources"""
        if self.is_acquiring:
            self.stop_acquisition()
            
        if self.daq:
            self.daq.close()
            
        logger.info("Contrôleur d'acquisition fermé")
        
    def __enter__(self):
        """Support du context manager"""
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Support du context manager"""
        self.close()

# Fonctions utilitaires pour l'interface
def create_default_maritime_config() -> Dict[int, MaritimeChannelConfig]:
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
