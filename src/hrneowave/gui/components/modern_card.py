"""Neutral section surface used by the project settings workspace."""

from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget


class ModernCard(QFrame):
    """Compatibility section container governed entirely by the global theme."""

    def __init__(self, title: str = "", parent=None):
        super().__init__(parent)
        self.title = title
        self.setObjectName("settingsSection")
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        self.title_label = None
        if title:
            header = QFrame()
            header.setObjectName("settingsSectionHeader")
            header_layout = QHBoxLayout(header)
            header_layout.setContentsMargins(10, 7, 10, 7)
            self.title_label = QLabel(title)
            self.title_label.setObjectName("sectionTitle")
            header_layout.addWidget(self.title_label)
            header_layout.addStretch()
            root.addWidget(header)
        self.content_widget = QWidget()
        self.content_widget.setObjectName("settingsSectionContent")
        root.addWidget(self.content_widget)

    def set_title(self, title: str) -> None:
        self.title = title
        if self.title_label is not None:
            self.title_label.setText(title)

    def get_content_widget(self) -> QWidget:
        return self.content_widget

    def add_content_layout(self, layout) -> None:
        self.content_widget.setLayout(layout)

    def set_content_widget(self, widget: QWidget) -> None:
        self.layout().replaceWidget(self.content_widget, widget)
        self.content_widget.deleteLater()
        self.content_widget = widget
        self.content_widget.setObjectName("settingsSectionContent")

    def animate_entrance(self) -> None:
        return
