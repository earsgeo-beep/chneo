import json
import unittest

import numpy as np

from hrneowave.acquisition.acquisition_controller import AcquisitionController, create_default_maritime_config
from hrneowave.core.calibration import (
    CALIBRATION_VALID,
    CONVERSION_FORMULA,
    CalibrationError,
    CalibrationPoint,
    CalibrationRecord,
)
from hrneowave.core.session_schema import build_channel_metadata


class CalibrationP1Tests(unittest.TestCase):
    def _build_record(self) -> CalibrationRecord:
        points = [
            CalibrationPoint(reference_value=0.0, measured_voltage=0.2),
            CalibrationPoint(reference_value=1.0, measured_voltage=2.2),
            CalibrationPoint(reference_value=2.0, measured_voltage=4.2),
            CalibrationPoint(reference_value=3.0, measured_voltage=6.2),
        ]
        return CalibrationRecord.fit_linear(
            sensor_id="WP-001",
            channel=0,
            sensor_type="wave_height",
            physical_unit="m",
            points=points,
            operator="metrology",
            reference_equipment="water_level_reference",
            date_utc="2026-04-26T00:00:00+00:00",
            calibration_id="cal_test_wp_001",
        )

    def test_linear_calibration_record_recovers_coefficients_and_applies_physical_conversion(self):
        record = self._build_record()

        self.assertEqual(record.validity_status, CALIBRATION_VALID)
        self.assertEqual(record.calibration_id, "cal_test_wp_001")
        self.assertAlmostEqual(record.sensitivity_v_per_unit, 2.0, places=12)
        self.assertAlmostEqual(record.intercept_volts, 0.2, places=12)
        self.assertAlmostEqual(record.offset_volts, -0.2, places=12)
        self.assertAlmostEqual(record.r_squared, 1.0, places=12)
        self.assertTrue(np.allclose(record.apply(np.array([0.2, 2.2, 4.2])), [0.0, 1.0, 2.0]))

    def test_calibration_requires_at_least_two_points(self):
        with self.assertRaises(CalibrationError):
            CalibrationRecord.fit_linear(
                sensor_id="WP-001",
                channel=0,
                sensor_type="wave_height",
                physical_unit="m",
                points=[CalibrationPoint(reference_value=0.0, measured_voltage=0.2)],
            )

    def test_calibration_rejects_non_monotonic_reference_values(self):
        with self.assertRaises(CalibrationError):
            CalibrationRecord.fit_linear(
                sensor_id="WP-001",
                channel=0,
                sensor_type="wave_height",
                physical_unit="m",
                points=[
                    CalibrationPoint(reference_value=0.0, measured_voltage=0.2),
                    CalibrationPoint(reference_value=2.0, measured_voltage=4.2),
                    CalibrationPoint(reference_value=1.0, measured_voltage=2.2),
                ],
            )

    def test_calibration_rejects_low_r_squared(self):
        with self.assertRaises(CalibrationError):
            CalibrationRecord.fit_linear(
                sensor_id="WP-001",
                channel=0,
                sensor_type="wave_height",
                physical_unit="m",
                min_r_squared=0.99,
                points=[
                    CalibrationPoint(reference_value=0.0, measured_voltage=0.0),
                    CalibrationPoint(reference_value=1.0, measured_voltage=1.0),
                    CalibrationPoint(reference_value=2.0, measured_voltage=0.0),
                    CalibrationPoint(reference_value=3.0, measured_voltage=1.0),
                ],
            )

    def test_calibration_record_round_trips_json_without_losing_metrology(self):
        record = self._build_record()
        reloaded = CalibrationRecord.from_json(record.to_json())

        self.assertEqual(reloaded.calibration_id, record.calibration_id)
        self.assertEqual(reloaded.sensor_id, record.sensor_id)
        self.assertEqual(reloaded.validity_status, CALIBRATION_VALID)
        self.assertEqual(reloaded.hardware_validation_status, "pending_hardware")
        self.assertEqual(reloaded.calibration_coefficients, record.calibration_coefficients)
        self.assertTrue(np.allclose(reloaded.apply([0.2, 2.2]), [0.0, 1.0]))

    def test_acquisition_channel_uses_only_valid_calibration_record_for_valid_status(self):
        controller = AcquisitionController.__new__(AcquisitionController)
        controller.channels_config = {0: create_default_maritime_config()[0]}

        record = self._build_record()
        self.assertTrue(controller.apply_calibration_record(record))

        config = controller.channels_config[0]
        self.assertEqual(config.calibration_status, CALIBRATION_VALID)
        self.assertEqual(config.calibration_id, record.calibration_id)
        self.assertAlmostEqual(config.calibration_offset, record.offset_volts)
        self.assertAlmostEqual(config.sensor_sensitivity, record.sensitivity_v_per_unit)
        self.assertIsInstance(config.calibration_record, dict)

        metadata = build_channel_metadata([config])[0]
        self.assertEqual(metadata["calibration_status"], CALIBRATION_VALID)
        self.assertEqual(metadata["calibration_id"], record.calibration_id)
        self.assertEqual(metadata["conversion_formula"], CONVERSION_FORMULA)
        self.assertEqual(metadata["hardware_validation_status"], "pending_hardware")
        self.assertIn("calibration_record", metadata)

    def test_calibration_record_dict_is_json_serializable(self):
        record = self._build_record()
        payload = record.to_dict()

        json.dumps(payload)
        self.assertAlmostEqual(payload["calibration_coefficients"]["sensitivity_v_per_unit"], 2.0)
        self.assertEqual(payload["conversion_formula"], CONVERSION_FORMULA)


if __name__ == "__main__":
    unittest.main()
