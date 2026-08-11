from __future__ import annotations

import json

import pytest

from hrneowave.acquisition import (
    GENERIC_DAQ_PROTOCOL,
    MCC_USB1608FS_PROTOCOL,
    HardwareQualificationProtocol,
    QualificationHistoryStore,
    QualificationStage,
    build_default_qualification_protocol_registry,
    device_identity,
)
from hrneowave.acquisition.acquisition_controller import MaritimeChannelConfig
from hrneowave.hardware import VoltageRange
from tests.hardware_test_doubles import physical_test_device


def _channel(channel: int, voltage_range: VoltageRange) -> MaritimeChannelConfig:
    return MaritimeChannelConfig(
        channel=channel,
        sensor_type="generic",
        label=f"Voie {channel}",
        voltage_range=voltage_range,
    )


def test_registry_selects_mcc_protocol_without_coupling_generic_devices():
    registry = build_default_qualification_protocol_registry()
    mcc = {
        "hardware_driver_id": "mcc.universal_library.usb1608fs",
        "hardware_model": "USB-1608FS",
    }

    assert registry.resolve(mcc) is MCC_USB1608FS_PROTOCOL
    assert registry.resolve(physical_test_device()) is GENERIC_DAQ_PROTOCOL


def test_q2_requires_two_channels_two_ranges_and_100_hz():
    stage = MCC_USB1608FS_PROTOCOL.stage("Q2")

    assert stage.validate_setup(
        [_channel(0, VoltageRange.BIPOLAR_10_V)],
        100.0,
    ) == (
        "2 voie(s) active(s) requise(s), 1 configurée(s)",
        "2 plage(s) électrique(s) distincte(s) requise(s)",
    )
    assert stage.validate_setup(
        [
            _channel(0, VoltageRange.BIPOLAR_10_V),
            _channel(1, VoltageRange.BIPOLAR_5_V),
        ],
        100.0,
    ) == ()
    assert stage.validate_setup(
        [
            _channel(0, VoltageRange.BIPOLAR_10_V),
            _channel(1, VoltageRange.BIPOLAR_5_V),
        ],
        200.0,
    ) == ("fréquence requise: 100 Hz",)


def test_stage_builds_traceable_generic_criteria():
    stage = MCC_USB1608FS_PROTOCOL.stage("Q3")

    criteria = stage.criteria(MCC_USB1608FS_PROTOCOL.protocol_id)

    assert criteria.protocol_id == "mcc_usb1608fs_q0_q4_v1"
    assert criteria.protocol_stage == "Q3"
    assert criteria.profile_name == "grounded_inputs"
    assert criteria.minimum_duration_seconds == 600.0
    assert criteria.required_channel_count == 8
    assert criteria.require_protocol_attestation


def test_protocol_rejects_forward_or_circular_prerequisites():
    first = QualificationStage(
        "P0",
        "Premier",
        "Premier palier",
        "quick_functional",
        1.0,
        1,
        prerequisites=("P1",),
    )
    second = QualificationStage(
        "P1",
        "Second",
        "Second palier",
        "quick_functional",
        1.0,
        1,
        prerequisites=("P0",),
    )

    with pytest.raises(ValueError, match="paliers précédents"):
        HardwareQualificationProtocol("invalid", "Invalide", "", (first, second))


def test_history_tracks_only_accepted_stages_for_same_device(tmp_path):
    device = {
        "driver_id": "mcc.universal_library.usb1608fs",
        "model": "USB-1608FS",
        "serial_number": "SN-001",
    }
    report_device = {
        "driver_id": device["driver_id"],
        "model": device["model"],
        "serial_number": device["serial_number"],
    }
    for stage, verdict in (("Q0", "accepted"), ("Q1", "refused")):
        payload = {
            "qualification_id": f"id-{stage}",
            "evaluated_at_utc": f"2026-08-09T12:0{stage[-1]}:00+00:00",
            "verdict": verdict,
            "profile_name": "quick_functional",
            "source_master_file": f"session-{stage}.h5",
            "source_sha256": "a" * 64,
            "criteria": {
                "protocol_id": MCC_USB1608FS_PROTOCOL.protocol_id,
                "protocol_stage": stage,
            },
            "device": report_device,
            "summary": {"checks_passed": 10, "checks_total": 11},
        }
        (tmp_path / f"{stage}_qualification.json").write_text(
            json.dumps(payload),
            encoding="utf-8",
        )
    (tmp_path / "broken_qualification.json").write_text("{", encoding="utf-8")

    scan = QualificationHistoryStore().scan(tmp_path)
    accepted = QualificationHistoryStore.accepted_stage_ids(
        scan.entries,
        MCC_USB1608FS_PROTOCOL,
        device,
    )

    assert accepted == frozenset({"Q0"})
    assert len(scan.entries) == 2
    assert len(scan.errors) == 1
    assert QualificationHistoryStore.is_stage_unlocked(
        MCC_USB1608FS_PROTOCOL.stage("Q1"),
        accepted,
    )
    assert not QualificationHistoryStore.is_stage_unlocked(
        MCC_USB1608FS_PROTOCOL.stage("Q2"),
        accepted,
    )
    assert device_identity(device) == "mcc.universal_library.usb1608fs|USB-1608FS|SN-001"
