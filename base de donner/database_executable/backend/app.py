#!/usr/bin/env python3
"""
API Backend pour la Base de Données d'Instrumentation Maritime
FastAPI + PostgreSQL + SQLAlchemy
"""

import sys
import os
from fastapi import FastAPI, HTTPException, Depends, Query, status, Request
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, date
import json
import os

# =============================================================================
# CONFIGURATION DE L'APPLICATION
# =============================================================================

app = FastAPI(
    title="API Instrumentation Maritime",
    description="API moderne pour la gestion d'équipements d'instrumentation maritime",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, spécifier les domaines autorisés
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware pour désactiver la mise en cache des fichiers statiques


# Servir l'interface web (frontend)
# Le chemin d'accès au répertoire 'frontend' est relatif à l'emplacement de 'app.py'
# Détermine le chemin de base (pour le développement et pour l'exécutable PyInstaller)
if getattr(sys, 'frozen', False):
    # Si l'application est "gelée" (exécutable), le chemin de base est le répertoire temporaire de PyInstaller
    base_dir = sys._MEIPASS
else:
    # Sinon (développement), c'est le répertoire du script
    base_dir = os.path.dirname(os.path.abspath(__file__))

# Chemin vers le dossier frontend
# Dans le cas de l'exécutable, 'frontend' est à la racine. 
# En développement, il est un niveau au-dessus de 'backend'.
frontend_path = os.path.join(base_dir, 'frontend') if getattr(sys, 'frozen', False) else os.path.join(base_dir, '..', 'frontend')

@app.get("/{full_path:path}")
async def serve_frontend(request: Request, full_path: str):
    """Sert les fichiers du frontend, avec index.html comme fallback et en-têtes no-cache."""
    file_path = os.path.join(frontend_path, full_path)

    # Si le chemin est un répertoire ou n'existe pas, servir index.html
    if not os.path.isfile(file_path) or full_path == "":
        file_path = os.path.join(frontend_path, "index.html")
    
    if not os.path.isfile(file_path):
        # Tenter de servir index.html si la ressource n'est pas trouvée
        index_path = os.path.join(frontend_path, "index.html")
        if not os.path.isfile(index_path):
             raise HTTPException(status_code=404, detail="Frontend files not found")
        response = FileResponse(index_path)
    else:
        response = FileResponse(file_path)
        
    # Ajouter les en-têtes pour empêcher la mise en cache
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

# =============================================================================
# MODÈLES PYDANTIC POUR LES RÉPONSES
# =============================================================================

class ServiceModel(BaseModel):
    id: int
    code: str
    nom: str
    responsable: Optional[str] = None
    description: Optional[str] = None

class EquipementModel(BaseModel):
    id_equipement: int
    numero: str
    description: str
    marque_type: Optional[str] = None
    numero_serie: Optional[str] = None
    n_inventaire: Optional[str] = None
    utilisateur: Optional[str] = None
    service: Optional[ServiceModel] = None
    localisation: Optional[str] = None
    etat: str
    annee_acquisition: Optional[int] = None
    statut_metrologique: str
    prochaine_verification: Optional[date] = None
    criticite: int = 1

class AlerteMetrologie(BaseModel):
    id_equipement: int
    numero: str
    description: str
    service: str
    prochaine_verification: Optional[date]
    statut_alerte: str
    jours_retard: Optional[int]

class KPIService(BaseModel):
    service: str
    total_equipements: int
    equipements_ok: int
    equipements_panne: int
    taux_disponibilite: float
    verifications_expirees: int

class DashboardStats(BaseModel):
    total_equipements: int
    equipements_ok: int
    equipements_panne: int
    verifications_expirees: int
    interventions_mois: int
    cout_maintenance_annee: float
    projets_actifs: int
    licences_expire_bientot: int

# =============================================================================
# DONNÉES SIMULÉES (EN ATTENDANT LA BASE DE DONNÉES)
# =============================================================================

# Services
services_data = [
    {"id": 1, "code": "CTS", "nom": "Centre Technique Spécialisé", "responsable": "Chef CTS"},
    {"id": 2, "code": "CEM", "nom": "Centre d'Études Maritimes", "responsable": "Chef CEM"},
    {"id": 3, "code": "DSC", "nom": "Direction Scientifique et Contrôle", "responsable": "Directeur DSC"},
    {"id": 4, "code": "INT", "nom": "Instrumentation", "responsable": "Chef Instrumentation"}
]

# Équipements simulés
equipements_data = [
    {
        "id_equipement": 1,
        "numero": "EQ-001",
        "description": "Oscilloscope numérique Tektronix",
        "marque_type": "Tektronix TDS2024C",
        "numero_serie": "C123456",
        "n_inventaire": "INV-2023-001",
        "utilisateur": "Technicien A",
        "service": services_data[0],
        "localisation": "Laboratoire 1",
        "etat": "OK",
        "annee_acquisition": 2023,
        "statut_metrologique": "CONFORME",
        "prochaine_verification": "2024-12-15",
        "criticite": 3
    },
    {
        "id_equipement": 2,
        "numero": "EQ-002",
        "description": "Multimètre de précision Fluke",
        "marque_type": "Fluke 8845A",
        "numero_serie": "F789012",
        "n_inventaire": "INV-2022-045",
        "utilisateur": "Technicien B",
        "service": services_data[1],
        "localisation": "Laboratoire 2",
        "etat": "EN_PANNE",
        "annee_acquisition": 2022,
        "statut_metrologique": "EXPIRE",
        "prochaine_verification": "2024-08-01",
        "criticite": 4
    },
    {
        "id_equipement": 3,
        "numero": "EQ-003",
        "description": "Générateur de signaux Keysight",
        "marque_type": "Keysight 33500B",
        "numero_serie": "K345678",
        "n_inventaire": "INV-2024-012",
        "utilisateur": "Ingénieur C",
        "service": services_data[2],
        "localisation": "Laboratoire 3",
        "etat": "OK",
        "annee_acquisition": 2024,
        "statut_metrologique": "CONFORME",
        "prochaine_verification": "2025-06-30",
        "criticite": 5
    }
]

# =============================================================================
# ENDPOINTS DE L'API
# =============================================================================



@app.get("/health", response_model=Dict[str, str])
async def health_check():
    """Vérification de l'état de l'API"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "database": "connected"  # À adapter selon la vraie connexion DB
    }

# =============================================================================
# ENDPOINTS SERVICES
# =============================================================================

@app.get("/api/services", response_model=List[ServiceModel])
async def get_services():
    """Récupérer tous les services"""
    return services_data

@app.get("/api/services/{service_id}", response_model=ServiceModel)
async def get_service(service_id: int):
    """Récupérer un service par ID"""
    service = next((s for s in services_data if s["id"] == service_id), None)
    if not service:
        raise HTTPException(status_code=404, detail="Service non trouvé")
    return service

# =============================================================================
# ENDPOINTS ÉQUIPEMENTS
# =============================================================================

@app.get("/api/equipements", response_model=List[EquipementModel])
async def get_equipements(
    service_id: Optional[int] = Query(None, description="Filtrer par service"),
    etat: Optional[str] = Query(None, description="Filtrer par état"),
    search: Optional[str] = Query(None, description="Recherche textuelle"),
    limit: int = Query(100, ge=1, le=1000, description="Nombre maximum de résultats"),
    offset: int = Query(0, ge=0, description="Décalage pour la pagination")
):
    """Récupérer les équipements avec filtres optionnels"""
    
    # Filtrage des données
    filtered_data = equipements_data.copy()
    
    if service_id:
        filtered_data = [eq for eq in filtered_data if eq["service"]["id"] == service_id]
    
    if etat:
        filtered_data = [eq for eq in filtered_data if eq["etat"] == etat]
    
    if search:
        search_lower = search.lower()
        filtered_data = [
            eq for eq in filtered_data 
            if search_lower in eq["description"].lower() 
            or search_lower in (eq["marque_type"] or "").lower()
            or search_lower in eq["numero"].lower()
        ]
    
    # Pagination
    total = len(filtered_data)
    paginated_data = filtered_data[offset:offset + limit]
    
    return paginated_data

@app.get("/api/equipements/{equipement_id}", response_model=EquipementModel)
async def get_equipement(equipement_id: int):
    """Récupérer un équipement par ID"""
    equipement = next((eq for eq in equipements_data if eq["id_equipement"] == equipement_id), None)
    if not equipement:
        raise HTTPException(status_code=404, detail="Équipement non trouvé")
    return equipement

@app.put("/api/equipements/{equipement_id}")
async def update_equipement(equipement_id: int, equipement_data: dict):
    """Mettre à jour un équipement"""
    # Simulation de mise à jour
    equipement = next((eq for eq in equipements_data if eq["id_equipement"] == equipement_id), None)
    if not equipement:
        raise HTTPException(status_code=404, detail="Équipement non trouvé")
    
    # Mise à jour des champs
    for key, value in equipement_data.items():
        if key in equipement:
            equipement[key] = value
    
    return {"message": "Équipement mis à jour avec succès", "equipement": equipement}

# =============================================================================
# ENDPOINTS DASHBOARD ET ANALYTICS
# =============================================================================

@app.get("/api/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats():
    """Statistiques globales pour le dashboard"""
    
    # Calcul des statistiques basées sur les données simulées
    total_equipements = len(equipements_data)
    equipements_ok = len([eq for eq in equipements_data if eq["etat"] == "OK"])
    equipements_panne = len([eq for eq in equipements_data if eq["etat"] == "EN_PANNE"])
    verifications_expirees = len([eq for eq in equipements_data if eq["statut_metrologique"] == "EXPIRE"])
    
    return DashboardStats(
        total_equipements=total_equipements,
        equipements_ok=equipements_ok,
        equipements_panne=equipements_panne,
        verifications_expirees=verifications_expirees,
        interventions_mois=15,  # Simulé
        cout_maintenance_annee=125000.0,  # Simulé
        projets_actifs=8,  # Simulé
        licences_expire_bientot=2  # Simulé
    )

@app.get("/api/dashboard/alertes-metrologie", response_model=List[AlerteMetrologie])
async def get_alertes_metrologie():
    """Alertes métrologiques pour le dashboard"""
    
    alertes = []
    for eq in equipements_data:
        if eq["statut_metrologique"] == "EXPIRE":
            alertes.append(AlerteMetrologie(
                id_equipement=eq["id_equipement"],
                numero=eq["numero"],
                description=eq["description"],
                service=eq["service"]["nom"],
                prochaine_verification=eq["prochaine_verification"],
                statut_alerte="EXPIRE",
                jours_retard=30  # Simulé
            ))
    
    return alertes

@app.get("/api/dashboard/kpi-services", response_model=List[KPIService])
async def get_kpi_services():
    """KPI par service pour le dashboard"""
    
    kpis = []
    for service in services_data:
        equipements_service = [eq for eq in equipements_data if eq["service"]["id"] == service["id"]]
        total = len(equipements_service)
        ok_count = len([eq for eq in equipements_service if eq["etat"] == "OK"])
        panne_count = len([eq for eq in equipements_service if eq["etat"] == "EN_PANNE"])
        expire_count = len([eq for eq in equipements_service if eq["statut_metrologique"] == "EXPIRE"])
        
        taux_disponibilite = (ok_count / total * 100) if total > 0 else 0
        
        kpis.append(KPIService(
            service=service["nom"],
            total_equipements=total,
            equipements_ok=ok_count,
            equipements_panne=panne_count,
            taux_disponibilite=round(taux_disponibilite, 2),
            verifications_expirees=expire_count
        ))
    
    return kpis

# =============================================================================
# ENDPOINTS RECHERCHE
# =============================================================================

@app.get("/api/search/equipements")
async def search_equipements(
    q: str = Query(..., min_length=2, description="Terme de recherche"),
    limit: int = Query(20, ge=1, le=100, description="Nombre de résultats")
):
    """Recherche full-text dans les équipements"""
    
    search_term = q.lower()
    results = []
    
    for eq in equipements_data:
        score = 0
        
        # Calcul du score de pertinence
        if search_term in eq["numero"].lower():
            score += 10
        if search_term in eq["description"].lower():
            score += 5
        if eq["marque_type"] and search_term in eq["marque_type"].lower():
            score += 3
        if eq["n_inventaire"] and search_term in eq["n_inventaire"].lower():
            score += 8
        
        if score > 0:
            result = eq.copy()
            result["search_score"] = score
            results.append(result)
    
    # Tri par score décroissant
    results.sort(key=lambda x: x["search_score"], reverse=True)
    
    return results[:limit]

# =============================================================================
# ENDPOINTS EXPORT
# =============================================================================

@app.get("/api/export/equipements")
async def export_equipements(format: str = Query("json", regex="^(json|csv)$")):
    """Export des équipements en JSON ou CSV"""
    
    if format == "json":
        return JSONResponse(
            content=equipements_data,
            headers={"Content-Disposition": "attachment; filename=equipements.json"}
        )
    
    elif format == "csv":
        # Simulation d'export CSV
        csv_content = "ID,Numero,Description,Marque,Service,Etat,Statut_Metrologique\n"
        for eq in equipements_data:
            csv_content += f"{eq['id_equipement']},{eq['numero']},{eq['description']},{eq['marque_type']},{eq['service']['nom']},{eq['etat']},{eq['statut_metrologique']}\n"
        
        return JSONResponse(
            content={"csv_data": csv_content},
            headers={"Content-Disposition": "attachment; filename=equipements.csv"}
        )

# =============================================================================
# GESTION DES ERREURS
# =============================================================================

@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"error": "Ressource non trouvée", "detail": str(exc)}
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"error": "Erreur interne du serveur", "detail": "Une erreur inattendue s'est produite"}
    )

# =============================================================================
# POINT D'ENTRÉE
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8001,
        log_level="info"
    )
