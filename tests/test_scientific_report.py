from __future__ import annotations

from hrneowave.core.scientific_report import (
    build_scientific_report_html,
    build_scientific_report_text,
)


def _results() -> dict:
    return {
        "sample_rate": 32.0,
        "metadata": {
            "sample_rate_hz": 32.0,
            "dt_seconds": 0.03125,
            "n_samples": 69120,
            "duration_s": 2160.0,
            "source_n_samples": 69120,
            "source_duration_s": 2160.0,
            "analysis_start_s": 0.0,
            "analysis_end_s": 2160.0,
        },
        "analysis_configuration": {
            "method": "Welch PSD + zero-upcrossing",
            "method_version": "1.2",
            "window": "hann",
            "segment_length": 1024,
            "overlap_ratio": 0.5,
            "detrend": True,
            "min_frequency": 0.0,
            "max_frequency": 16.0,
        },
        "channel_metadata": {
            "channel_08": {"physical_unit": "cm", "sensor_type": "wave_height"}
        },
        "basic_stats": {
            "channel_08": {
                "sample_count": 69120,
                "mean": 0.0,
                "std": 1.0,
                "rms": 1.0,
                "min": -2.0,
                "max": 2.0,
            }
        },
        "spectral_analysis": {
            "channel_08": {
                "peak_frequency": 0.03125,
                "peak_period": 32.0,
                "Hm0": 4.0,
                "Tm01": 5.0,
                "Tm02": 4.8,
                "Te": 5.2,
                "frequency_resolution": 0.03125,
                "segment_count": 134,
                "equivalent_degrees_of_freedom_approx": 268,
                "spectral_moments": {"m_1": 5.2, "m0": 1.0, "m1": 0.2, "m2": 0.0434, "m4": 0.003},
            }
        },
        "wave_parameters": {
            "channel_08": {"Tp": 32.0, "H1_3": 3.8, "H_max": 5.0, "n_waves": 300}
        },
        "quality": {
            "channel_08": {
                "status": "warning",
                "peak_period_reliable": False,
                "warnings": ["Pic spectral sur une limite de bande: Tp non fiable"],
                "spectral_to_time_variance_ratio": 1.0,
                "block_variance_ratio": 1.1,
            }
        },
        "cross_spectral_analysis": {},
        "incident_reflected_analysis": {"status": "not_configured", "reason": "géométrie absente"},
    }


def test_report_marks_unreliable_peak_and_documents_method():
    text = build_scientific_report_text(_results(), None)

    assert "Tp=NON FIABLE" in text
    assert "Welch PSD + zero-upcrossing" in text
    assert "moments intégrés" in text
    assert "DDL≈268" in text
    assert "LIMITES ET INTERPRÉTATION" in text


def test_html_report_contains_scientific_sections_and_plot():
    rendered = build_scientific_report_html(
        _results(),
        None,
        report_config={"title": "Essai Djendjen"},
        spectral_plot_data_uri="data:image/png;base64,AAAA",
    )

    assert "Essai Djendjen" in rendered
    assert "TRAÇABILITÉ DE LA SOURCE" in rendered
    assert "Figure spectrale" in rendered
    assert "data:image/png;base64,AAAA" in rendered
