#!/usr/bin/env python3
"""
Script final pour corriger définitivement les problèmes de QSizePolicy
Utilise la méthode QSizePolicy() + setHorizontalPolicy/setVerticalPolicy
"""

import os
import re
from pathlib import Path

def fix_qsizepolicy_in_file(file_path):
    """Corrige les appels QSizePolicy dans un fichier avec la méthode qui fonctionne"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Pattern pour détecter setSizePolicy avec QSizePolicy(...)
        pattern = r'(\w+)\.setSizePolicy\(QSizePolicy\(([^,]+),\s*([^)]+)\)\)'
        
        def replace_setsize_policy(match):
            widget = match.group(1)
            arg1 = match.group(2).strip()
            arg2 = match.group(3).strip()
            
            # Générer un nom de variable unique pour la policy
            policy_var = f"{widget.lower()}_policy"
            
            replacement = f"""{policy_var} = QSizePolicy()
        {policy_var}.setHorizontalPolicy({arg1})
        {policy_var}.setVerticalPolicy({arg2})
        {widget}.setSizePolicy({policy_var})"""
            
            return replacement
        
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
    print(f"Traitement final de {len(python_files)} fichiers Python...")
    
    fixed_count = 0
    for file_path in python_files:
        if fix_qsizepolicy_in_file(file_path):
            fixed_count += 1
    
    print(f"\nTerminé: {fixed_count} fichiers modifiés sur {len(python_files)}")

if __name__ == '__main__':
    main()