"""Model/view channel browser for dense multi-sensor campaigns."""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import QAbstractListModel, QModelIndex, Qt, Signal
from PySide6.QtGui import QColor


@dataclass(slots=True)
class ChannelItem:
    key: str
    name: str
    sensor: str = "Signal"
    unit: str = "—"
    color: str = "#16A7C5"
    visible: bool = True
    quality: str = "unknown"


class ChannelListModel(QAbstractListModel):
    KeyRole = Qt.ItemDataRole.UserRole + 1
    SensorRole = Qt.ItemDataRole.UserRole + 2
    UnitRole = Qt.ItemDataRole.UserRole + 3
    ColorRole = Qt.ItemDataRole.UserRole + 4
    QualityRole = Qt.ItemDataRole.UserRole + 5
    channel_visibility_changed = Signal(str, bool)

    def __init__(self, channels: list[ChannelItem] | None = None, parent=None):
        super().__init__(parent)
        self._channels = list(channels or [])

    def rowCount(self, parent=None) -> int:  # noqa: N802
        parent = parent or QModelIndex()
        return 0 if parent.isValid() else len(self._channels)

    def data(self, index: QModelIndex, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or not 0 <= index.row() < len(self._channels):
            return None
        item = self._channels[index.row()]
        if role == Qt.ItemDataRole.DisplayRole:
            return item.name
        if role == Qt.ItemDataRole.CheckStateRole:
            return Qt.CheckState.Checked if item.visible else Qt.CheckState.Unchecked
        if role == Qt.ItemDataRole.DecorationRole:
            return QColor(item.color)
        if role == self.KeyRole:
            return item.key
        if role == self.SensorRole:
            return item.sensor
        if role == self.UnitRole:
            return item.unit
        if role == self.ColorRole:
            return item.color
        if role == self.QualityRole:
            return item.quality
        if role == Qt.ItemDataRole.ToolTipRole:
            return f"{item.key} · {item.sensor} · {item.unit}"
        return None

    def flags(self, index: QModelIndex):
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsUserCheckable

    def setData(self, index: QModelIndex, value, role=Qt.ItemDataRole.EditRole):  # noqa: N802
        if role != Qt.ItemDataRole.CheckStateRole or not index.isValid():
            return False
        item = self._channels[index.row()]
        item.visible = value == Qt.CheckState.Checked
        self.dataChanged.emit(index, index, [Qt.ItemDataRole.CheckStateRole])
        self.channel_visibility_changed.emit(item.key, item.visible)
        return True

    def set_channels(self, channels: list[ChannelItem]) -> None:
        self.beginResetModel()
        self._channels = list(channels)
        self.endResetModel()

    def channel(self, row: int) -> ChannelItem | None:
        return self._channels[row] if 0 <= row < len(self._channels) else None

    def visible_keys(self) -> list[str]:
        return [item.key for item in self._channels if item.visible]

    def set_all_visible(self, visible: bool) -> None:
        if not self._channels:
            return
        for item in self._channels:
            item.visible = bool(visible)
        self.dataChanged.emit(
            self.index(0, 0),
            self.index(len(self._channels) - 1, 0),
            [Qt.ItemDataRole.CheckStateRole],
        )
        for item in self._channels:
            self.channel_visibility_changed.emit(item.key, item.visible)

    def set_only_visible(self, key: str) -> None:
        if not self._channels:
            return
        for item in self._channels:
            item.visible = item.key == key
        self.dataChanged.emit(
            self.index(0, 0),
            self.index(len(self._channels) - 1, 0),
            [Qt.ItemDataRole.CheckStateRole],
        )
        for item in self._channels:
            self.channel_visibility_changed.emit(item.key, item.visible)

    def set_quality(self, key: str, quality: str) -> None:
        for row, item in enumerate(self._channels):
            if item.key == key:
                item.quality = quality
                index = self.index(row, 0)
                self.dataChanged.emit(index, index, [self.QualityRole])
                return
