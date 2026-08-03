"""Canonical acquisition-session contract helpers.

This module keeps the scientific invariants shared by acquisition, export, and
post-processing: explicit sample rate, explicit time base, channel metadata, and
clear raw-vs-physical data separation.
"""

from __future__ import annotations

import json
import math
from typing import Any, Dict, Iterable, Mapping, Optional

from hrneowave.core.calibration import CONVERSION_FORMULA, HARDWARE_VALIDATION_PENDING

SCHEMA_VERSION = "1.0.0"
CLOCK_DOMAIN = "relative_monotonic_seconds"
DATA_KIND_PHYSICAL = "physical"
DATA_KIND_RAW = "raw"

SAMPLE_RATE_KEYS = (
    "sample_rate_hz",
    "sampling_rate_hz",
    "sample_rate",
    "sampling_rate",
    "fs",
    "Sample_Rate",
)

CSV_METADATA_COLUMNS = {
    "schema_version",
    "sample_rate_hz",
    "sampling_rate_hz",
    "sample_rate",
    "sampling_rate",
    "fs",
    "clock_domain",
    "data_kind",
    "dt_seconds",
    "duration_s",
    "n_samples",
    "time_start",
    "time_end",
    "warnings",
}


def _calibration_record_to_dict(value: Any) -> Optional[Dict[str, Any]]:
    if value is None:
        return None
    if hasattr(value, "to_dict"):
        return value.to_dict()
    if isinstance(value, Mapping):
        return dict(value)
    return None


def coerce_float(value: Any) -> Optional[float]:
    """Return a finite float if possible, otherwise None."""
    if value is None:
        return None
    if isinstance(value, bytes):
        value = value.decode("utf-8", errors="replace")
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return None
        if stripped.startswith("[") or stripped.startswith("{"):
            try:
                value = json.loads(stripped)
            except json.JSONDecodeError:
                value = stripped
        else:
            value = stripped
    if isinstance(value, (list, tuple)) and len(value) == 1:
        value = value[0]
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(numeric):
        return None
    return numeric


def extract_sample_rate(*containers: Optional[Mapping[str, Any]]) -> Optional[float]:
    """Extract a positive sample rate from known metadata keys."""
    for container in containers:
        if not container:
            continue
        for key in SAMPLE_RATE_KEYS:
            sample_rate = coerce_float(container.get(key))
            if sample_rate is not None and sample_rate > 0:
                return sample_rate
    return None


def require_sample_rate(*containers: Optional[Mapping[str, Any]]) -> float:
    """Extract a positive sample rate or fail loudly."""
    sample_rate = extract_sample_rate(*containers)
    if sample_rate is None:
        raise ValueError("Missing explicit sample rate in acquisition metadata")
    return sample_rate


def build_channel_metadata(channels: Iterable[Any]) -> list[Dict[str, Any]]:
    """Normalize channel configuration objects into serializable metadata."""
    channel_metadata = []
    for index, channel in enumerate(channels):
        channel_number = int(getattr(channel, "channel", index))
        range_type = getattr(channel, "range_type", "")
        range_name = getattr(range_type, "name", str(range_type))
        calibration_record = _calibration_record_to_dict(getattr(channel, "calibration_record", None))
        record_coefficients = {}
        if calibration_record:
            record_coefficients = calibration_record.get("calibration_coefficients") or {
                "offset_volts": calibration_record.get("offset_volts"),
                "scale": calibration_record.get("scale", 1.0),
                "sensitivity_v_per_unit": calibration_record.get("sensitivity_v_per_unit"),
                "intercept_volts": calibration_record.get("intercept_volts"),
            }
        calibration_status = (
            (calibration_record or {}).get("validity_status")
            or getattr(channel, "calibration_status", None)
            or "unverified"
        )
        calibration_id = (
            (calibration_record or {}).get("calibration_id")
            or getattr(channel, "calibration_id", None)
            or f"unverified_channel_{channel_number:02d}"
        )
        calibration_date = (calibration_record or {}).get("date_utc") or getattr(channel, "calibration_date", None)
        calibration_method = (
            (calibration_record or {}).get("method")
            or getattr(channel, "calibration_method", None)
            or "configured_coefficients"
        )
        calibration_uncertainty = (
            (calibration_record or {}).get("uncertainty")
            if calibration_record and (calibration_record or {}).get("uncertainty") is not None
            else getattr(channel, "calibration_uncertainty", None)
        )
        coefficients = record_coefficients or {
            "offset_volts": float(getattr(channel, "calibration_offset", 0.0)),
            "scale": float(getattr(channel, "calibration_scale", 1.0)),
            "sensitivity_v_per_unit": float(getattr(channel, "sensor_sensitivity", 1.0)),
        }
        channel_metadata.append({
            "channel": channel_number,
            "key": f"channel_{channel_number:02d}",
            "label": getattr(channel, "label", f"Channel {channel_number}"),
            "sensor_id": getattr(channel, "sensor_id", None) or f"sensor_channel_{channel_number:02d}",
            "sensor_type": getattr(channel, "sensor_type", "unknown"),
            "voltage_units": getattr(channel, "units", "V"),
            "physical_units": getattr(channel, "physical_units", ""),
            "range": range_name,
            "sensor_sensitivity": float(getattr(channel, "sensor_sensitivity", 1.0)),
            "calibration_offset": float(getattr(channel, "calibration_offset", 0.0)),
            "calibration_scale": float(getattr(channel, "calibration_scale", 1.0)),
            "calibration_id": calibration_id,
            "calibration_date": calibration_date,
            "calibration_method": calibration_method,
            "calibration_uncertainty": calibration_uncertainty,
            "calibration_status": calibration_status,
            "calibration_coefficients": coefficients,
            "conversion_formula": CONVERSION_FORMULA,
            "calibration_record": calibration_record,
            "hardware_validation_status": (calibration_record or {}).get(
                "hardware_validation_status",
                HARDWARE_VALIDATION_PENDING,
            ),
            "enabled": bool(getattr(channel, "enabled", True)),
        })
    return channel_metadata


def build_session_metadata(
    session: Any,
    *,
    hardware_available: bool,
    sample_count: Optional[int] = None,
) -> Dict[str, Any]:
    """Build session metadata shared by all export formats."""
    sample_rate = float(getattr(session, "sampling_rate"))
    n_samples = int(sample_count if sample_count is not None else getattr(session, "total_samples", 0))
    dt_seconds = 1.0 / sample_rate
    metadata = {
        "schema_version": SCHEMA_VERSION,
        "sample_rate_hz": sample_rate,
        "sample_rate": sample_rate,
        "sampling_rate": sample_rate,
        "dt_seconds": dt_seconds,
        "n_samples": n_samples,
        "duration_s": n_samples / sample_rate if n_samples > 0 else 0.0,
        "time_start": 0.0,
        "time_end": (n_samples - 1) * dt_seconds if n_samples > 0 else 0.0,
        "clock_domain": CLOCK_DOMAIN,
        "project_name": getattr(session, "project_name", ""),
        "session_id": getattr(session, "session_id", ""),
        "start_time": getattr(session, "start_time").isoformat(),
        "end_time": getattr(session, "end_time").isoformat()
        if getattr(session, "end_time", None)
        else None,
        "total_samples": int(getattr(session, "total_samples", 0)),
        "channels_count": len(getattr(session, "channels", [])),
        "hardware_available": bool(hardware_available),
        "hardware_validation_status": HARDWARE_VALIDATION_PENDING
        if not hardware_available
        else "hardware_available_unvalidated",
    }
    if getattr(session, "metadata", None):
        metadata.update(session.metadata)
    return metadata


def build_csv_metadata_row(
    sample_rate: float,
    data_kind: str = DATA_KIND_PHYSICAL,
    sample_count: Optional[int] = None,
) -> Dict[str, Any]:
    """Metadata columns repeated per CSV row for self-describing tabular export."""
    n_samples = int(sample_count or 0)
    dt_seconds = 1.0 / float(sample_rate)
    return {
        "schema_version": SCHEMA_VERSION,
        "sample_rate_hz": float(sample_rate),
        "dt_seconds": dt_seconds,
        "n_samples": n_samples,
        "duration_s": n_samples / float(sample_rate) if n_samples > 0 else 0.0,
        "time_start": 0.0,
        "time_end": (n_samples - 1) * dt_seconds if n_samples > 0 else 0.0,
        "clock_domain": CLOCK_DOMAIN,
        "data_kind": data_kind,
    }
