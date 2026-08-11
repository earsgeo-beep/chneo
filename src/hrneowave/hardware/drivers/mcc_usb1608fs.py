"""Plugin matériel MCC USB-1608FS pour le registre CHNeoWave."""

from __future__ import annotations

from hrneowave.acquisition.mcc_daq_wrapper import (
    MccUsbDeviceInfo,
    scan_available_devices,
)

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

    def __init__(self, scanner=scan_available_devices, backend_factory=MccDaqBackend) -> None:
        self._scanner = scanner
        self._backend_factory = backend_factory

    def discover(self) -> list[DeviceDescriptor]:
        devices: list[DeviceDescriptor] = []
        for detected in self._scanner():
            if isinstance(detected, MccUsbDeviceInfo):
                board_num = detected.board_num
                serial_number = detected.unique_id or None
                product_name = detected.product_name
            else:
                # Compatibilité avec les scanners injectés par les tests et
                # les intégrations historiques qui retournaient un entier.
                board_num = int(detected)
                serial_number = None
                product_name = "USB-1608FS"
            devices.append(
                DeviceDescriptor(
                    driver_id=self.driver_id,
                    device_id=str(board_num),
                    vendor="Measurement Computing",
                    model="USB-1608FS",
                    display_name=f"MCC USB-1608FS · carte {board_num}",
                    capabilities=self.CAPABILITIES,
                    serial_number=serial_number,
                    transport="USB",
                    metadata={
                        "board_num": int(board_num),
                        "discovery": "direct_usb",
                        "usb_product_name": product_name,
                    },
                )
            )
        return devices

    def open(self, device: DeviceDescriptor) -> MccDaqBackend:
        if device.driver_id != self.driver_id:
            raise DeviceNotFoundError(f"Périphérique incompatible: {device.key}")
        board_num = int(device.metadata.get("board_num", device.device_id))
        backend = self._backend_factory(
            board_num=board_num,
            descriptor=device,
        )
        backend.connect()
        return backend
