"""Enregistrement HDF5 incrementiel des sessions d'acquisition.

Le fichier de session est alimente au fil de l'acquisition. Il reste donc la
source complete des donnees, tandis que le controleur ne conserve en memoire
qu'un tampon court destine a l'affichage.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import numpy as np

from hrneowave import __version__


class RecordingError(RuntimeError):
    """Erreur empechant de garantir l'enregistrement de la session."""


class ContinuousHDF5Recorder:
    """Ecrit les tensions brutes et les valeurs physiques bloc par bloc."""

    FORMAT_VERSION = "2.0"

    def __init__(self, flush_interval_seconds: float = 1.0, chunk_samples: int = 4096):
        if flush_interval_seconds <= 0:
            raise ValueError("flush_interval_seconds doit etre strictement positif")
        if chunk_samples <= 0:
            raise ValueError("chunk_samples doit etre strictement positif")

        self.flush_interval_seconds = float(flush_interval_seconds)
        self.chunk_samples = int(chunk_samples)
        self.file_path: Path | None = None
        self.sample_count = 0
        self._file = None
        self._channel_keys: list[str] = []
        self._last_flush = 0.0

    @property
    def is_open(self) -> bool:
        return self._file is not None

    def start(self, file_path: str | Path, session: Any) -> Path:
        """Cree un nouveau fichier et sa structure extensible."""
        if self.is_open:
            raise RecordingError("Un fichier d'acquisition est deja ouvert")
        if session.sampling_rate <= 0:
            raise RecordingError("La frequence d'echantillonnage est invalide")
        if not session.channels:
            raise RecordingError("Aucun canal n'est configure pour l'enregistrement")

        try:
            import h5py
        except ImportError as exc:
            raise RecordingError(
                "h5py est requis pour securiser l'acquisition sur disque"
            ) from exc

        path = Path(file_path).expanduser().resolve()
        if path.suffix.lower() not in {".h5", ".hdf5"}:
            path = path.with_suffix(".h5")
        path.parent.mkdir(parents=True, exist_ok=True)

        try:
            # Le mode exclusif interdit d'ecraser silencieusement une session.
            handle = h5py.File(path, "x", libver="latest")
            self._file = handle
            self.file_path = path
            self.sample_count = 0
            self._last_flush = time.monotonic()

            handle.attrs["software"] = "CHNeoWave"
            handle.attrs["software_version"] = __version__
            handle.attrs["format_version"] = self.FORMAT_VERSION
            handle.attrs["recording_status"] = "recording"
            handle.attrs["created_at"] = session.start_time.isoformat()
            handle.attrs["n_channels"] = len(session.channels)
            handle.attrs["n_samples"] = 0

            metadata = handle.create_group("metadata")
            session_group = metadata.create_group("session")
            session_group.attrs["session_id"] = session.session_id
            session_group.attrs["project_name"] = session.project_name
            session_group.attrs["start_time"] = session.start_time.isoformat()
            session_group.attrs["sample_rate"] = float(session.sampling_rate)
            session_group.attrs["sampling_rate"] = float(session.sampling_rate)
            session_group.attrs["total_samples"] = 0
            for key, value in session.metadata.items():
                session_group.attrs[key] = self._attribute_value(value)

            channel_metadata = metadata.create_group("channels")
            calibration = metadata.create_group("calibration")
            processed_group = handle.create_group("acquisition_data")
            raw_group = handle.create_group("raw_voltage")

            processed_group.create_dataset(
                "time",
                shape=(0,),
                maxshape=(None,),
                dtype="f8",
                chunks=(self.chunk_samples,),
            )

            self._channel_keys = []
            for channel in session.channels:
                key = f"channel_{channel.channel:02d}"
                self._channel_keys.append(key)
                chunk_shape = (self.chunk_samples,)

                processed_dataset = processed_group.create_dataset(
                    key,
                    shape=(0,),
                    maxshape=(None,),
                    dtype="f8",
                    chunks=chunk_shape,
                    compression="lzf",
                    shuffle=True,
                )
                raw_dataset = raw_group.create_dataset(
                    key,
                    shape=(0,),
                    maxshape=(None,),
                    dtype="f8",
                    chunks=chunk_shape,
                    compression="lzf",
                    shuffle=True,
                )

                channel_group = channel_metadata.create_group(key)
                channel_group.attrs["physical_channel"] = int(channel.channel)
                channel_group.attrs["label"] = channel.label
                channel_group.attrs["sensor_type"] = channel.sensor_type
                channel_group.attrs["physical_unit"] = channel.physical_units
                channel_group.attrs["voltage_unit"] = channel.units
                channel_group.attrs["input_range"] = channel.range_type.name
                channel_group.attrs["sensor_sensitivity"] = float(channel.sensor_sensitivity)

                calibration_group = calibration.create_group(key)
                calibration_group.attrs["offset"] = float(channel.calibration_offset)
                calibration_group.attrs["scale"] = float(channel.calibration_scale)
                calibration_group.attrs["sensitivity"] = float(channel.sensor_sensitivity)

                for dataset in (processed_dataset, raw_dataset):
                    dataset.attrs["physical_channel"] = int(channel.channel)
                    dataset.attrs["label"] = channel.label
                    dataset.attrs["sensor_type"] = channel.sensor_type
                processed_dataset.attrs["unit"] = channel.physical_units
                raw_dataset.attrs["unit"] = channel.units

            handle.flush()
            return path
        except Exception as exc:
            self._close_handle()
            raise RecordingError(f"Impossible de creer le fichier HDF5: {exc}") from exc

    def append(self, raw_data: np.ndarray, processed_data: np.ndarray) -> None:
        """Ajoute un bloc complet et le rend periodiquement visible sur disque."""
        if not self.is_open:
            raise RecordingError("Aucun fichier d'acquisition n'est ouvert")

        raw = np.asarray(raw_data, dtype=np.float64)
        processed = np.asarray(processed_data, dtype=np.float64)
        expected_channels = len(self._channel_keys)
        if raw.ndim != 2 or processed.ndim != 2:
            raise RecordingError("Les blocs d'acquisition doivent etre bidimensionnels")
        if raw.shape != processed.shape:
            raise RecordingError("Les blocs brut et physique n'ont pas la meme forme")
        if raw.shape[1] != expected_channels:
            raise RecordingError(
                f"Bloc de {raw.shape[1]} canaux recu, {expected_channels} attendus"
            )
        if raw.shape[0] == 0:
            return

        try:
            start = self.sample_count
            stop = start + raw.shape[0]
            processed_group = self._file["acquisition_data"]
            raw_group = self._file["raw_voltage"]

            time_dataset = processed_group["time"]
            time_dataset.resize((stop,))
            sample_rate = float(self._file["metadata/session"].attrs["sample_rate"])
            time_dataset[start:stop] = np.arange(start, stop, dtype=np.float64) / sample_rate

            for index, key in enumerate(self._channel_keys):
                processed_dataset = processed_group[key]
                raw_dataset = raw_group[key]
                processed_dataset.resize((stop,))
                raw_dataset.resize((stop,))
                processed_dataset[start:stop] = processed[:, index]
                raw_dataset[start:stop] = raw[:, index]

            self.sample_count = stop
            self._file.attrs["n_samples"] = stop
            self._file["metadata/session"].attrs["total_samples"] = stop

            now = time.monotonic()
            if now - self._last_flush >= self.flush_interval_seconds:
                self.flush()
        except Exception as exc:
            try:
                self.abort(str(exc))
            except Exception:
                # L'erreur initiale (disque plein, support retire, etc.) reste
                # celle qui doit etre remontee au controleur.
                pass
            raise RecordingError(f"Echec d'ecriture du bloc HDF5: {exc}") from exc

    def flush(self) -> None:
        """Force h5py a transmettre les donnees au systeme de fichiers."""
        if not self.is_open:
            return
        self._file.flush()
        self._last_flush = time.monotonic()

    def finalize(self, session: Any, statistics: dict[str, Any]) -> None:
        """Marque la session complete, vide les buffers et ferme le fichier."""
        if not self.is_open:
            return
        try:
            expected_samples = session.metadata.get("expected_samples")
            counters_are_clean = not any(
                int(statistics.get(key, 0))
                for key in ("errors", "buffer_overruns", "recording_errors")
            )
            sample_count_is_valid = (
                expected_samples is None or int(expected_samples) == self.sample_count
            )
            recording_status = (
                "complete" if counters_are_clean and sample_count_is_valid else "error"
            )
            session_group = self._file["metadata/session"]
            session_group.attrs["end_time"] = (
                session.end_time.isoformat() if session.end_time else ""
            )
            session_group.attrs["total_samples"] = int(self.sample_count)
            self._file.attrs["n_samples"] = int(self.sample_count)
            self._file.attrs["recording_status"] = recording_status
            if expected_samples is not None:
                self._file.attrs["expected_samples"] = int(expected_samples)
            if not sample_count_is_valid:
                self._file.attrs["recording_error"] = (
                    f"Nombre d'echantillons incomplet: {self.sample_count}/{expected_samples}"
                )
            self._file.attrs["completed_at"] = (
                session.end_time.isoformat() if session.end_time else ""
            )
            self._file.attrs["errors"] = int(statistics.get("errors", 0))
            self._file.attrs["buffer_overruns"] = int(
                statistics.get("buffer_overruns", 0)
            )
            self.flush()
        finally:
            self._close_handle()

    def abort(self, reason: str) -> None:
        """Conserve un fichier partiel explicitement marque en erreur."""
        if not self.is_open:
            return
        try:
            self._file.attrs["recording_status"] = "error"
            self._file.attrs["recording_error"] = str(reason)
            self._file.attrs["n_samples"] = int(self.sample_count)
            self.flush()
        finally:
            self._close_handle()

    def close(self) -> None:
        """Ferme un enregistrement incomplet sans le presenter comme valide."""
        if self.is_open:
            self.abort("Enregistrement ferme avant finalisation")

    @staticmethod
    def _attribute_value(value: Any) -> Any:
        if value is None:
            return ""
        if isinstance(value, (str, int, float, bool, np.integer, np.floating)):
            return value
        return json.dumps(value, ensure_ascii=False, default=str)

    def _close_handle(self) -> None:
        handle = self._file
        self._file = None
        if handle is not None:
            handle.close()


def inspect_recording(file_path: str | Path) -> dict[str, Any]:
    """Controle rapidement une session sans charger les signaux en memoire."""
    try:
        import h5py
    except ImportError as exc:
        raise RecordingError("h5py est requis pour inspecter une session") from exc

    path = Path(file_path).expanduser().resolve()
    if not path.is_file():
        raise RecordingError(f"Fichier de session introuvable: {path}")

    try:
        with h5py.File(path, "r") as handle:
            status = str(handle.attrs.get("recording_status", "unknown"))
            declared_samples = int(handle.attrs.get("n_samples", -1))
            errors = int(handle.attrs.get("errors", 0))
            overruns = int(handle.attrs.get("buffer_overruns", 0))
            processed_group = handle.get("acquisition_data")
            raw_group = handle.get("raw_voltage")
            session_group = handle.get("metadata/session")

            issues: list[str] = []
            if processed_group is None or raw_group is None or session_group is None:
                issues.append("Structure HDF5 incomplete")
                channel_keys: list[str] = []
                sample_rate = 0.0
                lengths: dict[str, int] = {}
            else:
                channel_keys = sorted(
                    key for key in processed_group.keys() if key.startswith("channel_")
                )
                raw_keys = sorted(key for key in raw_group.keys() if key.startswith("channel_"))
                sample_rate = float(session_group.attrs.get("sample_rate", 0.0))
                lengths = {key: int(processed_group[key].shape[0]) for key in channel_keys}
                raw_lengths = {key: int(raw_group[key].shape[0]) for key in raw_keys}

                if channel_keys != raw_keys:
                    issues.append("Les listes de canaux brut et physique different")
                if "time" not in processed_group:
                    issues.append("Axe temporel absent")
                elif int(processed_group["time"].shape[0]) != declared_samples:
                    issues.append("Longueur de l'axe temporel incoherente")
                if any(length != declared_samples for length in lengths.values()):
                    issues.append("Longueur incoherente dans les donnees physiques")
                if any(length != declared_samples for length in raw_lengths.values()):
                    issues.append("Longueur incoherente dans les tensions brutes")
                if sample_rate <= 0:
                    issues.append("Frequence d'echantillonnage invalide")

            if status != "complete":
                issues.append(f"Session non complete: {status}")
            if declared_samples <= 0:
                issues.append("Aucun echantillon enregistre")
            if errors:
                issues.append(f"{errors} erreur(s) signalee(s)")
            if overruns:
                issues.append(f"{overruns} debordement(s) de buffer")

            return {
                "ok": not issues,
                "file": str(path),
                "recording_status": status,
                "format_version": str(handle.attrs.get("format_version", "unknown")),
                "session_id": str(
                    session_group.attrs.get("session_id", "") if session_group else ""
                ),
                "project_name": str(
                    session_group.attrs.get("project_name", "") if session_group else ""
                ),
                "sample_rate": sample_rate,
                "n_channels": len(channel_keys),
                "n_samples": declared_samples,
                "duration_seconds": (
                    declared_samples / sample_rate if sample_rate > 0 else None
                ),
                "errors": errors,
                "buffer_overruns": overruns,
                "channel_lengths": lengths,
                "issues": issues,
            }
    except RecordingError:
        raise
    except Exception as exc:
        raise RecordingError(f"Impossible de lire la session HDF5: {exc}") from exc
