from __future__ import annotations

import hashlib
import json
from dataclasses import replace
from datetime import datetime, timedelta
from pathlib import Path

import h5py
import numpy as np

from hrneowave.acquisition import (
    AcquisitionSession,
    ContinuousHDF5Recorder,
    HardwareQualificationService,
    MaritimeChannelConfig,
    QualificationCriteria,
    QualificationReportWriter,
)
from hrneowave.acquisition.qualification_protocol import MCC_USB1608FS_PROTOCOL
from hrneowave.hardware import VoltageRange


def _record_session(
    path: Path,
    values: np.ndarray,
    *,
    sample_rate: float = 100.0,
    timing_discontinuities: int = 0,
    extra_metadata: dict | None = None,
) -> Path:
    raw = np.asarray(values, dtype=np.float64)
    if raw.ndim == 1:
        raw = raw[:, np.newaxis]
    channels = [
        MaritimeChannelConfig(
            channel=index,
            sensor_type="generic",
            label=f"Voie {index + 1}",
            voltage_range=VoltageRange.BIPOLAR_10_V,
            physical_units="V",
        )
        for index in range(raw.shape[1])
    ]
    elapsed = raw.shape[0] / sample_rate
    started = datetime(2026, 8, 9, 12, 0, 0)
    session = AcquisitionSession(
        session_id="qualification_fixture",
        project_name="Banc MCC",
        start_time=started,
        sampling_rate=sample_rate,
        channels=channels,
        metadata={
            "acquisition_source": "physical_hardware",
            "hardware_available": True,
            "hardware_driver_id": "mcc.universal_library",
            "hardware_device_id": "board-0",
            "hardware_vendor": "Measurement Computing",
            "hardware_model": "USB-1608FS",
            "hardware_serial_number": "TEST-SERIAL",
            "hardware_transport": "USB",
            "requested_sampling_rate": sample_rate,
            "actual_sampling_rate": sample_rate,
            "expected_samples": raw.shape[0],
            "acquisition_wall_elapsed_seconds": elapsed,
            "backend_time_start_seconds": 0.0,
            "backend_time_end_seconds": (raw.shape[0] - 1) / sample_rate,
            **dict(extra_metadata or {}),
        },
    )
    recorder = ContinuousHDF5Recorder(chunk_samples=32)
    recorder.start(path, session)
    recorder.append(raw, raw)
    session.end_time = started + timedelta(seconds=elapsed)
    session.total_samples = raw.shape[0]
    recorder.finalize(
        session,
        {
            "errors": 0,
            "buffer_overruns": 0,
            "recording_errors": 0,
            "timing_discontinuities": timing_discontinuities,
            "max_timing_error_seconds": 0.0,
            "backend_blocks": 2,
        },
    )
    return path


def _failed_checks(report) -> set[str]:
    return {check.code for check in report.checks if not check.passed}


def test_quick_profile_accepts_complete_physical_session(tmp_path):
    phase = np.linspace(0.0, 2.0 * np.pi, 100, endpoint=False)
    source = _record_session(tmp_path / "accepted.h5", 0.2 * np.sin(phase))

    report = HardwareQualificationService(chunk_samples=17).evaluate(
        source,
        QualificationCriteria.quick_functional(minimum_duration_seconds=1.0),
    )

    assert report.accepted
    assert _failed_checks(report) == set()
    assert report.device["model"] == "USB-1608FS"
    assert report.channels[0].sample_count == 100
    assert report.channels[0].saturation_count == 0


def test_quick_profile_refuses_saturation(tmp_path):
    source = _record_session(tmp_path / "saturated.h5", np.full(100, 9.999))

    report = HardwareQualificationService().evaluate(
        source,
        QualificationCriteria.quick_functional(minimum_duration_seconds=1.0),
    )

    assert not report.accepted
    assert "saturation" in _failed_checks(report)


def test_grounded_profile_applies_offset_and_noise_thresholds(tmp_path):
    rng = np.random.default_rng(1608)
    accepted_source = _record_session(
        tmp_path / "grounded_ok.h5",
        rng.normal(loc=0.001, scale=0.002, size=100),
    )
    refused_source = _record_session(
        tmp_path / "grounded_bad.h5",
        rng.normal(loc=0.2, scale=0.03, size=100),
    )
    criteria = QualificationCriteria.grounded_inputs(minimum_duration_seconds=1.0)

    accepted = HardwareQualificationService().evaluate(accepted_source, criteria)
    refused = HardwareQualificationService().evaluate(refused_source, criteria)

    assert accepted.accepted
    assert not refused.accepted
    assert {"ground_offset", "ground_noise_rms"} <= _failed_checks(refused)


def test_timing_discontinuity_refuses_session(tmp_path):
    source = _record_session(
        tmp_path / "timing_error.h5",
        np.zeros(100),
        timing_discontinuities=1,
    )

    report = HardwareQualificationService().evaluate(
        source,
        QualificationCriteria.quick_functional(minimum_duration_seconds=1.0),
    )

    assert not report.accepted
    assert {"recording_integrity", "timing_continuity"} <= _failed_checks(report)


def test_report_bundle_is_traceable_and_does_not_modify_master(tmp_path):
    source = _record_session(tmp_path / "source.h5", np.zeros(100))
    source_hash_before = hashlib.sha256(source.read_bytes()).hexdigest()
    report = HardwareQualificationService().evaluate(
        source,
        QualificationCriteria.quick_functional(minimum_duration_seconds=1.0),
    )

    json_path, hdf5_path = QualificationReportWriter().write_bundle(
        report,
        tmp_path / "reports",
    )

    assert hashlib.sha256(source.read_bytes()).hexdigest() == source_hash_before
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["source_sha256"] == source_hash_before
    assert payload["verdict"] == "accepted"
    with h5py.File(hdf5_path, "r") as handle:
        embedded = json.loads(handle["report_json"][()].decode("utf-8"))
        assert handle.attrs["source_sha256"] == source_hash_before
        assert embedded["qualification_id"] == report.qualification_id


def test_non_finite_corruption_produces_a_serializable_refusal(tmp_path):
    source = _record_session(tmp_path / "corrupted.h5", np.zeros(100))
    with h5py.File(source, "r+") as handle:
        handle["raw_voltage/channel_00"][:] = np.nan

    report = HardwareQualificationService().evaluate(
        source,
        QualificationCriteria.quick_functional(minimum_duration_seconds=1.0),
    )
    json_path, _ = QualificationReportWriter().write_bundle(report, tmp_path / "reports")

    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert not report.accepted
    assert "finite_values" in _failed_checks(report)
    assert payload["channels"][0]["mean_volts"] is None


def test_protocol_requirements_are_verified_again_from_master_file(tmp_path):
    source = _record_session(tmp_path / "q2_same_range.h5", np.zeros((100, 2)))
    criteria = replace(
        MCC_USB1608FS_PROTOCOL.stage("Q2").criteria(
            MCC_USB1608FS_PROTOCOL.protocol_id,
            check_wall_clock=False,
        ),
        minimum_duration_seconds=1.0,
    )

    report = HardwareQualificationService().evaluate(source, criteria)

    assert not report.accepted
    assert "protocol_distinct_ranges" in _failed_checks(report)
    assert "protocol_channel_count" not in _failed_checks(report)


def test_formal_stage_requires_and_accepts_operator_attestation(tmp_path):
    source = _record_session(
        tmp_path / "q0_attested.h5",
        np.zeros(100),
        extra_metadata={
            "qualification_intent": True,
            "qualification_protocol_id": MCC_USB1608FS_PROTOCOL.protocol_id,
            "qualification_stage": "Q0",
            "qualification_operator_checklist": ["Câblage contrôlé"],
            "qualification_checklist_confirmed_at": "2026-08-09T12:00:00+00:00",
        },
    )
    criteria = replace(
        MCC_USB1608FS_PROTOCOL.stage("Q0").criteria(
            MCC_USB1608FS_PROTOCOL.protocol_id,
            check_wall_clock=False,
        ),
        minimum_duration_seconds=1.0,
    )

    report = HardwareQualificationService().evaluate(source, criteria)
    json_path, hdf5_path = QualificationReportWriter().write_bundle(
        report,
        tmp_path / "formal_reports",
    )

    assert report.accepted
    assert "protocol_attestation" not in _failed_checks(report)
    assert "Q0" in json_path.name
    with h5py.File(hdf5_path, "r") as handle:
        assert handle.attrs["schema_version"] == "1.1.0"
        assert handle.attrs["protocol_stage"] == "Q0"
