"""Plugin matériel MCC USB-1608FS pour le registre CHNeoWave."""

from __future__ import annotations

from hrneowave.acquisition.mcc_daq_wrapper import scan_available_boards

from ..contracts import (
    AcquisitionCapabilities,
    DeviceDescriptor,
    DeviceNotFoundError,
    HardwareDriverProvider,
    VoltageRange,
)
from .mcc_backend import MccDaqBackend


class MccUsb1608FsProvider(HardwareDriverProvider):
    """Découvre la carte par Universal Library, sans dépendre de ``cb.cfg``."""

    driver_id = "mcc.universal_library.usb1608fs"
    display_name = "MCC Universal Library"

    CAPABILITIES = AcquisitionCapabilities(
        analog_input_channels=8,
        voltage_ranges=(
            VoltageRange.BIPOLAR_1_V,
            VoltageRange.BIPOLAR_2_V,
            VoltageRange.BIPOLAR_5_V,
            VoltageRange.BIPOLAR_10_V,
        ),
        min_sample_rate_hz=1.0,
        max_sample_rate_hz_per_channel=12_500.0,
        max_aggregate_sample_rate_hz=100_000.0,
        supports_continuous=True,
        supports_external_trigger=False,
        supports_external_clock=False,
        supports_differential_inputs=False,
    )

    def __init__(self, scanner=scan_available_boards, backend_factory=MccDaqBackend) -> None:
        self._scanner = scanner
        self._backend_factory = backend_factory

    def discover(self) -> list[DeviceDescriptor]:
        return [
            DeviceDescriptor(
                driver_id=self.driver_id,
                device_id=str(board_num),
                vendor="Measurement Computing",
                model="USB-1608FS",
                display_name=f"MCC USB-1608FS · carte {board_num}",
                capabilities=self.CAPABILITIES,
                transport="USB",
                metadata={"board_num": int(board_num), "discovery": "direct_usb"},
            )
            for board_num in self._scanner()
        ]

    def open(self, device: DeviceDescriptor) -> MccDaqBackend:
        if device.driver_id != self.driver_id:
            raise DeviceNotFoundError(f"Périphérique incompatible: {device.key}")
        backend = self._backend_factory(
            board_num=int(device.device_id),
            descriptor=device,
        )
        backend.connect()
        return backend
