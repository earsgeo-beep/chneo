#!/usr/bin/env python3
"""
Script de lancement principal pour CHNeoWave.
"""

import argparse
import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(CURRENT_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)


def main(argv: list[str] | None = None) -> int:
    """
    Point d'entree principal.
    """
    from hrneowave import __version__

    parser = argparse.ArgumentParser(
        description="CHNeoWave - Logiciel d'acquisition et d'analyse de donnees maritimes",
        prog="chneowave",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"CHNeoWave {__version__}",
    )
    parser.add_argument(
        "--gui",
        action="store_true",
        default=True,
        help="Lance l'interface graphique (comportement par defaut)",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Active le mode debug",
    )
    args = parser.parse_args(argv)

    try:
        from hrneowave.cli import run_gui

        return run_gui(debug=args.debug)
    except Exception as exc:
        print(f"Erreur lors du lancement: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
