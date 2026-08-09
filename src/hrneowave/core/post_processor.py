"""Chargement, analyse scientifique et export des donnees CHNeoWave."""

from __future__ import annotations

import json
import os
from copy import deepcopy
from pathlib import Path
from typing import Any

import numpy as np
from scipy import signal

from .session_schema import CLOCK_DOMAIN, SAMPLE_RATE_KEYS, SCHEMA_VERSION, extract_sample_rate
from .wave_analysis import WaveAnalysisConfig, WaveAnalysisError, WaveAnalyzer
from .wave_separation import (
    MultiProbeWaveSeparator,
    WaveSeparationConfig,
    WaveSeparationError,
)

QObject = None
Signal = None


def _ensure_qt_imports() -> None:
    """Importe Qt conditionnellement pour garder le moteur testable sans GUI."""
    global QObject, Signal
    if QObject is not None:
        return
    try:
        from PySide6.QtCore import QObject, Signal
    except ImportError:
        QObject = object

        class MockSignal:
            def __init__(self, *args, **kwargs):
                pass

            def emit(self, *args, **kwargs):
                pass

        Signal = MockSignal


_ensure_qt_imports()


class PostProcessor(QObject):
    """Orchestre l'analyse canal par canal sans charger un long HDF5 en bloc."""

    dataLoaded = Signal(dict)
    analysisCompleted = Signal(dict)
    exportCompleted = Signal(str)
    errorOccurred = Signal(str)

    def __init__(self, config_path: str | None = None):
        super().__init__()
        self.config = self._load_config(config_path)
        self.current_data: dict[str, Any] | None = None
        self.current_analysis: dict[str, Any] | None = None
        self.sample_rate = 32.0
        self.source_file: str | None = None

    def _load_config(self, config_path: str | None) -> dict[str, Any]:
        config = {
            "analysis": {
                "window_size": 1024,
                "overlap": 0.5,
                "window": "hann",
                "detrend": True,
                "min_frequency": 0.0,
                "max_frequency": None,
                "minimum_samples": 32,
            },
            "export": {"formats": ["csv", "json", "hdf5"], "precision": 6},
        }
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, encoding="utf-8") as handle:
                    self._deep_update(config, json.load(handle))
            except Exception as exc:
                raise ValueError(f"Configuration d'analyse invalide: {exc}") from exc
        return config

    @staticmethod
    def _deep_update(target: dict[str, Any], update: dict[str, Any]) -> None:
        for key, value in update.items():
            if isinstance(value, dict) and isinstance(target.get(key), dict):
                PostProcessor._deep_update(target[key], value)
            else:
                target[key] = value

    def _wave_config(self) -> WaveAnalysisConfig:
        analysis = self.config["analysis"]
        return WaveAnalysisConfig(
            segment_length=int(analysis.get("window_size", 1024)),
            overlap_ratio=float(analysis.get("overlap", 0.5)),
            window=str(analysis.get("window", "hann")),
            detrend=bool(analysis.get("detrend", True)),
            min_frequency=float(analysis.get("min_frequency", 0.0)),
            max_frequency=(
                float(analysis["max_frequency"]) if analysis.get("max_frequency") is not None else None
            ),
            minimum_samples=int(analysis.get("minimum_samples", 32)),
        )

    @staticmethod
    def _normalize_metadata_value(value: Any) -> Any:
        if isinstance(value, bytes):
            value = value.decode("utf-8", errors="replace")
        if isinstance(value, np.generic):
            return value.item()
        if isinstance(value, str):
            stripped = value.strip()
            if stripped.startswith(("[", "{")):
                try:
                    return json.loads(stripped)
                except json.JSONDecodeError:
                    return value
        return value

    @staticmethod
    def _validate_acquisition_integrity(
        metadata: dict[str, Any],
        statistics: dict[str, Any] | None,
        source_format: str,
    ) -> None:
        """Refuse les sessions CHNeoWave incomplètes ou non matérielles."""

        counters = dict(statistics or {})
        for key in ("errors", "buffer_overruns", "recording_errors"):
            counters.setdefault(key, metadata.get(key, 0))
            if int(counters.get(key, 0) or 0) > 0:
                raise ValueError(
                    f"Session {source_format} contenant {key}={counters[key]}"
                )
        status = metadata.get("recording_status")
        if status is not None and str(status) != "complete":
            raise ValueError(
                f"Session {source_format} non valide: recording_status={status}"
            )
        if metadata.get("hardware_available") is False:
            raise ValueError(f"Session {source_format} non issue d'un équipement physique")
        source_kind = metadata.get("acquisition_source")
        if source_kind is not None and source_kind != "physical_hardware":
            raise ValueError(f"Source d'acquisition interdite: {source_kind}")

    def load_data_file(self, file_path: str) -> bool:
        try:
            path = Path(file_path).expanduser().resolve()
            if not path.is_file():
                raise FileNotFoundError(f"Fichier introuvable: {path}")
            extension = path.suffix.lower()
            if extension == ".csv":
                data = self._load_csv(path)
            elif extension == ".json":
                data = self._load_json(path)
            elif extension in {".h5", ".hdf5"}:
                data = self._load_hdf5(path)
            else:
                raise ValueError(f"Format non supporte: {extension}")

            if not data.get("channel_keys"):
                raise ValueError("Aucun canal exploitable dans le fichier")
            self.source_file = str(path)
            self.current_data = data
            self.current_analysis = None
            self.dataLoaded.emit(data)
            print(f"Donnees chargees: {path}")
            return True
        except Exception as exc:
            message = f"Erreur chargement donnees: {exc}"
            self.errorOccurred.emit(message)
            print(message)
            return False

    def _load_csv(self, file_path: Path) -> dict[str, Any]:
        import pandas as pd

        frame = pd.read_csv(file_path)
        if frame.empty:
            raise ValueError("Le fichier CSV est vide")

        normalized_columns = {column.strip().lower(): column for column in frame.columns}
        time_column = next(
            (
                normalized_columns[alias]
                for alias in ("time", "t", "time_s", "timestamp_s")
                if alias in normalized_columns
            ),
            None,
        )
        time_columns = [time_column] if time_column else []
        data_columns = [column for column in frame.columns if column.startswith(("channel_", "probe_"))]
        metadata: dict[str, Any] = {}
        sample_rate_column = next(
            (key for key in SAMPLE_RATE_KEYS if key in frame.columns),
            None,
        )
        if sample_rate_column:
            sample_rates = frame[sample_rate_column].dropna().astype(float)
            if sample_rates.empty or sample_rates.iloc[0] <= 0:
                raise ValueError("Frequence d'echantillonnage CSV invalide")
            if not np.allclose(sample_rates, sample_rates.iloc[0]):
                raise ValueError("La frequence d'echantillonnage varie dans le CSV")
            self.sample_rate = float(sample_rates.iloc[0])
        elif time_columns:
            self.sample_rate = self._infer_sample_rate(frame[time_columns[0]].to_numpy())
        else:
            raise ValueError("Le CSV ne contient ni sample_rate ni axe temporel")
        metadata["sample_rate"] = self.sample_rate
        metadata["sample_rate_hz"] = self.sample_rate

        if time_columns:
            inferred_rate = self._infer_sample_rate(frame[time_columns[0]].to_numpy())
            if not np.isclose(inferred_rate, self.sample_rate, rtol=1e-3, atol=1e-9):
                raise ValueError("L'axe temporel ne correspond pas a sample_rate_hz")

        channels = {column: frame[column].to_numpy(dtype=np.float64) for column in data_columns}
        time_values = (
            frame[time_columns[0]].to_numpy(dtype=np.float64)
            if time_columns
            else np.arange(len(frame), dtype=np.float64) / self.sample_rate
        )
        self._validate_channel_arrays(channels, time_values, "CSV")
        sample_count = int(len(time_values))
        metadata.update(
            {
                "schema_version": SCHEMA_VERSION,
                "dt_seconds": 1.0 / self.sample_rate,
                "n_samples": sample_count,
                "duration_s": sample_count / self.sample_rate,
                "time_start": float(time_values[0]),
                "time_end": float(time_values[-1]),
                "clock_domain": CLOCK_DOMAIN,
            }
        )
        channel_metadata: list[dict[str, Any]] = []
        sidecar_statistics: dict[str, Any] = {}
        sidecar_path = Path(f"{file_path}.metadata.json")
        if sidecar_path.is_file():
            with sidecar_path.open("r", encoding="utf-8") as handle:
                sidecar = json.load(handle)
            channel_metadata = list(sidecar.get("channel_metadata", []))
            sidecar_statistics = dict(sidecar.get("statistics", {}))
            sidecar_metadata = {
                key: self._normalize_metadata_value(value)
                for key, value in sidecar.get("metadata", {}).items()
            }
            sidecar_rate = extract_sample_rate(sidecar_metadata)
            if sidecar_rate is not None and not np.isclose(
                sidecar_rate,
                self.sample_rate,
                rtol=1e-9,
                atol=1e-12,
            ):
                raise ValueError("La frequence d'echantillonnage du sidecar CSV est incoherente")
            for key, value in sidecar_metadata.items():
                if key not in metadata:
                    metadata[key] = value

        self._validate_acquisition_integrity(metadata, sidecar_statistics, "CSV")

        return {
            "source_format": "csv",
            "metadata": metadata,
            "time": time_values,
            "channels": channels,
            "channel_keys": list(channels),
            "channel_metadata": channel_metadata,
        }

    def _load_json(self, file_path: Path) -> dict[str, Any]:
        with file_path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        channels_payload = payload.get("channels", {})
        channels = {key: np.asarray(values, dtype=np.float64) for key, values in channels_payload.items()}
        raw_channels = {
            key: np.asarray(values, dtype=np.float64)
            for key, values in payload.get("raw_channels", {}).items()
        }
        time_values = np.asarray(payload.get("time", []), dtype=np.float64)
        metadata = {
            key: self._normalize_metadata_value(value) for key, value in payload.get("metadata", {}).items()
        }
        self._validate_acquisition_integrity(
            metadata,
            dict(payload.get("statistics", {})),
            "JSON",
        )
        session = payload.get("session", {})
        sample_rate = extract_sample_rate(metadata, session)
        if sample_rate is None and time_values.size:
            sample_rate = self._infer_sample_rate(time_values)
        if sample_rate is None or float(sample_rate) <= 0:
            raise ValueError("Frequence d'echantillonnage JSON absente ou invalide")
        self.sample_rate = float(sample_rate)
        if time_values.size:
            self._validate_time_axis(
                time_values,
                self.sample_rate,
                self._validate_channel_arrays(channels, None, "JSON"),
                "JSON",
            )
        else:
            sample_count = self._validate_channel_arrays(channels, None, "JSON")
            time_values = np.arange(sample_count, dtype=np.float64) / self.sample_rate
        if raw_channels:
            if set(raw_channels) != set(channels):
                raise ValueError("Les listes de canaux bruts et physiques JSON sont differentes")
            self._validate_channel_arrays(raw_channels, time_values, "JSON brut")

        return {
            "source_format": "json",
            "metadata": metadata,
            "session": session,
            "time": time_values,
            "channels": channels,
            "raw_channels": raw_channels,
            "channel_keys": list(channels),
            "channel_metadata": list(payload.get("channel_metadata", [])),
        }

    def _load_hdf5(self, file_path: Path) -> dict[str, Any]:
        try:
            import h5py
        except ImportError as exc:
            raise ImportError("h5py requis pour les fichiers HDF5") from exc

        metadata: dict[str, Any] = {}
        session: dict[str, Any] = {}
        channel_metadata: dict[str, dict[str, Any]] = {}
        integrity_warnings: list[str] = []
        sampled_time: np.ndarray | None = None
        sampled_time_indices: np.ndarray | None = None
        with h5py.File(file_path, "r") as handle:
            metadata.update(
                {key: self._normalize_metadata_value(value) for key, value in handle.attrs.items()}
            )
            status = metadata.get("recording_status")
            if status is not None and str(status) != "complete":
                raise ValueError(f"Session HDF5 non valide: recording_status={status}")
            if int(metadata.get("errors", 0)) > 0:
                raise ValueError("Session HDF5 contenant des erreurs d'acquisition")
            if int(metadata.get("buffer_overruns", 0)) > 0:
                raise ValueError("Session HDF5 contenant des debordements de buffer")

            if "metadata/session" in handle:
                session = {
                    key: self._normalize_metadata_value(value)
                    for key, value in handle["metadata/session"].attrs.items()
                }
                metadata.update(session)
            self._validate_acquisition_integrity(metadata, None, "HDF5")
            if "metadata/channels" in handle:
                for key, group in handle["metadata/channels"].items():
                    channel_metadata[key] = {
                        name: self._normalize_metadata_value(value) for name, value in group.attrs.items()
                    }
                    channel_metadata[key].setdefault("key", key)

            acquisition_group = handle.get("acquisition_data")
            if acquisition_group is not None:
                channel_keys = sorted(
                    key for key in acquisition_group.keys() if key.startswith(("channel_", "probe_"))
                )
            else:
                channel_keys = sorted(key for key in handle.keys() if key.startswith(("channel_", "probe_")))

            channel_lengths = []
            for key in channel_keys:
                dataset = acquisition_group[key] if acquisition_group is not None else handle[key]
                if dataset.ndim != 1:
                    raise ValueError(f"Le canal {key} n'est pas un vecteur")
                channel_lengths.append(int(dataset.shape[0]))
            if len(set(channel_lengths)) > 1:
                raise ValueError("Les canaux HDF5 n'ont pas la meme longueur")
            declared_samples = metadata.get("n_samples")
            if (
                declared_samples is not None
                and channel_lengths
                and int(declared_samples) != channel_lengths[0]
            ):
                raise ValueError("Le compteur n_samples ne correspond pas aux donnees")

            if acquisition_group is not None and "time" in acquisition_group:
                time_dataset = acquisition_group["time"]
                if time_dataset.ndim != 1:
                    raise ValueError("L'axe temporel HDF5 n'est pas un vecteur")
                if channel_lengths and int(time_dataset.shape[0]) != channel_lengths[0]:
                    raise ValueError("L'axe temporel HDF5 n'a pas la longueur des canaux")
                if int(time_dataset.shape[0]) >= 2:
                    sampled_time_indices = np.unique(
                        np.linspace(
                            0,
                            int(time_dataset.shape[0]) - 1,
                            min(int(time_dataset.shape[0]), 4096),
                            dtype=int,
                        )
                    )
                    sampled_time = np.asarray(
                        time_dataset[sampled_time_indices],
                        dtype=np.float64,
                    )
            else:
                integrity_warnings.append("Axe temporel HDF5 absent: temps reconstruit depuis sample_rate_hz")

        sample_rate = extract_sample_rate(metadata, session)
        if sample_rate is None or float(sample_rate) <= 0:
            raise ValueError("Frequence d'echantillonnage HDF5 absente ou invalide")
        self.sample_rate = float(sample_rate)
        if sampled_time is not None and sampled_time_indices is not None:
            if not np.all(np.isfinite(sampled_time)) or np.any(np.diff(sampled_time) <= 0):
                raise ValueError("L'axe temporel HDF5 echantillonne est invalide")
            sampled_intervals = np.diff(sampled_time) / np.diff(sampled_time_indices)
            expected_interval = 1.0 / self.sample_rate
            if not np.allclose(
                sampled_intervals,
                expected_interval,
                rtol=1e-3,
                atol=1e-9,
            ):
                raise ValueError("L'axe temporel HDF5 ne correspond pas a sample_rate_hz")
        return {
            "source_format": "hdf5",
            "source_path": str(file_path),
            "metadata": metadata,
            "session": session,
            "channels": {},
            "channel_keys": channel_keys,
            "channel_metadata": [channel_metadata[key] for key in sorted(channel_metadata)],
            "integrity_warnings": integrity_warnings,
        }

    @staticmethod
    def _infer_sample_rate(time_values: np.ndarray) -> float:
        time_values = np.asarray(time_values, dtype=np.float64)
        if len(time_values) < 2 or not np.all(np.isfinite(time_values)):
            raise ValueError("Axe temporel insuffisant ou invalide")
        intervals = np.diff(time_values)
        if np.any(intervals <= 0):
            raise ValueError("L'axe temporel n'est pas strictement croissant")
        median_interval = float(np.median(intervals))
        if not np.allclose(intervals, median_interval, rtol=1e-3, atol=1e-9):
            raise ValueError("L'echantillonnage n'est pas regulier")
        return 1.0 / median_interval

    @classmethod
    def _validate_time_axis(
        cls,
        time_values: np.ndarray,
        sample_rate: float,
        expected_samples: int,
        source: str,
    ) -> None:
        values = np.asarray(time_values, dtype=np.float64)
        if len(values) != expected_samples:
            raise ValueError(
                f"L'axe temporel {source} contient {len(values)} echantillons, {expected_samples} attendus"
            )
        inferred_rate = cls._infer_sample_rate(values)
        if not np.isclose(inferred_rate, sample_rate, rtol=1e-3, atol=1e-9):
            raise ValueError(f"L'axe temporel {source} ne correspond pas a sample_rate_hz")

    @staticmethod
    def _validate_channel_arrays(
        channels: dict[str, np.ndarray],
        time_values: np.ndarray | None,
        source: str,
    ) -> int:
        if not channels:
            return 0
        lengths = {key: len(np.asarray(values)) for key, values in channels.items()}
        if len(set(lengths.values())) != 1:
            details = ", ".join(f"{key}={length}" for key, length in lengths.items())
            raise ValueError(f"Longueurs de canaux {source} incoherentes: {details}")
        sample_count = next(iter(lengths.values()))
        if sample_count == 0:
            raise ValueError(f"Les canaux {source} sont vides")
        if time_values is not None and len(time_values) != sample_count:
            raise ValueError(f"L'axe temporel {source} ne contient pas le meme nombre d'echantillons")
        return sample_count

    def _load_channel_values(self, channel: str) -> np.ndarray:
        if self.current_data is None:
            raise WaveAnalysisError("Aucune donnee chargee")
        if self.current_data.get("source_format") != "hdf5":
            return np.asarray(self.current_data["channels"][channel], dtype=np.float64)

        import h5py

        with h5py.File(self.current_data["source_path"], "r") as handle:
            if f"acquisition_data/{channel}" in handle:
                return np.asarray(handle[f"acquisition_data/{channel}"][:], dtype=np.float64)
            return np.asarray(handle[channel][:], dtype=np.float64)

    @staticmethod
    def _channel_metadata_map(
        channel_keys: list[str],
        metadata: Any,
    ) -> dict[str, dict[str, Any]]:
        if isinstance(metadata, dict):
            return {str(key): value for key, value in metadata.items() if isinstance(value, dict)}
        if not isinstance(metadata, list):
            return {}

        mapped: dict[str, dict[str, Any]] = {}
        for index, item in enumerate(metadata):
            if not isinstance(item, dict):
                continue
            key = item.get("key")
            if key not in channel_keys and index < len(channel_keys):
                key = channel_keys[index]
            if key in channel_keys:
                mapped[str(key)] = item
        return mapped

    def _compute_incident_reflected_analysis(
        self,
        channel_keys: list[str],
        channel_metadata_map: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        """Run optional multi-probe separation when geometry is explicit."""

        wave_types = {
            "wave_height",
            "wave_probe",
            "wave_elevation",
            "elevation",
            "houle",
        }
        wave_channels = [
            channel
            for channel in channel_keys
            if str(channel_metadata_map.get(channel, {}).get("sensor_type", "")).lower() in wave_types
        ]
        if len(wave_channels) < 3:
            return {
                "status": "not_configured",
                "reason": "Au moins trois canaux de type elevation de houle sont requis",
            }

        position_keys = (
            "probe_position_m",
            "position_m",
            "longitudinal_position_m",
            "x_m",
        )
        positions: list[float] = []
        missing_positions: list[str] = []
        for channel in wave_channels:
            channel_info = channel_metadata_map.get(channel, {})
            position = next(
                (channel_info[key] for key in position_keys if channel_info.get(key) is not None),
                None,
            )
            try:
                positions.append(float(position))
            except (TypeError, ValueError):
                missing_positions.append(channel)
        if missing_positions:
            return {
                "status": "not_configured",
                "reason": "Position longitudinale absente pour certaines sondes",
                "missing_probe_positions": missing_positions,
            }

        uncalibrated_channels = [
            channel
            for channel in wave_channels
            if str(
                channel_metadata_map.get(channel, {}).get(
                    "calibration_status",
                    "unverified",
                )
            )
            != "valid"
        ]
        if uncalibrated_channels:
            return {
                "status": "blocked",
                "reason": "Calibration valide requise sur toutes les sondes de houle",
                "uncalibrated_channels": uncalibrated_channels,
            }

        physical_units = {
            str(
                channel_metadata_map.get(channel, {}).get("physical_unit")
                or channel_metadata_map.get(channel, {}).get("physical_units")
                or ""
            ).strip()
            for channel in wave_channels
        }
        if len(physical_units) != 1 or not next(iter(physical_units), ""):
            return {
                "status": "blocked",
                "reason": "Toutes les sondes doivent partager une unite physique explicite",
                "detected_units": sorted(physical_units),
            }
        physical_unit = next(iter(physical_units))

        source_metadata = self.current_data.get("metadata", {}) if self.current_data else {}
        session_metadata = self.current_data.get("session", {}) if self.current_data else {}
        water_depth = next(
            (
                container[key]
                for container in (source_metadata, session_metadata)
                for key in ("water_depth_m", "water_depth")
                if container.get(key) is not None
            ),
            None,
        )
        try:
            water_depth_m = float(water_depth)
        except (TypeError, ValueError):
            return {
                "status": "not_configured",
                "reason": "Profondeur d'eau water_depth_m absente",
            }

        analysis_config = self._wave_config()
        segment_length = min(
            analysis_config.segment_length,
            len(self._load_channel_values(wave_channels[0])),
        )
        minimum_frequency = max(
            analysis_config.min_frequency,
            self.sample_rate / segment_length,
        )
        maximum_frequency = analysis_config.max_frequency or self.sample_rate / 2
        try:
            separator = MultiProbeWaveSeparator(
                WaveSeparationConfig(
                    probe_positions_m=tuple(positions),
                    water_depth_m=water_depth_m,
                    min_frequency_hz=minimum_frequency,
                    max_frequency_hz=maximum_frequency,
                    segment_length=analysis_config.segment_length,
                    overlap_ratio=analysis_config.overlap_ratio,
                    window=analysis_config.window,
                )
            )
            values = np.vstack([self._load_channel_values(channel) for channel in wave_channels])
            result = separator.analyze(values, self.sample_rate)
            result["channel_keys"] = wave_channels
            result["physical_unit"] = physical_unit
            return result
        except (ValueError, WaveAnalysisError, WaveSeparationError) as exc:
            return {
                "status": "failed",
                "reason": str(exc),
                "channel_keys": wave_channels,
            }

    def _zero_upcrossings(self, values: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        series = np.asarray(values, dtype=np.float64)
        if series.ndim != 1 or not np.all(np.isfinite(series)):
            raise WaveAnalysisError("Signal temporel invalide")
        centered = series - float(np.mean(series))
        indices = np.flatnonzero((centered[:-1] <= 0.0) & (centered[1:] > 0.0))
        crossings = []
        for index in indices:
            delta = centered[index + 1] - centered[index]
            fraction = -centered[index] / delta if delta else 0.0
            crossings.append(float(index + fraction))
        return centered, np.asarray(crossings, dtype=np.float64)

    def _extract_wave_heights(self, values: np.ndarray) -> np.ndarray:
        """Retourne les hauteurs crete-a-creux entre montees successives."""

        centered, crossings = self._zero_upcrossings(values)
        heights: list[float] = []
        for start_crossing, end_crossing in zip(crossings[:-1], crossings[1:], strict=False):
            start = max(0, int(np.ceil(start_crossing)))
            stop = min(len(centered), int(np.floor(end_crossing)) + 1)
            if stop - start >= 2:
                segment = centered[start:stop]
                heights.append(float(np.max(segment) - np.min(segment)))
        return np.asarray(heights, dtype=np.float64)

    def _compute_mean_period(self, values: np.ndarray) -> float:
        """Calcule la periode moyenne par zero-upcrossing interpole."""

        _, crossings = self._zero_upcrossings(values)
        if len(crossings) < 2:
            return 0.0
        return float(np.mean(np.diff(crossings)) / self.sample_rate)

    def _compute_spectral_analysis(self) -> dict[str, dict[str, Any]]:
        """Calcule une densite spectrale unilaterale conservant la variance."""

        if not self.current_data:
            raise WaveAnalysisError("Aucune donnee chargee")
        results: dict[str, dict[str, Any]] = {}
        for channel, values in self.current_data.get("channels", {}).items():
            series = np.asarray(values, dtype=np.float64)
            if series.ndim != 1 or len(series) < 2 or not np.all(np.isfinite(series)):
                raise WaveAnalysisError(f"Canal spectral invalide: {channel}")
            processed = series - float(np.mean(series))
            frequencies, density = signal.periodogram(
                processed,
                fs=self.sample_rate,
                window=self.config["analysis"].get("window", "hann"),
                detrend=False,
                return_onesided=True,
                scaling="density",
            )
            frequency_step = float(frequencies[1] - frequencies[0])
            m0 = float(np.sum(density) * frequency_step)
            peak_index = int(np.argmax(density[1:]) + 1) if len(density) > 1 else 0
            peak_frequency = float(frequencies[peak_index])
            results[channel] = {
                "method": "one_sided_periodogram",
                "frequencies": frequencies.tolist(),
                "psd": density.tolist(),
                "m0": m0,
                "Hm0": 4.0 * float(np.sqrt(max(m0, 0.0))),
                "peak_frequency": peak_frequency,
                "peak_period": 1.0 / peak_frequency if peak_frequency > 0 else 0.0,
                "frequency_resolution": frequency_step,
            }
        return results

    def run_analysis(self) -> bool:
        if self.current_data is None:
            self.errorOccurred.emit("Aucune donnee chargee")
            return False

        try:
            analyzer = WaveAnalyzer(self._wave_config())
            channel_keys = list(
                self.current_data.get("channel_keys") or self.current_data.get("channels", {}).keys()
            )
            if not channel_keys:
                raise WaveAnalysisError("Aucun canal exploitable")
            self.current_data["channel_keys"] = channel_keys
            channel_metadata_map = self._channel_metadata_map(
                channel_keys,
                self.current_data.get("channel_metadata", {}),
            )
            reference_channel = channel_keys[0]
            reference_values = self._load_channel_values(reference_channel)
            results: dict[str, Any] = {
                "basic_stats": {},
                "spectral_analysis": {},
                "wave_parameters": {},
                "zero_crossing_metrics": {},
                "goda_metrics": {},
                "quality": {},
                "cross_spectral_analysis": {},
                "incident_reflected_analysis": {},
                "analysis_configuration": analyzer.configuration(),
                "sample_rate": self.sample_rate,
                "reference_channel": reference_channel,
                "channel_metadata": deepcopy(self.current_data.get("channel_metadata", {})),
                "source_metadata": deepcopy(self.current_data.get("metadata", {})),
                "timestamp": np.datetime64("now").astype(str),
            }

            for channel in channel_keys:
                values = (
                    reference_values if channel == reference_channel else self._load_channel_values(channel)
                )
                channel_info = channel_metadata_map.get(channel, {})
                unit = str(
                    channel_info.get("physical_unit")
                    or channel_info.get("physical_units")
                    or channel_info.get("unit")
                    or ""
                )
                channel_results = analyzer.analyze_channel(values, self.sample_rate, unit)
                sensor_type = str(channel_info.get("sensor_type", "")).lower()
                wave_elevation_types = {
                    "wave_height",
                    "wave_probe",
                    "wave_elevation",
                    "elevation",
                    "houle",
                }
                interpretation_valid = sensor_type in wave_elevation_types
                channel_results["wave_parameters"]["interpretation"] = (
                    "wave_elevation" if interpretation_valid else "generic_amplitude"
                )
                channel_results["quality"]["wave_height_interpretation_valid"] = interpretation_valid
                if not interpretation_valid:
                    warning = (
                        "Type de capteur absent: verifier que le signal represente une elevation"
                        if not sensor_type
                        else "Hm0 et H1/3 restent dans l'unite du capteur; ce ne sont pas "
                        "des hauteurs de houle sans conversion en elevation"
                    )
                    channel_results["quality"]["warnings"].append(warning)
                    channel_results["quality"]["valid"] = False
                results["basic_stats"][channel] = channel_results["basic_stats"]
                results["spectral_analysis"][channel] = channel_results["spectral"]
                results["wave_parameters"][channel] = channel_results["wave_parameters"]
                results["quality"][channel] = channel_results["quality"]
                zero_crossing_metrics = self._compatibility_wave_metrics(channel_results["wave_parameters"])
                results["zero_crossing_metrics"][channel] = zero_crossing_metrics
                results["goda_metrics"][channel] = deepcopy(zero_crossing_metrics)

                if channel != reference_channel:
                    pair_key = f"{reference_channel}__{channel}"
                    results["cross_spectral_analysis"][pair_key] = analyzer.analyze_cross_spectrum(
                        reference_values,
                        values,
                        self.sample_rate,
                        results["spectral_analysis"][reference_channel]["peak_frequency"],
                    )

            results["incident_reflected_analysis"] = self._compute_incident_reflected_analysis(
                channel_keys,
                channel_metadata_map,
            )
            spectra = list(results["spectral_analysis"].values())
            sample_count = int(len(reference_values))
            processing_warnings: list[str] = list(self.current_data.get("integrity_warnings", []))
            separation_status = results["incident_reflected_analysis"].get("status")
            if separation_status in {"blocked", "failed"}:
                processing_warnings.append(
                    f"INCIDENT_REFLECTED_ANALYSIS_{separation_status.upper()}: "
                    f"{results['incident_reflected_analysis'].get('reason', '')}"
                )
            for channel in channel_keys:
                calibration_status = str(
                    channel_metadata_map.get(channel, {}).get(
                        "calibration_status",
                        "unverified",
                    )
                )
                if calibration_status != "valid":
                    processing_warnings.append(f"CALIBRATION_NOT_PERFORMED: {channel} ({calibration_status})")
            results["metadata"] = {
                "schema_version": SCHEMA_VERSION,
                "sample_rate_hz": float(self.sample_rate),
                "dt_seconds": 1.0 / float(self.sample_rate),
                "n_samples": sample_count,
                "duration_s": sample_count / float(self.sample_rate),
                "processing_method": "post_processor.run_analysis",
                "psd_method": "welch",
                "window": str(self.config["analysis"].get("window", "hann")),
                "overlap_applied": bool(
                    any(int(spectrum.get("segment_count", 1)) > 1 for spectrum in spectra)
                    and float(self.config["analysis"].get("overlap", 0.0)) > 0
                ),
                "detrend": bool(self.config["analysis"].get("detrend", True)),
                "warnings": processing_warnings,
                "result_semantics": {
                    "zero_crossing_metrics": "individual waves by zero-upcrossing",
                    "goda_metrics": (
                        "deprecated compatibility alias; not incident/reflected Goda separation"
                    ),
                },
            }

            self.current_analysis = results
            self.analysisCompleted.emit(results)
            print("Analyse terminee")
            return True
        except Exception as exc:
            message = f"Erreur analyse: {exc}"
            self.errorOccurred.emit(message)
            print(message)
            return False

    @staticmethod
    def _compatibility_wave_metrics(parameters: dict[str, Any]) -> dict[str, Any]:
        return {
            "Hs": parameters.get("Hs", 0.0),
            "H1_3": parameters.get("H1_3", 0.0),
            "Hm0": parameters.get("Hm0", 0.0),
            "H_max": parameters.get("H_max", 0.0),
            "H_mean": parameters.get("H_mean", 0.0),
            "H_rms": parameters.get("H_rms", 0.0),
            "n_waves": parameters.get("n_waves", 0),
            "Tp": parameters.get("Tp", 0.0),
            "Tm": parameters.get("T_mean", 0.0),
            "Tm01": parameters.get("Tm01", 0.0),
            "Tm02": parameters.get("Tm02", 0.0),
        }

    def export_results(self, output_path: str, format_type: str = "csv") -> bool:
        if self.current_analysis is None:
            self.errorOccurred.emit("Aucune analyse a exporter")
            return False
        try:
            if format_type == "csv":
                self._export_csv(output_path)
            elif format_type == "json":
                self._export_json(output_path)
            elif format_type == "hdf5":
                self._export_hdf5(output_path)
            else:
                raise ValueError(f"Format non supporte: {format_type}")
            self.exportCompleted.emit(output_path)
            return True
        except Exception as exc:
            self.errorOccurred.emit(f"Erreur export: {exc}")
            return False

    def _export_csv(self, output_path: str) -> None:
        import pandas as pd

        rows: list[dict[str, Any]] = []
        categories = ("basic_stats", "wave_parameters", "quality")
        for category in categories:
            for channel, metrics in self.current_analysis.get(category, {}).items():
                for metric, value in metrics.items():
                    if isinstance(value, (dict, list)):
                        value = json.dumps(self._prepare_json_data(value), ensure_ascii=False)
                    rows.append(
                        {
                            "channel": channel,
                            "category": category,
                            "metric": metric,
                            "value": value,
                        }
                    )
        for channel, spectrum in self.current_analysis["spectral_analysis"].items():
            for metric in (
                "peak_frequency",
                "peak_period",
                "Hm0",
                "Tm01",
                "Tm02",
                "Te",
                "frequency_resolution",
                "segment_count",
            ):
                rows.append(
                    {
                        "channel": channel,
                        "category": "spectral_analysis",
                        "metric": metric,
                        "value": spectrum.get(metric),
                    }
                )
        separation = self.current_analysis.get("incident_reflected_analysis", {})
        for metric in (
            "status",
            "incident_Hm0",
            "reflected_Hm0",
            "energy_reflection_coefficient",
            "frequency_resolution",
            "segment_count",
            "probe_count",
        ):
            if metric in separation:
                rows.append(
                    {
                        "channel": "multi_probe",
                        "category": "incident_reflected_analysis",
                        "metric": metric,
                        "value": separation[metric],
                    }
                )
        pd.DataFrame(rows).to_csv(output_path, index=False)

    def _export_json(self, output_path: str) -> None:
        with open(output_path, "w", encoding="utf-8") as handle:
            json.dump(
                self._prepare_json_data(self.current_analysis),
                handle,
                indent=2,
                ensure_ascii=False,
            )

    def _export_hdf5(self, output_path: str) -> None:
        try:
            import h5py
        except ImportError as exc:
            raise ImportError("h5py requis pour l'export HDF5") from exc

        with h5py.File(output_path, "w") as handle:
            handle.attrs["timestamp"] = str(self.current_analysis["timestamp"])
            handle.attrs["sample_rate"] = self.sample_rate
            handle.attrs["analysis_configuration"] = json.dumps(
                self.current_analysis["analysis_configuration"], ensure_ascii=False
            )

            for category in ("basic_stats", "wave_parameters", "quality"):
                category_group = handle.create_group(category)
                for channel, metrics in self.current_analysis[category].items():
                    channel_group = category_group.create_group(channel)
                    for metric, value in metrics.items():
                        channel_group.attrs[metric] = self._hdf5_attribute(value)

            spectral_group = handle.create_group("spectral_analysis")
            for channel, spectrum in self.current_analysis["spectral_analysis"].items():
                channel_group = spectral_group.create_group(channel)
                channel_group.create_dataset("frequencies", data=spectrum["frequencies"])
                channel_group.create_dataset("psd", data=spectrum["psd"])
                for metric, value in spectrum.items():
                    if metric not in {"frequencies", "psd", "power_spectrum"}:
                        channel_group.attrs[metric] = self._hdf5_attribute(value)

            cross_group = handle.create_group("cross_spectral_analysis")
            for pair, metrics in self.current_analysis["cross_spectral_analysis"].items():
                pair_group = cross_group.create_group(pair)
                for metric, value in metrics.items():
                    if metric in {"frequencies", "coherence", "phase_degrees"}:
                        pair_group.create_dataset(metric, data=value)
                    else:
                        pair_group.attrs[metric] = self._hdf5_attribute(value)

            separation_group = handle.create_group("incident_reflected_analysis")
            separation = self.current_analysis.get("incident_reflected_analysis", {})
            separation_arrays = {
                "frequencies",
                "valid_frequency_mask",
                "incident_psd",
                "reflected_psd",
                "reflection_coefficient_by_frequency",
                "condition_number_by_frequency",
                "normalized_residual_by_frequency",
            }
            for metric, value in separation.items():
                if metric in separation_arrays:
                    separation_group.create_dataset(metric, data=value)
                else:
                    separation_group.attrs[metric] = self._hdf5_attribute(value)

    def _hdf5_attribute(self, value: Any) -> Any:
        if isinstance(value, (str, int, float, bool, np.integer, np.floating)):
            return value
        return json.dumps(self._prepare_json_data(value), ensure_ascii=False)

    def _prepare_json_data(self, data: Any) -> Any:
        if isinstance(data, dict):
            return {key: self._prepare_json_data(value) for key, value in data.items()}
        if isinstance(data, (list, tuple)):
            return [self._prepare_json_data(item) for item in data]
        if isinstance(data, np.ndarray):
            return data.tolist()
        if isinstance(data, (np.integer, np.floating)):
            return data.item()
        return data

    def get_analysis_summary(self) -> dict[str, Any] | None:
        if self.current_analysis is None:
            return None
        return {
            "timestamp": self.current_analysis["timestamp"],
            "channels_analyzed": list(self.current_analysis["basic_stats"]),
            "sample_rate": self.sample_rate,
            "reference_channel": self.current_analysis["reference_channel"],
            "wave_summary": {
                channel: {
                    "H1_3": values.get("H1_3", 0.0),
                    "Hm0": values.get("Hm0", 0.0),
                    "Tp": values.get("Tp", 0.0),
                    "Tm02": values.get("Tm02", 0.0),
                    "n_waves": values.get("n_waves", 0),
                }
                for channel, values in self.current_analysis["wave_parameters"].items()
            },
            "incident_reflected_summary": {
                key: self.current_analysis.get("incident_reflected_analysis", {}).get(key)
                for key in (
                    "status",
                    "incident_Hm0",
                    "reflected_Hm0",
                    "energy_reflection_coefficient",
                    "probe_count",
                )
            },
        }
