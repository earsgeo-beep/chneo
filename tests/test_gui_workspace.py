"""Smoke tests for the professional laboratory workspace."""

# ruff: noqa: E402 - the offscreen platform must be selected before Qt imports.

from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

QtWidgets = pytest.importorskip("PySide6.QtWidgets", exc_type=ImportError)

from PySide6.QtWidgets import QApplication, QTableWidgetItem

from hrneowave.gui.views.acquisition_config_view import AcquisitionConfigView
from hrneowave.gui.views.analysis_view import AnalysisView
from hrneowave.gui.views.calibration_view import CalibrationView
from hrneowave.gui.widgets.main_sidebar import MainSidebar


@pytest.fixture(scope="module")
def qt_app():
    app = QApplication.instance() or QApplication([])
    yield app


def test_sidebar_can_release_workspace_width(qt_app):
    sidebar = MainSidebar()

    sidebar.collapse_sidebar(True)
    assert sidebar.width() == 72
    assert sidebar.navigation_buttons["calibration"].text() == "03"

    sidebar.collapse_sidebar(False)
    assert sidebar.width() == 248
    assert "Calibration" in sidebar.navigation_buttons["calibration"].text()


def test_calibration_workspace_fits_real_linear_record(qt_app):
    view = CalibrationView()
    points = ((0.0, 0.016), (50.0, 1.016), (100.0, 2.016))
    for row, (reference, voltage) in enumerate(points):
        view.points_table.setItem(row, 1, QTableWidgetItem(str(reference)))
        view.points_table.setItem(row, 2, QTableWidgetItem(str(voltage)))

    view._fit_active_channel()

    record = view._channel_records[0]
    assert record.r_squared == pytest.approx(1.0)
    assert record.sensitivity_v_per_unit == pytest.approx(0.02)
    assert view.calibration_status_label.text() == "CALIBRATION VALIDÉE"


def test_analysis_parameters_panel_is_collapsible(qt_app):
    view = AnalysisView()

    view._toggle_tools_panel()
    assert not view._tools_panel_expanded
    assert view.tools_panel.isHidden()
    assert view.tools_toggle_button.text() == "Afficher les paramètres"


def test_hardware_panel_uses_one_connected_state(qt_app):
    class ConnectedDaq:
        board_name = "USB-1608FS"

        @staticmethod
        def get_acquisition_status():
            return {"board_name": "USB-1608FS"}

    class ConnectedController:
        daq = ConnectedDaq()
        channels_config = {}
        is_acquiring = False

        @staticmethod
        def is_hardware_available():
            return True

        @staticmethod
        def close():
            return None

    view = AcquisitionConfigView()
    if view.controller is not None:
        view.controller.close()
    view.controller = ConnectedController()
    view._hardware_state = "connected"

    view.update_hardware_status()

    assert view.hardware_status_label.text() == "MATÉRIEL OPÉRATIONNEL"
    assert view.board_name_label.text() == "USB-1608FS"
    assert view.driver_status_label.text() == "Universal Library chargée"
    assert view.operation_mode_label.text() == "Acquisition matérielle"
