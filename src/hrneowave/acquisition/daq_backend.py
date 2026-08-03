"""DAQ backend abstraction for software-only and hardware acquisition paths.

The goal is to keep acquisition science testable without an MCC board:

* ``SimulatedDaqBackend`` produces raw voltages from analytic physical signals.
* ``FileReplayBackend`` replays an existing validated acquisition file.
* ``MccDaqBackend`` adapts the current MCC wrapper without claiming field
  validation before real hardware tests.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence

import numpy as np

from hrneowave.core.session_schema import DATA_KIND_RAW, extract_sample_rate

from .mcc_daq_wrapper import MCCDAQ_USB1608FS

logger = logging.getLogger(__name__)

PENDING_HARDWARE = "pending_hardware"
HARDWARE_AVAILABLE_UNVALIDATED = "hardware_available_unvalidated"


@dataclass
class DaqReadResult:
    """One acquisition chunk returned by a DAQ backend."""

    raw_data: np.ndarray
    time: np.ndarray
    sample_rate_hz: float
    backend_name: str
    data_kind: str = DATA_KIND_RAW
    hardware_validation_status: str = PENDING_HARDWARE
    warnings: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.raw_data = np.asarray(self.raw_data, dtype=float)
        self.time = np.asarray(self.time, dtype=float)
        if self.raw_data.ndim != 2:
            raise ValueError("DAQ data must use shape [samples, channels]")
        if self.time.ndim != 1:
            raise ValueError("DAQ time axis must be one-dimensional")
        if self.raw_data.shape[0] != self.time.shape[0]:
            raise ValueError("DAQ time axis length does not match sample count")
        if self.sample_rate_hz <= 0:
            raise ValueError("DAQ sample_rate_hz must be positive")
        if not np.all(np.isfinite(self.raw_data)):
            raise ValueError("DAQ raw data contains NaN/Inf")
        if not np.all(np.isfinite(self.time)):
            raise ValueError("DAQ time axis contains NaN/Inf")
        if self.time.size > 1 and not np.all(np.diff(self.time) > 0.0):
            raise ValueError("DAQ time axis must be strictly monotonic")


class DaqBackend(ABC):
    """Small contract shared by all acquisition sources."""

    name = "daq_backend"
    is_hardware = False
    realtime = False
    hardware_validation_status = PENDING_HARDWARE

    def __init__(self) -> None:
        self.channels: List[Any] = []
        self.sample_rate_hz: Optional[float] = None
        self.started = False

    def configure_channels(self, channels: Sequence[Any]) -> None:
        self.channels = list(channels)

    @abstractmethod
    def start(self, sample_rate_hz: float, channels: Sequence[Any], chunk_size: int = 100) -> float:
        """Start acquisition and return the actual sample rate."""

    @abstractmethod
    def read(self, num_samples: int = 100) -> Optional[DaqReadResult]:
        """Return the next raw-voltage chunk, or None when no data remains."""

    def stop(self) -> None:
        self.started = False

    def close(self) -> None:
        self.stop()

    def metadata(self) -> Dict[str, Any]:
        return {
            "backend_name": self.name,
            "backend_is_hardware": bool(self.is_hardware),
            "hardware_validation_status": self.hardware_validation_status,
            "sample_rate_hz": self.sample_rate_hz,
        }


class SimulatedDaqBackend(DaqBackend):
    """Software DAQ backend that emits raw voltages from analytic signals."""

    name = "simulated"
    is_hardware = False
    realtime = False
    hardware_validation_status = PENDING_HARDWARE

    def __init__(self, seed: Optional[int] = None, realtime: bool = False) -> None:
        super().__init__()
        self.rng = np.random.default_rng(seed)
        self.realtime = bool(realtime)
        self._sample_index = 0
        self._channel_state: Dict[int, Dict[str, float]] = {}
        self._chunk_size = 100

    def start(self, sample_rate_hz: float, channels: Sequence[Any], chunk_size: int = 100) -> float:
        if sample_rate_hz <= 0:
            raise ValueError("sample_rate_hz must be positive")
        self.configure_channels(channels)
        if not self.channels:
            raise ValueError("SimulatedDaqBackend requires at least one channel")
        self.sample_rate_hz = float(sample_rate_hz)
        self._chunk_size = int(chunk_size)
        self._sample_index = 0
        self._channel_state = {}
        self.started = True
        return self.sample_rate_hz

    def read(self, num_samples: int = 100) -> Optional[DaqReadResult]:
        if not self.started or self.sample_rate_hz is None:
            raise RuntimeError("SimulatedDaqBackend is not started")
        sample_count = int(num_samples or self._chunk_size)
        if sample_count <= 0:
            raise ValueError("num_samples must be positive")

        sample_indices = np.arange(sample_count, dtype=float) + self._sample_index
        time_values = sample_indices / self.sample_rate_hz
        physical_data = self._generate_physical_signals(time_values)
        raw_data = self._physical_to_raw(physical_data)
        warnings = detect_voltage_saturation(raw_data, self.channels)
        self._sample_index += sample_count

        return DaqReadResult(
            raw_data=raw_data,
            time=time_values,
            sample_rate_hz=self.sample_rate_hz,
            backend_name=self.name,
            hardware_validation_status=self.hardware_validation_status,
            warnings=warnings,
        )

    def _generate_physical_signals(self, time_values: np.ndarray) -> np.ndarray:
        physical_data = np.zeros((time_values.size, len(self.channels)), dtype=float)
        for index, channel in enumerate(self.channels):
            channel_number = int(getattr(channel, "channel", index))
            sensor_type = getattr(channel, "sensor_type", "generic")
            state = self._channel_state.setdefault(channel_number, {})

            if sensor_type == "wave_height":
                frequency = state.setdefault("frequency", float(0.15 + self.rng.random() * 0.35))
                amplitude = state.setdefault("amplitude", float(0.3 + self.rng.random() * 0.7))
                phase = state.setdefault("phase", float(self.rng.random() * 2.0 * np.pi))
                signal = amplitude * np.sin(2.0 * np.pi * frequency * time_values + phase)
                noise = 0.02 * self.rng.normal(0.0, 1.0, time_values.size)
                physical_data[:, index] = signal + noise
            elif sensor_type == "pressure":
                phase = state.setdefault("phase", float(self.rng.random() * 2.0 * np.pi))
                signal = 10.0 * np.sin(2.0 * np.pi * 0.05 * time_values + phase)
                noise = 0.2 * self.rng.normal(0.0, 1.0, time_values.size)
                physical_data[:, index] = signal + noise
            elif sensor_type == "accelerometer":
                phase = state.setdefault("phase", float(self.rng.random() * 2.0 * np.pi))
                signal = 9.81 + 0.1 * np.sin(2.0 * np.pi * 2.0 * time_values + phase)
                noise = 0.02 * self.rng.normal(0.0, 1.0, time_values.size)
                physical_data[:, index] = signal + noise
            else:
                physical_data[:, index] = self.rng.normal(0.0, 0.1, time_values.size)

        return physical_data

    def _physical_to_raw(self, physical_data: np.ndarray) -> np.ndarray:
        raw_data = np.zeros_like(physical_data, dtype=float)
        for index, channel in enumerate(self.channels):
            sensitivity = float(getattr(channel, "sensor_sensitivity", 1.0))
            scale = float(getattr(channel, "calibration_scale", 1.0))
            offset = float(getattr(channel, "calibration_offset", 0.0))
            if sensitivity <= 0 or scale <= 0:
                raise ValueError(f"Invalid calibration coefficients for channel {getattr(channel, 'channel', index)}")
            raw_data[:, index] = (physical_data[:, index] * sensitivity / scale) - offset
        return raw_data


class FileReplayBackend(DaqBackend):
    """Replay a validated CHNeoWave CSV/JSON/HDF5 acquisition file."""

    name = "file_replay"
    is_hardware = False
    realtime = False
    hardware_validation_status = PENDING_HARDWARE

    def __init__(self, file_path: str, prefer_raw: bool = True, loop: bool = False) -> None:
        super().__init__()
        self.file_path = file_path
        self.prefer_raw = bool(prefer_raw)
        self.loop = bool(loop)
        self._matrix: Optional[np.ndarray] = None
        self._time: Optional[np.ndarray] = None
        self._position = 0
        self._source_channels: List[str] = []
        self._warnings: List[str] = []

    def start(self, sample_rate_hz: float, channels: Sequence[Any], chunk_size: int = 100) -> float:
        self.configure_channels(channels)
        self._load_file()
        if self.sample_rate_hz is None:
            raise ValueError("Replay file has no usable sample rate")
        if sample_rate_hz > 0:
            relative_error = abs(float(sample_rate_hz) - self.sample_rate_hz) / self.sample_rate_hz
            if relative_error > 0.01:
                raise ValueError(
                    f"Replay sample rate mismatch: requested={sample_rate_hz}, file={self.sample_rate_hz}"
                )
        self._position = 0
        self.started = True
        return self.sample_rate_hz

    def read(self, num_samples: int = 100) -> Optional[DaqReadResult]:
        if not self.started or self._matrix is None or self._time is None or self.sample_rate_hz is None:
            raise RuntimeError("FileReplayBackend is not started")
        if self._position >= self._matrix.shape[0]:
            if not self.loop:
                return None
            self._position = 0

        end = min(self._position + int(num_samples), self._matrix.shape[0])
        raw_data = self._matrix[self._position:end, :]
        time_values = self._time[self._position:end]
        self._position = end
        if raw_data.size == 0:
            return None

        return DaqReadResult(
            raw_data=raw_data,
            time=time_values,
            sample_rate_hz=self.sample_rate_hz,
            backend_name=self.name,
            hardware_validation_status=self.hardware_validation_status,
            warnings=list(self._warnings),
        )

    def _load_file(self) -> None:
        from hrneowave.core.post_processor import PostProcessor

        processor = PostProcessor()
        if not processor.load_data_file(self.file_path):
            raise ValueError(f"Unable to load replay file: {self.file_path}")

        data = processor.current_data or {}
        metadata = data.get("metadata", {})
        self.sample_rate_hz = extract_sample_rate(metadata, data.get("session", {}))
        if self.sample_rate_hz is None:
            raise ValueError("Replay file has no explicit sample rate")

        raw_channels = data.get("raw_channels", {}) or {}
        physical_channels = data.get("channels", {}) or {}
        if self.prefer_raw and raw_channels:
            selected_channels = raw_channels
        else:
            selected_channels = physical_channels
            if self.prefer_raw:
                self._warnings.append("FILE_REPLAY_USING_PHYSICAL_CHANNELS_AS_RAW")

        if not selected_channels:
            raise ValueError("Replay file contains no channels")

        self._source_channels = sorted(selected_channels.keys())
        channel_arrays = [np.asarray(selected_channels[key], dtype=float) for key in self._source_channels]
        lengths = {array.shape[0] for array in channel_arrays}
        if len(lengths) != 1:
            raise ValueError("Replay channels do not have the same length")
        self._matrix = np.column_stack(channel_arrays)
        self._time = np.asarray(data.get("time"), dtype=float)
        if self._time.shape[0] != self._matrix.shape[0]:
            raise ValueError("Replay time axis length does not match channels")

    def metadata(self) -> Dict[str, Any]:
        payload = super().metadata()
        payload.update({
            "file_path": self.file_path,
            "prefer_raw": self.prefer_raw,
            "loop": self.loop,
            "source_channels": list(self._source_channels),
        })
        return payload


class MccDaqBackend(DaqBackend):
    """Adapter around the existing MCC wrapper.

    This backend only means that the MCC API is available. Scientific field
    validation remains pending until P1-B is executed with real hardware.
    """

    name = "mcc_usb1608fs"
    is_hardware = True
    realtime = True
    hardware_validation_status = HARDWARE_AVAILABLE_UNVALIDATED

    def __init__(self, board_num: int = 0, dll_path: Optional[str] = None) -> None:
        super().__init__()
        self.board_num = int(board_num)
        self.daq = MCCDAQ_USB1608FS(dll_path=dll_path)

    def start(self, sample_rate_hz: float, channels: Sequence[Any], chunk_size: int = 100) -> float:
        if sample_rate_hz <= 0:
            raise ValueError("sample_rate_hz must be positive")
        self.configure_channels(channels)
        if not self.daq.initialize(self.board_num):
            raise RuntimeError(f"Unable to initialize MCC board {self.board_num}")

        for channel in self.channels:
            self.daq.configure_channel(
                int(getattr(channel, "channel")),
                getattr(channel, "range_type"),
                getattr(channel, "label", ""),
                getattr(channel, "units", "V"),
            )

        channel_numbers = [int(getattr(channel, "channel")) for channel in self.channels]
        if not self.daq.start_continuous_acquisition(
            low_chan=min(channel_numbers),
            high_chan=max(channel_numbers),
            rate=float(sample_rate_hz),
            buffer_size=max(int(chunk_size), 100),
        ):
            raise RuntimeError("Unable to start MCC acquisition")

        self.sample_rate_hz = float(self.daq.acquisition_config.rate)
        self.started = True
        return self.sample_rate_hz

    def read(self, num_samples: int = 100) -> Optional[DaqReadResult]:
        if not self.started or self.sample_rate_hz is None:
            raise RuntimeError("MccDaqBackend is not started")
        raw_data = self.daq.get_data(num_samples=int(num_samples))
        if raw_data is None or raw_data.size == 0:
            return None
        sample_count = raw_data.shape[0]
        time_values = np.arange(sample_count, dtype=float) / self.sample_rate_hz
        return DaqReadResult(
            raw_data=raw_data,
            time=time_values,
            sample_rate_hz=self.sample_rate_hz,
            backend_name=self.name,
            hardware_validation_status=self.hardware_validation_status,
            warnings=detect_voltage_saturation(raw_data, self.channels),
        )

    def stop(self) -> None:
        if self.started:
            self.daq.stop_acquisition()
        super().stop()

    def close(self) -> None:
        self.daq.close()
        super().close()

    def metadata(self) -> Dict[str, Any]:
        payload = super().metadata()
        payload["board_num"] = self.board_num
        return payload


def detect_voltage_saturation(
    raw_data: np.ndarray,
    channels: Sequence[Any],
    threshold: float = 0.999,
) -> List[str]:
    """Return warnings for channels close to their configured voltage range."""
    data = np.asarray(raw_data, dtype=float)
    warnings: List[str] = []
    if data.ndim != 2:
        raise ValueError("raw_data must use shape [samples, channels]")

    for index, channel in enumerate(channels):
        if index >= data.shape[1]:
            break
        limit = _channel_voltage_limit(channel)
        if limit is None or limit <= 0:
            continue
        max_abs = float(np.max(np.abs(data[:, index]))) if data.shape[0] else 0.0
        if max_abs >= limit * threshold:
            channel_number = getattr(channel, "channel", index)
            warnings.append(
                f"VOLTAGE_SATURATION_RISK: channel={channel_number}, max_abs={max_abs:.6g} V, range=+-{limit:g} V"
            )
    return warnings


def _channel_voltage_limit(channel: Any) -> Optional[float]:
    range_type = getattr(channel, "range_type", None)
    range_name = getattr(range_type, "name", str(range_type))
    limits = {
        "BIP10VOLTS": 10.0,
        "BIP5VOLTS": 5.0,
        "BIP2VOLTS": 2.0,
        "BIP1VOLTS": 1.0,
    }
    return limits.get(range_name)
