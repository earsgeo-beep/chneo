"""Smoke tests for the professional laboratory workspace."""

# ruff: noqa: E402 - the offscreen platform must be selected before Qt imports.

from __future__ import annotations

import copy
import os
import tempfile
import time
from pathlib import Path

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

QtWidgets = pytest.importorskip("PySide6.QtWidgets", exc_type=ImportError)

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QTableWidgetItem

from hrneowave.acquisition import MCC_USB1608FS_PROTOCOL, AcquisitionController
from hrneowave.core.legacy_raw import LegacyRawImportOptions
from hrneowave.gui.styles.theme_manager import ThemeManager
from hrneowave.gui.views.acquisition_config_view import AcquisitionConfigView
from hrneowave.gui.views.analysis_view import AnalysisView
from hrneowave.gui.views.calibration_view import CalibrationView
from hrneowave.gui.views.report_view import ReportView
from hrneowave.gui.widgets.qualification_workspace import QualificationWorkspace
from hrneowave.gui.widgets.top_navigation import TopNavigationBar
from hrneowave.gui.workbench.channel_model import ChannelItem, ChannelListModel
from tests.hardware_test_doubles import DeterministicPhysicalBackend, physical_test_device


@pytest.fixture(scope="module")
def qt_app():
    app = QApplication.instance() or QApplication([])
    yield app


def test_navigation_is_horizontal_and_exposes_workspaces(qt_app):
    navigation = TopNavigationBar()

    assert navigation.height() == 58
    assert navigation.navigation_buttons["calibration"].text() == "Calibration"
    navigation.set_active_view("analysis")
    assert navigation.navigation_buttons["analysis"].isChecked()


def test_channel_model_tracks_visible_sensor_channels(qt_app):
    model = ChannelListModel(
        [
            ChannelItem("channel_00", "Sonde 1", unit="cm", visible=True),
            ChannelItem("channel_01", "Sonde 2", unit="cm", visible=False),
        ]
    )

    assert model.visible_keys() == ["channel_00"]
    model.setData(model.index(1, 0), Qt.CheckState.Checked, Qt.ItemDataRole.CheckStateRole)
    assert model.visible_keys() == ["channel_00", "channel_01"]
    model.set_only_visible("channel_01")
    assert model.visible_keys() == ["channel_01"]
    model.set_all_visible(True)
    assert model.visible_keys() == ["channel_00", "channel_01"]


def test_instrument_theme_has_distinct_light_and_dark_palettes(qt_app):
    manager = ThemeManager(qt_app)
    manager.apply_theme("light")
    light_stylesheet = qt_app.styleSheet()
    manager.apply_theme("dark")
    dark_stylesheet = qt_app.styleSheet()
    manager.apply_theme("light")

    assert light_stylesheet != dark_stylesheet
    assert "#E9EEF1" in light_stylesheet
    assert "#11191E" in dark_stylesheet


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


def test_calibration_live_monitor_reads_the_shared_physical_controller(qt_app):
    backend = DeterministicPhysicalBackend()
    backend.connect()
    controller = AcquisitionController(daq_backend=backend)
    view = CalibrationView()
    try:
        view.bind_acquisition_controller(controller)
        view._start_live_preview()
        deadline = time.monotonic() + 3.0
        while view._live_values.size == 0 and time.monotonic() < deadline:
            qt_app.processEvents()
            time.sleep(0.01)

        assert view._live_values.size > 0
        assert view.live_state_label.text() == "LECTURE LIVE"
        assert view.live_voltage_label.text().endswith(" V")
        assert controller.is_calibration_preview_active
        assert view.signal_verdict_label.text() == "SIGNAL INSTABLE"
        assert not view.record_point_button.isEnabled()
    finally:
        view._stop_live_preview()
        controller.close()


def test_analysis_parameters_panel_is_collapsible(qt_app):
    view = AnalysisView()

    view._toggle_tools_panel()
    assert view._tools_panel_expanded
    assert not view.results_area.details_drawer.isHidden()
    assert view.tools_toggle_button.text() == "Fermer"


def test_analysis_workbench_keeps_time_and_spectrum_visible(qt_app):
    view = AnalysisView()

    assert view.results_area.time_plot.isVisibleTo(view)
    assert view.results_area.spectrum_plot.isVisibleTo(view)
    assert view.results_area.plot_splitter.count() == 2


def test_analysis_view_loads_raw_and_draws_time_signals(qt_app):
    view = AnalysisView()
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "waves.raw"
        path.write_text(
            "\n".join(
                [
                    "2",
                    "2",
                    "2",
                    "2.0 -0.5",
                    "0 0.0 2.0",
                    "1 0.5 1.0",
                    "2 1.0 0.0",
                    "3 1.5 -1.0",
                ]
            ),
            encoding="ascii",
        )

        loaded = view.load_data_file(
            str(path),
            raw_options=LegacyRawImportOptions(
                sensor_type="wave_height",
                physical_unit="cm",
                calibration_confirmed=True,
            ),
        )

        assert loaded
        assert view.post_processor.current_data["source_format"] == "legacy_raw"
        assert view.post_processor.sample_rate == 2.0
        assert view.results_area.time_plot.series_count() == 2
        assert view.source_pane.channel_model.rowCount() == 2
        view.source_pane.channel_model.set_only_visible("channel_01")
        assert view.results_area.time_plot.series_count() == 1


def test_scientific_report_exports_pdf_with_current_qt_api(qt_app, tmp_path):
    view = ReportView()
    view.set_analysis_context(
        "laboratory.raw",
        {
            "sample_rate": 32.0,
            "metadata": {"sample_rate_hz": 32.0, "n_samples": 1024, "duration_s": 32.0},
            "analysis_configuration": {"method": "Welch PSD + zero-upcrossing"},
            "basic_stats": {},
            "spectral_analysis": {},
            "wave_parameters": {},
            "quality": {},
        },
    )
    output_path = tmp_path / "scientific-report.pdf"

    view.on_export_requested("pdf", str(output_path))

    assert output_path.is_file()
    assert output_path.stat().st_size > 0


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


def test_qualification_workspace_requires_checklist_and_locks_while_running(qt_app):
    workspace = QualificationWorkspace()
    workspace.set_protocol(MCC_USB1608FS_PROTOCOL, physical_test_device())

    assert workspace.selected_stage().stage_id == "Q0"
    assert not workspace.start_stage_button.isEnabled()

    for checkbox in workspace._checklist_widgets:
        checkbox.setChecked(True)

    assert workspace.checklist_complete()
    assert workspace.start_stage_button.isEnabled()

    workspace.set_running("Q0")

    assert not workspace.start_stage_button.isEnabled()


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
