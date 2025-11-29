#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de lancement principal pour CHNeoWave
"""

import sys
import os
import argparse

# Ajouter le répertoire src au path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

def main():
    """
    Point d'entrée principal
    """
    parser = argparse.ArgumentParser(
        description="CHNeoWave - Logiciel d'acquisition et d'analyse de données maritimes",
        prog="chneowave"
    )
    
    parser.add_argument(
        "--version", 
        action="version", 
        version="CHNeoWave 1.0.0"
    )
    
    parser.add_argument(
        "--gui", 
        action="store_true", 
        default=True,
        help="Lance l'interface graphique (par défaut)"
    )
    
    parser.add_argument(
        "--debug", 
        action="store_true", 
        help="Active le mode debug"
    )
    
    args = parser.parse_args()
    
    if args.debug:
        import logging
        logging.basicConfig(level=logging.DEBUG)
        print("Mode debug activé")
    
    # Lancer l'interface graphique
    try:
        import main
        main.main()
    except Exception as e:
        print(f"Erreur lors du lancement: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()