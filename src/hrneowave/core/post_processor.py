# post_processor.py - Module de post-traitement pour l'analyse des donnees de houle
import json
import os
from typing import Dict, Optional

import numpy as np


QObject = None
Signal = None


def _ensure_qt_imports():
    """Importe les modules Qt de maniere conditionnelle."""
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
    """Controleur de post-traitement et d'analyse des donnees."""

    dataLoaded = Signal(dict)
    analysisCompleted = Signal(dict)
    exportCompleted = Signal(str)
    errorOccurred = Signal(str)

    def __init__(self, config_path: Optional[str] = None):
        super().__init__()
        self.config = self._load_config(config_path)
        self.current_data = None
        self.current_analysis = None
        self.sample_rate = 32.0

    def _load_config(self, config_path: Optional[str]) -> Dict:
        default_config = {
            "analysis": {
                "window_size": 1024,
                "overlap": 0.5,
                "detrend": True,
                "apply_window": True,
            },
            "goda": {
                "significant_wave_height": True,
                "peak_period": True,
                "mean_period": True,
                "spectral_moments": True,
            },
            "export": {
                "formats": ["csv", "json", "hdf5"],
                "precision": 6,
            },
        }

        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as handle:
                    user_config = json.load(handle)
                default_config.update(user_config)
            except Exception as exc:
                print(f"Erreur chargement config: {exc}")

        return default_config

    def _normalize_metadata_value(self, value):
        if isinstance(value, bytes):
            value = value.decode("utf-8", errors="replace")
        if isinstance(value, np.generic):
            return value.item()
        if isinstance(value, str):
            stripped = value.strip()
            if stripped.startswith("[") or stripped.startswith("{"):
                try:
                    return json.loads(stripped)
                except json.JSONDecodeError:
                    return value
        return value

    def load_data_file(self, file_path: str) -> bool:
        try:
            if not os.path.exists(file_path):
                self.errorOccurred.emit(f"Fichier introuvable: {file_path}")
                return False

            extension = os.path.splitext(file_path)[1].lower()
            if extension == ".csv":
                data = self._load_csv(file_path)
            elif extension == ".json":
                data = self._load_json(file_path)
            elif extension in {".h5", ".hdf5"}:
                data = self._load_hdf5(file_path)
            else:
                self.errorOccurred.emit(f"Format non supporte: {extension}")
                return False

            self.current_data = data
            self.dataLoaded.emit(data)
            print(f"Donnees chargees: {file_path}")
            return True

        except Exception as exc:
            error_msg = f"Erreur chargement donnees: {exc}"
            print(f"Erreur {error_msg}")
            self.errorOccurred.emit(error_msg)
            return False

    def _load_csv(self, file_path: str) -> Dict:
        import pandas as pd

        frame = pd.read_csv(file_path)
        metadata = {}

        if "sample_rate" in frame.columns:
            self.sample_rate = float(frame["sample_rate"].iloc[0])
            metadata["sample_rate"] = self.sample_rate

        time_columns = [column for column in frame.columns if "time" in column.lower()]
        data_columns = [column for column in frame.columns if column.startswith("channel_") or column.startswith("probe_")]

        return {
            "metadata": metadata,
            "time": frame[time_columns[0]].to_numpy() if time_columns else np.arange(len(frame)) / self.sample_rate,
            "channels": {column: frame[column].to_numpy() for column in data_columns},
        }

    def _load_json(self, file_path: str) -> Dict:
        with open(file_path, "r", encoding="utf-8") as handle:
            data = json.load(handle)

        if "channels" in data:
            for channel, values in data["channels"].items():
                data["channels"][channel] = np.array(values)

        if "time" in data:
            data["time"] = np.array(data["time"])

        if "metadata" in data:
            data["metadata"] = {
                key: self._normalize_metadata_value(value)
                for key, value in data["metadata"].items()
            }

        sample_rate = None
        if "metadata" in data:
            sample_rate = data["metadata"].get("sample_rate") or data["metadata"].get("sampling_rate")
        if sample_rate is None and "session" in data:
            sample_rate = data["session"].get("sample_rate") or data["session"].get("sampling_rate")
        if sample_rate is not None:
            self.sample_rate = float(sample_rate)

        return data

    def _load_hdf5(self, file_path: str) -> Dict:
        try:
            import h5py
        except ImportError as exc:
            raise ImportError("h5py requis pour les fichiers HDF5") from exc

        data = {"channels": {}, "metadata": {}}

        with h5py.File(file_path, "r") as handle:
            data["metadata"].update({
                key: self._normalize_metadata_value(value)
                for key, value in handle.attrs.items()
            })

            if "metadata" in handle:
                metadata_group = handle["metadata"]
                data["metadata"].update({
                    key: self._normalize_metadata_value(value)
                    for key, value in metadata_group.attrs.items()
                })

                if "session" in metadata_group:
                    session_attrs = {
                        key: self._normalize_metadata_value(value)
                        for key, value in metadata_group["session"].attrs.items()
                    }
                    data["session"] = session_attrs
                    data["metadata"].update(session_attrs)

                if "calibration" in metadata_group:
                    data["calibration"] = {
                        key: self._normalize_metadata_value(value)
                        for key, value in metadata_group["calibration"].attrs.items()
                    }

            if "acquisition_data" in handle:
                acquisition_group = handle["acquisition_data"]
                for key in acquisition_group.keys():
                    if key == "time":
                        data["time"] = acquisition_group[key][:]
                    elif key.startswith("channel_") or key.startswith("probe_"):
                        data["channels"][key] = acquisition_group[key][:]

            if "time" in handle and "time" not in data:
                data["time"] = handle["time"][:]

            for key in handle.keys():
                if key.startswith("channel_") or key.startswith("probe_"):
                    data["channels"][key] = handle[key][:]

        sample_rate = data["metadata"].get("sample_rate") or data["metadata"].get("sampling_rate")
        if sample_rate is not None:
            self.sample_rate = float(sample_rate)

        if "time" not in data and data["channels"]:
            first_channel = next(iter(data["channels"].values()))
            data["time"] = np.arange(len(first_channel), dtype=float) / self.sample_rate

        return data

    def run_analysis(self) -> bool:
        if self.current_data is None:
            self.errorOccurred.emit("Aucune donnee chargee")
            return False

        try:
            analysis_results = {
                "basic_stats": self._compute_basic_stats(),
                "spectral_analysis": self._compute_spectral_analysis(),
                "goda_metrics": self._compute_goda_metrics(),
                "timestamp": np.datetime64("now").astype(str),
            }
            self.current_analysis = analysis_results
            self.analysisCompleted.emit(analysis_results)
            print("Analyse terminee")
            return True

        except Exception as exc:
            error_msg = f"Erreur analyse: {exc}"
            self.errorOccurred.emit(error_msg)
            print(error_msg)
            return False

    def _compute_basic_stats(self) -> Dict:
        stats = {}
        for channel, values in self.current_data["channels"].items():
            stats[channel] = {
                "mean": float(np.mean(values)),
                "std": float(np.std(values)),
                "min": float(np.min(values)),
                "max": float(np.max(values)),
                "rms": float(np.sqrt(np.mean(values ** 2))),
                "skewness": float(self._compute_skewness(values)),
                "kurtosis": float(self._compute_kurtosis(values)),
            }
        return stats

    def _compute_spectral_analysis(self) -> Dict:
        spectral_results = {}
        for channel, values in self.current_data["channels"].items():
            n_fft = self.config["analysis"]["window_size"]
            freqs = np.fft.fftfreq(n_fft, 1 / self.sample_rate)[: n_fft // 2]
            if self.config["analysis"]["apply_window"]:
                window = np.hanning(len(values))
                values = values * window
            fft_data = np.fft.fft(values, n_fft)
            power_spectrum = np.abs(fft_data[: n_fft // 2]) ** 2
            spectral_results[channel] = {
                "frequencies": freqs.tolist(),
                "power_spectrum": power_spectrum.tolist(),
                "peak_frequency": float(freqs[np.argmax(power_spectrum)]),
                "total_energy": float(np.sum(power_spectrum)),
            }
        return spectral_results

    def _compute_goda_metrics(self) -> Dict:
        goda_results = {}
        for channel, values in self.current_data["channels"].items():
            wave_heights = self._extract_wave_heights(values)
            if len(wave_heights) == 0:
                goda_results[channel] = {
                    "Hs": 0.0,
                    "H_max": 0.0,
                    "H_mean": 0.0,
                    "H_rms": 0.0,
                    "n_waves": 0,
                    "Tp": 0.0,
                    "Tm": 0.0,
                }
                continue

            sorted_heights = np.sort(wave_heights)[::-1]
            n_waves = len(sorted_heights)
            goda_results[channel] = {
                "Hs": float(np.mean(sorted_heights[: max(1, n_waves // 3)])),
                "H_max": float(np.max(sorted_heights)),
                "H_mean": float(np.mean(sorted_heights)),
                "H_rms": float(np.sqrt(np.mean(sorted_heights ** 2))),
                "n_waves": int(n_waves),
                "Tp": self._compute_peak_period(values),
                "Tm": self._compute_mean_period(values),
            }
        return goda_results

    def _extract_wave_heights(self, values: np.ndarray) -> np.ndarray:
        zero_crossings = np.where(np.diff(np.sign(values)))[0]
        wave_heights = []
        for index in range(0, len(zero_crossings) - 1, 2):
            if index + 1 >= len(zero_crossings):
                break
            start_idx = zero_crossings[index]
            end_idx = zero_crossings[index + 1]
            segment = values[start_idx:end_idx]
            if len(segment) > 0:
                wave_heights.append(np.max(segment) - np.min(segment))
        return np.array(wave_heights)

    def _compute_peak_period(self, values: np.ndarray) -> float:
        freqs = np.fft.fftfreq(len(values), 1 / self.sample_rate)
        fft_data = np.fft.fft(values)
        power_spectrum = np.abs(fft_data) ** 2
        valid_indices = freqs > 0
        if np.any(valid_indices):
            peak_freq = freqs[valid_indices][np.argmax(power_spectrum[valid_indices])]
            return float(1.0 / peak_freq) if peak_freq > 0 else 0.0
        return 0.0

    def _compute_mean_period(self, values: np.ndarray) -> float:
        zero_crossings = np.where(np.diff(np.sign(values)))[0]
        if len(zero_crossings) > 1:
            periods = np.diff(zero_crossings) / self.sample_rate * 2
            return float(np.mean(periods))
        return 0.0

    def _compute_skewness(self, values: np.ndarray) -> float:
        mean = np.mean(values)
        std = np.std(values)
        return float(np.mean(((values - mean) / std) ** 3)) if std > 0 else 0.0

    def _compute_kurtosis(self, values: np.ndarray) -> float:
        mean = np.mean(values)
        std = np.std(values)
        return float(np.mean(((values - mean) / std) ** 4) - 3.0) if std > 0 else 0.0

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

        rows = []
        for channel, stats in self.current_analysis["basic_stats"].items():
            for metric, value in stats.items():
                rows.append({
                    "channel": channel,
                    "category": "basic_stats",
                    "metric": metric,
                    "value": value,
                })
        for channel, goda in self.current_analysis["goda_metrics"].items():
            for metric, value in goda.items():
                rows.append({
                    "channel": channel,
                    "category": "goda_metrics",
                    "metric": metric,
                    "value": value,
                })
        pd.DataFrame(rows).to_csv(output_path, index=False)

    def _export_json(self, output_path: str) -> None:
        with open(output_path, "w", encoding="utf-8") as handle:
            json.dump(self._prepare_json_data(self.current_analysis), handle, indent=2, ensure_ascii=False)

    def _export_hdf5(self, output_path: str) -> None:
        try:
            import h5py
        except ImportError as exc:
            raise ImportError("h5py requis pour l'export HDF5") from exc

        with h5py.File(output_path, "w") as handle:
            handle.attrs["timestamp"] = self.current_analysis["timestamp"]
            handle.attrs["sample_rate"] = self.sample_rate

            stats_group = handle.create_group("basic_stats")
            for channel, stats in self.current_analysis["basic_stats"].items():
                channel_group = stats_group.create_group(channel)
                for metric, value in stats.items():
                    channel_group.attrs[metric] = value

            goda_group = handle.create_group("goda_metrics")
            for channel, goda in self.current_analysis["goda_metrics"].items():
                channel_group = goda_group.create_group(channel)
                for metric, value in goda.items():
                    channel_group.attrs[metric] = value

    def _prepare_json_data(self, data):
        if isinstance(data, dict):
            return {key: self._prepare_json_data(value) for key, value in data.items()}
        if isinstance(data, np.ndarray):
            return data.tolist()
        if isinstance(data, (np.integer, np.floating)):
            return float(data)
        return data

    def get_analysis_summary(self) -> Optional[Dict]:
        if self.current_analysis is None:
            return None

        summary = {
            "timestamp": self.current_analysis["timestamp"],
            "channels_analyzed": list(self.current_analysis["basic_stats"].keys()),
            "sample_rate": self.sample_rate,
        }
        if "goda_metrics" in self.current_analysis:
            summary["goda_summary"] = {}
            for channel, goda in self.current_analysis["goda_metrics"].items():
                summary["goda_summary"][channel] = {
                    "Hs": goda.get("Hs", 0),
                    "H_max": goda.get("H_max", 0),
                    "Tp": goda.get("Tp", 0),
                    "n_waves": goda.get("n_waves", 0),
                }
        return summary
