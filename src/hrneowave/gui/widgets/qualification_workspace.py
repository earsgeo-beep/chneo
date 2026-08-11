"""Poste opérateur pour exécuter et relire un protocole de qualification."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QFormLayout,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QProgressBar,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ...acquisition import (
    HardwareQualificationProtocol,
    QualificationHistoryEntry,
    QualificationHistoryScan,
    QualificationHistoryStore,
    QualificationStage,
    device_identity,
)


class QualificationWorkspace(QWidget):
    """Présente les paliers sans prendre directement le contrôle du matériel."""

    stage_requested = Signal(str)
    refresh_requested = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.protocol: HardwareQualificationProtocol | None = None
        self.device: Any = None
        self.accepted_stage_ids: frozenset[str] = frozenset()
        self._checklist_widgets: list[QCheckBox] = []
        self._running_stage_id: str | None = None
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(12)

        header = QFrame()
        header.setObjectName("quietSurface")
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(14, 10, 14, 10)
        self.protocol_name_label = QLabel("Aucun protocole matériel")
        self.protocol_name_label.setObjectName("sectionTitle")
        self.protocol_description_label = QLabel(
            "Connectez un équipement pour sélectionner son protocole de qualification."
        )
        self.protocol_description_label.setObjectName("mutedText")
        self.protocol_description_label.setWordWrap(True)
        self.protocol_progress = QProgressBar()
        self.protocol_progress.setFormat("%v / %m paliers acceptés")
        header_layout.addWidget(self.protocol_name_label)
        header_layout.addWidget(self.protocol_description_label)
        header_layout.addWidget(self.protocol_progress)
        layout.addWidget(header)

        stage_group = QGroupBox("Palier à exécuter")
        stage_form = QFormLayout(stage_group)
        self.stage_combo = QComboBox()
        self.stage_requirement_label = QLabel("Aucun palier disponible")
        self.stage_requirement_label.setWordWrap(True)
        self.stage_requirement_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        self.stage_state_label = QLabel("EN ATTENTE")
        self.stage_state_label.setProperty("state", "neutral")
        stage_form.addRow("Palier", self.stage_combo)
        stage_form.addRow("Exigences", self.stage_requirement_label)
        stage_form.addRow("État", self.stage_state_label)
        layout.addWidget(stage_group)

        self.checklist_group = QGroupBox("Checklist opérateur obligatoire")
        self.checklist_layout = QVBoxLayout(self.checklist_group)
        layout.addWidget(self.checklist_group)

        action_layout = QHBoxLayout()
        self.start_stage_button = QPushButton("Lancer le palier")
        self.start_stage_button.setProperty("kind", "primaryLarge")
        self.refresh_button = QPushButton("Actualiser l'historique")
        self.refresh_button.setProperty("kind", "secondary")
        action_layout.addWidget(self.start_stage_button)
        action_layout.addWidget(self.refresh_button)
        action_layout.addStretch()
        layout.addLayout(action_layout)

        history_group = QGroupBox("Historique traçable des rapports")
        history_layout = QVBoxLayout(history_group)
        self.history_summary_label = QLabel("Aucun rapport chargé")
        self.history_summary_label.setObjectName("mutedText")
        self.history_table = QTableWidget(0, 6)
        self.history_table.setHorizontalHeaderLabels(
            ["Palier", "Date UTC", "Verdict", "Contrôles", "Fichier maître", "Rapport JSON"]
        )
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.history_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.history_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        history_layout.addWidget(self.history_summary_label)
        history_layout.addWidget(self.history_table)
        layout.addWidget(history_group, 1)

        self.stage_combo.currentIndexChanged.connect(self._refresh_stage_details)
        self.start_stage_button.clicked.connect(self._request_selected_stage)
        self.refresh_button.clicked.connect(self.refresh_requested.emit)
        self._update_action_state()

    def set_protocol(
        self,
        protocol: HardwareQualificationProtocol | None,
        device: Any = None,
    ) -> None:
        self.protocol = protocol
        self.device = device
        self.accepted_stage_ids = frozenset()
        self.stage_combo.blockSignals(True)
        self.stage_combo.clear()
        if protocol is None:
            self.protocol_name_label.setText("Aucun protocole matériel")
            self.protocol_description_label.setText(
                "Connectez un équipement pour sélectionner son protocole de qualification."
            )
            self.protocol_progress.setRange(0, 1)
            self.protocol_progress.setValue(0)
        else:
            self.protocol_name_label.setText(protocol.name)
            self.protocol_description_label.setText(protocol.description)
            self.protocol_progress.setRange(0, len(protocol.stages))
            for stage in protocol.stages:
                self.stage_combo.addItem(f"{stage.stage_id} · {stage.title}", stage.stage_id)
        self.stage_combo.blockSignals(False)
        self._refresh_stage_details()

    def set_history(self, scan: QualificationHistoryScan) -> None:
        entries = self._relevant_entries(scan.entries)
        if self.protocol is not None and self.device is not None:
            self.accepted_stage_ids = QualificationHistoryStore.accepted_stage_ids(
                entries,
                self.protocol,
                self.device,
            )
            self.protocol_progress.setValue(len(self.accepted_stage_ids))
        else:
            self.accepted_stage_ids = frozenset()
            self.protocol_progress.setValue(0)
        self._populate_history(entries)
        error_suffix = f" · {len(scan.errors)} rapport(s) illisible(s)" if scan.errors else ""
        self.history_summary_label.setText(
            f"{len(entries)} rapport(s) pour cet équipement{error_suffix}"
        )
        self._refresh_stage_details()

    def set_running(self, stage_id: str | None) -> None:
        self._running_stage_id = stage_id
        self.stage_combo.setEnabled(stage_id is None)
        self.refresh_button.setEnabled(stage_id is None)
        self._refresh_stage_details()

    def selected_stage(self) -> QualificationStage | None:
        if self.protocol is None:
            return None
        stage_id = self.stage_combo.currentData()
        if not stage_id:
            return None
        return self.protocol.stage(str(stage_id))

    def select_stage(self, stage_id: str) -> bool:
        index = self.stage_combo.findData(stage_id)
        if index < 0:
            return False
        self.stage_combo.setCurrentIndex(index)
        return True

    def checklist_complete(self) -> bool:
        return bool(self._checklist_widgets) and all(
            checkbox.isChecked() for checkbox in self._checklist_widgets
        )

    def checklist_attestations(self) -> tuple[str, ...]:
        return tuple(
            checkbox.text()
            for checkbox in self._checklist_widgets
            if checkbox.isChecked()
        )

    def _refresh_stage_details(self) -> None:
        stage = self.selected_stage()
        self._replace_checklist(stage.checklist if stage else ())
        if stage is None:
            self.stage_requirement_label.setText("Aucun palier disponible")
            self._set_stage_state("EN ATTENTE", "neutral")
            self._update_action_state()
            return

        rate = (
            f"{stage.required_sample_rate_hz:g} Hz"
            if stage.required_sample_rate_hz is not None
            else "fréquence opérationnelle choisie"
        )
        profile = "entrées à AGND" if stage.profile_name == "grounded_inputs" else "fonctionnel"
        self.stage_requirement_label.setText(
            f"{stage.required_channel_count} voie(s) · {stage.duration_seconds:g} s · "
            f"{rate} · profil {profile} · "
            f"{stage.minimum_distinct_ranges} plage(s) distincte(s) minimum"
        )
        if self._running_stage_id == stage.stage_id:
            self._set_stage_state("EN COURS", "warning")
        elif stage.stage_id in self.accepted_stage_ids:
            self._set_stage_state("ACCEPTÉ · RÉEXÉCUTION POSSIBLE", "success")
        elif QualificationHistoryStore.is_stage_unlocked(stage, self.accepted_stage_ids):
            self._set_stage_state("PRÊT APRÈS CHECKLIST", "neutral")
        else:
            missing = sorted(set(stage.prerequisites) - set(self.accepted_stage_ids))
            self._set_stage_state(f"VERROUILLÉ · PRÉREQUIS {', '.join(missing)}", "warning")
        self._update_action_state()

    def _replace_checklist(self, labels: Iterable[str]) -> None:
        for checkbox in self._checklist_widgets:
            self.checklist_layout.removeWidget(checkbox)
            checkbox.deleteLater()
        self._checklist_widgets = []
        for label in labels:
            checkbox = QCheckBox(str(label))
            checkbox.toggled.connect(self._update_action_state)
            self.checklist_layout.addWidget(checkbox)
            self._checklist_widgets.append(checkbox)

    def _update_action_state(self) -> None:
        stage = self.selected_stage()
        unlocked = bool(
            stage
            and QualificationHistoryStore.is_stage_unlocked(
                stage,
                self.accepted_stage_ids,
            )
        )
        self.start_stage_button.setEnabled(
            self._running_stage_id is None and unlocked and self.checklist_complete()
        )

    def _request_selected_stage(self) -> None:
        stage = self.selected_stage()
        if stage is not None and self.start_stage_button.isEnabled():
            self.stage_requested.emit(stage.stage_id)

    def _relevant_entries(
        self,
        entries: Iterable[QualificationHistoryEntry],
    ) -> tuple[QualificationHistoryEntry, ...]:
        if self.protocol is None or self.device is None:
            return ()
        identity = device_identity(self.device)
        return tuple(
            entry
            for entry in entries
            if entry.protocol_id == self.protocol.protocol_id
            and entry.device_identity == identity
        )

    def _populate_history(self, entries: Iterable[QualificationHistoryEntry]) -> None:
        payload = tuple(entries)
        self.history_table.setRowCount(len(payload))
        for row, entry in enumerate(payload):
            values = (
                entry.protocol_stage or "Hors protocole",
                entry.evaluated_at_utc,
                entry.verdict.upper(),
                f"{entry.checks_passed}/{entry.checks_total}",
                entry.source_master_file,
                entry.report_path.name,
            )
            for column, value in enumerate(values):
                item = QTableWidgetItem(str(value))
                if column in {4, 5}:
                    item.setToolTip(
                        entry.source_master_file if column == 4 else str(entry.report_path)
                    )
                self.history_table.setItem(row, column, item)

    def _set_stage_state(self, text: str, state: str) -> None:
        self.stage_state_label.setText(text)
        self.stage_state_label.setProperty("state", state)
        self.stage_state_label.style().unpolish(self.stage_state_label)
        self.stage_state_label.style().polish(self.stage_state_label)
