"""Architecture matérielle extensible de CHNeoWave."""

from .contracts import (
    AcquisitionCapabilities,
    DeviceDescriptor,
    DeviceNotFoundError,
    DriverNotFoundError,
    HardwareDriverProvider,
    HardwareError,
    VoltageRange,
)
from .registry import DiscoveryReport, HardwareRegistry, build_default_hardware_registry

__all__ = [
    "AcquisitionCapabilities",
    "DeviceDescriptor",
    "DeviceNotFoundError",
    "DiscoveryReport",
    "DriverNotFoundError",
    "HardwareDriverProvider",
    "HardwareError",
    "HardwareRegistry",
    "VoltageRange",
    "build_default_hardware_registry",
]
