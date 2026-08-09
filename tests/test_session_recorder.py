from __future__ import annotations

import importlib.util
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

import numpy as np

from hrneowave.acquisition.acquisition_controller import (
    AcquisitionSession,
    MaritimeChannelConfig,
)
from hrneowave.acquisition.mcc_daq_wrapper import MCCRanges
from hrneowave.acquisition.session_recorder import (
    ContinuousHDF5Recorder,
    inspect_recording,
)

H5PY_AVAILABLE = importlib.util.find_spec("h5py") is not None


@unittest.skipUnless(H5PY_AVAILABLE, "h5py n'est pas installe dans cet environnement")
class ContinuousHDF5RecorderTests(unittest.TestCase):
    def test_writes_traceable_incremental_session(self):
        import h5py

        channels = [
            MaritimeChannelConfig(
                channel=0,
                sensor_type="wave_height",
                label="Sonde A",
                units="V",
                range_type=MCCRanges.BIP10VOLTS,
                physical_units="m",
                sensor_sensitivity=2.0,
                probe_position_m=0.0,
            ),
            MaritimeChannelConfig(
                channel=3,
                sensor_type="pressure",
                label="Pression B",
                units="V",
                range_type=MCCRanges.BIP5VOLTS,
                physical_units="hPa",
                sensor_sensitivity=0.01,
            ),
        ]
        session = AcquisitionSession(
            session_id="session_test",
            project_name="Bassin maritime",
            start_time=datetime.now(),
            sampling_rate=200.0,
            channels=channels,
            metadata={
                "selected_channels": [0, 3],
                "hardware_available": True,
                "water_depth_m": 0.8,
            },
        )

        raw_first = np.array([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]])
        raw_second = np.array([[7.0, 8.0], [9.0, 10.0]])
        processed_first = raw_first * np.array([0.5, 100.0])
        processed_second = raw_second * np.array([0.5, 100.0])

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "session.h5"
            recorder = ContinuousHDF5Recorder(flush_interval_seconds=0.001, chunk_samples=4)
            recorder.start(path, session)
            recorder.append(raw_first, processed_first)
            recorder.append(raw_second, processed_second)
            session.end_time = datetime.now()
            session.total_samples = 5
            recorder.finalize(
                session,
                {"errors": 0, "buffer_overruns": 0},
            )

            with h5py.File(path, "r") as handle:
                self.assertEqual(handle.attrs["recording_status"], "complete")
                self.assertEqual(handle.attrs["n_samples"], 5)
                self.assertEqual(handle["metadata/session"].attrs["sample_rate"], 200.0)
                self.assertEqual(handle["metadata/session"].attrs["water_depth_m"], 0.8)
                np.testing.assert_allclose(
                    handle["raw_voltage/channel_03"][:],
                    np.concatenate((raw_first[:, 1], raw_second[:, 1])),
                )
                np.testing.assert_allclose(
                    handle["acquisition_data/channel_00"][:],
                    np.concatenate((processed_first[:, 0], processed_second[:, 0])),
                )
                np.testing.assert_allclose(
                    handle["acquisition_data/time"][:],
                    np.arange(5) / 200.0,
                )
                self.assertEqual(
                    handle["metadata/channels/channel_03"].attrs["label"],
                    "Pression B",
                )
                self.assertEqual(
                    handle["metadata/channels/channel_03"].attrs["calibration_status"],
                    "unverified",
                )
                self.assertIn(
                    "conversion_formula",
                    handle["metadata/channels/channel_03"].attrs,
                )
                self.assertEqual(
                    handle["metadata/channels/channel_00"].attrs["probe_position_m"],
                    0.0,
                )

            inspection = inspect_recording(path)
            self.assertTrue(inspection["ok"])
            self.assertEqual(inspection["n_samples"], 5)
            self.assertEqual(inspection["n_channels"], 2)
            self.assertEqual(inspection["issues"], [])


if __name__ == "__main__":
    unittest.main()
