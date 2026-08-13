"""Analyse scientifique des series temporelles de houle.

Les spectres sont des densites spectrales de variance unilaterales calculees
par la methode de Welch. Les parametres spectraux suivent les definitions ITTC
usuelles: Hm0, Tp, Tm01 et Tm02.
"""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from typing import Any

import numpy as np
from scipy import signal, stats


class WaveAnalysisError(ValueError):
    """Donnees ou configuration incompatibles avec une analyse fiable."""


@dataclass(frozen=True)
class WaveAnalysisConfig:
    """Parametres numeriques explicites et exportables avec les resultats."""

    segment_length: int = 1024
    overlap_ratio: float = 0.5
    window: str = "hann"
    detrend: bool | str = True
    fft_length: int | None = None
    average: str = "mean"
    min_frequency: float = 0.0
    max_frequency: float | None = None
    filter_type: str = "none"
    filter_low_frequency: float | None = None
    filter_high_frequency: float | None = None
    filter_order: int = 4
    minimum_samples: int = 32

    def validate(self, sample_rate: float) -> None:
        if sample_rate <= 0 or not math.isfinite(sample_rate):
            raise WaveAnalysisError("La frequence d'echantillonnage est invalide")
        if self.segment_length < 8:
            raise WaveAnalysisError("La taille de segment doit etre au moins egale a 8")
        if self.fft_length is not None and self.fft_length < self.segment_length:
            raise WaveAnalysisError("Le nombre de points FFT doit etre superieur ou egal au segment")
        if not 0 <= self.overlap_ratio < 1:
            raise WaveAnalysisError("Le recouvrement doit etre compris entre 0 et 1 exclu")
        if self.average not in {"mean", "median"}:
            raise WaveAnalysisError("La moyenne Welch doit etre 'mean' ou 'median'")
        detrend = self.detrend
        if detrend not in {True, False, "none", "constant", "linear"}:
            raise WaveAnalysisError("Le detrendage doit etre none, constant ou linear")
        try:
            signal.get_window(self.window, self.segment_length)
        except (TypeError, ValueError) as exc:
            raise WaveAnalysisError(f"Fenetre spectrale invalide: {self.window}") from exc
        if self.min_frequency < 0:
            raise WaveAnalysisError("La frequence minimale ne peut pas etre negative")
        if self.min_frequency >= sample_rate / 2:
            raise WaveAnalysisError("La frequence minimale atteint ou depasse Nyquist")
        if self.max_frequency is not None:
            if self.max_frequency <= self.min_frequency:
                raise WaveAnalysisError("La bande frequentielle est invalide")
            if self.max_frequency > sample_rate / 2:
                raise WaveAnalysisError("La frequence maximale depasse Nyquist")
        self._validate_filter(sample_rate)

    def _validate_filter(self, sample_rate: float) -> None:
        filter_type = str(self.filter_type).lower()
        if filter_type not in {"none", "lowpass", "highpass", "bandpass", "bandstop"}:
            raise WaveAnalysisError("Type de filtre inconnu")
        if not 1 <= int(self.filter_order) <= 10:
            raise WaveAnalysisError("L'ordre du filtre doit etre compris entre 1 et 10")
        if filter_type == "none":
            return
        nyquist = sample_rate / 2.0
        low = self.filter_low_frequency
        high = self.filter_high_frequency
        if filter_type in {"highpass", "bandpass", "bandstop"}:
            if low is None or not 0 < float(low) < nyquist:
                raise WaveAnalysisError("La coupure basse du filtre doit etre entre 0 et Nyquist")
        if filter_type in {"lowpass", "bandpass", "bandstop"}:
            if high is None or not 0 < float(high) < nyquist:
                raise WaveAnalysisError("La coupure haute du filtre doit etre entre 0 et Nyquist")
        if filter_type in {"bandpass", "bandstop"} and float(low) >= float(high):
            raise WaveAnalysisError("Les coupures du filtre sont inversees")


class WaveAnalyzer:
    """Calcule statistiques, spectre, moments et vagues individuelles."""

    METHOD_VERSION = "1.4"

    def __init__(self, config: WaveAnalysisConfig | None = None):
        self.config = config or WaveAnalysisConfig()

    def configuration(self) -> dict[str, Any]:
        return {
            "method": "Welch PSD + zero-upcrossing",
            "method_version": self.METHOD_VERSION,
            **asdict(self.config),
        }

    def analyze_channel(
        self,
        values: np.ndarray,
        sample_rate: float,
        unit: str = "",
    ) -> dict[str, Any]:
        self.config.validate(sample_rate)
        series = self._validate_series(values)
        processed, processing = self.prepare_signal(series, sample_rate)

        spectral = self._spectral_analysis(
            processed,
            sample_rate,
            unit,
            constant_signal=bool(np.ptp(series) == 0),
        )
        temporal = self._zero_upcrossing_analysis(processed, sample_rate, unit)
        quality = self._quality_indicators(series, processed, spectral, sample_rate)
        peak_period_reliable = bool(quality["peak_period_reliable"])

        return {
            "basic_stats": self._basic_statistics(series, sample_rate, unit),
            "analysis_signal_stats": self._basic_statistics(processed, sample_rate, unit),
            "signal_processing": processing,
            "spectral": spectral,
            "wave_parameters": {
                **temporal,
                "Hm0": spectral["Hm0"],
                "Tp": spectral["peak_period"],
                "Tp_reliable": peak_period_reliable,
                "Tm01": spectral["Tm01"],
                "Tm02": spectral["Tm02"],
                "Te": spectral["Te"],
            },
            "quality": quality,
        }

    def analyze_cross_spectrum(
        self,
        reference: np.ndarray,
        compared: np.ndarray,
        sample_rate: float,
        reference_peak_frequency: float,
    ) -> dict[str, Any]:
        """Analyse la coherence et la phase d'un canal par rapport a une reference."""
        self.config.validate(sample_rate)
        x = self._validate_series(reference)
        y = self._validate_series(compared)
        sample_count = min(len(x), len(y))
        x = x[:sample_count]
        y = y[:sample_count]
        x, _ = self.prepare_signal(x, sample_rate)
        y, _ = self.prepare_signal(y, sample_rate)

        nperseg, noverlap, segment_count = self._welch_layout(sample_count)
        common = {
            "fs": sample_rate,
            "window": self.config.window,
            "nperseg": nperseg,
            "noverlap": noverlap,
            "detrend": False,
        }
        frequencies, coherence = signal.coherence(x, y, **common)
        _, cross_density = signal.csd(
            x,
            y,
            scaling="density",
            return_onesided=True,
            **common,
        )
        coherence = np.nan_to_num(coherence, nan=0.0, posinf=0.0, neginf=0.0)
        cross_density = np.nan_to_num(cross_density, nan=0.0, posinf=0.0, neginf=0.0)
        phase_degrees = np.degrees(np.angle(cross_density))
        band = self._frequency_mask(frequencies, sample_rate)
        valid_indices = np.flatnonzero(band)
        if len(valid_indices) == 0:
            raise WaveAnalysisError("Aucune frequence exploitable pour l'analyse croisee")

        peak_index = int(
            valid_indices[np.argmin(np.abs(frequencies[valid_indices] - reference_peak_frequency))]
        )
        max_index = int(valid_indices[np.argmax(coherence[valid_indices])])
        peak_frequency = float(frequencies[peak_index])
        phase_at_peak = float(phase_degrees[peak_index])
        time_lag = (
            -math.radians(phase_at_peak) / (2 * math.pi * peak_frequency) if peak_frequency > 0 else 0.0
        )

        return {
            "frequencies": frequencies.tolist(),
            "coherence": coherence.tolist(),
            "phase_degrees": phase_degrees.tolist(),
            "reference_peak_frequency": float(reference_peak_frequency),
            "coherence_at_reference_peak": float(coherence[peak_index]),
            "phase_at_reference_peak_degrees": phase_at_peak,
            "phase_convention": (
                "arg(conj(X_reference) * X_compared); positive phase means the compared signal leads"
            ),
            "time_lag_convention": "positive lag means the compared signal occurs later",
            "time_lag_at_reference_peak_seconds": time_lag,
            "maximum_coherence": float(coherence[max_index]),
            "frequency_at_maximum_coherence": float(frequencies[max_index]),
            "segment_count": segment_count,
        }

    def prepare_signal(
        self,
        values: np.ndarray,
        sample_rate: float,
    ) -> tuple[np.ndarray, dict[str, Any]]:
        """Prepare an offline analysis signal and return complete provenance.

        Detrending is explicit and the optional Butterworth filter is applied
        forward/backward in second-order sections.  This preserves peak phase
        positions and avoids the numerical fragility of high-order ``ba``
        coefficients.
        """

        self.config.validate(sample_rate)
        series = self._validate_series(values)
        detrend = self.config.detrend
        detrend_type = (
            "linear"
            if detrend is True
            else "none"
            if detrend is False
            else str(detrend).lower()
        )
        if detrend_type == "linear" and len(series) > 2:
            processed = signal.detrend(series, type="linear")
        elif detrend_type == "constant":
            processed = signal.detrend(series, type="constant")
        else:
            processed = series.copy()

        filter_type = str(self.config.filter_type).lower()
        if filter_type != "none":
            cutoff: float | list[float]
            if filter_type == "lowpass":
                cutoff = float(self.config.filter_high_frequency)
            elif filter_type == "highpass":
                cutoff = float(self.config.filter_low_frequency)
            else:
                cutoff = [
                    float(self.config.filter_low_frequency),
                    float(self.config.filter_high_frequency),
                ]
            sos = signal.butter(
                int(self.config.filter_order),
                cutoff,
                btype=filter_type,
                fs=sample_rate,
                output="sos",
            )
            try:
                processed = signal.sosfiltfilt(sos, processed)
            except ValueError as exc:
                raise WaveAnalysisError(
                    "L'intervalle est trop court pour appliquer ce filtre sans dephasage"
                ) from exc

        return np.asarray(processed, dtype=np.float64), {
            "detrend": detrend_type,
            "filter": {
                "type": filter_type,
                "family": "butterworth" if filter_type != "none" else "none",
                "implementation": "sosfiltfilt" if filter_type != "none" else "none",
                "zero_phase": bool(filter_type != "none"),
                "order": int(self.config.filter_order) if filter_type != "none" else 0,
                "low_frequency_hz": self.config.filter_low_frequency,
                "high_frequency_hz": self.config.filter_high_frequency,
            },
        }

    def _spectral_analysis(
        self,
        values: np.ndarray,
        sample_rate: float,
        unit: str,
        constant_signal: bool = False,
    ) -> dict[str, Any]:
        nperseg, noverlap, segment_count = self._welch_layout(len(values))
        nfft = max(nperseg, int(self.config.fft_length or nperseg))
        frequencies, density = signal.welch(
            values,
            fs=sample_rate,
            window=self.config.window,
            nperseg=nperseg,
            noverlap=noverlap,
            nfft=nfft,
            detrend=False,
            return_onesided=True,
            scaling="density",
            average=self.config.average,
        )
        density = np.maximum(np.asarray(density, dtype=np.float64), 0.0)
        if constant_signal:
            density.fill(0.0)
        band = self._frequency_mask(frequencies, sample_rate)
        band_indices = np.flatnonzero(band)
        if len(band_indices) < 2:
            raise WaveAnalysisError("La bande d'analyse contient moins de deux raies")

        band_frequencies = frequencies[band]
        band_density = density[band]
        moments = {
            "m_1": self._spectral_moment(band_frequencies, band_density, -1),
            "m0": self._spectral_moment(band_frequencies, band_density, 0),
            "m1": self._spectral_moment(band_frequencies, band_density, 1),
            "m2": self._spectral_moment(band_frequencies, band_density, 2),
            "m4": self._spectral_moment(band_frequencies, band_density, 4),
        }
        peak_local_index = int(np.argmax(band_density))
        peak_index = int(band_indices[peak_local_index])
        has_resolved_peak = float(band_density[peak_local_index]) > np.finfo(np.float64).tiny
        peak_frequency = (
            self._interpolated_peak(frequencies, density, peak_index) if has_resolved_peak else 0.0
        )
        if has_resolved_peak:
            peak_frequency = float(
                np.clip(
                    peak_frequency,
                    float(band_frequencies[0]),
                    float(band_frequencies[-1]),
                )
            )

        m0 = moments["m0"]
        m1 = moments["m1"]
        m2 = moments["m2"]
        m4 = moments["m4"]
        m_1 = moments["m_1"]
        hm0 = 4.0 * math.sqrt(max(m0, 0.0))
        tm01 = m0 / m1 if m1 > 0 else 0.0
        tm02 = math.sqrt(m0 / m2) if m2 > 0 else 0.0
        energy_period = m_1 / m0 if m0 > 0 else 0.0
        bandwidth = math.sqrt(max(0.0, 1.0 - (m2 * m2) / (m0 * m4))) if m0 > 0 and m4 > 0 else 0.0
        equivalent_dof = max(2, 2 * segment_count) if self.config.average == "mean" else None
        confidence_factors = (
            [
                float(equivalent_dof / stats.chi2.ppf(0.975, equivalent_dof)),
                float(equivalent_dof / stats.chi2.ppf(0.025, equivalent_dof)),
            ]
            if equivalent_dof is not None
            else None
        )

        return {
            "method": "Welch",
            "frequencies": frequencies.tolist(),
            "psd": density.tolist(),
            "power_spectrum": density.tolist(),
            "psd_units": f"{unit or 'unit'}^2/Hz",
            "analysis_band_hz": [
                float(band_frequencies[0]),
                float(band_frequencies[-1]),
            ],
            # Rayleigh resolution is governed by segment duration.  Zero
            # padding only refines the displayed frequency grid.
            "frequency_resolution": float(sample_rate / nperseg),
            "frequency_bin_spacing": float(frequencies[1] - frequencies[0]),
            "fft_length": nfft,
            "nyquist_frequency": float(sample_rate / 2),
            "segment_length": nperseg,
            "overlap_samples": noverlap,
            "segment_count": segment_count,
            "window": self.config.window,
            "average": self.config.average,
            "equivalent_degrees_of_freedom_approx": equivalent_dof,
            "psd_confidence_interval_95_factors_approx": confidence_factors,
            "confidence_interval_note": (
                "Multiply PSD by these lower/upper factors; approximation uses 2K "
                "degrees of freedom and does not correct overlap correlation"
                if confidence_factors is not None
                else "Chi-square confidence factors are not reported for median Welch averaging"
            ),
            "spectral_moments": moments,
            "peak_frequency": peak_frequency,
            "peak_period": 1.0 / peak_frequency if peak_frequency > 0 else 0.0,
            "peak_psd": float(density[peak_index]),
            "total_energy": m0,
            "Hm0": hm0,
            "Tm01": tm01,
            "Tm02": tm02,
            "Te": energy_period,
            "spectral_bandwidth_epsilon": bandwidth,
        }

    def _zero_upcrossing_analysis(
        self,
        values: np.ndarray,
        sample_rate: float,
        unit: str,
    ) -> dict[str, Any]:
        indices = np.flatnonzero((values[:-1] <= 0.0) & (values[1:] > 0.0))
        crossings: list[float] = []
        for index in indices:
            denominator = values[index + 1] - values[index]
            fraction = -values[index] / denominator if denominator else 0.0
            crossings.append(float(index + fraction))

        heights: list[float] = []
        periods: list[float] = []
        for start_crossing, end_crossing in zip(crossings[:-1], crossings[1:], strict=False):
            start = max(0, int(math.ceil(start_crossing)))
            stop = min(len(values), int(math.floor(end_crossing)) + 1)
            if stop - start < 2:
                continue
            segment = values[start:stop]
            heights.append(float(np.max(segment) - np.min(segment)))
            periods.append(float((end_crossing - start_crossing) / sample_rate))

        if not heights:
            return {
                "method": "zero-upcrossing",
                "unit": unit,
                "n_waves": 0,
                "Hs": 0.0,
                "H1_3": 0.0,
                "H1_10": 0.0,
                "H_min": 0.0,
                "H_max": 0.0,
                "H_mean": 0.0,
                "H_rms": 0.0,
                "T_mean": 0.0,
                "T_H1_3": 0.0,
            }

        height_array = np.asarray(heights)
        period_array = np.asarray(periods)
        order = np.argsort(height_array)[::-1]
        top_third_count = max(1, int(math.ceil(len(height_array) / 3)))
        top_tenth_count = max(1, int(math.ceil(len(height_array) / 10)))
        top_third = order[:top_third_count]

        return {
            "method": "zero-upcrossing",
            "unit": unit,
            "n_waves": int(len(height_array)),
            "Hs": float(np.mean(height_array[top_third])),
            "H1_3": float(np.mean(height_array[top_third])),
            "H1_10": float(np.mean(height_array[order[:top_tenth_count]])),
            "H_min": float(np.min(height_array)),
            "H_max": float(np.max(height_array)),
            "H_mean": float(np.mean(height_array)),
            "H_rms": float(np.sqrt(np.mean(height_array**2))),
            "T_mean": float(np.mean(period_array)),
            "T_H1_3": float(np.mean(period_array[top_third])),
        }

    def _quality_indicators(
        self,
        original: np.ndarray,
        processed: np.ndarray,
        spectral: dict[str, Any],
        sample_rate: float,
    ) -> dict[str, Any]:
        warnings: list[str] = []
        variance_time = float(np.var(processed))
        variance_spectral = float(spectral["spectral_moments"]["m0"])
        variance_ratio = variance_spectral / variance_time if variance_time > 0 else 0.0
        if bool(np.ptp(original) == 0):
            variance_time = 0.0
            variance_ratio = 0.0
            warnings.append("Signal constant: aucune energie de houle detectee")
        elif not 0.8 <= variance_ratio <= 1.2:
            warnings.append("Ecart notable entre variance temporelle et spectrale")

        segment_count = int(spectral["segment_count"])
        if segment_count < 4:
            warnings.append("Moins de quatre segments Welch: estimation spectrale peu stable")

        block_count = min(8, max(1, len(processed) // 32))
        block_variances = np.array(
            [np.var(block) for block in np.array_split(processed, block_count) if len(block)]
        )
        maximum_block_variance = float(np.max(block_variances))
        if maximum_block_variance > 0 and len(block_variances) > 1:
            variance_floor = max(
                np.finfo(np.float64).tiny,
                maximum_block_variance * 1e-12,
            )
            stationarity_ratio = float(
                maximum_block_variance / max(float(np.min(block_variances)), variance_floor)
            )
        else:
            stationarity_ratio = 1.0
        if stationarity_ratio > 4.0:
            warnings.append("Variance fortement non stationnaire entre les blocs")

        flat_tolerance = max(1e-12, float(np.ptp(original)) * 1e-12)
        longest_flat_run = self._longest_flat_run(original, flat_tolerance)
        flat_run_fraction = longest_flat_run / len(original)
        if not bool(np.ptp(original) == 0) and flat_run_fraction >= 0.05:
            warnings.append("Portion plate prolongee detectee: verifier capteur, cable ou saturation")

        peak_frequency = float(spectral["peak_frequency"])
        samples_per_peak_period = sample_rate / peak_frequency if peak_frequency > 0 else 0.0
        record_cycles_at_peak = len(original) * peak_frequency / sample_rate
        peak_resolution_ratio = (
            float(spectral["frequency_resolution"]) / peak_frequency if peak_frequency > 0 else 0.0
        )
        analysis_band = spectral["analysis_band_hz"]
        boundary_tolerance = float(spectral["frequency_resolution"]) * 0.51
        peak_at_band_boundary = bool(
            peak_frequency > 0
            and (
                abs(peak_frequency - float(analysis_band[0])) <= boundary_tolerance
                or abs(peak_frequency - float(analysis_band[1])) <= boundary_tolerance
            )
        )
        if peak_at_band_boundary:
            warnings.append(
                "Pic spectral sur une limite de bande: Tp à confirmer par l’ingénieur; "
                "ajuster la bande d'analyse"
            )
        if peak_frequency > 0 and samples_per_peak_period < 10.0:
            warnings.append("Moins de dix echantillons par periode de pic: resolution temporelle faible")
        if peak_frequency > 0 and record_cycles_at_peak < 10.0:
            warnings.append(
                "Moins de dix periodes de pic enregistrees: duree insuffisante pour une PSD stable"
            )

        time_axis = np.arange(len(original), dtype=np.float64) / sample_rate
        trend_slope = float(np.polyfit(time_axis, original, 1)[0]) if len(original) > 1 else 0.0
        peak_period_reliable = bool(
            peak_frequency > 0
            and not peak_at_band_boundary
            and samples_per_peak_period >= 10.0
            and record_cycles_at_peak >= 10.0
        )
        critical = bool(np.ptp(original) == 0 or stationarity_ratio > 4.0 or flat_run_fraction >= 0.05)
        # This is deliberately a diagnostic severity, never an acceptance verdict.
        # Only the engineer can accept or reject a channel with knowledge of the
        # basin layout, probe position and expected local response.
        status = "critical" if critical else ("warning" if warnings else "nominal")
        return {
            "valid": not warnings,
            "status": status,
            "diagnostic_level": status,
            "engineer_decision": "pending",
            "warnings": warnings,
            "sample_count": int(len(original)),
            "duration_seconds": float(len(original) / sample_rate),
            "welch_segment_count": segment_count,
            "variance_time_domain": variance_time,
            "variance_spectral": variance_spectral,
            "spectral_to_time_variance_ratio": variance_ratio,
            "block_variance_ratio": stationarity_ratio,
            "longest_flat_run_samples": longest_flat_run,
            "longest_flat_run_fraction": flat_run_fraction,
            "samples_per_peak_period": samples_per_peak_period,
            "record_cycles_at_peak": record_cycles_at_peak,
            "peak_frequency_resolution_ratio": peak_resolution_ratio,
            "peak_at_analysis_band_boundary": peak_at_band_boundary,
            "peak_period_reliable": peak_period_reliable,
            "linear_trend_per_second": trend_slope,
        }

    @staticmethod
    def _longest_flat_run(values: np.ndarray, tolerance: float) -> int:
        """Return the longest run of numerically unchanged consecutive samples."""

        if len(values) == 0:
            return 0
        unchanged = np.abs(np.diff(values)) <= tolerance
        longest = 1
        current = 1
        for is_unchanged in unchanged:
            current = current + 1 if is_unchanged else 1
            longest = max(longest, current)
        return int(longest)

    @staticmethod
    def _basic_statistics(
        values: np.ndarray,
        sample_rate: float,
        unit: str,
    ) -> dict[str, Any]:
        standard_deviation = float(np.std(values))
        return {
            "unit": unit,
            "sample_count": int(len(values)),
            "duration_seconds": float(len(values) / sample_rate),
            "mean": float(np.mean(values)),
            "std": standard_deviation,
            "variance": float(np.var(values)),
            "median": float(np.median(values)),
            "min": float(np.min(values)),
            "max": float(np.max(values)),
            "peak_to_peak": float(np.ptp(values)),
            "rms": float(np.sqrt(np.mean(values**2))),
            "skewness": (
                float(stats.skew(values, bias=False)) if len(values) > 2 and standard_deviation > 0 else 0.0
            ),
            "kurtosis": (
                float(stats.kurtosis(values, fisher=True, bias=False))
                if len(values) > 3 and standard_deviation > 0
                else 0.0
            ),
        }

    def _welch_layout(self, sample_count: int) -> tuple[int, int, int]:
        nperseg = min(self.config.segment_length, sample_count)
        if nperseg < 8:
            raise WaveAnalysisError("Signal trop court pour l'analyse spectrale")
        noverlap = min(nperseg - 1, int(round(nperseg * self.config.overlap_ratio)))
        step = nperseg - noverlap
        segment_count = 1 + max(0, (sample_count - nperseg) // step)
        return nperseg, noverlap, segment_count

    def _frequency_mask(self, frequencies: np.ndarray, sample_rate: float) -> np.ndarray:
        upper = self.config.max_frequency or sample_rate / 2
        return (frequencies > 0) & (frequencies >= self.config.min_frequency) & (frequencies <= upper)

    @staticmethod
    def _spectral_moment(
        frequencies: np.ndarray,
        density: np.ndarray,
        order: int,
    ) -> float:
        weighted = density * np.power(frequencies, order)
        return WaveAnalyzer._integrate(weighted, frequencies)

    @staticmethod
    def _integrate(values: np.ndarray, coordinates: np.ndarray) -> float:
        if len(values) < 2:
            return 0.0
        widths = np.diff(coordinates)
        return float(np.sum((values[:-1] + values[1:]) * widths * 0.5))

    @staticmethod
    def _interpolated_peak(
        frequencies: np.ndarray,
        density: np.ndarray,
        peak_index: int,
    ) -> float:
        if peak_index <= 0 or peak_index >= len(density) - 1:
            return float(frequencies[peak_index])
        left, center, right = np.log(np.maximum(density[peak_index - 1 : peak_index + 2], 1e-300))
        denominator = left - 2 * center + right
        if denominator == 0:
            return float(frequencies[peak_index])
        offset = float(np.clip(0.5 * (left - right) / denominator, -1.0, 1.0))
        resolution = frequencies[1] - frequencies[0]
        return float(frequencies[peak_index] + offset * resolution)

    def _validate_series(self, values: np.ndarray) -> np.ndarray:
        series = np.asarray(values, dtype=np.float64)
        if series.ndim != 1:
            raise WaveAnalysisError("Chaque canal doit etre une serie unidimensionnelle")
        if len(series) < self.config.minimum_samples:
            raise WaveAnalysisError(
                f"Signal trop court: {len(series)} echantillons, minimum {self.config.minimum_samples}"
            )
        if not np.all(np.isfinite(series)):
            invalid_count = int(np.count_nonzero(~np.isfinite(series)))
            raise WaveAnalysisError(f"Signal contenant {invalid_count} valeur(s) NaN ou infinie(s)")
        return series
