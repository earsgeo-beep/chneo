# -*- coding: utf-8 -*-
"""
CHNeoWave Dashboard View Maritime 2025 - Version Simplifiée
"""

import sys
from datetime import datetime
from typing import Dict, List, Optional
import logging

# Import PySide6 uniquement
from PySide6.QtCore import Qt, QTimer, Signal, QPropertyAnimation, QEasingCurve, QRect
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, 
    QPushButton, QFrame, QScrollArea, QSizePolicy, QSpacerItem
)
from PySide6.QtGui import QFont, QPalette, QColor
pyqtSignal = Signal

# Classes simplifiées
class MaritimeTheme:
    SPACE_XS = 8
    SPACE_SM = 13
    SPACE_MD = 21
    SPACE_LG = 34
    SPACE_XL = 55
    OCEAN_DEEP = "#0A1929"
    HARBOR_BLUE = "#1565C0"
    TIDAL_CYAN = "#00BCD4"
    FOAM_WHITE = "#FAFBFC"
    STORM_GRAY = "#37474F"

class StatusType:
    ACTIVE = "active"
    WARNING = "warning"
    ERROR = "error"
    INACTIVE = "inactive"

class DashboardMetrics:
    """Gestionnaire des métriques du tableau de bord maritime"""
    
    def __init__(self):
        self.metrics = {
            'system_status': StatusType.ACTIVE,
            'active_sessions': 0,
            'data_quality': 95.7,
            'performance_score': 88.3,
            'wave_height': 2.3,
            'current_speed': 1.2,
            'temperature': 18.5,
            'last_update': datetime.now()
        }
    
    def update_metric(self, key: str, value):
        """Met à jour une métrique"""
        self.metrics[key] = value
        self.metrics['last_update'] = datetime.now()
    
    def get_metric(self, key: str):
        """Récupère une métrique"""
        return self.metrics.get(key)
    
    def get_all_metrics(self) -> Dict:
        """Récupère toutes les métriques"""
        return self.metrics.copy()
    
    def get_kpi_data(self) -> List[Dict]:
        """Récupère les données KPI"""
        return [
            {
                'label': 'Hauteur de Vague',
                'value': self.metrics['wave_height'],
                'unit': 'm',
                'precision': 1,
                'status': StatusType.ACTIVE
            },
            {
                'label': 'Vitesse Courant',
                'value': self.metrics['current_speed'],
                'unit': 'm/s',
                'precision': 1,
                'status': StatusType.ACTIVE
            },
            {
                'label': 'Température',
                'value': self.metrics['temperature'],
                'unit': '°C',
                'precision': 1,
                'status': StatusType.ACTIVE
            },
            {
                'label': 'Qualité Données',
                'value': self.metrics['data_quality'],
                'unit': '%',
                'precision': 1,
                'status': StatusType.ACTIVE
            },
            {
                'label': 'Performance',
                'value': self.metrics['performance_score'],
                'unit': '%',
                'precision': 1,
                'status': StatusType.ACTIVE
            },
            {
                'label': 'Sessions Actives',
                'value': self.metrics['active_sessions'],
                'unit': '',
                'precision': 0,
                'status': StatusType.INACTIVE
            }
        ]

class DashboardViewMaritime(QWidget):
    """Vue principale du tableau de bord CHNeoWave avec design maritime industriel 2025 - Version Simplifiée"""
    
    # Signaux
    navigation_requested = pyqtSignal(str)
    theme_changed = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Gestionnaire de métriques
        self.metrics_manager = DashboardMetrics()
        
        # Indicateurs KPI
        self.kpi_indicators = []
        
        # Configuration de l'interface
        self.setup_ui()
        self.load_maritime_stylesheet()
        
        # Timer pour mise à jour des métriques
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_metrics)
        self.update_timer.start(5000)  # Mise à jour toutes les 5 secondes
    
    def setup_ui(self):
        """Configuration de l'interface utilisateur"""
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(
            MaritimeTheme.SPACE_LG,
            MaritimeTheme.SPACE_LG,
            MaritimeTheme.SPACE_LG,
            MaritimeTheme.SPACE_LG
        )
        main_layout.setSpacing(MaritimeTheme.SPACE_MD)
        
        # Zone de défilement
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Widget de contenu
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(MaritimeTheme.SPACE_LG)
        
        # En-tête maritime
        header = self.create_maritime_header()
        content_layout.addWidget(header)
        
        # Vue d'ensemble du statut
        overview = self.create_status_overview()
        content_layout.addWidget(overview)
        
        # Grille KPI
        kpi_grid = self.create_kpi_grid()
        content_layout.addWidget(kpi_grid)
        
        # Section monitoring
        monitoring = self.create_monitoring_section()
        content_layout.addWidget(monitoring)
        
        # Espacement flexible
        content_layout.addStretch()
        
        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)
    
    def create_maritime_header(self) -> QWidget:
        """Création de l'en-tête maritime"""
        header = QFrame()
        header.setObjectName("maritimeHeader")
        header.setStyleSheet(f"""
            QFrame#maritimeHeader {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {MaritimeTheme.OCEAN_DEEP},
                    stop:1 {MaritimeTheme.HARBOR_BLUE});
                border-radius: 10px;
                padding: 20px;
            }}
        """)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(
            MaritimeTheme.SPACE_LG,
            MaritimeTheme.SPACE_MD,
            MaritimeTheme.SPACE_LG,
            MaritimeTheme.SPACE_MD
        )
        
        # Titre principal
        title_label = QLabel("CHNeoWave - Tableau de Bord Maritime")
        title_label.setObjectName("mainTitle")
        title_font = QFont("Segoe UI", 24, QFont.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet(f"color: {MaritimeTheme.FOAM_WHITE};")
        
        # Statuts système
        status_container = QFrame()
        status_layout = QHBoxLayout(status_container)
        status_layout.setSpacing(MaritimeTheme.SPACE_SM)
        
        # Création des balises de statut (simplifiées)
        system_beacon = QLabel("Système: Actif")
        system_beacon.setObjectName("systemBeacon")
        system_beacon.setStyleSheet(f"""
            QLabel {{
                color: {MaritimeTheme.FOAM_WHITE};
                background: {MaritimeTheme.TIDAL_CYAN};
                padding: 5px 10px;
                border-radius: 5px;
                font-weight: bold;
            }}
        """)
        
        acquisition_beacon = QLabel("Acquisition: Inactif")
        acquisition_beacon.setObjectName("acquisitionBeacon")
        acquisition_beacon.setStyleSheet(f"""
            QLabel {{
                color: {MaritimeTheme.FOAM_WHITE};
                background: {MaritimeTheme.STORM_GRAY};
                padding: 5px 10px;
                border-radius: 5px;
                font-weight: bold;
            }}
        """)
        
        network_beacon = QLabel("Réseau: Actif")
        network_beacon.setObjectName("networkBeacon")
        network_beacon.setStyleSheet(f"""
            QLabel {{
                color: {MaritimeTheme.FOAM_WHITE};
                background: {MaritimeTheme.TIDAL_CYAN};
                padding: 5px 10px;
                border-radius: 5px;
                font-weight: bold;
            }}
        """)
        
        status_layout.addWidget(system_beacon)
        status_layout.addWidget(acquisition_beacon)
        status_layout.addWidget(network_beacon)
        status_layout.addStretch()
        
        # Assemblage de l'en-tête
        layout.addWidget(title_label, 2)
        layout.addWidget(status_container, 1)
        
        return header
    
    def create_status_overview(self) -> QWidget:
        """Création de l'aperçu du statut"""
        overview = QFrame()
        overview.setObjectName("statusOverview")
        overview.setStyleSheet(f"""
            QFrame#statusOverview {{
                background: {MaritimeTheme.FOAM_WHITE};
                border: 2px solid {MaritimeTheme.HARBOR_BLUE};
                border-radius: 10px;
            }}
        """)
        
        layout = QVBoxLayout(overview)
        layout.setContentsMargins(
            MaritimeTheme.SPACE_LG,
            MaritimeTheme.SPACE_MD,
            MaritimeTheme.SPACE_LG,
            MaritimeTheme.SPACE_MD
        )
        
        # Titre de section
        title = QLabel("Vue d'Ensemble Système")
        title.setObjectName("sectionTitle")
        title.setStyleSheet(f"""
            QLabel {{
                color: {MaritimeTheme.OCEAN_DEEP};
                font-size: 18px;
                font-weight: bold;
                margin-bottom: 10px;
            }}
        """)
        layout.addWidget(title)
        
        # Informations système
        info_label = QLabel("Système opérationnel - Toutes les fonctions disponibles")
        info_label.setStyleSheet(f"""
            QLabel {{
                color: {MaritimeTheme.STORM_GRAY};
                font-size: 14px;
            }}
        """)
        layout.addWidget(info_label)
        
        return overview
    
    def create_kpi_grid(self) -> QWidget:
        """Création de la grille KPI"""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(MaritimeTheme.SPACE_MD)
        
        # Titre de section
        title = QLabel("Indicateurs de Performance Maritime")
        title.setObjectName("sectionTitle")
        title.setStyleSheet(f"""
            QLabel {{
                color: {MaritimeTheme.OCEAN_DEEP};
                font-size: 18px;
                font-weight: bold;
                margin-bottom: 10px;
            }}
        """)
        layout.addWidget(title)
        
        # Grille KPI
        grid = QGridLayout()
        grid.setSpacing(MaritimeTheme.SPACE_MD)
        
        # Données KPI
        kpi_data = self.metrics_manager.get_kpi_data()
        
        # Création des indicateurs KPI
        for i, kpi in enumerate(kpi_data):
            indicator = self.create_kpi_indicator(kpi)
            row = i // 3
            col = i % 3
            grid.addWidget(indicator, row, col)
            self.kpi_indicators.append(indicator)
        
        layout.addLayout(grid)
        
        return container
    
    def create_kpi_indicator(self, kpi_data: Dict) -> QFrame:
        """Création d'un indicateur KPI"""
        indicator = QFrame()
        indicator.setObjectName("kpiIndicator")
        indicator.setStyleSheet(f"""
            QFrame#kpiIndicator {{
                background: {MaritimeTheme.FOAM_WHITE};
                border: 2px solid {MaritimeTheme.HARBOR_BLUE};
                border-radius: 8px;
                padding: 15px;
            }}
        """)
        
        layout = QVBoxLayout(indicator)
        layout.setSpacing(MaritimeTheme.SPACE_SM)
        
        # Label
        label = QLabel(kpi_data['label'])
        label.setStyleSheet(f"""
            QLabel {{
                color: {MaritimeTheme.OCEAN_DEEP};
                font-size: 12px;
                font-weight: bold;
            }}
        """)
        layout.addWidget(label)
        
        # Valeur
        value = QLabel(f"{kpi_data['value']}{kpi_data['unit']}")
        value.setStyleSheet(f"""
            QLabel {{
                color: {MaritimeTheme.HARBOR_BLUE};
                font-size: 20px;
                font-weight: bold;
            }}
        """)
        layout.addWidget(value)
        
        return indicator
    
    def create_monitoring_section(self) -> QWidget:
        """Création de la section monitoring"""
        monitoring = QFrame()
        monitoring.setObjectName("monitoringSection")
        monitoring.setStyleSheet(f"""
            QFrame#monitoringSection {{
                background: {MaritimeTheme.FOAM_WHITE};
                border: 2px solid {MaritimeTheme.HARBOR_BLUE};
                border-radius: 10px;
            }}
        """)
        
        layout = QVBoxLayout(monitoring)
        layout.setContentsMargins(
            MaritimeTheme.SPACE_LG,
            MaritimeTheme.SPACE_MD,
            MaritimeTheme.SPACE_LG,
            MaritimeTheme.SPACE_MD
        )
        
        # Titre de section
        title = QLabel("Monitoring en Temps Réel")
        title.setObjectName("sectionTitle")
        title.setStyleSheet(f"""
            QLabel {{
                color: {MaritimeTheme.OCEAN_DEEP};
                font-size: 18px;
                font-weight: bold;
                margin-bottom: 10px;
            }}
        """)
        layout.addWidget(title)
        
        # Informations monitoring
        info_label = QLabel("Système de monitoring opérationnel - Données en temps réel disponibles")
        info_label.setStyleSheet(f"""
            QLabel {{
                color: {MaritimeTheme.STORM_GRAY};
                font-size: 14px;
            }}
        """)
        layout.addWidget(info_label)
        
        return monitoring
    
    def load_maritime_stylesheet(self):
        """Charge la feuille de style maritime"""
        self.setStyleSheet(f"""
            QWidget {{
                background: {MaritimeTheme.FOAM_WHITE};
                color: {MaritimeTheme.OCEAN_DEEP};
                font-family: 'Segoe UI', Arial, sans-serif;
            }}
            
            QScrollArea {{
                border: none;
                background: transparent;
            }}
            
            QScrollBar:vertical {{
                background: {MaritimeTheme.STORM_GRAY};
                width: 12px;
                border-radius: 6px;
            }}
            
            QScrollBar::handle:vertical {{
                background: {MaritimeTheme.HARBOR_BLUE};
                border-radius: 6px;
                min-height: 20px;
            }}
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
        """)
    
    def update_metrics(self):
        """Met à jour les métriques"""
        # Simulation de mise à jour des métriques
        self.metrics_manager.update_metric('active_sessions', 
                                         self.metrics_manager.get_metric('active_sessions') + 1)
        
        # Mise à jour des indicateurs KPI
        kpi_data = self.metrics_manager.get_kpi_data()
        for i, indicator in enumerate(self.kpi_indicators):
            if i < len(kpi_data):
                kpi = kpi_data[i]
                value_label = indicator.findChild(QLabel, "")
                if value_label:
                    value_label.setText(f"{kpi['value']}{kpi['unit']}")
    
    def showEvent(self, event):
        """Événement d'affichage"""
        super().showEvent(event)
        self.update_metrics()
    
    def hideEvent(self, event):
        """Événement de masquage"""
        super().hideEvent(event)
        try:
            if self.update_timer:
                self.update_timer.stop()
        except RuntimeError:
            pass
