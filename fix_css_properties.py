#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de nettoyage des propriétés CSS incompatibles avec Qt
CHNeoWave - Correction critique pour affichage interface
"""

import os
import re
from pathlib import Path

def clean_css_properties(content: str) -> tuple[str, bool]:
    """
    Nettoie les propriétés CSS incompatibles avec Qt
    
    Returns:
        tuple: (contenu_nettoyé, modifié)
    """
    original_content = content
    
    # Propriétés CSS à supprimer ou commenter
    problematic_properties = [
        r'transition\s*:[^;]+;',
        r'transform\s*:[^;]+;',
        r'box-shadow\s*:[^;]+;',
        r'text-transform\s*:[^;]+;',
        r'outline-offset\s*:[^;]+;',
        r'content\s*:[^;]+;',
        r'::before\s*{[^}]*}',
        r'::after\s*{[^}]*}'
    ]
    
    # Commenter les propriétés problématiques
    for pattern in problematic_properties:
        content = re.sub(
            pattern,
            lambda m: f'/* {m.group(0)} - Non supporté par Qt */',
            content,
            flags=re.IGNORECASE | re.MULTILINE
        )
    
    # Nettoyer les commentaires déjà existants pour éviter les doublons
    content = re.sub(
        r'/\*\s*(/\*[^*]*\*/)\s*-\s*Non supporté par Qt\s*\*/',
        r'\1',
        content
    )
    
    return content, content != original_content

def process_python_file(file_path: Path) -> bool:
    """
    Traite un fichier Python pour nettoyer les setStyleSheet
    
    Returns:
        bool: True si le fichier a été modifié
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Vérifier si le fichier contient setStyleSheet
        if 'setStyleSheet' not in content:
            return False
        
        cleaned_content, modified = clean_css_properties(content)
        
        if modified:
            # Sauvegarder le fichier modifié
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(cleaned_content)
            print(f"✅ Nettoyé: {file_path}")
            return True
        else:
            print(f"⚪ Aucune modification: {file_path}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors du traitement de {file_path}: {e}")
        return False

def process_qss_file(file_path: Path) -> bool:
    """
    Traite un fichier QSS pour nettoyer les propriétés incompatibles
    
    Returns:
        bool: True si le fichier a été modifié
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        cleaned_content, modified = clean_css_properties(content)
        
        if modified:
            # Sauvegarder le fichier modifié
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(cleaned_content)
            print(f"✅ Nettoyé QSS: {file_path}")
            return True
        else:
            print(f"⚪ Aucune modification QSS: {file_path}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors du traitement QSS de {file_path}: {e}")
        return False

def main():
    """
    Fonction principale de nettoyage
    """
    print("🔧 CHNeoWave - Nettoyage des propriétés CSS incompatibles")
    print("=" * 60)
    
    # Répertoire de base
    base_dir = Path("C:/Users/LEM/Desktop/chneowave/src/hrneowave/gui")
    
    if not base_dir.exists():
        print(f"❌ Répertoire non trouvé: {base_dir}")
        return
    
    modified_files = []
    
    # Traiter les fichiers Python
    print("\n📁 Traitement des fichiers Python (.py)...")
    for py_file in base_dir.rglob("*.py"):
        if process_python_file(py_file):
            modified_files.append(py_file)
    
    # Traiter les fichiers QSS
    print("\n📁 Traitement des fichiers QSS (.qss)...")
    for qss_file in base_dir.rglob("*.qss"):
        if process_qss_file(qss_file):
            modified_files.append(qss_file)
    
    # Résumé
    print("\n" + "=" * 60)
    print(f"✅ Nettoyage terminé: {len(modified_files)} fichiers modifiés")
    
    if modified_files:
        print("\n📋 Fichiers modifiés:")
        for file_path in modified_files:
            print(f"  - {file_path.relative_to(base_dir)}")
    
    print("\n🚀 Vous pouvez maintenant relancer main.py")
    print("   Les erreurs 'Could not parse stylesheet' devraient être résolues.")

if __name__ == "__main__":
    main()