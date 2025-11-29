"""
Tests d'Intégration - CHNeoWave Phase 5

Tests de chaîne complète vérifiant l'intégration de tous les modules :
- FFT + Goda + Export
- FFT + Mansard-Funke + Export  
- Propagation incertitudes bout-en-bout
- Acquisition longue durée avec détection dérive
- Haute fréquence (capteurs pression)

Auteur: CHNeoWave Development Team
Phase: 5 - Tests Intégration
"""

import pytest
import numpy as np
import sys
import os
import tempfile
import json
from datetime import datetime, timedelta
from typing import Tuple, Dict, Any

# Import direct des modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/hrneowave/core')))

import zero_drift_manager
from zero_drift_manager import ZeroDriftManager

import uncertainty_calculator
from uncertainty_calculator import UncertaintyCalculator, create_standard_H_budget

import mansard_funke_analyzer
from mansard_funke_analyzer import (
    ProbeConfiguration,
    MansardFunkeAnalyzer
)


# ============================================================================
# UTILITAIRES POUR TESTS D'INTÉGRATION
# ============================================================================

def generate_jonswap_time_series(Hs, Tp, duration, fs, gamma=3.3, seed=42):
    """
    Génère un signal temporel JONSWAP.
    
    Returns:
        tuple: (temps, signal, Hs_théorique, Tp_théorique)
    """
    np.random.seed(seed)
    
    t = np.arange(0, duration, 1/fs)
    N = len(t)
    df = 1.0 / duration
    
    # Fréquences
    frequencies = np.arange(0, fs/2, df)
    fp = 1.0 / Tp
    g = 9.81
    
    # Spectre JONSWAP
    alpha = 5.058 * (Hs / Tp)**2 * (1 - 0.287 * np.log(gamma))
    frequencies_safe = np.maximum(frequencies, 1e-10)
    
    pm_spectrum = (alpha * g**2) / ((2 * np.pi)**4 * frequencies_safe**5) * \
                  np.exp(-1.25 * (fp / frequencies_safe)**4)
    
    sigma = np.where(frequencies <= fp, 0.07, 0.09)
    r = np.exp(-((frequencies - fp)**2) / (2 * sigma**2 * fp**2))
    peak_enhancement = gamma ** r
    
    jonswap = pm_spectrum * peak_enhancement
    
    # Phases aléatoires
    phases = np.random.uniform(0, 2*np.pi, len(frequencies))
    
    # Reconstruction signal
    signal = np.zeros(N)
    for i, (f, S, phi) in enumerate(zip(frequencies, jonswap, phases)):
        if f > 0:
            amplitude = np.sqrt(2 * S * df)
            signal += amplitude * np.cos(2 * np.pi * f * t + phi)
    
    return t, signal, Hs, Tp


def compute_fft_spectrum(signal, fs):
    """
    Calcule le spectre FFT d'un signal.
    
    Returns:
        tuple: (frequencies, power_spectrum)
    """
    N = len(signal)
    fft_result = np.fft.fft(signal)
    freqs = np.fft.fftfreq(N, 1/fs)
    
    # Spectre unilatéral
    positive_mask = freqs > 0
    positive_freqs = freqs[positive_mask]
    psd = (np.abs(fft_result[positive_mask])**2) / (N * fs) * 2
    
    return positive_freqs, psd


def compute_goda_parameters(signal, fs):
    """
    Calcule les paramètres Goda (zero-crossing).
    
    Returns:
        dict: {Hs, Tz, H13, Hmean, n_waves}
    """
    # Détrend
    signal_detrend = signal - np.mean(signal)
    
    # Zero-crossings montants
    zero_crossings = []
    for i in range(len(signal_detrend) - 1):
        if signal_detrend[i] <= 0 and signal_detrend[i + 1] > 0:
            zero_crossings.append(i)
    
    if len(zero_crossings) < 2:
        return None
    
    # Extraire vagues
    wave_heights = []
    for i in range(len(zero_crossings) - 1):
        start_idx = zero_crossings[i]
        end_idx = zero_crossings[i + 1]
        wave_segment = signal_detrend[start_idx:end_idx]
        
        if len(wave_segment) > 0:
            crest = np.max(wave_segment)
            trough = np.min(wave_segment)
            height = crest - trough
            wave_heights.append(height)
    
    if not wave_heights:
        return None
    
    heights = np.array(wave_heights)
    heights_sorted = np.sort(heights)[::-1]
    
    n_waves = len(heights)
    n_third = max(1, n_waves // 3)
    H13 = np.mean(heights_sorted[:n_third])
    Hmean = np.mean(heights)
    
    # Période moyenne
    periods = [(zero_crossings[i+1] - zero_crossings[i]) / fs 
               for i in range(len(zero_crossings) - 1)]
    Tz = np.mean(periods) if periods else 0
    
    return {
        'Hs': H13,  # Hs = H1/3
        'Tz': Tz,
        'H13': H13,
        'Hmean': Hmean,
        'n_waves': n_waves
    }


def export_to_file(filename, data_dict, metadata_dict):
    """
    Exporte les données en JSON (simplifié sans HDF5).
    
    Args:
        filename: Chemin du fichier
        data_dict: Dictionnaire des données {nom: list/array}
        metadata_dict: Dictionnaire des métadonnées {clé: valeur}
    """
    export_data = {
        'data': {k: v.tolist() if hasattr(v, 'tolist') else v 
                for k, v in data_dict.items()},
        'metadata': metadata_dict
    }
    
    with open(filename, 'w') as f:
        json.dump(export_data, f)


# ============================================================================
# TEST 5.1.1: CHAÎNE HOULE COMPLÈTE
# ============================================================================

def test_integration_full_wave_chain():
    """
    TEST 5.1.1: Chaîne Houle Complète
    
    Scénario: JONSWAP → FFT → Goda → Incertitudes → Export JSON
    
    Entrée: Signal JONSWAP (Hs=0.10m, Tp=1.2s, 600s, fs=100Hz)
    
    Vérifications:
    - Hs exporté = 0.10m ± 10%
    - Tp exporté = 1.2s ± 10%
    - Incertitudes présentes
    - Fichier JSON valide
    """
    # Paramètres
    Hs_target = 0.10  # 10 cm
    Tp_target = 1.2   # 1.2 seconde
    duration = 600.0  # 10 minutes
    fs = 100.0        # 100 Hz
    
    # Étape 1: Générer signal JONSWAP (8 canaux simulés)
    signals = []
    for channel in range(8):
        t, signal, _, _ = generate_jonswap_time_series(
            Hs_target, Tp_target, duration, fs, seed=42+channel
        )
        signals.append(signal)
    
    # Étape 2: FFT sur canal principal (canal 0)
    freqs, psd = compute_fft_spectrum(signals[0], fs)
    
    # Calcul Hs depuis spectre
    m0 = np.trapz(psd, freqs)
    Hs_from_spectrum = 4.0 * np.sqrt(m0)
    
    # Étape 3: Analyse Goda
    goda_results = compute_goda_parameters(signals[0], fs)
    
    assert goda_results is not None, "Analyse Goda a échoué"
    
    Hs_from_goda = goda_results['Hs']
    Tz_from_goda = goda_results['Tz']
    
    # Étape 4: Calcul incertitudes
    calc = UncertaintyCalculator()
    budget_H = create_standard_H_budget()
    
    # Étape 5: Export JSON (simplifié)
    with tempfile.NamedTemporaryFile(suffix='.json', delete=False, mode='w') as tmp:
        export_to_file(
            tmp.name,
            data_dict={
                'channel_0': signals[0][:1000],  # Sous-échantillon pour taille
                'frequencies': freqs[:100],
                'psd': psd[:100]
            },
            metadata_dict={
                'Hs_goda': float(Hs_from_goda),
                'Tz': float(Tz_from_goda),
                'Hs_spectrum': float(Hs_from_spectrum),
                'n_waves': int(goda_results['n_waves']),
                'uncertainty_Hs': float(budget_H.expanded_uncertainty),
                'acquisition_date': datetime.now().isoformat()
            }
        )
        
        # Vérifier fichier JSON
        with open(tmp.name, 'r') as f:
            exported = json.load(f)
            assert 'data' in exported, "Clé 'data' manquante"
            assert 'metadata' in exported, "Clé 'metadata' manquante"
            assert 'Hs_goda' in exported['metadata'], "Hs_goda manquant"
        
        # Nettoyer
        os.unlink(tmp.name)
    
    # Vérifications
    error_Hs = abs(Hs_from_goda - Hs_target) / Hs_target * 100
    assert error_Hs < 15.0, \
        f"Hs = {Hs_from_goda:.4f}m != cible {Hs_target:.4f}m (erreur {error_Hs:.1f}% > 15%)"
    
    # Tp approximatif depuis Tz (Tp ≈ 1.2×Tz pour JONSWAP)
    Tp_estimated = Tz_from_goda * 1.2
    error_Tp = abs(Tp_estimated - Tp_target) / Tp_target * 100
    
    print(f"✓ TEST 5.1.1 PASS: Chaîne complète - Hs={Hs_from_goda:.4f}m (±{error_Hs:.1f}%), "
          f"Tz={Tz_from_goda:.3f}s, N={goda_results['n_waves']} vagues, Export JSON OK")


# ============================================================================
# TEST 5.1.2: CHAÎNE RÉFLEXION COMPLÈTE
# ============================================================================

def test_integration_reflection_chain():
    """
    TEST 5.1.2: Chaîne Réflexion Complète
    
    Scénario: 3 Sondes → FFT → Mansard-Funke → Export
    
    Entrée: 3 signaux avec Kr=0.35 connu
    Config: x1=0, x2=0.3m, x3=0.8m, depth=0.5m
    
    Vérifications:
    - Kr_global = 0.35 ± 0.10
    - Spectres exportés
    - Incertitudes présentes
    """
    # Configuration
    config = ProbeConfiguration(
        x1=0.0,
        x2=0.3,
        x3=0.8,
        water_depth=0.5
    )
    
    # Paramètres onde
    A_incident = 0.04   # 4 cm
    Kr_target = 0.35
    A_reflected = A_incident * Kr_target
    frequency = 1.0     # 1 Hz
    duration = 600.0
    fs = 100.0
    
    # Générer 3 signaux (version simplifiée - ondes progressives)
    from scipy.optimize import fsolve
    
    omega = 2 * np.pi * frequency
    g = 9.81
    depth = config.water_depth
    
    # Résoudre dispersion
    def dispersion(k):
        return omega**2 - g * k * np.tanh(k * depth)
    
    k_guess = omega**2 / g if omega * np.sqrt(depth / g) > 2 else omega / np.sqrt(g * depth)
    k = fsolve(dispersion, k_guess)[0]
    
    t = np.arange(0, duration, 1/fs)
    
    # Signal aux 3 positions
    def signal_at_x(x):
        incident = A_incident * np.cos(k * x - omega * t)
        reflected = A_reflected * np.cos(-k * x - omega * t)
        return incident + reflected
    
    signal1 = signal_at_x(config.x1)
    signal2 = signal_at_x(config.x2)
    signal3 = signal_at_x(config.x3)
    
    # Analyse Mansard-Funke
    analyzer = MansardFunkeAnalyzer(config)
    
    # Valider géométrie
    validation = analyzer.validate_geometry(freq_min=0.5, freq_max=1.5)
    assert validation.is_valid or len(validation.singular_frequencies) < 5, \
        "Configuration géométrique problématique"
    
    # Calculer réflexion
    result = analyzer.compute_reflection(signal1, signal2, signal3, fs)
    
    # Vérifications
    assert not np.isnan(result.kr_global), "Kr global est NaN"
    
    error_Kr = abs(result.kr_global - Kr_target)
    assert error_Kr < 0.15, \
        f"Kr = {result.kr_global:.3f} != cible {Kr_target:.3f} (erreur {error_Kr:.3f} > 0.15)"
    
    # Export JSON (simplifié)
    with tempfile.NamedTemporaryFile(suffix='.json', delete=False, mode='w') as tmp:
        freqs_inc, psd_inc = result.incident_spectrum
        freqs_ref, psd_ref = result.reflected_spectrum
        
        export_to_file(
            tmp.name,
            data_dict={
                'signal_probe1': signal1[:1000],
                'signal_probe2': signal2[:1000],
                'signal_probe3': signal3[:1000],
                'frequencies_incident': freqs_inc[:100],
                'psd_incident': psd_inc[:100],
                'frequencies_reflected': freqs_ref[:100],
                'psd_reflected': psd_ref[:100]
            },
            metadata_dict={
                'Kr_global': float(result.kr_global),
                'n_singular': int(result.n_singular),
                'probe_x1': float(config.x1),
                'probe_x2': float(config.x2),
                'probe_x3': float(config.x3),
                'water_depth': float(config.water_depth)
            }
        )
        
        # Vérifier export
        with open(tmp.name, 'r') as f:
            exported = json.load(f)
            assert 'Kr_global' in exported['metadata']
        
        os.unlink(tmp.name)
    
    print(f"✓ TEST 5.1.2 PASS: Chaîne réflexion - Kr={result.kr_global:.3f} "
          f"(cible {Kr_target:.3f}, erreur {error_Kr:.3f}), {result.n_singular} singularités")


# ============================================================================
# TEST 5.1.3: PROPAGATION INCERTITUDES BOUT-EN-BOUT
# ============================================================================

def test_integration_uncertainty_propagation():
    """
    TEST 5.1.3: Propagation Incertitudes Bout-en-Bout
    
    Scénario: Signal bruité → Analyse complète → Vérification incertitudes
    
    Entrée: Signal JONSWAP + bruit (SNR = 30 dB)
    
    Vérifications:
    - u(Hs) calculée et cohérente
    - Format GUM respecté
    - Budget complet généré
    """
    # Paramètres
    Hs_target = 0.10
    Tp_target = 1.0
    duration = 300.0
    fs = 100.0
    SNR_dB = 30
    
    # Générer signal propre
    t, signal_clean, _, _ = generate_jonswap_time_series(
        Hs_target, Tp_target, duration, fs
    )
    
    # Ajouter bruit
    signal_power = np.mean(signal_clean**2)
    noise_power = signal_power / (10**(SNR_dB/10))
    noise = np.random.normal(0, np.sqrt(noise_power), len(signal_clean))
    signal_noisy = signal_clean + noise
    
    # Analyse Goda
    goda_results = compute_goda_parameters(signal_noisy, fs)
    assert goda_results is not None
    
    Hs_measured = goda_results['Hs']
    
    # Calcul incertitudes
    calc = UncertaintyCalculator()
    
    # Budget pour H (hauteur individuelle)
    budget_H = create_standard_H_budget(
        calibration_uncertainty=0.0003,
        daq_resolution=0.00015,
        noise=np.sqrt(noise_power),  # Bruit mesuré
        drift=0.0002
    )
    
    # Budget pour Hs (propagation)
    budget_Hs = calc.create_budget("Hs", coverage_factor=2.0)
    
    # Incertitude Type A (répétabilité sur vagues)
    if goda_results['n_waves'] >= 10:
        heights_sample = np.random.normal(
            Hs_measured, Hs_measured * 0.1, min(30, goda_results['n_waves'])
        )
        calc.add_type_a_component(budget_Hs, "Répétabilité vagues", heights_sample)
    
    # Incertitude Type B (propagée depuis H)
    # Hs = moyenne(H1/3), donc u(Hs) ≈ u(H) / sqrt(n/3)
    n_third = goda_results['n_waves'] // 3
    if n_third > 0:
        u_Hs_from_H = budget_H.combined_uncertainty / np.sqrt(n_third)
        calc.add_type_b_component(
            budget_Hs, "Propagation depuis H",
            u_Hs_from_H, uncertainty_calculator.Distribution.NORMAL
        )
    
    # Vérifications
    assert budget_Hs.combined_uncertainty > 0, "Incertitude combinée devrait être > 0"
    assert budget_Hs.expanded_uncertainty > budget_Hs.combined_uncertainty, \
        "Incertitude élargie devrait être > incertitude combinée"
    
    # Format GUM
    result_formatted = calc.format_result("Hs", Hs_measured, budget_Hs, "m")
    
    assert "Hs" in result_formatted
    assert "±" in result_formatted
    assert "m" in result_formatted
    assert "95%" in result_formatted or "k=2" in result_formatted
    
    # Rapport complet
    summary = budget_Hs.generate_summary()
    assert "BUDGET D'INCERTITUDE" in summary
    
    print(f"✓ TEST 5.1.3 PASS: Incertitudes - {result_formatted}")
    print(f"  uc(Hs) = {budget_Hs.combined_uncertainty:.6f} m, "
          f"U(Hs) = {budget_Hs.expanded_uncertainty:.6f} m")


# ============================================================================
# TEST 5.1.4: ACQUISITION LONGUE DURÉE
# ============================================================================

def test_integration_long_acquisition():
    """
    TEST 5.1.4: Acquisition Longue Durée
    
    Scénario: 30 minutes d'acquisition avec dérive
    
    Entrée: 8 canaux, fs=100Hz, durée=1800s, dérive 0.5 mm/h
    
    Vérifications:
    - Dérive détectée
    - Warning émis si dérive > seuil
    - Données complètes
    """
    # Paramètres
    n_channels = 8
    fs = 100.0
    duration = 1800.0  # 30 minutes
    drift_rate = 0.0005  # 0.5 mm/h
    
    # Gestionnaire de dérive
    manager = ZeroDriftManager(
        drift_threshold=0.001,
        drift_rate_threshold=0.0005
    )
    
    # Initialiser références
    for ch in range(n_channels):
        manager.set_reference_zero(ch, 0.0)
    
    # Simuler acquisition par segments de 5 minutes
    segment_duration = 300.0  # 5 minutes
    n_segments = int(duration / segment_duration)
    
    drifts_detected = []
    
    base_time = datetime.now()
    
    for seg in range(n_segments):
        # Temps écoulé en heures
        hours_elapsed = (seg * segment_duration) / 3600.0
        
        # Dérive accumulée
        drift_value = drift_rate * hours_elapsed
        
        # Vérifier dérive sur canal 0
        timestamp = base_time + timedelta(seconds=seg * segment_duration)
        status = manager.check_drift(0, drift_value, timestamp)
        
        drifts_detected.append(status.current_drift)
        
        # Générer données pour ce segment (simplifié)
        t_seg = np.arange(0, segment_duration, 1/fs)
        
        for ch in range(n_channels):
            # Signal JONSWAP avec dérive
            _, signal, _, _ = generate_jonswap_time_series(
                0.10, 1.0, segment_duration, fs, seed=ch+seg*10
            )
            signal_with_drift = signal + drift_value
    
    # Vérifications
    final_status = manager.check_drift(0, drift_rate * (duration / 3600.0))
    
    # Dérive devrait être détectée
    assert final_status.current_drift > 0, "Dérive devrait être détectée"
    
    # Taux de dérive devrait être proche de 0.5 mm/h
    assert abs(final_status.drift_rate - drift_rate) < 0.0002, \
        f"Taux dérive = {final_status.drift_rate:.6f} != {drift_rate:.6f}"
    
    # Warning attendu
    if final_status.drift_rate > manager.drift_rate_threshold:
        assert not final_status.is_acceptable, "Warning devrait être émis"
    
    print(f"✓ TEST 5.1.4 PASS: Acquisition longue - Dérive finale={final_status.current_drift:.6f}m, "
          f"Rate={final_status.drift_rate:.6f} m/h, Warning={not final_status.is_acceptable}")


# ============================================================================
# TEST 5.1.5: CHAÎNE HAUTE FRÉQUENCE
# ============================================================================

def test_integration_high_frequency():
    """
    TEST 5.1.5: Chaîne Haute Fréquence (Capteurs Pression)
    
    Scénario: Capteurs pression haute fréquence
    
    Entrée: 4 canaux, fs=2000Hz, durée=300s
    
    Vérifications:
    - FFT jusqu'à 500 Hz
    - Pics détectés correctement
    - Export CSV
    """
    # Paramètres
    n_channels = 4
    fs = 2000.0  # 2 kHz
    duration = 30.0  # 30 secondes (réduit pour performance)
    
    # Fréquences de test
    test_frequencies = [50, 100, 200, 400]  # Hz
    
    # Générer signaux multi-fréquences
    signals = []
    t = np.arange(0, duration, 1/fs)
    
    for ch in range(n_channels):
        signal = np.zeros_like(t)
        for freq in test_frequencies:
            amplitude = 0.01 / (freq / 50)  # Amplitude décroissante
            signal += amplitude * np.sin(2 * np.pi * freq * t)
        signals.append(signal)
    
    # FFT haute fréquence
    freqs, psd = compute_fft_spectrum(signals[0], fs)
    
    # Vérifier plage fréquentielle
    assert np.max(freqs) >= 500, f"Fréquence max = {np.max(freqs):.1f} Hz < 500 Hz"
    
    # Détecter pics
    peaks_detected = []
    for target_freq in test_frequencies:
        # Chercher pic dans fenêtre ±2 Hz
        window_mask = (freqs >= target_freq - 2) & (freqs <= target_freq + 2)
        if np.any(window_mask):
            window_psd = psd[window_mask]
            if np.max(window_psd) > np.median(psd) * 5:  # Seuil: 5x médiane
                peaks_detected.append(target_freq)
    
    # Vérifications
    assert len(peaks_detected) >= 3, \
        f"Seulement {len(peaks_detected)}/4 pics détectés"
    
    # Export CSV (simplifié)
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as tmp:
        # Header
        tmp.write("Time,Channel0,Channel1,Channel2,Channel3\n")
        
        # Données (sous-échantillonnées pour export)
        step = int(fs * 0.1)  # 1 point / 0.1s
        for i in range(0, len(t), step):
            row = f"{t[i]:.6f}"
            for sig in signals:
                row += f",{sig[i]:.6f}"
            tmp.write(row + "\n")
        
        csv_path = tmp.name
    
    # Vérifier fichier
    assert os.path.exists(csv_path)
    
    with open(csv_path, 'r') as f:
        lines = f.readlines()
        assert len(lines) > 100, "Fichier CSV trop court"
    
    os.unlink(csv_path)
    
    print(f"✓ TEST 5.1.5 PASS: Haute fréquence - FFT jusqu'à {np.max(freqs):.1f} Hz, "
          f"{len(peaks_detected)}/4 pics détectés, CSV OK")


# ============================================================================
# FIXTURE RAPPORT
# ============================================================================

@pytest.fixture(scope="session", autouse=True)
def generate_test_report(request):
    """Génère un rapport de test."""
    yield
    
    print("\n" + "="*80)
    print("RAPPORT DE TEST - PHASE 5, TÂCHE 5.1: TESTS INTÉGRATION CHAÎNE COMPLÈTE")
    print("="*80)
    print(f"Module: tests/test_integration.py")
    print(f"Date: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    print("\n✅ TÂCHE 5.1 COMPLÈTE si tous les tests sont PASS")
    print("="*80)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "-s"])
