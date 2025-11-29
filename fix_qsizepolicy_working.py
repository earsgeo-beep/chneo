#!/usr/bin/env python3
"""
Script pour corriger tous les appels QSizePolicy avec la méthode qui fonctionne
"""

import os
import re
from pathlib import Path

def fix_qsizepolicy_calls(file_path):
    """Corrige les appels QSizePolicy dans un fichier"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Pattern pour détecter les blocs QSizePolicy problématiques
        # Recherche les patterns comme:
        # var_policy = QSizePolicy()
        # var_policy.setHorizontalPolicy(...)
        # var_policy.setVerticalPolicy(...)
        # widget.setSizePolicy(var_policy)
        
        pattern = r'(\s+)(\w+)_policy = QSizePolicy\(\)\s*\n\s*\2_policy\.setHorizontalPolicy\((QSizePolicy\.Policy\.\w+)\)\s*\n\s*\2_policy\.setVerticalPolicy\((QSizePolicy\.Policy\.\w+)\)\s*\n\s*(\w+)\.setSizePolicy\(\2_policy\)'
        
        def replace_qsizepolicy(match):
            indent = match.group(1)
            var_name = match.group(2)
            h_policy = match.group(3)
            v_policy = match.group(4)
            widget_name = match.group(5)
            
            return f"{indent}{widget_name}.setSizePolicy({h_policy}, {v_policy})"
        
        content = re.sub(pattern, replace_qsizepolicy, content, flags=re.MULTILINE)
        
        # Pattern alternatif pour les cas où la variable n'a pas le suffixe _policy
        pattern2 = r'(\s+)(\w+_policy) = QSizePolicy\(\)\s*\n\s*\2\.setHorizontalPolicy\((QSizePolicy\.Policy\.\w+)\)\s*\n\s*\2\.setVerticalPolicy\((QSizePolicy\.Policy\.\w+)\)\s*\n\s*(\w+)\.setSizePolicy\(\2\)'
        
        def replace_qsizepolicy2(match):
            indent = match.group(1)
            var_name = match.group(2)
            h_policy = match.group(3)
            v_policy = match.group(4)
            widget_name = match.group(5)
            
            return f"{indent}{widget_name}.setSizePolicy({h_policy}, {v_policy})"
        
        content = re.sub(pattern2, replace_qsizepolicy2, content, flags=re.MULTILINE)
        
        # Pattern pour les cas avec self
        pattern3 = r'(\s+)(\w+_policy) = QSizePolicy\(\)\s*\n\s*\2\.setHorizontalPolicy\((QSizePolicy\.Policy\.\w+)\)\s*\n\s*\2\.setVerticalPolicy\((QSizePolicy\.Policy\.\w+)\)\s*\n\s*self\.setSizePolicy\(\2\)'
        
        def replace_qsizepolicy3(match):
            indent = match.group(1)
            var_name = match.group(2)
            h_policy = match.group(3)
            v_policy = match.group(4)
            
            return f"{indent}self.setSizePolicy({h_policy}, {v_policy})"
        
        content = re.sub(pattern3, replace_qsizepolicy3, content, flags=re.MULTILINE)
        
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
        if fix_qsizepolicy_calls(file_path):
            modified_files.append(file_path)
            print(f"Modifié: {file_path}")
    
    print(f"\nTerminé. {len(modified_files)} fichiers modifiés sur {len(python_files)}.")
    if modified_files:
        print("Fichiers modifiés:")
        for file_path in modified_files:
            print(f"  - {file_path}")

if __name__ == "__main__":
    main()