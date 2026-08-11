from __future__ import annotations

import importlib.util
import json
import math
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np

from hrneowave.core.post_processor import PostProcessor
from hrneowave.core.wave_analysis import (
    WaveAnalysisConfig,
    WaveAnalysisError,
    WaveAnalyzer,
)

H5PY_AVAILABLE = importlib.util.find_spec("h5py") is not None


class WaveAnalyzerTests(unittest.TestCase):
    def setUp(self):
        self.sample_rate = 50.0
        self.frequency = 0.37
        self.amplitude = 0.4
        self.time = np.arange(int(self.sample_rate * 200.0)) / self.sample_rate
        self.signal = self.amplitude * np.sin(2 * np.pi * self.frequency * self.time)
        self.analyzer = WaveAnalyzer(WaveAnalysisConfig(segment_length=2048, overlap_ratio=0.5))

    def test_regular_wave_parameters_match_analytic_signal(self):
        result = self.analyzer.analyze_channel(self.signal, self.sample_rate, "m")
        spectrum = result["spectral"]
        waves = result["wave_parameters"]

        self.assertAlmostEqual(spectrum["peak_frequency"], self.frequency, delta=0.005)
        self.assertAlmostEqual(spectrum["peak_period"], 1 / self.frequency, delta=0.04)
        self.assertAlmostEqual(
            spectrum["Hm0"],
            2 * math.sqrt(2) * self.amplitude,
            delta=0.02,
        )
        self.assertAlmostEqual(waves["H1_3"], 2 * self.amplitude, delta=0.01)
        self.assertAlmostEqual(waves["T_mean"], 1 / self.frequency, delta=0.02)
        self.assertGreater(waves["n_waves"], 60)

    def test_welch_density_integrates_to_time_variance(self):
        rng = np.random.default_rng(42)
        values = rng.normal(0.0, 0.25, 20000)
        result = self.analyzer.analyze_channel(values, self.sample_rate, "m")
        ratio = result["quality"]["spectral_to_time_variance_ratio"]
        self.assertAlmostEqual(ratio, 1.0, delta=0.08)

    def test_cross_spectrum_recovers_coherence_and_phase(self):
        compared = self.amplitude * np.sin(2 * np.pi * self.frequency * self.time + np.pi / 4)
        reference = self.analyzer.analyze_channel(self.signal, self.sample_rate, "m")
        cross = self.analyzer.analyze_cross_spectrum(
            self.signal,
            compared,
            self.sample_rate,
            reference["spectral"]["peak_frequency"],
        )
        self.assertGreater(cross["coherence_at_reference_peak"], 0.99)
        self.assertAlmostEqual(cross["phase_at_reference_peak_degrees"], 45.0, delta=1.0)
        expected_lag = -1.0 / (8.0 * self.frequency)
        self.assertAlmostEqual(
            cross["time_lag_at_reference_peak_seconds"],
            expected_lag,
            delta=0.02,
        )
        self.assertIn("positive lag", cross["time_lag_convention"])

    def test_welch_reports_reproducible_approximate_confidence_factors(self):
        spectrum = self.analyzer.analyze_channel(self.signal, self.sample_rate, "m")["spectral"]

        self.assertEqual(
            spectrum["equivalent_degrees_of_freedom_approx"],
            2 * spectrum["segment_count"],
        )
        lower, upper = spectrum["psd_confidence_interval_95_factors_approx"]
        self.assertLess(lower, 1.0)
        self.assertGreater(upper, 1.0)

    def test_quality_detects_a_prolonged_flat_portion(self):
        damaged = self.signal.copy()
        damaged[3000:4000] = 0.123

        quality = self.analyzer.analyze_channel(damaged, self.sample_rate, "m")["quality"]

        self.assertGreaterEqual(quality["longest_flat_run_fraction"], 0.09)
        self.assertTrue(any("Portion plate prolongee" in warning for warning in quality["warnings"]))

    def test_rejects_non_finite_measurements(self):
        invalid = self.signal.copy()
        invalid[12] = np.nan
        with self.assertRaises(WaveAnalysisError):
            self.analyzer.analyze_channel(invalid, self.sample_rate)

    def test_constant_signal_does_not_create_a_false_peak(self):
        result = self.analyzer.analyze_channel(np.ones(4096), self.sample_rate, "m")
        self.assertEqual(result["spectral"]["peak_frequency"], 0.0)
        self.assertEqual(result["spectral"]["Hm0"], 0.0)
        self.assertEqual(result["wave_parameters"]["n_waves"], 0)
        self.assertIn("Signal constant", result["quality"]["warnings"][0])

    def test_interpolated_peak_cannot_escape_the_selected_frequency_band(self):
        sample_rate = 32.0
        time = np.arange(8192, dtype=float) / sample_rate
        low_frequency_signal = np.sin(2 * np.pi * 0.09 * time)
        analyzer = WaveAnalyzer(
            WaveAnalysisConfig(
                segment_length=1024,
                overlap_ratio=0.5,
                min_frequency=0.1,
                max_frequency=2.0,
            )
        )

        spectrum = analyzer.analyze_channel(low_frequency_signal, sample_rate, "cm")["spectral"]

        band_minimum, band_maximum = spectrum["analysis_band_hz"]
        self.assertGreaterEqual(spectrum["peak_frequency"], band_minimum)
        self.assertLessEqual(spectrum["peak_frequency"], band_maximum)
        quality = analyzer.analyze_channel(low_frequency_signal, sample_rate, "cm")["quality"]
        self.assertTrue(quality["peak_at_analysis_band_boundary"])
        self.assertTrue(any("limite de bande" in warning for warning in quality["warnings"]))

        with patch.object(WaveAnalyzer, "_interpolated_peak", return_value=0.0):
            clamped = analyzer.analyze_channel(low_frequency_signal, sample_rate, "cm")["spectral"]
        self.assertEqual(clamped["peak_frequency"], clamped["analysis_band_hz"][0])


class PostProcessorSpectralTests(unittest.TestCase):
    def test_json_rejects_unsynchronised_channel_lengths(self):
        payload = {
            "metadata": {"sample_rate_hz": 10.0},
            "time": [0.0, 0.1, 0.2, 0.3],
            "channels": {
                "channel_00": [0.0, 1.0, 0.0, -1.0],
                "channel_01": [0.0, 1.0, 0.0],
            },
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "unsynchronised.json"
            path.write_text(json.dumps(payload), encoding="utf-8")

            processor = PostProcessor()
            self.assertFalse(processor.load_data_file(str(path)))

    def test_csv_time_axis_can_define_sample_rate_and_run_full_analysis(self):
        import pandas as pd

        sample_rate = 20.0
        frequency = 0.5
        time = np.arange(4000) / sample_rate
        frame = pd.DataFrame(
            {
                "time": time,
                "channel_00": 0.25 * np.sin(2 * np.pi * frequency * time),
                "channel_01": 0.25 * np.sin(2 * np.pi * frequency * time + np.pi / 6),
            }
        )

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "waves.csv"
            frame.to_csv(path, index=False)
            processor = PostProcessor()
            self.assertTrue(processor.load_data_file(str(path)))
            self.assertAlmostEqual(processor.sample_rate, sample_rate, places=9)
            self.assertTrue(processor.run_analysis())

            results = processor.current_analysis
            self.assertAlmostEqual(
                results["spectral_analysis"]["channel_00"]["peak_frequency"],
                frequency,
                delta=0.01,
            )
            self.assertIn(
                "channel_00__channel_01",
                results["cross_spectral_analysis"],
            )
            self.assertIn("Hm0", results["wave_parameters"]["channel_00"])

            json_path = Path(directory) / "analysis.json"
            csv_path = Path(directory) / "analysis.csv"
            self.assertTrue(processor.export_results(str(json_path), "json"))
            self.assertTrue(processor.export_results(str(csv_path), "csv"))
            self.assertIn("spectral_analysis", json.loads(json_path.read_text()))
            self.assertIn("wave_parameters", csv_path.read_text())

    @unittest.skipUnless(H5PY_AVAILABLE, "h5py n'est pas installe")
    def test_hdf5_is_loaded_lazily_and_incomplete_session_is_rejected(self):
        import h5py

        sample_rate = 20.0
        time = np.arange(4000) / sample_rate
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "session.h5"
            with h5py.File(path, "w") as handle:
                handle.attrs["recording_status"] = "recording"
                metadata = handle.create_group("metadata")
                session = metadata.create_group("session")
                session.attrs["sample_rate"] = sample_rate
                data = handle.create_group("acquisition_data")
                data.create_dataset(
                    "channel_00",
                    data=0.2 * np.sin(2 * np.pi * 0.4 * time),
                )

            processor = PostProcessor()
            self.assertFalse(processor.load_data_file(str(path)))

            with h5py.File(path, "a") as handle:
                handle.attrs["recording_status"] = "complete"
                handle["acquisition_data"].create_dataset(
                    "channel_01",
                    data=0.2 * np.sin(2 * np.pi * 0.4 * time + np.pi / 3),
                )

            self.assertTrue(processor.load_data_file(str(path)))
            self.assertEqual(processor.current_data["channels"], {})
            self.assertEqual(
                processor.current_data["channel_keys"],
                ["channel_00", "channel_01"],
            )
            self.assertTrue(processor.run_analysis())
            analysis_path = Path(directory) / "analysis.h5"
            self.assertTrue(processor.export_results(str(analysis_path), "hdf5"))
            with h5py.File(analysis_path, "r") as handle:
                self.assertIn("spectral_analysis/channel_00/psd", handle)
                self.assertIn(
                    "cross_spectral_analysis/channel_00__channel_01/coherence",
                    handle,
                )


if __name__ == "__main__":
    unittest.main()
