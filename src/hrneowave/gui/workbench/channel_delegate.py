"""Compact channel-row renderer without per-row widgets."""

from PySide6.QtCore import QRect, QSize, Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import QStyle, QStyledItemDelegate

from .channel_model import ChannelListModel


class ChannelDelegate(QStyledItemDelegate):
    def sizeHint(self, option, index):  # noqa: N802
        del option, index
        return QSize(154, 42)

    def paint(self, painter: QPainter, option, index) -> None:
        painter.save()
        selected = bool(option.state & QStyle.StateFlag.State_Selected)
        enabled = bool(option.state & QStyle.StateFlag.State_Enabled)
        dark = option.palette.window().color().lightness() < 120
        background = QColor("#18333F" if dark else "#E5EEF2")
        painter.fillRect(option.rect, background if selected else Qt.GlobalColor.transparent)
        if selected:
            painter.fillRect(
                QRect(option.rect.left(), option.rect.top(), 2, option.rect.height()), QColor("#19B5CF")
            )

        check_rect = QRect(option.rect.left() + 8, option.rect.center().y() - 7, 14, 14)
        painter.setPen(QPen(QColor("#78919C" if dark else "#6C7F88"), 1))
        painter.setBrush(
            QColor("#1597B2")
            if index.data(Qt.ItemDataRole.CheckStateRole) == Qt.CheckState.Checked
            else Qt.GlobalColor.transparent
        )
        painter.drawRect(check_rect)
        if index.data(Qt.ItemDataRole.CheckStateRole) == Qt.CheckState.Checked:
            painter.setPen(QPen(QColor("#071A24"), 1.5))
            painter.drawLine(
                check_rect.left() + 3, check_rect.center().y(), check_rect.left() + 6, check_rect.bottom() - 3
            )
            painter.drawLine(
                check_rect.left() + 6, check_rect.bottom() - 3, check_rect.right() - 2, check_rect.top() + 3
            )

        color = QColor(str(index.data(ChannelListModel.ColorRole)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(color)
        painter.drawRect(QRect(option.rect.left() + 29, option.rect.top() + 9, 3, option.rect.height() - 18))

        primary = QRect(option.rect.left() + 38, option.rect.top() + 3, option.rect.width() - 70, 18)
        secondary = QRect(option.rect.left() + 38, option.rect.top() + 20, option.rect.width() - 70, 17)
        font = QFont(option.font)
        font.setPointSizeF(8.5)
        font.setWeight(QFont.Weight.DemiBold)
        painter.setFont(font)
        painter.setPen(
            QColor("#F0F6F8" if dark and enabled else "#18323C" if enabled else "#68808A")
        )
        painter.drawText(primary, Qt.AlignmentFlag.AlignVCenter, str(index.data(Qt.ItemDataRole.DisplayRole)))
        font.setPointSizeF(7.4)
        font.setWeight(QFont.Weight.Normal)
        painter.setFont(font)
        painter.setPen(QColor("#91A8B2" if dark else "#617781"))
        painter.drawText(
            secondary, Qt.AlignmentFlag.AlignVCenter, str(index.data(ChannelListModel.SensorRole))
        )

        unit = str(index.data(ChannelListModel.UnitRole))
        painter.setPen(QColor("#AFC0C7" if dark else "#435D68"))
        painter.drawText(
            QRect(option.rect.right() - 48, option.rect.top() + 5, 34, 18),
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
            unit,
        )
        quality = str(index.data(ChannelListModel.QualityRole))
        qcolor = {
            "nominal": "#42B98E",
            "valid": "#42B98E",
            "warning": "#D49332",
            "critical": "#D45C68",
            "rejected": "#D45C68",
        }.get(quality, "#627A85")
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(qcolor))
        painter.drawEllipse(option.rect.right() - 11, option.rect.center().y() - 3, 6, 6)
        painter.restore()

    def editorEvent(self, event, model, option, index):  # noqa: N802
        if event.type() in (event.Type.MouseButtonRelease, event.Type.MouseButtonDblClick):
            if event.position().x() <= option.rect.left() + 28:
                checked = index.data(Qt.ItemDataRole.CheckStateRole) == Qt.CheckState.Checked
                return model.setData(
                    index,
                    Qt.CheckState.Unchecked if checked else Qt.CheckState.Checked,
                    Qt.ItemDataRole.CheckStateRole,
                )
        return super().editorEvent(event, model, option, index)
