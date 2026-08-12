"""High-performance interactive plots used by CHNeoWave workstations."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

import numpy as np
import pyqtgraph as pg
from PySide6.QtCore import Signal


@dataclass(frozen=True)
class PlotSeries:
    """One named scientific curve."""

    name: str
    x: np.ndarray
    y: np.ndarray
    color: str
    width: float = 1.25
    style: object | None = None


PLOT_PALETTES = {
    "light": {
        "background": "#FFFFFF",
        "foreground": "#405965",
        "grid": "#B7C6CD",
        "accent": "#137E92",
        "warning": "#C47B18",
        "selection": "#42B8C6",
    },
    "dark": {
        "background": "#081820",
        "foreground": "#B9C9D1",
        "grid": "#315563",
        "accent": "#45D4E7",
        "warning": "#E5A84B",
        "selection": "#45D4E7",
    },
}


class ScientificPlotWidget(pg.PlotWidget):
    """Instrument-style plot with cursor, range selection and large-data support."""

    cursor_moved = Signal(float, float)
    region_changed = Signal(float, float)

    def __init__(
        self,
        *,
        x_label: str,
        y_label: str,
        x_unit: str = "",
        y_unit: str = "",
        parent=None,
    ):
        super().__init__(parent=parent)
        self.setObjectName("scientificPlot")
        self.plot_item = self.getPlotItem()
        self.plot_item.setMenuEnabled(False)
        self.plot_item.showGrid(x=True, y=True, alpha=0.22)
        self.plot_item.setDownsampling(auto=True, mode="peak")
        self.plot_item.setClipToView(True)
        self.plot_item.setLabel("bottom", x_label, units=x_unit or None)
        self.plot_item.setLabel("left", y_label, units=y_unit or None)
        self.plot_item.hideButtons()

        self._theme = "light"
        self._y_log = False
        self._data_items: list[object] = []
        self._legend = self.plot_item.addLegend(offset=(8, 8), brush=None, pen=None)
        self._cursor_enabled = True
        self._region_enabled = False
        self._secondary_view: pg.ViewBox | None = None
        self._secondary_curve: pg.PlotCurveItem | None = None

        self._v_cursor = pg.InfiniteLine(angle=90, movable=False)
        self._h_cursor = pg.InfiniteLine(angle=0, movable=False)
        self._v_cursor.setZValue(100)
        self._h_cursor.setZValue(100)
        self.plot_item.addItem(self._v_cursor, ignoreBounds=True)
        self.plot_item.addItem(self._h_cursor, ignoreBounds=True)

        self._region = pg.LinearRegionItem(values=(0.0, 1.0), movable=True)
        self._region.setZValue(20)
        self._region.hide()
        self.plot_item.addItem(self._region, ignoreBounds=True)
        self._region.sigRegionChangeFinished.connect(self._emit_region)

        self._mouse_proxy = pg.SignalProxy(
            self.scene().sigMouseMoved,
            rateLimit=60,
            slot=self._on_mouse_moved,
        )
        self.setMinimumHeight(250)
        self.set_theme("light")

    @property
    def series_count(self) -> int:
        return sum(isinstance(item, pg.PlotDataItem) for item in self._data_items)

    def set_theme(self, theme: str) -> None:
        self._theme = "dark" if theme == "dark" else "light"
        palette = PLOT_PALETTES[self._theme]
        self.setBackground(palette["background"])
        for axis_name in ("left", "bottom", "right", "top"):
            axis = self.plot_item.getAxis(axis_name)
            axis.setPen(pg.mkPen(palette["grid"], width=1))
            axis.setTextPen(pg.mkPen(palette["foreground"]))
        cursor_pen = pg.mkPen(palette["foreground"], width=0.8, style=pg.QtCore.Qt.PenStyle.DashLine)
        self._v_cursor.setPen(cursor_pen)
        self._h_cursor.setPen(cursor_pen)
        self._region.setBrush(pg.mkBrush(palette["selection"] + "28"))
        self._region.setHoverBrush(pg.mkBrush(palette["selection"] + "40"))
        for boundary in self._region.lines:
            boundary.setPen(pg.mkPen(palette["selection"], width=1.1))
            boundary.setHoverPen(pg.mkPen(palette["selection"], width=1.7))

    def set_axis_labels(
        self,
        *,
        x_label: str | None = None,
        y_label: str | None = None,
        x_unit: str | None = None,
        y_unit: str | None = None,
    ) -> None:
        if x_label is not None:
            self.plot_item.setLabel("bottom", x_label, units=x_unit or None)
        if y_label is not None:
            self.plot_item.setLabel("left", y_label, units=y_unit or None)

    def set_cursor_enabled(self, enabled: bool) -> None:
        self._cursor_enabled = bool(enabled)
        self._v_cursor.setVisible(self._cursor_enabled)
        self._h_cursor.setVisible(self._cursor_enabled)

    def set_region_enabled(self, enabled: bool) -> None:
        self._region_enabled = bool(enabled)
        self._region.setVisible(self._region_enabled)

    def set_region(self, start: float, end: float, *, bounds: tuple[float, float] | None = None) -> None:
        if bounds is not None:
            self._region.setBounds(bounds)
        self._region.setRegion((float(start), float(end)))

    def region(self) -> tuple[float, float]:
        start, end = self._region.getRegion()
        return float(start), float(end)

    def clear_data(self) -> None:
        for item in self._data_items:
            try:
                self.plot_item.removeItem(item)
            except Exception:  # pragma: no cover - Qt item can already be detached
                pass
        self._data_items.clear()
        self._legend.clear()
        if self._secondary_curve is not None and self._secondary_view is not None:
            self._secondary_view.removeItem(self._secondary_curve)
            self._secondary_curve = None
        self.plot_item.hideAxis("right")

    def set_series(self, series: Iterable[PlotSeries], *, y_log: bool = False) -> None:
        self.clear_data()
        self._y_log = bool(y_log)
        self.plot_item.setLogMode(x=False, y=self._y_log)
        for definition in series:
            x = np.asarray(definition.x, dtype=float)
            y = np.asarray(definition.y, dtype=float)
            valid = np.isfinite(x) & np.isfinite(y)
            if y_log:
                valid &= y > 0
            if not np.any(valid):
                continue
            pen = pg.mkPen(definition.color, width=definition.width, style=definition.style)
            curve = self.plot_item.plot(
                x[valid],
                y[valid],
                pen=pen,
                name=definition.name,
                antialias=False,
                connect="finite",
            )
            curve.setDownsampling(auto=True, method="peak")
            curve.setClipToView(True)
            self._data_items.append(curve)

    def add_horizontal_guide(
        self,
        value: float,
        *,
        color: str,
        dashed: bool = False,
    ) -> None:
        style = pg.QtCore.Qt.PenStyle.DashLine if dashed else pg.QtCore.Qt.PenStyle.SolidLine
        guide = pg.InfiniteLine(
            pos=float(value), angle=0, movable=False, pen=pg.mkPen(color, width=0.9, style=style)
        )
        self.plot_item.addItem(guide)
        self._data_items.append(guide)

    def add_confidence_band(
        self,
        x: np.ndarray,
        lower: np.ndarray,
        upper: np.ndarray,
        *,
        color: str,
    ) -> None:
        lower_curve = pg.PlotCurveItem(x, lower, pen=pg.mkPen(color + "55", width=0.7))
        upper_curve = pg.PlotCurveItem(x, upper, pen=pg.mkPen(color + "55", width=0.7))
        band = pg.FillBetweenItem(lower_curve, upper_curve, brush=pg.mkBrush(color + "24"))
        for item in (lower_curve, upper_curve, band):
            self.plot_item.addItem(item)
            self._data_items.append(item)

    def add_target(self, x: float, y: float, *, label: str = "") -> None:
        palette = PLOT_PALETTES[self._theme]
        target_y = float(np.log10(y)) if self._y_log and y > 0 else float(y)
        target = pg.TargetItem(
            pos=(float(x), target_y),
            size=11,
            symbol="o",
            pen=pg.mkPen(palette["warning"], width=1.5),
            brush=pg.mkBrush(palette["background"]),
            label=label,
            labelOpts={"color": palette["warning"]},
        )
        self.plot_item.addItem(target)
        self._data_items.append(target)

    def set_secondary_series(
        self,
        x: np.ndarray,
        y: np.ndarray,
        *,
        label: str,
        unit: str,
        color: str,
    ) -> None:
        if self._secondary_view is None:
            self._secondary_view = pg.ViewBox()
            self.plot_item.scene().addItem(self._secondary_view)
            self.plot_item.getAxis("right").linkToView(self._secondary_view)
            self._secondary_view.setXLink(self.plot_item)
            self.plot_item.vb.sigResized.connect(self._update_secondary_geometry)
        self.plot_item.showAxis("right")
        self.plot_item.setLabel("right", label, units=unit)
        self._update_secondary_geometry()
        self._secondary_view.setYRange(0.0, 105.0, padding=0.0)
        self._secondary_curve = pg.PlotCurveItem(
            np.asarray(x, dtype=float),
            np.asarray(y, dtype=float),
            pen=pg.mkPen(color, width=1.1, style=pg.QtCore.Qt.PenStyle.DashLine),
        )
        self._secondary_view.addItem(self._secondary_curve)

    def auto_range(self) -> None:
        self.plot_item.enableAutoRange(x=True, y=True)
        self.plot_item.autoRange()

    def export_png(self, file_path: str) -> bool:
        return bool(self.grab().save(file_path, "PNG"))

    def _emit_region(self) -> None:
        start, end = self.region()
        self.region_changed.emit(start, end)

    def _on_mouse_moved(self, event) -> None:
        if not self._cursor_enabled or not event:
            return
        position = event[0]
        if not self.plot_item.sceneBoundingRect().contains(position):
            return
        point = self.plot_item.vb.mapSceneToView(position)
        x_value = float(point.x())
        y_value = float(point.y())
        self._v_cursor.setPos(x_value)
        self._h_cursor.setPos(y_value)
        self.cursor_moved.emit(x_value, y_value)

    def _update_secondary_geometry(self) -> None:
        if self._secondary_view is None:
            return
        self._secondary_view.setGeometry(self.plot_item.vb.sceneBoundingRect())
        self._secondary_view.linkedViewChanged(
            self.plot_item.vb,
            self._secondary_view.XAxis,
        )
