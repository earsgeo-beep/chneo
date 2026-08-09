"""Operational project overview for CHNeoWave."""

from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class DashboardViewMaritime(QWidget):
    """Truthful workflow dashboard: no simulated scientific KPIs."""

    navigation_requested = Signal(str)
    theme_changed = Signal(str)

    WORKFLOW = (
        ("calibration", "01", "Calibration", "Valider les sensibilités, unités et certificats."),
        (
            "acquisition",
            "02",
            "Acquisition",
            "Connecter un équipement physique et enregistrer la session maître.",
        ),
        ("analysis", "03", "Analyse", "Contrôler la qualité, les spectres et les paramètres."),
        ("export", "04", "Rapport", "Consolider les résultats et produire le livrable."),
    )

    def __init__(self, parent=None):
        super().__init__(parent)
        self.project_metadata: dict[str, object] = {}
        self.project_dir: Path | None = None
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(18)

        summary = QFrame()
        summary.setObjectName("operationalHeader")
        summary_layout = QHBoxLayout(summary)
        summary_layout.setContentsMargins(20, 16, 20, 16)
        summary_layout.setSpacing(24)

        identity = QVBoxLayout()
        identity.setSpacing(3)
        self.project_name_label = QLabel("Aucun projet actif")
        self.project_name_label.setObjectName("viewTitle")
        self.project_context_label = QLabel("Créez un projet pour démarrer le dossier expérimental.")
        self.project_context_label.setObjectName("mutedText")
        identity.addWidget(self.project_name_label)
        identity.addWidget(self.project_context_label)
        summary_layout.addLayout(identity, 1)

        self.project_state = QLabel("CONTEXTE À DÉFINIR")
        self.project_state.setProperty("state", "warning")
        self.hardware_state = QLabel("MATÉRIEL NON VÉRIFIÉ")
        self.hardware_state.setProperty("state", "neutral")
        summary_layout.addWidget(self.project_state)
        summary_layout.addWidget(self.hardware_state)
        root.addWidget(summary)

        section_row = QHBoxLayout()
        section_title = QLabel("Parcours de la campagne")
        section_title.setObjectName("sectionTitle")
        section_note = QLabel("Chaque étape alimente la suivante et reste traçable dans le projet.")
        section_note.setObjectName("mutedText")
        section_row.addWidget(section_title)
        section_row.addSpacing(12)
        section_row.addWidget(section_note)
        section_row.addStretch()
        root.addLayout(section_row)

        workflow_grid = QGridLayout()
        workflow_grid.setHorizontalSpacing(14)
        workflow_grid.setVerticalSpacing(14)
        for position, item in enumerate(self.WORKFLOW):
            workflow_grid.addWidget(self._workflow_card(*item), position // 2, position % 2)
        root.addLayout(workflow_grid)

        recent = QFrame()
        recent.setObjectName("surface")
        recent_layout = QVBoxLayout(recent)
        recent_layout.setContentsMargins(20, 16, 20, 16)
        recent_layout.setSpacing(8)
        recent_title = QLabel("Dernière session")
        recent_title.setObjectName("sectionTitle")
        self.recent_session_label = QLabel(
            "Aucune session enregistrée dans ce projet. La première acquisition apparaîtra ici."
        )
        self.recent_session_label.setObjectName("mutedText")
        recent_layout.addWidget(recent_title)
        recent_layout.addWidget(self.recent_session_label)
        root.addWidget(recent)
        root.addStretch()

    def _workflow_card(self, view_name: str, index: str, title: str, description: str) -> QFrame:
        card = QFrame()
        card.setObjectName("workflowCard")
        card.setProperty("active", "false")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(8)

        heading = QHBoxLayout()
        number = QLabel(index)
        number.setObjectName("pageEyebrow")
        title_label = QLabel(title)
        title_label.setObjectName("sectionTitle")
        state = QLabel("À PRÉPARER")
        state.setProperty("state", "neutral")
        heading.addWidget(number)
        heading.addWidget(title_label)
        heading.addStretch()
        heading.addWidget(state)

        description_label = QLabel(description)
        description_label.setObjectName("mutedText")
        description_label.setWordWrap(True)
        action = QPushButton("Ouvrir l'étape")
        action.setProperty("kind", "secondary")
        action.clicked.connect(lambda checked=False, target=view_name: self.navigation_requested.emit(target))

        layout.addLayout(heading)
        layout.addWidget(description_label)
        layout.addStretch()
        layout.addWidget(action)
        return card

    def set_project_context(self, project_metadata: dict, project_dir: str) -> None:
        self.project_metadata = project_metadata or {}
        self.project_dir = Path(project_dir) if project_dir else None
        project_name = self.project_metadata.get("name") or "Projet sans nom"
        laboratory = self.project_metadata.get("laboratory") or "Laboratoire non renseigné"
        manager = self.project_metadata.get("manager") or "Responsable non renseigné"
        self.project_name_label.setText(str(project_name))
        self.project_context_label.setText(f"{laboratory} · Responsable : {manager}")
        self.project_state.setText("PROJET ACTIF")
        self.project_state.setProperty("state", "success")
        self.project_state.style().unpolish(self.project_state)
        self.project_state.style().polish(self.project_state)
