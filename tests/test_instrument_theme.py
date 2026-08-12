"""Tests for the CHNeoWave instrument design system."""

from __future__ import annotations

import os

import numpy as np
import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

pytest.importorskip("PySide6.QtWidgets", exc_type=ImportError)
pytest.importorskip("pyqtgraph", exc_type=ImportError)

from PySide6.QtWidgets import QApplication

from hrneowave.gui.icons import brand_icon, svg_icon
from hrneowave.gui.styles.theme_manager import ThemeManager
from hrneowave.gui.widgets.scientific_plot import PlotSeries, ScientificPlotWidget


@pytest.fixture(scope="module")
def qt_app():
    return QApplication.instance() or QApplication([])


def test_vector_identity_icons_are_available(qt_app):
    assert not brand_icon().isNull()
    for name in ("project", "calibration", "acquisition", "analysis", "report", "settings"):
        assert not svg_icon(name).isNull()


def test_theme_manager_applies_two_real_palettes(qt_app):
    manager = ThemeManager(qt_app)
    manager.apply_theme("light")
    light_stylesheet = qt_app.styleSheet()
    manager.apply_theme("dark")
    dark_stylesheet = qt_app.styleSheet()

    assert manager.get_current_theme() == "dark"
    assert "#F3F6F8" in light_stylesheet
    assert "#061219" in dark_stylesheet
    assert light_stylesheet != dark_stylesheet
    assert 'QPushButton#navButton[active="true"]' in dark_stylesheet

    manager.apply_theme("light")


def test_scientific_plot_supports_series_cursor_region_and_dark_theme(qt_app):
    plot = ScientificPlotWidget(x_label="Temps", y_label="Amplitude", x_unit="s")
    x = np.linspace(0.0, 10.0, 1000)
    plot.set_series([PlotSeries("CH-01", x, np.sin(x), "#22A7BC")])
    plot.set_region(2.0, 6.0, bounds=(0.0, 10.0))
    plot.set_region_enabled(True)
    plot.set_theme("dark")

    assert plot.series_count == 1
    assert plot.region() == pytest.approx((2.0, 6.0))
    assert plot._region.isVisible()
