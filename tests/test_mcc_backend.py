from __future__ import annotations

import unittest
from enum import IntEnum, IntFlag
from types import SimpleNamespace

import numpy as np

from hrneowave.acquisition.mcc_daq_wrapper import (
    MCCDAQ_USB1608FS,
    MCCBackendError,
    MCCRanges,
    MccUsbDeviceInfo,
)


class FakeScanOptions(IntFlag):
    BACKGROUND = 1
    CONTINUOUS = 2
    SCALEDATA = 4
    SINGLEIO = 8
    CONVERTDATA = 16


class FakeULRange(IntEnum):
    BIP10VOLTS = 10
    BIP5VOLTS = 5
    BIP2VOLTS = 2
    BIP1VOLTS = 1


class FakeFunctionType(IntEnum):
    AIFUNCTION = 1


class FakeUL:
    def __init__(self):
        self.buffers = {}
        self.next_handle = 1
        self.active_handle = None
        self.current_count = 0
        self.queue = None
        self.scan_options = None
        self.stopped = False
        self.direct_mode_calls = 0
        self.created_devices = {}

    def ignore_instacal(self):
        self.direct_mode_calls += 1

    def get_daq_device_inventory(self, interface_type):
        return [SimpleNamespace(product_name="USB-1608FS", unique_id="TEST-1608")]

    def create_daq_device(self, board_num, device):
        if board_num in self.created_devices:
            raise RuntimeError("device already created")
        self.created_devices[board_num] = device

    def get_board_name(self, board_num):
        if board_num == 0:
            return "USB-1608FS"
        raise RuntimeError("board not configured")

    def a_load_queue(self, board_num, channels, gains, count):
        self.queue = (board_num, list(channels), list(gains), count)

    def scaled_win_buf_alloc(self, count):
        handle = self.next_handle
        self.next_handle += 1
        self.buffers[handle] = np.zeros(count, dtype=np.uint16)
        return handle

    win_buf_alloc = scaled_win_buf_alloc

    def a_in_scan(self, board_num, low, high, count, rate, gain, handle, options):
        self.active_handle = handle
        self.current_count = 0
        self.scan_options = options
        return rate

    def feed(self, values):
        buffer = self.buffers[self.active_handle]
        for value in values:
            buffer[self.current_count % len(buffer)] = float(value)
            self.current_count += 1

    def get_status(self, board_num, function_type):
        buffer = self.buffers[self.active_handle]
        index = (self.current_count - 1) % len(buffer) if self.current_count else 0
        return 1, self.current_count, index

    def scaled_win_buf_to_array(self, handle, destination, start, count):
        source = self.buffers[handle]
        for index in range(count):
            destination[index] = source[start + index]

    win_buf_to_array = scaled_win_buf_to_array

    def to_eng_units(self, board_num, ul_range, value):
        return float(value)

    def stop_background(self, board_num, function_type):
        self.stopped = True

    def win_buf_free(self, handle):
        self.buffers.pop(handle, None)


def fake_api():
    ul = FakeUL()
    return SimpleNamespace(
        ul=ul,
        FunctionType=FakeFunctionType,
        ScanOptions=FakeScanOptions,
        ULRange=FakeULRange,
        InterfaceType=SimpleNamespace(ANY=0),
    )


class MCCBackendTests(unittest.TestCase):
    def setUp(self):
        self.api = fake_api()
        self.backend = MCCDAQ_USB1608FS(api=self.api)
        self.assertTrue(self.backend.initialize(0))
        self.assertTrue(self.backend.configure_channel(0, MCCRanges.BIP10VOLTS, "Houle 1"))
        self.assertTrue(self.backend.configure_channel(2, MCCRanges.BIP2VOLTS, "Pression"))

    def tearDown(self):
        self.backend.close()

    def test_detects_direct_usb_board_without_instacal_configuration(self):
        devices = MCCDAQ_USB1608FS.detect_devices(api=self.api)
        self.assertEqual(
            devices,
            [MccUsbDeviceInfo(0, "USB-1608FS", "TEST-1608")],
        )
        self.assertEqual(self.api.ul.direct_mode_calls, 1)

        # Un nouveau scan reutilise le mode direct et la carte deja creee.
        self.assertEqual(MCCDAQ_USB1608FS.detect_boards(api=self.api), [0])
        self.assertEqual(self.api.ul.direct_mode_calls, 1)

    def test_uses_channel_gain_queue(self):
        self.assertTrue(
            self.backend.start_continuous_acquisition(0, 2, rate=1000, buffer_size=4)
        )
        _, channels, gains, count = self.api.ul.queue
        self.assertEqual(channels, list(range(8)))
        self.assertEqual(
            gains,
            [
                FakeULRange.BIP10VOLTS,
                FakeULRange.BIP10VOLTS,
                FakeULRange.BIP2VOLTS,
                FakeULRange.BIP10VOLTS,
                FakeULRange.BIP10VOLTS,
                FakeULRange.BIP10VOLTS,
                FakeULRange.BIP10VOLTS,
                FakeULRange.BIP10VOLTS,
            ],
        )
        self.assertEqual(count, 8)
        self.assertTrue(self.api.ul.scan_options & FakeScanOptions.SINGLEIO)
        self.assertTrue(self.api.ul.scan_options & FakeScanOptions.CONVERTDATA)
        self.assertFalse(self.api.ul.scan_options & FakeScanOptions.SCALEDATA)

    def test_reads_only_new_points_and_handles_wrap(self):
        self.assertTrue(
            self.backend.start_continuous_acquisition(0, 2, rate=1000, buffer_size=4)
        )
        first_scans = np.array([np.arange(8), np.arange(10, 18), np.arange(20, 28)])
        self.api.ul.feed(first_scans.ravel())
        first = self.backend.get_data(3)
        np.testing.assert_array_equal(first, [[0, 2], [10, 12], [20, 22]])
        self.assertIsNone(self.backend.get_data(1))

        second_scans = np.array([np.arange(30, 38), np.arange(40, 48), np.arange(50, 58)])
        self.api.ul.feed(second_scans.ravel())
        second = self.backend.get_data(3)
        np.testing.assert_array_equal(second, [[30, 32], [40, 42], [50, 52]])

    def test_detects_buffer_overrun(self):
        self.assertTrue(
            self.backend.start_continuous_acquisition(0, 2, rate=1000, buffer_size=2)
        )
        self.api.ul.feed(range(24))
        with self.assertRaises(MCCBackendError):
            self.backend.get_data(1)
        self.assertEqual(self.backend.buffer_overruns, 1)

    def test_rejects_rate_above_classic_aggregate_limit(self):
        self.assertFalse(
            self.backend.start_continuous_acquisition(
                0,
                2,
                rate=12501,
                buffer_size=4,
            )
        )
        self.assertIsNone(self.api.ul.active_handle)

    def test_unwraps_signed_32_bit_point_counter_rollover(self):
        self.assertEqual(self.backend._unwrap_point_counter(2_147_483_647), 2_147_483_647)
        self.assertEqual(self.backend._unwrap_point_counter(-2_147_483_648), 2_147_483_648)
        self.assertEqual(self.backend._unwrap_point_counter(-1), 4_294_967_295)
        self.assertEqual(self.backend._unwrap_point_counter(0), 4_294_967_296)


if __name__ == "__main__":
    unittest.main()
