"""Registre des pilotes matériels physiques CHNeoWave."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from .contracts import (
    DeviceDescriptor,
    DeviceNotFoundError,
    DriverNotFoundError,
    HardwareDriverProvider,
)

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DiscoveryReport:
    """Résultat complet d'un inventaire multi-pilotes."""

    devices: tuple[DeviceDescriptor, ...]
    driver_errors: dict[str, str] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return bool(self.devices) and not self.driver_errors


class HardwareRegistry:
    """Registre extensible sans fallback de démonstration."""

    def __init__(self) -> None:
        self._providers: dict[str, HardwareDriverProvider] = {}
        self._last_report = DiscoveryReport(devices=())

    def register(self, provider: HardwareDriverProvider) -> None:
        driver_id = str(provider.driver_id).strip()
        if not driver_id:
            raise ValueError("Un pilote doit déclarer un identifiant")
        if driver_id in self._providers:
            raise ValueError(f"Pilote déjà enregistré: {driver_id}")
        self._providers[driver_id] = provider

    def registered_drivers(self) -> tuple[str, ...]:
        return tuple(self._providers)

    def discover(self) -> DiscoveryReport:
        devices: list[DeviceDescriptor] = []
        errors: dict[str, str] = {}
        seen_keys: set[str] = set()

        for driver_id, provider in self._providers.items():
            try:
                discovered = provider.discover()
                for device in discovered:
                    if device.driver_id != driver_id:
                        raise ValueError(
                            f"Le pilote {driver_id} a publié un périphérique pour {device.driver_id}"
                        )
                    if device.key in seen_keys:
                        raise ValueError(f"Identifiant matériel dupliqué: {device.key}")
                    seen_keys.add(device.key)
                    devices.append(device)
            except Exception as exc:
                errors[driver_id] = str(exc)
                logger.exception("Échec de détection du pilote %s", driver_id)

        self._last_report = DiscoveryReport(tuple(devices), errors)
        return self._last_report

    def open_device(self, device_key: str):
        device = next(
            (item for item in self._last_report.devices if item.key == device_key),
            None,
        )
        if device is None:
            raise DeviceNotFoundError(
                f"Périphérique non présent dans le dernier inventaire: {device_key}"
            )
        provider = self._providers.get(device.driver_id)
        if provider is None:
            raise DriverNotFoundError(f"Pilote non enregistré: {device.driver_id}")
        backend = provider.open(device)
        if not bool(getattr(backend, "is_hardware", False)):
            raise TypeError(
                f"Le pilote {device.driver_id} a retourné une source non matérielle"
            )
        return backend


def build_default_hardware_registry() -> HardwareRegistry:
    """Construit le registre de production avec les pilotes réellement livrés."""

    from .drivers.mcc_usb1608fs import MccUsb1608FsProvider

    registry = HardwareRegistry()
    registry.register(MccUsb1608FsProvider())
    return registry

