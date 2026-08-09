"""Frequency-domain separation of incident and reflected laboratory waves.

The implementation applies the linear multi-probe model independently to each
Welch segment and frequency:

    eta_j(f) = A_i(f) exp(+i k x_j) + A_r(f) exp(-i k x_j)

where ``k`` is obtained from ``omega² = g k tanh(k h)``.  Averaging the squared
complex amplitudes over segments produces one-sided incident and reflected
spectral densities with the same window normalization as a Welch PSD.
"""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from typing import Any

import numpy as np
from scipy import signal

from .optimized_goda_analyzer import OptimizedGodaAnalyzer, ProbeGeometry


class WaveSeparationError(ValueError):
    """Raised when geometry or measurements cannot support wave separation."""


@dataclass(frozen=True)
class WaveSeparationConfig:
    """Physical geometry and numerical controls for multi-probe separation."""

    probe_positions_m: tuple[float, ...]
    water_depth_m: float
    min_frequency_hz: float
    max_frequency_hz: float
    segment_length: int = 1024
    overlap_ratio: float = 0.5
    window: str = "hann"
    max_condition_number: float = 100.0

    def validate(self, sample_rate: float) -> None:
        positions = np.asarray(self.probe_positions_m, dtype=np.float64)
        if positions.ndim != 1 or len(positions) < 3:
            raise WaveSeparationError("La separation incidente/reflechie requiert au moins trois sondes")
        if not np.all(np.isfinite(positions)) or len(np.unique(positions)) != len(positions):
            raise WaveSeparationError("Les positions de sondes doivent etre finies et distinctes")
        if not math.isfinite(self.water_depth_m) or self.water_depth_m <= 0:
            raise WaveSeparationError("La profondeur d'eau doit etre strictement positive")
        if not math.isfinite(sample_rate) or sample_rate <= 0:
            raise WaveSeparationError("La frequence d'echantillonnage est invalide")
        if (
            not math.isfinite(self.min_frequency_hz)
            or not math.isfinite(self.max_frequency_hz)
            or self.min_frequency_hz <= 0
            or self.max_frequency_hz <= self.min_frequency_hz
            or self.max_frequency_hz > sample_rate / 2
        ):
            raise WaveSeparationError("La bande de separation est invalide")
        if self.segment_length < 16:
            raise WaveSeparationError("La taille de segment doit etre au moins egale a 16")
        if not 0 <= self.overlap_ratio < 1:
            raise WaveSeparationError("Le recouvrement doit appartenir a [0, 1[")
        if not math.isfinite(self.max_condition_number) or self.max_condition_number <= 1:
            raise WaveSeparationError("Le seuil de conditionnement doit etre superieur a 1")


class MultiProbeWaveSeparator:
    """Separate incident and reflected PSDs from synchronized wave probes."""

    METHOD_VERSION = "1.0"

    def __init__(self, config: WaveSeparationConfig):
        self.config = config

    def analyze(self, values: np.ndarray, sample_rate: float) -> dict[str, Any]:
        """Analyze a matrix shaped ``(n_probes, n_samples)``."""

        self.config.validate(sample_rate)
        measurements = np.asarray(values, dtype=np.float64)
        expected_probes = len(self.config.probe_positions_m)
        if measurements.ndim != 2 or measurements.shape[0] != expected_probes:
            raise WaveSeparationError(f"Matrice attendue: ({expected_probes}, n_echantillons)")
        if measurements.shape[1] < 16 or not np.all(np.isfinite(measurements)):
            raise WaveSeparationError("Les mesures multi-sondes sont insuffisantes ou invalides")

        sample_count = measurements.shape[1]
        nperseg = min(self.config.segment_length, sample_count)
        noverlap = min(
            nperseg - 1,
            int(round(nperseg * self.config.overlap_ratio)),
        )
        step = nperseg - noverlap
        starts = np.arange(0, sample_count - nperseg + 1, step, dtype=int)
        if len(starts) == 0:
            raise WaveSeparationError("Aucun segment spectral exploitable")

        window = signal.get_window(self.config.window, nperseg, fftbins=True)
        window_energy = float(np.sum(window**2))
        processed = signal.detrend(measurements, axis=1, type="linear")
        segment_spectra = np.stack(
            [np.fft.rfft(processed[:, start : start + nperseg] * window, axis=1) for start in starts],
            axis=0,
        )
        frequencies = np.fft.rfftfreq(nperseg, d=1.0 / sample_rate)
        frequency_resolution = float(sample_rate / nperseg)
        one_sided_factor = np.full(len(frequencies), 2.0)
        one_sided_factor[0] = 1.0
        if nperseg % 2 == 0:
            one_sided_factor[-1] = 1.0
        density_scale = one_sided_factor / (sample_rate * window_energy)

        geometry = ProbeGeometry(
            positions=np.asarray(self.config.probe_positions_m, dtype=np.float64),
            water_depth=self.config.water_depth_m,
            frequency_range=(
                self.config.min_frequency_hz,
                self.config.max_frequency_hz,
            ),
        )
        analyzer = OptimizedGodaAnalyzer(geometry, enable_cache=True)
        incident_psd = np.zeros(len(frequencies), dtype=np.float64)
        reflected_psd = np.zeros(len(frequencies), dtype=np.float64)
        reflection_coefficient = np.zeros(len(frequencies), dtype=np.float64)
        condition_numbers = np.zeros(len(frequencies), dtype=np.float64)
        normalized_residuals = np.zeros(len(frequencies), dtype=np.float64)
        valid = (
            (frequencies >= self.config.min_frequency_hz)
            & (frequencies <= self.config.max_frequency_hz)
            & (frequencies > 0)
        )

        rejected_frequencies: list[float] = []
        for frequency_index in np.flatnonzero(valid):
            frequency = float(frequencies[frequency_index])
            matrix, left_vectors, singular_values, right_vectors = analyzer._get_geometry_matrix(frequency)
            if len(singular_values) < 2:
                valid[frequency_index] = False
                rejected_frequencies.append(frequency)
                continue
            condition_number = float(np.max(singular_values) / np.min(singular_values))
            condition_numbers[frequency_index] = condition_number
            if condition_number > self.config.max_condition_number:
                valid[frequency_index] = False
                rejected_frequencies.append(frequency)
                continue

            probe_coefficients = segment_spectra[:, :, frequency_index].T
            components = analyzer._solve_wave_components_svd(
                probe_coefficients,
                left_vectors,
                singular_values,
                right_vectors,
            ).T
            reconstructed = (matrix @ components.T).T
            residual_norm = np.linalg.norm(
                reconstructed - probe_coefficients.T,
                axis=1,
            )
            measurement_norm = np.linalg.norm(probe_coefficients.T, axis=1)
            normalized = np.divide(
                residual_norm,
                measurement_norm,
                out=np.zeros_like(residual_norm),
                where=measurement_norm > 0,
            )
            normalized_residuals[frequency_index] = float(np.mean(normalized))

            incident_psd[frequency_index] = float(
                np.mean(np.abs(components[:, 0]) ** 2) * density_scale[frequency_index]
            )
            reflected_psd[frequency_index] = float(
                np.mean(np.abs(components[:, 1]) ** 2) * density_scale[frequency_index]
            )
            if incident_psd[frequency_index] > 0:
                reflection_coefficient[frequency_index] = math.sqrt(
                    reflected_psd[frequency_index] / incident_psd[frequency_index]
                )

        valid_indices = np.flatnonzero(valid)
        if len(valid_indices) < 2:
            raise WaveSeparationError("Moins de deux frequences sont suffisamment bien conditionnees")

        incident_m0 = float(np.sum(incident_psd[valid]) * frequency_resolution)
        reflected_m0 = float(np.sum(reflected_psd[valid]) * frequency_resolution)
        energy_reflection_coefficient = math.sqrt(reflected_m0 / incident_m0) if incident_m0 > 0 else 0.0

        return {
            "status": "complete",
            "method": "multi_probe_frequency_domain_least_squares",
            "method_version": self.METHOD_VERSION,
            "model": "eta_j = Ai*exp(+ikx_j) + Ar*exp(-ikx_j)",
            "configuration": asdict(self.config),
            "frequencies": frequencies.tolist(),
            "valid_frequency_mask": valid.tolist(),
            "incident_psd": incident_psd.tolist(),
            "reflected_psd": reflected_psd.tolist(),
            "reflection_coefficient_by_frequency": reflection_coefficient.tolist(),
            "condition_number_by_frequency": condition_numbers.tolist(),
            "normalized_residual_by_frequency": normalized_residuals.tolist(),
            "rejected_frequencies_hz": rejected_frequencies,
            "incident_m0": incident_m0,
            "reflected_m0": reflected_m0,
            "incident_Hm0": 4.0 * math.sqrt(max(incident_m0, 0.0)),
            "reflected_Hm0": 4.0 * math.sqrt(max(reflected_m0, 0.0)),
            "energy_reflection_coefficient": energy_reflection_coefficient,
            "frequency_resolution": frequency_resolution,
            "segment_length": nperseg,
            "overlap_samples": noverlap,
            "segment_count": int(len(starts)),
            "probe_count": expected_probes,
            "sample_count": int(sample_count),
            "duration_seconds": float(sample_count / sample_rate),
        }
