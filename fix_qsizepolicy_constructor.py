#!/usr/bin/env python3
"""
Script pour corriger tous les appels setSizePolicy avec la méthode constructeur
"""

import os
import re
from pathlib import Path

def fix_qsizepolicy_constructor(file_path):
    """Corrige les appels setSizePolicy pour utiliser le constructeur"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Pattern pour détecter setSizePolicy(QSizePolicy.X, QSizePolicy.Y)
        pattern = r'(\s*)(\w+)\.setSizePolicy\((QSizePolicy\.\w+),\s*(QSizePolicy\.\w+)\)'
        
        def replace_setsizepolicy(match):
            indent = match.group(1)
            widget_name = match.group(2)
            h_policy = match.group(3)
            v_policy = match.group(4)
            
            # Générer un nom de variable unique
            var_name = f"{widget_name}_policy"
            if widget_name == "self":
                var_name = "self_policy"
            
            return f"{indent}{var_name} = QSizePolicy({h_policy}, {v_policy})\n{indent}{widget_name}.setSizePolicy({var_name})"
        
        content = re.sub(pattern, replace_setsizepolicy, content)
        
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
        if fix_qsizepolicy_constructor(file_path):
            modified_files.append(file_path)
            print(f"Modifié: {file_path}")
    
    print(f"\nTerminé. {len(modified_files)} fichiers modifiés sur {len(python_files)}.")
    if modified_files:
        print("Fichiers modifiés:")
        for file_path in modified_files:
            print(f"  - {file_path}")

if __name__ == "__main__":
    main()