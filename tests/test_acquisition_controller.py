from __future__ import annotations

import csv
import tempfile
import time
import unittest
from pathlib import Path

from hrneowave.acquisition.acquisition_controller import AcquisitionController
from hrneowave.core.post_processor import PostProcessor


class FakeRecorder:
    def __init__(self):
        self.path = None
        self.samples = 0
        self.finalized = False
        self.closed = False

    def start(self, path, session):
        self.path = Path(path).resolve()
        return self.path

    def append(self, raw_data, processed_data):
        if raw_data.shape != processed_data.shape:
            raise AssertionError("Les formes brut/physique doivent correspondre")
        self.samples += raw_data.shape[0]

    def finalize(self, session, statistics):
        self.finalized = True
        self.final_samples = session.total_samples

    def close(self):
        self.closed = True


class AcquisitionControllerTests(unittest.TestCase):
    def setUp(self):
        self.controller = AcquisitionController(board_scanner=lambda: [])
        self.assertTrue(
            self.controller.configure_maritime_channel(
                0,
                "wave_height",
                "Sonde de houle",
                range_volts=10.0,
                sensor_sensitivity=2.0,
                physical_units="m",
            )
        )

    def tearDown(self):
        self.controller.close()

    def test_rejects_zero_sensitivity(self):
        self.assertFalse(
            self.controller.configure_maritime_channel(
                1,
                "generic",
                "Invalide",
                sensor_sensitivity=0.0,
            )
        )

    def test_hardware_scan_can_be_deferred_until_operator_request(self):
        calls = []
        controller = AcquisitionController(
            board_scanner=lambda: calls.append("scan") or [],
            auto_initialize=False,
        )
        try:
            self.assertEqual(calls, [])
            self.assertEqual(controller.get_available_boards(), [])
            self.assertFalse(controller.refresh_hardware())
            self.assertEqual(calls, ["scan"])
        finally:
            controller.close()

    def test_simulation_respects_configured_rate(self):
        started = time.monotonic()
        self.assertTrue(
            self.controller.start_acquisition_session(
                "timing",
                sampling_rate=1000,
                duration_seconds=0.25,
                channels=[0],
            )
        )
        self.controller.acquisition_thread.join(timeout=2)
        elapsed = time.monotonic() - started
        samples = self.controller.stats["samples_acquired"]

        self.assertFalse(self.controller.is_acquiring)
        self.assertLess(elapsed, 1.0)
        self.assertEqual(samples, 250)

    def test_csv_preserves_sample_rate_for_analysis(self):
        self.assertTrue(
            self.controller.start_acquisition_session(
                "csv",
                sampling_rate=500,
                duration_seconds=0.12,
                channels=[0],
            )
        )
        self.controller.acquisition_thread.join(timeout=2)

        with tempfile.TemporaryDirectory() as directory:
            csv_path = Path(directory) / "session.csv"
            self.assertTrue(self.controller.export_session_data(str(csv_path), "csv"))

            with csv_path.open(newline="", encoding="utf-8") as handle:
                header = next(csv.reader(handle))
            self.assertEqual(header[:2], ["time", "sample_rate"])

            processor = PostProcessor()
            self.assertTrue(processor.load_data_file(str(csv_path)))
            self.assertEqual(processor.sample_rate, 500.0)

    def test_new_session_resets_previous_samples(self):
        self.assertTrue(
            self.controller.start_acquisition_session(
                "first", sampling_rate=500, duration_seconds=0.12, channels=[0]
            )
        )
        self.controller.acquisition_thread.join(timeout=2)
        first_count = self.controller.stats["samples_acquired"]
        self.assertGreater(first_count, 0)

        self.assertTrue(
            self.controller.start_acquisition_session(
                "second", sampling_rate=500, duration_seconds=0.12, channels=[0]
            )
        )
        self.controller.acquisition_thread.join(timeout=2)
        second_count = self.controller.stats["samples_acquired"]
        self.assertLessEqual(second_count, 200)

    def test_continuous_recorder_receives_every_acquired_sample(self):
        recorder = FakeRecorder()
        controller = AcquisitionController(
            board_scanner=lambda: [], recorder_factory=lambda: recorder
        )
        try:
            self.assertTrue(
                controller.configure_maritime_channel(
                    0,
                    "wave_height",
                    "Sonde enregistree",
                    sensor_sensitivity=2.0,
                )
            )
            with tempfile.TemporaryDirectory() as directory:
                self.assertTrue(
                    controller.start_acquisition_session(
                        "recording",
                        sampling_rate=500,
                        duration_seconds=0.12,
                        channels=[0],
                        recording_directory=directory,
                    )
                )
                controller.acquisition_thread.join(timeout=2)

                self.assertTrue(recorder.finalized)
                self.assertEqual(recorder.samples, controller.stats["samples_acquired"])
                self.assertEqual(recorder.final_samples, recorder.samples)
                self.assertEqual(
                    Path(controller.current_session.data_file_path).parent,
                    Path(directory).resolve(),
                )
        finally:
            controller.close()


if __name__ == "__main__":
    unittest.main()
