from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import numpy as np

from hrneowave.core.legacy_raw import (
    LegacyRawError,
    LegacyRawImportOptions,
    load_legacy_raw,
    read_legacy_raw_header,
)
from hrneowave.core.post_processor import PostProcessor


class LegacyRawTests(unittest.TestCase):
    @staticmethod
    def _write_raw(path: Path, rows: list[str] | None = None) -> None:
        path.write_text(
            "\r\n".join(
                [
                    "2.00000000000000E+0000",
                    "2",
                    "2",
                    "2.0  -0.5",
                    *(
                        rows
                        or [
                            "0  0.0  2.0",
                            "1  0.5  1.0",
                            "2  1.0  0.0",
                            "3  1.5  -1.0",
                        ]
                    ),
                ]
            )
            + "\r\n",
            encoding="ascii",
        )

    def test_header_and_calibrated_channels_are_traceable(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "campaign.raw"
            self._write_raw(path)

            header = read_legacy_raw_header(path)
            data = load_legacy_raw(
                path,
                LegacyRawImportOptions(
                    sensor_type="wave_height",
                    physical_unit="cm",
                    calibration_confirmed=True,
                ),
            )

            self.assertEqual(header.sample_rate_hz, 2.0)
            self.assertEqual(header.expected_sample_count, 4)
            self.assertEqual(data["channel_keys"], ["channel_00", "channel_01"])
            self.assertTrue(np.allclose(data["raw_channels"]["channel_00"], [0.0, 0.5, 1.0, 1.5]))
            self.assertTrue(np.allclose(data["channels"]["channel_00"], [0.0, 1.0, 2.0, 3.0]))
            self.assertTrue(np.allclose(data["channels"]["channel_01"], [-1.0, -0.5, 0.0, 0.5]))
            self.assertEqual(data["metadata"]["sample_rate_hz"], 2.0)
            self.assertEqual(data["metadata"]["duration_s"], 2.0)
            self.assertEqual(data["channel_metadata"][0]["physical_unit"], "cm")
            self.assertEqual(data["channel_metadata"][0]["calibration_status"], "valid")
            self.assertEqual(len(data["metadata"]["source_sha256"]), 64)

    def test_post_processor_requires_explicit_raw_interpretation(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "campaign.raw"
            self._write_raw(path)
            processor = PostProcessor()

            self.assertFalse(processor.load_data_file(str(path)))
            self.assertTrue(
                processor.load_data_file(
                    str(path),
                    raw_options=LegacyRawImportOptions(
                        sensor_type="wave_height",
                        physical_unit="cm",
                        calibration_confirmed=True,
                    ),
                )
            )
            self.assertEqual(processor.sample_rate, 2.0)

    def test_rejects_missing_sample_or_discontinuous_index(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "incomplete.raw"
            self._write_raw(path, ["0 0 0", "1 0 0", "2 0 0"])
            options = LegacyRawImportOptions(
                sensor_type="wave_height",
                physical_unit="cm",
                calibration_confirmed=True,
            )
            with self.assertRaisesRegex(LegacyRawError, "incomplet"):
                load_legacy_raw(path, options)

            self._write_raw(path, ["0 0 0", "1 0 0", "3 0 0", "4 0 0"])
            with self.assertRaisesRegex(LegacyRawError, "indices"):
                load_legacy_raw(path, options)

    def test_rejects_trailing_garbage_in_calibration_header(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "invalid-header.raw"
            self._write_raw(path)
            payload = path.read_text(encoding="ascii").replace("2.0  -0.5", "2.0 -0.5 garbage")
            path.write_text(payload, encoding="ascii")

            with self.assertRaisesRegex(LegacyRawError, "coefficients"):
                read_legacy_raw_header(path)


if __name__ == "__main__":
    unittest.main()
