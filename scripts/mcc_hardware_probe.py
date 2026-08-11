#!/usr/bin/env python3
"""Diagnostic non destructif de l'installation MCC hors ligne."""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from hrneowave.acquisition.mcc_daq_wrapper import (  # noqa: E402
    MCCDAQ_USB1608FS,
    MCCUniversalLibraryUnavailable,
)


def main() -> int:
    result = {
        "driver": "MCC Universal Library",
        "expected_device": "USB-1608FS",
        "boards": [],
        "ok": False,
    }
    try:
        detected_devices = MCCDAQ_USB1608FS.detect_devices()
        result["boards"] = [device.board_num for device in detected_devices]
        for detected in detected_devices:
            device = MCCDAQ_USB1608FS()
            if device.initialize(detected.board_num):
                result.setdefault("devices", []).append(
                    {
                        "board_num": detected.board_num,
                        "board_name": device.board_name,
                        "unique_id": detected.unique_id,
                    }
                )
                device.close()
        result["ok"] = bool(result.get("devices"))
    except MCCUniversalLibraryUnavailable as exc:
        result["error"] = str(exc)
    except Exception as exc:
        result["error"] = f"Diagnostic MCC impossible: {exc}"

    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
