from __future__ import annotations

import math
import tempfile
from pathlib import Path

import numpy as np
import pytest

from hrneowave.core.optimized_goda_analyzer import OptimizedGodaAnalyzer, ProbeGeometry
from hrneowave.core.post_processor import PostProcessor
from hrneowave.core.wave_separation import (
    MultiProbeWaveSeparator,
    WaveSeparationConfig,
    WaveSeparationError,
)


def _synthetic_incident_reflected_case():
    sample_rate = 20.0
    frequency = 0.5
    water_depth = 1.0
    positions = np.array([0.0, 0.4, 0.9, 1.4])
    geometry = ProbeGeometry(positions, water_depth, (0.1, 1.0))
    analyzer = OptimizedGodaAnalyzer(geometry, enable_cache=False)
    wave_number = analyzer._solve_dispersion_relation(2.0 * np.pi * frequency)
    incident = 0.3 + 0.0j
    reflected = 0.09 * np.exp(1j * 0.4)
    time = np.arange(int(sample_rate * 200.0)) / sample_rate
    complex_amplitudes = incident * np.exp(1j * wave_number * positions) + reflected * np.exp(
        -1j * wave_number * positions
    )
    values = np.real(complex_amplitudes[:, None] * np.exp(1j * 2.0 * np.pi * frequency * time)[None, :])
    return {
        "sample_rate": sample_rate,
        "frequency": frequency,
        "water_depth": water_depth,
        "positions": positions,
        "incident": incident,
        "reflected": reflected,
        "time": time,
        "values": values,
    }


def test_multi_probe_separation_recovers_known_reflection_coefficient():
    case = _synthetic_incident_reflected_case()
    separator = MultiProbeWaveSeparator(
        WaveSeparationConfig(
            probe_positions_m=tuple(case["positions"]),
            water_depth_m=case["water_depth"],
            min_frequency_hz=0.1,
            max_frequency_hz=1.0,
            segment_length=800,
            overlap_ratio=0.5,
        )
    )

    result = separator.analyze(case["values"], case["sample_rate"])

    expected_reflection = abs(case["reflected"]) / abs(case["incident"])
    expected_incident_hm0 = 2.0 * math.sqrt(2.0) * abs(case["incident"])
    expected_reflected_hm0 = 2.0 * math.sqrt(2.0) * abs(case["reflected"])
    assert result["status"] == "complete"
    assert result["energy_reflection_coefficient"] == pytest.approx(
        expected_reflection,
        abs=0.005,
    )
    assert result["incident_Hm0"] == pytest.approx(expected_incident_hm0, abs=0.005)
    assert result["reflected_Hm0"] == pytest.approx(expected_reflected_hm0, abs=0.005)


def test_post_processor_activates_separation_only_with_explicit_geometry():
    case = _synthetic_incident_reflected_case()
    processor = PostProcessor()
    processor.sample_rate = case["sample_rate"]
    processor.config["analysis"].update(
        {
            "window_size": 800,
            "min_frequency": 0.1,
            "max_frequency": 1.0,
        }
    )
    channel_keys = [f"probe_{index:02d}" for index in range(len(case["positions"]))]
    processor.current_data = {
        "metadata": {
            "sample_rate_hz": case["sample_rate"],
            "water_depth_m": case["water_depth"],
        },
        "time": case["time"],
        "channels": {channel: case["values"][index] for index, channel in enumerate(channel_keys)},
        "channel_keys": channel_keys,
        "channel_metadata": [
            {
                "key": channel,
                "sensor_type": "wave_height",
                "physical_units": "m",
                "probe_position_m": float(case["positions"][index]),
                "calibration_status": "valid",
            }
            for index, channel in enumerate(channel_keys)
        ],
    }

    assert processor.run_analysis()
    separation = processor.current_analysis["incident_reflected_analysis"]
    assert separation["status"] == "complete"
    assert separation["channel_keys"] == channel_keys
    assert separation["physical_unit"] == "m"
    assert separation["energy_reflection_coefficient"] == pytest.approx(0.3, abs=0.005)

    h5py = pytest.importorskip("h5py")
    with tempfile.TemporaryDirectory() as directory:
        output_path = Path(directory) / "separation.h5"
        assert processor.export_results(str(output_path), "hdf5")
        with h5py.File(output_path, "r") as handle:
            group = handle["incident_reflected_analysis"]
            assert group.attrs["status"] == "complete"
            assert "incident_psd" in group
            assert "reflected_psd" in group

    processor.current_data["channel_metadata"][0]["calibration_status"] = "unverified"
    metadata_map = processor._channel_metadata_map(
        channel_keys,
        processor.current_data["channel_metadata"],
    )
    blocked = processor._compute_incident_reflected_analysis(
        channel_keys,
        metadata_map,
    )
    assert blocked["status"] == "blocked"
    assert blocked["uncalibrated_channels"] == ["probe_00"]


def test_separation_rejects_less_than_three_probes():
    config = WaveSeparationConfig(
        probe_positions_m=(0.0, 0.5),
        water_depth_m=1.0,
        min_frequency_hz=0.1,
        max_frequency_hz=1.0,
    )
    separator = MultiProbeWaveSeparator(config)

    with pytest.raises(WaveSeparationError):
        separator.analyze(np.zeros((2, 2048)), sample_rate=20.0)
