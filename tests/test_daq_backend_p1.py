import unittest

import numpy as np

from hrneowave.acquisition.acquisition_controller import create_default_maritime_config
from hrneowave.acquisition.daq_backend import DaqBackend, DaqReadResult, detect_voltage_saturation
from hrneowave.hardware import HardwareRegistry
from hrneowave.hardware.drivers.mcc_usb1608fs import MccUsb1608FsProvider
from tests.hardware_test_doubles import (
    DeterministicPhysicalBackend,
    StaticPhysicalProvider,
    physical_test_device,
)


class DaqBackendContractTests(unittest.TestCase):
    def test_physical_backend_returns_raw_matrix_with_monotonic_time(self):
        backend = DeterministicPhysicalBackend()
        backend.connect()
        channels = [create_default_maritime_config()[0], create_default_maritime_config()[2]]

        actual_rate = backend.start(sample_rate_hz=50.0, channels=channels, chunk_size=8)
        result = backend.read(num_samples=8)

        self.assertEqual(actual_rate, 50.0)
        self.assertEqual(result.raw_data.shape, (8, 2))
        self.assertEqual(result.time.shape, (8,))
        self.assertTrue(np.all(np.diff(result.time) > 0.0))
        self.assertTrue(np.allclose(np.diff(result.time), 1.0 / 50.0))
        self.assertEqual(result.hardware_validation_status, "test_fixture_validated")

    def test_read_result_rejects_non_monotonic_time(self):
        with self.assertRaises(ValueError, msg="L'axe temporel doit être strictement monotone"):
            DaqReadResult(
                raw_data=np.zeros((3, 1)),
                time=np.array([0.0, 0.02, 0.01]),
                sample_rate_hz=50.0,
                backend_name="invalid",
            )

    def test_voltage_saturation_detection_uses_generic_channel_ranges(self):
        pressure = create_default_maritime_config()[2]
        raw_data = np.array([[0.0], [4.999], [-1.0]], dtype=float)

        warnings = detect_voltage_saturation(raw_data, [pressure])

        self.assertTrue(warnings)
        self.assertIn("VOLTAGE_SATURATION_RISK", warnings[0])

    def test_registry_discovers_and_opens_a_physical_device(self):
        calls: list[str] = []
        registry = HardwareRegistry()
        registry.register(StaticPhysicalProvider(calls=calls))

        report = registry.discover()
        backend = registry.open_device(report.devices[0].key)

        self.assertEqual(report.devices[0], physical_test_device())
        self.assertTrue(backend.connected)
        self.assertEqual(calls, ["discover", f"open:{report.devices[0].key}"])

    def test_mcc_is_an_isolated_driver_with_declared_capabilities(self):
        opened: list[tuple[int, str]] = []

        def backend_factory(board_num, descriptor):
            opened.append((board_num, descriptor.key))
            return DeterministicPhysicalBackend(descriptor)

        provider = MccUsb1608FsProvider(
            scanner=lambda: [2],
            backend_factory=backend_factory,
        )
        device = provider.discover()[0]
        backend = provider.open(device)

        self.assertEqual(device.model, "USB-1608FS")
        self.assertEqual(device.capabilities.analog_input_channels, 8)
        self.assertEqual(device.capabilities.max_sample_rate_hz_per_channel, 12_500.0)
        self.assertEqual(opened, [(2, device.key)])
        self.assertTrue(backend.connected)

    def test_registry_rejects_non_hardware_provider_result(self):
        class ForbiddenSource(DaqBackend):
            is_hardware = False

            def connect(self):
                self.connected = True

            def start(self, sample_rate_hz, channels, chunk_size=100):
                return float(sample_rate_hz)

            def read(self, num_samples=100):
                return None

            def status(self):
                return {}

        class ForbiddenProvider(StaticPhysicalProvider):
            def open(self, device):
                source = ForbiddenSource(device)
                source.connect()
                return source

        registry = HardwareRegistry()
        registry.register(ForbiddenProvider())
        report = registry.discover()

        with self.assertRaises(TypeError):
            registry.open_device(report.devices[0].key)


if __name__ == "__main__":
    unittest.main()
