import json
import tempfile
import unittest
from pathlib import Path

import numpy as np

from hrneowave.acquisition.acquisition_controller import AcquisitionController, create_default_maritime_config
from hrneowave.acquisition.daq_backend import (
    FileReplayBackend,
    SimulatedDaqBackend,
    detect_voltage_saturation,
)


class DaqBackendP1Tests(unittest.TestCase):
    def test_simulated_backend_returns_raw_voltage_matrix_with_monotonic_time(self):
        configs = create_default_maritime_config()
        channels = [configs[0], configs[2]]
        backend = SimulatedDaqBackend(seed=42)

        actual_rate = backend.start(sample_rate_hz=50.0, channels=channels, chunk_size=8)
        result = backend.read(num_samples=8)

        self.assertEqual(actual_rate, 50.0)
        self.assertEqual(result.raw_data.shape, (8, 2))
        self.assertEqual(result.time.shape, (8,))
        self.assertTrue(np.all(np.diff(result.time) > 0.0))
        self.assertTrue(np.allclose(np.diff(result.time), 1.0 / 50.0))
        self.assertEqual(result.hardware_validation_status, "pending_hardware")
        self.assertFalse(np.any(np.abs(result.raw_data[:, 1]) > 5.0))

    def test_voltage_saturation_detection_uses_channel_ranges(self):
        configs = create_default_maritime_config()
        pressure = configs[2]
        raw_data = np.array([[0.0], [4.999], [-1.0]], dtype=float)

        warnings = detect_voltage_saturation(raw_data, [pressure])

        self.assertTrue(warnings)
        self.assertIn("VOLTAGE_SATURATION_RISK", warnings[0])

    def test_file_replay_backend_preserves_raw_channels_and_time_axis(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "replay.json"
            payload = {
                "metadata": {
                    "schema_version": "1.0.0",
                    "sample_rate_hz": 50.0,
                    "clock_domain": "relative_monotonic_seconds",
                },
                "time": [0.0, 0.02, 0.04, 0.06],
                "channels": {
                    "channel_00": [0.0, 0.5, 1.0, 0.5],
                    "channel_01": [1.0, 1.5, 2.0, 1.5],
                },
                "raw_channels": {
                    "channel_00": [0.0, 0.1, 0.2, 0.1],
                    "channel_01": [0.0, 0.2, 0.4, 0.2],
                },
            }
            path.write_text(json.dumps(payload), encoding="utf-8")

            backend = FileReplayBackend(str(path))
            actual_rate = backend.start(sample_rate_hz=50.0, channels=[], chunk_size=2)
            first = backend.read(num_samples=2)
            second = backend.read(num_samples=2)
            exhausted = backend.read(num_samples=2)

            self.assertEqual(actual_rate, 50.0)
            self.assertTrue(np.allclose(first.raw_data[:, 0], [0.0, 0.1]))
            self.assertTrue(np.allclose(second.raw_data[:, 1], [0.4, 0.2]))
            self.assertTrue(np.allclose(second.time, [0.04, 0.06]))
            self.assertIsNone(exhausted)

    def test_file_replay_rejects_sample_rate_mismatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad_rate.json"
            payload = {
                "metadata": {"sample_rate_hz": 50.0},
                "time": [0.0, 0.02, 0.04],
                "channels": {"channel_00": [0.0, 1.0, 0.0]},
            }
            path.write_text(json.dumps(payload), encoding="utf-8")

            backend = FileReplayBackend(str(path))
            with self.assertRaises(ValueError):
                backend.start(sample_rate_hz=100.0, channels=[])

    def test_acquisition_controller_accepts_injected_simulated_backend(self):
        backend = SimulatedDaqBackend(seed=7, realtime=False)
        controller = AcquisitionController(daq_backend=backend)
        controller.channels_config = {0: create_default_maritime_config()[0]}

        self.assertTrue(
            controller.start_acquisition_session(
                "backend_p1",
                sampling_rate=100.0,
                duration_seconds=0.001,
                channels=[0],
            )
        )
        controller.acquisition_thread.join(timeout=2.0)

        self.assertFalse(controller.is_acquiring)
        self.assertGreater(controller.stats["samples_acquired"], 0)
        self.assertTrue(controller.data_buffer)
        self.assertEqual(controller.current_session.metadata["backend_name"], "simulated")
        self.assertEqual(
            controller.current_session.metadata["hardware_validation_status"],
            "pending_hardware",
        )
        self.assertFalse(controller.is_hardware_available())


if __name__ == "__main__":
    unittest.main()
