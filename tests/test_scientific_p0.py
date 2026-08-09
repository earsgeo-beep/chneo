import json
import math
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

import numpy as np

from hrneowave.acquisition.acquisition_controller import (
    AcquisitionController,
    AcquisitionSession,
    create_default_maritime_config,
)
from hrneowave.core.optimized_goda_analyzer import OptimizedGodaAnalyzer, ProbeGeometry
from hrneowave.core.post_processor import PostProcessor
from hrneowave.core.session_schema import build_channel_metadata


class ScientificP0Tests(unittest.TestCase):
    def _build_export_controller(self):
        controller = AcquisitionController.__new__(AcquisitionController)
        controller.daq = None
        controller.data_buffer = []
        controller.last_exported_path = None
        controller.stats = {
            "samples_acquired": 5,
            "acquisition_rate": 0.0,
            "last_update": None,
            "errors": 0,
            "buffer_overruns": 0,
        }
        configs = create_default_maritime_config()
        channels = [configs[0], configs[1]]
        controller.current_session = AcquisitionSession(
            session_id="scientific_p0_export",
            project_name="scientific_p0_export",
            start_time=datetime.now(),
            sampling_rate=50.0,
            total_samples=5,
            channels=channels,
        )
        raw_data = np.array(
            [
                [0.0, 0.0],
                [0.1, 0.2],
                [0.2, 0.4],
                [0.3, 0.6],
                [0.4, 0.8],
            ],
            dtype=float,
        )
        controller.data_buffer.append({
            "timestamp": datetime.now(),
            "raw_data": raw_data,
            "processed_data": controller._convert_to_physical_units(raw_data),
            "sample_count": raw_data.shape[0],
        })
        return controller

    def test_zero_crossing_returns_full_wave_height_for_sine(self):
        processor = PostProcessor()
        processor.sample_rate = 100.0
        time = np.arange(0.0, 10.0, 1.0 / processor.sample_rate)
        signal = np.sin(2.0 * np.pi * time)

        heights = processor._extract_wave_heights(signal)
        mean_period = processor._compute_mean_period(signal)

        self.assertGreaterEqual(len(heights), 8)
        self.assertTrue(np.allclose(heights, 2.0, atol=1e-12))
        self.assertAlmostEqual(mean_period, 1.0, places=12)

    def test_zero_crossing_removes_mean_level_and_ignores_exact_zero_artifacts(self):
        processor = PostProcessor()
        processor.sample_rate = 100.0
        time = np.arange(0.0, 10.0, 1.0 / processor.sample_rate)
        offset_signal = 1.2 + np.sin(2.0 * np.pi * time)
        quantized_signal = np.round(np.sin(2.0 * np.pi * time), 1)

        offset_heights = processor._extract_wave_heights(offset_signal)
        quantized_heights = processor._extract_wave_heights(quantized_signal)

        self.assertGreaterEqual(len(offset_heights), 8)
        self.assertGreaterEqual(len(quantized_heights), 8)
        self.assertTrue(np.allclose(offset_heights, 2.0, atol=1e-12))
        self.assertTrue(np.allclose(quantized_heights, 2.0, atol=1e-12))
        self.assertAlmostEqual(processor._compute_mean_period(quantized_signal), 1.0, places=12)

    def test_psd_m0_is_variance_for_unit_sine(self):
        for duration in (4.0, 8.0, 16.0):
            processor = PostProcessor()
            processor.sample_rate = 100.0
            time = np.arange(0.0, duration, 1.0 / processor.sample_rate)
            signal = np.sin(2.0 * np.pi * 2.0 * time)
            processor.current_data = {"channels": {"eta": signal}}

            spectrum = processor._compute_spectral_analysis()["eta"]

            self.assertAlmostEqual(spectrum["m0"], 0.5, places=5)
            self.assertAlmostEqual(spectrum["Hm0"], 4.0 * math.sqrt(0.5), places=5)
            self.assertAlmostEqual(spectrum["peak_frequency"], 2.0, delta=0.1)
            self.assertEqual(spectrum["method"], "one_sided_periodogram")

    def test_complex_goda_svd_recovers_incident_and_reflected_components(self):
        geometry = ProbeGeometry(
            positions=np.array([0.0, 0.4, 0.9, 1.4]),
            water_depth=1.0,
            frequency_range=(0.1, 5.0),
        )
        analyzer = OptimizedGodaAnalyzer(geometry, enable_cache=False)
        frequency = 0.8
        wave_number = analyzer._solve_dispersion_relation(2.0 * np.pi * frequency)
        matrix = np.column_stack(
            [
                np.exp(1j * wave_number * geometry.positions),
                np.exp(-1j * wave_number * geometry.positions),
            ]
        )
        true_components = np.array([1.0 + 0.3j, 0.25 - 0.2j])

        result = analyzer.analyze_frequency(matrix @ true_components, frequency)

        self.assertAlmostEqual(result.incident_amplitude, abs(true_components[0]), places=12)
        self.assertAlmostEqual(result.reflected_amplitude, abs(true_components[1]), places=12)
        self.assertAlmostEqual(
            result.reflection_coefficient,
            abs(true_components[1]) / abs(true_components[0]),
            places=12,
        )

    def test_pressure_simulation_stays_inside_default_daq_range(self):
        controller = AcquisitionController.__new__(AcquisitionController)
        controller._simulation_sample_index = 0
        controller._simulation_channel_state = {}
        configs = create_default_maritime_config()
        controller.current_session = AcquisitionSession(
            session_id="scientific_p0",
            project_name="scientific_p0",
            start_time=datetime.now(),
            sampling_rate=100.0,
            channels=[configs[index] for index in sorted(configs)],
        )

        raw_data = controller._generate_simulation_data()
        pressure_raw = raw_data[:, 2]

        self.assertFalse(np.any(pressure_raw < -5.0))
        self.assertFalse(np.any(pressure_raw > 5.0))

    def test_calibration_contract_does_not_return_fake_ok_coefficients(self):
        controller = AcquisitionController.__new__(AcquisitionController)
        controller.daq = None
        configs = create_default_maritime_config()
        controller.channels_config = {0: configs[0]}

        result = controller.calibrate_system()
        channel_result = result["channels"][0]

        self.assertFalse(result["calibration_valid"])
        self.assertEqual(result["calibration_status"], "not_performed")
        self.assertEqual(result["system_status"], "not_calibrated")
        self.assertEqual(channel_result["calibration_status"], "not_performed")
        self.assertIn("sensitivity_v_per_unit", channel_result)
        self.assertNotIn("offset_correction", channel_result)
        self.assertNotIn("scale_correction", channel_result)

    def test_time_vector_monotonic_and_dt(self):
        controller = self._build_export_controller()
        time_vector = controller._build_time_vector(5)

        self.assertTrue(np.all(np.diff(time_vector) > 0.0))
        self.assertTrue(np.allclose(np.diff(time_vector), 1.0 / 50.0))
        self.assertAlmostEqual(time_vector[0], 0.0)
        self.assertAlmostEqual(time_vector[-1], 4.0 / 50.0)

    def test_export_contains_sample_rate_units_and_calibration_metadata(self):
        controller = self._build_export_controller()

        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp)
            json_path = output_dir / "session.json"
            hdf5_path = output_dir / "session.h5"
            csv_path = output_dir / "session.csv"

            self.assertTrue(controller._export_json(str(json_path)))
            self.assertTrue(controller._export_hdf5(str(hdf5_path)))
            self.assertTrue(controller._export_csv(str(csv_path)))

            payload = json.loads(json_path.read_text(encoding="utf-8"))
            metadata = payload["metadata"]
            channel_metadata = payload["channel_metadata"][0]

            self.assertEqual(metadata["sample_rate_hz"], 50.0)
            self.assertEqual(metadata["dt_seconds"], 1.0 / 50.0)
            self.assertEqual(metadata["n_samples"], 5)
            self.assertEqual(metadata["duration_s"], 5.0 / 50.0)
            self.assertEqual(metadata["time_start"], 0.0)
            self.assertEqual(metadata["time_end"], 4.0 / 50.0)
            self.assertIn("channel_units", metadata)
            self.assertIn("sensor_id", channel_metadata)
            self.assertIn("calibration_status", channel_metadata)
            self.assertIn("calibration_coefficients", channel_metadata)

            import h5py

            with h5py.File(hdf5_path, "r") as handle:
                self.assertEqual(handle.attrs["sample_rate_hz"], 50.0)
                self.assertEqual(handle.attrs["dt_seconds"], 1.0 / 50.0)
                self.assertEqual(handle.attrs["n_samples"], 5)
                self.assertIn("metadata", handle)
                self.assertIn("channels", handle["metadata"])

            csv_text = csv_path.read_text(encoding="utf-8")
            self.assertIn("sample_rate_hz", csv_text.splitlines()[0])
            self.assertIn("dt_seconds", csv_text.splitlines()[0])
            self.assertIn("n_samples", csv_text.splitlines()[0])
            sidecar_path = Path(f"{csv_path}.metadata.json")
            self.assertTrue(sidecar_path.exists())
            sidecar = json.loads(sidecar_path.read_text(encoding="utf-8"))
            self.assertIn("channel_metadata", sidecar)
            self.assertIn("calibration_status", sidecar["channel_metadata"][0])

    def test_analysis_export_contains_processing_metadata_and_warnings(self):
        processor = PostProcessor()
        processor.sample_rate = 100.0
        time = np.arange(0.0, 2.0, 1.0 / processor.sample_rate)
        processor.current_data = {
            "metadata": {"sample_rate_hz": processor.sample_rate},
            "time": time,
            "channels": {"eta": np.sin(2.0 * np.pi * time)},
            "channel_metadata": build_channel_metadata([create_default_maritime_config()[0]]),
        }

        self.assertTrue(processor.run_analysis())
        metadata = processor.current_analysis["metadata"]

        self.assertEqual(metadata["schema_version"], "1.0.0")
        self.assertEqual(metadata["sample_rate_hz"], 100.0)
        self.assertEqual(metadata["dt_seconds"], 0.01)
        self.assertEqual(metadata["n_samples"], len(time))
        self.assertEqual(metadata["processing_method"], "post_processor.run_analysis")
        self.assertEqual(metadata["psd_method"], "one_sided_periodogram")
        self.assertEqual(metadata["window"], "hann")
        self.assertFalse(metadata["overlap_applied"])
        self.assertTrue(metadata["detrend"])
        self.assertTrue(any("CALIBRATION_NOT_PERFORMED" in warning for warning in metadata["warnings"]))

    def test_schema_requires_calibration_metadata(self):
        config = create_default_maritime_config()[0]
        metadata = build_channel_metadata([config])[0]

        self.assertIn("sensor_id", metadata)
        self.assertIn("calibration_id", metadata)
        self.assertIn("calibration_status", metadata)
        self.assertIn("calibration_coefficients", metadata)
        self.assertIn("conversion_formula", metadata)
        self.assertEqual(metadata["calibration_status"], "unverified")

    def test_csv_round_trip_uses_exact_time_column_not_time_start(self):
        controller = self._build_export_controller()

        with tempfile.TemporaryDirectory() as tmp:
            csv_path = Path(tmp) / "session.csv"
            self.assertTrue(controller._export_csv(str(csv_path)))

            processor = PostProcessor()
            self.assertTrue(processor.load_data_file(str(csv_path)))

            expected_time = np.arange(5, dtype=float) / 50.0
            self.assertTrue(np.allclose(processor.current_data["time"], expected_time))
            self.assertEqual(processor.current_data["metadata"]["sample_rate_hz"], 50.0)
            self.assertTrue(processor.current_data["channel_metadata"])
            self.assertIn("calibration_status", processor.current_data["channel_metadata"][0])

    def test_loader_rejects_sample_rate_inconsistent_with_time_axis(self):
        with tempfile.TemporaryDirectory() as tmp:
            csv_path = Path(tmp) / "bad_time.csv"
            csv_path.write_text(
                "\n".join([
                    "schema_version,sample_rate_hz,dt_seconds,n_samples,duration_s,time_start,time_end,clock_domain,data_kind,time,channel_00",
                    "1.0.0,100,0.01,3,0.03,0,0.02,relative_monotonic_seconds,physical,0.00,0.0",
                    "1.0.0,100,0.01,3,0.03,0,0.02,relative_monotonic_seconds,physical,0.02,1.0",
                    "1.0.0,100,0.01,3,0.03,0,0.02,relative_monotonic_seconds,physical,0.04,0.0",
                ]),
                encoding="utf-8",
            )

            processor = PostProcessor()
            self.assertFalse(processor.load_data_file(str(csv_path)))

    def test_analysis_rejects_nan_without_silent_time_compression(self):
        processor = PostProcessor()
        processor.sample_rate = 100.0
        values = np.sin(2.0 * np.pi * np.arange(0.0, 2.0, 0.01))
        values[50] = np.nan
        processor.current_data = {
            "metadata": {"sample_rate_hz": processor.sample_rate},
            "time": np.arange(values.size) / processor.sample_rate,
            "channels": {"eta": values},
        }

        self.assertFalse(processor.run_analysis())

    def test_hdf5_round_trip_preserves_channel_calibration_metadata(self):
        controller = self._build_export_controller()

        with tempfile.TemporaryDirectory() as tmp:
            hdf5_path = Path(tmp) / "session.h5"
            self.assertTrue(controller._export_hdf5(str(hdf5_path)))

            processor = PostProcessor()
            self.assertTrue(processor.load_data_file(str(hdf5_path)))

            channel_metadata = processor.current_data["channel_metadata"]
            self.assertTrue(channel_metadata)
            self.assertIn("sensor_id", channel_metadata[0])
            self.assertIn("calibration_id", channel_metadata[0])
            self.assertIn("calibration_status", channel_metadata[0])
            self.assertIn("calibration_coefficients", channel_metadata[0])
            self.assertEqual(channel_metadata[0]["calibration_status"], "unverified")


if __name__ == "__main__":
    unittest.main()
