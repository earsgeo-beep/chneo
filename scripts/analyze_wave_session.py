#!/usr/bin/env python3
"""Analyse une session CHNeoWave sans ouvrir l'interface graphique."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from hrneowave.core.post_processor import PostProcessor


def _output_format(path: Path) -> str:
    formats = {
        ".csv": "csv",
        ".json": "json",
        ".h5": "hdf5",
        ".hdf5": "hdf5",
    }
    try:
        return formats[path.suffix.lower()]
    except KeyError as exc:
        raise ValueError("La sortie doit etre .csv, .json, .h5 ou .hdf5") from exc


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Analyse spectrale et temporelle d'une session CHNeoWave."
    )
    parser.add_argument("input_file", help="Session CSV, JSON ou HDF5")
    parser.add_argument("--output", required=True, help="Resultat CSV, JSON ou HDF5")
    parser.add_argument("--segment-length", type=int, default=1024)
    parser.add_argument("--overlap", type=float, default=0.5)
    parser.add_argument("--min-frequency", type=float, default=0.0)
    parser.add_argument("--max-frequency", type=float)
    parser.add_argument("--no-detrend", action="store_true")
    args = parser.parse_args()

    processor = PostProcessor()
    processor.config["analysis"].update(
        {
            "window_size": args.segment_length,
            "overlap": args.overlap,
            "min_frequency": args.min_frequency,
            "max_frequency": args.max_frequency,
            "detrend": not args.no_detrend,
        }
    )
    if not processor.load_data_file(args.input_file):
        return 2
    if not processor.run_analysis():
        return 3

    output_path = Path(args.output).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        format_type = _output_format(output_path)
    except ValueError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        return 4
    if not processor.export_results(str(output_path), format_type):
        return 5

    summary = processor.get_analysis_summary() or {}
    print(
        json.dumps(
            {"ok": True, "output": str(output_path), "summary": summary},
            indent=2,
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
