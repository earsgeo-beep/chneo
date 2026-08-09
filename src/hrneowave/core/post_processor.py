"""Chargement, analyse scientifique et export des donnees CHNeoWave."""

from __future__ import annotations

import json
import os
from copy import deepcopy
from pathlib import Path
from typing import Any

import numpy as np
from scipy import signal

from .session_schema import SAMPLE_RATE_KEYS, SCHEMA_VERSION, extract_sample_rate
from .wave_analysis import WaveAnalysisConfig, WaveAnalysisError, WaveAnalyzer

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
                float(analysis["max_frequency"])
                if analysis.get("max_frequency") is not None
                else None
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

        exact_time = next(
            (column for column in frame.columns if column.strip().lower() == "time"),
            None,
        )
        time_columns = [exact_time] if exact_time else [
            column for column in frame.columns if column.lower().endswith("_time")
        ]
        data_columns = [
            column
            for column in frame.columns
            if column.startswith(("channel_", "probe_"))
        ]
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

        channels = {
            column: frame[column].to_numpy(dtype=np.float64)
            for column in data_columns
        }
        channel_metadata: list[dict[str, Any]] = []
        sidecar_path = Path(f"{file_path}.metadata.json")
        if sidecar_path.is_file():
            with sidecar_path.open("r", encoding="utf-8") as handle:
                sidecar = json.load(handle)
            channel_metadata = list(sidecar.get("channel_metadata", []))

        return {
            "source_format": "csv",
            "metadata": metadata,
            "time": (
                frame[time_columns[0]].to_numpy(dtype=np.float64)
                if time_columns
                else np.arange(len(frame), dtype=np.float64) / self.sample_rate
            ),
            "channels": channels,
            "channel_keys": list(channels),
            "channel_metadata": channel_metadata,
        }

    def _load_json(self, file_path: Path) -> dict[str, Any]:
        with file_path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        channels_payload = payload.get("channels", {})
        channels = {
            key: np.asarray(values, dtype=np.float64)
            for key, values in channels_payload.items()
        }
        raw_channels = {
            key: np.asarray(values, dtype=np.float64)
            for key, values in payload.get("raw_channels", {}).items()
        }
        metadata = {
            key: self._normalize_metadata_value(value)
            for key, value in payload.get("metadata", {}).items()
        }
        session = payload.get("session", {})
        sample_rate = extract_sample_rate(metadata, session)
        if sample_rate is None and "time" in payload:
            sample_rate = self._infer_sample_rate(np.asarray(payload["time"], dtype=float))
        if sample_rate is None or float(sample_rate) <= 0:
            raise ValueError("Frequence d'echantillonnage JSON absente ou invalide")
        self.sample_rate = float(sample_rate)

        return {
            "source_format": "json",
            "metadata": metadata,
            "session": session,
            "time": np.asarray(payload.get("time", []), dtype=np.float64),
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
        with h5py.File(file_path, "r") as handle:
            metadata.update(
                {
                    key: self._normalize_metadata_value(value)
                    for key, value in handle.attrs.items()
                }
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
            if "metadata/channels" in handle:
                for key, group in handle["metadata/channels"].items():
                    channel_metadata[key] = {
                        name: self._normalize_metadata_value(value)
                        for name, value in group.attrs.items()
                    }

            acquisition_group = handle.get("acquisition_data")
            if acquisition_group is not None:
                channel_keys = sorted(
                    key
                    for key in acquisition_group.keys()
                    if key.startswith(("channel_", "probe_"))
                )
            else:
                channel_keys = sorted(
                    key for key in handle.keys() if key.startswith(("channel_", "probe_"))
                )

            channel_lengths = []
            for key in channel_keys:
                dataset = (
                    acquisition_group[key]
                    if acquisition_group is not None
                    else handle[key]
                )
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

        sample_rate = extract_sample_rate(metadata, session)
        if sample_rate is None or float(sample_rate) <= 0:
            raise ValueError("Frequence d'echantillonnage HDF5 absente ou invalide")
        self.sample_rate = float(sample_rate)
        return {
            "source_format": "hdf5",
            "source_path": str(file_path),
            "metadata": metadata,
            "session": session,
            "channels": {},
            "channel_keys": channel_keys,
            "channel_metadata": [channel_metadata[key] for key in sorted(channel_metadata)],
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
            return {
                str(key): value
                for key, value in metadata.items()
                if isinstance(value, dict)
            }
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
                self.current_data.get("channel_keys")
                or self.current_data.get("channels", {}).keys()
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
                "goda_metrics": {},
                "quality": {},
                "cross_spectral_analysis": {},
                "analysis_configuration": analyzer.configuration(),
                "sample_rate": self.sample_rate,
                "reference_channel": reference_channel,
                "channel_metadata": deepcopy(self.current_data.get("channel_metadata", {})),
                "source_metadata": deepcopy(self.current_data.get("metadata", {})),
                "timestamp": np.datetime64("now").astype(str),
            }

            for channel in channel_keys:
                values = (
                    reference_values
                    if channel == reference_channel
                    else self._load_channel_values(channel)
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
                channel_results["quality"][
                    "wave_height_interpretation_valid"
                ] = interpretation_valid
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
                results["goda_metrics"][channel] = self._compatibility_wave_metrics(
                    channel_results["wave_parameters"]
                )

                if channel != reference_channel:
                    pair_key = f"{reference_channel}__{channel}"
                    results["cross_spectral_analysis"][pair_key] = (
                        analyzer.analyze_cross_spectrum(
                            reference_values,
                            values,
                            self.sample_rate,
                            results["spectral_analysis"][reference_channel]["peak_frequency"],
                        )
                    )

            spectra = list(results["spectral_analysis"].values())
            sample_count = int(len(reference_values))
            processing_warnings: list[str] = []
            for channel in channel_keys:
                calibration_status = str(
                    channel_metadata_map.get(channel, {}).get(
                        "calibration_status",
                        "unverified",
                    )
                )
                if calibration_status != "valid":
                    processing_warnings.append(
                        f"CALIBRATION_NOT_PERFORMED: {channel} ({calibration_status})"
                    )
            single_segment = bool(spectra) and all(
                int(spectrum.get("segment_count", 1)) == 1 for spectrum in spectra
            )
            results["metadata"] = {
                "schema_version": SCHEMA_VERSION,
                "sample_rate_hz": float(self.sample_rate),
                "dt_seconds": 1.0 / float(self.sample_rate),
                "n_samples": sample_count,
                "duration_s": sample_count / float(self.sample_rate),
                "processing_method": "post_processor.run_analysis",
                "psd_method": (
                    "one_sided_periodogram" if single_segment else "welch"
                ),
                "window": str(self.config["analysis"].get("window", "hann")),
                "overlap_applied": bool(
                    any(int(spectrum.get("segment_count", 1)) > 1 for spectrum in spectra)
                    and float(self.config["analysis"].get("overlap", 0.0)) > 0
                ),
                "detrend": bool(self.config["analysis"].get("detrend", True)),
                "warnings": processing_warnings,
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
        }
