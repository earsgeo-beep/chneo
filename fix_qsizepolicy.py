#!/usr/bin/env python3
"""
Script pour corriger les problèmes de QSizePolicy dans CHNeoWave
PySide6 6.9.x nécessite une syntaxe spécifique
"""

import os
import re
from pathlib import Path

def fix_qsizepolicy_in_file(file_path):
    """Corrige les appels QSizePolicy dans un fichier"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Pattern pour détecter setSizePolicy avec deux arguments directs
        pattern = r'(\w+)\.setSizePolicy\(([^,]+),\s*([^)]+)\)'
        
        def replace_setsize_policy(match):
            widget = match.group(1)
            arg1 = match.group(2).strip()
            arg2 = match.group(3).strip()
            
            # Si les arguments sont déjà des objets QSizePolicy complets, ne pas changer
            if 'QSizePolicy(' in arg1:
                return match.group(0)
            
            # Convertir les constantes en objets QSizePolicy complets
            policy_map = {
                'QSizePolicy.Expanding': 'QSizePolicy.Policy.Expanding',
                'QSizePolicy.Preferred': 'QSizePolicy.Policy.Preferred', 
                'QSizePolicy.Fixed': 'QSizePolicy.Policy.Fixed',
                'QSizePolicy.Minimum': 'QSizePolicy.Policy.Minimum',
                'EXPANDING': 'QSizePolicy.Policy.Expanding',
                'PREFERRED': 'QSizePolicy.Policy.Preferred',
                'FIXED': 'QSizePolicy.Policy.Fixed',
                'MINIMUM': 'QSizePolicy.Policy.Minimum'
            }
            
            # Remplacer les constantes par les valeurs Policy complètes
            for old, new in policy_map.items():
                arg1 = arg1.replace(old, new)
                arg2 = arg2.replace(old, new)
            
            return f'{widget}.setSizePolicy(QSizePolicy({arg1}, {arg2}))'
        
        # Appliquer les corrections
        content = re.sub(pattern, replace_setsize_policy, content)
        
        # Écrire le fichier seulement s'il y a des changements
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✓ Corrigé: {file_path}")
            return True
        else:
            print(f"- Aucun changement: {file_path}")
            return False
            
    except Exception as e:
        print(f"✗ Erreur dans {file_path}: {e}")
        return False

def main():
    """Fonction principale"""
    src_dir = Path('src')
    
    if not src_dir.exists():
        print("Répertoire 'src' non trouvé")
        return
    
    python_files = list(src_dir.rglob('*.py'))
    print(f"Traitement de {len(python_files)} fichiers Python...")
    
    fixed_count = 0
    for file_path in python_files:
        if fix_qsizepolicy_in_file(file_path):
            fixed_count += 1
    
    print(f"\nTerminé: {fixed_count} fichiers modifiés sur {len(python_files)}")

if __name__ == '__main__':
    main()