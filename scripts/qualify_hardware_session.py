#!/usr/bin/env python3
"""Qualifie une session matérielle CHNeoWave depuis son fichier HDF5 maître."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from hrneowave.acquisition import (
    MCC_USB1608FS_PROTOCOL,
    HardwareQualificationService,
    QualificationCriteria,
    QualificationError,
    QualificationReportWriter,
)


def _arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Contrôle l'intégrité, la cadence, la continuité temporelle et les voies "
            "d'une acquisition physique terminée."
        )
    )
    parser.add_argument("source", type=Path, help="fichier HDF5 maître à qualifier")
    parser.add_argument(
        "--profile",
        choices=("quick", "grounded"),
        default="quick",
        help="quick: essai fonctionnel; grounded: entrées reliées à AGND",
    )
    parser.add_argument(
        "--stage",
        choices=tuple(stage.stage_id for stage in MCC_USB1608FS_PROTOCOL.stages),
        default=None,
        help="palier formel MCC Q0 à Q4; applique sa durée et ses exigences exactes",
    )
    parser.add_argument(
        "--minimum-duration",
        type=float,
        default=None,
        metavar="SECONDS",
        help="durée minimale exigée (3 s pour quick, 60 s pour grounded par défaut)",
    )
    parser.add_argument(
        "--output-directory",
        type=Path,
        default=None,
        help="dossier des rapports; par défaut <dossier_source>/qualification_reports",
    )
    parser.add_argument(
        "--ignore-wall-clock",
        action="store_true",
        help=(
            "désactive uniquement le contrôle de cadence par horloge monotone; "
            "réservé aux anciens fichiers sans cette preuve"
        ),
    )
    return parser.parse_args()


def _criteria(arguments: argparse.Namespace) -> QualificationCriteria:
    check_wall_clock = not arguments.ignore_wall_clock
    if arguments.stage is not None:
        if arguments.minimum_duration is not None:
            raise ValueError("--minimum-duration ne peut pas modifier un palier formel Q0-Q4")
        if arguments.ignore_wall_clock:
            raise ValueError("--ignore-wall-clock est interdit pour un palier formel Q0-Q4")
        return MCC_USB1608FS_PROTOCOL.stage(arguments.stage).criteria(
            MCC_USB1608FS_PROTOCOL.protocol_id,
            check_wall_clock=True,
        )
    if arguments.profile == "grounded":
        duration = 60.0 if arguments.minimum_duration is None else arguments.minimum_duration
        return QualificationCriteria.grounded_inputs(
            duration,
            check_wall_clock=check_wall_clock,
        )
    duration = 3.0 if arguments.minimum_duration is None else arguments.minimum_duration
    return QualificationCriteria.quick_functional(
        duration,
        check_wall_clock=check_wall_clock,
    )


def main() -> int:
    arguments = _arguments()
    source = arguments.source.expanduser().resolve()
    output_directory = (
        arguments.output_directory.expanduser().resolve()
        if arguments.output_directory is not None
        else source.parent / "qualification_reports"
    )
    try:
        report = HardwareQualificationService().evaluate(source, _criteria(arguments))
        json_path, hdf5_path = QualificationReportWriter().write_bundle(
            report,
            output_directory,
        )
    except (OSError, ValueError, QualificationError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False, indent=2), file=sys.stderr)
        return 1

    failed = [
        {"code": check.code, "scope": check.scope, "message": check.message}
        for check in report.checks
        if not check.passed
    ]
    print(
        json.dumps(
            {
                "qualification_id": report.qualification_id,
                "verdict": report.verdict,
                "accepted": report.accepted,
                "profile": report.profile_name,
                "protocol_id": report.criteria.protocol_id,
                "protocol_stage": report.criteria.protocol_stage,
                "source": report.source_master_file,
                "source_sha256": report.source_sha256,
                "failed_checks": failed,
                "json_report": str(json_path),
                "hdf5_report": str(hdf5_path),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if report.accepted else 2


if __name__ == "__main__":
    raise SystemExit(main())
