"""Mesures courtes utilisées par le moniteur de calibration physique."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class LiveSignalMetrics:
    """Résumé électrique d'une fenêtre de tension réellement acquise."""

    sample_count: int
    latest_voltage: float
    mean_voltage: float
    noise_rms_voltage: float
    peak_to_peak_voltage: float
    minimum_voltage: float
    maximum_voltage: float
    drift_voltage: float
    verdict: str

    @property
    def capturable(self) -> bool:
        return self.verdict == "stable" and self.sample_count > 0


def analyze_live_voltage(
    values,
    *,
    voltage_limit: float,
    stability_limit_voltage: float,
    minimum_samples: int = 20,
) -> LiveSignalMetrics:
    """Évalue stabilité, bruit, dérive et saturation d'une fenêtre statique.

    ``stability_limit_voltage`` est une exigence opérateur explicite; aucune
    tolérance propre à un type de capteur n'est inventée par le logiciel.
    """

    data = np.asarray(values, dtype=np.float64).reshape(-1)
    limit = float(voltage_limit)
    stability_limit = float(stability_limit_voltage)
    if limit <= 0 or not np.isfinite(limit):
        raise ValueError("voltage_limit doit être positif et fini")
    if stability_limit <= 0 or not np.isfinite(stability_limit):
        raise ValueError("stability_limit_voltage doit être positif et fini")

    if data.size == 0:
        return _empty_metrics("settling")
    if not np.all(np.isfinite(data)):
        return _empty_metrics("invalid", sample_count=int(data.size))

    mean = float(np.mean(data))
    centered = data - mean
    noise_rms = float(np.sqrt(np.mean(centered**2)))
    minimum = float(np.min(data))
    maximum = float(np.max(data))
    peak_to_peak = maximum - minimum
    midpoint = data.size // 2
    drift = abs(float(np.mean(data[midpoint:])) - float(np.mean(data[:midpoint]))) if midpoint > 0 else 0.0

    if np.max(np.abs(data)) >= limit * 0.98:
        verdict = "saturation"
    elif data.size < max(1, int(minimum_samples)):
        verdict = "settling"
    elif noise_rms <= stability_limit and drift <= 2.0 * stability_limit:
        verdict = "stable"
    else:
        verdict = "unstable"

    return LiveSignalMetrics(
        sample_count=int(data.size),
        latest_voltage=float(data[-1]),
        mean_voltage=mean,
        noise_rms_voltage=noise_rms,
        peak_to_peak_voltage=peak_to_peak,
        minimum_voltage=minimum,
        maximum_voltage=maximum,
        drift_voltage=drift,
        verdict=verdict,
    )


def _empty_metrics(verdict: str, sample_count: int = 0) -> LiveSignalMetrics:
    nan = float("nan")
    return LiveSignalMetrics(
        sample_count=sample_count,
        latest_voltage=nan,
        mean_voltage=nan,
        noise_rms_voltage=nan,
        peak_to_peak_voltage=nan,
        minimum_voltage=nan,
        maximum_voltage=nan,
        drift_voltage=nan,
        verdict=verdict,
    )
