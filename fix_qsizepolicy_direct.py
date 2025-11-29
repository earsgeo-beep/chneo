#!/usr/bin/env python3
"""
Script pour corriger tous les appels QSizePolicy.Policy.X vers QSizePolicy.X
"""

import os
import re
from pathlib import Path

def fix_qsizepolicy_notation(file_path):
    """Corrige la notation QSizePolicy dans un fichier"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Remplacer QSizePolicy.Policy.X par QSizePolicy.X
        replacements = {
            'QSizePolicy.Policy.Expanding': 'QSizePolicy.Expanding',
            'QSizePolicy.Policy.Preferred': 'QSizePolicy.Preferred',
            'QSizePolicy.Policy.Fixed': 'QSizePolicy.Fixed',
            'QSizePolicy.Policy.Minimum': 'QSizePolicy.Minimum',
            'QSizePolicy.Policy.Maximum': 'QSizePolicy.Maximum',
            'QSizePolicy.Policy.MinimumExpanding': 'QSizePolicy.MinimumExpanding',
            'QSizePolicy.Policy.Ignored': 'QSizePolicy.Ignored'
        }
        
        for old_notation, new_notation in replacements.items():
            content = content.replace(old_notation, new_notation)
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        
        return False
        
    except Exception as e:
        print(f"Erreur lors du traitement de {file_path}: {e}")
        return False

def main():
    """Fonction principale"""
    src_dir = Path("src")
    if not src_dir.exists():
        print("Répertoire src non trouvé")
        return
    
    python_files = list(src_dir.rglob("*.py"))
    print(f"Traitement de {len(python_files)} fichiers Python...")
    
    modified_files = []
    
    for file_path in python_files:
        if fix_qsizepolicy_notation(file_path):
            modified_files.append(file_path)
            print(f"Modifié: {file_path}")
    
    print(f"\nTerminé. {len(modified_files)} fichiers modifiés sur {len(python_files)}.")
    if modified_files:
        print("Fichiers modifiés:")
        for file_path in modified_files:
            print(f"  - {file_path}")

if __name__ == "__main__":
    main()