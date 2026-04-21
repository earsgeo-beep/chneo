# -*- coding: utf-8 -*-
"""Surface d'import minimale pour l'interface CHNeoWave."""

from .main_window import MainWindow
from .styles.theme_manager import ThemeManager as CHNeoWaveTheme
from .view_manager import ViewManager
from .views import (
    DashboardViewMaritime,
    WelcomeView,
    get_acquisition_view,
    get_analysis_view,
    get_calibration_view,
    get_export_view,
    get_settings_view,
)

__all__ = [
    "MainWindow",
    "ViewManager",
    "CHNeoWaveTheme",
    "DashboardViewMaritime",
    "WelcomeView",
    "get_calibration_view",
    "get_acquisition_view",
    "get_analysis_view",
    "get_export_view",
    "get_settings_view",
]
