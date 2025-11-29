#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API Locale SQLite pour la Base de Donnees d'Instrumentation Maritime
Version Windows compatible - sans emojis Unicode
"""

import sqlite3
import json
from datetime import datetime, date
from typing import List, Dict, Any, Optional
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

class LocalDatabaseAPI:
    def __init__(self, db_file="instrumentation_maritime.db"):
        self.db_file = db_file
        self.ensure_database_exists()
    
    def ensure_database_exists(self):
        """Verifier que la base de donnees existe"""
        if not os.path.exists(self.db_file):
            print(f"ERREUR: Base de donnees non trouvee: {self.db_file}")
            print("Executez d'abord: python create_db_simple.py")
            return False
        return True
    
    def get_connection(self):
        """Obtenir une connexion a la base de donnees"""
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row  # Pour acceder aux colonnes par nom
        return conn
    
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Obtenir les statistiques pour le dashboard"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Total equipements
            cursor.execute("SELECT COUNT(*) FROM equipements WHERE etat NOT IN ('REBUT', 'REFORME')")
            total_equipements = cursor.fetchone()[0]
            
            # Equipements OK
            cursor.execute("SELECT COUNT(*) FROM equipements WHERE etat = 'OK'")
            equipements_ok = cursor.fetchone()[0]
            
            # Equipements en panne
            cursor.execute("SELECT COUNT(*) FROM equipements WHERE etat = 'EN_PANNE'")
            equipements_panne = cursor.fetchone()[0]
            
            # Verifications expirees
            cursor.execute("SELECT COUNT(*) FROM equipements WHERE prochaine_verification < date('now')")
            verifications_expirees = cursor.fetchone()[0]
            
            # Interventions du mois
            cursor.execute("""
                SELECT COUNT(*) FROM interventions 
                WHERE date_intervention >= date('now', 'start of month')
            """)
            interventions_mois = cursor.fetchone()[0]
            
            # Cout maintenance annee
            cursor.execute("""
                SELECT COALESCE(SUM(cout), 0) FROM interventions 
                WHERE strftime('%Y', date_intervention) = strftime('%Y', 'now')
            """)
            cout_maintenance_annee = cursor.fetchone()[0]
            
            # Projets actifs
            cursor.execute("SELECT COUNT(*) FROM projets WHERE statut = 'ACTIF'")
            projets_actifs = cursor.fetchone()[0]
            
            return {
                "total_equipements": total_equipements,
                "equipements_ok": equipements_ok,
                "equipements_panne": equipements_panne,
                "verifications_expirees": verifications_expirees,
                "interventions_mois": interventions_mois,
                "cout_maintenance_annee": float(cout_maintenance_annee),
                "projets_actifs": projets_actifs,
                "licences_expire_bientot": 0  # Pas de licences dans cette version
            }
        
        finally:
            conn.close()
    
    def get_alertes_metrologie(self) -> List[Dict[str, Any]]:
        """Obtenir les alertes metrologiques"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT 
                    e.id_equipement,
                    e.numero,
                    e.description,
                    s.nom as service,
                    e.prochaine_verification,
                    CASE 
                        WHEN e.prochaine_verification < date('now') THEN 'EXPIRE'
                        WHEN e.prochaine_verification < date('now', '+30 days') THEN 'ALERTE'
                        WHEN e.prochaine_verification < date('now', '+60 days') THEN 'ATTENTION'
                        ELSE 'OK'
                    END as statut_alerte,
                    julianday('now') - julianday(e.prochaine_verification) as jours_retard
                FROM equipements e
                LEFT JOIN services s ON e.service_id = s.id
                WHERE e.prochaine_verification IS NOT NULL
                    AND e.etat NOT IN ('REBUT', 'REFORME')
                    AND e.prochaine_verification < date('now', '+60 days')
                ORDER BY e.prochaine_verification
            """)
            
            alertes = []
            for row in cursor.fetchall():
                alertes.append({
                    "id_equipement": row["id_equipement"],
                    "numero": row["numero"],
                    "description": row["description"],
                    "service": row["service"],
                    "prochaine_verification": row["prochaine_verification"],
                    "statut_alerte": row["statut_alerte"],
                    "jours_retard": int(row["jours_retard"]) if row["jours_retard"] > 0 else None
                })
            
            return alertes
        
        finally:
            conn.close()
    
    def get_kpi_services(self) -> List[Dict[str, Any]]:
        """Obtenir les KPI par service"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT 
                    s.id as service_id,
                    s.code,
                    s.nom as service,
                    COUNT(e.id_equipement) as total_equipements,
                    SUM(CASE WHEN e.etat = 'OK' THEN 1 ELSE 0 END) as equipements_ok,
                    SUM(CASE WHEN e.etat = 'EN_PANNE' THEN 1 ELSE 0 END) as equipements_panne,
                    SUM(CASE WHEN e.etat = 'MAINTENANCE' THEN 1 ELSE 0 END) as equipements_maintenance,
                    ROUND(
                        CAST(SUM(CASE WHEN e.etat = 'OK' THEN 1 ELSE 0 END) AS FLOAT) / 
                        NULLIF(COUNT(e.id_equipement), 0) * 100, 2
                    ) as taux_disponibilite,
                    SUM(CASE WHEN e.prochaine_verification < date('now') THEN 1 ELSE 0 END) as verifications_expirees
                FROM services s
                LEFT JOIN equipements e ON s.id = e.service_id
                WHERE e.etat IS NULL OR e.etat NOT IN ('REBUT', 'REFORME')
                GROUP BY s.id, s.code, s.nom
                ORDER BY s.nom
            """)
            
            kpis = []
            for row in cursor.fetchall():
                kpis.append({
                    "service_id": row["service_id"],
                    "code": row["code"],
                    "service": row["service"],
                    "total_equipements": row["total_equipements"],
                    "equipements_ok": row["equipements_ok"],
                    "equipements_panne": row["equipements_panne"],
                    "equipements_maintenance": row["equipements_maintenance"],
                    "taux_disponibilite": float(row["taux_disponibilite"] or 0),
                    "verifications_expirees": row["verifications_expirees"]
                })
            
            return kpis
        
        finally:
            conn.close()
    
    def get_services(self) -> List[Dict[str, Any]]:
        """Obtenir tous les services"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT * FROM services ORDER BY nom")
            services = []
            for row in cursor.fetchall():
                services.append({
                    "id": row["id"],
                    "code": row["code"],
                    "nom": row["nom"],
                    "responsable": row["responsable"],
                    "description": row["description"]
                })
            return services
        
        finally:
            conn.close()
    
    def get_equipements(self, service_id: Optional[int] = None, 
                       etat: Optional[str] = None,
                       search: Optional[str] = None) -> List[Dict[str, Any]]:
        """Obtenir les equipements avec filtres"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Construction de la requete avec filtres
            query = """
                SELECT 
                    e.*,
                    s.nom as service_nom,
                    s.code as service_code
                FROM equipements e
                LEFT JOIN services s ON e.service_id = s.id
                WHERE 1=1
            """
            params = []
            
            if service_id:
                query += " AND e.service_id = ?"
                params.append(service_id)
            
            if etat:
                query += " AND e.etat = ?"
                params.append(etat)
            
            if search:
                query += " AND (e.description LIKE ? OR e.marque_type LIKE ? OR e.numero LIKE ?)"
                search_param = f"%{search}%"
                params.extend([search_param, search_param, search_param])
            
            query += " ORDER BY e.numero"
            
            cursor.execute(query, params)
            
            equipements = []
            for row in cursor.fetchall():
                equipement = {
                    "id_equipement": row["id_equipement"],
                    "numero": row["numero"],
                    "description": row["description"],
                    "marque_type": row["marque_type"],
                    "numero_serie": row["numero_serie"],
                    "n_inventaire": row["n_inventaire"],
                    "utilisateur": row["utilisateur"],
                    "localisation": row["localisation"],
                    "etat": row["etat"],
                    "annee_acquisition": row["annee_acquisition"],
                    "valeur_acquisition": float(row["valeur_acquisition"]) if row["valeur_acquisition"] else None,
                    "statut_metrologique": row["statut_metrologique"],
                    "date_derniere_verification": row["date_derniere_verification"],
                    "prochaine_verification": row["prochaine_verification"],
                    "frequence_verification_mois": row["frequence_verification_mois"],
                    "criticite": row["criticite"],
                    "commentaires": row["commentaires"],
                    "service": {
                        "id": row["service_id"],
                        "nom": row["service_nom"],
                        "code": row["service_code"]
                    } if row["service_id"] else None
                }
                equipements.append(equipement)
            
            return equipements
        
        finally:
            conn.close()

# Instance globale de l'API
api = LocalDatabaseAPI()

class LocalAPIHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Gerer les requetes GET"""
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        query_params = parse_qs(parsed_url.query)
        
        # Headers CORS
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        try:
            if path == '/api/dashboard/stats':
                data = api.get_dashboard_stats()
            
            elif path == '/api/dashboard/alertes-metrologie':
                data = api.get_alertes_metrologie()
            
            elif path == '/api/dashboard/kpi-services':
                data = api.get_kpi_services()
            
            elif path == '/api/services':
                data = api.get_services()
            
            elif path == '/api/equipements':
                service_id = int(query_params.get('service_id', [None])[0]) if query_params.get('service_id', [None])[0] else None
                etat = query_params.get('etat', [None])[0]
                search = query_params.get('search', [None])[0]
                data = api.get_equipements(service_id, etat, search)
            
            elif path == '/health':
                data = {
                    "status": "healthy",
                    "timestamp": datetime.now().isoformat(),
                    "database": "connected"
                }
            
            else:
                data = {
                    "message": "API Locale Instrumentation Maritime",
                    "version": "1.0.0",
                    "status": "active",
                    "endpoints": [
                        "/api/dashboard/stats",
                        "/api/dashboard/alertes-metrologie",
                        "/api/dashboard/kpi-services",
                        "/api/services",
                        "/api/equipements",
                        "/health"
                    ]
                }
            
            # Envoyer la reponse JSON
            response = json.dumps(data, ensure_ascii=False, default=str)
            self.wfile.write(response.encode('utf-8'))
        
        except Exception as e:
            error_response = {"error": str(e)}
            response = json.dumps(error_response)
            self.wfile.write(response.encode('utf-8'))
    
    def do_OPTIONS(self):
        """Gerer les requetes OPTIONS pour CORS"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def log_message(self, format, *args):
        """Personnaliser les logs"""
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {format % args}")

if __name__ == "__main__":
    print("Demarrage de l'API Locale d'Instrumentation Maritime")
    print("=" * 60)
    
    # Verifier la base de donnees
    if not api.ensure_database_exists():
        exit(1)
    
    # Test rapide
    print("Test de la base de donnees...")
    stats = api.get_dashboard_stats()
    print(f"OK - {stats['total_equipements']} equipements trouves")
    
    # Demarrer le serveur web
    server_address = ('localhost', 8000)
    httpd = HTTPServer(server_address, LocalAPIHandler)
    
    print(f"\nServeur API demarre sur http://localhost:8000")
    print(f"Dashboard: Ouvrez frontend/index.html dans votre navigateur")
    print(f"API Test: http://localhost:8000/health")
    print(f"\nAppuyez sur Ctrl+C pour arreter")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print(f"\nServeur arrete")
        httpd.shutdown()
