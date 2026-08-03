"""Metrological calibration primitives for CHNeoWave.

The active acquisition path stores raw voltages and physical values. This
module defines the reproducible conversion contract used between both domains:

    measured_voltage = sensitivity_v_per_unit * reference_physical + intercept
    physical_value = (raw_voltage - intercept) / sensitivity_v_per_unit

For compatibility with the existing session schema, ``offset_volts`` is stored
as ``-intercept`` and ``scale`` is currently fixed to 1.0.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

import numpy as np

CALIBRATION_VALID = "valid"
CALIBRATION_INVALID = "invalid"
HARDWARE_VALIDATION_PENDING = "pending_hardware"

CONVERSION_FORMULA = "physical = ((raw_voltage + offset_volts) * scale) / sensitivity_v_per_unit"


class CalibrationError(ValueError):
    """Raised when a calibration record cannot be scientifically accepted."""


@dataclass
class CalibrationPoint:
    """One reference point used by the calibration fit."""

    reference_value: float
    measured_voltage: float
    timestamp_utc: Optional[str] = None
    standard_uncertainty: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_mapping(cls, payload: Mapping[str, Any]) -> "CalibrationPoint":
        return cls(
            reference_value=float(payload["reference_value"]),
            measured_voltage=float(payload["measured_voltage"]),
            timestamp_utc=payload.get("timestamp_utc"),
            standard_uncertainty=(
                None
                if payload.get("standard_uncertainty") is None
                else float(payload["standard_uncertainty"])
            ),
        )


@dataclass
class CalibrationRecord:
    """Validated linear calibration record for one sensor/channel."""

    calibration_id: str
    sensor_id: str
    channel: int
    sensor_type: str
    physical_unit: str
    voltage_unit: str
    date_utc: str
    operator: str
    method: str
    reference_equipment: str
    points: List[CalibrationPoint]
    offset_volts: float
    scale: float
    sensitivity_v_per_unit: float
    intercept_volts: float
    r_squared: float
    residuals: List[float]
    residual_rms: float
    uncertainty: float
    reference_range: Tuple[float, float]
    measured_voltage_range: Tuple[float, float]
    validity_status: str
    validity_reason: str
    hardware_validation_status: str = HARDWARE_VALIDATION_PENDING

    @classmethod
    def fit_linear(
        cls,
        *,
        sensor_id: str,
        channel: int,
        sensor_type: str,
        physical_unit: str,
        points: Sequence[CalibrationPoint | Mapping[str, Any]],
        voltage_unit: str = "V",
        operator: str = "",
        method: str = "linear_least_squares_voltage_vs_physical",
        reference_equipment: str = "",
        date_utc: Optional[str] = None,
        calibration_id: Optional[str] = None,
        min_r_squared: float = 0.995,
        hardware_validation_status: str = HARDWARE_VALIDATION_PENDING,
    ) -> "CalibrationRecord":
        """Fit and validate a linear calibration record.

        Invalid records fail loudly. A channel must not become ``valid`` from a
        low-quality or under-specified fit.
        """

        normalized_points = _normalize_points(points)
        reference_values = np.asarray([point.reference_value for point in normalized_points], dtype=float)
        measured_volts = np.asarray([point.measured_voltage for point in normalized_points], dtype=float)

        _validate_fit_inputs(reference_values, measured_volts, min_r_squared)

        sensitivity, intercept = np.polyfit(reference_values, measured_volts, 1)
        sensitivity = float(sensitivity)
        intercept = float(intercept)
        if not math.isfinite(sensitivity) or not math.isfinite(intercept):
            raise CalibrationError("Calibration fit produced non-finite coefficients")
        if sensitivity <= 0:
            raise CalibrationError(
                "Calibration sensitivity must be positive in the current acquisition contract"
            )

        predicted_volts = sensitivity * reference_values + intercept
        residual_volts = measured_volts - predicted_volts
        ss_res = float(np.sum(residual_volts ** 2))
        ss_tot = float(np.sum((measured_volts - np.mean(measured_volts)) ** 2))
        r_squared = 1.0 if ss_tot == 0.0 else float(1.0 - ss_res / ss_tot)
        if not math.isfinite(r_squared):
            raise CalibrationError("Calibration R^2 is non-finite")
        if r_squared < min_r_squared:
            raise CalibrationError(
                f"Calibration R^2 too low: {r_squared:.12g} < {min_r_squared:.12g}"
            )

        predicted_physical = (measured_volts - intercept) / sensitivity
        residuals = predicted_physical - reference_values
        residual_rms = float(math.sqrt(float(np.mean(residuals ** 2))))
        dof = max(1, int(reference_values.size) - 2)
        uncertainty = float(math.sqrt(float(np.sum(residuals ** 2)) / dof))

        if date_utc is None:
            date_utc = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        if calibration_id is None:
            calibration_id = _make_calibration_id(sensor_id, channel, date_utc, normalized_points)

        return cls(
            calibration_id=calibration_id,
            sensor_id=str(sensor_id),
            channel=int(channel),
            sensor_type=str(sensor_type),
            physical_unit=str(physical_unit),
            voltage_unit=str(voltage_unit),
            date_utc=str(date_utc),
            operator=str(operator),
            method=str(method),
            reference_equipment=str(reference_equipment),
            points=list(normalized_points),
            offset_volts=float(-intercept),
            scale=1.0,
            sensitivity_v_per_unit=sensitivity,
            intercept_volts=intercept,
            r_squared=r_squared,
            residuals=[float(value) for value in residuals],
            residual_rms=residual_rms,
            uncertainty=uncertainty,
            reference_range=(float(np.min(reference_values)), float(np.max(reference_values))),
            measured_voltage_range=(float(np.min(measured_volts)), float(np.max(measured_volts))),
            validity_status=CALIBRATION_VALID,
            validity_reason="linear_fit_accepted",
            hardware_validation_status=str(hardware_validation_status),
        )

    def apply(self, raw_voltage: Any) -> np.ndarray:
        """Convert raw voltage values to physical values using this record."""
        if self.validity_status != CALIBRATION_VALID:
            raise CalibrationError(f"Calibration record is not valid: {self.validity_status}")
        if self.sensitivity_v_per_unit <= 0:
            raise CalibrationError("Calibration sensitivity must be positive")
        raw = np.asarray(raw_voltage, dtype=float)
        if not np.all(np.isfinite(raw)):
            raise CalibrationError("Raw voltage contains NaN/Inf")
        return ((raw + self.offset_volts) * self.scale) / self.sensitivity_v_per_unit

    @property
    def calibration_coefficients(self) -> Dict[str, float]:
        return {
            "offset_volts": float(self.offset_volts),
            "scale": float(self.scale),
            "sensitivity_v_per_unit": float(self.sensitivity_v_per_unit),
            "intercept_volts": float(self.intercept_volts),
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "calibration_id": self.calibration_id,
            "sensor_id": self.sensor_id,
            "channel": self.channel,
            "sensor_type": self.sensor_type,
            "physical_unit": self.physical_unit,
            "voltage_unit": self.voltage_unit,
            "date_utc": self.date_utc,
            "operator": self.operator,
            "method": self.method,
            "reference_equipment": self.reference_equipment,
            "points": [point.to_dict() for point in self.points],
            "offset_volts": self.offset_volts,
            "scale": self.scale,
            "sensitivity_v_per_unit": self.sensitivity_v_per_unit,
            "intercept_volts": self.intercept_volts,
            "r_squared": self.r_squared,
            "residuals": list(self.residuals),
            "residual_rms": self.residual_rms,
            "uncertainty": self.uncertainty,
            "reference_range": list(self.reference_range),
            "measured_voltage_range": list(self.measured_voltage_range),
            "validity_status": self.validity_status,
            "validity_reason": self.validity_reason,
            "hardware_validation_status": self.hardware_validation_status,
            "calibration_coefficients": self.calibration_coefficients,
            "conversion_formula": CONVERSION_FORMULA,
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "CalibrationRecord":
        points = [CalibrationPoint.from_mapping(item) for item in payload.get("points", [])]
        reference_range = payload.get("reference_range", (0.0, 0.0))
        voltage_range = payload.get("measured_voltage_range", (0.0, 0.0))
        return cls(
            calibration_id=str(payload["calibration_id"]),
            sensor_id=str(payload["sensor_id"]),
            channel=int(payload["channel"]),
            sensor_type=str(payload.get("sensor_type", "")),
            physical_unit=str(payload.get("physical_unit", "")),
            voltage_unit=str(payload.get("voltage_unit", "V")),
            date_utc=str(payload.get("date_utc", "")),
            operator=str(payload.get("operator", "")),
            method=str(payload.get("method", "")),
            reference_equipment=str(payload.get("reference_equipment", "")),
            points=points,
            offset_volts=float(payload["offset_volts"]),
            scale=float(payload.get("scale", 1.0)),
            sensitivity_v_per_unit=float(payload["sensitivity_v_per_unit"]),
            intercept_volts=float(payload.get("intercept_volts", -float(payload["offset_volts"]))),
            r_squared=float(payload["r_squared"]),
            residuals=[float(value) for value in payload.get("residuals", [])],
            residual_rms=float(payload.get("residual_rms", 0.0)),
            uncertainty=float(payload.get("uncertainty", 0.0)),
            reference_range=(float(reference_range[0]), float(reference_range[1])),
            measured_voltage_range=(float(voltage_range[0]), float(voltage_range[1])),
            validity_status=str(payload.get("validity_status", CALIBRATION_INVALID)),
            validity_reason=str(payload.get("validity_reason", "")),
            hardware_validation_status=str(
                payload.get("hardware_validation_status", HARDWARE_VALIDATION_PENDING)
            ),
        )

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, sort_keys=True)

    @classmethod
    def from_json(cls, payload: str) -> "CalibrationRecord":
        return cls.from_dict(json.loads(payload))

    def to_channel_metadata(self) -> Dict[str, Any]:
        return {
            "sensor_id": self.sensor_id,
            "channel": self.channel,
            "sensor_type": self.sensor_type,
            "physical_units": self.physical_unit,
            "voltage_units": self.voltage_unit,
            "calibration_id": self.calibration_id,
            "calibration_date": self.date_utc,
            "calibration_method": self.method,
            "calibration_uncertainty": self.uncertainty,
            "calibration_status": self.validity_status,
            "calibration_coefficients": self.calibration_coefficients,
            "conversion_formula": CONVERSION_FORMULA,
            "calibration_record": self.to_dict(),
            "hardware_validation_status": self.hardware_validation_status,
        }


def fit_linear_calibration(**kwargs: Any) -> CalibrationRecord:
    """Convenience wrapper for ``CalibrationRecord.fit_linear``."""
    return CalibrationRecord.fit_linear(**kwargs)


def _normalize_points(points: Sequence[CalibrationPoint | Mapping[str, Any]]) -> List[CalibrationPoint]:
    if len(points) < 2:
        raise CalibrationError("Calibration requires at least two reference points")
    normalized = []
    for item in points:
        if isinstance(item, CalibrationPoint):
            point = item
        else:
            point = CalibrationPoint.from_mapping(item)
        normalized.append(point)
    return normalized


def _validate_fit_inputs(reference_values: np.ndarray, measured_volts: np.ndarray, min_r_squared: float) -> None:
    if reference_values.size != measured_volts.size:
        raise CalibrationError("Reference and measured arrays must have the same length")
    if reference_values.size < 2:
        raise CalibrationError("Calibration requires at least two reference points")
    if not np.all(np.isfinite(reference_values)) or not np.all(np.isfinite(measured_volts)):
        raise CalibrationError("Calibration points contain NaN/Inf")
    if not math.isfinite(float(min_r_squared)) or not (0.0 <= min_r_squared <= 1.0):
        raise CalibrationError("min_r_squared must be in [0, 1]")

    reference_diffs = np.diff(reference_values)
    if not (np.all(reference_diffs > 0.0) or np.all(reference_diffs < 0.0)):
        raise CalibrationError("Reference values must be strictly monotonic")
    if float(np.ptp(reference_values)) <= 0.0:
        raise CalibrationError("Reference range must be non-zero")
    if float(np.ptp(measured_volts)) <= 0.0:
        raise CalibrationError("Measured voltage range must be non-zero")


def _make_calibration_id(
    sensor_id: str,
    channel: int,
    date_utc: str,
    points: Iterable[CalibrationPoint],
) -> str:
    payload = {
        "sensor_id": sensor_id,
        "channel": channel,
        "date_utc": date_utc,
        "points": [point.to_dict() for point in points],
    }
    digest = hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()
    return f"cal_ch{int(channel):02d}_{digest[:12]}"
