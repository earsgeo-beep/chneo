# Architecture de la Base de Données d'Instrumentation Maritime Moderne

## Vue d'ensemble

Cette architecture implémente une base de données moderne et professionnelle pour la gestion d'équipements d'instrumentation scientifique et maritime du Laboratoire d'Études Maritimes (LEM), basée sur l'analyse du fichier Excel BDD INST 2025.xlsx contenant 24 feuilles de données.

## Analyse des Données Source

### Structure Identifiée (24 feuilles Excel)
- **Inv 2025** : 231 équipements (inventaire principal)
- **Liste EMS 2025** : 79 équipements sous contrôle métrologique
- **Pl Metrologique 2025** : 74 équipements avec planning métrologique
- **Suivi Plan Etalo 2025** : 209 enregistrements d'étalonnage
- **Support Tech-CTS/CEM** : 159 projets techniques (103 CTS + 56 CEM)
- **Formation** : Historique des formations techniques
- **Licences** : 8 licences actives
- **Invest-Acht/Suivi invest** : Suivi budgétaire et investissements
- **Rebut-Reforme** : 33 équipements réformés

## Architecture Relationnelle Optimisée

### 1. Tables Principales

```sql
-- Table centrale des équipements
CREATE TABLE equipements (
    id_equipement SERIAL PRIMARY KEY,
    numero VARCHAR(50) UNIQUE NOT NULL,
    description TEXT NOT NULL,
    marque_type VARCHAR(200),
    numero_serie VARCHAR(100),
    n_inventaire VARCHAR(50) UNIQUE,
    utilisateur VARCHAR(100),
    service_id INTEGER REFERENCES services(id),
    localisation VARCHAR(200),
    etat equipement_etat DEFAULT 'OK',
    annee_acquisition INTEGER,
    statut_metrologique metrologie_statut DEFAULT 'CONFORME',
    date_derniere_verification DATE,
    prochaine_verification DATE,
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Services organisationnels
CREATE TABLE services (
    id SERIAL PRIMARY KEY,
    code VARCHAR(10) UNIQUE NOT NULL, -- CTS, CEM, DSC, INT
    nom VARCHAR(100) NOT NULL,
    responsable VARCHAR(100),
    description TEXT
);

-- Contrôles et étalonnages métrologiques
CREATE TABLE metrologie (
    id_controle SERIAL PRIMARY KEY,
    equipement_id INTEGER REFERENCES equipements(id_equipement),
    type_controle controle_type NOT NULL,
    date_verification DATE NOT NULL,
    resultat metrologie_resultat DEFAULT 'CONFORME',
    prestataire VARCHAR(200),
    cout DECIMAL(10,2),
    devise VARCHAR(3) DEFAULT 'DA',
    prochaine_echeance DATE,
    certificat_path VARCHAR(500),
    commentaires TEXT,
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Projets et utilisation opérationnelle
CREATE TABLE projets (
    id_projet SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    description TEXT,
    service_id INTEGER REFERENCES services(id),
    date_debut DATE,
    date_fin DATE,
    statut projet_statut DEFAULT 'ACTIF',
    budget_alloue DECIMAL(12,2),
    responsable VARCHAR(100)
);

-- Association équipements-projets
CREATE TABLE equipement_projets (
    equipement_id INTEGER REFERENCES equipements(id_equipement),
    projet_id INTEGER REFERENCES projets(id_projet),
    date_affectation DATE DEFAULT CURRENT_DATE,
    taux_utilisation DECIMAL(5,2), -- pourcentage
    PRIMARY KEY (equipement_id, projet_id)
);

-- Interventions de maintenance
CREATE TABLE interventions (
    id_intervention SERIAL PRIMARY KEY,
    equipement_id INTEGER REFERENCES equipements(id_equipement),
    type_intervention intervention_type NOT NULL,
    date_intervention DATE NOT NULL,
    description TEXT,
    technicien VARCHAR(100),
    cout DECIMAL(10,2),
    duree_heures DECIMAL(5,2),
    statut intervention_statut DEFAULT 'PLANIFIEE',
    pieces_changees TEXT,
    commentaires TEXT
);

-- Formations du personnel
CREATE TABLE formations (
    id_formation SERIAL PRIMARY KEY,
    titre VARCHAR(200) NOT NULL,
    description TEXT,
    formateur VARCHAR(100),
    date_formation DATE,
    duree_heures INTEGER,
    service_id INTEGER REFERENCES services(id),
    participants TEXT[], -- Array PostgreSQL
    cout DECIMAL(10,2),
    certificat_obtenu BOOLEAN DEFAULT FALSE
);

-- Licences logicielles et réglementaires
CREATE TABLE licences (
    id_licence SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    type_licence licence_type NOT NULL,
    fournisseur VARCHAR(200),
    date_acquisition DATE,
    date_expiration DATE,
    cout_annuel DECIMAL(10,2),
    nombre_postes INTEGER,
    statut licence_statut DEFAULT 'ACTIVE',
    contact_support VARCHAR(200)
);

-- Budgets et investissements
CREATE TABLE budgets (
    id_budget SERIAL PRIMARY KEY,
    annee INTEGER NOT NULL,
    service_id INTEGER REFERENCES services(id),
    poste_budgetaire VARCHAR(100),
    budget_alloue DECIMAL(12,2),
    budget_consomme DECIMAL(12,2) DEFAULT 0,
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 2. Types Énumérés (ENUM)

```sql
-- États des équipements
CREATE TYPE equipement_etat AS ENUM ('OK', 'EN_PANNE', 'MAINTENANCE', 'REBUT', 'REFORME');

-- Statuts métrologiques
CREATE TYPE metrologie_statut AS ENUM ('CONFORME', 'NON_CONFORME', 'EN_ATTENTE', 'EXPIRE');

-- Types de contrôles
CREATE TYPE controle_type AS ENUM ('ETALONNAGE', 'VERIFICATION', 'MAINTENANCE_PREVENTIVE', 'CONTROLE_QUALITE');

-- Résultats métrologiques
CREATE TYPE metrologie_resultat AS ENUM ('CONFORME', 'NON_CONFORME', 'AJUSTE', 'REFORME');

-- Statuts des projets
CREATE TYPE projet_statut AS ENUM ('ACTIF', 'TERMINE', 'SUSPENDU', 'ANNULE');

-- Types d'interventions
CREATE TYPE intervention_type AS ENUM ('MAINTENANCE_PREVENTIVE', 'REPARATION', 'INSTALLATION', 'MISE_A_JOUR');

-- Statuts des interventions
CREATE TYPE intervention_statut AS ENUM ('PLANIFIEE', 'EN_COURS', 'TERMINEE', 'REPORTEE');

-- Types de licences
CREATE TYPE licence_type AS ENUM ('LOGICIEL', 'REGLEMENTAIRE', 'CERTIFICATION', 'ABONNEMENT');

-- Statuts des licences
CREATE TYPE licence_statut AS ENUM ('ACTIVE', 'EXPIREE', 'SUSPENDUE', 'RENOUVELEE');
```

### 3. Index et Contraintes

```sql
-- Index pour les performances
CREATE INDEX idx_equipements_service ON equipements(service_id);
CREATE INDEX idx_equipements_etat ON equipements(etat);
CREATE INDEX idx_equipements_prochaine_verif ON equipements(prochaine_verification);
CREATE INDEX idx_metrologie_equipement ON metrologie(equipement_id);
CREATE INDEX idx_metrologie_date ON metrologie(date_verification);
CREATE INDEX idx_interventions_equipement ON interventions(equipement_id);
CREATE INDEX idx_interventions_date ON interventions(date_intervention);

-- Contraintes d'intégrité
ALTER TABLE equipements ADD CONSTRAINT chk_annee_acquisition 
    CHECK (annee_acquisition >= 1990 AND annee_acquisition <= EXTRACT(YEAR FROM CURRENT_DATE) + 1);

ALTER TABLE metrologie ADD CONSTRAINT chk_cout_positif 
    CHECK (cout >= 0);

ALTER TABLE budgets ADD CONSTRAINT chk_budget_coherent 
    CHECK (budget_consomme <= budget_alloue);
```

## Fonctionnalités Modernes

### 1. Triggers pour l'Audit et la Traçabilité

```sql
-- Fonction de mise à jour automatique des timestamps
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.date_modification = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers sur les tables principales
CREATE TRIGGER update_equipements_modtime 
    BEFORE UPDATE ON equipements 
    FOR EACH ROW EXECUTE FUNCTION update_modified_column();
```

### 2. Vues Métier pour les Dashboards

```sql
-- Vue des équipements avec alertes métrologiques
CREATE VIEW v_alertes_metrologie AS
SELECT 
    e.id_equipement,
    e.numero,
    e.description,
    s.nom as service,
    e.prochaine_verification,
    CASE 
        WHEN e.prochaine_verification < CURRENT_DATE THEN 'EXPIRE'
        WHEN e.prochaine_verification < CURRENT_DATE + INTERVAL '30 days' THEN 'ALERTE'
        ELSE 'OK'
    END as statut_alerte
FROM equipements e
JOIN services s ON e.service_id = s.id
WHERE e.prochaine_verification IS NOT NULL;

-- Vue des KPI par service
CREATE VIEW v_kpi_services AS
SELECT 
    s.nom as service,
    COUNT(e.id_equipement) as total_equipements,
    COUNT(CASE WHEN e.etat = 'OK' THEN 1 END) as equipements_ok,
    COUNT(CASE WHEN e.etat = 'EN_PANNE' THEN 1 END) as equipements_panne,
    ROUND(
        COUNT(CASE WHEN e.etat = 'OK' THEN 1 END)::DECIMAL / 
        NULLIF(COUNT(e.id_equipement), 0) * 100, 2
    ) as taux_disponibilite
FROM services s
LEFT JOIN equipements e ON s.id = e.service_id
GROUP BY s.id, s.nom;
```

## Technologies Recommandées

### Base de Données
- **PostgreSQL 15+** : Robustesse entreprise, support JSON, arrays
- **Connexions** : Pool de connexions (pgbouncer)
- **Sauvegarde** : pg_dump automatisé quotidien

### Backend API
- **FastAPI** (Python) : API REST moderne et performante
- **SQLAlchemy** : ORM avec support PostgreSQL avancé
- **Pydantic** : Validation des données et sérialisation
- **JWT** : Authentification sécurisée

### Frontend Web
- **React 18** avec TypeScript
- **Material-UI** : Composants professionnels
- **Chart.js** : Graphiques interactifs
- **React Query** : Gestion d'état et cache

### DevOps
- **Docker** : Conteneurisation
- **nginx** : Reverse proxy et serveur statique
- **GitHub Actions** : CI/CD

## Sécurité et Conformité

### 1. Authentification et Autorisation
- Authentification JWT avec refresh tokens
- Rôles : Admin, Chef_Service, Technicien, Lecteur
- Permissions granulaires par service

### 2. Audit et Traçabilité
- Log de toutes les modifications (qui, quand, quoi)
- Historique des changements d'état des équipements
- Traçabilité des certificats d'étalonnage

### 3. Conformité Normative
- **ISO 9001** : Système de management de la qualité
- **ISO 10012** : Système de management de la mesure
- **GDPR** : Protection des données personnelles

## Performances et Scalabilité

### Objectifs
- **Temps de réponse** : < 2 secondes pour 95% des requêtes
- **Disponibilité** : > 99.5% (SLA)
- **Utilisateurs simultanés** : 100+
- **Croissance** : Support de 10,000+ équipements

### Optimisations
- Index sur les colonnes fréquemment recherchées
- Pagination des résultats
- Cache Redis pour les données fréquentes
- Compression des réponses API

Cette architecture moderne transforme la gestion Excel actuelle en un système digital professionnel avec analytics avancés et interface utilisateur de niveau entreprise.
