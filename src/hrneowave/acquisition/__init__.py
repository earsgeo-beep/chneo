"""Acquisition physique et traçable de CHNeoWave."""

from hrneowave.hardware import VoltageRange

from .acquisition_controller import (
    AcquisitionController,
    AcquisitionSession,
    MaritimeChannelConfig,
    create_default_maritime_config,
)
from .daq_backend import DaqBackend, DaqReadResult
from .hardware_qualification import (
    HardwareQualificationService,
    QualificationCheck,
    QualificationCriteria,
    QualificationError,
    QualificationReport,
    QualificationReportWriter,
)
from .session_exporter import SessionExportError, SessionExporter
from .session_recorder import ContinuousHDF5Recorder, RecordingError, inspect_recording

DEFAULT_SAMPLING_RATE = 1000.0
DEFAULT_BUFFER_SIZE = 10_000
DEFAULT_EXPORT_FORMAT = "hdf5"

MARITIME_SENSOR_TYPES = (
    "wave_height",
    "pressure",
    "accelerometer",
    "temperature",
    "flow_velocity",
    "force",
    "displacement",
    "strain",
    "inclination",
    "generic",
)

VOLTAGE_RANGES = {item.label: item for item in VoltageRange}

__all__ = [
    "AcquisitionController",
    "AcquisitionSession",
    "ContinuousHDF5Recorder",
    "DaqBackend",
    "DaqReadResult",
    "HardwareQualificationService",
    "MARITIME_SENSOR_TYPES",
    "MaritimeChannelConfig",
    "RecordingError",
    "QualificationCheck",
    "QualificationCriteria",
    "QualificationError",
    "QualificationReport",
    "QualificationReportWriter",
    "SessionExportError",
    "SessionExporter",
    "VOLTAGE_RANGES",
    "VoltageRange",
    "create_default_maritime_config",
    "inspect_recording",
]
