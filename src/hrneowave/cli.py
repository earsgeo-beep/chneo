#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interface en ligne de commande pour CHNeoWave.
"""

import argparse
import logging
import os
import sys

QApplication = None
Qt = None


def _ensure_qt_imports() -> str | None:
    """Charge un binding Qt compatible et retourne son nom."""
    global QApplication, Qt

    try:
        from PySide6.QtWidgets import QApplication as _QApplication
        from PySide6.QtCore import Qt as _Qt

        QApplication = _QApplication
        Qt = _Qt
        return "PySide6"
    except ImportError:
        try:
            from PyQt6.QtWidgets import QApplication as _QApplication
            from PyQt6.QtCore import Qt as _Qt

            QApplication = _QApplication
            Qt = _Qt
            return "PyQt6"
        except ImportError:
            return None


def _set_qt_application_attributes() -> None:
    """Active les attributs Qt utiles sans dépendre d'une API Qt précise."""
    if QApplication is None or Qt is None:
        return

    app_attrs = getattr(Qt, "ApplicationAttribute", Qt)
    for attr_name in ("AA_EnableHighDpiScaling", "AA_UseHighDpiPixmaps"):
        attr = getattr(app_attrs, attr_name, None)
        if attr is None:
            attr = getattr(Qt, attr_name, None)
        if attr is not None:
            QApplication.setAttribute(attr, True)


def _exec_application(app) -> int:
    """Exécute la boucle Qt quelle que soit la variante d'API disponible."""
    exec_fn = getattr(app, "exec", None)
    if exec_fn is None:
        exec_fn = getattr(app, "exec_", None)
    if exec_fn is None:
        raise RuntimeError("Aucune méthode d'exécution Qt disponible")
    return exec_fn()


def _ensure_project_root_on_path() -> None:
    """Ajoute la racine du projet au PYTHONPATH local."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    if project_root not in sys.path:
        sys.path.insert(0, project_root)


def _configure_logging(debug: bool = False) -> logging.Logger:
    """Initialise un logging simple utilisable dès le bootstrap."""
    logging.basicConfig(
        level=logging.DEBUG if debug else logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        filename="chneowave_debug.log",
        filemode="w",
    )
    return logging.getLogger(__name__)


def run_gui() -> int:
    """
    Lance l'interface graphique CHNeoWave.
    """
    logger = logging.getLogger(__name__)
    logger.info("run_gui() started")

    _ensure_project_root_on_path()

    binding_name = _ensure_qt_imports()
    if not binding_name:
        logger.critical("Aucune bibliothèque Qt trouvée (PySide6 ou PyQt6)")
        raise RuntimeError("Qt non disponible")

    _set_qt_application_attributes()

    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
        app.setApplicationName("CHNeoWave")
        app.setApplicationVersion("1.0.0")
        app.setOrganizationName("Laboratoire Maritime")

    from hrneowave.gui.styles.theme_manager import ThemeManager
    from hrneowave.gui.main_window import MainWindow

    logger.info("Qt binding chargé: %s", binding_name)

    theme_manager = ThemeManager(app)
    theme_manager.apply_theme("maritime_modern")

    logger.info("Creating MainWindow...")
    window = MainWindow()
    logger.info("Showing MainWindow...")
    window.show()

    logger.info("Starting event loop...")
    exit_code = _exec_application(app)
    logger.info("Event loop finished with exit code %s", exit_code)
    return exit_code


def run_cli(argv: list[str] | None = None) -> int:
    """
    Point d'entrée CLI.

    Par défaut, CHNeoWave est une application desktop et lance la GUI.
    """
    parser = argparse.ArgumentParser(
        description="CHNeoWave - Logiciel d'acquisition et d'analyse de données maritimes",
        prog="chneowave",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="CHNeoWave 1.0.0",
    )
    parser.add_argument(
        "--gui",
        action="store_true",
        default=False,
        help="Lance explicitement l'interface graphique",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Active le mode debug",
    )

    args = parser.parse_args(argv)
    logger = _configure_logging(debug=args.debug)
    logger.info("run_cli() started")

    # Application desktop: sans sous-commande dédiée, la GUI reste le comportement par défaut.
    return run_gui()


if __name__ == "__main__":
    sys.exit(run_cli())
