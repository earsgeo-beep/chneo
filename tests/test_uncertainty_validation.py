"""
Tests de Validation - Module Incertitudes GUM

Tests scientifiques pour valider l'implémentation du calcul d'incertitudes
selon JCGM 100:2008 (GUM).

Références:
    - JCGM 100:2008 - Guide to the expression of uncertainty in measurement
    - JCGM 101:2008 - Propagation of distributions using Monte Carlo

Auteur: CHNeoWave Development Team
Phase: 3 - Incertitudes GUM
"""

import pytest
import numpy as np
import sys
import os
from typing import Tuple

# Import direct
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/hrneowave/core')))

import uncertainty_calculator
from uncertainty_calculator import (
    UncertaintyCalculator,
    UncertaintyBudget,
    UncertaintyComponent,
    UncertaintyType,
    Distribution,
    create_standard_H_budget
)


# ============================================================================
# TEST 3.1: INCERTITUDE TYPE B - DISTRIBUTION RECTANGULAIRE
# ============================================================================

def test_gum_type_b_rectangular():
    """
    TEST 3.1: Incertitude Type B - Distribution rectangulaire
    
    Pour une grandeur uniformément distribuée dans [a-b, a+b]:
        u = b / √3
    
    Critère de succès: u correct à 1e-10
    """
    calc = UncertaintyCalculator()
    budget = calc.create_budget("Test_Rect")
    
    # Demi-largeur = 0.001 m
    half_width = 0.001
    
    calc.add_type_b_component(
        budget, "Test rectangulaire",
        half_width, Distribution.RECTANGULAR
    )
    
    # u théorique
    u_theoretical = half_width / np.sqrt(3)
    u_calculated = budget.combined_uncertainty
    
    error = abs(u_calculated - u_theoretical)
    
    assert error < 1e-10, \
        f"u = {u_calculated:.10f} != théorique {u_theoretical:.10f} (erreur {error:.2e})"
    
    print(f"✓ TEST 3.1 PASS: u_rect = {u_calculated:.10f} (théorique {u_theoretical:.10f})")


# ============================================================================
# TEST 3.2: INCERTITUDE TYPE A - ÉCART-TYPE DE LA MOYENNE
# ============================================================================

def test_gum_type_a_standard_deviation():
    """
    TEST 3.2: Incertitude Type A - Écart-type de la moyenne
    
    Pour n mesures répétées:
        u = s / √n
        où s = écart-type expérimental
    
    Critère de succès: u correct à 1e-10
    """
    calc = UncertaintyCalculator()
    budget = calc.create_budget("Test_TypeA")
    
    # Mesures répétées (10 valeurs)
    measurements = np.array([1.0, 1.1, 0.9, 1.05, 0.95, 1.02, 0.98, 1.03, 0.97, 1.0])
    
    # Calcul manuel
    n = len(measurements)
    s = np.std(measurements, ddof=1)  # n-1
    u_theoretical = s / np.sqrt(n)
    
    # Calcul via module
    calc.add_type_a_component(budget, "Répétabilité", measurements)
    u_calculated = budget.combined_uncertainty
    
    error = abs(u_calculated - u_theoretical)
    
    assert error < 1e-10, \
        f"u = {u_calculated:.10f} != théorique {u_theoretical:.10f}"
    
    print(f"✓ TEST 3.2 PASS: u_typeA = {u_calculated:.6f} (s={s:.6f}, n={n})")


# ============================================================================
# TEST 3.3: INCERTITUDE COMBINÉE - LOI DE PROPAGATION
# ============================================================================

def test_gum_combined_uncertainty():
    """
    TEST 3.3: Incertitude combinée - Loi de propagation
    
    Avec plusieurs composantes indépendantes:
        uc(y) = √[u₁² + u₂² + ... + uₙ²]
    
    Critère de succès: uc correct à 1e-10
    """
    calc = UncertaintyCalculator()
    budget = calc.create_budget("Test_Combined")
    
    # Trois composantes
    u1 = 0.0003
    u2 = 0.0002
    u3 = 0.0001
    
    budget.add_component(UncertaintyComponent(
        name="Composante 1", type=UncertaintyType.TYPE_B, value=u1
    ))
    budget.add_component(UncertaintyComponent(
        name="Composante 2", type=UncertaintyType.TYPE_B, value=u2
    ))
    budget.add_component(UncertaintyComponent(
        name="Composante 3", type=UncertaintyType.TYPE_B, value=u3
    ))
    
    # Calcul théorique
    uc_theoretical = np.sqrt(u1**2 + u2**2 + u3**2)
    uc_calculated = budget.combined_uncertainty
    
    error = abs(uc_calculated - uc_theoretical)
    
    assert error < 1e-10, \
        f"uc = {uc_calculated:.10f} != théorique {uc_theoretical:.10f}"
    
    print(f"✓ TEST 3.3 PASS: uc = {uc_calculated:.10f} = √({u1**2:.2e} + {u2**2:.2e} + {u3**2:.2e})")


# ============================================================================
# TEST 3.4: COEFFICIENTS DE SENSIBILITÉ
# ============================================================================

def test_gum_sensitivity_coefficients():
    """
    TEST 3.4: Coefficients de sensibilité
    
    Pour y = f(x), avec c = ∂f/∂x:
        u(y) = |c| × u(x)
    
    Exemple: y = 2x, donc c = 2
    
    Critère de succès: u(y) = 2 × u(x)
    """
    calc = UncertaintyCalculator()
    budget = calc.create_budget("Test_Sensitivity")
    
    # u(x) = 0.001
    u_x = 0.001
    # c = ∂y/∂x = 2
    c = 2.0
    
    budget.add_component(UncertaintyComponent(
        name="Variable x",
        type=UncertaintyType.TYPE_B,
        value=u_x,
        sensitivity_coefficient=c
    ))
    
    # u(y) théorique
    u_y_theoretical = abs(c) * u_x
    u_y_calculated = budget.combined_uncertainty
    
    error = abs(u_y_calculated - u_y_theoretical)
    
    assert error < 1e-10, \
        f"u(y) = {u_y_calculated:.10f} != théorique {u_y_theoretical:.10f}"
    
    print(f"✓ TEST 3.4 PASS: u(y) = {u_y_calculated:.10f} = {c} × {u_x:.10f}")


# ============================================================================
# TEST 3.5: INCERTITUDE ÉLARGIE (FACTEUR k)
# ============================================================================

def test_gum_expanded_uncertainty():
    """
    TEST 3.5: Incertitude élargie
    
    U = k × uc
    où k = 2 pour ~95% de confiance (loi normale)
    
    Critère de succès: U = k × uc à 1e-10
    """
    calc = UncertaintyCalculator()
    budget = calc.create_budget("Test_Expanded", coverage_factor=2.0)
    
    # Composante unique
    uc = 0.0005
    budget.add_component(UncertaintyComponent(
        name="Composante", type=UncertaintyType.TYPE_B, value=uc
    ))
    
    # U théorique
    k = 2.0
    U_theoretical = k * uc
    U_calculated = budget.expanded_uncertainty
    
    error = abs(U_calculated - U_theoretical)
    
    assert error < 1e-10, \
        f"U = {U_calculated:.10f} != théorique {U_theoretical:.10f}"
    
    print(f"✓ TEST 3.5 PASS: U = {U_calculated:.10f} = k({k}) × uc({uc:.10f})")


# ============================================================================
# TEST 3.6: DEGRÉS DE LIBERTÉ EFFECTIFS (WELCH-SATTERTHWAITE)
# ============================================================================

def test_gum_welch_satterthwaite():
    """
    TEST 3.6: Degrés de liberté effectifs (Welch-Satterthwaite)
    
    Pour composantes Type B uniquement: νeff = ∞
    Pour mix Type A/B: formule de Welch-Satterthwaite
    
    Critère de succès: νeff correct
    """
    calc = UncertaintyCalculator()
    
    # Cas 1: Type B uniquement → νeff = ∞
    budget1 = calc.create_budget("Test_DOF_B")
    calc.add_type_b_component(budget1, "B1", 0.001, Distribution.RECTANGULAR)
    calc.add_type_b_component(budget1, "B2", 0.002, Distribution.RECTANGULAR)
    
    assert budget1.effective_degrees_of_freedom == np.inf, \
        "Type B uniquement devrait donner νeff = ∞"
    
    # Cas 2: Type A avec n=10 mesures → νeff ≈ 9
    budget2 = calc.create_budget("Test_DOF_A")
    measurements = np.random.normal(1.0, 0.01, 10)
    calc.add_type_a_component(budget2, "A1", measurements)
    
    # νeff devrait être proche de 9 (n-1)
    assert abs(budget2.effective_degrees_of_freedom - 9.0) < 0.1, \
        f"Type A (n=10) devrait donner νeff ≈ 9, obtenu {budget2.effective_degrees_of_freedom}"
    
    print(f"✓ TEST 3.6 PASS: νeff = ∞ (Type B), νeff ≈ 9 (Type A n=10)")


# ============================================================================
# TEST 3.7: CONTRIBUTIONS RELATIVES
# ============================================================================

def test_gum_component_contributions():
    """
    TEST 3.7: Contributions relatives des composantes
    
    Vérifie que la somme des contributions = 100%
    
    Critère de succès: Σ contributions = 100%
    """
    calc = UncertaintyCalculator()
    budget = calc.create_budget("Test_Contributions")
    
    # Plusieurs composantes
    budget.add_component(UncertaintyComponent(
        name="C1", type=UncertaintyType.TYPE_B, value=0.003
    ))
    budget.add_component(UncertaintyComponent(
        name="C2", type=UncertaintyType.TYPE_B, value=0.002
    ))
    budget.add_component(UncertaintyComponent(
        name="C3", type=UncertaintyType.TYPE_B, value=0.001
    ))
    
    contributions = budget.get_component_contributions()
    total_percent = sum(contributions.values())
    
    assert abs(total_percent - 100.0) < 1e-6, \
        f"Somme contributions = {total_percent:.6f}% != 100%"
    
    print(f"✓ TEST 3.7 PASS: Σ contributions = {total_percent:.6f}%")
    for name, percent in contributions.items():
        print(f"    {name}: {percent:.2f}%")


# ============================================================================
# TEST 3.8: BUDGET STANDARD HAUTEUR H
# ============================================================================

def test_gum_standard_h_budget():
    """
    TEST 3.8: Budget standard pour hauteur de vague H
    
    Vérifie que create_standard_H_budget() fonctionne correctement
    
    Critère de succès: Budget créé avec 4 composantes, uc > 0
    """
    budget = create_standard_H_budget()
    
    # Vérifier nombre de composantes
    assert len(budget.components) == 4, \
        f"Budget standard devrait avoir 4 composantes, obtenu {len(budget.components)}"
    
    # Vérifier que uc > 0
    assert budget.combined_uncertainty > 0, \
        "Incertitude combinée devrait être > 0"
    
    # Vérifier que U > uc
    assert budget.expanded_uncertainty > budget.combined_uncertainty, \
        "Incertitude élargie devrait être > incertitude combinée"
    
    print(f"✓ TEST 3.8 PASS: Budget H créé avec uc = {budget.combined_uncertainty:.6f} m, U = {budget.expanded_uncertainty:.6f} m")


# ============================================================================
# TEST 3.9: PROPAGATION D'INCERTITUDES
# ============================================================================

def test_gum_uncertainty_propagation():
    """
    TEST 3.9: Propagation d'incertitudes à travers une fonction
    
    Exemple: Hs = 4 × √m0
    où m0 a une incertitude u(m0)
    
    c = ∂Hs/∂m0 = 2 / √m0
    u(Hs) = |c| × u(m0)
    
    Critère de succès: u(Hs) correct à 1%
    """
    calc = UncertaintyCalculator()
    
    # Budget pour m0
    budget_m0 = calc.create_budget("m0")
    m0_value = 0.001  # m²
    u_m0 = 0.00005  # m²
    
    budget_m0.add_component(UncertaintyComponent(
        name="m0_uncertainty", type=UncertaintyType.TYPE_B, value=u_m0
    ))
    
    # Coefficient de sensibilité pour Hs = 4√m0
    # c = ∂(4√m0)/∂m0 = 2/√m0
    c_m0 = 2.0 / np.sqrt(m0_value)
    
    # Propagation
    u_Hs_calculated = calc.compute_propagated_uncertainty(
        {"m0": budget_m0},
        {"m0": c_m0}
    )
    
    # U théorique
    u_Hs_theoretical = abs(c_m0) * u_m0
    
    error_percent = abs(u_Hs_calculated - u_Hs_theoretical) / u_Hs_theoretical * 100
    
    assert error_percent < 1.0, \
        f"u(Hs) = {u_Hs_calculated:.8f} != théorique {u_Hs_theoretical:.8f} (erreur {error_percent:.2f}%)"
    
    print(f"✓ TEST 3.9 PASS: u(Hs) = {u_Hs_calculated:.8f} (propagé depuis u(m0)={u_m0:.8f})")


# ============================================================================
# TEST 3.10: FORMAT RÉSULTAT
# ============================================================================

def test_gum_result_formatting():
    """
    TEST 3.10: Formatage de résultat avec incertitude
    
    Vérifie que le format suit les conventions GUM
    
    Critère de succès: Chaîne correctement formatée
    """
    calc = UncertaintyCalculator()
    budget = calc.create_budget("Hs", coverage_factor=2.0)
    
    budget.add_component(UncertaintyComponent(
        name="Test", type=UncertaintyType.TYPE_B, value=0.004
    ))
    
    Hs_value = 0.125  # 12.5 cm
    result = calc.format_result("Hs", Hs_value, budget, "m")
    
    # Vérifier contenu
    assert "Hs" in result, "Résultat devrait contenir le nom de la grandeur"
    assert str(Hs_value) in result, "Résultat devrait contenir la valeur"
    assert "±" in result, "Résultat devrait contenir ±"
    assert "m" in result, "Résultat devrait contenir l'unité"
    assert "95%" in result or "k=2" in result, "Résultat devrait indiquer le niveau de confiance"
    
    print(f"✓ TEST 3.10 PASS: Format = {result}")


# ============================================================================
# FIXTURE RAPPORT DE TEST
# ============================================================================

@pytest.fixture(scope="session", autouse=True)
def generate_test_report(request):
    """Génère un rapport de test."""
    yield
    
    print("\n" + "="*80)
    print("RAPPORT DE TEST - PHASE 3: VALIDATION MODULE INCERTITUDES GUM")
    print("="*80)
    print(f"Module: tests/test_uncertainty_validation.py")
    print(f"Date: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    print("\n✅ MODULE INCERTITUDES GUM VALIDÉ si tous les tests sont PASS")
    print("="*80)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "-s"])
