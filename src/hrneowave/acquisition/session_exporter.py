"""Exports intègres construits depuis le fichier HDF5 maître d'une session."""

from __future__ import annotations

import csv
import json
import shutil
from pathlib import Path
from typing import Any

import numpy as np

from hrneowave.core.session_schema import (
    CLOCK_DOMAIN,
    DATA_KIND_PHYSICAL,
    SCHEMA_VERSION,
    build_csv_metadata_row,
)

from .session_recorder import RecordingError, inspect_recording


class SessionExportError(RuntimeError):
    """L'export ne peut pas garantir l'intégrité ou l'exhaustivité des données."""


class SessionExporter:
    """Convertit une session complète sans utiliser le tampon d'aperçu mémoire."""

    def __init__(self, chunk_samples: int = 4096) -> None:
        if chunk_samples <= 0:
            raise ValueError("chunk_samples doit être positif")
        self.chunk_samples = int(chunk_samples)

    def export(self, source_file: str | Path, output_file: str | Path, format_name: str) -> Path:
        source = Path(source_file).expanduser().resolve()
        target = Path(output_file).expanduser().resolve()
        try:
            inspection = inspect_recording(source)
        except RecordingError as exc:
            raise SessionExportError(str(exc)) from exc
        if not inspection.get("ok"):
            issues = "; ".join(inspection.get("issues", [])) or "statut inconnu"
            raise SessionExportError(f"Session maître non exportable: {issues}")

        target.parent.mkdir(parents=True, exist_ok=True)
        normalized = format_name.lower()
        if normalized in {"hdf5", "h5"}:
            return self._copy_hdf5(source, target)
        if normalized == "csv":
            return self._export_csv(source, target)
        if normalized == "json":
            return self._export_json(source, target)
        raise SessionExportError(f"Format non supporté: {format_name}")

    @staticmethod
    def _copy_hdf5(source: Path, target: Path) -> Path:
        if source == target:
            return target
        shutil.copy2(source, target)
        return target

    def _export_csv(self, source: Path, target: Path) -> Path:
        import h5py

        with h5py.File(source, "r") as handle:
            metadata, channel_metadata, statistics = self._read_contract(handle)
            acquisition = handle["acquisition_data"]
            channel_keys = sorted(key for key in acquisition if key.startswith("channel_"))
            time_dataset = acquisition["time"]
            sample_count = int(time_dataset.shape[0])
            sample_rate = float(metadata["sample_rate_hz"])
            metadata_row = build_csv_metadata_row(
                sample_rate,
                DATA_KIND_PHYSICAL,
                sample_count,
            )

            with target.open("w", newline="", encoding="utf-8") as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(
                    ["time", "sample_rate", *metadata_row.keys(), *channel_keys]
                )
                repeated_metadata = list(metadata_row.values())
                for start in range(0, sample_count, self.chunk_samples):
                    stop = min(start + self.chunk_samples, sample_count)
                    time_values = np.asarray(time_dataset[start:stop], dtype=float)
                    channels = [
                        np.asarray(acquisition[key][start:stop], dtype=float)
                        for key in channel_keys
                    ]
                    matrix = np.column_stack(channels)
                    for index, row in enumerate(matrix):
                        writer.writerow(
                            [float(time_values[index]), sample_rate, *repeated_metadata, *row.tolist()]
                        )

        sidecar = {
            "metadata": metadata,
            "channel_metadata": channel_metadata,
            "statistics": statistics,
            "source_master_file": source.name,
        }
        Path(f"{target}.metadata.json").write_text(
            json.dumps(sidecar, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        return target

    def _export_json(self, source: Path, target: Path) -> Path:
        import h5py

        with h5py.File(source, "r") as handle, target.open("w", encoding="utf-8") as output:
            metadata, channel_metadata, statistics = self._read_contract(handle)
            acquisition = handle["acquisition_data"]
            raw_group = handle.get("raw_voltage")
            channel_keys = sorted(key for key in acquisition if key.startswith("channel_"))

            output.write('{"metadata":')
            json.dump(metadata, output, ensure_ascii=False, allow_nan=False)
            output.write(',"time":')
            self._write_dataset_array(output, acquisition["time"])
            output.write(',"channels":{')
            self._write_channel_group(output, acquisition, channel_keys)
            output.write('},"raw_channels":{')
            if raw_group is not None:
                self._write_channel_group(output, raw_group, channel_keys)
            output.write('},"session":')
            json.dump(
                {
                    "session_id": metadata.get("session_id", ""),
                    "project_name": metadata.get("project_name", ""),
                    "start_time": metadata.get("start_time", ""),
                    "end_time": metadata.get("end_time", ""),
                    "sampling_rate": metadata["sample_rate_hz"],
                    "total_samples": metadata["n_samples"],
                },
                output,
                ensure_ascii=False,
                allow_nan=False,
            )
            output.write(',"channel_metadata":')
            json.dump(channel_metadata, output, ensure_ascii=False, allow_nan=False)
            output.write(',"statistics":')
            json.dump(statistics, output, ensure_ascii=False, allow_nan=False)
            output.write('}')
        return target

    def _write_channel_group(self, output, group, channel_keys: list[str]) -> None:
        for index, key in enumerate(channel_keys):
            if index:
                output.write(",")
            output.write(json.dumps(key))
            output.write(":")
            self._write_dataset_array(output, group[key])

    def _write_dataset_array(self, output, dataset) -> None:
        output.write("[")
        first = True
        sample_count = int(dataset.shape[0])
        for start in range(0, sample_count, self.chunk_samples):
            stop = min(start + self.chunk_samples, sample_count)
            values = np.asarray(dataset[start:stop], dtype=float)
            for value in values:
                if not first:
                    output.write(",")
                output.write(json.dumps(float(value), allow_nan=False))
                first = False
        output.write("]")

    @classmethod
    def _read_contract(cls, handle) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, int]]:
        metadata = {key: cls._normalize(value) for key, value in handle.attrs.items()}
        if "metadata/session" in handle:
            for key, value in handle["metadata/session"].attrs.items():
                metadata.setdefault(key, cls._normalize(value))

        sample_rate = metadata.get("sample_rate_hz", metadata.get("sample_rate"))
        if sample_rate is None:
            raise SessionExportError("Fréquence d'échantillonnage absente du fichier maître")
        metadata["sample_rate_hz"] = float(sample_rate)
        metadata["sample_rate"] = float(sample_rate)
        metadata["sampling_rate"] = float(sample_rate)
        sample_count = int(handle.attrs["n_samples"])
        dt_seconds = 1.0 / float(sample_rate)
        metadata.update(
            {
                "schema_version": metadata.get("schema_version", SCHEMA_VERSION),
                "n_samples": sample_count,
                "dt_seconds": dt_seconds,
                "duration_s": sample_count / float(sample_rate),
                "time_start": 0.0,
                "time_end": (sample_count - 1) * dt_seconds if sample_count else 0.0,
                "clock_domain": metadata.get("clock_domain", CLOCK_DOMAIN),
                "data_kind": DATA_KIND_PHYSICAL,
            }
        )
        if metadata.get("hardware_available") is not True:
            raise SessionExportError(
                "Le fichier maître ne prouve pas l'utilisation d'un équipement physique"
            )
        if metadata.get("acquisition_source") != "physical_hardware":
            raise SessionExportError("La source d'acquisition physique n'est pas attestée")

        channel_metadata: list[dict[str, Any]] = []
        if "metadata/channels" in handle:
            for key, group in sorted(handle["metadata/channels"].items()):
                payload = {name: cls._normalize(value) for name, value in group.attrs.items()}
                payload.setdefault("key", key)
                channel_metadata.append(payload)
        metadata["channel_units"] = {
            item["key"]: item.get("physical_units", item.get("physical_unit", ""))
            for item in channel_metadata
        }

        statistics = {
            "errors": int(handle.attrs.get("errors", 0)),
            "buffer_overruns": int(handle.attrs.get("buffer_overruns", 0)),
            "recording_errors": int(handle.attrs.get("recording_errors", 0)),
            "timing_discontinuities": int(handle.attrs.get("timing_discontinuities", 0)),
            "max_timing_error_seconds": float(
                handle.attrs.get("max_timing_error_seconds", 0.0)
            ),
            "backend_blocks": int(handle.attrs.get("backend_blocks", 0)),
        }
        metadata.update(statistics)
        metadata["recording_status"] = str(handle.attrs.get("recording_status", "unknown"))
        return metadata, channel_metadata, statistics

    @classmethod
    def _normalize(cls, value: Any) -> Any:
        if isinstance(value, bytes):
            value = value.decode("utf-8", errors="replace")
        if isinstance(value, np.generic):
            value = value.item()
        if isinstance(value, str):
            stripped = value.strip()
            if stripped.startswith(("{", "[")):
                try:
                    return json.loads(stripped)
                except json.JSONDecodeError:
                    return value
        if isinstance(value, (str, int, float, bool)) or value is None:
            return value
        if isinstance(value, (list, tuple)):
            return [cls._normalize(item) for item in value]
        return str(value)
