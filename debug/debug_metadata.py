#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de diagnostic pour le gestionnaire de métadonnées
"""

import sys
import os
from pathlib import Path
import traceback

# Ajouter le chemin source
sys.path.insert(0, str(Path(__file__).parent / "src"))

print("🔍 Diagnostic du gestionnaire de métadonnées")
print("=" * 50)

# Test d'import étape par étape
print("\n1. Test d'import des modules de base...")
try:
    import json
    import uuid
    from datetime import datetime, timedelta
    from enum import Enum
    from dataclasses import dataclass, field, asdict
    from typing import List, Dict, Optional, Any, Union
    from pathlib import Path
    import hashlib
    print("✓ Modules de base importés")
except Exception as e:
    print(f"❌ Erreur import modules de base: {e}")
    sys.exit(1)

print("\n2. Test d'import du module metadata_manager...")
try:
    from hrneowave.core.metadata_manager import (
        ExperimentType,
        WaveType,
        SensorMetadata,
        WaveConditions,
        EnvironmentalConditions,
        ModelGeometry,
        AcquisitionSettings,
        SessionMetadata,
        MetadataManager,
        create_sample_session_metadata
    )
    print("✓ Module metadata_manager importé")
except Exception as e:
    print(f"❌ Erreur import metadata_manager: {e}")
    print("\nTraceback complet:")
    traceback.print_exc()
    sys.exit(1)

print("\n3. Test de création des classes...")
try:
    # Test ExperimentType
    exp_type = ExperimentType.WAVE_PROPAGATION
    print(f"✓ ExperimentType: {exp_type}")
    
    # Test WaveType
    wave_type = WaveType.REGULAR
    print(f"✓ WaveType: {wave_type}")
    
    # Test SensorMetadata
    sensor = SensorMetadata(
        sensor_id="TEST_001",
        sensor_type="wave_probe",
        channel=0,
        location={"x": 0.0, "y": 0.0, "z": 0.0},
        measurement_range={"min": -300, "max": 300},
        units="mm"
    )
    print(f"✓ SensorMetadata: {sensor.sensor_id}")
    
    # Test WaveConditions
    wave_conditions = WaveConditions(
        wave_type=WaveType.REGULAR,
        significant_height=0.1,
        peak_period=2.0,
        wave_direction=0.0,
        water_depth=0.5
    )
    print(f"✓ WaveConditions: H={wave_conditions.significant_height}m")
    
    # Test EnvironmentalConditions
    env_conditions = EnvironmentalConditions(
        temperature=20.0,
        humidity=50.0,
        atmospheric_pressure=1013.25
    )
    print(f"✓ EnvironmentalConditions: T={env_conditions.temperature}°C")
    
    # Test ModelGeometry
    model_geometry = ModelGeometry(
        model_name="Test Model",
        model_type="ship",
        scale_factor=1.0,
        length=1.0,
        beam=0.2,
        draft=0.05
    )
    print(f"✓ ModelGeometry: {model_geometry.model_name}")
    
    # Test AcquisitionSettings
    acq_settings = AcquisitionSettings(
        sampling_rate=100.0,
        duration=60.0,
        pre_trigger=5.0,
        post_trigger=5.0
    )
    print(f"✓ AcquisitionSettings: {acq_settings.sampling_rate}Hz")
    
except Exception as e:
    print(f"❌ Erreur création classes: {e}")
    traceback.print_exc()
    sys.exit(1)

print("\n4. Test de création SessionMetadata...")
try:
    session = SessionMetadata(
        session_id=str(uuid.uuid4()),
        session_name="Test Session",
        experiment_type=ExperimentType.WAVE_PROPAGATION,
        test_number="TEST_001",
        operator="Test Operator",
        created_at=datetime.now(),
        sensors=[sensor],
        wave_conditions=wave_conditions,
        environmental_conditions=env_conditions,
        model_geometry=model_geometry,
        acquisition_settings=acq_settings
    )
    print(f"✓ SessionMetadata créé: {session.session_id}")
    
    # Test de sérialisation
    session_dict = asdict(session)
    print(f"✓ Sérialisation réussie: {len(session_dict)} champs")
    
    # Test de vérification d'intégrité
    integrity_ok = session.verify_integrity()
    print(f"✓ Intégrité: {integrity_ok}")
    
except Exception as e:
    print(f"❌ Erreur SessionMetadata: {e}")
    traceback.print_exc()
    sys.exit(1)

print("\n5. Test de création d'exemple...")
try:
    sample_session = create_sample_session_metadata()
    print(f"✓ Session d'exemple créée: {sample_session.session_name}")
    print(f"  - ID: {sample_session.session_id}")
    print(f"  - Type: {sample_session.experiment_type}")
    print(f"  - Capteurs: {len(sample_session.sensors)}")
    
except Exception as e:
    print(f"❌ Erreur création exemple: {e}")
    traceback.print_exc()
    sys.exit(1)

print("\n6. Test MetadataManager...")
try:
    import tempfile
    
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"✓ Répertoire temporaire: {temp_dir}")
        
        # Créer le gestionnaire
        manager = MetadataManager(temp_dir)
        print("✓ MetadataManager créé")
        
        # Sauvegarder
        file_path = manager.save_metadata(sample_session)
        print(f"✓ Sauvegarde: {file_path.name}")
        
        # Charger
        loaded_session = manager.load_metadata(file_path)
        print(f"✓ Chargement: {loaded_session.session_name}")
        
        # Vérifier cohérence
        if loaded_session.session_id != sample_session.session_id:
            raise ValueError("ID de session différent")
        print("✓ Cohérence vérifiée")
        
        # Lister
        sessions = manager.list_sessions()
        print(f"✓ Sessions listées: {len(sessions)}")
        
except Exception as e:
    print(f"❌ Erreur MetadataManager: {e}")
    traceback.print_exc()
    sys.exit(1)

print("\n✅ DIAGNOSTIC RÉUSSI")
print("Le module metadata_manager fonctionne correctement.")
print("Le problème doit être ailleurs dans le test principal.")