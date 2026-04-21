# -*- coding: utf-8 -*-
"""
CHNeoWave GUI Widgets - Maritime Theme 2025
Composants d'interface utilisateur avec design maritime et Golden Ratio
"""

from .kpi_card import KPICard
from .main_sidebar import MainSidebar

__all__ = [
    'KPICard',
    'MainSidebar',
]

# Version du module widgets
__version__ = '1.0.0'

# Métadonnées du design
DESIGN_INFO = {
    'theme': 'Maritime PRO 2025',
    'golden_ratio': 1.618,
    'fibonacci_spacing': [8, 13, 21, 34, 55, 89],
    'color_palette': {
        'deep_navy': '#0A1929',
        'harbor_blue': '#055080', 
        'steel_blue': '#2B79B6',
        'tidal_cyan': '#00ACC1',
        'foam_white': '#F5FBFF',
        'storm_gray': '#445868',
        'coral_alert': '#FF6B47'
    },
    'typography': {
        'font_family': 'Inter',
        'h1_size': 34,
        'h2_size': 21,
        'body_size': 13
    }
}
