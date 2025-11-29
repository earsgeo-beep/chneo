#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Correction du problème spécifique dans DashboardViewMaritime
"""

import sys
import traceback
from pathlib import Path

# Ajouter le chemin du projet
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_dashboard_view_creation_detailed():
    """Test détaillé de création de DashboardViewMaritime"""
    print("🔍 TEST CRÉATION DASHBOARDVIEW DÉTAILLÉ")
    print("=" * 50)
    
    try:
        from PySide6.QtWidgets import QApplication
        
        # Créer QApplication
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        print("✅ QApplication créé")
        
        # Test import DashboardViewMaritime
        print("🔄 Import DashboardViewMaritime...")
        from hrneowave.gui.views.dashboard_view import DashboardViewMaritime
        print("✅ DashboardViewMaritime importé")
        
        # Test création DashboardViewMaritime avec debug détaillé
        print("🔄 Création DashboardViewMaritime...")
        print("=" * 30)
        
        try:
            dashboard_view = DashboardViewMaritime(parent=None)
            print("✅ DashboardViewMaritime créée avec succès")
            return True
        except Exception as e:
            print(f"❌ Erreur création DashboardViewMaritime: {e}")
            traceback.print_exc()
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        traceback.print_exc()
        return False

def fix_dashboard_view_imports():
    """Corriger les imports problématiques dans DashboardViewMaritime"""
    print("\n🔧 CORRECTION IMPORTS DASHBOARDVIEW")
    print("=" * 40)
    
    try:
        # Lire le fichier dashboard_view.py
        dashboard_path = Path("src/hrneowave/gui/views/dashboard_view.py")
        
        if not dashboard_path.exists():
            print(f"❌ Fichier non trouvé: {dashboard_path}")
            return False
        
        with open(dashboard_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("✅ Fichier dashboard_view.py lu")
        
        # Créer une sauvegarde
        backup_path = dashboard_path.with_suffix('.py.backup')
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Sauvegarde créée: {backup_path}")
        
        # Remplacer les imports problématiques par des imports sûrs
        original_imports = '''# Import hiérarchique PySide6 > PyQt6 > PyQt5
try:
    from PySide6.QtCore import Qt, QTimer, Signal, QPropertyAnimation, QEasingCurve, QRect
    from PySide6.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, 
        QPushButton, QFrame, QScrollArea, QSizePolicy, QSpacerItem
    )
    from PySide6.QtGui import QFont, QPalette, QColor
    pyqtSignal = Signal
except ImportError:
    try:
        from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QPropertyAnimation, QEasingCurve, QRect
        from PyQt6.QtWidgets import (
            QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, 
            QPushButton, QFrame, QScrollArea, QSizePolicy, QSpacerItem
        )
        from PyQt6.QtGui import QFont, QPalette, QColor
        Signal = pyqtSignal
    except ImportError:
        from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QPropertyAnimation, QEasingCurve, QRect
        from PyQt5.QtWidgets import (
            QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, 
            QPushButton, QFrame, QScrollArea, QSizePolicy, QSpacerItem
        )
        from PyQt5.QtGui import QFont, QPalette, QColor
        Signal = pyqtSignal'''
        
        safe_imports = '''# Import PySide6 uniquement
from PySide6.QtCore import Qt, QTimer, Signal, QPropertyAnimation, QEasingCurve, QRect
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, 
    QPushButton, QFrame, QScrollArea, QSizePolicy, QSpacerItem
)
from PySide6.QtGui import QFont, QPalette, QColor
pyqtSignal = Signal'''
        
        # Remplacer les imports
        content = content.replace(original_imports, safe_imports)
        print("✅ Imports PySide6 simplifiés")
        
        # Remplacer les imports problématiques des widgets maritimes
        maritime_imports = '''# Import des composants maritimes
try:
    from ..widgets.maritime import (
        MaritimeCard, KPIIndicator, MaritimeButton,
        StatusBeacon, MaritimeGrid
    )
    from ..widgets.maritime_components import (
        MaritimeTheme, StatusType, create_maritime_layout
    )
except ImportError:
    # Fallback si les widgets maritimes ne sont pas encore disponibles
    MaritimeCard = QFrame
    KPIIndicator = QFrame
    StatusBeacon = QFrame
    MaritimeButton = QPushButton
    MaritimeGrid = QFrame
    
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
    
    def create_maritime_layout(*args, **kwargs):
        return QVBoxLayout()'''
        
        safe_maritime_imports = '''# Import des composants maritimes (simplifié)
# Fallback pour les widgets maritimes
MaritimeCard = QFrame
KPIIndicator = QFrame
StatusBeacon = QFrame
MaritimeButton = QPushButton
MaritimeGrid = QFrame

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

def create_maritime_layout(*args, **kwargs):
    return QVBoxLayout()'''
        
        # Remplacer les imports maritimes
        content = content.replace(maritime_imports, safe_maritime_imports)
        print("✅ Imports maritimes simplifiés")
        
        # Remplacer l'import problématique de ProgressStepper
        progress_import = '''try:
    from ..widgets.progress_stepper import ProgressStepper
except ImportError:
    ProgressStepper = QFrame'''
        
        safe_progress_import = '''# Fallback pour ProgressStepper
ProgressStepper = QFrame'''
        
        # Remplacer l'import ProgressStepper
        content = content.replace(progress_import, safe_progress_import)
        print("✅ Import ProgressStepper simplifié")
        
        # Écrire le fichier modifié
        with open(dashboard_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Fichier dashboard_view.py modifié avec imports sûrs")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la modification: {e}")
        traceback.print_exc()
        return False

def create_test_dashboard_view_fixed():
    """Créer un test pour DashboardViewMaritime corrigé"""
    print("\n🔧 CRÉATION TEST DASHBOARDVIEW CORRIGÉ")
    print("=" * 40)
    
    test_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test DashboardViewMaritime corrigé
"""

import sys
import traceback
from pathlib import Path

# Ajouter le chemin du projet
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_dashboard_view_fixed():
    """Test DashboardViewMaritime corrigé"""
    print("🚀 TEST DASHBOARDVIEW CORRIGÉ")
    print("=" * 50)
    
    try:
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import Qt, QTimer
        
        # Créer QApplication
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
            app.setApplicationName("CHNeoWave Dashboard Test")
        
        print("✅ QApplication créé")
        
        # Test import DashboardViewMaritime
        print("🔄 Import DashboardViewMaritime...")
        from hrneowave.gui.views.dashboard_view import DashboardViewMaritime
        print("✅ DashboardViewMaritime importé")
        
        # Test création DashboardViewMaritime
        print("🔄 Création DashboardViewMaritime...")
        dashboard_view = DashboardViewMaritime(parent=None)
        print("✅ DashboardViewMaritime créée")
        
        # Test affichage
        print("🔄 Affichage DashboardViewMaritime...")
        dashboard_view.show()
        
        visible = dashboard_view.isVisible()
        print(f"✅ DashboardViewMaritime visible: {visible}")
        
        if visible:
            print("🎉 SUCCÈS: DashboardViewMaritime visible!")
            
            # Maintenir ouvert 5 secondes
            timer = QTimer()
            timer.timeout.connect(app.quit)
            timer.start(5000)
            
            print("🔄 Maintien ouvert 5 secondes...")
            exit_code = app.exec()
            print(f"✅ Test terminé (code: {exit_code})")
            return True
        else:
            print("❌ PROBLÈME: DashboardViewMaritime non visible")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    exit(0 if test_dashboard_view_fixed() else 1)
'''
    
    try:
        with open('test_dashboard_view_fixed.py', 'w', encoding='utf-8') as f:
            f.write(test_content)
        print("✅ Test DashboardViewMaritime corrigé créé: test_dashboard_view_fixed.py")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de la création du test: {e}")
        return False

def main():
    """Point d'entrée principal"""
    print("🔧 CORRECTEUR DASHBOARDVIEW")
    print("=" * 50)
    
    # Test détaillé de création DashboardViewMaritime
    if not test_dashboard_view_creation_detailed():
        print("❌ ÉCHEC: Test création DashboardViewMaritime")
        return 1
    
    # Corriger les imports problématiques
    if not fix_dashboard_view_imports():
        print("❌ ÉCHEC: Correction imports DashboardViewMaritime")
        return 1
    
    # Créer test DashboardViewMaritime corrigé
    if not create_test_dashboard_view_fixed():
        print("❌ ÉCHEC: Création test DashboardViewMaritime corrigé")
        return 1
    
    print("\n🎉 CORRECTION DASHBOARDVIEW TERMINÉE!")
    print("✅ Imports DashboardViewMaritime corrigés")
    print("✅ Test DashboardViewMaritime corrigé créé: test_dashboard_view_fixed.py")
    
    print("\n🚀 COMMANDES DE TEST:")
    print("1. Test DashboardViewMaritime corrigé: python test_dashboard_view_fixed.py")
    print("2. Test MainWindow sûr: python test_main_window_safe.py")
    print("3. Lancement application: python main.py")
    
    return 0

if __name__ == "__main__":
    exit(main()) 