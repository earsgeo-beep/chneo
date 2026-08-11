from __future__ import annotations

import numpy as np

from hrneowave.core.live_signal import analyze_live_voltage


def test_live_signal_accepts_a_stable_static_window():
    values = 0.016 + np.array([0.0, 0.0001, -0.0001, 0.00005] * 10)

    metrics = analyze_live_voltage(
        values,
        voltage_limit=10.0,
        stability_limit_voltage=0.001,
    )

    assert metrics.verdict == "stable"
    assert metrics.capturable
    assert metrics.mean_voltage == np.mean(values)
    assert metrics.noise_rms_voltage < 0.001


def test_live_signal_reports_motion_or_noise_as_unstable():
    values = np.linspace(0.0, 0.5, 100)

    metrics = analyze_live_voltage(
        values,
        voltage_limit=10.0,
        stability_limit_voltage=0.001,
    )

    assert metrics.verdict == "unstable"
    assert not metrics.capturable
    assert metrics.drift_voltage > 0.001


def test_live_signal_reports_voltage_range_saturation():
    metrics = analyze_live_voltage(
        np.full(40, 9.9),
        voltage_limit=10.0,
        stability_limit_voltage=0.001,
    )

    assert metrics.verdict == "saturation"
    assert not metrics.capturable
