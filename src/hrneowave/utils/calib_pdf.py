#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module de génération de certificats PDF de calibration
Utilise ReportLab pour créer des rapports de calibration professionnels
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm, mm
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.platypus import Image as RLImage
    from reportlab.graphics.shapes import Drawing, Line
    from reportlab.graphics.charts.lineplots import LinePlot
    from reportlab.graphics.widgets.markers import makeMarker
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Backend non-interactif

from .hash_tools import hash_string


class CalibrationPDFGenerator:
    """
    Générateur de certificats PDF de calibration
    """
    
    def __init__(self):
        if not REPORTLAB_AVAILABLE:
            raise ImportError("ReportLab n'est pas installé. Installez-le avec: pip install reportlab")
        
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """
        Configuration des styles personnalisés
        """
        # Style pour le titre principal
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#2c3e50')
        ))
        
        # Style pour les sous-titres
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            textColor=colors.HexColor('#34495e')
        ))
        
        # Style pour le texte normal
        self.styles.add(ParagraphStyle(
            name='CustomNormal',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6
        ))
        
        # Style pour les signatures
        self.styles.add(ParagraphStyle(
            name='Signature',
            parent=self.styles['Normal'],
            fontSize=8,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#7f8c8d')
        ))
    
    def generate_certificate(self, calibration_data: Dict, output_path: str) -> bool:
        """
        Méthode de compatibilité pour les tests
        """
        # Validation des données d'entrée
        if not isinstance(calibration_data, dict):
            raise ValueError("Les données de calibration doivent être un dictionnaire")
        
        # Vérifier la présence de données de capteurs/canaux
        if 'sensors' not in calibration_data and 'channels' not in calibration_data:
            raise ValueError("Aucune donnée de capteur ou canal trouvée")
        
        # Convertir la structure de données des tests vers le format attendu
        converted_data = self._convert_test_data_format(calibration_data)
        
        # Extraire les informations du capteur depuis calibration_data
        sensor_info = {
            'name': calibration_data.get('sensor_name', 'Capteur de houle'),
            'type': calibration_data.get('sensor_type', 'Résistif'),
            'serial_number': calibration_data.get('serial_number', 'CHN-001')
        }
        
        # Stocker les données originales pour la signature
        converted_data['_original_data'] = calibration_data
        
        return self.generate_calibration_certificate(output_path, converted_data, sensor_info)
    
    def _convert_test_data_format(self, test_data: Dict) -> Dict:
        """
        Convertit le format de données des tests vers le format interne
        """
        converted = test_data.copy()
        
        # Si on a des 'sensors', les convertir en 'channels'
        if 'sensors' in test_data:
            channels = []
            for sensor in test_data['sensors']:
                channel = {
                    'channel': sensor.get('id', sensor.get('channel', 1)),
                    'gain': sensor.get('gain', 1.0),
                    'offset': sensor.get('offset', 0.0),
                    'r_squared': sensor.get('r_squared', 0.999)
                }
                channels.append(channel)
            converted['channels'] = channels
        
        return converted
    
    def generate_calibration_certificate(
        self,
        output_path: str,
        calibration_data: Dict,
        sensor_info: Dict,
        lab_info: Optional[Dict] = None
    ) -> bool:
        """
        Génère un certificat PDF de calibration
        
        Args:
            output_path: Chemin de sortie du PDF
            calibration_data: Données de calibration (gains, offsets, R²)
            sensor_info: Informations sur le capteur
            lab_info: Informations sur le laboratoire
        
        Returns:
            True si la génération a réussi
        """
        try:
            # Création du document PDF
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=2*cm,
                leftMargin=2*cm,
                topMargin=2*cm,
                bottomMargin=2*cm
            )
            
            # Construction du contenu
            story = []
            
            # En-tête
            story.extend(self._build_header(lab_info))
            
            # Titre principal
            story.append(Paragraph(
                "CERTIFICAT DE CALIBRATION",
                self.styles['CustomHeading']
            ))
            story.append(Spacer(1, 20))
            
            # Informations générales
            story.extend(self._build_general_info(sensor_info, calibration_data))
            
            # Tableau des résultats de calibration
            story.extend(self._build_calibration_table(calibration_data))
            
            # Graphique de linéarité
            linearity_plot_path = self._create_linearity_plot(calibration_data, output_path)
            if linearity_plot_path:
                story.extend(self._build_linearity_section(linearity_plot_path))
            
            # Signature numérique
            story.extend(self._build_digital_signature(calibration_data))
            
            # Pied de page
            story.extend(self._build_footer())
            
            # Génération du PDF
            doc.build(story)
            
            # Nettoyage des fichiers temporaires
            if linearity_plot_path and os.path.exists(linearity_plot_path):
                os.remove(linearity_plot_path)
            
            return True
            
        except Exception as e:
            print(f"Erreur lors de la génération du PDF: {e}")
            return False
    
    def _build_header(self, lab_info: Optional[Dict]) -> List:
        """
        Construction de l'en-tête du document
        """
        elements = []
        
        # Titre CHNeoWave en premier
        elements.append(Paragraph(
            "<b>CHNeoWave</b> - Système d'Acquisition Maritime",
            self.styles['CustomTitle']
        ))
        elements.append(Spacer(1, 10))
        
        if lab_info:
            lab_name = lab_info.get('name', 'Laboratoire d\'Études Maritimes')
            lab_address = lab_info.get('address', 'Méditerranée, France')
            
            elements.append(Paragraph(
                f"<b>{lab_name}</b><br/>{lab_address}",
                self.styles['CustomNormal']
            ))
        else:
            elements.append(Paragraph(
                "<b>Laboratoire d'Études Maritimes</b><br/>Méditerranée, France",
                self.styles['CustomNormal']
            ))
        
        elements.append(Spacer(1, 20))
        return elements
    
    def _build_general_info(self, sensor_info: Dict, calibration_data: Dict) -> List:
        """
        Construction des informations générales
        """
        elements = []
        
        elements.append(Paragraph("Informations Générales", self.styles['CustomHeading']))
        
        # Tableau d'informations
        info_data = [
            ['Capteur:', sensor_info.get('name', 'N/A')],
            ['Type:', sensor_info.get('type', 'N/A')],
            ['Numéro de série:', sensor_info.get('serial_number', 'N/A')],
            ['Date de calibration:', calibration_data.get('calibration_date', datetime.now().strftime('%d/%m/%Y'))],
            ['Opérateur:', calibration_data.get('operator', 'CHNeoWave System')],
            ['Température:', f"{calibration_data.get('temperature', 20.0):.1f} °C"],
            ['Humidité:', f"{calibration_data.get('humidity', 50.0):.1f} %"]
        ]
        
        info_table = Table(info_data, colWidths=[4*cm, 8*cm])
        info_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1'))
        ]))
        
        elements.append(info_table)
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _build_calibration_table(self, calibration_data: Dict) -> List:
        """
        Construction du tableau des résultats de calibration
        """
        elements = []
        
        elements.append(Paragraph("Résultats de Calibration", self.styles['CustomHeading']))
        
        # Données de calibration
        channels = calibration_data.get('channels', [])
        if not channels:
            # Données par défaut si aucune donnée
            channels = [{
                'channel': 1,
                'gain': 1.0,
                'offset': 0.0,
                'r_squared': 0.999
            }]
        
        # En-tête du tableau
        table_data = [['Canal', 'Gain', 'Offset', 'R² (Linéarité)', 'Statut']]
        
        # Données des canaux
        for channel in channels:
            gain = channel.get('gain', 1.0)
            offset = channel.get('offset', 0.0)
            r_squared = channel.get('r_squared', 0.999)
            
            # Statut basé sur R²
            if r_squared >= 0.998:
                status = "✓ Conforme"
                status_color = colors.green
            elif r_squared >= 0.995:
                status = "⚠ Acceptable"
                status_color = colors.orange
            else:
                status = "✗ Non conforme"
                status_color = colors.red
            
            table_data.append([
                str(channel.get('channel', 'N/A')),
                f"{gain:.6f}",
                f"{offset:.6f}",
                f"{r_squared:.6f}",
                status
            ])
        
        # Création du tableau
        calib_table = Table(table_data, colWidths=[2*cm, 3*cm, 3*cm, 3*cm, 3*cm])
        calib_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white)
        ]))
        
        elements.append(calib_table)
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _create_linearity_plot(self, calibration_data: Dict, output_path: str) -> Optional[str]:
        """
        Création du graphique de linéarité
        """
        try:
            channels = calibration_data.get('channels', [])
            if not channels:
                return None
            
            # Création du graphique
            fig, ax = plt.subplots(figsize=(8, 6))
            
            plotted_channels = 0
            # Pour chaque canal, tracer uniquement les points réellement saisis.
            for i, channel in enumerate(channels[:4]):  # Max 4 canaux pour la lisibilité
                record = channel.get('calibration_record') or channel
                points = record.get('points') or []
                if len(points) < 2:
                    continue
                x_ref = np.asarray(
                    [point['reference_value'] for point in points],
                    dtype=float,
                )
                y_measured = np.asarray(
                    [point['measured_voltage'] for point in points],
                    dtype=float,
                )
                gain = float(
                    record.get('sensitivity_v_per_unit', record.get('gain', 0.0))
                )
                offset = float(
                    record.get('intercept_volts', record.get('offset', 0.0))
                )
                r_squared = float(record.get('r_squared', 0.0))
                fit_reference = np.linspace(float(np.min(x_ref)), float(np.max(x_ref)), 100)
                fit_voltage = gain * fit_reference + offset
                
                # Tracé
                color = plt.cm.tab10(i)
                ax.scatter(x_ref, y_measured, color=color, alpha=0.7, 
                          label=f'Canal {channel.get("channel", i+1)} (R²={r_squared:.4f})')
                ax.plot(fit_reference, fit_voltage, color=color, linestyle='--', alpha=0.8)
                plotted_channels += 1

            if not plotted_channels:
                plt.close(fig)
                return None
            
            ax.set_xlabel('Valeur de référence')
            ax.set_ylabel('Valeur mesurée')
            ax.set_title('Linéarité de la calibration')
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            # Sauvegarde temporaire
            plot_path = output_path.replace('.pdf', '_linearity.png')
            plt.savefig(plot_path, dpi=150, bbox_inches='tight')
            plt.close()
            
            return plot_path
            
        except Exception as e:
            print(f"Erreur lors de la création du graphique: {e}")
            return None
    
    def _build_linearity_section(self, plot_path: str) -> List:
        """
        Construction de la section graphique de linéarité
        """
        elements = []
        
        elements.append(Paragraph("Graphique de Linéarité", self.styles['CustomHeading']))
        
        try:
            # Ajout de l'image
            img = RLImage(plot_path, width=14*cm, height=10.5*cm)
            elements.append(img)
        except Exception as e:
            elements.append(Paragraph(
                f"Erreur lors du chargement du graphique: {e}",
                self.styles['CustomNormal']
            ))
        
        elements.append(Spacer(1, 20))
        return elements
    
    def _build_digital_signature(self, calibration_data: Dict) -> List:
        """
        Construction de la signature numérique
        """
        elements = []
        
        elements.append(Paragraph("Signature Numérique", self.styles['CustomHeading']))
        
        # Utiliser les données originales si disponibles, sinon les données converties
        data_for_signature = calibration_data.get('_original_data', calibration_data)
        
        # Nettoyer les données pour la signature (enlever les métadonnées internes)
        clean_data = {k: v for k, v in data_for_signature.items() if not k.startswith('_')}
        
        # Calcul du hash SHA-256 des données de calibration
        calib_json = json.dumps(clean_data, sort_keys=True, default=str)
        signature_hash = hash_string(calib_json)
        
        elements.append(Paragraph(
            f"<b>SHA-256:</b> {signature_hash}",
            self.styles['CustomNormal']
        ))
        
        elements.append(Paragraph(
            f"<b>Généré le:</b> {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}",
            self.styles['CustomNormal']
        ))
        
        elements.append(Spacer(1, 20))
        return elements
    
    def _build_footer(self) -> List:
        """
        Construction du pied de page
        """
        elements = []
        
        elements.append(Spacer(1, 30))
        elements.append(Paragraph(
            "Ce certificat a été généré automatiquement par CHNeoWave v1.1.0",
            self.styles['Signature']
        ))
        
        return elements
    
    def validate_calibration_data(self, calibration_data: Dict) -> Tuple[bool, str]:
        """
        Validation des données de calibration
        
        Returns:
            Tuple (is_valid, error_message)
        """
        if not isinstance(calibration_data, dict):
            return False, "Les données de calibration doivent être un dictionnaire"
        
        # Support des deux formats: 'channels' et 'sensors'
        channels = calibration_data.get('channels', [])
        sensors = calibration_data.get('sensors', [])
        
        data_to_validate = channels if channels else sensors
        
        if not data_to_validate:
            return False, "Aucun canal/capteur de calibration trouvé"
        
        for i, item in enumerate(data_to_validate):
            if not isinstance(item, dict):
                return False, f"L'élément {i+1} doit être un dictionnaire"
            
            r_squared = item.get('r_squared')
            if r_squared is None:
                return False, f"R² manquant pour l'élément {i+1}"
            
            if not isinstance(r_squared, (int, float)):
                return False, f"R² invalide pour l'élément {i+1}"
            
            if r_squared < 0.995:
                return False, f"R² trop faible ({r_squared:.4f}) pour l'élément {i+1}. Minimum requis: 0.995"
        
        return True, "Données de calibration valides"


def create_calibration_certificate(
    output_path: str,
    calibration_data: Dict,
    sensor_info: Optional[Dict] = None,
    lab_info: Optional[Dict] = None
) -> bool:
    """
    Fonction utilitaire pour créer un certificat de calibration
    
    Args:
        output_path: Chemin de sortie du PDF
        calibration_data: Données de calibration
        sensor_info: Informations sur le capteur
        lab_info: Informations sur le laboratoire
    
    Returns:
        True si la génération a réussi
    """
    if not REPORTLAB_AVAILABLE:
        print("ReportLab n'est pas disponible. Installation requise: pip install reportlab")
        return False
    
    generator = CalibrationPDFGenerator()
    
    # Validation des données
    is_valid, error_msg = generator.validate_calibration_data(calibration_data)
    if not is_valid:
        print(f"Erreur de validation: {error_msg}")
        return False
    
    # Informations par défaut
    if sensor_info is None:
        sensor_info = {
            'name': 'Capteur de Houle',
            'type': 'Résistif',
            'serial_number': 'CHW-001'
        }
    
    return generator.generate_calibration_certificate(
        output_path, calibration_data, sensor_info, lab_info
    )


if __name__ == "__main__":
    # Test de génération d'un certificat
    test_calibration_data = {
        'calibration_date': '15/12/2024',
        'operator': 'Technicien Test',
        'temperature': 21.5,
        'humidity': 45.0,
        'channels': [
            {'channel': 1, 'gain': 1.000123, 'offset': 0.000456, 'r_squared': 0.9995},
            {'channel': 2, 'gain': 0.999876, 'offset': -0.000123, 'r_squared': 0.9998},
            {'channel': 3, 'gain': 1.000789, 'offset': 0.000234, 'r_squared': 0.9996}
        ]
    }
    
    test_sensor_info = {
        'name': 'Capteur Test',
        'type': 'Résistif',
        'serial_number': 'TEST-001'
    }
    
    success = create_calibration_certificate(
        'test_calibration.pdf',
        test_calibration_data,
        test_sensor_info
    )
    
    if success:
        print("Certificat de test généré avec succès")
    else:
        print("Erreur lors de la génération du certificat")
