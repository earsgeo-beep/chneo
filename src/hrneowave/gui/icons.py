"""Vector icon and brand primitives for the CHNeoWave instrument interface.

The application deliberately owns this small line-icon set instead of mixing
font glyphs, emoji and platform-dependent symbols.  SVGs are rendered by Qt at
the requested size, so they remain crisp on high-DPI laboratory displays.
"""

from __future__ import annotations

from PySide6.QtCore import QByteArray, QRectF, QSize, Qt
from PySide6.QtGui import QColor, QIcon, QPainter, QPainterPath, QPen, QPixmap
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import QWidget

_PATHS: dict[str, str] = {
    "menu": '<path d="M4 7h16M4 12h16M4 17h16"/>',
    "collapse": '<path d="m14.5 5-7 7 7 7"/><path d="M19 5v14"/>',
    "expand": '<path d="m9.5 5 7 7-7 7"/><path d="M5 5v14"/>',
    "project": '<path d="M3.5 6.5h6l2 2h9v9.5a2 2 0 0 1-2 2h-13a2 2 0 0 1-2-2z"/><path d="M3.5 10h17"/>',
    "system": (
        '<rect x="4" y="4" width="6" height="6" rx="1"/>'
        '<rect x="14" y="4" width="6" height="6" rx="1"/>'
        '<rect x="4" y="14" width="6" height="6" rx="1"/>'
        '<path d="M14 17h6M17 14v6"/>'
    ),
    "calibration": (
        '<path d="M4 6h7M15 6h5M4 12h3M11 12h9M4 18h9M17 18h3"/>'
        '<circle cx="13" cy="6" r="2"/><circle cx="9" cy="12" r="2"/>'
        '<circle cx="15" cy="18" r="2"/>'
    ),
    "acquisition": '<path d="M3 13h3l2.2-6 3.4 11 2.7-8 2.2 3H21"/><path d="M4 4v16h16"/>',
    "analysis": (
        '<path d="M3 17c2.2 0 2.4-10 5-10s2.4 10 5 10 2.4-10 5-10c1.2 0 2 2 3 4"/><path d="M3 21h18"/>'
    ),
    "report": '<path d="M6 3.5h8l4 4V21H6z"/><path d="M14 3.5V8h4M9 12h6M9 16h6"/>',
    "settings": (
        '<circle cx="12" cy="12" r="3"/>'
        '<path d="M12 3v2M12 19v2M3 12h2M19 12h2M5.6 5.6 7 7'
        'M17 17l1.4 1.4M18.4 5.6 17 7M7 17l-1.4 1.4"/>'
    ),
    "sun": (
        '<circle cx="12" cy="12" r="3.5"/>'
        '<path d="M12 2.5v2M12 19.5v2M2.5 12h2M19.5 12h2M5.3 5.3l1.4 1.4'
        'M17.3 17.3l1.4 1.4M18.7 5.3l-1.4 1.4M6.7 17.3l-1.4 1.4"/>'
    ),
    "moon": '<path d="M19.5 15.2A8 8 0 0 1 8.8 4.5 8.2 8.2 0 1 0 19.5 15.2z"/>',
    "hardware": (
        '<rect x="6" y="6" width="12" height="12" rx="2"/>'
        '<path d="M9 1.8v4.2M15 1.8v4.2M9 18v4.2M15 18v4.2M1.8 9H6M18 9h4.2'
        'M1.8 15H6M18 15h4.2M9.5 10h5v4h-5z"/>'
    ),
    "offline": (
        '<path d="M4 15.5a11.8 11.8 0 0 1 16 0M7 18.5a7.5 7.5 0 0 1 10 0'
        'M10.2 21a2.8 2.8 0 0 1 3.6 0"/><path d="M4 4l16 16"/>'
    ),
    "open": '<path d="M4 19V6h6l2 2h8v11z"/><path d="M9 14h6M12 11v6"/>',
    "refresh": '<path d="M20 7v5h-5"/><path d="M18.5 16.5A8 8 0 1 1 20 12"/>',
    "play": '<path d="m8 5 11 7-11 7z"/>',
    "export": '<path d="M12 3v12M7.5 7.5 12 3l4.5 4.5"/><path d="M5 13v7h14v-7"/>',
    "fit": '<path d="M4 9V4h5M15 4h5v5M20 15v5h-5M9 20H4v-5"/><path d="M8 12h8"/>',
    "cursor": '<path d="m6 3 12 9-6 1.5-2.5 6z"/>',
    "region": '<rect x="5" y="4" width="14" height="16" rx="1"/><path d="M9 4v16M15 4v16"/>',
    "image": (
        '<rect x="3.5" y="4.5" width="17" height="15" rx="2"/>'
        '<circle cx="9" cy="10" r="2"/><path d="m5.5 17 4.5-4 3 2.5 2.5-2 3 3.5"/>'
    ),
    "info": '<circle cx="12" cy="12" r="9"/><path d="M12 11v6M12 7.5h.01"/>',
    "check": '<circle cx="12" cy="12" r="9"/><path d="m8 12 2.7 2.7L16.5 9"/>',
    "warning": '<path d="M12 3 2.8 20h18.4z"/><path d="M12 9v5M12 17.5h.01"/>',
    "error": '<circle cx="12" cy="12" r="9"/><path d="m9 9 6 6M15 9l-6 6"/>',
}


def svg_icon(name: str, color: str = "#667C88", size: int = 18) -> QIcon:
    """Return a theme-aware monochrome SVG icon."""

    body = _PATHS.get(name, _PATHS["system"])
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" '
        'viewBox="0 0 24 24" fill="none" '
        f'stroke="{color}" stroke-width="1.7" stroke-linecap="round" '
        f'stroke-linejoin="round">{body}</svg>'
    )
    renderer = QSvgRenderer(QByteArray(svg.encode("utf-8")))
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    return QIcon(pixmap)


def brand_icon(size: int = 64) -> QIcon:
    """Return the two-colour CHNeoWave application icon."""

    svg = """<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64">
    <rect x="3" y="3" width="58" height="58" rx="12" fill="#126F86"/>
    <path d="M10 37c7-9 13-9 20 0s14 9 24-1M12 46c7-6 13-6 20 0s13 6 20-1"
          fill="none" stroke="#E9FBFD" stroke-width="3.2" stroke-linecap="round"/>
    <path d="M32 13v25" fill="none" stroke="#7DE5EE" stroke-width="3" stroke-linecap="round"/>
    <circle cx="32" cy="14" r="4.5" fill="#7DE5EE"/>
    </svg>"""
    renderer = QSvgRenderer(QByteArray(svg.encode("utf-8")))
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    return QIcon(pixmap)


class BrandMark(QWidget):
    """CHNeoWave mark: a measurement probe crossing a two-layer wave."""

    def __init__(self, parent=None, size: int = 36):
        super().__init__(parent)
        self._theme = "light"
        self.setFixedSize(size, size)
        self.setAccessibleName("CHNeoWave")
        self.setToolTip("CHNeoWave · Station d'analyse maritime")

    def sizeHint(self) -> QSize:  # noqa: N802 - Qt API
        return self.size()

    def set_theme(self, theme: str) -> None:
        self._theme = "dark" if theme == "dark" else "light"
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802 - Qt API
        del event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        bounds = QRectF(self.rect()).adjusted(1.0, 1.0, -1.0, -1.0)
        background = QColor("#123947" if self._theme == "dark" else "#126F86")
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(background)
        painter.drawRoundedRect(bounds, 7.0, 7.0)

        scale_x = self.width() / 36.0
        scale_y = self.height() / 36.0
        painter.scale(scale_x, scale_y)
        wave_pen = QPen(QColor("#E9FBFD"), 1.8)
        wave_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(wave_pen)
        wave = QPainterPath()
        wave.moveTo(6, 20)
        wave.cubicTo(10, 15, 13, 15, 17, 20)
        wave.cubicTo(21, 25, 25, 25, 30, 19)
        painter.drawPath(wave)
        lower_wave = QPainterPath()
        lower_wave.moveTo(7, 25)
        lower_wave.cubicTo(11, 22, 14, 22, 18, 25)
        lower_wave.cubicTo(22, 28, 25, 28, 29, 24)
        painter.setOpacity(0.65)
        painter.drawPath(lower_wave)

        painter.setOpacity(1.0)
        probe_pen = QPen(QColor("#7DE5EE"), 1.7)
        probe_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(probe_pen)
        painter.drawLine(18, 7, 18, 21)
        painter.setBrush(QColor("#7DE5EE"))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QRectF(15.8, 6.0, 4.4, 4.4))
        painter.end()
