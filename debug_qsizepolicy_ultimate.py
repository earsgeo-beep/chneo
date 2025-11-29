#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test ultime pour résoudre le problème QSizePolicy avec PySide6
"""

import sys
from PySide6.QtWidgets import QApplication, QWidget, QSizePolicy
from PySide6.QtCore import Qt

def test_qsizepolicy_methods():
    """Test toutes les méthodes possibles pour QSizePolicy"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    widget = QWidget()
    
    print("=== Tests QSizePolicy avec PySide6 ===")
    print(f"Version PySide6: {getattr(sys.modules['PySide6'], '__version__', 'inconnue')}")
    print(f"Type QSizePolicy: {type(QSizePolicy)}")
    print(f"Type QSizePolicy.Expanding: {type(QSizePolicy.Expanding)}")
    
    # Test 1: Méthode directe avec constantes
    try:
        widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        print("✅ Test 1 RÉUSSI: setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)")
    except Exception as e:
        print(f"❌ Test 1 ÉCHOUÉ: {e}")
    
    # Test 2: Création objet QSizePolicy vide puis setters
    try:
        policy = QSizePolicy()
        policy.setHorizontalPolicy(QSizePolicy.Expanding)
        policy.setVerticalPolicy(QSizePolicy.Preferred)
        widget.setSizePolicy(policy)
        print("✅ Test 2 RÉUSSI: QSizePolicy() + setters + setSizePolicy(policy)")
    except Exception as e:
        print(f"❌ Test 2 ÉCHOUÉ: {e}")
    
    # Test 3: Création objet QSizePolicy avec constructeur
    try:
        policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        widget.setSizePolicy(policy)
        print("✅ Test 3 RÉUSSI: QSizePolicy(Expanding, Preferred) + setSizePolicy(policy)")
    except Exception as e:
        print(f"❌ Test 3 ÉCHOUÉ: {e}")
    
    # Test 4: Avec Policy explicite
    try:
        widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        print("✅ Test 4 RÉUSSI: setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)")
    except Exception as e:
        print(f"❌ Test 4 ÉCHOUÉ: {e}")
    
    # Test 5: Avec valeurs entières
    try:
        widget.setSizePolicy(7, 5)  # Expanding=7, Preferred=5
        print("✅ Test 5 RÉUSSI: setSizePolicy(7, 5)")
    except Exception as e:
        print(f"❌ Test 5 ÉCHOUÉ: {e}")
    
    # Test 6: Récupération de la politique actuelle
    try:
        current_policy = widget.sizePolicy()
        print(f"✅ Test 6 RÉUSSI: sizePolicy() retourne {type(current_policy)}")
        print(f"   Horizontal: {current_policy.horizontalPolicy()}")
        print(f"   Vertical: {current_policy.verticalPolicy()}")
    except Exception as e:
        print(f"❌ Test 6 ÉCHOUÉ: {e}")
    
    # Test 7: Méthode alternative avec sizePolicy().setXXX()
    try:
        widget.sizePolicy().setHorizontalPolicy(QSizePolicy.Expanding)
        widget.sizePolicy().setVerticalPolicy(QSizePolicy.Preferred)
        print("✅ Test 7 RÉUSSI: widget.sizePolicy().setXXXPolicy()")
    except Exception as e:
        print(f"❌ Test 7 ÉCHOUÉ: {e}")
    
    print("\n=== Fin des tests ===")
    
    app.quit()

if __name__ == "__main__":
    test_qsizepolicy_methods()