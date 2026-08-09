"""Adaptateur physique MCC vers le contrat d'acquisition générique."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import numpy as np

from hrneowave.acquisition.daq_backend import (
    DaqBackend,
    DaqReadResult,
    detect_voltage_saturation,
)
from hrneowave.acquisition.mcc_daq_wrapper import MCCDAQ_USB1608FS, MCCRanges
from hrneowave.hardware.contracts import DeviceDescriptor, VoltageRange


class MccDaqBackend(DaqBackend):
    """Traduit le protocole de la MCC USB-1608FS vers le contrat commun."""

    name = "mcc_usb1608fs"

    _MCC_RANGES = {
        VoltageRange.BIPOLAR_1_V: MCCRanges.BIP1VOLTS,
        VoltageRange.BIPOLAR_2_V: MCCRanges.BIP2VOLTS,
        VoltageRange.BIPOLAR_5_V: MCCRanges.BIP5VOLTS,
        VoltageRange.BIPOLAR_10_V: MCCRanges.BIP10VOLTS,
    }

    def __init__(
        self,
        board_num: int,
        descriptor: DeviceDescriptor,
        daq_factory=MCCDAQ_USB1608FS,
    ) -> None:
        super().__init__(descriptor)
        self.board_num = int(board_num)
        self.daq = daq_factory()
        self._sample_index = 0

    def connect(self) -> None:
        if self.connected:
            return
        if not self.daq.initialize(self.board_num):
            raise RuntimeError(f"Impossible d'initialiser la carte MCC {self.board_num}")
        self.connected = True

    def start(
        self,
        sample_rate_hz: float,
        channels: Sequence[Any],
        chunk_size: int = 100,
    ) -> float:
        if not self.connected:
            raise RuntimeError("La carte doit être connectée et validée avant l'acquisition")
        self.configure_channels(channels)
        self.capabilities.validate(float(sample_rate_hz), len(self.channels))

        self.daq.clear_channels()
        for channel in self.channels:
            voltage_range = getattr(channel, "voltage_range", None)
            try:
                mcc_range = self._MCC_RANGES[voltage_range]
            except KeyError as exc:
                raise ValueError(
                    f"Plage non traduisible par le pilote MCC: {voltage_range}"
                ) from exc
            if not self.daq.configure_channel(
                int(channel.channel),
                mcc_range,
                getattr(channel, "label", ""),
                getattr(channel, "units", "V"),
            ):
                raise RuntimeError(f"Configuration MCC refusée sur le canal {channel.channel}")

        channel_numbers = [int(channel.channel) for channel in self.channels]
        if not self.daq.start_continuous_acquisition(
            low_chan=min(channel_numbers),
            high_chan=max(channel_numbers),
            rate=float(sample_rate_hz),
            buffer_size=max(int(chunk_size), 100),
        ):
            raise RuntimeError("Impossible de démarrer l'acquisition MCC")

        self.sample_rate_hz = float(self.daq.acquisition_config.rate)
        self._sample_index = 0
        self.started = True
        return self.sample_rate_hz

    def read(self, num_samples: int = 100) -> DaqReadResult | None:
        if not self.started or self.sample_rate_hz is None:
            raise RuntimeError("L'acquisition MCC n'est pas démarrée")
        raw_data = self.daq.wait_for_data(
            num_samples=int(num_samples),
            timeout=0.25,
        )
        if raw_data is None or raw_data.size == 0:
            return None
        sample_count = raw_data.shape[0]
        indices = self._sample_index + np.arange(sample_count, dtype=float)
        time_values = indices / self.sample_rate_hz
        self._sample_index += sample_count
        return DaqReadResult(
            raw_data=raw_data,
            time=time_values,
            sample_rate_hz=self.sample_rate_hz,
            backend_name=self.name,
            warnings=detect_voltage_saturation(raw_data, self.channels),
        )

    def status(self) -> dict[str, Any]:
        payload = self.daq.get_acquisition_status()
        payload.update(
            {
                "connected": self.connected,
                "device_key": self.descriptor.key,
                "driver_id": self.descriptor.driver_id,
                "vendor": self.descriptor.vendor,
                "model": self.descriptor.model,
            }
        )
        return payload

    def stop(self) -> None:
        if self.started:
            self.daq.stop_acquisition()
        super().stop()

    def close(self) -> None:
        self.daq.close()
        super().close()

    def metadata(self) -> dict[str, Any]:
        payload = super().metadata()
        payload["board_num"] = self.board_num
        return payload
