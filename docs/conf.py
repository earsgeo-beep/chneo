"""Configuration Sphinx minimale pour la documentation active CHNeoWave."""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

project = "CHNeoWave"
author = "CHNeoWave"
copyright = "2026, CHNeoWave"

try:
    from hrneowave import __version__
except Exception:
    __version__ = "0.3.0"

version = __version__
release = __version__

extensions = ["sphinx.ext.githubpages"]
templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
language = "fr"

html_theme = "alabaster"
html_static_path = []
