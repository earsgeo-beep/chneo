"""Qualification traçable d'une chaîne d'acquisition physique.

Le moteur analyse le fichier HDF5 maître après l'essai. Il ne décide jamais à
partir du tampon d'affichage et ne modifie pas les données sources.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

import numpy as np

from .session_recorder import RecordingError, inspect_recording

QUALIFICATION_SCHEMA_VERSION = "1.1.0"
VERDICT_ACCEPTED = "accepted"
VERDICT_REFUSED = "refused"


def _json_safe(value: Any) -> Any:
    """Remplace les nombres non finis afin qu'un rapport de refus reste sérialisable."""

    if isinstance(value, np.generic):
        value = value.item()
    if isinstance(value, float) and not math.isfinite(value):
        return None
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    return value


class QualificationError(RuntimeError):
    """Le rapport ne peut pas être construit de manière fiable."""


@dataclass(frozen=True)
class QualificationCriteria:
    """Seuils explicites appliqués à une session de qualification."""

    profile_name: str
    minimum_duration_seconds: float
    protocol_id: str = ""
    protocol_stage: str = ""
    required_channel_count: int | None = None
    minimum_distinct_ranges: int = 1
    require_protocol_attestation: bool = False
    maximum_rate_relative_error: float = 0.01
    maximum_wall_rate_relative_error: float | None = 0.10
    maximum_timing_error_ratio: float = 0.05
    maximum_missing_samples: int = 0
    saturation_level_fraction: float = 0.999
    maximum_saturation_fraction: float = 0.0
    maximum_abs_mean_fraction_of_range: float | None = None
    maximum_noise_rms_fraction_of_range: float | None = None
    maximum_peak_to_peak_fraction_of_range: float | None = None
    require_expected_samples: bool = True
    require_backend_timing_evidence: bool = True

    def __post_init__(self) -> None:
        if not self.profile_name.strip():
            raise ValueError("Le profil de qualification doit être nommé")
        bounded_fractions = (
            self.maximum_rate_relative_error,
            self.maximum_timing_error_ratio,
            self.saturation_level_fraction,
            self.maximum_saturation_fraction,
        )
        if self.minimum_duration_seconds <= 0:
            raise ValueError("La durée minimale doit être positive")
        if self.maximum_missing_samples < 0:
            raise ValueError("Le nombre d'échantillons manquants toléré ne peut pas être négatif")
        if self.required_channel_count is not None and self.required_channel_count <= 0:
            raise ValueError("Le nombre de voies exigé doit être positif")
        if self.minimum_distinct_ranges <= 0:
            raise ValueError("Le nombre de plages distinctes doit être positif")
        if any(not math.isfinite(value) or value < 0 for value in bounded_fractions):
            raise ValueError("Les seuils de qualification doivent être finis et positifs")
        if not 0 < self.saturation_level_fraction <= 1:
            raise ValueError("Le niveau de saturation doit appartenir à ]0, 1]")
        for value in (
            self.maximum_wall_rate_relative_error,
            self.maximum_abs_mean_fraction_of_range,
            self.maximum_noise_rms_fraction_of_range,
            self.maximum_peak_to_peak_fraction_of_range,
        ):
            if value is not None and (not math.isfinite(value) or value < 0):
                raise ValueError("Les seuils de voie doivent être finis et positifs")

    @classmethod
    def quick_functional(
        cls,
        minimum_duration_seconds: float = 3.0,
        *,
        check_wall_clock: bool = True,
    ) -> QualificationCriteria:
        """Profil court: intégrité, cadence, continuité et saturation."""

        return cls(
            profile_name="quick_functional",
            minimum_duration_seconds=float(minimum_duration_seconds),
            maximum_wall_rate_relative_error=0.10 if check_wall_clock else None,
        )

    @classmethod
    def grounded_inputs(
        cls,
        minimum_duration_seconds: float = 60.0,
        *,
        check_wall_clock: bool = True,
    ) -> QualificationCriteria:
        """Profil préliminaire avec entrées reliées à la masse analogique."""

        return cls(
            profile_name="grounded_inputs",
            minimum_duration_seconds=float(minimum_duration_seconds),
            maximum_wall_rate_relative_error=0.05 if check_wall_clock else None,
            maximum_abs_mean_fraction_of_range=0.005,
            maximum_noise_rms_fraction_of_range=0.001,
            maximum_peak_to_peak_fraction_of_range=0.01,
        )


@dataclass(frozen=True)
class QualificationCheck:
    code: str
    scope: str
    description: str
    passed: bool
    observed: Any
    limit: Any
    unit: str = ""
    message: str = ""

    def to_dict(self) -> dict[str, Any]:
        return _json_safe(asdict(self))


@dataclass(frozen=True)
class ChannelQualificationMetrics:
    channel_key: str
    physical_channel: int
    label: str
    range_limit_volts: float
    sample_count: int
    finite_count: int
    non_finite_count: int
    minimum_volts: float
    maximum_volts: float
    mean_volts: float
    rms_volts: float
    noise_rms_volts: float
    peak_to_peak_volts: float
    saturation_count: int
    saturation_fraction: float

    def to_dict(self) -> dict[str, Any]:
        return _json_safe(asdict(self))


@dataclass(frozen=True)
class QualificationReport:
    qualification_id: str
    evaluated_at_utc: str
    schema_version: str
    verdict: str
    profile_name: str
    source_master_file: str
    source_sha256: str
    criteria: QualificationCriteria
    device: dict[str, Any]
    session: dict[str, Any]
    channels: tuple[ChannelQualificationMetrics, ...]
    checks: tuple[QualificationCheck, ...]

    @property
    def accepted(self) -> bool:
        return self.verdict == VERDICT_ACCEPTED

    def to_dict(self) -> dict[str, Any]:
        passed_count = sum(check.passed for check in self.checks)
        return {
            "qualification_id": self.qualification_id,
            "evaluated_at_utc": self.evaluated_at_utc,
            "schema_version": self.schema_version,
            "verdict": self.verdict,
            "accepted": self.accepted,
            "profile_name": self.profile_name,
            "source_master_file": self.source_master_file,
            "source_sha256": self.source_sha256,
            "summary": {
                "checks_total": len(self.checks),
                "checks_passed": passed_count,
                "checks_failed": len(self.checks) - passed_count,
                "channels_evaluated": len(self.channels),
            },
            "criteria": asdict(self.criteria),
            "device": self.device,
            "session": self.session,
            "channels": [channel.to_dict() for channel in self.channels],
            "checks": [check.to_dict() for check in self.checks],
        }


class HardwareQualificationService:
    """Produit un verdict reproductible depuis un HDF5 maître terminé."""

    def __init__(self, chunk_samples: int = 65_536) -> None:
        if chunk_samples <= 0:
            raise ValueError("chunk_samples doit être positif")
        self.chunk_samples = int(chunk_samples)

    def evaluate(
        self,
        source_file: str | Path,
        criteria: QualificationCriteria,
    ) -> QualificationReport:
        try:
            import h5py
        except ImportError as exc:
            raise QualificationError("h5py est requis pour qualifier une acquisition") from exc

        source = Path(source_file).expanduser().resolve()
        try:
            inspection = inspect_recording(source)
        except RecordingError as exc:
            raise QualificationError(str(exc)) from exc

        checks: list[QualificationCheck] = [
            self._check(
                "recording_integrity",
                "session",
                "Le fichier maître est complet et cohérent",
                bool(inspection.get("ok")),
                inspection.get("issues", []),
                "aucune anomalie",
                message="; ".join(inspection.get("issues", [])),
            )
        ]

        try:
            with h5py.File(source, "r") as handle:
                root = self._attributes(handle.attrs)
                session_group = handle.get("metadata/session")
                session = self._attributes(session_group.attrs) if session_group is not None else {}
                metadata = {**root, **session}
                device = self._device_metadata(metadata)
                checks.extend(self._session_checks(handle, metadata, criteria))
                channels = self._channel_metrics(handle, criteria)
                checks.extend(self._channel_checks(channels, criteria))
        except QualificationError:
            raise
        except Exception as exc:
            raise QualificationError(f"Analyse de qualification impossible: {exc}") from exc

        verdict = VERDICT_ACCEPTED if all(check.passed for check in checks) else VERDICT_REFUSED
        return QualificationReport(
            qualification_id=str(uuid4()),
            evaluated_at_utc=datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            schema_version=QUALIFICATION_SCHEMA_VERSION,
            verdict=verdict,
            profile_name=criteria.profile_name,
            source_master_file=str(source),
            source_sha256=self._sha256(source),
            criteria=criteria,
            device=device,
            session={
                key: metadata.get(key)
                for key in (
                    "session_id",
                    "project_name",
                    "start_time",
                    "end_time",
                    "requested_sampling_rate",
                    "actual_sampling_rate",
                    "expected_samples",
                    "total_samples",
                    "acquisition_wall_elapsed_seconds",
                    "qualification_protocol_id",
                    "qualification_stage",
                    "qualification_checklist_confirmed_at",
                )
            },
            channels=tuple(channels),
            checks=tuple(checks),
        )

    def _session_checks(self, handle, metadata, criteria) -> list[QualificationCheck]:
        sample_count = int(handle.attrs.get("n_samples", 0))
        actual_rate = self._positive_float(
            metadata.get("actual_sampling_rate", metadata.get("sample_rate_hz"))
        )
        requested_rate = self._positive_float(metadata.get("requested_sampling_rate"))
        nominal_duration = sample_count / actual_rate if actual_rate else 0.0
        expected_samples = self._optional_int(metadata.get("expected_samples"))
        backend_blocks = int(handle.attrs.get("backend_blocks", 0))
        timing_evidence = "timing_discontinuities" in handle.attrs and backend_blocks > 0
        timing_discontinuities = int(handle.attrs.get("timing_discontinuities", 0))
        maximum_timing_error = float(handle.attrs.get("max_timing_error_seconds", 0.0))
        timing_limit = (
            criteria.maximum_timing_error_ratio / actual_rate if actual_rate else 0.0
        )
        backend_start = self._finite_float(metadata.get("backend_time_start_seconds"))
        backend_end = self._finite_float(metadata.get("backend_time_end_seconds"))

        identity_present = bool(
            str(metadata.get("hardware_driver_id", "")).strip()
            and str(metadata.get("hardware_model", "")).strip()
        )
        checks = [
            self._check(
                "hardware_identity",
                "device",
                "Le pilote et le modèle sont identifiés",
                identity_present,
                {
                    "driver": metadata.get("hardware_driver_id", ""),
                    "model": metadata.get("hardware_model", ""),
                    "serial": metadata.get("hardware_serial_number", ""),
                },
                "driver et modèle présents",
            ),
            self._check(
                "minimum_duration",
                "session",
                "La durée nominale atteint le palier demandé",
                nominal_duration + 1e-12 >= criteria.minimum_duration_seconds,
                nominal_duration,
                criteria.minimum_duration_seconds,
                "s",
            ),
        ]

        if criteria.require_protocol_attestation:
            recorded_protocol = str(metadata.get("qualification_protocol_id", ""))
            recorded_stage = str(metadata.get("qualification_stage", ""))
            checklist = metadata.get("qualification_operator_checklist", [])
            if not isinstance(checklist, list):
                checklist = []
            attested = bool(
                metadata.get("qualification_intent") is True
                and recorded_protocol == criteria.protocol_id
                and recorded_stage == criteria.protocol_stage
                and checklist
                and str(metadata.get("qualification_checklist_confirmed_at", "")).strip()
            )
            checks.append(
                self._check(
                    "protocol_attestation",
                    "session",
                    "Le palier et la checklist opérateur sont attestés dans le fichier maître",
                    attested,
                    {
                        "protocol_id": recorded_protocol,
                        "stage": recorded_stage,
                        "checklist_items": len(checklist),
                        "confirmed_at": metadata.get(
                            "qualification_checklist_confirmed_at",
                            "",
                        ),
                    },
                    {
                        "protocol_id": criteria.protocol_id,
                        "stage": criteria.protocol_stage,
                        "checklist_required": True,
                    },
                )
            )

        channel_group = handle.get("metadata/channels")
        channel_count = len(channel_group) if channel_group is not None else 0
        distinct_ranges = (
            {
                str(group.attrs.get("input_range", "")).strip()
                for group in channel_group.values()
                if str(group.attrs.get("input_range", "")).strip()
            }
            if channel_group is not None
            else set()
        )
        if criteria.required_channel_count is not None:
            checks.append(
                self._check(
                    "protocol_channel_count",
                    "session",
                    "Le nombre de voies respecte le palier du protocole",
                    channel_count == criteria.required_channel_count,
                    channel_count,
                    criteria.required_channel_count,
                    "channels",
                )
            )
        if criteria.minimum_distinct_ranges > 1:
            checks.append(
                self._check(
                    "protocol_distinct_ranges",
                    "session",
                    "Le palier utilise le nombre requis de plages électriques distinctes",
                    len(distinct_ranges) >= criteria.minimum_distinct_ranges,
                    sorted(distinct_ranges),
                    {"minimum_distinct_ranges": criteria.minimum_distinct_ranges},
                )
            )

        if criteria.require_expected_samples:
            missing = abs(sample_count - expected_samples) if expected_samples is not None else None
            checks.append(
                self._check(
                    "sample_count",
                    "session",
                    "Le nombre d'échantillons correspond au contrat",
                    missing is not None and missing <= criteria.maximum_missing_samples,
                    {"recorded": sample_count, "expected": expected_samples, "difference": missing},
                    {"maximum_difference": criteria.maximum_missing_samples},
                    "samples",
                )
            )

        relative_rate_error = (
            abs(actual_rate - requested_rate) / requested_rate
            if actual_rate is not None and requested_rate is not None
            else None
        )
        checks.append(
            self._check(
                "sample_rate",
                "session",
                "La fréquence effective respecte la fréquence demandée",
                relative_rate_error is not None
                and relative_rate_error <= criteria.maximum_rate_relative_error,
                {
                    "requested_hz": requested_rate,
                    "actual_hz": actual_rate,
                    "relative_error": relative_rate_error,
                },
                criteria.maximum_rate_relative_error,
                "relative",
            )
        )
        if criteria.maximum_wall_rate_relative_error is not None:
            wall_elapsed = self._positive_float(
                metadata.get("acquisition_wall_elapsed_seconds")
            )
            wall_rate = sample_count / wall_elapsed if wall_elapsed is not None else None
            wall_rate_error = (
                abs(wall_rate - actual_rate) / actual_rate
                if wall_rate is not None and actual_rate is not None
                else None
            )
            checks.append(
                self._check(
                    "wall_clock_rate",
                    "session",
                    "La cadence observée par l'horloge monotone est cohérente",
                    wall_rate_error is not None
                    and wall_rate_error <= criteria.maximum_wall_rate_relative_error,
                    {
                        "elapsed_seconds": wall_elapsed,
                        "observed_rate_hz": wall_rate,
                        "relative_error": wall_rate_error,
                    },
                    criteria.maximum_wall_rate_relative_error,
                    "relative",
                )
            )
        if criteria.require_backend_timing_evidence:
            checks.append(
                self._check(
                    "timing_evidence",
                    "session",
                    "La continuité des blocs du pilote a été surveillée",
                    timing_evidence,
                    {"present": timing_evidence, "backend_blocks": backend_blocks},
                    {"present": True, "minimum_backend_blocks": 1},
                )
            )
        checks.extend(
            [
                self._check(
                    "timing_continuity",
                    "session",
                    "Aucune discontinuité temporelle n'est détectée",
                    timing_evidence and timing_discontinuities == 0,
                    timing_discontinuities,
                    0,
                    "events",
                ),
                self._check(
                    "timing_error",
                    "session",
                    "L'erreur temporelle reste sous la tolérance",
                    timing_evidence
                    and actual_rate is not None
                    and maximum_timing_error <= timing_limit,
                    maximum_timing_error,
                    timing_limit,
                    "s",
                ),
                self._backend_time_span_check(
                    sample_count,
                    actual_rate,
                    backend_start,
                    backend_end,
                    timing_limit,
                ),
                self._time_axis_check(handle, actual_rate, sample_count),
            ]
        )
        return checks

    def _backend_time_span_check(
        self,
        sample_count,
        sample_rate,
        backend_start,
        backend_end,
        tolerance,
    ) -> QualificationCheck:
        expected_span = (
            (sample_count - 1) / sample_rate
            if sample_rate is not None and sample_count > 0
            else None
        )
        observed_span = (
            backend_end - backend_start
            if backend_start is not None and backend_end is not None
            else None
        )
        passed = bool(
            observed_span is not None
            and expected_span is not None
            and abs(observed_span - expected_span) <= tolerance
        )
        return self._check(
            "backend_time_span",
            "session",
            "La durée fournie par le pilote correspond au nombre d'échantillons",
            passed,
            {
                "start_seconds": backend_start,
                "end_seconds": backend_end,
                "span_seconds": observed_span,
            },
            {"expected_span_seconds": expected_span, "tolerance_seconds": tolerance},
            "s",
        )

    def _time_axis_check(self, handle, sample_rate, sample_count) -> QualificationCheck:
        time_dataset = handle.get("acquisition_data/time")
        observed: dict[str, Any] = {"sample_count": sample_count}
        passed = bool(time_dataset is not None and sample_rate is not None and sample_count > 0)
        if passed:
            first = float(time_dataset[0])
            last = float(time_dataset[-1])
            expected_last = (sample_count - 1) / sample_rate
            tolerance = max(1e-12, (1.0 / sample_rate) * 1e-6)
            observed.update(first_seconds=first, last_seconds=last)
            passed = abs(first) <= tolerance and abs(last - expected_last) <= tolerance
        else:
            expected_last = None
        return self._check(
            "recorded_time_axis",
            "session",
            "L'axe temps enregistré correspond au compteur d'échantillons",
            passed,
            observed,
            {"first_seconds": 0.0, "last_seconds": expected_last},
            "s",
        )

    def _channel_metrics(self, handle, criteria) -> list[ChannelQualificationMetrics]:
        raw_group = handle.get("raw_voltage")
        channel_group = handle.get("metadata/channels")
        if raw_group is None or channel_group is None:
            raise QualificationError("Tensions brutes ou métadonnées des canaux absentes")

        metrics: list[ChannelQualificationMetrics] = []
        for key in sorted(name for name in raw_group if name.startswith("channel_")):
            dataset = raw_group[key]
            metadata = self._attributes(channel_group[key].attrs) if key in channel_group else {}
            range_min = self._finite_float(metadata.get("input_range_min_v"))
            range_max = self._finite_float(metadata.get("input_range_max_v"))
            if range_min is None or range_max is None:
                range_limit = 0.0
            else:
                range_limit = max(abs(range_min), abs(range_max))
            metrics.append(
                self._measure_channel(
                    key,
                    dataset,
                    metadata,
                    range_limit,
                    criteria.saturation_level_fraction,
                )
            )
        if not metrics:
            raise QualificationError("Aucun canal brut ne peut être qualifié")
        return metrics

    def _measure_channel(
        self,
        key,
        dataset,
        metadata,
        range_limit,
        saturation_level,
    ) -> ChannelQualificationMetrics:
        sample_count = int(dataset.shape[0])
        finite_count = 0
        non_finite_count = 0
        total = 0.0
        total_squares = 0.0
        minimum = math.inf
        maximum = -math.inf
        saturation_count = 0
        saturation_threshold = range_limit * saturation_level

        for start in range(0, sample_count, self.chunk_samples):
            stop = min(start + self.chunk_samples, sample_count)
            values = np.asarray(dataset[start:stop], dtype=np.float64)
            finite_mask = np.isfinite(values)
            finite = values[finite_mask]
            non_finite_count += int(values.size - finite.size)
            if not finite.size:
                continue
            finite_count += int(finite.size)
            total += float(np.sum(finite, dtype=np.float64))
            total_squares += float(np.sum(finite * finite, dtype=np.float64))
            minimum = min(minimum, float(np.min(finite)))
            maximum = max(maximum, float(np.max(finite)))
            if saturation_threshold > 0:
                saturation_count += int(np.count_nonzero(np.abs(finite) >= saturation_threshold))

        if finite_count:
            mean = total / finite_count
            rms = math.sqrt(max(0.0, total_squares / finite_count))
            variance = max(0.0, total_squares / finite_count - mean * mean)
            noise_rms = math.sqrt(variance)
            peak_to_peak = maximum - minimum
        else:
            minimum = maximum = mean = rms = noise_rms = peak_to_peak = math.nan

        return ChannelQualificationMetrics(
            channel_key=key,
            physical_channel=int(metadata.get("physical_channel", -1)),
            label=str(metadata.get("label", key)),
            range_limit_volts=float(range_limit),
            sample_count=sample_count,
            finite_count=finite_count,
            non_finite_count=non_finite_count,
            minimum_volts=minimum,
            maximum_volts=maximum,
            mean_volts=mean,
            rms_volts=rms,
            noise_rms_volts=noise_rms,
            peak_to_peak_volts=peak_to_peak,
            saturation_count=saturation_count,
            saturation_fraction=(saturation_count / finite_count if finite_count else 1.0),
        )

    def _channel_checks(self, channels, criteria) -> list[QualificationCheck]:
        checks: list[QualificationCheck] = []
        for channel in channels:
            scope = channel.channel_key
            checks.extend(
                [
                    self._check(
                        "finite_values",
                        scope,
                        "Toutes les tensions brutes sont finies",
                        channel.non_finite_count == 0,
                        channel.non_finite_count,
                        0,
                        "samples",
                    ),
                    self._check(
                        "input_range_known",
                        scope,
                        "La plage électrique du canal est traçable",
                        channel.range_limit_volts > 0,
                        channel.range_limit_volts,
                        "> 0",
                        "V",
                    ),
                    self._check(
                        "saturation",
                        scope,
                        "La proportion de valeurs proches de la pleine échelle est acceptable",
                        channel.saturation_fraction <= criteria.maximum_saturation_fraction,
                        channel.saturation_fraction,
                        criteria.maximum_saturation_fraction,
                        "fraction",
                    ),
                ]
            )
            if criteria.maximum_abs_mean_fraction_of_range is not None:
                limit = channel.range_limit_volts * criteria.maximum_abs_mean_fraction_of_range
                checks.append(
                    self._check(
                        "ground_offset",
                        scope,
                        "L'offset avec entrée à la masse reste sous le seuil",
                        channel.range_limit_volts > 0 and abs(channel.mean_volts) <= limit,
                        abs(channel.mean_volts),
                        limit,
                        "V",
                    )
                )
            if criteria.maximum_noise_rms_fraction_of_range is not None:
                limit = channel.range_limit_volts * criteria.maximum_noise_rms_fraction_of_range
                checks.append(
                    self._check(
                        "ground_noise_rms",
                        scope,
                        "Le bruit RMS avec entrée à la masse reste sous le seuil",
                        channel.range_limit_volts > 0 and channel.noise_rms_volts <= limit,
                        channel.noise_rms_volts,
                        limit,
                        "V RMS",
                    )
                )
            if criteria.maximum_peak_to_peak_fraction_of_range is not None:
                limit = channel.range_limit_volts * criteria.maximum_peak_to_peak_fraction_of_range
                checks.append(
                    self._check(
                        "ground_peak_to_peak",
                        scope,
                        "Le bruit crête-à-crête avec entrée à la masse reste sous le seuil",
                        channel.range_limit_volts > 0 and channel.peak_to_peak_volts <= limit,
                        channel.peak_to_peak_volts,
                        limit,
                        "V",
                    )
                )
        return checks

    @staticmethod
    def _check(code, scope, description, passed, observed, limit, unit="", message=""):
        return QualificationCheck(
            code=str(code),
            scope=str(scope),
            description=str(description),
            passed=bool(passed),
            observed=observed,
            limit=limit,
            unit=str(unit),
            message=str(message),
        )

    @staticmethod
    def _device_metadata(metadata: dict[str, Any]) -> dict[str, Any]:
        return {
            "driver_id": metadata.get("hardware_driver_id", ""),
            "device_id": metadata.get("hardware_device_id", ""),
            "vendor": metadata.get("hardware_vendor", ""),
            "model": metadata.get("hardware_model", ""),
            "serial_number": metadata.get("hardware_serial_number", ""),
            "transport": metadata.get("hardware_transport", ""),
            "display_name": metadata.get("hardware_display_name", ""),
        }

    @classmethod
    def _attributes(cls, attributes) -> dict[str, Any]:
        return {key: cls._normalize(value) for key, value in attributes.items()}

    @classmethod
    def _normalize(cls, value: Any) -> Any:
        if isinstance(value, bytes):
            value = value.decode("utf-8", errors="replace")
        if isinstance(value, np.generic):
            value = value.item()
        if isinstance(value, str) and value.strip().startswith(("[", "{")):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        if isinstance(value, (str, int, float, bool)) or value is None:
            return value
        return str(value)

    @staticmethod
    def _positive_float(value: Any) -> float | None:
        try:
            number = float(value)
        except (TypeError, ValueError):
            return None
        return number if math.isfinite(number) and number > 0 else None

    @staticmethod
    def _finite_float(value: Any) -> float | None:
        try:
            number = float(value)
        except (TypeError, ValueError):
            return None
        return number if math.isfinite(number) else None

    @staticmethod
    def _optional_int(value: Any) -> int | None:
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _sha256(path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()


class QualificationReportWriter:
    """Écrit un rapport autonome sans modifier le fichier maître qualifié."""

    def write_bundle(
        self,
        report: QualificationReport,
        output_directory: str | Path,
    ) -> tuple[Path, Path]:
        directory = Path(output_directory).expanduser().resolve()
        directory.mkdir(parents=True, exist_ok=True)
        session_id = str(report.session.get("session_id") or "session")
        safe_session = re.sub(r"[^A-Za-z0-9._-]+", "_", session_id).strip("._-")
        suffix = report.qualification_id.split("-", 1)[0]
        stage = re.sub(
            r"[^A-Za-z0-9._-]+",
            "_",
            report.criteria.protocol_stage,
        ).strip("._-")
        stage_prefix = f"{stage}_" if stage else ""
        base_name = (
            f"{safe_session}_{stage_prefix}{report.profile_name}_{suffix}_qualification"
        )
        json_path = self.write_json(report, directory / f"{base_name}.json")
        hdf5_path = self.write_hdf5(report, directory / f"{base_name}.h5")
        return json_path, hdf5_path

    @staticmethod
    def write_json(report: QualificationReport, output_file: str | Path) -> Path:
        path = Path(output_file).expanduser().resolve()
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("x", encoding="utf-8") as handle:
            json.dump(report.to_dict(), handle, indent=2, ensure_ascii=False, allow_nan=False)
        return path

    @staticmethod
    def write_hdf5(report: QualificationReport, output_file: str | Path) -> Path:
        try:
            import h5py
        except ImportError as exc:
            raise QualificationError("h5py est requis pour écrire le rapport HDF5") from exc

        path = Path(output_file).expanduser().resolve()
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = report.to_dict()
        with h5py.File(path, "x", libver="latest") as handle:
            handle.attrs["schema_version"] = report.schema_version
            handle.attrs["qualification_id"] = report.qualification_id
            handle.attrs["evaluated_at_utc"] = report.evaluated_at_utc
            handle.attrs["verdict"] = report.verdict
            handle.attrs["profile_name"] = report.profile_name
            handle.attrs["protocol_id"] = report.criteria.protocol_id
            handle.attrs["protocol_stage"] = report.criteria.protocol_stage
            handle.attrs["source_master_file"] = report.source_master_file
            handle.attrs["source_sha256"] = report.source_sha256
            string_type = h5py.string_dtype(encoding="utf-8")
            handle.create_dataset(
                "report_json",
                data=json.dumps(payload, ensure_ascii=False, allow_nan=False),
                dtype=string_type,
            )
            channels_group = handle.create_group("channels")
            for channel in report.channels:
                group = channels_group.create_group(channel.channel_key)
                for key, value in channel.to_dict().items():
                    group.attrs[key] = QualificationReportWriter._hdf5_value(value)
            checks_group = handle.create_group("checks")
            for index, check in enumerate(report.checks):
                group = checks_group.create_group(f"{index:03d}_{check.code}_{check.scope}")
                for key, value in check.to_dict().items():
                    group.attrs[key] = QualificationReportWriter._hdf5_value(value)
        return path

    @staticmethod
    def _hdf5_value(value: Any) -> Any:
        if value is None:
            return ""
        if isinstance(value, (str, int, float, bool, np.integer, np.floating)):
            return value
        return json.dumps(value, ensure_ascii=False, allow_nan=False)
