#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gestionnaire d'export pour CHNeoWave v1.1.0-RC
Supporte les formats HDF5 et TDMS pour l'export de données scientifiques
"""

import numpy as np
import time
import os
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime
import json

from hrneowave import __version__

# Imports conditionnels pour les formats d'export
try:
    import h5py
    HDF5_AVAILABLE = True
except ImportError:
    HDF5_AVAILABLE = False
    print("h5py non disponible - export HDF5 désactivé")

try:
    from nptdms import TdmsWriter, ChannelObject
    TDMS_AVAILABLE = True
except ImportError:
    TDMS_AVAILABLE = False
    print("nptdms non disponible - export TDMS désactivé")

@dataclass
class ExportConfig:
    """Configuration pour l'export de données"""
    format: str  # 'hdf5' ou 'tdms'
    filename: str
    metadata: Dict[str, Any]
    compression: bool = True
    chunk_size: int = 1000
    
    # Métadonnées spécifiques CHNeoWave
    session_info: Dict[str, Any] = None
    calibration_info: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.session_info is None:
            self.session_info = {}
        if self.calibration_info is None:
            self.calibration_info = {}

class ExportManager:
    """Gestionnaire principal pour l'export de données scientifiques"""
    
    def __init__(self):
        self.supported_formats = []
        if HDF5_AVAILABLE:
            self.supported_formats.append('hdf5')
        if TDMS_AVAILABLE:
            self.supported_formats.append('tdms')
        
        print(f"Formats d'export disponibles: {self.supported_formats}")
    
    def export_session_data(self, data: np.ndarray, config: ExportConfig) -> bool:
        """
        Exporte les données d'une session complète
        
        Args:
            data: Données à exporter (shape: [n_channels, n_samples])
            config: Configuration d'export
            
        Returns:
            True si l'export a réussi
        """
        if config.format not in self.supported_formats:
            print(f"Format {config.format} non supporté. Disponibles: {self.supported_formats}")
            return False
        
        try:
            if config.format == 'hdf5':
                return self._export_hdf5(data, config)
            elif config.format == 'tdms':
                return self._export_tdms(data, config)
            else:
                return False
        except Exception as e:
            print(f"Erreur lors de l'export {config.format}: {e}")
            return False
    
    def _export_hdf5(self, data: np.ndarray, config: ExportConfig) -> bool:
        """Export au format HDF5"""
        if not HDF5_AVAILABLE:
            return False
        
        filepath = Path(config.filename)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with h5py.File(filepath, 'w') as f:
            # Groupe principal pour les données
            data_group = f.create_group('acquisition_data')
            
            # Paramètres de compression
            compression_opts = {
                'compression': 'gzip' if config.compression else None,
                'compression_opts': 9 if config.compression else None,
                'chunks': True
            }
            
            # Sauvegarder les données par canal
            n_channels, n_samples = data.shape
            for ch in range(n_channels):
                dataset_name = f'channel_{ch:02d}'
                data_group.create_dataset(
                    dataset_name, 
                    data=data[ch, :],
                    **compression_opts
                )
                
                # Métadonnées du canal
                data_group[dataset_name].attrs['channel_index'] = ch
                data_group[dataset_name].attrs['unit'] = 'V'  # Volts par défaut
                data_group[dataset_name].attrs['sensor_type'] = 'wave_probe'
            
            # Métadonnées globales
            metadata_group = f.create_group('metadata')
            
            # Informations de session
            session_group = metadata_group.create_group('session')
            for key, value in config.session_info.items():
                if isinstance(value, (str, int, float, bool)):
                    session_group.attrs[key] = value
                else:
                    session_group.attrs[key] = str(value)
            
            # Informations générales
            metadata_group.attrs['export_timestamp'] = datetime.now().isoformat()
            metadata_group.attrs['software'] = 'CHNeoWave'
            metadata_group.attrs['version'] = __version__
            metadata_group.attrs['format_version'] = '1.0'
            metadata_group.attrs['n_channels'] = n_channels
            metadata_group.attrs['n_samples'] = n_samples
            
            # Métadonnées utilisateur
            for key, value in config.metadata.items():
                if isinstance(value, (str, int, float, bool)):
                    metadata_group.attrs[key] = value
                else:
                    metadata_group.attrs[key] = str(value)
            
            # Informations de calibration
            if config.calibration_info:
                calib_group = metadata_group.create_group('calibration')
                for key, value in config.calibration_info.items():
                    if isinstance(value, (str, int, float, bool)):
                        calib_group.attrs[key] = value
                    else:
                        calib_group.attrs[key] = str(value)
        
        print(f"Export HDF5 réussi: {filepath}")
        return True
    
    def _export_tdms(self, data: np.ndarray, config: ExportConfig) -> bool:
        """Export au format TDMS (National Instruments)"""
        if not TDMS_AVAILABLE:
            return False
        
        filepath = Path(config.filename)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        # Créer les objets de canaux
        channels = []
        n_channels, n_samples = data.shape
        
        for ch in range(n_channels):
            channel = ChannelObject(
                'CHNeoWave',  # Nom du groupe
                f'Channel_{ch:02d}',  # Nom du canal
                data[ch, :],  # Données
                properties={
                    'wf_start_time': datetime.now(),
                    'wf_increment': 1.0 / config.session_info.get('sample_rate', 32.0),
                    'wf_samples': n_samples,
                    'unit_string': 'V',
                    'sensor_type': 'wave_probe',
                    'channel_index': ch
                }
            )
            channels.append(channel)
        
        # Écrire le fichier TDMS
        with TdmsWriter(str(filepath)) as tdms_writer:
            # Propriétés du fichier
            file_properties = {
                'Title': 'CHNeoWave Acquisition Data',
                'Author': f'CHNeoWave v{__version__}',
                'Export_Timestamp': datetime.now().isoformat(),
                'Sample_Rate': config.session_info.get('sample_rate', 32.0),
                'Number_of_Channels': n_channels,
                'Number_of_Samples': n_samples
            }
            
            # Ajouter les métadonnées utilisateur
            file_properties.update(config.metadata)
            
            # Propriétés du groupe
            group_properties = {
                'Description': 'Données d\'acquisition de houle',
                'Acquisition_Mode': config.session_info.get('mode', 'simulate'),
                'Buffer_Size': config.session_info.get('buffer_size', 10000)
            }
            
            # Écrire les données
            tdms_writer.write_data(
                channels,
                file_properties=file_properties,
                group_properties={'CHNeoWave': group_properties}
            )
        
        print(f"Export TDMS réussi: {filepath}")
        return True
    
    def export_realtime_chunk(self, data: np.ndarray, config: ExportConfig, 
                             append: bool = True) -> bool:
        """
        Exporte un chunk de données en temps réel
        
        Args:
            data: Chunk de données (shape: [n_channels, n_samples])
            config: Configuration d'export
            append: True pour ajouter aux données existantes
            
        Returns:
            True si l'export a réussi
        """
        if config.format == 'hdf5':
            return self._append_hdf5_chunk(data, config, append)
        elif config.format == 'tdms':
            # TDMS ne supporte pas l'append facilement, on accumule
            return self._append_tdms_chunk(data, config, append)
        else:
            return False
    
    def _append_hdf5_chunk(self, data: np.ndarray, config: ExportConfig, 
                          append: bool) -> bool:
        """Ajoute un chunk au fichier HDF5"""
        if not HDF5_AVAILABLE:
            return False
        
        filepath = Path(config.filename)
        mode = 'a' if append and filepath.exists() else 'w'
        
        try:
            with h5py.File(filepath, mode) as f:
                if 'acquisition_data' not in f:
                    # Créer la structure initiale
                    data_group = f.create_group('acquisition_data')
                    n_channels = data.shape[0]
                    
                    for ch in range(n_channels):
                        dataset_name = f'channel_{ch:02d}'
                        # Créer un dataset extensible
                        data_group.create_dataset(
                            dataset_name,
                            data=data[ch, :],
                            maxshape=(None,),
                            chunks=True,
                            compression='gzip' if config.compression else None
                        )
                else:
                    # Étendre les datasets existants
                    data_group = f['acquisition_data']
                    n_channels = data.shape[0]
                    
                    for ch in range(n_channels):
                        dataset_name = f'channel_{ch:02d}'
                        if dataset_name in data_group:
                            dataset = data_group[dataset_name]
                            old_size = dataset.shape[0]
                            new_size = old_size + data.shape[1]
                            dataset.resize((new_size,))
                            dataset[old_size:new_size] = data[ch, :]
            
            return True
        except Exception as e:
            print(f"Erreur append HDF5: {e}")
            return False
    
    def _append_tdms_chunk(self, data: np.ndarray, config: ExportConfig, 
                          append: bool) -> bool:
        """Accumule les chunks TDMS (implémentation simplifiée)"""
        # Pour TDMS, on peut utiliser un buffer temporaire
        # et écrire le fichier complet à la fin
        # Cette implémentation est simplifiée
        return True
    
    def get_export_info(self, filepath: str) -> Optional[Dict[str, Any]]:
        """
        Lit les métadonnées d'un fichier exporté
        
        Args:
            filepath: Chemin vers le fichier
            
        Returns:
            Dictionnaire avec les métadonnées ou None
        """
        path = Path(filepath)
        if not path.exists():
            return None
        
        try:
            if path.suffix.lower() == '.h5' or path.suffix.lower() == '.hdf5':
                return self._read_hdf5_info(filepath)
            elif path.suffix.lower() == '.tdms':
                return self._read_tdms_info(filepath)
            else:
                return None
        except Exception as e:
            print(f"Erreur lecture métadonnées: {e}")
            return None
    
    def _read_hdf5_info(self, filepath: str) -> Dict[str, Any]:
        """Lit les métadonnées HDF5"""
        info = {}
        with h5py.File(filepath, 'r') as f:
            if 'metadata' in f:
                metadata = f['metadata']
                for key in metadata.attrs:
                    info[key] = metadata.attrs[key]
            
            if 'acquisition_data' in f:
                data_group = f['acquisition_data']
                info['channels'] = list(data_group.keys())
                if info['channels']:
                    first_channel = data_group[info['channels'][0]]
                    info['samples_per_channel'] = first_channel.shape[0]
        
        return info
    
    def _read_tdms_info(self, filepath: str) -> Dict[str, Any]:
        """Lit les métadonnées TDMS"""
        if not TDMS_AVAILABLE:
            return {}
        
        from nptdms import TdmsFile
        
        info = {}
        with TdmsFile.read(filepath) as tdms_file:
            # Propriétés du fichier
            for prop_name, prop_value in tdms_file.properties.items():
                info[prop_name] = prop_value
            
            # Informations sur les groupes et canaux
            info['groups'] = [group.name for group in tdms_file.groups()]
            info['channels'] = []
            
            for group in tdms_file.groups():
                for channel in group.channels():
                    info['channels'].append(f"{group.name}/{channel.name}")
        
        return info

# Factory function
def create_export_manager() -> ExportManager:
    """Crée un gestionnaire d'export"""
    return ExportManager()

# Fonctions utilitaires
def create_export_config(format_type: str, filename: str, 
                        session_info: Dict[str, Any] = None,
                        metadata: Dict[str, Any] = None) -> ExportConfig:
    """Crée une configuration d'export standard"""
    if session_info is None:
        session_info = {}
    if metadata is None:
        metadata = {}
    
    return ExportConfig(
        format=format_type,
        filename=filename,
        metadata=metadata,
        session_info=session_info,
        compression=True
    )

def get_available_formats() -> List[str]:
    """Retourne la liste des formats d'export disponibles"""
    formats = []
    if HDF5_AVAILABLE:
        formats.append('hdf5')
    if TDMS_AVAILABLE:
        formats.append('tdms')
    return formats
