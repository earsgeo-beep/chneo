"""Interactive scientific plot with an embedded instrument toolbar."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pyqtgraph as pg
import pyqtgraph.exporters
from PySide6.QtCore import QRectF, Signal
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
)

from .icons import line_icon


class ScientificPlotWidget(QFrame):
    """Fast plot designed for long records and repeatable operator actions."""

    region_changed = Signal(float, float)
    cursor_moved = Signal(float, float)

    def __init__(
        self,
        title: str,
        x_label: str,
        y_label: str,
        *,
        logarithmic_y: bool = False,
        parent=None,
    ):
        super().__init__(parent)
        self.setObjectName("scientificPlot")
        self._curves: dict[str, pg.PlotDataItem] = {}
        self._markers: list[pg.PlotDataItem] = []
        self._fills: list[tuple[pg.FillBetweenItem, pg.PlotDataItem, pg.PlotDataItem]] = []
        self._image_item: pg.ImageItem | None = None
        self._color_bar: pg.ColorBarItem | None = None
        self._logarithmic_y = logarithmic_y
        self._logarithmic_x = False
        self._cursor_enabled = False
        self._region_enabled = False
        self._grid_visible = True
        self._legend_visible = True
        self._theme = "light"
        self._build_ui(title, x_label, y_label)

    def _build_ui(self, title: str, x_label: str, y_label: str) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QFrame()
        header.setObjectName("plotHeader")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(9, 3, 5, 3)
        header_layout.setSpacing(3)
        self.title_label = QLabel(title.upper())
        self.title_label.setObjectName("plotTitle")
        self.method_label = QLabel()
        self.method_label.setObjectName("plotMeta")
        header_layout.addWidget(self.title_label)
        header_layout.addWidget(self.method_label)
        header_layout.addStretch()

        self.tool_buttons: dict[str, QPushButton] = {}
        tools = (
            ("cursor", "Curseur de lecture", True),
            ("region", "Sélectionner l’intervalle", True),
            ("zoom_in", "Zoom avant", False),
            ("zoom_out", "Zoom arrière", False),
            ("pan", "Déplacement libre", True),
            ("grid", "Afficher la grille", True),
            ("legend", "Afficher la légende", True),
            ("fit", "Ajuster toutes les données", False),
            ("export", "Exporter le graphe", False),
        )
        for name, tooltip, checkable in tools:
            button = QPushButton()
            button.setObjectName("plotTool")
            button.setFixedSize(25, 24)
            button.setCheckable(checkable)
            button.setIcon(line_icon(name, "#78919C"))
            button.setToolTip(tooltip)
            button.clicked.connect(lambda checked=False, tool=name: self._activate_tool(tool, checked))
            self.tool_buttons[name] = button
            header_layout.addWidget(button)
        self.tool_buttons["grid"].setChecked(True)
        self.tool_buttons["legend"].setChecked(True)
        layout.addWidget(header)

        self.plot = pg.PlotWidget(background=None)
        self.plot.setObjectName("plotCanvas")
        self.plot.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.plot.setLabel("bottom", x_label)
        self.plot.setLabel("left", y_label)
        self.plot.showGrid(x=True, y=True, alpha=0.22)
        self.plot.setMouseEnabled(x=True, y=True)
        self.plot.getPlotItem().setMenuEnabled(False)
        self.plot.getPlotItem().hideButtons()
        self.legend = self.plot.addLegend(offset=(8, 8), colCount=3)
        self.plot.setDownsampling(auto=True, mode="peak")
        self.plot.setClipToView(True)
        if self._logarithmic_y:
            self.plot.setLogMode(x=False, y=True)
        layout.addWidget(self.plot, 1)

        self.cursor_v = pg.InfiniteLine(angle=90, movable=False, pen=pg.mkPen("#D79B34", width=1))
        self.cursor_h = pg.InfiniteLine(angle=0, movable=False, pen=pg.mkPen("#D79B34", width=1))
        self.cursor_v.hide()
        self.cursor_h.hide()
        self.plot.addItem(self.cursor_v, ignoreBounds=True)
        self.plot.addItem(self.cursor_h, ignoreBounds=True)
        self.region = pg.LinearRegionItem(
            values=(0.0, 1.0),
            movable=True,
            brush=pg.mkBrush(22, 167, 197, 38),
            pen=pg.mkPen("#16A7C5", width=1),
        )
        self.region.hide()
        self.plot.addItem(self.region)
        self.region.sigRegionChangeFinished.connect(self._emit_region)
        self.plot.scene().sigMouseMoved.connect(self._mouse_moved)
        self.apply_theme("light")

    def set_title_metadata(self, text: str) -> None:
        self.method_label.setText(text)

    def set_axis_labels(self, x_label: str | None = None, y_label: str | None = None) -> None:
        if x_label is not None:
            self.plot.setLabel("bottom", x_label)
        if y_label is not None:
            self.plot.setLabel("left", y_label)

    def set_series(
        self,
        series: dict[str, tuple[np.ndarray, np.ndarray, str]],
        *,
        clear: bool = True,
        fit: bool = True,
    ) -> None:
        if clear:
            self.clear_series()
        for key, (x_values, y_values, color) in series.items():
            x = np.asarray(x_values, dtype=float)
            y = np.asarray(y_values, dtype=float)
            finite = np.isfinite(x) & np.isfinite(y)
            if self._logarithmic_y:
                finite &= y > 0
            curve = self.plot.plot(
                x[finite],
                y[finite],
                pen=pg.mkPen(color, width=1.15),
                name=key,
            )
            self._curves[key] = curve
        self.legend.setVisible(self._legend_visible and bool(series))
        if series and fit:
            self.fit_data()

    def update_series(
        self,
        series: dict[str, tuple[np.ndarray, np.ndarray, str]],
        *,
        fit: bool = False,
    ) -> None:
        """Met à jour des courbes existantes sans les recréer à chaque bloc."""

        requested_keys = set(series)
        for key in tuple(self._curves):
            if key in requested_keys:
                continue
            curve = self._curves.pop(key)
            self.plot.removeItem(curve)
            try:
                self.legend.removeItem(key)
            except (KeyError, ValueError):
                pass
        for key, (x_values, y_values, color) in series.items():
            x = np.asarray(x_values, dtype=float)
            y = np.asarray(y_values, dtype=float)
            finite = np.isfinite(x) & np.isfinite(y)
            if self._logarithmic_y:
                finite &= y > 0
            curve = self._curves.get(key)
            if curve is None:
                curve = self.plot.plot(
                    x[finite],
                    y[finite],
                    pen=pg.mkPen(color, width=1.15),
                    name=key,
                )
                self._curves[key] = curve
            else:
                curve.setData(x[finite], y[finite])
                curve.setPen(pg.mkPen(color, width=1.15))
        self.legend.setVisible(self._legend_visible and bool(series))
        if series and fit:
            self.fit_data()

    def add_confidence_band(
        self,
        x_values: np.ndarray,
        lower_values: np.ndarray,
        upper_values: np.ndarray,
        color: str,
    ) -> None:
        """Draw an unlabeled uncertainty envelope behind the PSD curves."""

        x = np.asarray(x_values, dtype=float)
        lower = np.asarray(lower_values, dtype=float)
        upper = np.asarray(upper_values, dtype=float)
        finite = np.isfinite(x) & np.isfinite(lower) & np.isfinite(upper)
        if self._logarithmic_y:
            finite &= (lower > 0) & (upper > 0)
        lower_curve = self.plot.plot(x[finite], lower[finite], pen=pg.mkPen(color, width=0.6))
        upper_curve = self.plot.plot(x[finite], upper[finite], pen=pg.mkPen(color, width=0.6))
        fill = pg.FillBetweenItem(
            lower_curve,
            upper_curve,
            brush=pg.mkBrush((*pg.mkColor(color).getRgb()[:3], 32)),
        )
        self.plot.addItem(fill)
        self._fills.append((fill, lower_curve, upper_curve))

    def set_spectrogram(
        self,
        times: np.ndarray,
        frequencies: np.ndarray,
        density: np.ndarray,
        *,
        dynamic_range_db: float = 60.0,
        color_map: str = "viridis",
        color_label: str = "PSD (dB)",
    ) -> None:
        """Render one channel as a calibrated time-frequency map."""

        self.clear_series()
        times = np.asarray(times, dtype=float)
        frequencies = np.asarray(frequencies, dtype=float)
        density = np.asarray(density, dtype=float)
        if density.shape != (len(frequencies), len(times)) or density.size == 0:
            return
        decibels = 10.0 * np.log10(np.maximum(density, np.finfo(float).tiny))
        maximum = float(np.nanmax(decibels))
        minimum = maximum - max(10.0, float(dynamic_range_db))
        decibels = np.clip(decibels, minimum, maximum)
        image = pg.ImageItem(decibels.T, axisOrder="col-major")
        x_step = float(np.median(np.diff(times))) if len(times) > 1 else 1.0
        y_step = float(np.median(np.diff(frequencies))) if len(frequencies) > 1 else 1.0
        image.setRect(
            QRectF(
                float(times[0] - x_step / 2.0),
                float(frequencies[0] - y_step / 2.0),
                float(x_step * len(times)),
                float(y_step * len(frequencies)),
            )
        )
        color = pg.colormap.get(color_map)
        image.setLookupTable(color.getLookupTable(nPts=256))
        image.setLevels((minimum, maximum))
        self.plot.addItem(image)
        color_bar = pg.ColorBarItem(
            values=(minimum, maximum),
            colorMap=color,
            label=color_label,
            interactive=False,
            width=12,
        )
        color_bar.setImageItem(image, insert_in=self.plot.getPlotItem())
        self._image_item = image
        self._color_bar = color_bar
        self.legend.hide()
        self.set_log_mode(False, False)
        self.fit_data()

    def add_marker(self, x: float, y: float, color: str = "#E49A2F") -> None:
        marker = self.plot.plot(
            [x], [y], pen=None, symbol="o", symbolSize=7, symbolBrush=color, symbolPen=None
        )
        self._markers.append(marker)

    def clear_series(self) -> None:
        for curve in self._curves.values():
            self.plot.removeItem(curve)
        for marker in self._markers:
            self.plot.removeItem(marker)
        for fill, lower_curve, upper_curve in self._fills:
            self.plot.removeItem(fill)
            self.plot.removeItem(lower_curve)
            self.plot.removeItem(upper_curve)
        if self._color_bar is not None:
            try:
                self._color_bar.close()
            except (AttributeError, RuntimeError):
                pass
            self._color_bar = None
        if self._image_item is not None:
            self.plot.removeItem(self._image_item)
            self._image_item = None
        self._curves.clear()
        self._markers.clear()
        self._fills.clear()
        self.legend.clear()

    def series_count(self) -> int:
        return len(self._curves)

    def set_region(self, start: float, end: float, *, visible: bool = True) -> None:
        self.region.blockSignals(True)
        self.region.setRegion((float(start), float(end)))
        self.region.blockSignals(False)
        self.region.setVisible(visible)
        self._region_enabled = visible
        self.tool_buttons["region"].setChecked(visible)

    def selected_region(self) -> tuple[float, float]:
        start, end = self.region.getRegion()
        return float(start), float(end)

    def fit_data(self) -> None:
        self.plot.enableAutoRange()

    def set_x_range(self, start: float, end: float, *, padding: float = 0.01) -> None:
        if end > start:
            self.plot.setXRange(float(start), float(end), padding=padding)

    def set_log_mode(self, logarithmic_x: bool, logarithmic_y: bool) -> None:
        self._logarithmic_x = bool(logarithmic_x)
        self._logarithmic_y = bool(logarithmic_y)
        self.plot.setLogMode(x=self._logarithmic_x, y=self._logarithmic_y)

    def set_grid_visible(self, visible: bool) -> None:
        self._grid_visible = bool(visible)
        self.plot.showGrid(x=visible, y=visible, alpha=0.22)
        self.tool_buttons["grid"].setChecked(visible)

    def set_legend_visible(self, visible: bool) -> None:
        self._legend_visible = bool(visible)
        self.legend.setVisible(visible and bool(self._curves))
        self.tool_buttons["legend"].setChecked(visible)

    def apply_theme(self, theme: str) -> None:
        self._theme = "dark" if theme == "dark" else "light"
        dark = self._theme == "dark"
        foreground = "#AFC1C9" if dark else "#526A75"
        background = "#0B202B" if dark else "#FBFCFC"
        self.plot.setBackground(background)
        self.legend.setBrush(pg.mkBrush("#102833DD" if dark else "#FFFFFFDD"))
        self.legend.setPen(pg.mkPen("#36505C" if dark else "#C7D2D7"))
        for axis_name in ("left", "bottom"):
            axis = self.plot.getAxis(axis_name)
            axis.setPen(pg.mkPen("#36505C" if dark else "#B7C6CD"))
            axis.setTextPen(pg.mkPen(foreground))

    def _activate_tool(self, tool: str, checked: bool) -> None:
        view_box = self.plot.getViewBox()
        if tool == "cursor":
            self._cursor_enabled = checked
            self.cursor_v.setVisible(checked)
            self.cursor_h.setVisible(checked)
        elif tool == "region":
            self._region_enabled = checked
            self.region.setVisible(checked)
            if checked and self._curves:
                left, right = view_box.viewRange()[0]
                self.region.setRegion((left + 0.2 * (right - left), left + 0.8 * (right - left)))
        elif tool == "pan":
            view_box.setMouseMode(pg.ViewBox.PanMode if checked else pg.ViewBox.RectMode)
        elif tool == "grid":
            self.set_grid_visible(checked)
        elif tool == "legend":
            self.set_legend_visible(checked)
        elif tool == "zoom_in":
            view_box.scaleBy((0.75, 0.75))
        elif tool == "zoom_out":
            view_box.scaleBy((1.35, 1.35))
        elif tool == "fit":
            self.fit_data()
        elif tool == "export":
            self._export_image()

    def _mouse_moved(self, position) -> None:
        if not self._cursor_enabled or not self.plot.sceneBoundingRect().contains(position):
            return
        point = self.plot.getViewBox().mapSceneToView(position)
        self.cursor_v.setPos(point.x())
        self.cursor_h.setPos(point.y())
        self.cursor_moved.emit(float(point.x()), float(point.y()))

    def _emit_region(self) -> None:
        self.region_changed.emit(*self.selected_region())

    def _export_image(self) -> None:
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Exporter le graphe",
            str(Path.cwd() / "graphe.png"),
            "Image PNG (*.png);;Graphique vectoriel SVG (*.svg)",
        )
        if not file_path:
            return
        if Path(file_path).suffix.lower() == ".svg":
            exporter = pg.exporters.SVGExporter(self.plot.plotItem)
        else:
            exporter = pg.exporters.ImageExporter(self.plot.plotItem)
            exporter.parameters()["width"] = 1800
        exporter.export(file_path)
