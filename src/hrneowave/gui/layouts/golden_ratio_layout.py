# -*- coding: utf-8 -*-
"""
Layout basé sur le nombre d'or - Proportions harmonieuses
Implémente des layouts utilisant le ratio doré (φ ≈ 1.618) pour une interface équilibrée

Auteur: Architecte Logiciel en Chef (ALC)
Date: 2025-01-26
Version: 1.1.0
"""

from PySide6.QtWidgets import QLayout, QLayoutItem, QWidget, QSizePolicy
from PySide6.QtCore import Qt, QRect, QSize, QPoint
from typing import List, Optional
import math


class GoldenRatioLayout(QLayout):
    """
    Layout basé sur le nombre d'or pour des proportions harmonieuses
    """
    
    # Constante du nombre d'or
    PHI = (1 + math.sqrt(5)) / 2  # ≈ 1.618
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Liste des éléments du layout
        self._items: List[QLayoutItem] = []
        
        # Configuration par défaut
        self._spacing = 10
        self._orientation = Qt.Horizontal
        self._golden_sections = []  # Sections avec proportions dorées
        
        # Marges par défaut
        self.setContentsMargins(16, 16, 16, 16)
    
    def addItem(self, item: QLayoutItem):
        """Ajoute un élément au layout"""
        self._items.append(item)
        self.invalidate()
    
    def addWidget(self, widget: QWidget, ratio_type: str = "auto"):
        """Ajoute un widget avec un type de ratio spécifique"""
        from PySide6.QtWidgets import QWidgetItem
        
        item = QWidgetItem(widget)
        
        # Stocker le type de ratio
        item.ratio_type = ratio_type
        
        self.addItem(item)
        return item
    
    def count(self) -> int:
        """Retourne le nombre d'éléments"""
        return len(self._items)
    
    def itemAt(self, index: int) -> Optional[QLayoutItem]:
        """Retourne l'élément à l'index donné"""
        if 0 <= index < len(self._items):
            return self._items[index]
        return None
    
    def takeAt(self, index: int) -> Optional[QLayoutItem]:
        """Retire et retourne l'élément à l'index donné"""
        if 0 <= index < len(self._items):
            item = self._items.pop(index)
            self.invalidate()
            return item
        return None
    
    def setSpacing(self, spacing: int):
        """Définit l'espacement entre les éléments"""
        self._spacing = spacing
        self.invalidate()
    
    def spacing(self) -> int:
        """Retourne l'espacement actuel"""
        return self._spacing
    
    def setOrientation(self, orientation: Qt.Orientation):
        """Définit l'orientation du layout"""
        self._orientation = orientation
        self.invalidate()
    
    def orientation(self) -> Qt.Orientation:
        """Retourne l'orientation actuelle"""
        return self._orientation
    
    def sizeHint(self) -> QSize:
        """Calcule la taille recommandée"""
        valid_items = [
            item for item in self._items
            if item is not None and (not hasattr(item, "widget") or item.widget() is not None)
        ]
        if not valid_items:
            return QSize(0, 0)
        
        total_width = 0
        total_height = 0
        
        if self._orientation == Qt.Horizontal:
            max_height = 0
            for item in valid_items:
                try:
                    size = item.sizeHint()
                    if size.isValid():
                        total_width += size.width()
                        max_height = max(max_height, size.height())
                except Exception:
                    continue
            
            total_width += self._spacing * max(0, len(valid_items) - 1)
            total_height = max_height
        else:
            max_width = 0
            for item in valid_items:
                try:
                    size = item.sizeHint()
                    if size.isValid():
                        total_height += size.height()
                        max_width = max(max_width, size.width())
                except Exception:
                    continue
            
            total_height += self._spacing * max(0, len(valid_items) - 1)
            total_width = max_width
        
        # Ajouter les marges
        margins = self.contentsMargins()
        total_width += margins.left() + margins.right()
        total_height += margins.top() + margins.bottom()
        
        return QSize(max(0, total_width), max(0, total_height))
    
    def minimumSize(self) -> QSize:
        """Calcule la taille minimale"""
        valid_items = [
            item for item in self._items
            if item is not None and (not hasattr(item, "widget") or item.widget() is not None)
        ]
        if not valid_items:
            return QSize(0, 0)
        
        total_width = 0
        total_height = 0
        
        if self._orientation == Qt.Horizontal:
            max_height = 0
            for item in valid_items:
                try:
                    size = item.minimumSize()
                    if size.isValid():
                        total_width += size.width()
                        max_height = max(max_height, size.height())
                except Exception:
                    continue
            
            total_width += self._spacing * max(0, len(valid_items) - 1)
            total_height = max_height
        else:
            max_width = 0
            for item in valid_items:
                try:
                    size = item.minimumSize()
                    if size.isValid():
                        total_height += size.height()
                        max_width = max(max_width, size.width())
                except Exception:
                    continue
            
            total_height += self._spacing * max(0, len(valid_items) - 1)
            total_width = max_width
        
        # Ajouter les marges
        margins = self.contentsMargins()
        total_width += margins.left() + margins.right()
        total_height += margins.top() + margins.bottom()
        
        return QSize(max(0, total_width), max(0, total_height))
    
    def setGeometry(self, rect: QRect):
        """Positionne les éléments selon les proportions dorées"""
        super().setGeometry(rect)
        
        if not self._items:
            return
        
        # Zone de contenu (sans les marges)
        margins = self.contentsMargins()
        content_rect = rect.adjusted(
            margins.left(), margins.top(),
            -margins.right(), -margins.bottom()
        )
        
        # Calculer les proportions dorées
        self._calculate_golden_sections(content_rect)
        
        # Positionner les éléments
        self._position_items(content_rect)
    
    def _calculate_golden_sections(self, rect: QRect):
        """Calcule les sections basées sur le nombre d'or"""
        self._golden_sections = []
        
        if not self._items:
            return
        
        if self._orientation == Qt.Horizontal:
            self._calculate_horizontal_sections(rect)
        else:
            self._calculate_vertical_sections(rect)
    
    def _calculate_horizontal_sections(self, rect: QRect):
        """Calcule les sections horizontales"""
        total_width = rect.width() - self._spacing * (len(self._items) - 1)
        
        # Analyser les types de ratio des éléments
        ratio_weights = []
        for item in self._items:
            ratio_type = getattr(item, 'ratio_type', 'auto')
            
            if ratio_type == 'golden_major':
                # Section majeure (φ)
                ratio_weights.append(self.PHI)
            elif ratio_type == 'golden_minor':
                # Section mineure (1)
                ratio_weights.append(1.0)
            elif ratio_type == 'golden_square':
                # Section carrée basée sur φ
                ratio_weights.append(1.0)
            else:
                # Auto : calculer selon la taille préférée
                preferred_width = item.sizeHint().width()
                ratio_weights.append(preferred_width / 100.0)  # Normalisation
        
        # Normaliser les poids
        total_weight = sum(ratio_weights)
        if total_weight > 0:
            ratio_weights = [w / total_weight for w in ratio_weights]
        else:
            ratio_weights = [1.0 / len(self._items)] * len(self._items)
        
        # Calculer les largeurs
        x = rect.x()
        for i, weight in enumerate(ratio_weights):
            width = int(total_width * weight)
            section_rect = QRect(x, rect.y(), width, rect.height())
            self._golden_sections.append(section_rect)
            x += width + self._spacing
    
    def _calculate_vertical_sections(self, rect: QRect):
        """Calcule les sections verticales"""
        total_height = rect.height() - self._spacing * (len(self._items) - 1)
        
        # Analyser les types de ratio des éléments
        ratio_weights = []
        for item in self._items:
            ratio_type = getattr(item, 'ratio_type', 'auto')
            
            if ratio_type == 'golden_major':
                # Section majeure (φ)
                ratio_weights.append(self.PHI)
            elif ratio_type == 'golden_minor':
                # Section mineure (1)
                ratio_weights.append(1.0)
            elif ratio_type == 'golden_square':
                # Section carrée basée sur φ
                ratio_weights.append(1.0)
            else:
                # Auto : calculer selon la taille préférée
                preferred_height = item.sizeHint().height()
                ratio_weights.append(preferred_height / 100.0)  # Normalisation
        
        # Normaliser les poids
        total_weight = sum(ratio_weights)
        if total_weight > 0:
            ratio_weights = [w / total_weight for w in ratio_weights]
        else:
            ratio_weights = [1.0 / len(self._items)] * len(self._items)
        
        # Calculer les hauteurs
        y = rect.y()
        for i, weight in enumerate(ratio_weights):
            height = int(total_height * weight)
            section_rect = QRect(rect.x(), y, rect.width(), height)
            self._golden_sections.append(section_rect)
            y += height + self._spacing
    
    def _position_items(self, rect: QRect):
        """Positionne les éléments dans leurs sections"""
        for i, item in enumerate(self._items):
            if i < len(self._golden_sections):
                section_rect = self._golden_sections[i]
                item.setGeometry(section_rect)
    
    def expandingDirections(self) -> Qt.Orientations:
        """Retourne les directions d'expansion"""
        return Qt.Horizontal | Qt.Vertical
    
    def hasHeightForWidth(self) -> bool:
        """Indique si le layout a une hauteur dépendante de la largeur"""
        return False
    
    def invalidate(self):
        """Invalide le layout"""
        self._golden_sections = []
        super().invalidate()


class GoldenRatioGridLayout(QLayout):
    """
    Layout en grille basé sur le nombre d'or
    """
    
    PHI = (1 + math.sqrt(5)) / 2
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self._items = []
        self._grid_items = {}  # {(row, col): item}
        self._row_count = 0
        self._col_count = 0
        self._spacing = 10
        
        self.setContentsMargins(16, 16, 16, 16)
    
    def addWidget(self, widget: QWidget, row: int, col: int, 
                  row_span: int = 1, col_span: int = 1, 
                  ratio_type: str = "auto"):
        """Ajoute un widget à la grille"""
        item = QLayoutItem()
        item.widget = lambda: widget
        item.sizeHint = lambda: widget.sizeHint()
        item.minimumSize = lambda: widget.minimumSizeHint()
        item.maximumSize = lambda: widget.maximumSize()
        item.expandingDirections = lambda: widget.sizePolicy().expandingDirections()
        item.isEmpty = lambda: False
        item.setGeometry = lambda rect: widget.setGeometry(rect)
        item.geometry = lambda: widget.geometry()
        
        # Propriétés de grille
        item.row = row
        item.col = col
        item.row_span = row_span
        item.col_span = col_span
        item.ratio_type = ratio_type
        
        self._items.append(item)
        self._grid_items[(row, col)] = item
        
        # Mettre à jour les dimensions de la grille
        self._row_count = max(self._row_count, row + row_span)
        self._col_count = max(self._col_count, col + col_span)
        
        self.invalidate()
        return item
    
    def addItem(self, item: QLayoutItem):
        """Ajoute un élément au layout"""
        self._items.append(item)
        self.invalidate()
    
    def count(self) -> int:
        return len(self._items)
    
    def itemAt(self, index: int) -> Optional[QLayoutItem]:
        if 0 <= index < len(self._items):
            return self._items[index]
        return None
    
    def takeAt(self, index: int) -> Optional[QLayoutItem]:
        if 0 <= index < len(self._items):
            item = self._items.pop(index)
            # Retirer de la grille aussi
            for key, grid_item in list(self._grid_items.items()):
                if grid_item == item:
                    del self._grid_items[key]
                    break
            self.invalidate()
            return item
        return None
    
    def sizeHint(self) -> QSize:
        """Calcule la taille recommandée basée sur le nombre d'or"""
        if not self._items:
            return QSize(0, 0)
        
        # Calculer les dimensions de base
        base_width = 200  # Largeur de base
        base_height = int(base_width / self.PHI)  # Hauteur dorée
        
        total_width = base_width * self._col_count + self._spacing * (self._col_count - 1)
        total_height = base_height * self._row_count + self._spacing * (self._row_count - 1)
        
        # Ajouter les marges
        margins = self.contentsMargins()
        total_width += margins.left() + margins.right()
        total_height += margins.top() + margins.bottom()
        
        return QSize(total_width, total_height)
    
    def minimumSize(self) -> QSize:
        """Calcule la taille minimale"""
        if not self._items:
            return QSize(0, 0)
        
        min_width = 100 * self._col_count + self._spacing * (self._col_count - 1)
        min_height = int(100 / self.PHI) * self._row_count + self._spacing * (self._row_count - 1)
        
        margins = self.contentsMargins()
        min_width += margins.left() + margins.right()
        min_height += margins.top() + margins.bottom()
        
        return QSize(min_width, min_height)
    
    def setGeometry(self, rect: QRect):
        """Positionne les éléments dans la grille dorée"""
        super().setGeometry(rect)
        
        if not self._items or self._row_count == 0 or self._col_count == 0:
            return
        
        # Zone de contenu
        margins = self.contentsMargins()
        content_rect = rect.adjusted(
            margins.left(), margins.top(),
            -margins.right(), -margins.bottom()
        )
        
        # Calculer les dimensions des cellules
        cell_width = (content_rect.width() - self._spacing * (self._col_count - 1)) // self._col_count
        cell_height = (content_rect.height() - self._spacing * (self._row_count - 1)) // self._row_count
        
        # Ajuster selon le nombre d'or si possible
        golden_height = int(cell_width / self.PHI)
        if golden_height <= cell_height:
            cell_height = golden_height
        
        # Positionner chaque élément
        for item in self._items:
            if hasattr(item, 'row') and hasattr(item, 'col'):
                row = item.row
                col = item.col
                row_span = getattr(item, 'row_span', 1)
                col_span = getattr(item, 'col_span', 1)
                
                # Calculer la position et la taille
                x = content_rect.x() + col * (cell_width + self._spacing)
                y = content_rect.y() + row * (cell_height + self._spacing)
                
                width = cell_width * col_span + self._spacing * (col_span - 1)
                height = cell_height * row_span + self._spacing * (row_span - 1)
                
                item_rect = QRect(x, y, width, height)
                item.setGeometry(item_rect)
    
    def expandingDirections(self) -> Qt.Orientations:
        return Qt.Horizontal | Qt.Vertical
    
    def hasHeightForWidth(self) -> bool:
        return False


def create_golden_ratio_sizes(base_size: int = 100) -> dict:
    """
    Crée un ensemble de tailles basées sur le nombre d'or
    
    Args:
        base_size: Taille de base en pixels
    
    Returns:
        Dictionnaire avec différentes tailles dorées
    """
    phi = (1 + math.sqrt(5)) / 2
    
    return {
        'xs': int(base_size / (phi * phi)),      # ~38px
        'sm': int(base_size / phi),              # ~62px
        'md': base_size,                         # 100px
        'lg': int(base_size * phi),              # ~162px
        'xl': int(base_size * phi * phi),        # ~262px
        'xxl': int(base_size * phi * phi * phi)  # ~424px
    }


def create_golden_ratio_spacing() -> dict:
    """
    Crée un système d'espacement basé sur le nombre d'or
    
    Returns:
        Dictionnaire avec différents espacements
    """
    phi = (1 + math.sqrt(5)) / 2
    base = 8  # Espacement de base
    
    return {
        'xs': int(base / phi),          # ~5px
        'sm': base,                     # 8px
        'md': int(base * phi),          # ~13px
        'lg': int(base * phi * phi),    # ~21px
        'xl': int(base * phi * phi * phi)  # ~34px
    }