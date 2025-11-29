#!/usr/bin/env python3
"""
Création de la base de données locale SQLite
Pour la gestion d'instrumentation maritime
"""

import sqlite3
import json
import os
from datetime import datetime, date

def create_local_database():
    """Créer la base de données SQLite locale"""
    
    # Nom du fichier de base de données
    db_file = "instrumentation_maritime.db"
    
    # Supprimer l'ancienne base si elle existe
    if os.path.exists(db_file):
        os.remove(db_file)
        print(f"Ancienne base de données supprimée: {db_file}")
    
    # Créer la connexion
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    print(f"Création de la base de données locale: {db_file}")
    
    # =============================================================================
    # CRÉATION DES TABLES
    # =============================================================================
    
    # Table des services
    cursor.execute('''
    CREATE TABLE services (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT UNIQUE NOT NULL,
        nom TEXT NOT NULL,
        responsable TEXT,
        description TEXT,
        date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Table des équipements
    cursor.execute('''
    CREATE TABLE equipements (
        id_equipement INTEGER PRIMARY KEY AUTOINCREMENT,
        numero TEXT UNIQUE NOT NULL,
        description TEXT NOT NULL,
        marque_type TEXT,
        numero_serie TEXT,
        n_inventaire TEXT UNIQUE,
        utilisateur TEXT,
        service_id INTEGER,
        localisation TEXT,
        etat TEXT DEFAULT 'OK',
        annee_acquisition INTEGER,
        valeur_acquisition REAL,
        statut_metrologique TEXT DEFAULT 'CONFORME',
        date_derniere_verification DATE,
        prochaine_verification DATE,
        frequence_verification_mois INTEGER DEFAULT 12,
        criticite INTEGER DEFAULT 1,
        commentaires TEXT,
        date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (service_id) REFERENCES services (id)
    )
    ''')
    
    # Table métrologie
    cursor.execute('''
    CREATE TABLE metrologie (
        id_controle INTEGER PRIMARY KEY AUTOINCREMENT,
        equipement_id INTEGER,
        type_controle TEXT NOT NULL,
        date_verification DATE NOT NULL,
        resultat TEXT DEFAULT 'CONFORME',
        prestataire TEXT,
        cout REAL,
        devise TEXT DEFAULT 'DA',
        prochaine_echeance DATE,
        certificat_numero TEXT,
        certificat_path TEXT,
        commentaires TEXT,
        technicien_responsable TEXT,
        date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (equipement_id) REFERENCES equipements (id_equipement)
    )
    ''')
    
    # Table projets
    cursor.execute('''
    CREATE TABLE projets (
        id_projet INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT NOT NULL,
        description TEXT,
        service_id INTEGER,
        date_debut DATE,
        date_fin DATE,
        statut TEXT DEFAULT 'ACTIF',
        budget_alloue REAL,
        budget_consomme REAL DEFAULT 0,
        responsable TEXT,
        priorite INTEGER DEFAULT 3,
        avancement_pourcentage REAL DEFAULT 0,
        date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (service_id) REFERENCES services (id)
    )
    ''')
    
    # Table interventions
    cursor.execute('''
    CREATE TABLE interventions (
        id_intervention INTEGER PRIMARY KEY AUTOINCREMENT,
        equipement_id INTEGER,
        type_intervention TEXT NOT NULL,
        date_intervention DATE NOT NULL,
        date_fin_intervention DATE,
        description TEXT NOT NULL,
        technicien TEXT,
        cout REAL,
        duree_heures REAL,
        statut TEXT DEFAULT 'PLANIFIEE',
        pieces_changees TEXT,
        fournisseur TEXT,
        commentaires TEXT,
        date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (equipement_id) REFERENCES equipements (id_equipement)
    )
    ''')
    
    # Table formations
    cursor.execute('''
    CREATE TABLE formations (
        id_formation INTEGER PRIMARY KEY AUTOINCREMENT,
        titre TEXT NOT NULL,
        description TEXT,
        formateur TEXT,
        organisme TEXT,
        date_formation DATE,
        duree_heures INTEGER,
        service_id INTEGER,
        participants TEXT,
        cout REAL,
        lieu TEXT,
        certificat_obtenu BOOLEAN DEFAULT 0,
        validite_mois INTEGER,
        date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (service_id) REFERENCES services (id)
    )
    ''')
    
    # Table licences
    cursor.execute('''
    CREATE TABLE licences (
        id_licence INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT NOT NULL,
        type_licence TEXT NOT NULL,
        fournisseur TEXT,
        version TEXT,
        date_acquisition DATE,
        date_expiration DATE,
        cout_annuel REAL,
        nombre_postes INTEGER DEFAULT 1,
        postes_utilises INTEGER DEFAULT 0,
        statut TEXT DEFAULT 'ACTIVE',
        contact_support TEXT,
        commentaires TEXT,
        date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Table budgets
    cursor.execute('''
    CREATE TABLE budgets (
        id_budget INTEGER PRIMARY KEY AUTOINCREMENT,
        annee INTEGER NOT NULL,
        service_id INTEGER,
        poste_budgetaire TEXT NOT NULL,
        budget_alloue REAL NOT NULL,
        budget_consomme REAL DEFAULT 0,
        budget_engage REAL DEFAULT 0,
        responsable TEXT,
        date_validation DATE,
        commentaires TEXT,
        date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (service_id) REFERENCES services (id)
    )
    ''')
    
    print("✅ Tables créées avec succès")
    
    # =============================================================================
    # INSERTION DES DONNÉES DE RÉFÉRENCE
    # =============================================================================
    
    # Services
    services_data = [
        ('CTS', 'Centre Technique Spécialisé', 'Chef CTS', 'Service technique principal'),
        ('CEM', "Centre d'Études Maritimes", 'Chef CEM', 'Études et recherche maritime'),
        ('DSC', 'Direction Scientifique et Contrôle', 'Directeur DSC', 'Direction scientifique'),
        ('INT', 'Instrumentation', 'Chef Instrumentation', 'Service instrumentation')
    ]
    
    cursor.executemany('''
    INSERT INTO services (code, nom, responsable, description) 
    VALUES (?, ?, ?, ?)
    ''', services_data)
    
    print("✅ Services insérés")
    
    # Équipements d'exemple
    equipements_data = [
        ('EQ-001', 'Oscilloscope numérique Tektronix', 'Tektronix TDS2024C', 'C123456', 'INV-2023-001', 'Technicien A', 1, 'Laboratoire 1', 'OK', 2023, 15000.0, 'CONFORME', '2024-01-15', '2025-01-15', 12, 3, 'Équipement principal de mesure'),
        ('EQ-002', 'Multimètre de précision Fluke', 'Fluke 8845A', 'F789012', 'INV-2022-045', 'Technicien B', 2, 'Laboratoire 2', 'EN_PANNE', 2022, 8500.0, 'EXPIRE', '2023-08-01', '2024-08-01', 12, 4, 'Nécessite réparation urgente'),
        ('EQ-003', 'Générateur de signaux Keysight', 'Keysight 33500B', 'K345678', 'INV-2024-012', 'Ingénieur C', 3, 'Laboratoire 3', 'OK', 2024, 12000.0, 'CONFORME', '2024-06-30', '2025-06-30', 12, 5, 'Équipement critique'),
        ('EQ-004', 'Analyseur de spectre Rohde & Schwarz', 'R&S FSW26', 'RS456789', 'INV-2023-078', 'Technicien D', 1, 'Laboratoire 1', 'OK', 2023, 45000.0, 'CONFORME', '2024-03-15', '2025-03-15', 12, 5, 'Équipement haute précision'),
        ('EQ-005', 'Alimentation stabilisée Agilent', 'Agilent E3631A', 'AG123456', 'INV-2021-034', 'Technicien A', 4, 'Atelier', 'MAINTENANCE', 2021, 2500.0, 'EN_ATTENTE', '2024-02-01', '2024-08-01', 6, 2, 'Maintenance préventive en cours')
    ]
    
    cursor.executemany('''
    INSERT INTO equipements (numero, description, marque_type, numero_serie, n_inventaire, utilisateur, service_id, localisation, etat, annee_acquisition, valeur_acquisition, statut_metrologique, date_derniere_verification, prochaine_verification, frequence_verification_mois, criticite, commentaires) 
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', equipements_data)
    
    print("✅ Équipements d'exemple insérés")
    
    # Enregistrements métrologiques
    metrologie_data = [
        (1, 'ETALONNAGE', '2024-01-15', 'CONFORME', 'COFRAC Métrologie', 1200.0, 'DA', '2025-01-15', 'CERT-2024-001', None, 'Étalonnage annuel conforme', 'Technicien Métrologie'),
        (2, 'VERIFICATION', '2023-08-01', 'NON_CONFORME', 'Bureau Veritas', 800.0, 'DA', '2024-08-01', 'CERT-2023-045', None, 'Dérive constatée - réparation nécessaire', 'Expert Externe'),
        (3, 'ETALONNAGE', '2024-06-30', 'CONFORME', 'COFRAC Métrologie', 1500.0, 'DA', '2025-06-30', 'CERT-2024-078', None, 'Étalonnage haute précision', 'Technicien Spécialisé'),
        (4, 'ETALONNAGE', '2024-03-15', 'CONFORME', 'Rohde & Schwarz Service', 3500.0, 'DA', '2025-03-15', 'CERT-2024-034', None, 'Étalonnage constructeur', 'Ingénieur R&S'),
        (5, 'VERIFICATION', '2024-02-01', 'EN_ATTENTE', 'Service Interne', 0.0, 'DA', '2024-08-01', None, None, 'Vérification interne en attente', 'Technicien Interne')
    ]
    
    cursor.executemany('''
    INSERT INTO metrologie (equipement_id, type_controle, date_verification, resultat, prestataire, cout, devise, prochaine_echeance, certificat_numero, certificat_path, commentaires, technicien_responsable) 
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', metrologie_data)
    
    print("✅ Données métrologiques insérées")
    
    # Projets
    projets_data = [
        ('Modernisation Laboratoire 1', 'Mise à niveau des équipements de mesure', 1, '2024-01-01', '2024-12-31', 'ACTIF', 150000.0, 45000.0, 'Chef Projet A', 4, 30.0),
        ('Certification ISO 17025', 'Obtention de la certification du laboratoire', 3, '2024-03-01', '2025-02-28', 'ACTIF', 80000.0, 25000.0, 'Responsable Qualité', 5, 40.0),
        ('Formation Personnel Technique', 'Programme de formation continue', 2, '2024-02-01', '2024-11-30', 'ACTIF', 25000.0, 12000.0, 'RH Technique', 3, 60.0),
        ('Maintenance Préventive 2024', 'Programme annuel de maintenance', 4, '2024-01-01', '2024-12-31', 'ACTIF', 75000.0, 35000.0, 'Chef Maintenance', 3, 50.0)
    ]
    
    cursor.executemany('''
    INSERT INTO projets (nom, description, service_id, date_debut, date_fin, statut, budget_alloue, budget_consomme, responsable, priorite, avancement_pourcentage) 
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', projets_data)
    
    print("✅ Projets insérés")
    
    # Valider les changements
    conn.commit()
    
    # =============================================================================
    # CRÉATION DES INDEX POUR LES PERFORMANCES
    # =============================================================================
    
    indexes = [
        "CREATE INDEX idx_equipements_service ON equipements(service_id)",
        "CREATE INDEX idx_equipements_etat ON equipements(etat)",
        "CREATE INDEX idx_equipements_prochaine_verif ON equipements(prochaine_verification)",
        "CREATE INDEX idx_metrologie_equipement ON metrologie(equipement_id)",
        "CREATE INDEX idx_metrologie_date ON metrologie(date_verification)",
        "CREATE INDEX idx_interventions_equipement ON interventions(equipement_id)",
        "CREATE INDEX idx_projets_service ON projets(service_id)"
    ]
    
    for index_sql in indexes:
        cursor.execute(index_sql)
    
    print("✅ Index créés pour les performances")
    
    # Fermer la connexion
    conn.close()
    
    print(f"\n🎉 Base de données locale créée avec succès !")
    print(f"📁 Fichier: {os.path.abspath(db_file)}")
    print(f"📊 Données d'exemple insérées")
    
    return db_file

def test_database(db_file):
    """Tester la base de données créée"""
    
    print(f"\n🔍 Test de la base de données: {db_file}")
    
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    # Test des services
    cursor.execute("SELECT COUNT(*) FROM services")
    services_count = cursor.fetchone()[0]
    print(f"✅ Services: {services_count}")
    
    # Test des équipements
    cursor.execute("SELECT COUNT(*) FROM equipements")
    equipements_count = cursor.fetchone()[0]
    print(f"✅ Équipements: {equipements_count}")
    
    # Test des données métrologiques
    cursor.execute("SELECT COUNT(*) FROM metrologie")
    metrologie_count = cursor.fetchone()[0]
    print(f"✅ Contrôles métrologiques: {metrologie_count}")
    
    # Test des projets
    cursor.execute("SELECT COUNT(*) FROM projets")
    projets_count = cursor.fetchone()[0]
    print(f"✅ Projets: {projets_count}")
    
    # Test d'une requête complexe
    cursor.execute('''
    SELECT 
        s.nom as service,
        COUNT(e.id_equipement) as total_equipements,
        SUM(CASE WHEN e.etat = 'OK' THEN 1 ELSE 0 END) as equipements_ok
    FROM services s
    LEFT JOIN equipements e ON s.id = e.service_id
    GROUP BY s.id, s.nom
    ORDER BY s.nom
    ''')
    
    results = cursor.fetchall()
    print(f"\n📊 Statistiques par service:")
    for service, total, ok in results:
        print(f"  - {service}: {total} équipements ({ok} OK)")
    
    conn.close()
    print(f"\n✅ Test terminé avec succès !")

if __name__ == "__main__":
    print("🚀 Création de la base de données locale d'instrumentation maritime")
    print("=" * 70)
    
    # Créer la base de données
    db_file = create_local_database()
    
    # Tester la base de données
    test_database(db_file)
    
    print(f"\n🎯 Votre base de données locale est prête !")
    print(f"📁 Emplacement: {os.path.abspath(db_file)}")
    print(f"🔧 Utilisez cette base avec l'API locale")
