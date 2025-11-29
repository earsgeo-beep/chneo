#!/usr/bin/env python3
"""
Vue du tableau de bord principal (Dashboard) CHNeoWave - Version Golden Ratio.

Implémente le système de design Golden Ratio avec palette maritime professionnelle.

Auteur: Architecte Logiciel en Chef (ALC)
Date: 2024-12-20
Version: 1.1.0-golden
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton, 
    QGraphicsOpacityEffect, QSplitter, QGridLayout, QScrollArea
)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, Signal, QTimer
from PySide6.QtGui import QPalette, QColor, QFont, QPainter, QPen, QLinearGradient

from hrneowave.gui.layouts.fibonacci_grid_mixin import FibonacciGridMixin
from hrneowave.gui.components.phi_card import PhiCard
from hrneowave.gui.components.performance_widget import PerformanceWidget, create_memory_collector, create_thread_collector
from hrneowave.core.performance_monitor import PerformanceMonitor
from typing import List

# Constantes Golden Ratio
PHI = 1.618
PHI_INVERSE = 1 / PHI  # ≈ 0.618

# Palette Maritime Professionnelle
class MaritimePalette:
    """Palette de couleurs maritime professionnelle."""
    
    # Couleurs primaires
    HARBOR_BLUE = "#00558c"      # Bleu océan professionnel
    STEEL_BLUE = "#0478b9"       # Bleu métallique
    FROST_WHITE = "#d3edf9"      # Blanc glacé
    
    # Mode clair (défaut)
    LIGHT_BACKGROUND = "#FAFBFC"  # Fond principal
    LIGHT_SURFACE = "#FFFFFF"     # Surface
    LIGHT_TEXT = "#0A1929"        # Texte
    
    # Mode sombre (optionnel)
    DARK_BACKGROUND = "#0A1929"   # Fond principal
    DARK_SURFACE = "#1A1F2E"      # Surface
    DARK_TEXT = "rgba(255,255,255,0.87)"  # Texte
    
    # Couleurs d'état
    SUCCESS = "#2e7d32"           # Vert maritime
    WARNING = "#f57c00"           # Orange maritime
    ERROR = "#d32f2f"             # Rouge maritime
    INFO = STEEL_BLUE             # Bleu info

class ModernFFTWidget(QWidget):
    """Widget FFT moderne avec design maritime et Golden Ratio."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(int(400 * PHI), 300)  # Proportions Golden Ratio
        self.freqs = []
        self.amps = []
        self._setup_style()
    
    def _setup_style(self):
        """Configure le style maritime moderne."""
        self.setStyleSheet(f"""
            ModernFFTWidget {{
                background-color: {MaritimePalette.LIGHT_SURFACE};
                border: 1px solid {MaritimePalette.HARBOR_BLUE};
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0,85,140,0.1);
            }}
        """)
    
    def update_data(self, freqs, amps):
        """Met à jour les données FFT."""
        self.freqs = freqs if freqs else []
        self.amps = amps if amps else []
        self.update()
    
    def paintEvent(self, event):
        """Dessine le graphique FFT avec style maritime moderne."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Fond avec gradient subtil
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor(MaritimePalette.LIGHT_SURFACE))
        gradient.setColorAt(1, QColor(MaritimePalette.FROST_WHITE))
        painter.fillRect(self.rect(), gradient)
        
        # Titre avec police maritime
        painter.setPen(QPen(QColor(MaritimePalette.HARBOR_BLUE)))
        font = QFont("Segoe UI", 14, QFont.Bold)
        painter.setFont(font)
        painter.drawText(21, 34, "Analyse Spectrale Temps Réel")  # Padding Fibonacci (21, 34)
        
        # Labels des axes
        painter.setFont(QFont("Segoe UI", 10))
        painter.setPen(QPen(QColor(MaritimePalette.LIGHT_TEXT)))
        painter.drawText(21, self.height() - 13, "Fréquence (Hz)")
        
        # Label Y avec rotation
        painter.save()
        painter.translate(13, self.height() // 2)
        painter.rotate(-90)
        painter.drawText(0, 0, "Amplitude")
        painter.restore()
        
        # Dessiner les données si disponibles
        if self.freqs and self.amps and len(self.freqs) == len(self.amps):
            self._draw_maritime_fft_data(painter)
        else:
            # Message "Pas de données" avec style maritime
            painter.setPen(QPen(QColor(MaritimePalette.STEEL_BLUE)))
            painter.setFont(QFont("Segoe UI", 11))
            painter.drawText(self.width() // 2 - 80, self.height() // 2, "En attente de données...")
    
    def _draw_maritime_fft_data(self, painter):
        """Dessine les données FFT avec style maritime."""
        if not self.freqs or not self.amps:
            return
        
        # Marges basées sur Fibonacci
        margin_left = 55
        margin_right = 21
        margin_top = 55
        margin_bottom = 34
        
        plot_width = self.width() - margin_left - margin_right
        plot_height = self.height() - margin_top - margin_bottom
        
        if plot_width <= 0 or plot_height <= 0:
            return
        
        # Normalisation des données
        min_freq = min(self.freqs)
        max_freq = max(self.freqs)
        min_amp = min(self.amps)
        max_amp = max(self.amps)
        
        if max_freq == min_freq or max_amp == min_amp:
            return
        
        # Grille de fond maritime
        painter.setPen(QPen(QColor(MaritimePalette.FROST_WHITE), 1))
        for i in range(5):
            y = margin_top + i * plot_height / 4
            painter.drawLine(margin_left, int(y), margin_left + plot_width, int(y))
        
        # Courbe principale avec gradient maritime
        painter.setPen(QPen(QColor(MaritimePalette.STEEL_BLUE), 3))
        
        points = []
        for freq, amp in zip(self.freqs, self.amps):
            x = margin_left + (freq - min_freq) / (max_freq - min_freq) * plot_width
            y = margin_top + plot_height - (amp - min_amp) / (max_amp - min_amp) * plot_height
            points.append((x, y))
        
        # Dessiner la courbe avec transitions fluides
        for i in range(len(points) - 1):
            x1, y1 = points[i]
            x2, y2 = points[i + 1]
            painter.drawLine(int(x1), int(y1), int(x2), int(y2))

class GoldenKPICard(QWidget):
    """Carte KPI avec proportions Golden Ratio et design maritime."""
    
    def __init__(self, title: str, value: str = "0", unit: str = "", parent=None):
        super().__init__(parent)
        self.title = title
        self.value = value
        self.unit = unit
        self._setup_ui()
        self._setup_style()
    
    def _setup_ui(self):
        """Configure l'interface avec proportions Golden Ratio."""
        layout = QVBoxLayout(self)
        
        # Padding basé sur Fibonacci (8, 13, 21)
        layout.setContentsMargins(13, 13, 13, 13)
        layout.setSpacing(8)
        
        # Titre
        self.title_label = QLabel(self.title)
        self.title_label.setObjectName("KPITitle")
        layout.addWidget(self.title_label)
        
        # Valeur principale
        self.value_label = QLabel(self.value + self.unit)
        self.value_label.setObjectName("KPIValue")
        layout.addWidget(self.value_label)
        
        # Taille basée sur Golden Ratio
        base_width = 144  # Fibonacci
        base_height = int(base_width / PHI)
        self.setFixedSize(base_width, base_height)
    
    def _setup_style(self):
        """Configure le style maritime moderne."""
        self.setStyleSheet(f"""
            GoldenKPICard {{
                background-color: {MaritimePalette.LIGHT_SURFACE};
                border: 1px solid {MaritimePalette.FROST_WHITE};
                border-radius: 8px;
            }}
            
            GoldenKPICard:hover {{
                border-color: {MaritimePalette.STEEL_BLUE};
                background-color: {MaritimePalette.FROST_WHITE};
            }}
            
            QLabel#KPITitle {{
                color: {MaritimePalette.HARBOR_BLUE};
                font: 10px "Segoe UI";
                font-weight: 500;
                margin-bottom: 5px;
            }}
            
            QLabel#KPIValue {{
                color: {MaritimePalette.LIGHT_TEXT};
                font: bold 18px "Segoe UI";
                font-weight: 700;
            }}
        """)
    
    def update_value(self, value: str):
        """Met à jour la valeur affichée."""
        self.value = value
        self.value_label.setText(value + self.unit)

class DashboardViewGolden(QWidget):
    """Dashboard principal avec design Golden Ratio et palette maritime."""
    
    acquisitionRequested = Signal()
    
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.setObjectName("DashboardViewGolden")
        
        # Widgets principaux
        self.fft_widget = None
        self.performance_monitor = PerformanceMonitor()
        self.performance_widget = None
        
        # Cartes KPI
        self.kpi_cards = {}
        
        self._setup_ui()
        self._setup_style()
        self._setup_performance_monitoring()
        self._setup_animations()
    
    def _setup_ui(self):
        """Configure l'interface avec Golden Ratio (1:1.618)."""
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(21, 21, 21, 21)  # Padding Fibonacci
        main_layout.setSpacing(21)
        
        # Splitter principal avec Golden Ratio
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # === ZONE KPI (Gauche) - Proportion 1 ===
        kpi_zone = self._create_kpi_zone()
        
        # === ZONE GRAPHIQUE (Droite) - Proportion φ ===
        graph_zone = self._create_graph_zone()
        
        # Ajout au splitter avec proportions Golden Ratio
        splitter.addWidget(kpi_zone)
        splitter.addWidget(graph_zone)
        
        # Application du Golden Ratio : 1 : 1.618
        total_width = 1000  # Largeur de référence
        left_width = int(total_width / (1 + PHI))  # ≈ 382
        right_width = int(total_width * PHI / (1 + PHI))  # ≈ 618
        splitter.setSizes([left_width, right_width])
    
    def _create_kpi_zone(self) -> QWidget:
        """Crée la zone KPI avec navigation verticale optimisée."""
        kpi_container = QWidget()
        kpi_layout = QVBoxLayout(kpi_container)
        kpi_layout.setSpacing(13)  # Espacement Fibonacci
        
        # Titre de section
        section_title = QLabel("Indicateurs de Performance")
        section_title.setObjectName("SectionTitle")
        kpi_layout.addWidget(section_title)
        
        # Grille de cartes KPI avec proportions φ
        kpi_grid = QGridLayout()
        kpi_grid.setSpacing(13)
        
        # Création des cartes KPI
        self.kpi_cards = {
            'cpu': GoldenKPICard("Charge CPU", "0", "%"),
            'memory': GoldenKPICard("Mémoire", "0", "%"),
            'disk': GoldenKPICard("Disque", "0", "%"),
            'threads': GoldenKPICard("Threads", "0"),
            'uptime': GoldenKPICard("Temps", "0", "s"),
            'sensors': GoldenKPICard("Capteurs", "0")
        }
        
        # Disposition en grille 2x3 (Golden Ratio)
        positions = [(0,0), (0,1), (1,0), (1,1), (2,0), (2,1)]
        for (card_key, card), (row, col) in zip(self.kpi_cards.items(), positions):
            kpi_grid.addWidget(card, row, col)
        
        kpi_layout.addLayout(kpi_grid)
        
        # Espace flexible
        kpi_layout.addStretch()
        
        # Bouton d'action principal
        self.primary_button = QPushButton("Démarrer l'Acquisition")
        self.primary_button.setObjectName("PrimaryButton")
        self.primary_button.clicked.connect(self.acquisitionRequested)
        kpi_layout.addWidget(self.primary_button)
        
        return kpi_container
    
    def _create_graph_zone(self) -> QWidget:
        """Crée la zone graphique avec monitoring intégré."""
        graph_container = QWidget()
        graph_layout = QVBoxLayout(graph_container)
        graph_layout.setSpacing(13)
        
        # Titre de section
        section_title = QLabel("Analyse en Temps Réel")
        section_title.setObjectName("SectionTitle")
        graph_layout.addWidget(section_title)
        
        # Splitter vertical pour FFT et monitoring
        vertical_splitter = QSplitter(Qt.Vertical)
        
        # Container FFT
        self.fft_container = QWidget()
        self.fft_container_layout = QVBoxLayout(self.fft_container)
        self.fft_container_layout.setContentsMargins(0, 0, 0, 0)
        
        # Container monitoring
        self.monitoring_container = QWidget()
        self.monitoring_container_layout = QVBoxLayout(self.monitoring_container)
        self.monitoring_container_layout.setContentsMargins(0, 0, 0, 0)
        
        vertical_splitter.addWidget(self.fft_container)
        vertical_splitter.addWidget(self.monitoring_container)
        
        # Proportions Golden Ratio pour les sous-zones
        fft_height = int(400 * PHI)  # Zone principale
        monitoring_height = int(400 * PHI_INVERSE)  # Zone secondaire
        vertical_splitter.setSizes([fft_height, monitoring_height])
        
        graph_layout.addWidget(vertical_splitter)
        
        return graph_container
    
    def _setup_style(self):
        """Configure le style maritime moderne global."""
        self.setStyleSheet(f"""
            DashboardViewGolden {{
                background-color: {MaritimePalette.LIGHT_BACKGROUND};
                color: {MaritimePalette.LIGHT_TEXT};
            }}
            
            QLabel#SectionTitle {{
                color: {MaritimePalette.HARBOR_BLUE};
                font: bold 16px "Segoe UI";
                font-weight: 600;
                margin-bottom: 8px;
                padding-bottom: 5px;
                border-bottom: 2px solid {MaritimePalette.FROST_WHITE};
            }}
            
            QPushButton#PrimaryButton {{
                background-color: {MaritimePalette.HARBOR_BLUE};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 13px 21px;
                font: bold 14px "Segoe UI";
                font-weight: 600;
                min-height: 34px;
            }}
            
            QPushButton#PrimaryButton:hover {{
                background-color: {MaritimePalette.STEEL_BLUE};
            }}
            
            QPushButton#PrimaryButton:pressed {{
                background-color: {MaritimePalette.HARBOR_BLUE};
            }}
            
            QSplitter::handle {{
                background-color: {MaritimePalette.FROST_WHITE};
                width: 2px;
                height: 2px;
            }}
            
            QSplitter::handle:hover {{
                background-color: {MaritimePalette.STEEL_BLUE};
            }}
        """)
    
    def _setup_animations(self):
        """Configure les animations d'entrée en cascade."""
        # Animation des cartes KPI avec délai en cascade
        for i, card in enumerate(self.kpi_cards.values()):
            effect = QGraphicsOpacityEffect(card)
            card.setGraphicsEffect(effect)
            
            animation = QPropertyAnimation(effect, b"opacity")
            animation.setDuration(400)  # 400ms par carte
            animation.setStartValue(0.0)
            animation.setEndValue(1.0)
            animation.setEasingCurve(QEasingCurve.OutCubic)
            
            # Délai en cascade basé sur Fibonacci
            QTimer.singleShot(i * 89, animation.start)  # 89ms de délai
    
    def _setup_performance_monitoring(self):
        """Configure le monitoring de performance avancé."""
        # Configuration des seuils avec palette maritime
        self.performance_monitor.thresholds.cpu_warning = 70.0
        self.performance_monitor.thresholds.cpu_critical = 90.0
        self.performance_monitor.thresholds.memory_warning = 75.0
        self.performance_monitor.thresholds.memory_critical = 90.0
        
        # Connexion des signaux
        self.performance_monitor.metrics_updated.connect(self._update_kpis_from_monitor)
        
        # Démarrage du monitoring
        self.performance_monitor.start_monitoring()
    
    def showEvent(self, event):
        """Initialisation différée des widgets lourds."""
        super().showEvent(event)
        
        # Création du widget FFT moderne
        if self.fft_widget is None:
            self.fft_widget = ModernFFTWidget(parent=self)
            self.fft_container_layout.addWidget(self.fft_widget)
        
        # Création du widget de monitoring
        if self.performance_widget is None:
            self.performance_widget = PerformanceWidget(parent=self)
            # Les collecteurs personnalisés doivent être des fonctions qui retournent PerformanceMetric
            self.performance_widget.add_custom_metric("python_memory", lambda: create_memory_collector())
            self.performance_widget.add_custom_metric("active_threads", lambda: create_thread_collector())
            self.monitoring_container_layout.addWidget(self.performance_widget)
            self.performance_widget.start_monitoring()
    
    def _update_kpis_from_monitor(self, metrics):
        """Met à jour les KPIs depuis le monitoring."""
        if hasattr(metrics, 'cpu_usage'):
            self.kpi_cards['cpu'].update_value(f"{metrics.cpu_usage:.1f}")
        
        if hasattr(metrics, 'memory_used_mb') and hasattr(metrics, 'memory_available_mb'):
            total = metrics.memory_used_mb + metrics.memory_available_mb
            percent = (metrics.memory_used_mb / total) * 100 if total > 0 else 0
            self.kpi_cards['memory'].update_value(f"{percent:.1f}")
        
        if hasattr(metrics, 'disk_used_gb') and hasattr(metrics, 'disk_total_gb'):
            percent = (metrics.disk_used_gb / metrics.disk_total_gb) * 100 if metrics.disk_total_gb > 0 else 0
            self.kpi_cards['disk'].update_value(f"{percent:.1f}")
        
        if hasattr(metrics, 'active_threads'):
            self.kpi_cards['threads'].update_value(str(metrics.active_threads))
    
    def update_fft_plot(self, freqs, amps):
        """Met à jour le graphique FFT."""
        if self.fft_widget:
            self.fft_widget.update_data(freqs, amps)
    
    def closeEvent(self, event):
        """Nettoyage lors de la fermeture."""
        if hasattr(self, 'performance_monitor'):
            self.performance_monitor.stop_monitoring()
        
        if hasattr(self, 'performance_widget') and self.performance_widget:
            self.performance_widget.stop_monitoring()
        
        super().closeEvent(event)