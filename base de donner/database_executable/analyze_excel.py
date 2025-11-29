#!/usr/bin/env python3
"""
Script d'analyse du fichier BDD INST 2025.xlsx
Analyse la structure des données pour créer une base de données moderne
"""

import pandas as pd
import json
from pathlib import Path
import sys

def analyze_excel_file(file_path):
    """Analyse le fichier Excel et extrait la structure des données"""
    
    print(f"Analyse du fichier: {file_path}")
    print("=" * 50)
    
    try:
        # Lire toutes les feuilles Excel
        excel_file = pd.ExcelFile(file_path)
        sheets = excel_file.sheet_names
        
        print(f"Nombre de feuilles trouvées: {len(sheets)}")
        print(f"Noms des feuilles: {sheets}")
        print("\n")
        
        analysis_result = {
            "file_info": {
                "total_sheets": len(sheets),
                "sheet_names": sheets
            },
            "sheets_analysis": {}
        }
        
        # Analyser chaque feuille
        for sheet_name in sheets:
            print(f"Analyse de la feuille: {sheet_name}")
            print("-" * 30)
            
            try:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                
                sheet_info = {
                    "rows": len(df),
                    "columns": len(df.columns),
                    "column_names": list(df.columns),
                    "data_types": df.dtypes.to_dict(),
                    "sample_data": df.head(3).to_dict('records') if len(df) > 0 else []
                }
                
                analysis_result["sheets_analysis"][sheet_name] = sheet_info
                
                print(f"  - Lignes: {len(df)}")
                print(f"  - Colonnes: {len(df.columns)}")
                print(f"  - Noms des colonnes: {list(df.columns)}")
                
                # Afficher quelques exemples de données
                if len(df) > 0:
                    print("  - Aperçu des données:")
                    for i, row in df.head(2).iterrows():
                        print(f"    Ligne {i+1}: {dict(row)}")
                
                print()
                
            except Exception as e:
                print(f"  Erreur lors de la lecture de la feuille {sheet_name}: {e}")
                analysis_result["sheets_analysis"][sheet_name] = {"error": str(e)}
        
        # Sauvegarder l'analyse
        with open("excel_analysis.json", "w", encoding="utf-8") as f:
            json.dump(analysis_result, f, indent=2, ensure_ascii=False, default=str)
        
        print("Analyse terminée. Résultats sauvegardés dans excel_analysis.json")
        return analysis_result
        
    except Exception as e:
        print(f"Erreur lors de l'analyse du fichier: {e}")
        return None

if __name__ == "__main__":
    file_path = "BDD INST 2025.xlsx"
    
    if not Path(file_path).exists():
        print(f"Erreur: Le fichier {file_path} n'existe pas.")
        sys.exit(1)
    
    analyze_excel_file(file_path)
