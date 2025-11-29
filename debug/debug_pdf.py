#!/usr/bin/env python3
"""
Script de débogage pour les problèmes PDF
"""

import sys
import os
import json
from pathlib import Path

# Ajouter le chemin src au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from hrneowave.utils.calib_pdf import CalibrationPDFGenerator
from hrneowave.utils.hash_tools import hash_string

def debug_pdf_generation():
    """Test de génération et lecture PDF"""
    
    # Données de test
    sample_data = {
        'sensor_count': 2,
        'sensors': [
            {
                'id': 1,
                'name': 'Capteur Test 1',
                'gain': 1.000123,
                'offset': 0.000456,
                'r_squared': 0.9995,
                'points': [
                    {'reference': 0.0, 'measured': 0.000456, 'error': 0.000456},
                    {'reference': 5.0, 'measured': 5.000579, 'error': 0.000579},
                    {'reference': 10.0, 'measured': 10.000702, 'error': 0.000702}
                ]
            },
            {
                'id': 2,
                'name': 'Capteur Test 2',
                'gain': 0.999876,
                'offset': -0.000123,
                'r_squared': 0.9998,
                'points': [
                    {'reference': 0.0, 'measured': -0.000123, 'error': -0.000123},
                    {'reference': 5.0, 'measured': 4.999257, 'error': -0.000743},
                    {'reference': 10.0, 'measured': 9.998637, 'error': -0.001363}
                ]
            }
        ]
    }
    
    output_file = 'debug_test.pdf'
    
    try:
        print("=== Génération du PDF ===")
        generator = CalibrationPDFGenerator()
        success = generator.generate_certificate(sample_data, output_file)
        
        if not success:
            print("❌ Échec de la génération PDF")
            return
        
        print("✓ PDF généré avec succès")
        
        # Calcul du hash attendu
        expected_hash = hash_string(json.dumps(sample_data, sort_keys=True, default=str))
        print(f"Hash attendu: {expected_hash}")
        
        print("\n=== Lecture du contenu PDF ===")
        
        # Lecture avec différents encodages
        encodings = ['latin-1', 'utf-8', 'cp1252']
        
        for encoding in encodings:
            try:
                print(f"\n--- Tentative avec encodage {encoding} ---")
                with open(output_file, 'rb') as f:
                    pdf_content = f.read().decode(encoding, errors='ignore')
                
                # Recherche du titre
                if 'CHNeoWave' in pdf_content:
                    print("✓ Titre CHNeoWave trouvé")
                else:
                    print("❌ Titre CHNeoWave manquant")
                
                # Recherche du hash (premiers 16 caractères)
                hash_short = expected_hash[:16]
                if hash_short in pdf_content:
                    print(f"✓ Hash SHA-256 trouvé: {hash_short}...")
                else:
                    print(f"❌ Hash SHA-256 manquant: {hash_short}...")
                
                # Recherche de mots-clés
                keywords = ['Certificat', 'Calibration', 'Signature', 'SHA-256']
                for keyword in keywords:
                    if keyword in pdf_content:
                        print(f"✓ Mot-clé '{keyword}' trouvé")
                    else:
                        print(f"❌ Mot-clé '{keyword}' manquant")
                
                # Afficher un extrait du contenu
                print(f"\nExtrait du contenu (premiers 500 caractères):")
                print(repr(pdf_content[:500]))
                
            except Exception as e:
                print(f"❌ Erreur avec encodage {encoding}: {e}")
        
        # Nettoyage
        if os.path.exists(output_file):
            os.remove(output_file)
            print(f"\n✓ Fichier {output_file} supprimé")
        
    except Exception as e:
        print(f"❌ Erreur générale: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    debug_pdf_generation()