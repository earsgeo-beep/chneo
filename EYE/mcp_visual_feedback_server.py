# MCP Visual Feedback Server Implementation
# Exemple d'implémentation d'un serveur MCP pour feedback visuel en temps réel

import asyncio
import base64
import json
import os
from typing import Any, Dict, List, Optional
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import mss
from fastmcp import FastMCP
from pydantic import BaseModel

class VisualIssue(BaseModel):
    type: str  # 'contrast', 'alignment', 'responsive', 'accessibility'
    severity: str  # 'high', 'medium', 'low'
    description: str
    location: Dict[str, int]  # x, y, width, height
    suggestion: str

class CorrectionSuggestion(BaseModel):
    issue_type: str
    css_changes: Dict[str, str]
    html_changes: Optional[str] = None
    explanation: str

class MCPVisualFeedbackServer:
    def __init__(self):
        self.app = FastMCP("Visual Feedback Server")
        self.screenshots_dir = Path("./screenshots")
        self.screenshots_dir.mkdir(exist_ok=True)

    async def capture_screenshot(self, target: str, format: str = "screenshot") -> str:
        """Capture une interface utilisateur"""
        try:
            with mss.mss() as sct:
                # Capture de l'écran complet par défaut
                screenshot = sct.grab(sct.monitors[1])
                img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")

            timestamp = int(asyncio.get_event_loop().time())
            filename = f"capture_{timestamp}.png"
            filepath = self.screenshots_dir / filename
            img.save(filepath)

            return str(filepath)

        except Exception as e:
            raise Exception(f"Erreur lors de la capture: {str(e)}")

    def analyze_contrast_issues(self, image_path: str) -> List[VisualIssue]:
        """Analyse les problèmes de contraste"""
        issues = []

        # Charger l'image
        img = cv2.imread(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Détection de texte avec contraste faible
        # Simulé pour l'exemple - en réalité, utiliserait OCR + analyse de contraste
        height, width = gray.shape

        # Zones sombres avec possiblement du texte
        dark_regions = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY_INV)[1]
        contours, _ = cv2.findContours(dark_regions, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            if w > 50 and h > 20:  # Taille minimale pour du texte
                issues.append(VisualIssue(
                    type="contrast",
                    severity="high",
                    description="Texte potentiellement illisible sur fond sombre",
                    location={"x": x, "y": y, "width": w, "height": h},
                    suggestion="Augmenter le contraste ou changer la couleur du texte"
                ))

        return issues

    def analyze_alignment_issues(self, image_path: str) -> List[VisualIssue]:
        """Analyse les problèmes d'alignement"""
        issues = []

        img = cv2.imread(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Détection de bords pour analyser l'alignement
        edges = cv2.Canny(gray, 50, 150)
        lines = cv2.HoughLines(edges, 1, np.pi/180, threshold=100)

        if lines is not None and len(lines) < 5:
            # Très peu de lignes droites détectées = problèmes d'alignement potentiels
            issues.append(VisualIssue(
                type="alignment",
                severity="medium",
                description="Éléments possiblement mal alignés",
                location={"x": 0, "y": 0, "width": img.shape[1], "height": img.shape[0]},
                suggestion="Vérifier l'alignement des éléments avec CSS Grid ou Flexbox"
            ))

        return issues

    def generate_corrections(self, issues: List[VisualIssue], context: str = "css") -> List[CorrectionSuggestion]:
        """Génère des suggestions de correction"""
        corrections = []

        for issue in issues:
            if issue.type == "contrast":
                corrections.append(CorrectionSuggestion(
                    issue_type="contrast",
                    css_changes={
                        "color": "#ffffff",
                        "background-color": "#333333",
                        "text-shadow": "1px 1px 2px rgba(0,0,0,0.8)"
                    },
                    explanation="Amélioration du contraste texte/fond pour une meilleure lisibilité"
                ))

            elif issue.type == "alignment":
                corrections.append(CorrectionSuggestion(
                    issue_type="alignment",
                    css_changes={
                        "display": "flex",
                        "align-items": "center",
                        "justify-content": "space-between",
                        "gap": "1rem"
                    },
                    explanation="Utilisation de Flexbox pour un alignement cohérent"
                ))

        return corrections

    def setup_routes(self):
        """Configuration des outils MCP"""

        @self.app.tool()
        async def capture_ui(target: str, format: str = "screenshot", wait_time: int = 2000) -> Dict[str, Any]:
            """Capture une interface utilisateur"""
            await asyncio.sleep(wait_time / 1000)  # Attente en secondes
            filepath = await self.capture_screenshot(target, format)

            return {
                "success": True,
                "filepath": filepath,
                "message": f"Capture réalisée: {filepath}"
            }

        @self.app.tool()
        async def analyze_visual_issues(image_path: str, check_types: List[str] = ["contrast", "alignment"]) -> Dict[str, Any]:
            """Analyse les problèmes visuels détectés"""
            all_issues = []

            if "contrast" in check_types:
                all_issues.extend(self.analyze_contrast_issues(image_path))

            if "alignment" in check_types:
                all_issues.extend(self.analyze_alignment_issues(image_path))

            return {
                "success": True,
                "issues_count": len(all_issues),
                "issues": [issue.dict() for issue in all_issues],
                "message": f"Analyse terminée: {len(all_issues)} problèmes détectés"
            }

        @self.app.tool()
        async def suggest_corrections(issues: List[Dict], context: str = "css") -> Dict[str, Any]:
            """Suggère des corrections basées sur l'analyse"""
            issue_objects = [VisualIssue(**issue) for issue in issues]
            corrections = self.generate_corrections(issue_objects, context)

            return {
                "success": True,
                "corrections_count": len(corrections),
                "corrections": [corr.dict() for corr in corrections],
                "message": f"Généré {len(corrections)} suggestions de correction"
            }

        @self.app.tool()
        async def compare_ui_versions(before_image: str, after_image: str, diff_sensitivity: float = 0.5) -> Dict[str, Any]:
            """Compare deux versions d'interface"""
            try:
                # Charger les images
                img1 = cv2.imread(before_image)
                img2 = cv2.imread(after_image)

                # Calculer la différence
                diff = cv2.absdiff(img1, img2)
                diff_score = np.mean(diff) / 255.0

                # Sauvegarder l'image de différence
                timestamp = int(asyncio.get_event_loop().time())
                diff_path = self.screenshots_dir / f"diff_{timestamp}.png"
                cv2.imwrite(str(diff_path), diff)

                return {
                    "success": True,
                    "difference_score": diff_score,
                    "significant_change": diff_score > diff_sensitivity,
                    "diff_image": str(diff_path),
                    "message": f"Différence calculée: {diff_score:.2%}"
                }

            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "message": "Erreur lors de la comparaison"
                }

        @self.app.tool()
        async def apply_corrections(corrections: List[Dict], target_file: str, backup: bool = True) -> Dict[str, Any]:
            """Applique automatiquement les corrections (simulation)"""
            try:
                if backup and os.path.exists(target_file):
                    backup_file = f"{target_file}.backup"
                    with open(target_file, 'r') as src, open(backup_file, 'w') as dst:
                        dst.write(src.read())

                # Ici, on simulerait l'application des corrections au fichier CSS/HTML
                applied_count = len(corrections)

                return {
                    "success": True,
                    "applied_corrections": applied_count,
                    "backup_created": backup,
                    "message": f"Appliqué {applied_count} corrections à {target_file}"
                }

            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "message": "Erreur lors de l'application des corrections"
                }

# Remplacer l'entrée asynchrone par une entrée synchrone compatible avec FastMCP

def main():
    """Point d'entrée principal"""
    server = MCPVisualFeedbackServer()
    server.setup_routes()

    # Lancement du serveur MCP (bloquant, géré en interne par FastMCP)
    server.app.run()

if __name__ == "__main__":
    main()
