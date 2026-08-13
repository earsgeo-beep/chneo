"""Lecteur strict du format ASCII RAW historique du laboratoire.

Le contrat observe est volontairement limite et valide avant tout calcul::

    ligne 1  frequence d'echantillonnage [Hz]
    ligne 2  duree declaree [s]
    ligne 3  nombre de canaux
    ligne 4  un coefficient multiplicatif par canal
    suite    index_echantillon, canal_1, ..., canal_n

Le lecteur ne devine jamais l'unite ni le sens metrologique des coefficients.
Ces informations doivent etre confirmees explicitement par l'operateur.
"""

from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from .session_schema import CLOCK_DOMAIN, SCHEMA_VERSION

IMPORTER_VERSION = "1.0"


class LegacyRawError(ValueError):
    """Le fichier ne respecte pas le contrat RAW historique attendu."""


@dataclass(frozen=True)
class LegacyRawHeader:
    sample_rate_hz: float
    declared_duration_s: float
    channel_count: int
    calibration_factors: tuple[float, ...]

    @property
    def expected_sample_count(self) -> int:
        return int(round(self.sample_rate_hz * self.declared_duration_s))


@dataclass(frozen=True)
class LegacyRawImportOptions:
    """Interpretation metrologique confirmee lors de l'import."""

    sensor_type: str
    physical_unit: str
    apply_calibration: bool = True
    calibration_confirmed: bool = False

    def validate(self) -> None:
        if not self.sensor_type.strip():
            raise LegacyRawError("Le type de signal RAW doit etre explicite")
        if self.apply_calibration and not self.physical_unit.strip():
            raise LegacyRawError("L'unite physique des coefficients RAW est obligatoire")
        if self.apply_calibration and not self.calibration_confirmed:
            raise LegacyRawError(
                "Confirmez que les coefficients RAW sont exprimes en unite/V "
                "et que le zero avait ete applique"
            )


def read_legacy_raw_header(file_path: str | Path) -> LegacyRawHeader:
    """Lit et valide les quatre lignes d'en-tete sans charger les mesures."""

    path = Path(file_path)
    try:
        content = path.read_text(encoding="ascii", errors="replace")
    except UnicodeDecodeError as exc:
        raise LegacyRawError("Le fichier RAW n'est pas un fichier ASCII compatible") from exc
    except OSError as exc:
        raise LegacyRawError(f"Lecture RAW impossible: {exc}") from exc

    lines = [line.strip() for line in content.splitlines() if line.strip()][:4]

    if len(lines) < 4:
        raise LegacyRawError("En-tete RAW incomplet: quatre lignes sont requises")
    try:
        sample_rate = float(lines[0])
        declared_duration = float(lines[1])
        channel_count_float = float(lines[2])
    except ValueError as exc:
        raise LegacyRawError("Frequence, duree ou nombre de canaux RAW invalide") from exc

    if not math.isfinite(sample_rate) or sample_rate <= 0:
        raise LegacyRawError("Frequence d'echantillonnage RAW invalide")
    if not math.isfinite(declared_duration) or declared_duration <= 0:
        raise LegacyRawError("Duree RAW invalide")
    if not channel_count_float.is_integer():
        raise LegacyRawError("Le nombre de canaux RAW n'est pas entier")
    channel_count = int(channel_count_float)
    if not 1 <= channel_count <= 256:
        raise LegacyRawError("Le nombre de canaux RAW est hors limites")

    factor_tokens = lines[3].split()
    if len(factor_tokens) != channel_count:
        raise LegacyRawError(
            f"En-tete RAW: {len(factor_tokens)} coefficients, {channel_count} canaux declares"
        )
    try:
        calibration_factors = np.asarray(
            [float(token) for token in factor_tokens],
            dtype=np.float64,
        )
    except ValueError as exc:
        raise LegacyRawError("Coefficient de calibration RAW invalide") from exc
    if not np.all(np.isfinite(calibration_factors)):
        raise LegacyRawError("Coefficient de calibration RAW non fini")
    if np.any(calibration_factors == 0.0):
        raise LegacyRawError("Un coefficient de calibration RAW est nul")

    expected_samples_float = sample_rate * declared_duration
    if not np.isclose(
        expected_samples_float,
        round(expected_samples_float),
        rtol=0.0,
        atol=1e-6,
    ):
        raise LegacyRawError("La duree RAW ne correspond pas a un nombre entier d'echantillons")

    return LegacyRawHeader(
        sample_rate_hz=sample_rate,
        declared_duration_s=declared_duration,
        channel_count=channel_count,
        calibration_factors=tuple(float(value) for value in calibration_factors),
    )


def load_legacy_raw(
    file_path: str | Path,
    options: LegacyRawImportOptions,
) -> dict[str, Any]:
    """Charge un RAW valide en conservant tension brute et valeur physique."""

    options.validate()
    path = Path(file_path)
    header = read_legacy_raw_header(path)
    try:
        content = path.read_text(encoding="ascii", errors="replace")
        lines = [line.strip() for line in content.splitlines() if line.strip()]
        measure_lines = lines[4:]
        if not measure_lines:
            raise LegacyRawError("Table de mesures RAW vide")
        rows = np.loadtxt(measure_lines, dtype=np.float64, ndmin=2)
    except (OSError, ValueError) as exc:
        raise LegacyRawError(f"Table de mesures RAW invalide: {exc}") from exc

    expected_columns = header.channel_count + 1
    if rows.ndim != 2 or rows.shape[1] != expected_columns:
        actual_columns = rows.shape[1] if rows.ndim == 2 else 0
        raise LegacyRawError(f"RAW: {actual_columns} colonnes detectees, {expected_columns} attendues")
    if rows.shape[0] != header.expected_sample_count:
        raise LegacyRawError(
            f"RAW incomplet: {rows.shape[0]} echantillons, {header.expected_sample_count} attendus"
        )
    if not np.all(np.isfinite(rows)):
        raise LegacyRawError("Le fichier RAW contient des valeurs NaN ou infinies")

    sample_indices = rows[:, 0]
    expected_indices = np.arange(rows.shape[0], dtype=np.float64)
    if not np.allclose(sample_indices, expected_indices, rtol=0.0, atol=1e-9):
        raise LegacyRawError("Les indices RAW ne sont pas continus depuis zero")

    raw_values = np.asarray(rows[:, 1:], dtype=np.float64)
    factors = np.asarray(header.calibration_factors, dtype=np.float64)
    if options.apply_calibration:
        physical_values = raw_values * factors[np.newaxis, :]
        physical_unit = options.physical_unit.strip()
        calibration_status = "valid"
        data_kind = "physical"
    else:
        physical_values = raw_values.copy()
        physical_unit = "V"
        calibration_status = "unverified"
        data_kind = "raw_voltage"

    source_hash = _sha256(path)
    channel_keys = [f"channel_{index:02d}" for index in range(header.channel_count)]
    raw_channels = {
        key: np.asarray(raw_values[:, index], dtype=np.float64) for index, key in enumerate(channel_keys)
    }
    channels = {
        key: np.asarray(physical_values[:, index], dtype=np.float64) for index, key in enumerate(channel_keys)
    }
    channel_metadata = []
    for index, key in enumerate(channel_keys):
        factor = float(factors[index])
        channel_metadata.append(
            {
                "key": key,
                "channel": index,
                "sensor_id": f"RAW-CH-{index + 1:02d}",
                "sensor_type": options.sensor_type.strip(),
                "physical_unit": physical_unit,
                "raw_unit": "V",
                "calibration_status": calibration_status,
                "calibration_id": f"legacy-raw-{source_hash[:16]}-{index:02d}",
                "calibration_source": "legacy_raw_header_operator_confirmed",
                "calibration_coefficients": {
                    "scale_physical_per_volt": factor if options.apply_calibration else 1.0,
                    "offset_physical": 0.0,
                },
                "conversion_formula": (
                    "physical = raw_voltage * scale_physical_per_volt"
                    if options.apply_calibration
                    else "physical = raw_voltage"
                ),
                "calibration_validity_scope": "legacy_file_conversion_only",
            }
        )

    sample_count = int(rows.shape[0])
    sample_rate = header.sample_rate_hz
    time_values = sample_indices / sample_rate
    metadata = {
        "schema_version": SCHEMA_VERSION,
        "legacy_raw_importer_version": IMPORTER_VERSION,
        "source_format": "legacy_raw_ascii_v1",
        "source_file_name": path.name,
        "source_sha256": source_hash,
        "acquisition_source": "legacy_external_measurement",
        "sample_rate": sample_rate,
        "sample_rate_hz": sample_rate,
        "dt_seconds": 1.0 / sample_rate,
        "n_samples": sample_count,
        "duration_s": sample_count / sample_rate,
        "declared_duration_s": header.declared_duration_s,
        "time_start": float(time_values[0]),
        "time_end": float(time_values[-1]),
        "clock_domain": CLOCK_DOMAIN,
        "data_kind": data_kind,
        "legacy_calibration_factors": list(header.calibration_factors),
        "legacy_calibration_convention": (
            "physical = raw_voltage * factor; zero offset confirmed"
            if options.apply_calibration
            else "coefficients preserved but not applied"
        ),
        "legacy_calibration_operator_confirmed": bool(options.calibration_confirmed),
    }
    integrity_warnings = []
    if not options.apply_calibration:
        integrity_warnings.append(
            "RAW_VOLTAGE_ONLY: coefficients historiques non appliques; les amplitudes restent en volts"
        )

    return {
        "source_format": "legacy_raw",
        "source_path": str(path),
        "metadata": metadata,
        "time": time_values,
        "channels": channels,
        "raw_channels": raw_channels,
        "channel_keys": channel_keys,
        "channel_metadata": channel_metadata,
        "integrity_warnings": integrity_warnings,
    }


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()
