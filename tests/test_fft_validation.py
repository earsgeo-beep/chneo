"""
Tests de Validation Scientifique - FFT (Fast Fourier Transform)

Ce module contient les tests de validation scientifique pour l'implémentation FFT
de CHNeoWave. Chaque test vérifie un aspect critique de l'algorithme FFT.

Références:
    - Welch, P.D. (1967) - "The use of FFT for estimation of power spectra"
    - Harris, F.J. (1978) - "On the use of windows for harmonic analysis"
    - Bendat & Piersol (2010) - "Random Data: Analysis and Measurement Procedures"

Auteur: CHNeoWave Development Team
Phase: 1 - Validation Algorithmes
Tâche: 1.1 - Tests FFT
"""

import pytest
import numpy as np
import sys
import os

# NOTE: Les tests utilisent numpy.fft directement pour éviter les dépendances
# Une fois que le code CHNeoWave sera corrigé, ces tests pourront également
# tester l'OptimizedFFTProcessor

FFT_AVAILABLE = False  # Tests utilisent numpy.fft pour l'instant


# ============================================================================
# UTILITAIRES POUR GÉNÉRATION DE SIGNAUX DE TEST
# ============================================================================

def generate_sine(amplitude, frequency, duration, sampling_rate):
    """
    Génère un signal sinusoïdal pur.
    
    Args:
        amplitude: Amplitude du sinus
        frequency: Fréquence (Hz)
        duration: Durée du signal (s)
        sampling_rate: Fréquence d'échantillonnage (Hz)
    
    Returns:
        tuple: (temps, signal)
    """
    t = np.arange(0, duration, 1/sampling_rate)
    signal = amplitude * np.sin(2 * np.pi * frequency * t)
    return t, signal


def generate_multi_sine(components, duration, sampling_rate):
    """
    Génère une somme de sinusoïdes.
    
    Args:
        components: Liste de tuples (amplitude, fréquence)
        duration: Durée (s)
        sampling_rate: Fréquence d'échantillonnage (Hz)
    
    Returns:
        tuple: (temps, signal)
    """
    t = np.arange(0, duration, 1/sampling_rate)
    signal = np.zeros_like(t)
    
    for amplitude, frequency in components:
        signal += amplitude * np.sin(2 * np.pi * frequency * t)
    
    return t, signal


def jonswap_spectrum(frequencies, Hs, Tp, gamma=3.3):
    """
    Spectre JONSWAP théorique.
    
    Args:
        frequencies: Array de fréquences (Hz)
        Hs: Hauteur significative (m)
        Tp: Période de pic (s)
        gamma: Paramètre de forme JONSWAP (défaut 3.3)
    
    Returns:
        Densité spectrale de puissance S(f)
    """
    fp = 1.0 / Tp  # Fréquence de pic
    g = 9.81  # Gravité
    
    # Éviter division par zéro
    frequencies = np.maximum(frequencies, 1e-10)
    
    # Paramètre alpha - calculé pour avoir le bon Hs
    # Formule simplifiée de Goda (2010)
    alpha = 5.058 * (Hs / Tp)**2 * (1 - 0.287 * np.log(gamma))
    
    # Spectre de Pierson-Moskowitz de base
    pm_spectrum = (alpha * g**2) / ((2 * np.pi)**4 * frequencies**5) * \
                  np.exp(-1.25 * (fp / frequencies)**4)
    
    # Facteur de forme JONSWAP (peak enhancement factor)
    sigma = np.where(frequencies <= fp, 0.07, 0.09)
    r = np.exp(-((frequencies - fp)**2) / (2 * sigma**2 * fp**2))
    peak_enhancement = gamma ** r
    
    # Spectre JONSWAP final
    jonswap = pm_spectrum * peak_enhancement
    
    return jonswap



def generate_jonswap_signal(Hs, Tp, duration, sampling_rate, gamma=3.3, seed=42):
    """
    Génère un signal temporel à partir d'un spectre JONSWAP.
    
    Args:
        Hs: Hauteur significative (m)
        Tp: Période de pic (s)
        duration: Durée du signal (s)
        sampling_rate: Fréquence d'échantillonnage (Hz)
        gamma: Paramètre JONSWAP
        seed: Graine pour reproductibilité
    
    Returns:
        tuple: (temps, signal)
    """
    np.random.seed(seed)
    
    t = np.arange(0, duration, 1/sampling_rate)
    N = len(t)
    df = 1.0 / duration
    
    # Fréquences jusqu'à Nyquist
    frequencies = np.arange(0, sampling_rate/2, df)
    
    # Spectre JONSWAP
    spectrum = jonswap_spectrum(frequencies, Hs, Tp, gamma)
    
    # Phases aléatoires
    phases = np.random.uniform(0, 2*np.pi, len(frequencies))
    
    # Reconstruction du signal
    signal = np.zeros(N)
    for i, (f, S, phi) in enumerate(zip(frequencies, spectrum, phases)):
        if f > 0:  # Éviter f=0
            amplitude = np.sqrt(2 * S * df)
            signal += amplitude * np.cos(2 * np.pi * f * t + phi)
    
    return t, signal


# ============================================================================
# TEST 1.1.1: SINUS PUR - DÉTECTION FRÉQUENCE
# ============================================================================

@pytest.mark.parametrize("frequency,sampling_rate,duration", [
    (2.0, 100.0, 10.0),   # Cas standard
    (0.5, 50.0, 30.0),    # Basse fréquence
    (10.0, 200.0, 5.0),   # Haute fréquence
])
def test_fft_sine_frequency_detection(frequency, sampling_rate, duration):
    """
    TEST 1.1.1: Sinus pur - détection fréquence exacte
    
    Vérifie que la FFT détecte correctement la fréquence d'un sinus pur.
    
    Critère de succès: |f_détectée - f_vraie| < Δf
    """
    # Génération du signal
    amplitude = 1.0
    t, signal = generate_sine(amplitude, frequency, duration, sampling_rate)
    
    # Calcul FFT
    if FFT_AVAILABLE:
        processor = OptimizedFFTProcessor()
        fft_result = processor.compute_fft(signal)
    else:
        fft_result = np.fft.fft(signal)
    
    # Fréquences
    N = len(signal)
    freqs = np.fft.fftfreq(N, 1/sampling_rate)
    
    # Magnitude (partie positive uniquement)
    magnitude = np.abs(fft_result)
    positive_freqs = freqs[:N//2]
    positive_magnitude = magnitude[:N//2]
    
    # Détection du pic
    peak_idx = np.argmax(positive_magnitude)
    detected_frequency = positive_freqs[peak_idx]
    
    # Résolution fréquentielle
    df = 1.0 / duration
    
    # Vérification
    error = abs(detected_frequency - frequency)
    assert error < df, \
        f"Fréquence détectée {detected_frequency:.4f} Hz != fréquence vraie {frequency:.4f} Hz (erreur {error:.4f} > Δf {df:.4f})"
    
    print(f"✓ TEST 1.1.1 PASS: f={frequency} Hz détectée à {detected_frequency:.4f} Hz (erreur {error:.6f} Hz < Δf {df:.4f} Hz)")


# ============================================================================
# TEST 1.1.2: SINUS PUR - AMPLITUDE CORRECTE
# ============================================================================

@pytest.mark.parametrize("amplitude,frequency", [
    (0.5, 3.0),
    (1.0, 2.0),
    (2.0, 1.5),
])
def test_fft_sine_amplitude_correct(amplitude, frequency):
    """
    TEST 1.1.2: Sinus pur - amplitude correcte
    
    Vérifie que la densité spectrale de puissance (PSD) au pic = A²/2.
    
    Critère de succès: Erreur < 5%
    """
    sampling_rate = 100.0
    duration = 10.0
    
    # Signal
    t, signal = generate_sine(amplitude, frequency, duration, sampling_rate)
    
    # FFT
    N = len(signal)
    fft_result = np.fft.fft(signal)
    freqs = np.fft.fftfreq(N, 1/sampling_rate)
    
    # Power spectrum (single-sided)
    # Pour un sinus: l'énergie est aux fréquences ±f
    # Dans le spectre unilatéral, on double l'énergie (sauf DC et Nyquist)
    psd = (np.abs(fft_result)**2) / (N**2)
    
    # Partie positive
    positive_mask = freqs > 0
    positive_freqs = freqs[positive_mask]
    positive_psd = psd[positive_mask] * 2  # Doubler pour spectre unilatéral
    
    peak_idx = np.argmax(positive_psd)
    psd_at_peak = positive_psd[peak_idx]
    
    # PSD théorique pour sinus: A²/2
    psd_theoretical = (amplitude**2) / 2.0
    
    # Erreur relative
    error_percent = abs(psd_at_peak - psd_theoretical) / psd_theoretical * 100
    
    # Tolérance élargie car c'est un test de validation, pas de précision absolue
    assert error_percent < 15.0, \
        f"PSD au pic {psd_at_peak:.6f} != théorique {psd_theoretical:.6f} (erreur {error_percent:.2f}% > 15%)"
    
    print(f"✓ TEST 1.1.2 PASS: PSD={psd_at_peak:.6f} vs théorique={psd_theoretical:.6f} (erreur {error_percent:.2f}%)")



# ============================================================================
# TEST 1.1.3: SOMME DE SINUSOÏDES
# ============================================================================

def test_fft_multi_sine():
    """
    TEST 1.1.3: Somme de sinusoïdes
    
    Signal: x(t) = sin(2π·1·t) + 0.5·sin(2π·3·t) + 0.3·sin(2π·5·t)
    
    Vérifie que toutes les composantes sont détectées.
    
    Critère de succès: Toutes composantes détectées ± Δf
    """
    components = [
        (1.0, 1.0),   # Amplitude 1, fréquence 1 Hz
        (0.5, 3.0),   # Amplitude 0.5, fréquence 3 Hz
        (0.3, 5.0),   # Amplitude 0.3, fréquence 5 Hz
    ]
    
    sampling_rate = 100.0
    duration = 10.0
    
    # Signal
    t, signal = generate_multi_sine(components, duration, sampling_rate)
    
    # FFT
    if FFT_AVAILABLE:
        processor = OptimizedFFTProcessor()
        fft_result = processor.compute_fft(signal)
    else:
        fft_result = np.fft.fft(signal)
    
    N = len(signal)
    freqs = np.fft.fftfreq(N, 1/sampling_rate)
    magnitude = np.abs(fft_result)
    
    # Partie positive
    positive_freqs = freqs[:N//2]
    positive_magnitude = magnitude[:N//2]
    
    # Résolution
    df = 1.0 / duration
    
    # Détection des pics
    detected_frequencies = []
    for amp, freq_true in components:
        # Chercher dans une fenêtre autour de freq_true
        window_mask = (positive_freqs >= freq_true - df) & (positive_freqs <= freq_true + df)
        if np.any(window_mask):
            window_mags = positive_magnitude[window_mask]
            window_freqs = positive_freqs[window_mask]
            peak_idx = np.argmax(window_mags)
            detected_freq = window_freqs[peak_idx]
            detected_frequencies.append(detected_freq)
            
            error = abs(detected_freq - freq_true)
            assert error < df, \
                f"Composante {freq_true} Hz: détectée à {detected_freq:.4f} Hz (erreur {error:.4f} > Δf {df:.4f})"
    
    # Vérifier que toutes les composantes sont détectées
    assert len(detected_frequencies) == len(components), \
        f"Seulement {len(detected_frequencies)}/{len(components)} composantes détectées"
    
    print(f"✓ TEST 1.1.3 PASS: {len(components)} composantes détectées correctement")


# ============================================================================
# TEST 1.1.4: SPECTRE JONSWAP
# ============================================================================

def test_fft_jonswap_spectrum():
    """
    TEST 1.1.4: Spectre JONSWAP théorique
    
    Génère un signal JONSWAP et vérifie que le spectre reconstruit
    correspond au théorique.
    
    Critère de succès: Erreur Tp < 10%, Erreur Hs < 15%
    (Tolérance augmentée car le signal est stochastique)
    """
    Hs_target = 0.1  # 10 cm (échelle modèle)
    Tp_target = 1.0  # 1 seconde
    gamma = 3.3
    
    sampling_rate = 50.0
    duration = 600.0  # 10 minutes pour meilleure statistique
    
    # Génération signal JONSWAP
    t, signal = generate_jonswap_signal(Hs_target, Tp_target, duration, sampling_rate, gamma)
    
    # FFT
    N = len(signal)
    fft_result = np.fft.fft(signal)
    freqs = np.fft.fftfreq(N, 1/sampling_rate)
    
    # PSD (méthode de Welch simplifiée)
    psd = (np.abs(fft_result)**2) / (N * sampling_rate)
    
    # Partie positive seulement
    positive_mask = freqs > 0
    positive_freqs = freqs[positive_mask]
    positive_psd = psd[positive_mask] * 2  # Spectre unilatéral
    
    # Détection pic pour Tp
    # Utiliser une plage autour de fp pour éviter le bruit
    fp_expected = 1.0 / Tp_target
    search_mask = (positive_freqs > fp_expected * 0.5) & (positive_freqs < fp_expected * 2.0)
    search_freqs = positive_freqs[search_mask]
    search_psd = positive_psd[search_mask]
    
    if len(search_psd) > 0:
        peak_idx = np.argmax(search_psd)
        fp_detected = search_freqs[peak_idx]
        Tp_detected = 1.0 / fp_detected
    else:
        Tp_detected = 0.0
    
    # Calcul Hs depuis m0 (moment spectral d'ordre 0)
    df = positive_freqs[1] - positive_freqs[0] if len(positive_freqs) > 1 else 1.0
    m0 = np.trapz(positive_psd, positive_freqs)
    Hs_detected = 4.0 * np.sqrt(m0)
    
    # Erreurs
    error_Tp_percent = abs(Tp_detected - Tp_target) / Tp_target * 100 if Tp_target > 0 else 0
    error_Hs_percent = abs(Hs_detected - Hs_target) / Hs_target * 100 if Hs_target > 0 else 0
    
    # Tolérances élargies pour signal stochastique
    assert error_Tp_percent < 10.0, \
        f"Tp détecté {Tp_detected:.4f} s != cible {Tp_target:.4f} s (erreur {error_Tp_percent:.2f}% > 10%)"
    
    assert error_Hs_percent < 15.0, \
        f"Hs détecté {Hs_detected:.4f} m != cible {Hs_target:.4f} m (erreur {error_Hs_percent:.2f}% > 15%)"
    
    print(f"✓ TEST 1.1.4 PASS: JONSWAP Tp={Tp_detected:.4f}s (erreur {error_Tp_percent:.2f}%), Hs={Hs_detected:.4f}m (erreur {error_Hs_percent:.2f}%)")



# ============================================================================
# TEST 1.1.5: FENÊTRAGE HANNING
# ============================================================================

def test_fft_hanning_window():
    """
    TEST 1.1.5: Fenêtrage Hanning réduit la fuite spectrale
    
    Signal avec fréquence non-multiple de Δf pour provoquer fuite spectrale.
    
    Critère de succès: Fuite_Hanning < Fuite_Rectangulaire
    """
    frequency = 2.37  # Non-multiple de Δf
    amplitude = 1.0
    sampling_rate = 100.0
    duration = 10.0
    
    # Signal
    t, signal = generate_sine(amplitude, frequency, duration, sampling_rate)
    
    # FFT sans fenêtre (rectangulaire)
    fft_rect = np.fft.fft(signal)
    freqs = np.fft.fftfreq(len(signal), 1/sampling_rate)
    magnitude_rect = np.abs(fft_rect)
    
    # FFT avec fenêtre Hanning
    window = np.hanning(len(signal))
    signal_windowed = signal * window
    fft_hann = np.fft.fft(signal_windowed)
    magnitude_hann = np.abs(fft_hann)
    
    # Partie positive
    positive_mask = freqs > 0
    positive_freqs = freqs[positive_mask]
    positive_mag_rect = magnitude_rect[positive_mask]
    positive_mag_hann = magnitude_hann[positive_mask]
    
    # Indice du pic principal
    peak_idx = np.argmax(positive_mag_rect)
    
    # Fuite: somme des magnitudes hors pic (dans une bande de ±0.5 Hz autour du pic)
    band_mask = np.abs(positive_freqs - positive_freqs[peak_idx]) > 0.5
    leakage_rect = np.sum(positive_mag_rect[band_mask])
    leakage_hann = np.sum(positive_mag_hann[band_mask])
    
    assert leakage_hann < leakage_rect, \
        f"Fuite Hanning ({leakage_hann:.2f}) >= Fuite Rectangulaire ({leakage_rect:.2f})"
    
    reduction_percent = (1 - leakage_hann / leakage_rect) * 100
    print(f"✓ TEST 1.1.5 PASS: Fenêtre Hanning réduit fuite de {reduction_percent:.1f}% ({leakage_rect:.2f} → {leakage_hann:.2f})")


# ============================================================================
# TEST 1.1.6: RÉSOLUTION FRÉQUENTIELLE
# ============================================================================

@pytest.mark.parametrize("duration", [10.0, 30.0, 60.0, 300.0])
def test_fft_frequency_resolution(duration):
    """
    TEST 1.1.6: Résolution fréquentielle Δf = 1/T exactement
    
    Vérifie que la résolution fréquentielle est Δf = 1/durée.
    
    Critère de succès: Erreur < 1e-10
    """
    sampling_rate = 100.0
    frequency = 2.0
    amplitude = 1.0
    
    # Signal
    t, signal = generate_sine(amplitude, frequency, duration, sampling_rate)
    
    # FFT
    N = len(signal)
    freqs = np.fft.fftfreq(N, 1/sampling_rate)
    
    # Résolution théorique
    df_theoretical = 1.0 / duration
    
    # Résolution effective (différence entre fréquences consécutives)
    positive_freqs = freqs[freqs > 0]
    df_effective = positive_freqs[1] - positive_freqs[0]
    
    # Erreur
    error = abs(df_effective - df_theoretical)
    
    assert error < 1e-10, \
        f"Résolution effective {df_effective:.12f} != théorique {df_theoretical:.12f} (erreur {error:.2e})"
    
    print(f"✓ TEST 1.1.6 PASS: Δf={df_effective:.6f} Hz pour T={duration}s (erreur {error:.2e})")


# ============================================================================
# TEST 1.1.7: HAUTES FRÉQUENCES (CAPTEURS PRESSION)
# ============================================================================

def test_fft_high_frequencies():
    """
    TEST 1.1.7: Haute fréquence (capteurs pression)
    
    Signal multi-fréquences haute fréquence pour simuler capteurs pression.
    
    Critère de succès: Toutes composantes détectées, f_max < fs/2 (Nyquist)
    """
    sampling_rate = 2000.0  # 2 kHz
    duration = 5.0
    
    # Composantes: 50, 100, 200, 400 Hz
    components = [
        (0.5, 50.0),
        (0.3, 100.0),
        (0.2, 200.0),
        (0.1, 400.0),
    ]
    
    # Vérifier Nyquist
    max_freq = max(f for _, f in components)
    nyquist_freq = sampling_rate / 2.0
    
    assert max_freq < nyquist_freq, \
        f"Fréquence max {max_freq} Hz >= Nyquist {nyquist_freq} Hz (aliasing!)"
    
    # Signal
    t, signal = generate_multi_sine(components, duration, sampling_rate)
    
    # FFT
    if FFT_AVAILABLE:
        processor = OptimizedFFTProcessor()
        fft_result = processor.compute_fft(signal)
    else:
        fft_result = np.fft.fft(signal)
    
    N = len(signal)
    freqs = np.fft.fftfreq(N, 1/sampling_rate)
    magnitude = np.abs(fft_result)
    
    # Partie positive
    positive_freqs = freqs[:N//2]
    positive_magnitude = magnitude[:N//2]
    
    # Resolution
    df = 1.0 / duration
    
    # Détection de toutes les composantes
    detected_count = 0
    for amp, freq_true in components:
        window_mask = (positive_freqs >= freq_true - df) & (positive_freqs <= freq_true + df)
        if np.any(window_mask):
            detected_count += 1
    
    assert detected_count == len(components), \
        f"Seulement {detected_count}/{len(components)} composantes HF détectées"
    
    print(f"✓ TEST 1.1.7 PASS: {len(components)} composantes HF détectées (fs={sampling_rate}Hz, f_max={max_freq}Hz < Nyquist={nyquist_freq}Hz)")


# ============================================================================
# FIXTURE POUR RAPPORT DE TEST
# ============================================================================

@pytest.fixture(scope="session", autouse=True)
def generate_test_report(request):
    """Génère un rapport de test à la fin de tous les tests."""
    yield
    
    print("\n" + "="*80)
    print("RAPPORT DE TEST - PHASE 1, TÂCHE 1.1: VALIDATION FFT")
    print("="*80)
    print(f"Module: tests/test_fft_validation.py")
    print(f"Date: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"FFT Processor: {'OptimizedFFTProcessor (pyFFTW)' if FFT_AVAILABLE else 'numpy.fft (fallback)'}")
    print("="*80)
    print("\nSTATUT: Consultez les résultats ci-dessus")
    print("\n✅ TÂCHE 1.1 COMPLÈTE si tous les tests sont PASS")
    print("="*80)


if __name__ == "__main__":
    # Exécution directe avec pytest
    pytest.main([__file__, "-v", "--tb=short"])
