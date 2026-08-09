"""Smoke tests for the professional laboratory workspace."""

# ruff: noqa: E402 - the offscreen platform must be selected before Qt imports.

from __future__ import annotations

import copy
import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

QtWidgets = pytest.importorskip("PySide6.QtWidgets", exc_type=ImportError)

from PySide6.QtWidgets import QApplication, QTableWidgetItem

from hrneowave.gui.views.acquisition_config_view import AcquisitionConfigView
from hrneowave.gui.views.analysis_view import AnalysisView
from hrneowave.gui.views.calibration_view import CalibrationView
from hrneowave.gui.widgets.main_sidebar import MainSidebar
from tests.hardware_test_doubles import physical_test_device


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


def test_calibration_channel_count_follows_active_hardware(qt_app):
    view = CalibrationView(channel_count=2)

    view.set_channel_count(24)

    assert view.channel_count == 24
    assert view.channel_combo.count() == 24
    assert view.channel_progress_label.text() == "CANAL 1 / 24"


def test_analysis_parameters_panel_is_collapsible(qt_app):
    view = AnalysisView()

    view._toggle_tools_panel()
    assert not view._tools_panel_expanded
    assert view.tools_panel.parameters_panel.isHidden()
    assert view.tools_toggle_button.text() == "Afficher les réglages"


def test_hardware_panel_uses_one_connected_state(qt_app):
    class ConnectedController:
        selected_device = physical_test_device()
        channels_config = {}
        is_acquiring = False

        @staticmethod
        def is_hardware_available():
            return True

        @staticmethod
        def get_hardware_status():
            return {"connected": True, "buffer_overruns": 0}

        @staticmethod
        def close():
            return None

    view = AcquisitionConfigView()
    if view.controller is not None:
        view.controller.close()
    view.controller = ConnectedController()
    view._hardware_state = "connected"

    view.update_hardware_status()

    assert view.hardware_status_label.text() == "MATÉRIEL CONNECTÉ"
    assert view.qualification_status_label.text() == "Non exécutée"
    assert view.board_name_label.text() == "Test Laboratory Deterministic DAQ"
    assert view.driver_status_label.text() == "test.physical.driver"
    assert view.operation_mode_label.text() == "Qualification à exécuter"
    assert not view.start_acquisition_btn.isEnabled()
    assert view.test_acquisition_btn.isEnabled()


def test_acquisition_configuration_round_trip_preserves_scientific_geometry(qt_app):
    view = AcquisitionConfigView()
    try:
        view._initialize_channels_table(8)
        view.project_name_edit.setText("Essai houle multidirectionnel")
        view.water_depth_spin.setValue(0.8)
        view.sampling_rate_spin.setValue(200.0)
        view.duration_spin.setValue(120.0)

        for row, position in enumerate((0.0, 0.4, 0.8)):
            view.channels_table.cellWidget(row, 1).setChecked(True)
            view.channels_table.cellWidget(row, 2).setCurrentText("wave_height")
            view.channels_table.setItem(row, 5, QTableWidgetItem("0.02"))
            view.channels_table.setItem(row, 6, QTableWidgetItem("m"))
            view.channels_table.setItem(row, 7, QTableWidgetItem(str(position)))

        snapshot = view.configuration_snapshot()
        view.project_name_edit.setText("Modifié")
        view.water_depth_spin.setValue(1.2)
        view.channels_table.setItem(1, 7, QTableWidgetItem("9.0"))

        view.apply_configuration_snapshot(snapshot)

        assert view.project_name_edit.text() == "Essai houle multidirectionnel"
        assert view.water_depth_spin.value() == pytest.approx(0.8)
        assert view.channels_table.item(1, 7).text() == "0.4"
        assert view.channels_table.item(2, 5).text() == "0.02"

        invalid = copy.deepcopy(snapshot)
        invalid["project_name"] = "Ne doit pas être appliqué"
        invalid["scientific_context"]["water_depth_m"] = 1.5
        invalid["channels"][-1]["sensitivity_v_per_unit"] = 0.0
        with pytest.raises(ValueError, match="Sensibilité invalide"):
            view.apply_configuration_snapshot(invalid)
        assert view.project_name_edit.text() == "Essai houle multidirectionnel"
        assert view.water_depth_spin.value() == pytest.approx(0.8)
    finally:
        if view.controller is not None:
            view.controller.close()
