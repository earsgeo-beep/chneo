"""
Module de Gestion de la Dérive Zéro des Capteurs

Ce module détecte et corrige la dérive du zéro des capteurs de pression/niveau
pour garantir la précision des mesures maritimes.

Références scientifiques:
    - ITTC Recommended Procedures 7.5-02-07-02.1 - "Testing and Extrapolation 
      Methods, Loads and Responses, Seakeeping, Seakeeping Experiments"
    - ISO 17025:2017 - "General requirements for the competence of testing 
      and calibration laboratories"

Auteur: CHNeoWave Development Team
Phase: 4 - Gestion Dérive Zéro
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, NamedTuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import warnings


# ============================================================================
# STRUCTURES DE DONNÉES
# ============================================================================

@dataclass
class DriftMeasurement:
    """
    Mesure de dérive du zéro pour un capteur.
    
    Attributes:
        timestamp: Horodatage de la mesure
        channel_id: Identifiant du canal/capteur
        zero_value: Valeur mesurée au repos (niveau zéro théorique)
        temperature: Température ambiante (°C) si disponible
        pressure: Pression atmosphérique (hPa) si disponible
    """
    timestamp: datetime
    channel_id: int
    zero_value: float
    temperature: Optional[float] = None
    pressure: Optional[float] = None


@dataclass
class DriftStatus:
    """
    État de la dérive pour un capteur.
    
    Attributes:
        channel_id: Identifiant du canal
        current_drift: Dérive actuelle (valeur mesurée - zéro de référence)
        drift_rate: Taux de dérive (unités/heure)
        is_acceptable: True si dérive dans les limites acceptables
        warning_level: Niveau d'avertissement (0=OK, 1=Attention, 2=Critique)
        last_check: Horodatage de la dernière vérification
        measurements_history: Historique des mesures
    """
    channel_id: int
    current_drift: float
    drift_rate: float
    is_acceptable: bool
    warning_level: int
    last_check: datetime
    measurements_history: List[DriftMeasurement] = field(default_factory=list)


@dataclass
class DriftCorrection:
    """
    Correction à appliquer pour compenser la dérive.
    
    Attributes:
        channel_id: Identifiant du canal
        offset: Offset à soustraire des mesures (en unités physiques)
        applied_at: Horodatage de l'application
        reason: Raison de la correction
    """
    channel_id: int
    offset: float
    applied_at: datetime
    reason: str


# ============================================================================
# GESTIONNAIRE DE DÉRIVE ZÉRO
# ============================================================================

class ZeroDriftManager:
    """
    Gestionnaire de dérive zéro pour les capteurs maritimes.
    
    Détecte, surveille et corrige automatiquement la dérive du zéro
    des capteurs de niveau/pression.
    
    Example:
        >>> manager = ZeroDriftManager(
        >>>     drift_threshold=0.001,  # 1 mm acceptable
        >>>     drift_rate_threshold=0.0005  # 0.5 mm/h acceptable
        >>> )
        >>> 
        >>> # Enregistrer référence initiale
        >>> manager.set_reference_zero(channel_id=0, value=0.0)
        >>> 
        >>> # Vérifications avant essai
        >>> drift_ok = manager.check_pre_test_drift(channel_id=0, current_value=0.0002)
        >>> 
        >>> # Correction automatique si nécessaire
        >>> corrected_signal = manager.apply_correction(channel_id=0, signal=raw_signal)
    """
    
    def __init__(self,
                 drift_threshold: float = 0.001,
                 drift_rate_threshold: float = 0.0005,
                 max_history_hours: float = 24.0,
                 auto_correct: bool = True):
        """
        Initialise le gestionnaire de dérive.
        
        Args:
            drift_threshold: Seuil de dérive acceptable (m)
            drift_rate_threshold: Seuil de taux de dérive (m/h)
            max_history_hours: Durée max de conservation historique (h)
            auto_correct: Activer correction automatique
        """
        self.drift_threshold = drift_threshold
        self.drift_rate_threshold = drift_rate_threshold
        self.max_history_hours = max_history_hours
        self.auto_correct = auto_correct
        
        # Stockage des données
        self._reference_zeros: Dict[int, float] = {}
        self._drift_status: Dict[int, DriftStatus] = {}
        self._corrections: Dict[int, List[DriftCorrection]] = {}
        
        # Statistiques
        self._total_checks = 0
        self._total_corrections = 0
    
    def set_reference_zero(self, channel_id: int, value: float,
                          timestamp: Optional[datetime] = None):
        """
        Définit la valeur de référence du zéro pour un capteur.
        
        Args:
            channel_id: Identifiant du canal
            value: Valeur de référence (mesurée au repos, eau calme)
            timestamp: Horodatage (défaut: maintenant)
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        self._reference_zeros[channel_id] = value
        
        # Initialiser le statut
        if channel_id not in self._drift_status:
            self._drift_status[channel_id] = DriftStatus(
                channel_id=channel_id,
                current_drift=0.0,
                drift_rate=0.0,
                is_acceptable=True,
                warning_level=0,
                last_check=timestamp,
                measurements_history=[]
            )
        
        # Ajouter mesure initiale
        measurement = DriftMeasurement(
            timestamp=timestamp,
            channel_id=channel_id,
            zero_value=value
        )
        
        self._drift_status[channel_id].measurements_history.append(measurement)
        
        print(f"✓ Zéro de référence défini pour canal {channel_id}: {value:.6f} m")
    
    def check_drift(self, channel_id: int, current_value: float,
                   timestamp: Optional[datetime] = None) -> DriftStatus:
        """
        Vérifie la dérive actuelle d'un capteur.
        
        Args:
            channel_id: Identifiant du canal
            current_value: Valeur mesurée actuellement au repos
            timestamp: Horodatage (défaut: maintenant)
        
        Returns:
            DriftStatus avec détails de la dérive
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        if channel_id not in self._reference_zeros:
            raise ValueError(f"Aucun zéro de référence pour canal {channel_id}")
        
        reference = self._reference_zeros[channel_id]
        status = self._drift_status[channel_id]
        
        # Calculer dérive
        current_drift = current_value - reference
        
        # Ajouter mesure à l'historique
        measurement = DriftMeasurement(
            timestamp=timestamp,
            channel_id=channel_id,
            zero_value=current_value
        )
        status.measurements_history.append(measurement)
        
        # Nettoyer ancien historique
        self._clean_old_history(channel_id, timestamp)
        
        # Calculer taux de dérive
        drift_rate = self._compute_drift_rate(channel_id)
        
        # Déterminer niveau d'avertissement
        warning_level = self._evaluate_warning_level(
            abs(current_drift), abs(drift_rate)
        )
        
        # Mettre à jour statut
        status.current_drift = current_drift
        status.drift_rate = drift_rate
        status.is_acceptable = warning_level == 0
        status.warning_level = warning_level
        status.last_check = timestamp
        
        self._total_checks += 1
        
        return status
    
    def _clean_old_history(self, channel_id: int, current_time: datetime):
        """Supprime les mesures trop anciennes de l'historique."""
        if channel_id not in self._drift_status:
            return
        
        status = self._drift_status[channel_id]
        cutoff_time = current_time - timedelta(hours=self.max_history_hours)
        
        # Filtrer les mesures récentes
        status.measurements_history = [
            m for m in status.measurements_history 
            if m.timestamp >= cutoff_time
        ]
    
    def _compute_drift_rate(self, channel_id: int) -> float:
        """
        Calcule le taux de dérive (régression linéaire).
        
        Returns:
            Taux de dérive en unités/heure
        """
        status = self._drift_status[channel_id]
        history = status.measurements_history
        
        if len(history) < 2:
            return 0.0
        
        # Extraire temps et valeurs
        times = [(m.timestamp - history[0].timestamp).total_seconds() / 3600.0 
                for m in history]  # heures
        values = [m.zero_value for m in history]
        
        # Régression linéaire simple
        times_arr = np.array(times)
        values_arr = np.array(values)
        
        # Vérifier variance
        if np.std(times_arr) < 1e-10:
            # Tous les temps identiques, pas de tendance calculable
            return 0.0
        
        try:
            # Pente = taux de dérive
            coeffs = np.polyfit(times_arr, values_arr, 1)
            drift_rate = coeffs[0]  # unités/heure
            return drift_rate
        except np.linalg.LinAlgError:
            # Échec régression, retourner 0
            return 0.0

    
    def _evaluate_warning_level(self, drift_abs: float, 
                                drift_rate_abs: float) -> int:
        """
        Évalue le niveau d'avertissement.
        
        Returns:
            0 = OK, 1 = Attention, 2 = Critique
        """
        # Critères
        # Critique: dérive > 2× seuil OU taux > 2× seuil
        if (drift_abs > 2 * self.drift_threshold or 
            drift_rate_abs > 2 * self.drift_rate_threshold):
            return 2
        
        # Attention: dérive > seuil OU taux > seuil
        if (drift_abs > self.drift_threshold or 
            drift_rate_abs > self.drift_rate_threshold):
            return 1
        
        # OK
        return 0
    
    def check_pre_test_drift(self, channel_id: int, current_value: float,
                            timestamp: Optional[datetime] = None) -> bool:
        """
        Vérifie si la dérive est acceptable avant un essai.
        
        Args:
            channel_id: Identifiant du canal
            current_value: Valeur mesurée au repos avant essai
            timestamp: Horodatage
        
        Returns:
            True si acceptable, False sinon
        """
        status = self.check_drift(channel_id, current_value, timestamp)
        
        if not status.is_acceptable:
            warnings.warn(
                f"⚠️ DÉRIVE EXCESSIVE canal {channel_id}: "
                f"drift={status.current_drift:.6f} m, "
                f"rate={status.drift_rate:.6f} m/h. "
                f"Recalibration recommandée avant essai.",
                UserWarning
            )
            
            if self.auto_correct:
                self.apply_auto_correction(channel_id, timestamp)
        
        return status.is_acceptable
    
    def apply_auto_correction(self, channel_id: int,
                             timestamp: Optional[datetime] = None):
        """
        Applique une correction automatique de dérive.
        
        Args:
            channel_id: Identifiant du canal
            timestamp: Horodatage
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        status = self._drift_status[channel_id]
        
        # Offset = dérive actuelle
        offset = status.current_drift
        
        correction = DriftCorrection(
            channel_id=channel_id,
            offset=offset,
            applied_at=timestamp,
            reason=f"Auto-correction: drift={offset:.6f} m, rate={status.drift_rate:.6f} m/h"
        )
        
        if channel_id not in self._corrections:
            self._corrections[channel_id] = []
        
        self._corrections[channel_id].append(correction)
        
        # Réinitialiser référence
        current_value = status.measurements_history[-1].zero_value
        new_reference = current_value
        self._reference_zeros[channel_id] = new_reference
        
        self._total_corrections += 1
        
        print(f"✓ Correction auto appliquée canal {channel_id}: offset={offset:.6f} m")
    
    def apply_correction(self, channel_id: int, 
                        signal: np.ndarray) -> np.ndarray:
        """
        Applique les corrections de dérive à un signal.
        
        Args:
            channel_id: Identifiant du canal
            signal: Signal à corriger
        
        Returns:
            Signal corrigé
        """
        if channel_id not in self._corrections or not self._corrections[channel_id]:
            return signal  # Pas de correction
        
        # Utiliser la dernière correction
        correction = self._corrections[channel_id][-1]
        corrected_signal = signal - correction.offset
        
        return corrected_signal
    
    def get_drift_report(self, channel_id: int) -> str:
        """
        Génère un rapport de dérive pour un capteur.
        
        Args:
            channel_id: Identifiant du canal
        
        Returns:
            Rapport formaté
        """
        if channel_id not in self._drift_status:
            return f"Aucune donnée de dérive pour canal {channel_id}"
        
        status = self._drift_status[channel_id]
        reference = self._reference_zeros[channel_id]
        
        lines = []
        lines.append("="*80)
        lines.append(f"RAPPORT DE DÉRIVE - CANAL {channel_id}")
        lines.append("="*80)
        lines.append(f"Zéro de référence:        {reference:.6f} m")
        lines.append(f"Dérive actuelle:          {status.current_drift:.6f} m")
        lines.append(f"Taux de dérive:           {status.drift_rate:.6f} m/h")
        lines.append(f"Seuil dérive:             {self.drift_threshold:.6f} m")
        lines.append(f"Seuil taux:               {self.drift_rate_threshold:.6f} m/h")
        lines.append("")
        
        # Statut
        if status.warning_level == 0:
            lines.append("✅ STATUT: OK - Dérive acceptable")
        elif status.warning_level == 1:
            lines.append("⚠️  STATUT: ATTENTION - Dérive proche des limites")
        else:
            lines.append("🔴 STATUT: CRITIQUE - Dérive excessive, recalibration nécessaire")
        
        lines.append("")
        lines.append(f"Dernière vérification:    {status.last_check.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"Nombre de mesures:        {len(status.measurements_history)}")
        
        # Corrections appliquées
        if channel_id in self._corrections and self._corrections[channel_id]:
            lines.append("")
            lines.append("CORRECTIONS APPLIQUÉES:")
            for i, corr in enumerate(self._corrections[channel_id][-5:], 1):  # 5 dernières
                lines.append(f"  {i}. {corr.applied_at.strftime('%Y-%m-%d %H:%M:%S')} - "
                           f"Offset: {corr.offset:.6f} m")
        
        lines.append("="*80)
        
        return "\n".join(lines)
    
    def get_all_channels_status(self) -> Dict[int, DriftStatus]:
        """Retourne le statut de tous les canaux."""
        return self._drift_status.copy()
    
    def reset_channel(self, channel_id: int):
        """Réinitialise complètement un canal."""
        if channel_id in self._reference_zeros:
            del self._reference_zeros[channel_id]
        if channel_id in self._drift_status:
            del self._drift_status[channel_id]
        if channel_id in self._corrections:
            del self._corrections[channel_id]
        
        print(f"✓ Canal {channel_id} réinitialisé")


# ============================================================================
# FONCTIONS UTILITAIRES
# ============================================================================

def simulate_sensor_drift(clean_signal: np.ndarray, 
                         drift_amplitude: float,
                         drift_type: str = "linear") -> np.ndarray:
    """
    Simule une dérive de capteur sur un signal propre.
    
    Args:
        clean_signal: Signal sans dérive
        drift_amplitude: Amplitude de la dérive
        drift_type: Type ("linear", "exponential", "thermal")
    
    Returns:
        Signal avec dérive ajoutée
    """
    n = len(clean_signal)
    t = np.linspace(0, 1, n)
    
    if drift_type == "linear":
        drift = drift_amplitude * t
    elif drift_type == "exponential":
        drift = drift_amplitude * (np.exp(t) - 1) / (np.e - 1)
    elif drift_type == "thermal":
        # Dérive thermique sinusoïdale
        drift = drift_amplitude * np.sin(2 * np.pi * t)
    else:
        raise ValueError(f"Type de dérive inconnu: {drift_type}")
    
    return clean_signal + drift


if __name__ == "__main__":
    # Exemple d'utilisation
    print("="*80)
    print("MODULE GESTION DÉRIVE ZÉRO - EXEMPLE D'UTILISATION")
    print("="*80)
    print()
    
    # Créer gestionnaire
    manager = ZeroDriftManager(
        drift_threshold=0.001,  # 1 mm
        drift_rate_threshold=0.0005,  # 0.5 mm/h
        auto_correct=True
    )
    
    # Définir zéro de référence
    manager.set_reference_zero(channel_id=0, value=0.0)
    print()
    
    # Simuler vérifications périodiques avec dérive progressive
    print("Simulation de vérifications avec dérive progressive:")
    print("-"*80)
    
    base_time = datetime.now()
    drifts = [0.0, 0.0002, 0.0005, 0.0008, 0.0012]  # Dérive croissante
    
    for i, drift_value in enumerate(drifts):
        current_time = base_time + timedelta(hours=i)
        measured_value = 0.0 + drift_value  # Référence + dérive
        
        status = manager.check_drift(0, measured_value, current_time)
        
        warning_symbols = ["✅", "⚠️ ", "🔴"]
        symbol = warning_symbols[status.warning_level]
        
        print(f"t+{i}h: Mesure={measured_value:.6f} m, "
              f"Dérive={status.current_drift:.6f} m, "
              f"Taux={status.drift_rate:.6f} m/h {symbol}")
    
    print()
    
    # Rapport complet
    print(manager.get_drift_report(0))
    print()
    
    # Statistiques
    print(f"Total vérifications: {manager._total_checks}")
    print(f"Total corrections:   {manager._total_corrections}")
    print()
    
    print("="*80)
    print("Structure du module créée avec succès ✓")
    print("="*80)
