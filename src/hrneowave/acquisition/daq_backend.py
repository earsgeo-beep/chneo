"""Contrat d'acquisition réservé aux équipements physiques.

Les fichiers existants sont relus par le post-traitement, jamais injectés dans
le contrôleur comme une fausse carte. Il n'existe volontairement aucun backend
de simulation dans ce module de production.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Any

import numpy as np

from hrneowave.core.session_schema import DATA_KIND_RAW
from hrneowave.hardware.contracts import DeviceDescriptor, VoltageRange

logger = logging.getLogger(__name__)

HARDWARE_AVAILABLE_UNVALIDATED = "hardware_available_unvalidated"


@dataclass
class DaqReadResult:
    """Bloc de tensions brutes retourné par un pilote physique."""

    raw_data: np.ndarray
    time: np.ndarray
    sample_rate_hz: float
    backend_name: str
    data_kind: str = DATA_KIND_RAW
    hardware_validation_status: str = HARDWARE_AVAILABLE_UNVALIDATED
    warnings: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.raw_data = np.asarray(self.raw_data, dtype=float)
        self.time = np.asarray(self.time, dtype=float)
        if self.raw_data.ndim != 2:
            raise ValueError("DAQ data must use shape [samples, channels]")
        if self.time.ndim != 1:
            raise ValueError("DAQ time axis must be one-dimensional")
        if self.raw_data.shape[0] != self.time.shape[0]:
            raise ValueError("DAQ time axis length does not match sample count")
        if self.sample_rate_hz <= 0:
            raise ValueError("DAQ sample_rate_hz must be positive")
        if not np.all(np.isfinite(self.raw_data)):
            raise ValueError("DAQ raw data contains NaN/Inf")
        if not np.all(np.isfinite(self.time)):
            raise ValueError("DAQ time axis contains NaN/Inf")
        if self.time.size > 1 and not np.all(np.diff(self.time) > 0.0):
            raise ValueError("DAQ time axis must be strictly monotonic")


class DaqBackend(ABC):
    """Interface commune de tout pilote matériel autorisé à acquérir."""

    name = "hardware_daq"
    is_hardware = True
    realtime = True
    hardware_validation_status = HARDWARE_AVAILABLE_UNVALIDATED

    def __init__(self, descriptor: DeviceDescriptor) -> None:
        self.descriptor = descriptor
        self.channels: list[Any] = []
        self.sample_rate_hz: float | None = None
        self.connected = False
        self.started = False

    @property
    def capabilities(self):
        return self.descriptor.capabilities

    def configure_channels(self, channels: Sequence[Any]) -> None:
        self.channels = list(channels)

    @abstractmethod
    def connect(self) -> None:
        """Ouvre et valide la communication avec l'équipement."""

    @abstractmethod
    def start(
        self,
        sample_rate_hz: float,
        channels: Sequence[Any],
        chunk_size: int = 100,
    ) -> float:
        """Démarre l'acquisition et retourne la fréquence réellement appliquée."""

    @abstractmethod
    def read(self, num_samples: int = 100) -> DaqReadResult | None:
        """Retourne le prochain bloc de tensions brutes."""

    @abstractmethod
    def status(self) -> dict[str, Any]:
        """Retourne un diagnostic matériel sans fabriquer d'état nominal."""

    def stop(self) -> None:
        self.started = False

    def close(self) -> None:
        self.stop()
        self.connected = False

    def metadata(self) -> dict[str, Any]:
        return {
            "backend_name": self.name,
            "backend_is_hardware": True,
            "hardware_validation_status": self.hardware_validation_status,
            "sample_rate_hz": self.sample_rate_hz,
            **self.descriptor.to_metadata(),
        }


def detect_voltage_saturation(
    raw_data: np.ndarray,
    channels: Sequence[Any],
    threshold: float = 0.999,
) -> list[str]:
    """Signale les voies proches de la plage électrique configurée."""

    data = np.asarray(raw_data, dtype=float)
    if data.ndim != 2:
        raise ValueError("raw_data must use shape [samples, channels]")

    warnings: list[str] = []
    for index, channel in enumerate(channels):
        if index >= data.shape[1]:
            break
        voltage_range = getattr(channel, "voltage_range", None)
        if not isinstance(voltage_range, VoltageRange):
            continue
        limit = voltage_range.maximum
        max_abs = float(np.max(np.abs(data[:, index]))) if data.shape[0] else 0.0
        if max_abs >= limit * threshold:
            channel_number = getattr(channel, "channel", index)
            warnings.append(
                "VOLTAGE_SATURATION_RISK: "
                f"channel={channel_number}, max_abs={max_abs:.6g} V, "
                f"range=+-{limit:g} V"
            )
    return warnings
