"""Doubles de test strictement réservés aux tests du contrat matériel."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import numpy as np

from hrneowave.acquisition.daq_backend import DaqBackend, DaqReadResult
from hrneowave.hardware import (
    AcquisitionCapabilities,
    DeviceDescriptor,
    HardwareDriverProvider,
    VoltageRange,
)


def physical_test_device(channel_count: int = 8) -> DeviceDescriptor:
    return DeviceDescriptor(
        driver_id="test.physical.driver",
        device_id="bench-001",
        vendor="Test Laboratory",
        model="Deterministic DAQ",
        display_name="Test Laboratory Deterministic DAQ",
        capabilities=AcquisitionCapabilities(
            analog_input_channels=channel_count,
            voltage_ranges=(
                VoltageRange.BIPOLAR_1_V,
                VoltageRange.BIPOLAR_2_V,
                VoltageRange.BIPOLAR_5_V,
                VoltageRange.BIPOLAR_10_V,
            ),
            min_sample_rate_hz=1.0,
            max_sample_rate_hz_per_channel=20_000.0,
            max_aggregate_sample_rate_hz=100_000.0,
        ),
        serial_number="TEST-001",
        transport="test-fixture",
    )


class DeterministicPhysicalBackend(DaqBackend):
    """Backend de banc déterministe; il n'est jamais importé par la production."""

    name = "deterministic_physical_test_backend"
    hardware_validation_status = "test_fixture_validated"

    def __init__(self, descriptor: DeviceDescriptor | None = None) -> None:
        super().__init__(descriptor or physical_test_device())
        self._sample_index = 0

    def connect(self) -> None:
        self.connected = True

    def start(
        self,
        sample_rate_hz: float,
        channels: Sequence[Any],
        chunk_size: int = 100,
    ) -> float:
        if not self.connected:
            raise RuntimeError("Le banc de test doit être connecté")
        self.configure_channels(channels)
        self.capabilities.validate(sample_rate_hz, len(self.channels))
        self.sample_rate_hz = float(sample_rate_hz)
        self._sample_index = 0
        self.started = True
        return self.sample_rate_hz

    def read(self, num_samples: int = 100) -> DaqReadResult:
        if not self.started or self.sample_rate_hz is None:
            raise RuntimeError("Le banc de test n'est pas démarré")
        indices = self._sample_index + np.arange(int(num_samples), dtype=float)
        time_values = indices / self.sample_rate_hz
        columns = [0.001 * indices + 0.01 * index for index in range(len(self.channels))]
        raw_data = np.column_stack(columns)
        self._sample_index += int(num_samples)
        return DaqReadResult(
            raw_data=raw_data,
            time=time_values,
            sample_rate_hz=self.sample_rate_hz,
            backend_name=self.name,
            hardware_validation_status=self.hardware_validation_status,
        )

    def status(self) -> dict[str, Any]:
        return {
            "connected": self.connected,
            "is_running": self.started,
            "buffer_overruns": 0,
            "device_key": self.descriptor.key,
        }


class StaticPhysicalProvider(HardwareDriverProvider):
    driver_id = "test.physical.driver"
    display_name = "Test Laboratory Driver"

    def __init__(
        self,
        devices: list[DeviceDescriptor] | None = None,
        calls: list[str] | None = None,
    ) -> None:
        self.devices = devices if devices is not None else [physical_test_device()]
        self.calls = calls if calls is not None else []

    def discover(self) -> list[DeviceDescriptor]:
        self.calls.append("discover")
        return list(self.devices)

    def open(self, device: DeviceDescriptor) -> DaqBackend:
        self.calls.append(f"open:{device.key}")
        backend = DeterministicPhysicalBackend(device)
        backend.connect()
        return backend
