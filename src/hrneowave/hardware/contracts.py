"""Contrats matériels communs à tous les systèmes d'acquisition CHNeoWave.

Le noyau scientifique ne doit connaître ni MCC, ni IOtech, ni Keithley. Un
pilote traduit les capacités de son équipement vers ces structures génériques.
Seuls des équipements physiques peuvent être publiés dans le registre.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from hrneowave.acquisition.daq_backend import DaqBackend


class HardwareError(RuntimeError):
    """Erreur matérielle exploitable par l'interface opérateur."""


class DriverNotFoundError(HardwareError):
    """Le pilote demandé n'est pas enregistré dans l'application."""


class DeviceNotFoundError(HardwareError):
    """Le périphérique demandé n'est plus présent ou n'est plus accessible."""


class VoltageRange(Enum):
    """Plages bipolaires génériques exprimées par leur valeur absolue."""

    BIPOLAR_1_V = 1.0
    BIPOLAR_2_V = 2.0
    BIPOLAR_5_V = 5.0
    BIPOLAR_10_V = 10.0

    @property
    def minimum(self) -> float:
        return -float(self.value)

    @property
    def maximum(self) -> float:
        return float(self.value)

    @property
    def label(self) -> str:
        return f"±{self.value:g} V"

    @classmethod
    def from_limit(cls, limit_volts: float) -> VoltageRange:
        normalized = float(limit_volts)
        for item in cls:
            if item.value == normalized:
                return item
        raise ValueError(f"Plage bipolaire non prise en charge: ±{normalized:g} V")


@dataclass(frozen=True)
class AcquisitionCapabilities:
    """Capacités nécessaires pour construire une configuration valide."""

    analog_input_channels: int
    voltage_ranges: tuple[VoltageRange, ...]
    min_sample_rate_hz: float
    max_sample_rate_hz_per_channel: float
    max_aggregate_sample_rate_hz: float | None = None
    supports_continuous: bool = True
    supports_external_trigger: bool = False
    supports_external_clock: bool = False
    supports_differential_inputs: bool = False

    def __post_init__(self) -> None:
        if self.analog_input_channels <= 0:
            raise ValueError("Le nombre de voies analogiques doit être positif")
        if not self.voltage_ranges:
            raise ValueError("Au moins une plage de tension doit être déclarée")
        if self.min_sample_rate_hz <= 0:
            raise ValueError("La fréquence minimale doit être positive")
        if self.max_sample_rate_hz_per_channel < self.min_sample_rate_hz:
            raise ValueError("La fréquence maximale est inférieure à la fréquence minimale")

    def validate(self, sample_rate_hz: float, channel_count: int) -> None:
        rate = float(sample_rate_hz)
        if channel_count <= 0 or channel_count > self.analog_input_channels:
            raise ValueError(
                f"Nombre de canaux invalide: {channel_count}/{self.analog_input_channels}"
            )
        if not self.min_sample_rate_hz <= rate <= self.max_sample_rate_hz_per_channel:
            raise ValueError(
                "Fréquence hors capacités du matériel: "
                f"{rate:g} Hz, plage {self.min_sample_rate_hz:g}–"
                f"{self.max_sample_rate_hz_per_channel:g} Hz"
            )
        if (
            self.max_aggregate_sample_rate_hz is not None
            and rate * channel_count > self.max_aggregate_sample_rate_hz
        ):
            raise ValueError(
                "Débit agrégé trop élevé: "
                f"{rate * channel_count:g} S/s > {self.max_aggregate_sample_rate_hz:g} S/s"
            )


@dataclass(frozen=True)
class DeviceDescriptor:
    """Identité stable d'un équipement découvert par un pilote."""

    driver_id: str
    device_id: str
    vendor: str
    model: str
    display_name: str
    capabilities: AcquisitionCapabilities
    serial_number: str | None = None
    transport: str = "unknown"
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def key(self) -> str:
        return f"{self.driver_id}:{self.device_id}"

    def to_metadata(self) -> dict[str, Any]:
        return {
            "hardware_driver_id": self.driver_id,
            "hardware_device_id": self.device_id,
            "hardware_vendor": self.vendor,
            "hardware_model": self.model,
            "hardware_serial_number": self.serial_number or "",
            "hardware_transport": self.transport,
            "hardware_display_name": self.display_name,
        }


class HardwareDriverProvider(ABC):
    """Point d'extension d'un constructeur de cartes d'acquisition."""

    driver_id: str
    display_name: str

    @abstractmethod
    def discover(self) -> list[DeviceDescriptor]:
        """Retourne uniquement les équipements physiques actuellement présents."""

    @abstractmethod
    def open(self, device: DeviceDescriptor) -> DaqBackend:
        """Ouvre et valide l'équipement avant de retourner son backend."""

