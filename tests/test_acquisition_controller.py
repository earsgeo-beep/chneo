from __future__ import annotations

import csv
import json
import tempfile
import time
import unittest
from datetime import datetime
from pathlib import Path

import numpy as np

from hrneowave.acquisition.acquisition_controller import AcquisitionController, AcquisitionSession
from hrneowave.acquisition.daq_backend import DaqReadResult
from hrneowave.acquisition.hardware_qualification import QualificationCriteria
from hrneowave.core.post_processor import PostProcessor
from hrneowave.hardware import HardwareRegistry
from tests.hardware_test_doubles import DeterministicPhysicalBackend, StaticPhysicalProvider


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
        self.temporary_directory = tempfile.TemporaryDirectory()
        backend = DeterministicPhysicalBackend()
        backend.connect()
        self.controller = AcquisitionController(daq_backend=backend)
        self.assertTrue(
            self.controller.configure_maritime_channel(
                0,
                "wave_height",
                "Sonde de houle",
                range_volts=10.0,
                sensor_sensitivity=2.0,
                physical_units="m",
                probe_position_m=0.4,
            )
        )

    def tearDown(self):
        self.controller.close()
        self.temporary_directory.cleanup()

    @property
    def recording_directory(self) -> str:
        return self.temporary_directory.name

    def _start(self, project_name: str, **kwargs) -> bool:
        return self.controller.start_acquisition_session(
            project_name,
            recording_directory=self.recording_directory,
            **kwargs,
        )

    def test_rejects_zero_sensitivity(self):
        self.assertFalse(
            self.controller.configure_maritime_channel(
                1,
                "generic",
                "Invalide",
                sensor_sensitivity=0.0,
            )
        )

    def test_rejects_non_finite_scientific_parameters(self):
        self.assertFalse(
            self.controller.configure_maritime_channel(
                1,
                "wave_height",
                "Sonde invalide",
                sensor_sensitivity=float("nan"),
                probe_position_m=0.8,
            )
        )
        self.assertFalse(
            self._start(
                "bad_rate",
                sampling_rate=float("nan"),
                duration_seconds=0.1,
                channels=[0],
            )
        )
        self.assertFalse(
            self._start(
                "bad_duration",
                sampling_rate=100.0,
                duration_seconds=float("inf"),
                channels=[0],
            )
        )

    def test_backend_time_discontinuity_is_counted_and_refused(self):
        self.controller.current_session = AcquisitionSession(
            session_id="timing-check",
            project_name="Timing",
            start_time=datetime.now(),
            sampling_rate=100.0,
            channels=list(self.controller.channels_config.values()),
        )
        first = DaqReadResult(
            raw_data=np.zeros((2, 1)),
            time=np.array([0.0, 0.01]),
            sample_rate_hz=100.0,
            backend_name=self.controller._daq_backend.name,
        )
        discontinuous = DaqReadResult(
            raw_data=np.zeros((2, 1)),
            time=np.array([0.03, 0.04]),
            sample_rate_hz=100.0,
            backend_name=self.controller._daq_backend.name,
        )

        self.controller._validate_backend_timing(first)
        with self.assertRaisesRegex(RuntimeError, "Discontinuité temporelle"):
            self.controller._validate_backend_timing(discontinuous)

        self.assertEqual(self.controller.stats["timing_discontinuities"], 1)

    def test_hardware_scan_can_be_deferred_until_operator_request(self):
        calls: list[str] = []
        registry = HardwareRegistry()
        registry.register(StaticPhysicalProvider(devices=[], calls=calls))
        controller = AcquisitionController(hardware_registry=registry, auto_initialize=False)
        try:
            self.assertEqual(calls, [])
            self.assertEqual(controller.get_available_devices(), [])
            self.assertFalse(controller.refresh_hardware())
            self.assertEqual(calls, ["discover"])
        finally:
            controller.close()

    def test_session_refuses_to_start_without_physical_hardware(self):
        controller = AcquisitionController(auto_initialize=False)
        try:
            controller.channels_config = dict(self.controller.channels_config)
            self.assertFalse(
                controller.start_acquisition_session(
                    "forbidden",
                    sampling_rate=100.0,
                    duration_seconds=0.1,
                    channels=[0],
                    recording_directory=self.recording_directory,
                )
            )
        finally:
            controller.close()

    def test_scientific_geometry_is_stored_in_physical_session_contract(self):
        self.assertEqual(self.controller.get_channel_configuration(0)["probe_position_m"], 0.4)
        self.assertTrue(
            self._start(
                "geometry",
                sampling_rate=100,
                duration_seconds=0.1,
                channels=[0],
                water_depth_m=0.8,
            )
        )
        self.controller.acquisition_thread.join(timeout=2)

        metadata = self.controller.current_session.metadata
        self.assertEqual(metadata["water_depth_m"], 0.8)
        self.assertEqual(metadata["acquisition_source"], "physical_hardware")
        self.assertTrue(metadata["hardware_available"])
        self.assertEqual(self.controller.current_session.channels[0].probe_position_m, 0.4)

    def test_rejects_non_physical_water_depth(self):
        self.assertFalse(
            self._start(
                "bad_depth",
                sampling_rate=100,
                duration_seconds=0.1,
                channels=[0],
                water_depth_m=0.0,
            )
        )

    def test_physical_backend_respects_configured_rate_and_sample_target(self):
        started = time.monotonic()
        self.assertTrue(
            self._start(
                "timing",
                sampling_rate=1000,
                duration_seconds=0.25,
                channels=[0],
            )
        )
        self.controller.acquisition_thread.join(timeout=2)
        elapsed = time.monotonic() - started

        self.assertFalse(self.controller.is_acquiring)
        self.assertLess(elapsed, 1.0)
        self.assertEqual(self.controller.stats["samples_acquired"], 250)

    def test_csv_preserves_sample_rate_and_integrity_for_analysis(self):
        self.assertTrue(
            self._start(
                "csv",
                sampling_rate=500,
                duration_seconds=0.12,
                channels=[0],
            )
        )
        self.controller.acquisition_thread.join(timeout=2)

        csv_path = Path(self.recording_directory) / "session.csv"
        self.assertTrue(self.controller.export_session_data(str(csv_path), "csv"))
        with csv_path.open(newline="", encoding="utf-8") as handle:
            header = next(csv.reader(handle))
        self.assertEqual(header[:2], ["time", "sample_rate"])

        processor = PostProcessor()
        self.assertTrue(processor.load_data_file(str(csv_path)))
        self.assertEqual(processor.sample_rate, 500.0)

    def test_export_uses_complete_master_not_limited_preview(self):
        self.controller.preview_sample_limit = 20
        self.assertTrue(
            self._start(
                "complete_export",
                sampling_rate=1000,
                duration_seconds=0.125,
                channels=[0],
            )
        )
        self.controller.acquisition_thread.join(timeout=2)
        preview_samples = sum(item["sample_count"] for item in self.controller.data_buffer)
        self.assertLessEqual(preview_samples, self.controller.preview_sample_limit)

        json_path = Path(self.recording_directory) / "complete.json"
        self.assertTrue(self.controller.export_session_data(str(json_path), "json"))
        payload = json.loads(json_path.read_text(encoding="utf-8"))
        self.assertEqual(len(payload["time"]), 125)
        self.assertEqual(len(payload["channels"]["channel_00"]), 125)

    def test_new_session_resets_previous_samples(self):
        self.assertTrue(
            self._start("first", sampling_rate=500, duration_seconds=0.12, channels=[0])
        )
        self.controller.acquisition_thread.join(timeout=2)
        self.assertGreater(self.controller.stats["samples_acquired"], 0)

        self.assertTrue(
            self._start("second", sampling_rate=500, duration_seconds=0.12, channels=[0])
        )
        self.controller.acquisition_thread.join(timeout=2)
        self.assertEqual(self.controller.stats["samples_acquired"], 60)

    def test_completed_session_can_be_qualified_from_master_file(self):
        self.assertTrue(
            self._start(
                "qualification",
                sampling_rate=100,
                duration_seconds=1.0,
                channels=[0],
            )
        )
        self.controller.acquisition_thread.join(timeout=2)

        report = self.controller.qualify_current_session(
            QualificationCriteria.quick_functional(
                minimum_duration_seconds=1.0,
                check_wall_clock=False,
            )
        )

        self.assertTrue(report.accepted)
        self.assertIsNotNone(self.controller.last_qualification_files)
        for path in self.controller.last_qualification_files:
            self.assertTrue(Path(path).is_file())

    def test_continuous_recorder_receives_every_acquired_sample(self):
        recorder = FakeRecorder()
        backend = DeterministicPhysicalBackend()
        backend.connect()
        controller = AcquisitionController(
            daq_backend=backend,
            recorder_factory=lambda: recorder,
        )
        try:
            self.assertTrue(
                controller.configure_maritime_channel(
                    0,
                    "wave_height",
                    "Sonde enregistrée",
                    sensor_sensitivity=2.0,
                )
            )
            self.assertTrue(
                controller.start_acquisition_session(
                    "recording",
                    sampling_rate=500,
                    duration_seconds=0.12,
                    channels=[0],
                    recording_directory=self.recording_directory,
                )
            )
            controller.acquisition_thread.join(timeout=2)

            self.assertTrue(recorder.finalized)
            self.assertEqual(recorder.samples, controller.stats["samples_acquired"])
            self.assertEqual(recorder.final_samples, recorder.samples)
            self.assertEqual(
                Path(controller.current_session.data_file_path).parent,
                Path(self.recording_directory).resolve(),
            )
        finally:
            controller.close()


if __name__ == "__main__":
    unittest.main()
