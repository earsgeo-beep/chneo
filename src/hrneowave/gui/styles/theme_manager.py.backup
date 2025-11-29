import os
import logging
import re
from pathlib import Path

try:
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import QObject, Signal
except ImportError:
    raise ImportError("PySide6 n'est pas installé. Veuillez l'installer pour utiliser CHNeoWave.")

class ThemeManager(QObject):
    """Gestionnaire de thèmes simplifié pour charger les fichiers QSS."""
    theme_changed = Signal(str)

    def __init__(self, app: QApplication):
        super().__init__(app)
        self.app = app
        self._styles_dir = Path(__file__).parent
        self._logger = logging.getLogger(__name__)
        self._current_theme = ''

    def _parse_variables(self, content: str) -> dict:
        """Parse les variables CSS-like depuis une chaîne de caractères."""
        import re
        variables = {}
        # Regex simple pour extraire --variable: valeur;
        var_matches = re.findall(r'(--[a-zA-Z0-9-]+):\s*([^;]+);', content)
        for name, value in var_matches:
            variables[name.strip()] = value.strip()
        self._logger.debug(f"{len(variables)} variables de thème parsées.")
        return variables

    def _replace_variables(self, content: str, variables: dict) -> str:
        """Remplace les `var(--variable)` par leurs valeurs."""
        import re
        def replacer(match):
            var_name = match.group(1).strip()
            return variables.get(var_name, f'var({var_name})') # Garde l'original si non trouvé

        return re.sub(r'var\((--[a-zA-Z0-9-]+)\)', replacer, content)

    def _load_stylesheet(self, theme_name: str) -> str:
        """Charge, parse les variables et combine les fichiers QSS."""
        # 1. Charger le nouveau thème maritime moderne
        if theme_name == 'maritime_modern':
            theme_file_path = self._styles_dir / 'maritime_modern.qss'
        else:
            # Fallback vers l'ancien thème professionnel
            theme_file_path = self._styles_dir / 'professional_theme.qss'
            
        if not theme_file_path.exists():
            self._logger.error(f"Fichier de thème principal manquant: {theme_file_path}")
            return ""
        
        try:
            theme_content = theme_file_path.read_text(encoding='utf-8')
        except IOError as e:
            self._logger.error(f"Impossible de lire {theme_file_path}: {e}")
            return ""

        # 2. Parser les variables depuis ce fichier (si applicable)
        variables = self._parse_variables(theme_content)

        # 3. Charger tous les autres fichiers QSS et les concaténer
        full_stylesheet = self._load_all_qss_files(theme_name, theme_content)

        # 4. Remplacer les variables dans la feuille de style complète
        final_stylesheet = self._replace_variables(full_stylesheet, variables)
        
        # Supprimer les blocs de définition de variables pour ne pas polluer le QSS final
        final_stylesheet = re.sub(r'QWidget\s*\{[^\}]*--bg-primary[^\}]*\}', '', final_stylesheet, flags=re.DOTALL)

        return final_stylesheet

    def _load_all_qss_files(self, theme_name: str, base_theme_content: str) -> str:
        """Charge et concatène tous les fichiers QSS nécessaires."""
        stylesheet_parts = [base_theme_content]

        self._logger.info(f"Chargement du thème '{theme_name}'")

        # Charger les fichiers d'animation pour le thème maritime moderne
        if theme_name == 'maritime_modern':
            animation_file = self._styles_dir / 'animations.qss'
            if animation_file.exists():
                try:
                    stylesheet_parts.append(animation_file.read_text(encoding='utf-8'))
                    self._logger.info("Animations maritimes chargées")
                except IOError as e:
                    self._logger.error(f"Impossible de lire le fichier d'animations {animation_file}: {e}")

        # Fichiers QSS des composants
        component_qss_files = [
            'main_sidebar.qss',
            'components.qss' # Fichier générique pour les petits composants
        ]

        for qss_file in component_qss_files:
            file_path = self._styles_dir / qss_file
            if file_path.exists():
                try:
                    stylesheet_parts.append(file_path.read_text(encoding='utf-8'))
                except IOError as e:
                    self._logger.error(f"Impossible de lire le fichier de composant {file_path}: {e}")
            # Pas de warning si le fichier de composant est manquant, c'est optionnel

        return '\n'.join(stylesheet_parts)

    def apply_theme(self, theme_name: str):
        """Applique un thème à l'application."""
        valid_themes = ['light', 'dark', 'maritime_modern']
        if theme_name not in valid_themes:
            self._logger.error(f"Thème invalide: '{theme_name}'. Utilisez {valid_themes}.")
            return

        stylesheet = self._load_stylesheet(theme_name)
        if stylesheet:
            self.app.setStyleSheet(stylesheet)
            if self._current_theme != theme_name:
                self._current_theme = theme_name
                self.theme_changed.emit(theme_name)
                self._logger.info(f"Thème '{theme_name}' appliqué avec succès.")

    def toggle_theme(self):
        """Bascule entre les thèmes disponibles."""
        themes = ['maritime_modern', 'light', 'dark']
        current_index = themes.index(self._current_theme) if self._current_theme in themes else 0
        new_theme = themes[(current_index + 1) % len(themes)]
        self.apply_theme(new_theme)
        
    def apply_maritime_modern_theme(self):
        """Applique directement le thème maritime moderne."""
        self.apply_theme('maritime_modern')

    def get_current_theme(self) -> str:
        return self._current_theme