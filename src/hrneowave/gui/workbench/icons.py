"""Small monochrome engineering icons drawn with Qt vector primitives.

The interface deliberately avoids emoji, platform fonts and decorative icon
packs: every symbol is rendered from the same 20 x 20 construction grid.
"""

from __future__ import annotations

from PySide6.QtCore import QPointF, QRectF, QSize, Qt
from PySide6.QtGui import QColor, QIcon, QIconEngine, QPainter, QPainterPath, QPen, QPixmap


class _LineIconEngine(QIconEngine):
    def __init__(self, name: str, color: str):
        super().__init__()
        self.name = name
        self.color = QColor(color)

    def clone(self):
        return _LineIconEngine(self.name, self.color.name())

    def pixmap(self, size: QSize, mode: QIcon.Mode, state: QIcon.State) -> QPixmap:
        pixmap = QPixmap(size)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.paint(painter, QRectF(pixmap.rect()), mode, state)
        painter.end()
        return pixmap

    def paint(self, painter: QPainter, rect, mode: QIcon.Mode, state: QIcon.State) -> None:
        del state
        color = QColor(self.color)
        if mode == QIcon.Mode.Disabled:
            color.setAlpha(90)
        scale = min(rect.width(), rect.height()) / 20.0
        painter.save()
        painter.translate(rect.center())
        painter.scale(scale, scale)
        painter.translate(-10.0, -10.0)
        pen = QPen(color, 1.55, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        self._draw(painter)
        painter.restore()

    def _draw(self, p: QPainter) -> None:
        n = self.name
        if n == "brand":
            p.drawLine(QPointF(3, 14), QPointF(3, 6))
            p.drawLine(QPointF(17, 14), QPointF(17, 6))
            path = QPainterPath(QPointF(3, 11))
            path.cubicTo(6, 7, 8, 15, 11, 10)
            path.cubicTo(13, 7, 15, 9, 17, 7)
            p.drawPath(path)
        elif n == "projects":
            p.drawRect(QRectF(3, 5, 14, 11))
            p.drawLine(3, 8, 17, 8)
            p.drawLine(7, 5, 8, 3)
            p.drawLine(8, 3, 12, 3)
            p.drawLine(12, 3, 13, 5)
        elif n == "dashboard":
            for r in (QRectF(3, 3, 6, 6), QRectF(11, 3, 6, 6), QRectF(3, 11, 6, 6), QRectF(11, 11, 6, 6)):
                p.drawRect(r)
        elif n == "calibration":
            p.drawLine(3, 14, 7, 10)
            p.drawLine(7, 10, 10, 12)
            p.drawLine(10, 12, 17, 5)
            p.drawEllipse(QPointF(7, 10), 1.4, 1.4)
            p.drawLine(3, 17, 17, 17)
        elif n == "acquisition":
            p.drawRect(QRectF(3, 5, 14, 10))
            p.drawEllipse(QPointF(7, 10), 2.2, 2.2)
            p.drawLine(11, 8, 15, 8)
            p.drawLine(11, 11, 15, 11)
        elif n == "analysis":
            path = QPainterPath(QPointF(2, 11))
            path.cubicTo(5, 11, 5, 5, 8, 5)
            path.cubicTo(11, 5, 10, 15, 13, 15)
            path.cubicTo(15, 15, 16, 10, 18, 10)
            p.drawPath(path)
        elif n == "report":
            p.drawRect(QRectF(4, 2.5, 12, 15))
            p.drawLine(7, 7, 13, 7)
            p.drawLine(7, 10, 13, 10)
            p.drawLine(7, 13, 11, 13)
        elif n == "settings":
            p.drawEllipse(QPointF(10, 10), 3, 3)
            for a, b in (
                ((10, 2), (10, 5)),
                ((10, 15), (10, 18)),
                ((2, 10), (5, 10)),
                ((15, 10), (18, 10)),
                ((4.4, 4.4), (6.5, 6.5)),
                ((13.5, 13.5), (15.6, 15.6)),
                ((15.6, 4.4), (13.5, 6.5)),
                ((6.5, 13.5), (4.4, 15.6)),
            ):
                p.drawLine(QPointF(*a), QPointF(*b))
        elif n == "theme":
            p.drawEllipse(QPointF(10, 10), 6, 6)
            p.setBrush(self.color)
            p.drawPie(QRectF(4, 4, 12, 12), 90 * 16, 180 * 16)
            p.setBrush(Qt.BrushStyle.NoBrush)
        elif n == "folder":
            p.drawPath(QPainterPath(QPointF(2.5, 6)))
            p.drawRect(QRectF(2.5, 6, 15, 10))
            p.drawLine(3, 6, 3, 4)
            p.drawLine(3, 4, 8, 4)
            p.drawLine(8, 4, 10, 6)
        elif n == "run":
            path = QPainterPath(QPointF(6, 3))
            path.lineTo(16, 10)
            path.lineTo(6, 17)
            path.closeSubpath()
            p.drawPath(path)
        elif n == "cursor":
            p.drawLine(10, 2, 10, 18)
            p.drawLine(2, 10, 18, 10)
            p.drawEllipse(QPointF(10, 10), 2, 2)
        elif n == "region":
            p.drawRect(QRectF(4, 3, 12, 14))
            p.drawLine(7, 3, 7, 17)
            p.drawLine(13, 3, 13, 17)
        elif n == "zoom_in" or n == "zoom_out":
            p.drawEllipse(QPointF(8.5, 8.5), 5, 5)
            p.drawLine(12, 12, 17, 17)
            p.drawLine(6, 8.5, 11, 8.5)
            if n == "zoom_in":
                p.drawLine(8.5, 6, 8.5, 11)
        elif n == "pan":
            p.drawRect(QRectF(6, 5, 8, 10))
            p.drawLine(10, 2, 10, 7)
            p.drawLine(3, 10, 8, 10)
            p.drawLine(12, 10, 17, 10)
            p.drawLine(10, 13, 10, 18)
        elif n == "grid":
            p.drawRect(QRectF(3, 3, 14, 14))
            p.drawLine(7.7, 3, 7.7, 17)
            p.drawLine(12.3, 3, 12.3, 17)
            p.drawLine(3, 7.7, 17, 7.7)
            p.drawLine(3, 12.3, 17, 12.3)
        elif n == "legend":
            for y in (5.0, 10.0, 15.0):
                p.drawLine(3, y, 7, y)
                p.drawLine(10, y, 17, y)
        elif n == "fit":
            p.drawLine(3, 7, 3, 3)
            p.drawLine(3, 3, 7, 3)
            p.drawLine(13, 3, 17, 3)
            p.drawLine(17, 3, 17, 7)
            p.drawLine(3, 13, 3, 17)
            p.drawLine(3, 17, 7, 17)
            p.drawLine(13, 17, 17, 17)
            p.drawLine(17, 17, 17, 13)
        elif n == "export":
            p.drawRect(QRectF(3, 8, 14, 9))
            p.drawLine(10, 2, 10, 12)
            p.drawLine(6.5, 5.5, 10, 2)
            p.drawLine(13.5, 5.5, 10, 2)
        elif n == "menu":
            p.drawLine(4, 5, 16, 5)
            p.drawLine(4, 10, 16, 10)
            p.drawLine(4, 15, 16, 15)
        elif n == "close":
            p.drawLine(4, 4, 16, 16)
            p.drawLine(16, 4, 4, 16)
        else:
            p.drawEllipse(QPointF(10, 10), 6, 6)


def line_icon(name: str, color: str = "#9CB3BE") -> QIcon:
    """Return a high-DPI monochrome icon from the CHNeoWave construction grid."""

    return QIcon(_LineIconEngine(name, color))
