-- Base de Données d'Instrumentation Maritime Moderne
-- Schéma PostgreSQL complet
-- Généré le 2025-08-12

-- =============================================================================
-- 1. SUPPRESSION ET CRÉATION DE LA BASE DE DONNÉES
-- =============================================================================

-- DROP DATABASE IF EXISTS instrumentation_maritime;
-- CREATE DATABASE instrumentation_maritime WITH ENCODING 'UTF8';
-- \c instrumentation_maritime;

-- =============================================================================
-- 2. EXTENSIONS POSTGRESQL
-- =============================================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm"; -- Pour la recherche full-text

-- =============================================================================
-- 3. TYPES ÉNUMÉRÉS
-- =============================================================================

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

-- =============================================================================
-- 4. TABLES PRINCIPALES
-- =============================================================================

-- Table des services organisationnels
CREATE TABLE services (
    id SERIAL PRIMARY KEY,
    code VARCHAR(10) UNIQUE NOT NULL, -- CTS, CEM, DSC, INT
    nom VARCHAR(100) NOT NULL,
    responsable VARCHAR(100),
    description TEXT,
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table centrale des équipements
CREATE TABLE equipements (
    id_equipement SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE,
    numero VARCHAR(50) UNIQUE NOT NULL,
    description TEXT NOT NULL,
    marque_type VARCHAR(200),
    numero_serie VARCHAR(100),
    n_inventaire VARCHAR(50) UNIQUE,
    utilisateur VARCHAR(100),
    service_id INTEGER REFERENCES services(id) ON DELETE SET NULL,
    localisation VARCHAR(200),
    etat equipement_etat DEFAULT 'OK',
    annee_acquisition INTEGER,
    valeur_acquisition DECIMAL(12,2),
    statut_metrologique metrologie_statut DEFAULT 'CONFORME',
    date_derniere_verification DATE,
    prochaine_verification DATE,
    frequence_verification_mois INTEGER DEFAULT 12,
    criticite INTEGER DEFAULT 1 CHECK (criticite BETWEEN 1 AND 5),
    commentaires TEXT,
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Contrôles et étalonnages métrologiques
CREATE TABLE metrologie (
    id_controle SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE,
    equipement_id INTEGER REFERENCES equipements(id_equipement) ON DELETE CASCADE,
    type_controle controle_type NOT NULL,
    date_verification DATE NOT NULL,
    resultat metrologie_resultat DEFAULT 'CONFORME',
    prestataire VARCHAR(200),
    cout DECIMAL(10,2),
    devise VARCHAR(3) DEFAULT 'DA',
    prochaine_echeance DATE,
    certificat_numero VARCHAR(100),
    certificat_path VARCHAR(500),
    temperature_ambiante DECIMAL(5,2),
    humidite_ambiante DECIMAL(5,2),
    incertitude_mesure VARCHAR(100),
    commentaires TEXT,
    technicien_responsable VARCHAR(100),
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Projets et utilisation opérationnelle
CREATE TABLE projets (
    id_projet SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE,
    nom VARCHAR(200) NOT NULL,
    description TEXT,
    service_id INTEGER REFERENCES services(id) ON DELETE SET NULL,
    date_debut DATE,
    date_fin DATE,
    statut projet_statut DEFAULT 'ACTIF',
    budget_alloue DECIMAL(12,2),
    budget_consomme DECIMAL(12,2) DEFAULT 0,
    responsable VARCHAR(100),
    priorite INTEGER DEFAULT 3 CHECK (priorite BETWEEN 1 AND 5),
    avancement_pourcentage DECIMAL(5,2) DEFAULT 0 CHECK (avancement_pourcentage BETWEEN 0 AND 100),
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Association équipements-projets
CREATE TABLE equipement_projets (
    equipement_id INTEGER REFERENCES equipements(id_equipement) ON DELETE CASCADE,
    projet_id INTEGER REFERENCES projets(id_projet) ON DELETE CASCADE,
    date_affectation DATE DEFAULT CURRENT_DATE,
    date_liberation DATE,
    taux_utilisation DECIMAL(5,2) CHECK (taux_utilisation BETWEEN 0 AND 100),
    commentaires TEXT,
    PRIMARY KEY (equipement_id, projet_id)
);

-- Interventions de maintenance
CREATE TABLE interventions (
    id_intervention SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE,
    equipement_id INTEGER REFERENCES equipements(id_equipement) ON DELETE CASCADE,
    type_intervention intervention_type NOT NULL,
    date_intervention DATE NOT NULL,
    date_fin_intervention DATE,
    description TEXT NOT NULL,
    technicien VARCHAR(100),
    cout DECIMAL(10,2),
    duree_heures DECIMAL(5,2),
    statut intervention_statut DEFAULT 'PLANIFIEE',
    pieces_changees TEXT,
    fournisseur VARCHAR(200),
    numero_bon_commande VARCHAR(50),
    garantie_mois INTEGER,
    commentaires TEXT,
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Formations du personnel
CREATE TABLE formations (
    id_formation SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE,
    titre VARCHAR(200) NOT NULL,
    description TEXT,
    formateur VARCHAR(100),
    organisme VARCHAR(200),
    date_formation DATE,
    duree_heures INTEGER,
    service_id INTEGER REFERENCES services(id) ON DELETE SET NULL,
    participants TEXT[], -- Array PostgreSQL
    cout DECIMAL(10,2),
    lieu VARCHAR(200),
    certificat_obtenu BOOLEAN DEFAULT FALSE,
    validite_mois INTEGER,
    competences_acquises TEXT[],
    evaluation_satisfaction DECIMAL(3,1) CHECK (evaluation_satisfaction BETWEEN 0 AND 10),
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Licences logicielles et réglementaires
CREATE TABLE licences (
    id_licence SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE,
    nom VARCHAR(200) NOT NULL,
    type_licence licence_type NOT NULL,
    fournisseur VARCHAR(200),
    version VARCHAR(50),
    date_acquisition DATE,
    date_expiration DATE,
    cout_annuel DECIMAL(10,2),
    nombre_postes INTEGER DEFAULT 1,
    postes_utilises INTEGER DEFAULT 0,
    statut licence_statut DEFAULT 'ACTIVE',
    contact_support VARCHAR(200),
    email_support VARCHAR(200),
    telephone_support VARCHAR(50),
    cle_licence TEXT,
    commentaires TEXT,
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Budgets et investissements
CREATE TABLE budgets (
    id_budget SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE,
    annee INTEGER NOT NULL,
    service_id INTEGER REFERENCES services(id) ON DELETE SET NULL,
    poste_budgetaire VARCHAR(100) NOT NULL,
    budget_alloue DECIMAL(12,2) NOT NULL,
    budget_consomme DECIMAL(12,2) DEFAULT 0,
    budget_engage DECIMAL(12,2) DEFAULT 0,
    responsable VARCHAR(100),
    date_validation DATE,
    commentaires TEXT,
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table d'audit pour traçabilité
CREATE TABLE audit_log (
    id_audit SERIAL PRIMARY KEY,
    table_name VARCHAR(50) NOT NULL,
    record_id INTEGER NOT NULL,
    action VARCHAR(10) NOT NULL, -- INSERT, UPDATE, DELETE
    old_values JSONB,
    new_values JSONB,
    user_id VARCHAR(100),
    ip_address INET,
    user_agent TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- 5. CONTRAINTES D'INTÉGRITÉ
-- =============================================================================

-- Contraintes sur les équipements
ALTER TABLE equipements ADD CONSTRAINT chk_annee_acquisition 
    CHECK (annee_acquisition >= 1990 AND annee_acquisition <= EXTRACT(YEAR FROM CURRENT_DATE) + 1);

ALTER TABLE equipements ADD CONSTRAINT chk_valeur_positive 
    CHECK (valeur_acquisition >= 0);

-- Contraintes sur la métrologie
ALTER TABLE metrologie ADD CONSTRAINT chk_cout_positif 
    CHECK (cout >= 0);

ALTER TABLE metrologie ADD CONSTRAINT chk_date_coherente 
    CHECK (prochaine_echeance >= date_verification);

-- Contraintes sur les budgets
ALTER TABLE budgets ADD CONSTRAINT chk_budget_coherent 
    CHECK (budget_consomme <= budget_alloue);

ALTER TABLE budgets ADD CONSTRAINT chk_budget_engage_coherent 
    CHECK (budget_engage <= budget_alloue);

-- Contraintes sur les licences
ALTER TABLE licences ADD CONSTRAINT chk_postes_coherents 
    CHECK (postes_utilises <= nombre_postes);

-- =============================================================================
-- 6. INDEX POUR LES PERFORMANCES
-- =============================================================================

-- Index sur les équipements
CREATE INDEX idx_equipements_service ON equipements(service_id);
CREATE INDEX idx_equipements_etat ON equipements(etat);
CREATE INDEX idx_equipements_prochaine_verif ON equipements(prochaine_verification);
CREATE INDEX idx_equipements_numero ON equipements(numero);
CREATE INDEX idx_equipements_inventaire ON equipements(n_inventaire);

-- Index sur la métrologie
CREATE INDEX idx_metrologie_equipement ON metrologie(equipement_id);
CREATE INDEX idx_metrologie_date ON metrologie(date_verification);
CREATE INDEX idx_metrologie_echeance ON metrologie(prochaine_echeance);

-- Index sur les interventions
CREATE INDEX idx_interventions_equipement ON interventions(equipement_id);
CREATE INDEX idx_interventions_date ON interventions(date_intervention);
CREATE INDEX idx_interventions_statut ON interventions(statut);

-- Index sur les projets
CREATE INDEX idx_projets_service ON projets(service_id);
CREATE INDEX idx_projets_statut ON projets(statut);
CREATE INDEX idx_projets_dates ON projets(date_debut, date_fin);

-- Index pour la recherche full-text
CREATE INDEX idx_equipements_search ON equipements USING gin(to_tsvector('french', description || ' ' || COALESCE(marque_type, '')));
CREATE INDEX idx_projets_search ON projets USING gin(to_tsvector('french', nom || ' ' || COALESCE(description, '')));

-- =============================================================================
-- 7. FONCTIONS ET TRIGGERS
-- =============================================================================

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

CREATE TRIGGER update_projets_modtime 
    BEFORE UPDATE ON projets 
    FOR EACH ROW EXECUTE FUNCTION update_modified_column();

CREATE TRIGGER update_interventions_modtime 
    BEFORE UPDATE ON interventions 
    FOR EACH ROW EXECUTE FUNCTION update_modified_column();

CREATE TRIGGER update_licences_modtime 
    BEFORE UPDATE ON licences 
    FOR EACH ROW EXECUTE FUNCTION update_modified_column();

CREATE TRIGGER update_budgets_modtime 
    BEFORE UPDATE ON budgets 
    FOR EACH ROW EXECUTE FUNCTION update_modified_column();

-- Fonction de calcul automatique de la prochaine vérification
CREATE OR REPLACE FUNCTION calculate_next_verification()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.date_derniere_verification IS NOT NULL AND NEW.frequence_verification_mois IS NOT NULL THEN
        NEW.prochaine_verification = NEW.date_derniere_verification + (NEW.frequence_verification_mois || ' months')::INTERVAL;
    END IF;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER calculate_equipement_next_verification 
    BEFORE INSERT OR UPDATE ON equipements 
    FOR EACH ROW EXECUTE FUNCTION calculate_next_verification();

-- =============================================================================
-- 8. VUES MÉTIER POUR LES DASHBOARDS
-- =============================================================================

-- Vue des équipements avec alertes métrologiques
CREATE VIEW v_alertes_metrologie AS
SELECT 
    e.id_equipement,
    e.uuid,
    e.numero,
    e.description,
    e.marque_type,
    s.nom as service,
    s.code as service_code,
    e.prochaine_verification,
    e.statut_metrologique,
    CASE 
        WHEN e.prochaine_verification < CURRENT_DATE THEN 'EXPIRE'
        WHEN e.prochaine_verification < CURRENT_DATE + INTERVAL '30 days' THEN 'ALERTE'
        WHEN e.prochaine_verification < CURRENT_DATE + INTERVAL '60 days' THEN 'ATTENTION'
        ELSE 'OK'
    END as statut_alerte,
    CURRENT_DATE - e.prochaine_verification as jours_retard
FROM equipements e
LEFT JOIN services s ON e.service_id = s.id
WHERE e.prochaine_verification IS NOT NULL
    AND e.etat NOT IN ('REBUT', 'REFORME');

-- Vue des KPI par service
CREATE VIEW v_kpi_services AS
SELECT 
    s.id as service_id,
    s.code,
    s.nom as service,
    COUNT(e.id_equipement) as total_equipements,
    COUNT(CASE WHEN e.etat = 'OK' THEN 1 END) as equipements_ok,
    COUNT(CASE WHEN e.etat = 'EN_PANNE' THEN 1 END) as equipements_panne,
    COUNT(CASE WHEN e.etat = 'MAINTENANCE' THEN 1 END) as equipements_maintenance,
    ROUND(
        COUNT(CASE WHEN e.etat = 'OK' THEN 1 END)::DECIMAL / 
        NULLIF(COUNT(e.id_equipement), 0) * 100, 2
    ) as taux_disponibilite,
    COUNT(CASE WHEN e.prochaine_verification < CURRENT_DATE THEN 1 END) as verifications_expirees,
    COUNT(CASE WHEN e.prochaine_verification < CURRENT_DATE + INTERVAL '30 days' THEN 1 END) as verifications_a_prevoir
FROM services s
LEFT JOIN equipements e ON s.id = e.service_id
WHERE e.etat IS NULL OR e.etat NOT IN ('REBUT', 'REFORME')
GROUP BY s.id, s.code, s.nom;

-- Vue des coûts de maintenance par équipement
CREATE VIEW v_couts_maintenance AS
SELECT 
    e.id_equipement,
    e.numero,
    e.description,
    s.nom as service,
    COUNT(i.id_intervention) as nb_interventions,
    COALESCE(SUM(i.cout), 0) as cout_total_maintenance,
    COALESCE(AVG(i.cout), 0) as cout_moyen_intervention,
    MAX(i.date_intervention) as derniere_intervention
FROM equipements e
LEFT JOIN services s ON e.service_id = s.id
LEFT JOIN interventions i ON e.id_equipement = i.equipement_id
WHERE e.etat NOT IN ('REBUT', 'REFORME')
GROUP BY e.id_equipement, e.numero, e.description, s.nom;

-- Vue du planning métrologique
CREATE VIEW v_planning_metrologique AS
SELECT 
    e.id_equipement,
    e.numero,
    e.description,
    s.nom as service,
    e.prochaine_verification,
    e.frequence_verification_mois,
    e.criticite,
    EXTRACT(YEAR FROM e.prochaine_verification) as annee_verification,
    EXTRACT(MONTH FROM e.prochaine_verification) as mois_verification,
    CASE 
        WHEN e.prochaine_verification < CURRENT_DATE THEN 1
        WHEN e.prochaine_verification < CURRENT_DATE + INTERVAL '30 days' THEN 2
        WHEN e.prochaine_verification < CURRENT_DATE + INTERVAL '60 days' THEN 3
        ELSE 4
    END as priorite_verification
FROM equipements e
LEFT JOIN services s ON e.service_id = s.id
WHERE e.prochaine_verification IS NOT NULL
    AND e.etat NOT IN ('REBUT', 'REFORME')
ORDER BY priorite_verification, e.prochaine_verification;

-- =============================================================================
-- 9. DONNÉES DE RÉFÉRENCE
-- =============================================================================

-- Insertion des services
INSERT INTO services (code, nom, responsable, description) VALUES
('CTS', 'Centre Technique Spécialisé', 'Chef CTS', 'Service technique principal'),
('CEM', 'Centre d''Études Maritimes', 'Chef CEM', 'Études et recherche maritime'),
('DSC', 'Direction Scientifique et Contrôle', 'Directeur DSC', 'Direction scientifique'),
('INT', 'Instrumentation', 'Chef Instrumentation', 'Service instrumentation');

-- =============================================================================
-- 10. FONCTIONS UTILITAIRES
-- =============================================================================

-- Fonction de recherche full-text
CREATE OR REPLACE FUNCTION search_equipements(search_term TEXT)
RETURNS TABLE (
    id_equipement INTEGER,
    numero VARCHAR(50),
    description TEXT,
    marque_type VARCHAR(200),
    service_nom VARCHAR(100),
    rank REAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        e.id_equipement,
        e.numero,
        e.description,
        e.marque_type,
        s.nom as service_nom,
        ts_rank(to_tsvector('french', e.description || ' ' || COALESCE(e.marque_type, '')), plainto_tsquery('french', search_term)) as rank
    FROM equipements e
    LEFT JOIN services s ON e.service_id = s.id
    WHERE to_tsvector('french', e.description || ' ' || COALESCE(e.marque_type, '')) @@ plainto_tsquery('french', search_term)
    ORDER BY rank DESC;
END;
$$ LANGUAGE plpgsql;

-- Fonction de calcul des statistiques globales
CREATE OR REPLACE FUNCTION get_dashboard_stats()
RETURNS JSON AS $$
DECLARE
    result JSON;
BEGIN
    SELECT json_build_object(
        'total_equipements', (SELECT COUNT(*) FROM equipements WHERE etat NOT IN ('REBUT', 'REFORME')),
        'equipements_ok', (SELECT COUNT(*) FROM equipements WHERE etat = 'OK'),
        'equipements_panne', (SELECT COUNT(*) FROM equipements WHERE etat = 'EN_PANNE'),
        'verifications_expirees', (SELECT COUNT(*) FROM equipements WHERE prochaine_verification < CURRENT_DATE),
        'interventions_mois', (SELECT COUNT(*) FROM interventions WHERE date_intervention >= DATE_TRUNC('month', CURRENT_DATE)),
        'cout_maintenance_annee', (SELECT COALESCE(SUM(cout), 0) FROM interventions WHERE EXTRACT(YEAR FROM date_intervention) = EXTRACT(YEAR FROM CURRENT_DATE)),
        'projets_actifs', (SELECT COUNT(*) FROM projets WHERE statut = 'ACTIF'),
        'licences_expire_bientot', (SELECT COUNT(*) FROM licences WHERE date_expiration < CURRENT_DATE + INTERVAL '60 days' AND statut = 'ACTIVE')
    ) INTO result;
    
    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- COMMENTAIRES FINAUX
-- =============================================================================

COMMENT ON DATABASE instrumentation_maritime IS 'Base de données moderne pour la gestion d''équipements d''instrumentation maritime - LEM 2025';

-- Fin du schéma
-- Version: 1.0.0
-- Date: 2025-08-12
-- Auteur: Nexus AI Software Architect
