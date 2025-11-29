"""
Module de Calcul d'Incertitudes selon GUM (Guide to the expression of uncertainty)

Ce module implémente le calcul d'incertitudes de mesure selon la méthode GUM
(JCGM 100:2008) pour les grandeurs maritimes mesurées par CHNeoWave.

Références scientifiques:
    - JCGM 100:2008 - "Evaluation of measurement data - Guide to the expression 
      of uncertainty in measurement (GUM)"
    - JCGM 101:2008 - "Propagation of distributions using a Monte Carlo method"
    - ISO/IEC Guide 98-3:2008

Auteur: CHNeoWave Development Team
Phase: 3 - Incertitudes GUM
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
import warnings


# ============================================================================
# ÉNUMÉRATIONS ET CONSTANTES
# ============================================================================

class UncertaintyType(Enum):
    """Type d'incertitude selon GUM."""
    TYPE_A = "A"  # Évaluation statistique (répétabilité)
    TYPE_B = "B"  # Évaluation par d'autres moyens (spécifications, certificats)


class Distribution(Enum):
    """Distributions de probabilité pour incertitudes Type B."""
    NORMAL = "normal"        # Distribution normale (gaussienne)
    RECTANGULAR = "rectangular"  # Distribution rectangulaire (uniforme)
    TRIANGULAR = "triangular"    # Distribution triangulaire
    U_SHAPED = "u_shaped"        # Distribution en U


# Facteurs de diviseur pour distributions Type B
DISTRIBUTION_DIVISORS = {
    Distribution.NORMAL: 1.0,      # u = σ (déjà écart-type)
    Distribution.RECTANGULAR: np.sqrt(3),  # u = a/√3
    Distribution.TRIANGULAR: np.sqrt(6),   # u = a/√6
    Distribution.U_SHAPED: np.sqrt(2),     # u = a/√2
}


# ============================================================================
# STRUCTURES DE DONNÉES
# ============================================================================

@dataclass
class UncertaintyComponent:
    """
    Composante individuelle d'incertitude.
    
    Attributes:
        name: Nom de la source d'incertitude
        type: Type A ou B
        value: Valeur de l'incertitude (écart-type)
        distribution: Distribution (pour Type B)
        degrees_of_freedom: Degrés de liberté (pour Type A)
        sensitivity_coefficient: Coefficient de sensibilité cᵢ = ∂y/∂xᵢ
    """
    name: str
    type: UncertaintyType
    value: float
    distribution: Distribution = Distribution.NORMAL
    degrees_of_freedom: Optional[float] = None
    sensitivity_coefficient: float = 1.0
    
    @property
    def contribution(self) -> float:
        """Contribution à l'incertitude combinée: uᵢ(y) = |cᵢ| × u(xᵢ)."""
        return abs(self.sensitivity_coefficient) * self.value
    
    @property
    def variance_contribution(self) -> float:
        """Contribution à la variance: [cᵢ × u(xᵢ)]²."""
        return self.contribution ** 2


@dataclass
class UncertaintyBudget:
    """
    Budget d'incertitude complet pour une grandeur.
    
    Attributes:
        measurand: Nom de la grandeur mesurée (ex: "H", "Hs", "Kr")
        components: Liste des composantes d'incertitude
        combined_uncertainty: Incertitude combinée uc (calculée)
        coverage_factor: Facteur d'élargissement k (défaut: 2 pour 95%)
        expanded_uncertainty: Incertitude élargie U = k × uc
        effective_degrees_of_freedom: Degrés de liberté effectifs (Welch-Satterthwaite)
    """
    measurand: str
    components: List[UncertaintyComponent] = field(default_factory=list)
    coverage_factor: float = 2.0
    
    def __post_init__(self):
        """Calcule automatiquement les incertitudes combinée et élargie."""
        self._update_calculations()
    
    def _update_calculations(self):
        """Recalcule les incertitudes après ajout de composantes."""
        # Incertitude combinée
        self.combined_uncertainty = self._compute_combined_uncertainty()
        
        # Degrés de liberté effectifs (formule de Welch-Satterthwaite)
        self.effective_degrees_of_freedom = self._compute_effective_dof()
        
        # Incertitude élargie
        self.expanded_uncertainty = self.coverage_factor * self.combined_uncertainty
    
    def _compute_combined_uncertainty(self) -> float:
        """
        Calcule l'incertitude combinée.
        
        Formule GUM: uc(y) = √(Σ[cᵢ × u(xᵢ)]²)
        
        Returns:
            Incertitude combinée (écart-type)
        """
        if not self.components:
            return 0.0
        
        # Somme des variances
        variance_sum = sum(comp.variance_contribution for comp in self.components)
        
        return np.sqrt(variance_sum)
    
    def _compute_effective_dof(self) -> float:
        """
        Calcule les degrés de liberté effectifs (Welch-Satterthwaite).
        
        Formule: νeff = uc⁴ / Σ[uᵢ⁴ / νᵢ]
        
        Returns:
            Degrés de liberté effectifs
        """
        if not self.components or self.combined_uncertainty == 0:
            return np.inf
        
        uc4 = self.combined_uncertainty ** 4
        
        denominator = 0.0
        for comp in self.components:
            if comp.degrees_of_freedom is not None and comp.degrees_of_freedom > 0:
                ui4 = comp.variance_contribution ** 2  # (cᵢuᵢ)⁴
                denominator += ui4 / comp.degrees_of_freedom
        
        if denominator == 0:
            return np.inf  # Incertitudes Type B uniquement (νᵢ = ∞)
        
        return uc4 / denominator
    
    def add_component(self, component: UncertaintyComponent):
        """
        Ajoute une composante au budget.
        
        Args:
            component: Composante d'incertitude à ajouter
        """
        self.components.append(component)
        self._update_calculations()
    
    def get_component_contributions(self) -> Dict[str, float]:
        """
        Retourne les contributions de chaque composante en %.
        
        Returns:
            Dictionnaire {nom_composante: contribution_%}
        """
        if self.combined_uncertainty == 0:
            return {comp.name: 0.0 for comp in self.components}
        
        total_variance = self.combined_uncertainty ** 2
        
        contributions = {}
        for comp in self.components:
            percent = (comp.variance_contribution / total_variance) * 100
            contributions[comp.name] = percent
        
        return contributions
    
    def generate_summary(self) -> str:
        """
        Génère un résumé textuel du budget d'incertitude.
        
        Returns:
            Résumé formaté en texte
        """
        lines = []
        lines.append("="*80)
        lines.append(f"BUDGET D'INCERTITUDE - {self.measurand}")
        lines.append("="*80)
        lines.append("")
        
        # Tableau des composantes
        lines.append(f"{'Source':<30} {'Type':<6} {'u(xi)':<12} {'ci':<10} {'ui(y)':<12} {'%':<8}")
        lines.append("-"*80)
        
        contributions = self.get_component_contributions()
        
        for comp in self.components:
            type_str = comp.type.value
            u_xi = f"{comp.value:.6f}"
            ci = f"{comp.sensitivity_coefficient:.4f}"
            ui_y = f"{comp.contribution:.6f}"
            contrib_pct = f"{contributions[comp.name]:.2f}%"
            
            lines.append(f"{comp.name:<30} {type_str:<6} {u_xi:<12} {ci:<10} {ui_y:<12} {contrib_pct:<8}")
        
        lines.append("-"*80)
        lines.append("")
        
        # Résultats
        lines.append(f"Incertitude combinée (uc):     {self.combined_uncertainty:.6f}")
        lines.append(f"Facteur d'élargissement (k):    {self.coverage_factor:.2f}")
        lines.append(f"Incertitude élargie (U):        {self.expanded_uncertainty:.6f}")
        lines.append(f"Degrés de liberté effectifs:    {self.effective_degrees_of_freedom:.1f}")
        
        confidence_level = "95%" if self.coverage_factor == 2.0 else f"k={self.coverage_factor}"
        lines.append("")
        lines.append(f"Résultat: {self.measurand} ± {self.expanded_uncertainty:.6f} ({confidence_level})")
        lines.append("="*80)
        
        return "\n".join(lines)


# ============================================================================
# CALCULATEUR D'INCERTITUDES
# ============================================================================

class UncertaintyCalculator:
    """
    Calculateur d'incertitudes selon GUM (JCGM 100:2008).
    
    Gère les budgets d'incertitude pour différentes grandeurs maritimes
    et effectue la propagation des incertitudes.
    
    Example:
        >>> calc = UncertaintyCalculator()
        >>> 
        >>> # Budget pour hauteur de vague H
        >>> budget_H = calc.create_budget("H")
        >>> 
        >>> # Ajout incertitudes Type B
        >>> budget_H.add_component(UncertaintyComponent(
        >>>     name="Calibration sonde",
        >>>     type=UncertaintyType.TYPE_B,
        >>>     value=0.0003,  # 0.3 mm
        >>>     distribution=Distribution.NORMAL
        >>> ))
        >>> 
        >>> # Ajout incertitudes Type A
        >>> budget_H.add_component(UncertaintyComponent(
        >>>     name="Répétabilité",
        >>>     type=UncertaintyType.TYPE_A,
        >>>     value=0.0001,  # 0.1 mm
        >>>     degrees_of_freedom=9  # n-1 pour 10 mesures
        >>> ))
        >>> 
        >>> print(budget_H.generate_summary())
    """
    
    def __init__(self):
        """Initialise le calculateur d'incertitudes."""
        self.budgets: Dict[str, UncertaintyBudget] = {}
    
    def create_budget(self, measurand: str, coverage_factor: float = 2.0) -> UncertaintyBudget:
        """
        Crée un nouveau budget d'incertitude.
        
        Args:
            measurand: Nom de la grandeur (ex: "H", "Hs", "Tp", "Kr")
            coverage_factor: Facteur k (2 pour 95%, 3 pour 99.7%)
        
        Returns:
            Budget d'incertitude vide
        """
        budget = UncertaintyBudget(measurand=measurand, coverage_factor=coverage_factor)
        self.budgets[measurand] = budget
        return budget
    
    def add_type_b_component(self, 
                            budget: UncertaintyBudget,
                            name: str,
                            half_width: float,
                            distribution: Distribution = Distribution.RECTANGULAR,
                            sensitivity_coefficient: float = 1.0):
        """
        Ajoute une composante d'incertitude Type B.
        
        Args:
            budget: Budget d'incertitude cible
            name: Nom de la source
            half_width: Demi-largeur a (pour rectangulaire) ou écart-type
            distribution: Type de distribution
            sensitivity_coefficient: Coefficient de sensibilité cᵢ
        """
        # Calculer incertitude-type selon la distribution
        divisor = DISTRIBUTION_DIVISORS[distribution]
        u_value = half_width / divisor
        
        component = UncertaintyComponent(
            name=name,
            type=UncertaintyType.TYPE_B,
            value=u_value,
            distribution=distribution,
            degrees_of_freedom=None,  # Type B → νᵢ = ∞
            sensitivity_coefficient=sensitivity_coefficient
        )
        
        budget.add_component(component)
    
    def add_type_a_component(self,
                            budget: UncertaintyBudget,
                            name: str,
                            measurements: np.ndarray,
                            sensitivity_coefficient: float = 1.0):
        """
        Ajoute une composante d'incertitude Type A (statistique).
        
        Args:
            budget: Budget d'incertitude cible
            name: Nom de la source
            measurements: Array de mesures répétées
            sensitivity_coefficient: Coefficient de sensibilité cᵢ
        """
        if len(measurements) < 2:
            warnings.warn(f"Type A '{name}': Moins de 2 mesures, incertitude = 0")
            return
        
        # Moyenne et écart-type expérimental
        mean = np.mean(measurements)
        std_dev = np.std(measurements, ddof=1)  # n-1
        
        # Incertitude-type de la moyenne: u = s/√n
        n = len(measurements)
        u_value = std_dev / np.sqrt(n)
        
        # Degrés de liberté
        degrees_of_freedom = n - 1
        
        component = UncertaintyComponent(
            name=name,
            type=UncertaintyType.TYPE_A,
            value=u_value,
            distribution=Distribution.NORMAL,
            degrees_of_freedom=degrees_of_freedom,
            sensitivity_coefficient=sensitivity_coefficient
        )
        
        budget.add_component(component)
    
    def compute_propagated_uncertainty(self,
                                      input_budgets: Dict[str, UncertaintyBudget],
                                      sensitivity_coefficients: Dict[str, float]) -> float:
        """
        Propage les incertitudes à travers une fonction.
        
        Pour y = f(x₁, x₂, ...), avec coefficients de sensibilité cᵢ = ∂f/∂xᵢ
        
        Args:
            input_budgets: Dictionnaire {variable: budget}
            sensitivity_coefficients: Dictionnaire {variable: cᵢ}
        
        Returns:
            Incertitude combinée propagée
        """
        variance_sum = 0.0
        
        for var_name, budget in input_budgets.items():
            ci = sensitivity_coefficients.get(var_name, 1.0)
            ui = budget.combined_uncertainty
            variance_sum += (ci * ui) ** 2
        
        return np.sqrt(variance_sum)
    
    def format_result(self, measurand: str, value: float, 
                     budget: UncertaintyBudget, unit: str = "") -> str:
        """
        Formate un résultat avec son incertitude.
        
        Args:
            measurand: Nom de la grandeur
            value: Valeur mesurée
            budget: Budget d'incertitude
            unit: Unité (ex: "m", "s", "")
        
        Returns:
            Chaîne formatée (ex: "Hs = 0.125 ± 0.004 m (k=2, 95%)")
        """
        confidence = "95%" if budget.coverage_factor == 2.0 else f"k={budget.coverage_factor}"
        
        if unit:
            unit = f" {unit}"
        
        return (f"{measurand} = {value:.6f} ± {budget.expanded_uncertainty:.6f}{unit} "
                f"(k={budget.coverage_factor}, {confidence})")


# ============================================================================
# FONCTIONS UTILITAIRES
# ============================================================================

def create_standard_H_budget(calibration_uncertainty: float = 0.0003,
                            daq_resolution: float = 0.00015,
                            noise: float = 0.0001,
                            drift: float = 0.0002) -> UncertaintyBudget:
    """
    Crée un budget d'incertitude standard pour la hauteur de vague H.
    
    Args:
        calibration_uncertainty: Incertitude de calibration (m)
        daq_resolution: Résolution DAQ (m)
        noise: Bruit électronique (m)
        drift: Dérive du zéro (m)
    
    Returns:
        Budget d'incertitude pour H
    """
    calc = UncertaintyCalculator()
    budget = calc.create_budget("H", coverage_factor=2.0)
    
    # Type B - Calibration (normale)
    budget.add_component(UncertaintyComponent(
        name="Calibration sonde",
        type=UncertaintyType.TYPE_B,
        value=calibration_uncertainty,
        distribution=Distribution.NORMAL
    ))
    
    # Type B - Résolution DAQ (rectangulaire)
    calc.add_type_b_component(
        budget, "Résolution DAQ 16-bit", 
        daq_resolution, Distribution.RECTANGULAR
    )
    
    # Type B - Bruit (normal)
    budget.add_component(UncertaintyComponent(
        name="Bruit électronique",
        type=UncertaintyType.TYPE_B,
        value=noise,
        distribution=Distribution.NORMAL
    ))
    
    # Type B - Dérive (rectangulaire)
    calc.add_type_b_component(
        budget, "Dérive zéro",
        drift, Distribution.RECTANGULAR
    )
    
    return budget


if __name__ == "__main__":
    # Exemple d'utilisation
    print("="*80)
    print("MODULE INCERTITUDES GUM - EXEMPLE D'UTILISATION")
    print("="*80)
    print()
    
    # Créer calculateur
    calc = UncertaintyCalculator()
    
    # Budget pour hauteur de vague H
    print("Exemple 1: Budget d'incertitude pour hauteur de vague H")
    print("-"*80)
    
    budget_H = create_standard_H_budget()
    print(budget_H.generate_summary())
    print()
    
    # Formatage résultat
    H_measured = 0.125  # 12.5 cm
    result = calc.format_result("H", H_measured, budget_H, "m")
    print(f"Résultat formaté: {result}")
    print()
    
    # Exemple 2: Budget avec Type A
    print("="*80)
    print("Exemple 2: Budget avec incertitude Type A (répétabilité)")
    print("-"*80)
    
    budget_H2 = calc.create_budget("H_avec_repetitions", coverage_factor=2.0)
    
    # Type B (calibration)
    calc.add_type_b_component(
        budget_H2, "Calibration",
        0.0003, Distribution.NORMAL
    )
    
    # Type A (mesures répétées)
    measurements = np.array([0.1250, 0.1248, 0.1252, 0.1249, 0.1251,
                            0.1250, 0.1249, 0.1251, 0.1250, 0.1248])  # 10 mesures
    
    calc.add_type_a_component(budget_H2, "Répétabilité", measurements)
    
    print(budget_H2.generate_summary())
    print()
    
    print("="*80)
    print("Structure du module créée avec succès ✓")
    print("="*80)
