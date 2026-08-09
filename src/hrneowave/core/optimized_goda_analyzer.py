"""Module d'analyse Goda optimisé pour CHNeoWave

Ce module remplace l'implémentation Goda basique par une version optimisée
utilisant SVD, cache intelligent et stabilité numérique améliorée.

Gains de performance attendus: +1000% avec cache géométrie fixe
"""

import hashlib
import warnings
from collections import OrderedDict
from dataclasses import dataclass
from typing import NamedTuple

import numpy as np
from scipy.linalg import svd
from scipy.optimize import brentq


@dataclass
class ProbeGeometry:
    """Configuration géométrique des sondes"""

    positions: np.ndarray  # Positions des sondes [m]
    water_depth: float  # Profondeur d'eau [m]
    frequency_range: tuple[float, float]  # Plage de fréquences [Hz]

    def __post_init__(self):
        self.positions = np.asarray(self.positions, dtype=np.float64)
        if self.positions.ndim != 1 or len(self.positions) < 2:
            raise ValueError("Au moins deux positions de sonde sont requises")
        if not np.all(np.isfinite(self.positions)):
            raise ValueError("Les positions de sonde doivent etre finies")
        if len(np.unique(self.positions)) != len(self.positions):
            raise ValueError("Les positions de sonde doivent etre distinctes")
        if not np.isfinite(self.water_depth) or self.water_depth <= 0:
            raise ValueError("La profondeur d'eau doit etre strictement positive")
        frequency_min, frequency_max = map(float, self.frequency_range)
        if (
            not np.isfinite(frequency_min)
            or not np.isfinite(frequency_max)
            or frequency_min <= 0
            or frequency_max <= frequency_min
        ):
            raise ValueError("La plage de frequences doit verifier 0 < fmin < fmax")
        self.water_depth = float(self.water_depth)
        self.frequency_range = (frequency_min, frequency_max)
        self.n_probes = len(self.positions)
        self.geometry_hash = self._compute_hash()

    def _compute_hash(self) -> str:
        """Calcule un hash unique pour cette géométrie"""
        data = np.concatenate([self.positions.flatten(), [self.water_depth], list(self.frequency_range)])
        return hashlib.md5(data.tobytes()).hexdigest()[:16]


class WaveComponents(NamedTuple):
    """Résultats de l'analyse de séparation des ondes"""

    incident_amplitude: float
    reflected_amplitude: float
    reflection_coefficient: float
    phase_incident: float
    phase_reflected: float
    frequency: float
    wavelength: float
    wave_number: float
    condition_number: float
    normalized_residual: float


class OptimizedGodaAnalyzer:
    """Analyseur Goda optimisé avec SVD et cache intelligent"""

    def __init__(
        self,
        geometry: ProbeGeometry,
        cache_size: int = 128,
        svd_threshold: float = 1e-12,
        enable_cache: bool = True,
    ):
        """
        Initialise l'analyseur Goda optimisé

        Args:
            geometry: Configuration géométrique des sondes
            cache_size: Taille du cache LRU pour les matrices
            svd_threshold: Seuil pour la troncature SVD
            enable_cache: Active le cache des matrices
        """
        self.geometry = geometry
        if cache_size <= 0:
            raise ValueError("cache_size doit etre strictement positif")
        if not np.isfinite(svd_threshold) or not 0 < svd_threshold < 1:
            raise ValueError("svd_threshold doit etre compris strictement entre 0 et 1")
        self.cache_size = cache_size
        self.svd_threshold = svd_threshold
        self.enable_cache = enable_cache
        self.g = 9.81  # Accélération gravitationnelle [m/s²]

        # Cache pour les matrices de géométrie
        self._matrix_cache: OrderedDict[
            str,
            tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray],
        ] = OrderedDict()
        self._dispersion_cache: dict[float, float] = {}

        # Pré-calcul des matrices pour les fréquences communes
        self._precompute_common_matrices()

    def _precompute_common_matrices(self) -> None:
        """Pré-calcule les matrices pour les fréquences courantes"""
        if not self.enable_cache:
            return

        frequency_min, frequency_max = self.geometry.frequency_range
        common_freqs = np.logspace(
            np.log10(frequency_min),
            np.log10(frequency_max),
            50,
        )

        for freq in common_freqs:
            try:
                self._get_geometry_matrix(freq)
            except Exception:
                # Ignorer les erreurs pour les fréquences problématiques
                continue

    def _solve_dispersion_cached(self, omega: float) -> float:
        """Résolution cachée de la relation de dispersion"""
        cache_key = float(omega)
        if cache_key not in self._dispersion_cache:
            if len(self._dispersion_cache) >= 256:
                oldest_key = next(iter(self._dispersion_cache))
                self._dispersion_cache.pop(oldest_key)
            self._dispersion_cache[cache_key] = self._solve_dispersion_relation(cache_key)
        return self._dispersion_cache[cache_key]

    def _solve_dispersion_relation(self, omega: float) -> float:
        """
        Résout la relation de dispersion: ω² = gk·tanh(kh)

        Args:
            omega: Pulsation [rad/s]

        Returns:
            Nombre d'onde k [rad/m]
        """

        if not np.isfinite(omega) or omega <= 0:
            raise ValueError("La pulsation doit etre strictement positive et finie")

        def dispersion_residual(k: float) -> float:
            return self.g * k * np.tanh(k * self.geometry.water_depth) - omega**2

        deep_water_estimate = omega**2 / self.g
        shallow_water_estimate = omega / np.sqrt(self.g * self.geometry.water_depth)
        upper = max(deep_water_estimate, shallow_water_estimate, 1e-12)
        while dispersion_residual(upper) <= 0:
            upper *= 2.0
            if not np.isfinite(upper):
                raise ValueError("Impossible d'encadrer la racine de dispersion")

        wave_number = float(
            brentq(
                dispersion_residual,
                0.0,
                upper,
                xtol=1e-13,
                rtol=1e-13,
                maxiter=100,
            )
        )
        if wave_number <= 0 or not np.isfinite(wave_number):
            raise ValueError("La relation de dispersion n'a pas produit de racine physique")
        return wave_number

    def _get_matrix_cache_key(self, frequency: float) -> str:
        """Génère une clé de cache pour une fréquence donnée"""
        return f"{self.geometry.geometry_hash}_{frequency:.6f}"

    def _get_geometry_matrix(self, frequency: float) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Construit ou récupère la matrice de géométrie pour une fréquence

        Returns:
            Tuple (A_matrix, U, s, Vt) où A = U @ diag(s) @ Vt
        """
        cache_key = self._get_matrix_cache_key(frequency)

        if self.enable_cache and cache_key in self._matrix_cache:
            # Déplacer l'élément accédé à la fin pour marquer comme récemment utilisé
            self._matrix_cache.move_to_end(cache_key)
            return self._matrix_cache[cache_key]

        omega = 2 * np.pi * frequency
        k = self._solve_dispersion_cached(omega)

        # Construction de la matrice A pour le système Goda
        # A @ [Ai, Ar] = [η1, η2, ..., ηN]
        # où Ai = amplitude incidente, Ar = amplitude réfléchie

        n_probes = self.geometry.n_probes
        A = np.zeros((n_probes, 2), dtype=complex)

        for i, x_pos in enumerate(self.geometry.positions):
            # Onde incidente: Ai * exp(ikx)
            A[i, 0] = np.exp(1j * k * x_pos)
            # Onde réfléchie: Ar * exp(-ikx)
            A[i, 1] = np.exp(-1j * k * x_pos)

        # Décomposition SVD pour stabilité numérique
        U, s, Vt = svd(A, full_matrices=False)

        # Filtrage relatif: le seuil suit l'echelle de la matrice.
        valid_indices = s > float(np.max(s)) * self.svd_threshold
        U_filtered = U[:, valid_indices]
        s_filtered = s[valid_indices]
        Vt_filtered = Vt[valid_indices, :]

        if len(s_filtered) < 2:
            warnings.warn(
                f"Matrice mal conditionnée pour f={frequency:.3f} Hz",
                stacklevel=2,
            )

        result = (A, U_filtered, s_filtered, Vt_filtered)

        # Cache avec limitation de taille (LRU)
        if self.enable_cache:
            if len(self._matrix_cache) >= self.cache_size:
                self._matrix_cache.popitem(last=False)  # Supprimer le plus ancien
            self._matrix_cache[cache_key] = result

        return result

    def _solve_wave_components_svd(
        self, measurements: np.ndarray, U: np.ndarray, s: np.ndarray, Vt: np.ndarray
    ) -> np.ndarray:
        """
        Résout le système linéaire en utilisant la décomposition SVD

        Args:
            measurements: Mesures des sondes [η1, η2, ..., ηN]
            U, s, Vt: Décomposition SVD de la matrice A

        Returns:
            Solution [Ai, Ar] (amplitudes incidente et réfléchie)
        """
        # Pseudo-inverse complexe via SVD: A+ = V @ diag(1/s) @ U^H.
        # ``scipy.linalg.svd`` retourne V^H, pas V^T. Les conjugaisons sont
        # indispensables pour separer correctement les composantes de phase.
        s_inv = 1.0 / s
        A_pinv = Vt.conj().T @ np.diag(s_inv) @ U.conj().T

        # Solution des moindres carrés
        solution = A_pinv @ measurements

        return solution

    def analyze_frequency(self, measurements: np.ndarray, frequency: float) -> WaveComponents:
        """
        Analyse une fréquence spécifique avec la méthode Goda optimisée

        Args:
            measurements: Amplitudes complexes mesurées par les sondes
            frequency: Fréquence d'analyse [Hz]

        Returns:
            Composantes d'onde séparées
        """
        measurements = np.asarray(measurements, dtype=complex)

        frequency_min, frequency_max = self.geometry.frequency_range
        if not np.isfinite(frequency) or not frequency_min <= frequency <= frequency_max:
            raise ValueError(f"Frequence {frequency} Hz hors plage [{frequency_min}, {frequency_max}] Hz")
        if measurements.ndim != 1 or not np.all(np.isfinite(measurements)):
            raise ValueError("Les amplitudes complexes des sondes sont invalides")

        if len(measurements) != self.geometry.n_probes:
            raise ValueError(
                f"Nombre de mesures ({len(measurements)}) != nombre de sondes ({self.geometry.n_probes})"
            )

        # Récupération de la matrice de géométrie
        A, U, s, Vt = self._get_geometry_matrix(frequency)
        if len(s) < 2:
            raise ValueError("Geometrie de sondes singuliere a cette frequence: separation impossible")

        # Résolution du système linéaire
        solution = self._solve_wave_components_svd(measurements, U, s, Vt)
        condition_number = float(np.max(s) / np.min(s))
        residual_norm = float(np.linalg.norm(A @ solution - measurements))
        measurement_norm = float(np.linalg.norm(measurements))
        normalized_residual = residual_norm / measurement_norm if measurement_norm > 0 else 0.0

        # Extraction des composantes
        A_incident = solution[0]
        A_reflected = solution[1]

        # Calcul des paramètres physiques
        incident_amplitude = abs(A_incident)
        reflected_amplitude = abs(A_reflected)

        # Coefficient de réflexion
        if incident_amplitude > 1e-12:
            reflection_coefficient = reflected_amplitude / incident_amplitude
        else:
            reflection_coefficient = np.nan

        # Phases
        phase_incident = np.angle(A_incident)
        phase_reflected = np.angle(A_reflected)

        # Paramètres d'onde
        omega = 2 * np.pi * frequency
        k = self._solve_dispersion_cached(omega)
        wavelength = 2 * np.pi / k if k > 0 else np.inf

        return WaveComponents(
            incident_amplitude=incident_amplitude,
            reflected_amplitude=reflected_amplitude,
            reflection_coefficient=reflection_coefficient,
            phase_incident=phase_incident,
            phase_reflected=phase_reflected,
            frequency=frequency,
            wavelength=wavelength,
            wave_number=k,
            condition_number=condition_number,
            normalized_residual=normalized_residual,
        )

    def analyze_spectrum(self, frequency_spectrum: dict[float, np.ndarray]) -> dict[float, WaveComponents]:
        """
        Analyse un spectre complet de fréquences

        Args:
            frequency_spectrum: {frequency: measurements_array}

        Returns:
            Dictionnaire des résultats par fréquence
        """
        results = {}

        for freq, measurements in frequency_spectrum.items():
            try:
                results[freq] = self.analyze_frequency(measurements, freq)
            except Exception as e:
                warnings.warn(
                    f"Erreur analyse fréquence {freq:.3f} Hz: {e}",
                    stacklevel=2,
                )
                continue

        return results

    def get_cache_stats(self) -> dict[str, int]:
        """Retourne les statistiques du cache"""
        return {
            "matrix_cache_size": len(self._matrix_cache),
            "max_cache_size": self.cache_size,
            "dispersion_cache_size": len(self._dispersion_cache),
            "geometry_hash": self.geometry.geometry_hash,
        }

    def clear_cache(self) -> None:
        """Vide tous les caches"""
        self._matrix_cache.clear()
        self._dispersion_cache.clear()


# Fonction utilitaire pour migration depuis l'ancien code
def create_analyzer_from_positions(
    positions: list[float],
    water_depth: float,
    freq_range: tuple[float, float] = (0.05, 2.0),
) -> OptimizedGodaAnalyzer:
    """Crée un analyseur à partir de positions de sondes simples"""
    geometry = ProbeGeometry(
        positions=np.array(positions),
        water_depth=water_depth,
        frequency_range=freq_range,
    )
    return OptimizedGodaAnalyzer(geometry)


# Exemple d'utilisation
if __name__ == "__main__":
    import time

    # Configuration test
    probe_positions = [0.5, 0.8, 1.1, 1.4, 1.7, 2.0, 2.3, 2.6]  # 8 sondes
    water_depth = 0.5  # 50 cm

    geometry = ProbeGeometry(positions=probe_positions, water_depth=water_depth, frequency_range=(0.1, 1.5))

    analyzer = OptimizedGodaAnalyzer(geometry)

    # Test de performance
    test_frequency = 0.5  # Hz
    n_tests = 1000

    # Génération de données test
    np.random.seed(42)
    test_measurements = np.random.randn(len(probe_positions)) + 1j * np.random.randn(len(probe_positions))

    # Benchmark
    start_time = time.time()
    for _ in range(n_tests):
        result = analyzer.analyze_frequency(test_measurements, test_frequency)
    end_time = time.time()

    print(f"Temps pour {n_tests} analyses: {end_time - start_time:.4f}s")
    print(f"Temps par analyse: {(end_time - start_time) / n_tests * 1000:.2f}ms")
    print("\nRésultat exemple:")
    print(f"  Amplitude incidente: {result.incident_amplitude:.4f}")
    print(f"  Amplitude réfléchie: {result.reflected_amplitude:.4f}")
    print(f"  Coefficient réflexion: {result.reflection_coefficient:.4f}")
    print(f"  Longueur d'onde: {result.wavelength:.3f}m")

    print(f"\nStatistiques cache: {analyzer.get_cache_stats()}")
