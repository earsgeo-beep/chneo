"""
Tests de Validation - Module Gestion Dérive Zéro

Tests pour valider la détection et correction de dérive des capteurs.

Auteur: CHNeoWave Development Team
Phase: 4 - Gestion Dérive Zéro
"""

import pytest
import numpy as np
import sys
import os
from typing import Tuple
from datetime import datetime, timedelta

# Import direct
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/hrneowave/core')))

import zero_drift_manager
from zero_drift_manager import (
    ZeroDriftManager,
    DriftMeasurement,
    simulate_sensor_drift
)


# ============================================================================
# TEST 4.1: DÉTECTION DÉRIVE NULLE
# ============================================================================

def test_zero_drift_no_drift():
    """
    TEST 4.1: Pas de dérive - capteur stable
    
    Critère: drift = 0, is_acceptable = True
    """
    manager = ZeroDriftManager(drift_threshold=0.001)
    manager.set_reference_zero(0, 0.0)
    
    # Plusieurs vérifications sans dérive
    for i in range(5):
        status = manager.check_drift(0, 0.0)
    
    assert abs(status.current_drift) < 1e-10, \
        f"Dérive devrait être 0, obtenu {status.current_drift}"
    
    assert status.is_acceptable, "Statut devrait être acceptable"
    assert status.warning_level == 0, "Warning level devra être 0"
    
    print(f"✓ TEST 4.1 PASS: Pas de dérive détectée (drift={status.current_drift:.10f})")


# ============================================================================
# TEST 4.2: DÉTECTION DÉRIVE LINÉAIRE
# ============================================================================

def test_zero_drift_linear_detection():
    """
    TEST 4.2: Détection dérive linéaire
    
    Critère: Dérive détectée correctement
    """
    manager = ZeroDriftManager(drift_threshold=0.001)
    manager.set_reference_zero(0, 0.0)
    
    base_time = datetime.now()
    
    # Dérive linéaire: 0.0003 m/h
    for i in range(5):
        drift_value = 0.0003 * i  # 0, 0.3, 0.6, 0.9, 1.2 mm
        timestamp = base_time + timedelta(hours=i)
        status = manager.check_drift(0, drift_value, timestamp)
    
    # Dérive finale
    assert abs(status.current_drift - 0.0012) < 0.0001, \
        f"Dérive devrait être ~0.0012, obtenu {status.current_drift}"
    
    # Taux de dérive devrait être ~0.0003 m/h
    assert abs(status.drift_rate - 0.0003) < 0.0001, \
        f"Taux devrait être ~0.0003 m/h, obtenu {status.drift_rate}"
    
    print(f"✓ TEST 4.2 PASS: Dérive linéaire détectée (rate={status.drift_rate:.6f} m/h)")


# ============================================================================
# TEST 4.3: NIVEAUX D'AVERTISSEMENT
# ============================================================================

def test_zero_drift_warning_levels():
    """
    TEST 4.3: Niveaux d'avertissement (OK, Attention, Critique)
    
    Critère: Niveaux corrects selon seuils
    """
    # Cas 1: OK (drift < seuil)
    manager1 = ZeroDriftManager(drift_threshold=0.001, drift_rate_threshold=0.0005)
    manager1.set_reference_zero(0, 0.0)
    status1 = manager1.check_drift(0, 0.0005)
    assert status1.warning_level == 0, f"Devrait être OK, obtenu {status1.warning_level}"
    
    # Cas 2: Attention (seuil < drift < 2×seuil)
    manager2 = ZeroDriftManager(drift_threshold=0.001, drift_rate_threshold=0.0005)
    manager2.set_reference_zero(0, 0.0)
    status2 = manager2.check_drift(0, 0.0015)
    assert status2.warning_level >= 1, f"Devrait être Attention ou Critique, obtenu {status2.warning_level}"
    
    # Cas 3: Critique (drift > 2×seuil)
    manager3 = ZeroDriftManager(drift_threshold=0.001, drift_rate_threshold=0.0005)
    manager3.set_reference_zero(0, 0.0)
    status3 = manager3.check_drift(0, 0.0025)
    assert status3.warning_level == 2, f"Devrait être Critique, obtenu {status3.warning_level}"
    
    print(f"✓ TEST 4.3 PASS: Niveaux d'avertissement corrects")



# ============================================================================
# TEST 4.4: CORRECTION AUTOMATIQUE
# ============================================================================

def test_zero_drift_auto_correction():
    """
    TEST 4.4: Correction automatique de dérive
    
    Critère: Signal corrigé = signal - offset
    """
    manager = ZeroDriftManager(drift_threshold=0.001, auto_correct=True)
    manager.set_reference_zero(0, 0.0)
    
    # Créer dérive
    drift_offset = 0.002
    status = manager.check_drift(0, drift_offset)
    
    # Appliquer correction manuelle
    manager.apply_auto_correction(0)
    
    # Signal de test
    signal = np.array([0.01, 0.02, 0.03, 0.04, 0.05])
    corrected = manager.apply_correction(0, signal)
    
    # Vérifier correction
    expected = signal - drift_offset
    error = np.max(np.abs(corrected - expected))
    
    assert error < 1e-10, \
        f"Correction inexacte, erreur max = {error}"
    
    print(f"✓ TEST 4.4 PASS: Correction auto appliquée (offset={drift_offset:.6f} m)")


# ============================================================================
# TEST 4.5: VÉRIFICATION PRÉ-ESSAI
# ============================================================================

def test_zero_drift_pre_test_check():
    """
    TEST 4.5: Vérification pré-essai
    
    Critère: Retourne False si dérive excessive
    """
    # Dérive acceptable  
    manager1 = ZeroDriftManager(drift_threshold=0.001, auto_correct=False)
    manager1.set_reference_zero(0, 0.0)
    is_ok1 = manager1.check_pre_test_drift(0, 0.0005)
    assert is_ok1, "Dérive acceptable devrait retourner True"
    
    # Dérive excessive (ici on teste juste le seuil de drift, pas le rate)
    manager2 = ZeroDriftManager(drift_threshold=0.001, drift_rate_threshold=10.0, auto_correct=False)
    manager2.set_reference_zero(0, 0.0)
    is_ok2 = manager2.check_pre_test_drift(0, 0.0025)
    assert not is_ok2, f"Dérive excessive devrait retourner False, obtenu {is_ok2}"
    
    print(f"✓ TEST 4.5 PASS: Vérification pré-essai fonctionne")



# ============================================================================
# TEST 4.6: SIMULATION DÉRIVE
# ============================================================================

def test_zero_drift_simulation():
    """
    TEST 4.6: Simulation de dérive sur signal
    
    Critère: Signal avec dérive != signal propre
    """
    clean_signal = np.sin(2 * np.pi * np.linspace(0, 1, 100))
    drift_amp = 0.01
    
    # Dérive linéaire
    drifted = simulate_sensor_drift(clean_signal, drift_amp, "linear")
    
    # Vérifier que c'est différent
    diff = np.max(np.abs(drifted - clean_signal))
    assert diff > 0, "Signal avec dérive devrait être différent"
    
    # Vérifier amplitude de dérive
    assert diff <= drift_amp * 1.01, \
        f"Dérive max devrait être ~{drift_amp}, obtenu {diff}"
    
    print(f"✓ TEST 4.6 PASS: Simulation dérive fonctionne (max_drift={diff:.6f})")


# ============================================================================
# FIXTURE RAPPORT
# ============================================================================

@pytest.fixture(scope="session", autouse=True)
def generate_test_report(request):
    """Génère un rapport de test."""
    yield
    
    print("\n" + "="*80)
    print("RAPPORT DE TEST - PHASE 4: VALIDATION GESTION DÉRIVE ZÉRO")
    print("="*80)
    print(f"Module: tests/test_zerodrift_validation.py")
    print(f"Date: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    print("\n✅ MODULE DÉRIVE ZÉRO VALIDÉ si tous les tests sont PASS")
    print("="*80)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "-s"])
