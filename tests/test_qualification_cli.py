from __future__ import annotations

from argparse import Namespace

import pytest

from scripts.qualify_hardware_session import _criteria


def _arguments(**overrides) -> Namespace:
    values = {
        "stage": None,
        "profile": "quick",
        "minimum_duration": None,
        "ignore_wall_clock": False,
    }
    values.update(overrides)
    return Namespace(**values)


def test_cli_stage_uses_the_formal_protocol_contract():
    criteria = _criteria(_arguments(stage="Q2"))

    assert criteria.protocol_id == "mcc_usb1608fs_q0_q4_v1"
    assert criteria.protocol_stage == "Q2"
    assert criteria.profile_name == "grounded_inputs"
    assert criteria.minimum_duration_seconds == 60.0
    assert criteria.required_channel_count == 2
    assert criteria.minimum_distinct_ranges == 2


def test_cli_refuses_to_weaken_a_formal_stage_duration():
    with pytest.raises(ValueError, match="ne peut pas modifier"):
        _criteria(_arguments(stage="Q4", minimum_duration=3.0))


def test_cli_refuses_to_remove_wall_clock_proof_from_a_formal_stage():
    with pytest.raises(ValueError, match="interdit"):
        _criteria(_arguments(stage="Q4", ignore_wall_clock=True))
