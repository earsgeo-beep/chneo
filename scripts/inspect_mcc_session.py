#!/usr/bin/env python3
"""Valide rapidement un fichier de session MCC CHNeoWave."""

from __future__ import annotations

import argparse
import json

from hrneowave.acquisition.session_recorder import RecordingError, inspect_recording


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Controle la structure, les compteurs et l'etat d'une session MCC HDF5."
    )
    parser.add_argument("session_file", help="Chemin du fichier .h5 a controler")
    args = parser.parse_args()

    try:
        result = inspect_recording(args.session_file)
    except RecordingError as exc:
        result = {"ok": False, "error": str(exc)}

    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
