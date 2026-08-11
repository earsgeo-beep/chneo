"""Backend MCC USB-1608FS base sur l'Universal Library officielle.

Le paquet :mod:`mcculw` est une fine couche Python au-dessus de l'Universal
Library installee avec InstaCal. Il ne requiert aucune connexion internet a
l'execution. Ce module conserve l'API historique de CHNeoWave tout en confiant
la gestion des buffers Windows a l'API MCC.
"""

from __future__ import annotations

import ctypes
import logging
import threading
import time
from dataclasses import dataclass
from enum import IntEnum
from types import SimpleNamespace
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)


def _enable_direct_discovery(api: Any) -> None:
    """Active le mode sans InstaCal exactement une fois par instance UL.

    MCC impose que ``ignore_instacal`` soit le premier appel Universal Library.
    Le marqueur est pose sur le module ``ul`` lui-meme afin qu'un nouveau scan
    dans le meme processus ne rappelle pas cette fonction trop tard.
    """

    marker = "_chneowave_direct_discovery_enabled"
    if getattr(api.ul, marker, False):
        return
    api.ul.ignore_instacal()
    setattr(api.ul, marker, True)


class MCCBackendError(RuntimeError):
    """Erreur d'acquisition MCC avec un message exploitable par l'interface."""


class MCCUniversalLibraryUnavailable(MCCBackendError):
    """L'Universal Library ou son paquet Python n'est pas disponible."""


class MCCErrorCodes(IntEnum):
    """Codes conserves pour compatibilite avec l'ancienne API."""

    NOERRORS = 0
    BADBOARD = 1
    BADCHANNEL = 15
    BADRANGE = 16


class MCCRanges(IntEnum):
    """Plages analogiques prises en charge par la MCC USB-1608FS."""

    BIP10VOLTS = 1
    BIP5VOLTS = 2
    BIP2VOLTS = 5
    BIP1VOLTS = 7

    @property
    def full_scale_volts(self) -> float:
        return {
            MCCRanges.BIP10VOLTS: 10.0,
            MCCRanges.BIP5VOLTS: 5.0,
            MCCRanges.BIP2VOLTS: 2.0,
            MCCRanges.BIP1VOLTS: 1.0,
        }[self]


class MCCOptions(IntEnum):
    """Anciennes options publiques conservees pour les imports existants."""

    DEFAULTOPTION = 0x0000
    CONTINUOUS = 0x0001
    BACKGROUND = 0x0002
    SCALEDATA = 0x0200


@dataclass(frozen=True)
class ChannelConfig:
    """Configuration d'une entree analogique."""

    channel: int
    range_type: MCCRanges
    enabled: bool = True
    label: str = ""
    units: str = "V"


@dataclass
class AcquisitionConfig:
    """Configuration effective du scan MCC."""

    board_num: int = 0
    low_chan: int = 0
    high_chan: int = 7
    rate: float = 1000.0
    count: int = 0
    n_channels: int = 0
    n_scan_channels: int = 0


@dataclass(frozen=True)
class MccUsbDeviceInfo:
    """Identité USB conservée après la création du numéro logique UL."""

    board_num: int
    product_name: str
    unique_id: str


def _load_mcc_api() -> SimpleNamespace:
    """Charge mcculw uniquement quand le backend materiel est utilise."""

    try:
        from mcculw import ul
        from mcculw.enums import FunctionType, InterfaceType, ScanOptions, ULRange
    except (ImportError, OSError) as exc:
        raise MCCUniversalLibraryUnavailable(
            "MCC Universal Library indisponible. Installer InstaCal/Universal Library "
            "puis le paquet Python mcculw depuis le kit hors ligne."
        ) from exc

    return SimpleNamespace(
        ul=ul,
        FunctionType=FunctionType,
        InterfaceType=InterfaceType,
        ScanOptions=ScanOptions,
        ULRange=ULRange,
    )


class MCCDAQ_USB1608FS:
    """Acquisition continue d'une MCC USB-1608FS decouverte directement en USB.

    ``api`` est injectable afin de tester toute la logique de buffer sans carte.
    En production, il est omis et le module charge l'Universal Library locale.
    """

    MAX_CHANNELS = 8
    MAX_AGGREGATE_RATE = 100_000.0
    SUPPORTED_RANGES = (
        MCCRanges.BIP10VOLTS,
        MCCRanges.BIP5VOLTS,
        MCCRanges.BIP2VOLTS,
        MCCRanges.BIP1VOLTS,
    )

    def __init__(self, api: Any | None = None):
        self._api = api
        self.board_num = 0
        self.board_name = ""
        self.is_initialized = False
        self.channels_config: dict[int, ChannelConfig] = {}
        self.acquisition_config = AcquisitionConfig()

        self._memhandle: int | None = None
        self._buffer_count = 0
        self._last_point_count = 0
        self._last_raw_counter: int | None = None
        self._counter_epoch = 0
        self._last_observed_point_count = 0
        self._sequence = 0
        self._running = False
        self._output_indices: list[int] = []
        self._output_ranges: list[Any] = []
        self._lock = threading.RLock()
        self.buffer_overruns = 0

    @property
    def api(self):
        if self._api is None:
            self._api = _load_mcc_api()
        return self._api

    @classmethod
    def detect_devices(
        cls,
        api: Any | None = None,
        max_boards: int = 10,
    ) -> list[MccUsbDeviceInfo]:
        """Detecte les cartes MCC connectees en USB.

        La detection utilise exclusivement l'inventaire USB de l'Universal
        Library. InstaCal et son fichier ``cb.cfg`` ne sont jamais consultes.
        """

        try:
            active_api = api or _load_mcc_api()
        except MCCUniversalLibraryUnavailable:
            return []

        detected: list[MccUsbDeviceInfo] = []
        try:
            _enable_direct_discovery(active_api)
            devices = active_api.ul.get_daq_device_inventory(
                active_api.InterfaceType.ANY
            )
            for dev in devices:
                product_name = str(getattr(dev, "product_name", "")).strip()
                if product_name.upper() != "USB-1608FS":
                    logger.info("Peripherique MCC ignore: %s", product_name or "inconnu")
                    continue
                if len(detected) >= max_boards:
                    break
                board_num = len(detected)
                unique_id = str(getattr(dev, "unique_id", "")).strip()
                try:
                    active_api.ul.create_daq_device(board_num, dev)
                    detected.append(
                        MccUsbDeviceInfo(board_num, product_name, unique_id)
                    )
                    logger.info(
                        "Carte MCC detectee (USB): %s (SN: %s) -> board %s",
                        dev.product_name,
                        dev.unique_id,
                        board_num,
                    )
                except Exception as exc:
                    # Un second scan peut retrouver une carte deja enregistree
                    # dans cette instance UL. Dans ce cas, on la reutilise.
                    try:
                        existing_name = active_api.ul.get_board_name(board_num)
                    except Exception:
                        existing_name = ""
                    if str(existing_name).strip().upper() == "USB-1608FS":
                        detected.append(
                            MccUsbDeviceInfo(board_num, product_name, unique_id)
                        )
                    else:
                        logger.debug("create_daq_device(%s) echoue: %s", board_num, exc)
        except Exception as exc:
            logger.error("Detection USB directe impossible: %s", exc)
        return detected

    @classmethod
    def detect_boards(cls, api: Any | None = None, max_boards: int = 10) -> list[int]:
        """Retourne les numéros logiques historiques après l'inventaire USB."""

        return [
            device.board_num
            for device in cls.detect_devices(api=api, max_boards=max_boards)
        ]

    def initialize(self, board_num: int = 0) -> bool:
        """Ouvre logiquement une carte MCC.

        La carte doit avoir ete creee par ``detect_boards``. Cette separation
        garantit que ``ignore_instacal`` reste le premier appel UL du processus.
        """

        try:
            board_name = ""
            try:
                board_name = self.api.ul.get_board_name(board_num)
            except Exception:
                pass

            if not board_name:
                raise MCCBackendError(
                    f"Aucune carte MCC creee au numero {board_num}; lancer d'abord le scan USB"
                )

            self.board_num = board_num
            self.board_name = str(board_name)
            self.is_initialized = True

            # Nettoyer un scan reste actif après un arrêt brutal de
            # l'application, sinon l'UL peut retourner l'erreur 29.
            try:
                self.api.ul.stop_background(
                    self.board_num,
                    self.api.FunctionType.AIFUNCTION,
                )
            except Exception:
                pass

            logger.info("Carte MCC initialisee: %s (board %s)", self.board_name, board_num)
            return True
        except Exception as exc:
            logger.error("Initialisation MCC impossible: %s", exc)
            self.is_initialized = False
            return False

    def configure_channel(
        self,
        channel: int,
        range_type: MCCRanges,
        label: str = "",
        units: str = "V",
    ) -> bool:
        """Configure un canal et sa plage pour la channel-gain queue MCC."""

        if not 0 <= channel < self.MAX_CHANNELS:
            logger.error("Canal MCC invalide: %s", channel)
            return False
        try:
            normalized_range = MCCRanges(range_type)
        except ValueError:
            logger.error("Plage MCC non prise en charge: %s", range_type)
            return False

        self.channels_config[channel] = ChannelConfig(
            channel=channel,
            range_type=normalized_range,
            label=label or f"Canal {channel}",
            units=units,
        )
        return True

    def clear_channels(self) -> None:
        if self._running:
            raise MCCBackendError("Impossible de modifier les canaux pendant l'acquisition")
        self.channels_config.clear()

    def _ul_range(self, range_type: MCCRanges):
        names = {
            MCCRanges.BIP10VOLTS: "BIP10VOLTS",
            MCCRanges.BIP5VOLTS: "BIP5VOLTS",
            MCCRanges.BIP2VOLTS: "BIP2VOLTS",
            MCCRanges.BIP1VOLTS: "BIP1VOLTS",
        }
        return getattr(self.api.ULRange, names[range_type])

    def _scan_options(self):
        # SINGLEIO donne au USB-1608FS classique un paquet exactement egal au
        # nombre de canaux. CONVERTDATA applique la calibration MCC aux codes
        # 16 bits avant leur conversion en volts.
        return (
            self.api.ScanOptions.BACKGROUND
            | self.api.ScanOptions.CONTINUOUS
            | self.api.ScanOptions.SINGLEIO
            | self.api.ScanOptions.CONVERTDATA
        )

    def start_continuous_acquisition(
        self,
        low_chan: int = 0,
        high_chan: int = 7,
        rate: float = 1000.0,
        buffer_size: int = 10000,
    ) -> bool:
        """Demarre un scan continu et alloue un buffer circulaire MCC."""

        if not self.is_initialized:
            logger.error("Carte MCC non initialisee")
            return False
        if self._running:
            logger.error("Un scan MCC est deja en cours")
            return False
        if rate <= 0 or buffer_size <= 0:
            logger.error("Frequence ou taille de buffer invalide")
            return False

        selected_channels = [
            config
            for channel, config in sorted(self.channels_config.items())
            if low_chan <= channel <= high_chan and config.enabled
        ]
        if not selected_channels:
            logger.error("Aucun canal MCC configure pour le scan")
            return False

        # Le USB-1608FS classique impose une file de gains contenant les huit
        # canaux dans l'ordre. Les canaux non demandes sont donc acquis en
        # +/-10 V, puis retires du bloc retourne au controleur.
        selected_by_number = {item.channel: item for item in selected_channels}
        scan_channels = [
            selected_by_number.get(
                channel,
                ChannelConfig(channel=channel, range_type=MCCRanges.BIP10VOLTS),
            )
            for channel in range(self.MAX_CHANNELS)
        ]
        output_indices = [item.channel for item in selected_channels]
        output_ranges = [self._ul_range(item.range_type) for item in selected_channels]
        n_channels = len(selected_channels)
        n_scan_channels = len(scan_channels)
        aggregate_rate = float(rate) * n_scan_channels
        if aggregate_rate > self.MAX_AGGREGATE_RATE:
            logger.error(
                "Frequence MCC trop elevee: %.3f Hz/canal produit %.3f S/s "
                "pour une limite agregee de %.3f S/s",
                float(rate),
                aggregate_rate,
                self.MAX_AGGREGATE_RATE,
            )
            return False
        buffer_count = int(buffer_size) * n_scan_channels

        try:
            # Deuxième protection contre un scan résiduel avant l'allocation
            # et le démarrage d'une nouvelle acquisition.
            try:
                self.api.ul.stop_background(
                    self.board_num,
                    self.api.FunctionType.AIFUNCTION,
                )
            except Exception:
                pass

            channel_queue = [item.channel for item in scan_channels]
            gain_queue = [self._ul_range(item.range_type) for item in scan_channels]
            self.api.ul.a_load_queue(
                self.board_num,
                channel_queue,
                gain_queue,
                n_scan_channels,
            )

            memhandle = self.api.ul.win_buf_alloc(buffer_count)
            if not memhandle:
                raise MCCBackendError("Allocation du buffer MCC impossible")

            try:
                actual_rate = self.api.ul.a_in_scan(
                    self.board_num,
                    channel_queue[0],
                    channel_queue[-1],
                    buffer_count,
                    int(rate),
                    gain_queue[0],
                    memhandle,
                    self._scan_options(),
                )
            except Exception:
                self.api.ul.win_buf_free(memhandle)
                raise

            with self._lock:
                self._memhandle = memhandle
                self._buffer_count = buffer_count
                self._last_point_count = 0
                self._last_raw_counter = None
                self._counter_epoch = 0
                self._last_observed_point_count = 0
                self._sequence = 0
                self.buffer_overruns = 0
                self._running = True
                self._output_indices = output_indices
                self._output_ranges = output_ranges
                self.acquisition_config = AcquisitionConfig(
                    board_num=self.board_num,
                    low_chan=0,
                    high_chan=self.MAX_CHANNELS - 1,
                    rate=float(actual_rate),
                    count=buffer_count,
                    n_channels=n_channels,
                    n_scan_channels=n_scan_channels,
                )
            logger.info(
                "Scan MCC demarre: %s canaux lus sur 8, %.3f Hz/canal, buffer=%s points",
                n_channels,
                float(actual_rate),
                buffer_count,
            )
            return True
        except Exception as exc:
            logger.exception("Demarrage du scan MCC impossible: %s", exc)
            return False

    def _copy_raw_points(self, start_index: int, point_count: int) -> np.ndarray:
        """Copie une zone, avec gestion explicite du retour au debut du buffer."""

        if not self._memhandle or point_count <= 0:
            return np.empty(0, dtype=np.uint16)

        output = np.empty(point_count, dtype=np.uint16)
        first_count = min(point_count, self._buffer_count - start_index)

        first = (ctypes.c_ushort * first_count)()
        self.api.ul.win_buf_to_array(self._memhandle, first, start_index, first_count)
        output[:first_count] = np.ctypeslib.as_array(first)

        remaining = point_count - first_count
        if remaining:
            second = (ctypes.c_ushort * remaining)()
            self.api.ul.win_buf_to_array(self._memhandle, second, 0, remaining)
            output[first_count:] = np.ctypeslib.as_array(second)
        return output

    def _convert_selected_to_volts(self, selected_raw: np.ndarray) -> np.ndarray:
        volts = np.empty(selected_raw.shape, dtype=np.float64)
        for column, ul_range in enumerate(self._output_ranges):
            volts[:, column] = np.fromiter(
                (
                    self.api.ul.to_eng_units(self.board_num, ul_range, int(value))
                    for value in selected_raw[:, column]
                ),
                dtype=np.float64,
                count=selected_raw.shape[0],
            )
        return volts

    def _unwrap_point_counter(self, raw_count: int) -> int:
        """Convertit le compteur signé 32 bits MCC en compteur Python monotone."""

        unsigned_count = int(raw_count) & 0xFFFFFFFF
        if self._last_raw_counter is not None and unsigned_count < self._last_raw_counter:
            # Un retour de 0xFFFFFFFF vers 0 est le rollover documenté de
            # l'Universal Library. Un petit recul signale au contraire un reset.
            if self._last_raw_counter - unsigned_count > 0x7FFFFFFF:
                self._counter_epoch += 0x1_0000_0000
            else:
                raise MCCBackendError("Le compteur MCC a reculé hors rollover 32 bits")
        absolute_count = self._counter_epoch + unsigned_count
        if absolute_count < self._last_observed_point_count:
            raise MCCBackendError("Le compteur MCC absolu a reculé pendant le scan")
        self._last_raw_counter = unsigned_count
        self._last_observed_point_count = absolute_count
        return absolute_count

    def get_data(self, num_samples: int = 1000) -> np.ndarray | None:
        """Retourne uniquement les nouveaux echantillons complets disponibles."""

        if not self._running or not self._memhandle:
            return None

        try:
            _, current_count, _ = self.api.ul.get_status(
                self.board_num,
                self.api.FunctionType.AIFUNCTION,
            )
            n_scan_channels = self.acquisition_config.n_scan_channels

            with self._lock:
                current_count = self._unwrap_point_counter(int(current_count))
                if current_count < self._last_point_count:
                    raise MCCBackendError("Le compteur MCC a recule pendant le scan")

                available_points = current_count - self._last_point_count
                if available_points > self._buffer_count:
                    self.buffer_overruns += 1
                    raise MCCBackendError(
                        "Debordement du buffer MCC: le logiciel n'a pas lu les donnees assez vite"
                    )

                available_samples = available_points // n_scan_channels
                samples_to_read = min(int(num_samples), available_samples)
                if samples_to_read <= 0:
                    return None

                point_count = samples_to_read * n_scan_channels
                start_index = self._last_point_count % self._buffer_count
                points = self._copy_raw_points(start_index, point_count)
                self._last_point_count += point_count
                self._sequence += 1

            scan_matrix = points.reshape(samples_to_read, n_scan_channels)
            selected_raw = scan_matrix[:, self._output_indices]
            return self._convert_selected_to_volts(selected_raw)
        except MCCBackendError:
            raise
        except Exception as exc:
            raise MCCBackendError(f"Lecture MCC impossible: {exc}") from exc

    def wait_for_data(self, num_samples: int, timeout: float = 1.0) -> np.ndarray | None:
        """Attend sans boucle CPU active qu'un bloc complet soit disponible."""

        deadline = time.monotonic() + max(0.0, timeout)
        while self._running and time.monotonic() < deadline:
            data = self.get_data(num_samples)
            if data is not None:
                return data
            time.sleep(0.002)
        return None

    def get_acquisition_status(self) -> dict[str, Any]:
        status: dict[str, Any] = {
            "board_num": self.board_num,
            "board_name": self.board_name,
            "is_running": self._running,
            "actual_rate": self.acquisition_config.rate,
            "channels_count": self.acquisition_config.n_channels,
            "scan_channels_count": self.acquisition_config.n_scan_channels,
            "points_read": self._last_point_count,
            "sequence": self._sequence,
            "buffer_overruns": self.buffer_overruns,
        }
        if self._running:
            try:
                _, current_count, current_index = self.api.ul.get_status(
                    self.board_num,
                    self.api.FunctionType.AIFUNCTION,
                )
                status.update(
                    current_count=int(current_count),
                    current_index=int(current_index),
                )
            except Exception as exc:
                status["error"] = str(exc)
        return status

    def stop_acquisition(self) -> bool:
        if not self._running:
            return True
        try:
            self.api.ul.stop_background(self.board_num, self.api.FunctionType.AIFUNCTION)
            return True
        except Exception as exc:
            logger.error("Arret du scan MCC impossible: %s", exc)
            return False
        finally:
            self._running = False

    def get_available_ranges(self) -> list[MCCRanges]:
        return list(self.SUPPORTED_RANGES)

    def get_channel_info(self, channel: int) -> dict[str, Any] | None:
        config = self.channels_config.get(channel)
        if config is None:
            return None
        return {
            "channel": config.channel,
            "range": config.range_type.name,
            "enabled": config.enabled,
            "label": config.label,
            "units": config.units,
        }

    def close(self) -> None:
        self.stop_acquisition()
        if self._memhandle:
            try:
                self.api.ul.win_buf_free(self._memhandle)
            except Exception as exc:
                logger.warning("Liberation du buffer MCC impossible: %s", exc)
            finally:
                self._memhandle = None
        self.is_initialized = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def scan_available_boards(api: Any | None = None) -> list[int]:
    """Fonction de compatibilite utilisee par le controleur et l'interface."""

    return MCCDAQ_USB1608FS.detect_boards(api=api)


def scan_available_devices(api: Any | None = None) -> list[MccUsbDeviceInfo]:
    """Retourne l'identité USB nécessaire à la traçabilité métrologique."""

    return MCCDAQ_USB1608FS.detect_devices(api=api)


def get_error_message(error_code: int) -> str:
    messages = {
        MCCErrorCodes.NOERRORS: "Aucune erreur",
        MCCErrorCodes.BADBOARD: "Numero de carte invalide",
        MCCErrorCodes.BADCHANNEL: "Numero de canal invalide",
        MCCErrorCodes.BADRANGE: "Plage analogique invalide",
    }
    try:
        normalized = MCCErrorCodes(error_code)
    except ValueError:
        return f"Erreur MCC inconnue: {error_code}"
    return messages.get(normalized, f"Erreur MCC: {error_code}")
