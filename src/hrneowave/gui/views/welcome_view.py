"""Project entry point for CHNeoWave."""

from PySide6.QtCore import QDate, Qt, Signal
from PySide6.QtWidgets import (
    QDateEdit,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class WelcomeView(QWidget):
    """Focused project creation screen without decorative distractions."""

    projectSelected = Signal(str)
    projectCreationRequested = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.project_metadata = {}
        self._build_ui()
        self._setup_connections()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(18)

        intro = QLabel("Démarrer une campagne d'essais")
        intro.setObjectName("viewTitle")
        description = QLabel(
            "Le projet relie la configuration des capteurs, l'équipement d'acquisition, "
            "l'analyse scientifique et le rapport final."
        )
        description.setObjectName("mutedText")
        description.setWordWrap(True)
        root.addWidget(intro)
        root.addWidget(description)

        content = QHBoxLayout()
        content.setSpacing(18)

        form_card = QFrame()
        form_card.setObjectName("projectForm")
        form_layout = QVBoxLayout(form_card)
        form_layout.setContentsMargins(22, 20, 22, 20)
        form_layout.setSpacing(16)

        form_title = QLabel("Nouveau projet")
        form_title.setObjectName("sectionTitle")
        form_hint = QLabel("Les champs marqués * assurent la traçabilité du dossier.")
        form_hint.setObjectName("mutedText")
        form_layout.addWidget(form_title)
        form_layout.addWidget(form_hint)

        fields = QFormLayout()
        fields.setHorizontalSpacing(18)
        fields.setVerticalSpacing(12)
        fields.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)

        self.project_name = QLineEdit()
        self.project_name.setPlaceholderText("Ex. Essais de houle – bassin 02")
        self.project_manager = QLineEdit()
        self.project_manager.setPlaceholderText("Responsable de la campagne")
        self.laboratory = QLineEdit()
        self.laboratory.setPlaceholderText("Laboratoire / organisme")
        self.project_date = QDateEdit(QDate.currentDate())
        self.project_date.setCalendarPopup(True)
        self.water_depth = QDoubleSpinBox()
        self.water_depth.setRange(0.0, 50.0)
        self.water_depth.setDecimals(4)
        self.water_depth.setSingleStep(0.01)
        self.water_depth.setSpecialValueText("Non renseignée")
        self.water_depth.setSuffix(" m")
        self.description = QTextEdit()
        self.description.setPlaceholderText(
            "Objectif, modèle physique, conditions d'essai et remarques utiles."
        )
        self.description.setMaximumHeight(95)

        fields.addRow("Nom du projet *", self.project_name)
        fields.addRow("Responsable *", self.project_manager)
        fields.addRow("Laboratoire *", self.laboratory)
        fields.addRow("Date d'essai", self.project_date)
        fields.addRow("Profondeur d'eau", self.water_depth)
        fields.addRow("Contexte", self.description)
        form_layout.addLayout(fields)

        actions = QHBoxLayout()
        self.open_button = QPushButton("Ouvrir un projet")
        self.open_button.setProperty("kind", "secondary")
        self.create_button = QPushButton("Créer et continuer")
        self.create_button.setProperty("kind", "primaryLarge")
        self.create_button.setEnabled(False)
        actions.addWidget(self.open_button)
        actions.addStretch()
        actions.addWidget(self.create_button)
        form_layout.addLayout(actions)

        context_card = QFrame()
        context_card.setObjectName("contextPanel")
        context_card.setMaximumWidth(350)
        context_layout = QVBoxLayout(context_card)
        context_layout.setContentsMargins(22, 20, 22, 20)
        context_layout.setSpacing(14)

        context_title = QLabel("Dossier expérimental")
        context_title.setObjectName("sectionTitle")
        context_layout.addWidget(context_title)
        context_layout.addWidget(
            self._context_item(
                "01  Configuration",
                "Équipement, pilote, canaux, capteurs, unités et certificats de calibration.",
            )
        )
        context_layout.addWidget(
            self._context_item(
                "02  Données brutes",
                "Session HDF5 continue, horodatée et contrôlée avant analyse.",
            )
        )
        context_layout.addWidget(
            self._context_item(
                "03  Résultats",
                "Spectres, paramètres de houle, contrôles qualité et exports.",
            )
        )
        context_layout.addStretch()

        local_note = QLabel("FONCTIONNEMENT LOCAL · AUCUN INTERNET REQUIS")
        local_note.setProperty("state", "success")
        local_note.setAlignment(Qt.AlignmentFlag.AlignCenter)
        context_layout.addWidget(local_note)

        content.addWidget(form_card, 3)
        content.addWidget(context_card, 2)
        root.addLayout(content, 1)

    @staticmethod
    def _context_item(title: str, text: str) -> QFrame:
        frame = QFrame()
        frame.setObjectName("quietSurface")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(4)
        title_label = QLabel(title)
        title_label.setObjectName("sectionTitle")
        text_label = QLabel(text)
        text_label.setObjectName("mutedText")
        text_label.setWordWrap(True)
        layout.addWidget(title_label)
        layout.addWidget(text_label)
        return frame

    def _setup_connections(self) -> None:
        self.project_name.textChanged.connect(self._validate_form)
        self.project_manager.textChanged.connect(self._validate_form)
        self.laboratory.textChanged.connect(self._validate_form)
        self.create_button.clicked.connect(self._create_project)
        self.open_button.clicked.connect(self._open_existing_project)

    def _validate_form(self) -> None:
        is_valid = all(
            (
                len(self.project_name.text().strip()) >= 3,
                len(self.project_manager.text().strip()) >= 2,
                len(self.laboratory.text().strip()) >= 2,
            )
        )
        self.create_button.setEnabled(is_valid)

    def _create_project(self) -> None:
        self.project_metadata = {
            "name": self.project_name.text().strip(),
            "manager": self.project_manager.text().strip(),
            "laboratory": self.laboratory.text().strip(),
            "date": self.project_date.date().toString(Qt.DateFormat.ISODate),
            "description": self.description.toPlainText().strip(),
            "created_at": QDate.currentDate().toString(Qt.DateFormat.ISODate),
            "water_depth_m": (self.water_depth.value() if self.water_depth.value() > 0 else None),
        }
        self.projectCreationRequested.emit(self.project_metadata)

    def _open_existing_project(self) -> None:
        project_path = QFileDialog.getExistingDirectory(self, "Ouvrir un projet CHNeoWave")
        if project_path:
            self.projectSelected.emit(project_path)

    def reset_view(self) -> None:
        self.project_name.clear()
        self.project_manager.clear()
        self.laboratory.clear()
        self.description.clear()
        self.project_date.setDate(QDate.currentDate())
        self.water_depth.setValue(0.0)
        self.create_button.setEnabled(False)

    def get_project_metadata(self) -> dict:
        return self.project_metadata
