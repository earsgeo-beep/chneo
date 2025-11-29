"""
Module d'Analyse de Réflexion - Méthode Mansard-Funke (Trois Sondes)

Ce module implémente la méthode des trois sondes de Mansard et Funke (1980)
pour la séparation des composantes incidente et réfléchie d'un train de vagues
et le calcul du coefficient de réflexion.

Références scientifiques:
    - Mansard, E.P.D. & Funke, E.R. (1980) - "The measurement of incident and 
      reflected spectra using a least squares method"
    - Zelt, J.A. & Skjelbreia, J.E. (1992) - "Estimating incident and reflected 
      wave fields using an arbitrary number of wave gauges"
    - Isaacson, M. (1991) - "Measurement of regular wave reflection"

Auteur: CHNeoWave Development Team
Phase: 2 - Implémentation Mansard-Funke
"""

import numpy as np
from scipy.linalg import lstsq, svd
from scipy.optimize import fsolve
from typing import Dict, List, Tuple, Optional, NamedTuple
from dataclasses import dataclass
import warnings


# ============================================================================
# STRUCTURES DE DONNÉES
# ============================================================================

@dataclass
class ProbeConfiguration:
    """
    Configuration géométrique des trois sondes.
    
    Attributes:
        x1: Position de la sonde 1 (m) - référence à x=0
        x2: Position de la sonde 2 (m)
        x3: Position de la sonde 3 (m)
        water_depth: Profondeur d'eau (m)
        
    Note:
        Les positions doivent respecter x1 < x2 < x3 par convention.
    """
    x1: float
    x2: float
    x3: float
    water_depth: float
    
    def __post_init__(self):
        """Validation basique de la configuration."""
        if not (self.x1 < self.x2 < self.x3):
            raise ValueError(
                f"Les positions doivent être croissantes: x1={self.x1} < x2={self.x2} < x3={self.x3}"
            )
        
        if self.water_depth <= 0:
            raise ValueError(f"Profondeur d'eau doit être > 0, reçu {self.water_depth}")
    
    @property
    def x12(self) -> float:
        """Espacement entre sondes 1 et 2 (m)."""
        return self.x2 - self.x1
    
    @property
    def x23(self) -> float:
        """Espacement entre sondes 2 et 3 (m)."""
        return self.x3 - self.x2
    
    @property
    def x13(self) -> float:
        """Espacement total entre sondes 1 et 3 (m)."""
        return self.x3 - self.x1


class WaveComponents(NamedTuple):
    """
    Résultats de l'analyse de séparation incident/réfléchi.
    
    Attributes:
        frequency: Fréquence analysée (Hz)
        incident_amplitude: Amplitude complexe onde incidente
        reflected_amplitude: Amplitude complexe onde réfléchie
        reflection_coefficient: Coefficient de réflexion |Ar|/|Ai|
        incident_phase: Phase onde incidente (rad)
        reflected_phase: Phase onde réfléchie (rad)
        wavelength: Longueur d'onde (m)
        wave_number: Nombre d'onde k (rad/m)
        is_singular: True si fréquence près d'une singularité
    """
    frequency: float
    incident_amplitude: complex
    reflected_amplitude: complex
    reflection_coefficient: float
    incident_phase: float
    reflected_phase: float
    wavelength: float
    wave_number: float
    is_singular: bool = False


@dataclass
class ValidationResult:
    """
    Résultat de la validation géométrique.
    
    Attributes:
        is_valid: True si la configuration est acceptable
        warnings: Liste des avertissements
        singular_frequencies: Fréquences à exclure (singularités)
        recommended_spacing: Espacements recommandés pour la plage de fréquences
    """
    is_valid: bool
    warnings: List[str]
    singular_frequencies: List[float]
    recommended_spacing: Dict[str, float]


@dataclass
class ReflectionResult:
    """
    Résultat complet de l'analyse de réflexion.
    
    Attributes:
        kr_global: Coefficient de réflexion global (sans dimension)
        kr_by_frequency: Dictionnaire {fréquence: Kr(f)}
        incident_spectrum: Tuple (fréquences, PSD incident)
        reflected_spectrum: Tuple (fréquences, PSD réfléchi)
        wave_components: Dictionnaire {fréquence: WaveComponents}
        n_singular: Nombre de fréquences exclues (singularités)
    """
    kr_global: float
    kr_by_frequency: Dict[float, float]
    incident_spectrum: Tuple[np.ndarray, np.ndarray]
    reflected_spectrum: Tuple[np.ndarray, np.ndarray]
    wave_components: Dict[float, WaveComponents]
    n_singular: int


# ============================================================================
# VALIDATEUR DE GÉOMÉTRIE
# ============================================================================

class GeometryValidator:
    """
    Validateur de configuration géométrique selon Mansard & Funke (1980).
    
    Vérifie que la configuration des sondes est appropriée pour la plage
    de fréquences d'analyse et détecte les singularités potentielles.
    """
    
    def __init__(self, g: float = 9.81):
        """
        Initialise le validateur.
        
        Args:
            g: Accélération gravitationnelle (m/s²)
        """
        self.g = g
    
    def solve_dispersion_relation(self, omega: float, depth: float) -> float:
        """
        Résout la relation de dispersion: ω² = gk·tanh(kh)
        
        Args:
            omega: Pulsation (rad/s)
            depth: Profondeur d'eau (m)
        
        Returns:
            Nombre d'onde k (rad/m)
        """
        def dispersion_eq(k):
            return omega**2 - self.g * k * np.tanh(k * depth)
        
        # Estimation initiale
        if omega * np.sqrt(depth / self.g) > 2:
            # Eau profonde: k ≈ ω²/g
            k_guess = omega**2 / self.g
        else:
            # Eau peu profonde: k ≈ ω/√(gh)
            k_guess = omega / np.sqrt(self.g * depth)
        
        try:
            k_solution = fsolve(dispersion_eq, k_guess, full_output=True)
            k = k_solution[0][0]
            
            if k_solution[2] != 1 or k <= 0:
                warnings.warn(f"Convergence douteuse pour ω={omega:.3f} rad/s")
                return max(k_guess, 1e-10)
            
            return max(k, 1e-10)
        
        except Exception as e:
            warnings.warn(f"Erreur résolution dispersion: {e}")
            return max(k_guess, 1e-10)
    
    def check_singularity(self, spacing: float, wavelength: float, 
                         tolerance: float = 0.05) -> bool:
        """
        Vérifie si un espacement est proche d'une singularité.
        
        Singularités: X = n × L/2 (n entier)
        
        Args:
            spacing: Espacement entre sondes (m)
            wavelength: Longueur d'onde (m)
            tolerance: Tolérance relative (0.05 = 5%)
        
        Returns:
            True si près d'une singularité
        """
        # Calculer n = 2 × spacing / wavelength
        n = 2.0 * spacing / wavelength
        
        # Distance au plus proche entier
        n_nearest = round(n)
        distance = abs(n - n_nearest)
        
        # Si distance < tolérance, on est près d'une singularité
        return distance < tolerance
    
    def validate_geometry(self, config: ProbeConfiguration, 
                         freq_min: float, freq_max: float) -> ValidationResult:
        """
        Valide la configuration géométrique pour une plage de fréquences.
        
        Args:
            config: Configuration des sondes
            freq_min: Fréquence minimum (Hz)
            freq_max: Fréquence maximum (Hz)
        
        Returns:
            ValidationResult avec diagnostic complet
        """
        warnings_list = []
        singular_frequencies = []
        
        # Vérifier asymétrie (requis par Mansard-Funke)
        if abs(config.x12 - config.x23) < 1e-6:
            warnings_list.append(
                "⚠️ CRITIQUE: Espacements égaux (X₁₂ = X₂₃). "
                "Configuration symétrique non recommandée par Mansard & Funke."
            )
        
        # Analyser plusieurs fréquences dans la plage
        test_frequencies = np.linspace(freq_min, freq_max, 50)
        
        for freq in test_frequencies:
            omega = 2 * np.pi * freq
            k = self.solve_dispersion_relation(omega, config.water_depth)
            wavelength = 2 * np.pi / k if k > 0 else np.inf
            
            # Vérifier singularités pour X₁₂
            if self.check_singularity(config.x12, wavelength):
                singular_frequencies.append(freq)
                continue
            
            # Vérifier singularités pour X₁₃
            if self.check_singularity(config.x13, wavelength):
                if freq not in singular_frequencies:
                    singular_frequencies.append(freq)
        
        # Recommandations HR Wallingford
        # Espacement optimal: L/20 < X < L/3
        omega_peak = 2 * np.pi * ((freq_min + freq_max) / 2)
        k_peak = self.solve_dispersion_relation(omega_peak, config.water_depth)
        L_peak = 2 * np.pi / k_peak if k_peak > 0 else 1.0
        
        recommended_spacing = {
            'L_peak': L_peak,
            'X12_min': L_peak / 20,
            'X12_max': L_peak / 3,
            'X12_optimal': 0.3 * L_peak,
            'X23_optimal': 0.5 * L_peak
        }
        
        # Vérifier limites recommandées
        if config.x12 < L_peak / 20:
            warnings_list.append(
                f"⚠️ X₁₂ = {config.x12:.3f}m < L/20 = {L_peak/20:.3f}m. "
                "Espacement trop petit."
            )
        
        if config.x12 > L_peak / 3:
            warnings_list.append(
                f"⚠️ X₁₂ = {config.x12:.3f}m > L/3 = {L_peak/3:.3f}m. "
                "Espacement trop grand."
            )
        
        # Avertissement sur singularités
        if singular_frequencies:
            n_singular = len(singular_frequencies)
            pct_singular = (n_singular / len(test_frequencies)) * 100
            warnings_list.append(
                f"⚠️ {n_singular} fréquences ({pct_singular:.1f}%) près de singularités. "
                "Ces fréquences seront exclues de l'analyse."
            )
        
        # Configuration valide si < 30% de fréquences singulières
        is_valid = (len(singular_frequencies) / len(test_frequencies)) < 0.3
        
        return ValidationResult(
            is_valid=is_valid,
            warnings=warnings_list,
            singular_frequencies=singular_frequencies,
            recommended_spacing=recommended_spacing
        )


# ============================================================================
# ANALYSEUR MANSARD-FUNKE
# ============================================================================

class MansardFunkeAnalyzer:
    """
    Analyseur de réflexion par méthode des trois sondes (Mansard & Funke, 1980).
    
    Permet la séparation des composantes incidente et réfléchie d'un train de vagues
    et le calcul du coefficient de réflexion Kr.
    
    Example:
        >>> config = ProbeConfiguration(x1=0.0, x2=0.3, x3=0.7, water_depth=0.5)
        >>> analyzer = MansardFunkeAnalyzer(config)
        >>> 
        >>> # Valider la géométrie
        >>> validation = analyzer.validate_geometry(freq_min=0.5, freq_max=3.0)
        >>> if not validation.is_valid:
        >>>     print("Avertissements:", validation.warnings)
        >>> 
        >>> # Analyser les signaux
        >>> result = analyzer.compute_reflection(signal1, signal2, signal3, 
        >>>                                       sampling_rate=100.0)
        >>> 
        >>> print(f"Coefficient de réflexion global: Kr = {result.kr_global:.3f}")
    """
    
    def __init__(self, config: ProbeConfiguration, 
                 svd_threshold: float = 1e-12,
                 g: float = 9.81):
        """
        Initialise l'analyseur Mansard-Funke.
        
        Args:
            config: Configuration géométrique des trois sondes
            svd_threshold: Seuil pour filtre SVD (stabilité numérique)
            g: Accélération gravitationnelle (m/s²)
        """
        self.config = config
        self.svd_threshold = svd_threshold
        self.g = g
        
        # Validateur de géométrie
        self.validator = GeometryValidator(g=g)
        
        # Cache pour les résultats
        self._last_validation: Optional[ValidationResult] = None
    
    def validate_geometry(self, freq_min: float, freq_max: float) -> ValidationResult:
        """
        Valide la configuration géométrique pour une plage de fréquences.
        
        Args:
            freq_min: Fréquence minimum d'analyse (Hz)
            freq_max: Fréquence maximum d'analyse (Hz)
        
        Returns:
            ValidationResult avec diagnostic
        """
        self._last_validation = self.validator.validate_geometry(
            self.config, freq_min, freq_max
        )
        return self._last_validation
    
    def _build_transfer_matrix(self, k: float) -> np.ndarray:
        """
        Construit la matrice de transfert M pour un nombre d'onde k.
        
        Matrice M (3×2):
            M = | e^(ikx₁)   e^(-ikx₁) |
                | e^(ikx₂)   e^(-ikx₂) |
                | e^(ikx₃)   e^(-ikx₃) |
        
        Args:
            k: Nombre d'onde (rad/m)
        
        Returns:
            Matrice M (3×2) complexe
        """
        M = np.zeros((3, 2), dtype=complex)
        
        # Positions des sondes
        positions = [self.config.x1, self.config.x2, self.config.x3]
        
        for i, x in enumerate(positions):
            M[i, 0] = np.exp(1j * k * x)   # Onde incidente
            M[i, 1] = np.exp(-1j * k * x)  # Onde réfléchie
        
        return M
    
    def _solve_least_squares_svd(self, M: np.ndarray, 
                                 Z: np.ndarray) -> Tuple[complex, complex, bool]:
        """
        Résout le système linéaire par moindres carrés avec SVD.
        
        Résout: M × [Aᵢ, Aᵣ]ᵀ = Z
        
        Args:
            M: Matrice de transfert (3×2)
            Z: Vecteur des observations (3×1)
        
        Returns:
            Tuple (Aᵢ, Aᵣ, is_singular)
        """
        # Décomposition SVD
        U, s, Vt = svd(M, full_matrices=False)
        
        # Vérifier conditionnement
        condition_number = s[0] / s[-1] if s[-1] > 0 else np.inf
        
        is_singular = condition_number > 1e10
        
        if is_singular:
            # Matrice mal conditionnée, retourner NaN
            return complex(np.nan), complex(np.nan), True
        
        # Filtrer valeurs singulières faibles
        valid_indices = s > self.svd_threshold
        U_filtered = U[:, valid_indices]
        s_filtered = s[valid_indices]
        Vt_filtered = Vt[valid_indices, :]
        
        if len(s_filtered) < 2:
            return complex(np.nan), complex(np.nan), True
        
        # Pseudo-inverse via SVD
        s_inv = 1.0 / s_filtered
        M_pinv = Vt_filtered.T @ np.diag(s_inv) @ U_filtered.T
        
        # Solution
        solution = M_pinv @ Z
        
        A_incident = solution[0]
        A_reflected = solution[1]
        
        return A_incident, A_reflected, False
    
    def analyze_frequency(self, Z1: complex, Z2: complex, Z3: complex, 
                         frequency: float) -> WaveComponents:
        """
        Analyse une fréquence spécifique.
        
        Args:
            Z1, Z2, Z3: Amplitudes complexes FFT aux trois sondes
            frequency: Fréquence d'analyse (Hz)
        
        Returns:
            WaveComponents avec résultats de séparation
        """
        # Nombre d'onde
        omega = 2 * np.pi * frequency
        k = self.validator.solve_dispersion_relation(omega, self.config.water_depth)
        wavelength = 2 * np.pi / k if k > 0 else np.inf
        
        # Vérifier singularité
        is_singular = (
            self.validator.check_singularity(self.config.x12, wavelength) or
            self.validator.check_singularity(self.config.x13, wavelength)
        )
        
        if is_singular:
            # Retourner composantes NaN
            return WaveComponents(
                frequency=frequency,
                incident_amplitude=complex(np.nan),
                reflected_amplitude=complex(np.nan),
                reflection_coefficient=np.nan,
                incident_phase=np.nan,
                reflected_phase=np.nan,
                wavelength=wavelength,
                wave_number=k,
                is_singular=True
            )
        
        # Construire matrice de transfert
        M = self._build_transfer_matrix(k)
        
        # Vecteur observations
        Z = np.array([Z1, Z2, Z3])
        
        # Résolution
        A_incident, A_reflected, failed = self._solve_least_squares_svd(M, Z)
        
        if failed:
            is_singular = True
        
        # Calculs
        incident_amplitude_mag = abs(A_incident)
        reflected_amplitude_mag = abs(A_reflected)
        
        if incident_amplitude_mag > 1e-12:
            kr = reflected_amplitude_mag / incident_amplitude_mag
        else:
            kr = np.nan
        
        incident_phase = np.angle(A_incident)
        reflected_phase = np.angle(A_reflected)
        
        return WaveComponents(
            frequency=frequency,
            incident_amplitude=A_incident,
            reflected_amplitude=A_reflected,
            reflection_coefficient=kr,
            incident_phase=incident_phase,
            reflected_phase=reflected_phase,
            wavelength=wavelength,
            wave_number=k,
            is_singular=is_singular
        )
    
    def compute_reflection(self, signal1: np.ndarray, signal2: np.ndarray, 
                          signal3: np.ndarray, sampling_rate: float) -> ReflectionResult:
        """
        Calcule le coefficient de réflexion à partir de trois signaux temporels.
        
        Args:
            signal1, signal2, signal3: Signaux temporels des trois sondes
            sampling_rate: Fréquence d'échantillonnage (Hz)
        
        Returns:
            ReflectionResult avec Kr global, Kr(f), spectres
        """
        # Vérifier longueurs
        if not (len(signal1) == len(signal2) == len(signal3)):
            raise ValueError("Les trois signaux doivent avoir la même longueur")
        
        N = len(signal1)
        
        # FFT des trois signaux
        FFT1 = np.fft.fft(signal1)
        FFT2 = np.fft.fft(signal2)
        FFT3 = np.fft.fft(signal3)
        
        freqs = np.fft.fftfreq(N, 1/sampling_rate)
        
        # Partie positive uniquement
        positive_mask = freqs > 0
        positive_freqs = freqs[positive_mask]
        Z1_positive = FFT1[positive_mask]
        Z2_positive = FFT2[positive_mask]
        Z3_positive = FFT3[positive_mask]
        
        # Analyser chaque fréquence
        wave_components = {}
        kr_by_freq = {}
        incident_spectrum = []
        reflected_spectrum = []
        n_singular = 0
        
        for i, freq in enumerate(positive_freqs):
            result = self.analyze_frequency(
                Z1_positive[i], Z2_positive[i], Z3_positive[i], freq
            )
            
            wave_components[freq] = result
            
            if not result.is_singular and not np.isnan(result.reflection_coefficient):
                kr_by_freq[freq] = result.reflection_coefficient
                incident_spectrum.append(abs(result.incident_amplitude)**2)
                reflected_spectrum.append(abs(result.reflected_amplitude)**2)
            else:
                n_singular += 1
                incident_spectrum.append(0.0)
                reflected_spectrum.append(0.0)
        
        # Coefficient de réflexion global
        # Kr_global = √(m0_réfléchi / m0_incident)
        incident_spectrum_arr = np.array(incident_spectrum)
        reflected_spectrum_arr = np.array(reflected_spectrum)
        
        m0_incident = np.trapz(incident_spectrum_arr, positive_freqs)
        m0_reflected = np.trapz(reflected_spectrum_arr, positive_freqs)
        
        if m0_incident > 0:
            kr_global = np.sqrt(m0_reflected / m0_incident)
        else:
            kr_global = np.nan
        
        return ReflectionResult(
            kr_global=kr_global,
            kr_by_frequency=kr_by_freq,
            incident_spectrum=(positive_freqs, incident_spectrum_arr),
            reflected_spectrum=(positive_freqs, reflected_spectrum_arr),
            wave_components=wave_components,
            n_singular=n_singular
        )
    
    def get_incident_spectrum(self, result: ReflectionResult) -> Tuple[np.ndarray, np.ndarray]:
        """Retourne le spectre de houle incidente."""
        return result.incident_spectrum
    
    def get_reflected_spectrum(self, result: ReflectionResult) -> Tuple[np.ndarray, np.ndarray]:
        """Retourne le spectre de houle réfléchie."""
        return result.reflected_spectrum
    
    def get_kr_by_frequency(self, result: ReflectionResult) -> Tuple[np.ndarray, np.ndarray]:
        """Retourne Kr(f) pour chaque fréquence."""
        frequencies = list(result.kr_by_frequency.keys())
        kr_values = list(result.kr_by_frequency.values())
        return np.array(frequencies), np.array(kr_values)


# ============================================================================
# FONCTIONS UTILITAIRES
# ============================================================================

def create_probe_configuration(x1: float, x2: float, x3: float, 
                              depth: float) -> ProbeConfiguration:
    """
    Fonction utilitaire pour créer une configuration de sondes.
    
    Args:
        x1, x2, x3: Positions des sondes (m)
        depth: Profondeur d'eau (m)
    
    Returns:
        ProbeConfiguration validée
    """
    return ProbeConfiguration(x1=x1, x2=x2, x3=x3, water_depth=depth)


if __name__ == "__main__":
    # Exemple d'utilisation
    print("="*80)
    print("MODULE MANSARD-FUNKE - EXEMPLE D'UTILISATION")
    print("="*80)
    
    # Configuration
    config = ProbeConfiguration(
        x1=0.0,   # Sonde 1 à l'origine
        x2=0.3,   # Sonde 2 à 30 cm
        x3=0.7,   # Sonde 3 à 70 cm
        water_depth=0.5  # 50 cm de profondeur
    )
    
    print(f"\nConfiguration géométrique:")
    print(f"  Sonde 1: x₁ = {config.x1:.2f} m")
    print(f"  Sonde 2: x₂ = {config.x2:.2f} m")
    print(f"  Sonde 3: x₃ = {config.x3:.2f} m")
    print(f"  Profondeur: h = {config.water_depth:.2f} m")
    print(f"  Espacement X₁₂ = {config.x12:.2f} m")
    print(f"  Espacement X₂₃ = {config.x23:.2f} m")
    
    # Analyseur
    analyzer = MansardFunkeAnalyzer(config)
    
    # Validation
    validation = analyzer.validate_geometry(freq_min=0.5, freq_max=2.0)
    
    print(f"\nValidation géométrique:")
    print(f"  Valide: {validation.is_valid}")
    print(f"  Nombre d'avertissements: {len(validation.warnings)}")
    
    if validation.warnings:
        print("\n  Avertissements:")
        for warning in validation.warnings:
            print(f"    - {warning}")
    
    print(f"\n  Espacements recommandés:")
    print(f"    L_pic ≈ {validation.recommended_spacing['L_peak']:.3f} m")
    print(f"    X₁₂ optimal ≈ {validation.recommended_spacing['X12_optimal']:.3f} m")
    print(f"    X₂₃ optimal ≈ {validation.recommended_spacing['X23_optimal']:.3f} m")
    
    print("\n" + "="*80)
    print("Structure du module créée avec succès ✓")
    print("="*80)
