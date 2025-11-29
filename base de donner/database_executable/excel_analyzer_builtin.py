#!/usr/bin/env python3
"""
Analyseur Excel utilisant les bibliothèques intégrées de Python
Pour analyser BDD INST 2025.xlsx sans dépendances externes
"""

import zipfile
import xml.etree.ElementTree as ET
import json
from pathlib import Path
import re

class ExcelAnalyzer:
    def __init__(self, excel_file):
        self.excel_file = excel_file
        self.workbook_data = {}
        self.sheets_info = {}
        
    def analyze(self):
        """Analyse le fichier Excel (.xlsx)"""
        print(f"Analyse du fichier: {self.excel_file}")
        print("=" * 50)
        
        try:
            with zipfile.ZipFile(self.excel_file, 'r') as zip_file:
                # Lire les informations du workbook
                self._read_workbook_info(zip_file)
                
                # Analyser chaque feuille
                self._analyze_sheets(zip_file)
                
                # Sauvegarder les résultats
                self._save_analysis()
                
                return self.sheets_info
                
        except Exception as e:
            print(f"Erreur lors de l'analyse: {e}")
            return None
    
    def _read_workbook_info(self, zip_file):
        """Lit les informations générales du workbook"""
        try:
            workbook_xml = zip_file.read('xl/workbook.xml').decode('utf-8')
            root = ET.fromstring(workbook_xml)
            
            # Extraire les noms des feuilles
            sheets = []
            for sheet in root.findall('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheet'):
                sheet_name = sheet.get('name')
                sheet_id = sheet.get('sheetId')
                sheets.append({'name': sheet_name, 'id': sheet_id})
            
            self.workbook_data = {
                'total_sheets': len(sheets),
                'sheets': sheets
            }
            
            print(f"Nombre de feuilles: {len(sheets)}")
            for sheet in sheets:
                print(f"  - {sheet['name']} (ID: {sheet['id']})")
            print()
            
        except Exception as e:
            print(f"Erreur lors de la lecture du workbook: {e}")
    
    def _analyze_sheets(self, zip_file):
        """Analyse chaque feuille du classeur"""
        for i, sheet in enumerate(self.workbook_data.get('sheets', []), 1):
            sheet_name = sheet['name']
            print(f"Analyse de la feuille: {sheet_name}")
            print("-" * 30)
            
            try:
                # Lire le fichier XML de la feuille
                sheet_xml_path = f'xl/worksheets/sheet{i}.xml'
                if sheet_xml_path in zip_file.namelist():
                    sheet_xml = zip_file.read(sheet_xml_path).decode('utf-8')
                    sheet_data = self._parse_sheet_xml(sheet_xml)
                    
                    self.sheets_info[sheet_name] = sheet_data
                    
                    print(f"  - Lignes avec données: {sheet_data['rows_with_data']}")
                    print(f"  - Colonnes avec données: {sheet_data['columns_with_data']}")
                    print(f"  - Cellules non vides: {sheet_data['non_empty_cells']}")
                    print()
                else:
                    print(f"  Fichier XML non trouvé pour la feuille {sheet_name}")
                    
            except Exception as e:
                print(f"  Erreur lors de l'analyse de {sheet_name}: {e}")
                self.sheets_info[sheet_name] = {'error': str(e)}
    
    def _parse_sheet_xml(self, xml_content):
        """Parse le contenu XML d'une feuille"""
        root = ET.fromstring(xml_content)
        
        rows_with_data = 0
        columns_with_data = set()
        non_empty_cells = 0
        sample_cells = []
        
        # Parcourir toutes les cellules
        for row in root.findall('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}row'):
            row_num = int(row.get('r', 0))
            has_data = False
            
            for cell in row.findall('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c'):
                cell_ref = cell.get('r', '')
                
                # Extraire la colonne de la référence (ex: A1 -> A)
                col_match = re.match(r'([A-Z]+)', cell_ref)
                if col_match:
                    columns_with_data.add(col_match.group(1))
                
                # Vérifier si la cellule a du contenu
                value_elem = cell.find('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v')
                if value_elem is not None and value_elem.text:
                    non_empty_cells += 1
                    has_data = True
                    
                    # Collecter quelques exemples
                    if len(sample_cells) < 10:
                        sample_cells.append({
                            'cell': cell_ref,
                            'value': value_elem.text
                        })
            
            if has_data:
                rows_with_data += 1
        
        return {
            'rows_with_data': rows_with_data,
            'columns_with_data': len(columns_with_data),
            'column_letters': sorted(list(columns_with_data)),
            'non_empty_cells': non_empty_cells,
            'sample_cells': sample_cells
        }
    
    def _save_analysis(self):
        """Sauvegarde l'analyse dans un fichier JSON"""
        analysis_data = {
            'workbook_info': self.workbook_data,
            'sheets_analysis': self.sheets_info
        }
        
        with open('excel_analysis_builtin.json', 'w', encoding='utf-8') as f:
            json.dump(analysis_data, f, indent=2, ensure_ascii=False)
        
        print("Analyse sauvegardée dans excel_analysis_builtin.json")

if __name__ == "__main__":
    excel_file = "BDD INST 2025.xlsx"
    
    if not Path(excel_file).exists():
        print(f"Erreur: Le fichier {excel_file} n'existe pas.")
        exit(1)
    
    analyzer = ExcelAnalyzer(excel_file)
    result = analyzer.analyze()
    
    if result:
        print("\nAnalyse terminée avec succès!")
    else:
        print("\nÉchec de l'analyse.")
