"""Protocoles progressifs de qualification des équipements d'acquisition.

Le moteur de qualification reste générique. Ce module décrit des séquences de
banc interchangeables et associe un protocole à un modèle matériel sans faire
dépendre le contrôleur scientifique d'un constructeur.
"""

from __future__ import annotations

import json
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

from .hardware_qualification import QualificationCriteria


@dataclass(frozen=True)
class QualificationStage:
    """Palier opérateur reproductible d'un protocole matériel."""

    stage_id: str
    title: str
    description: str
    profile_name: str
    duration_seconds: float
    required_channel_count: int
    minimum_distinct_ranges: int = 1
    required_sample_rate_hz: float | None = None
    prerequisites: tuple[str, ...] = ()
    checklist: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.stage_id.strip() or not self.title.strip():
            raise ValueError("Un palier de qualification doit être identifié et nommé")
        if self.profile_name not in {"quick_functional", "grounded_inputs"}:
            raise ValueError(f"Profil de qualification inconnu: {self.profile_name}")
        if self.duration_seconds <= 0 or self.required_channel_count <= 0:
            raise ValueError("La durée et le nombre de voies doivent être positifs")
        if self.minimum_distinct_ranges <= 0:
            raise ValueError("Le nombre de plages distinctes doit être positif")
        if self.required_sample_rate_hz is not None and self.required_sample_rate_hz <= 0:
            raise ValueError("La fréquence imposée doit être positive")

    def criteria(
        self,
        protocol_id: str,
        *,
        check_wall_clock: bool = True,
    ) -> QualificationCriteria:
        if self.profile_name == "grounded_inputs":
            base = QualificationCriteria.grounded_inputs(
                self.duration_seconds,
                check_wall_clock=check_wall_clock,
            )
        else:
            base = QualificationCriteria.quick_functional(
                self.duration_seconds,
                check_wall_clock=check_wall_clock,
            )
        return replace(
            base,
            protocol_id=protocol_id,
            protocol_stage=self.stage_id,
            required_channel_count=self.required_channel_count,
            minimum_distinct_ranges=self.minimum_distinct_ranges,
            require_protocol_attestation=True,
        )

    def validate_setup(
        self,
        channels: Sequence[Any],
        sample_rate_hz: float,
    ) -> tuple[str, ...]:
        issues: list[str] = []
        if len(channels) != self.required_channel_count:
            issues.append(
                f"{self.required_channel_count} voie(s) active(s) requise(s), "
                f"{len(channels)} configurée(s)"
            )
        ranges = {
            str(getattr(getattr(channel, "voltage_range", None), "label", "")).strip()
            for channel in channels
        }
        ranges.discard("")
        if len(ranges) < self.minimum_distinct_ranges:
            issues.append(
                f"{self.minimum_distinct_ranges} plage(s) électrique(s) distincte(s) requise(s)"
            )
        if (
            self.required_sample_rate_hz is not None
            and abs(float(sample_rate_hz) - self.required_sample_rate_hz)
            > max(1e-9, self.required_sample_rate_hz * 1e-9)
        ):
            issues.append(f"fréquence requise: {self.required_sample_rate_hz:g} Hz")
        return tuple(issues)


@dataclass(frozen=True)
class HardwareQualificationProtocol:
    protocol_id: str
    name: str
    description: str
    stages: tuple[QualificationStage, ...]
    driver_ids: tuple[str, ...] = ()
    model_names: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.protocol_id.strip() or not self.name.strip() or not self.stages:
            raise ValueError("Le protocole doit être identifié, nommé et contenir des paliers")
        stage_ids = [stage.stage_id for stage in self.stages]
        if len(stage_ids) != len(set(stage_ids)):
            raise ValueError("Les identifiants de paliers doivent être uniques")
        preceding: set[str] = set()
        for stage in self.stages:
            invalid = set(stage.prerequisites) - preceding
            if invalid:
                raise ValueError(
                    f"Les prérequis de {stage.stage_id} doivent être des paliers précédents: "
                    f"{', '.join(sorted(invalid))}"
                )
            preceding.add(stage.stage_id)

    def stage(self, stage_id: str) -> QualificationStage:
        for stage in self.stages:
            if stage.stage_id == stage_id:
                return stage
        raise KeyError(f"Palier inconnu: {stage_id}")

    def matches(self, device: Any) -> bool:
        driver = _device_value(device, "driver_id", "hardware_driver_id")
        model = _device_value(device, "model", "hardware_model")
        driver_match = not self.driver_ids or driver.casefold() in {
            item.casefold() for item in self.driver_ids
        }
        model_match = not self.model_names or model.casefold() in {
            item.casefold() for item in self.model_names
        }
        return driver_match and model_match


class QualificationProtocolRegistry:
    """Registre extensible des protocoles, distinct du registre des pilotes."""

    def __init__(self) -> None:
        self._protocols: list[HardwareQualificationProtocol] = []

    def register(self, protocol: HardwareQualificationProtocol) -> None:
        if any(item.protocol_id == protocol.protocol_id for item in self._protocols):
            raise ValueError(f"Protocole déjà enregistré: {protocol.protocol_id}")
        self._protocols.append(protocol)

    def resolve(self, device: Any) -> HardwareQualificationProtocol:
        for protocol in self._protocols:
            if (protocol.driver_ids or protocol.model_names) and protocol.matches(device):
                return protocol
        for protocol in self._protocols:
            if not protocol.driver_ids and not protocol.model_names:
                return protocol
        raise LookupError("Aucun protocole de qualification compatible")

    @property
    def protocols(self) -> tuple[HardwareQualificationProtocol, ...]:
        return tuple(self._protocols)


@dataclass(frozen=True)
class QualificationHistoryEntry:
    report_path: Path
    qualification_id: str
    protocol_id: str
    protocol_stage: str
    profile_name: str
    verdict: str
    evaluated_at_utc: str
    device_identity: str
    source_master_file: str
    source_sha256: str
    checks_passed: int
    checks_total: int

    @classmethod
    def from_payload(cls, path: Path, payload: dict[str, Any]) -> QualificationHistoryEntry:
        criteria = payload.get("criteria") or {}
        device = payload.get("device") or {}
        summary = payload.get("summary") or {}
        qualification_id = str(payload.get("qualification_id", "")).strip()
        if not qualification_id:
            raise ValueError("qualification_id absent")
        return cls(
            report_path=path,
            qualification_id=qualification_id,
            protocol_id=str(criteria.get("protocol_id", "")),
            protocol_stage=str(criteria.get("protocol_stage", "")),
            profile_name=str(payload.get("profile_name", "")),
            verdict=str(payload.get("verdict", "unknown")),
            evaluated_at_utc=str(payload.get("evaluated_at_utc", "")),
            device_identity=device_identity(device),
            source_master_file=str(payload.get("source_master_file", "")),
            source_sha256=str(payload.get("source_sha256", "")),
            checks_passed=int(summary.get("checks_passed", 0)),
            checks_total=int(summary.get("checks_total", 0)),
        )


@dataclass(frozen=True)
class QualificationHistoryScan:
    entries: tuple[QualificationHistoryEntry, ...]
    errors: tuple[str, ...]


class QualificationHistoryStore:
    """Relit les rapports JSON autonomes sans inventer de résultat manquant."""

    def scan(self, directory: str | Path) -> QualificationHistoryScan:
        root = Path(directory).expanduser().resolve()
        if not root.is_dir():
            return QualificationHistoryScan((), ())
        entries: list[QualificationHistoryEntry] = []
        errors: list[str] = []
        for path in sorted(root.glob("*_qualification.json")):
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
                if not isinstance(payload, dict):
                    raise ValueError("contenu JSON non objet")
                entries.append(QualificationHistoryEntry.from_payload(path, payload))
            except (OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
                errors.append(f"{path.name}: {exc}")
        entries.sort(key=lambda item: item.evaluated_at_utc, reverse=True)
        return QualificationHistoryScan(tuple(entries), tuple(errors))

    @staticmethod
    def accepted_stage_ids(
        entries: Iterable[QualificationHistoryEntry],
        protocol: HardwareQualificationProtocol,
        device: Any,
    ) -> frozenset[str]:
        identity = device_identity(device)
        known_stage_ids = {stage.stage_id for stage in protocol.stages}
        return frozenset(
            entry.protocol_stage
            for entry in entries
            if entry.protocol_id == protocol.protocol_id
            and entry.device_identity == identity
            and entry.verdict == "accepted"
            and entry.protocol_stage in known_stage_ids
        )

    @staticmethod
    def is_stage_unlocked(
        stage: QualificationStage,
        accepted_stage_ids: Iterable[str],
    ) -> bool:
        return set(stage.prerequisites) <= set(accepted_stage_ids)


def device_identity(device: Any) -> str:
    serial = _device_value(device, "serial_number", "hardware_serial_number")
    driver = _device_value(device, "driver_id", "hardware_driver_id")
    device_id = _device_value(device, "device_id", "hardware_device_id")
    model = _device_value(device, "model", "hardware_model")
    return "|".join((driver, model, serial or device_id))


def _device_value(device: Any, attribute: str, mapping_key: str) -> str:
    if isinstance(device, dict):
        return str(device.get(mapping_key, device.get(attribute, "")) or "").strip()
    return str(getattr(device, attribute, "") or "").strip()


def build_default_qualification_protocol_registry() -> QualificationProtocolRegistry:
    registry = QualificationProtocolRegistry()
    registry.register(MCC_USB1608FS_PROTOCOL)
    registry.register(GENERIC_DAQ_PROTOCOL)
    return registry


_COMMON_CHECKLIST = (
    "Le câble USB, l'alimentation et le support disque sont stables.",
    "Les voies sélectionnées et leurs plages ont été contrôlées.",
    "Les entrées inutilisées sont raccordées conformément au manuel du matériel.",
)
_GROUNDED_CHECKLIST = _COMMON_CHECKLIST + (
    "Les entrées mesurées sont reliées à la masse analogique, sans capteur de campagne.",
)

MCC_USB1608FS_PROTOCOL = HardwareQualificationProtocol(
    protocol_id="mcc_usb1608fs_q0_q4_v1",
    name="MCC USB-1608FS · Q0 à Q4",
    description="Qualification progressive de la carte, du pilote, du PC et du stockage.",
    driver_ids=("mcc.universal_library.usb1608fs",),
    model_names=("USB-1608FS",),
    stages=(
        QualificationStage(
            "Q0",
            "Essai fonctionnel court",
            "Une voie pendant 3 secondes pour vérifier la chaîne minimale.",
            "quick_functional",
            3.0,
            1,
            required_sample_rate_hz=100.0,
            checklist=_COMMON_CHECKLIST,
        ),
        QualificationStage(
            "Q1",
            "Bruit d'une voie à la masse",
            "Une voie reliée à AGND pendant 60 secondes.",
            "grounded_inputs",
            60.0,
            1,
            required_sample_rate_hz=100.0,
            prerequisites=("Q0",),
            checklist=_GROUNDED_CHECKLIST,
        ),
        QualificationStage(
            "Q2",
            "Deux voies et plages mixtes",
            "Deux voies à AGND utilisant deux plages électriques distinctes.",
            "grounded_inputs",
            60.0,
            2,
            minimum_distinct_ranges=2,
            required_sample_rate_hz=100.0,
            prerequisites=("Q1",),
            checklist=_GROUNDED_CHECKLIST,
        ),
        QualificationStage(
            "Q3",
            "Huit voies · endurance intermédiaire",
            "Les huit voies à AGND pendant 10 minutes.",
            "grounded_inputs",
            600.0,
            8,
            required_sample_rate_hz=100.0,
            prerequisites=("Q2",),
            checklist=_GROUNDED_CHECKLIST,
        ),
        QualificationStage(
            "Q4",
            "Huit voies · endurance laboratoire",
            "Les huit voies pendant 60 minutes à la fréquence opérationnelle.",
            "quick_functional",
            3600.0,
            8,
            prerequisites=("Q3",),
            checklist=_COMMON_CHECKLIST,
        ),
    ),
)

GENERIC_DAQ_PROTOCOL = HardwareQualificationProtocol(
    protocol_id="generic_physical_daq_v1",
    name="DAQ physique · contrôle générique",
    description="Contrôle minimal pour un pilote sans protocole constructeur enregistré.",
    stages=(
        QualificationStage(
            "D0",
            "Essai fonctionnel générique",
            "Contrôle court d'une voie; ne vaut pas qualification constructeur.",
            "quick_functional",
            3.0,
            1,
            checklist=_COMMON_CHECKLIST,
        ),
    ),
)
