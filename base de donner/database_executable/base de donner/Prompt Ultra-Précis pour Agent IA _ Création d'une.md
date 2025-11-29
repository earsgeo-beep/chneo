<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# Prompt Ultra-Précis pour Agent IA : Création d'une Base de Données d'Instrumentation Maritime Moderne

## **CONTEXTE ET MISSION**

Vous êtes un expert en conception de bases de données chargé de créer une **base de données moderne et professionnelle** pour la gestion d'équipements d'instrumentation scientifique et maritime du Laboratoire d'Études Maritimes (LEM).

## **DONNÉES SOURCE À INTÉGRER**

### Structure Existante (23 feuilles Excel)

- **INVENTAIRE** : 230 équipements (4 services : CTS, CEM, DSC, INT)
- **MÉTROLOGIE** : 78 équipements sous contrôle + 208 enregistrements d'étalonnage
- **PROJETS** : 155 projets techniques (CTS: 101, CEM: 54)
- **FORMATIONS** : Historique complet des formations techniques
- **LICENCES** : 6 licences actives avec dates d'expiration
- **MAINTENANCE** : Suivi des interventions et pannes
- **INVESTISSEMENTS** : Budgets et acquisitions


## **ARCHITECTURE DE BASE DE DONNÉES MODERNE REQUISE**

### 1. **Structure Relationnelle Optimisée**

```sql
-- Tables principales à créer :
- EQUIPEMENTS (table centrale)
- METROLOGIE (contrôles/étalonnages)
- PROJETS (utilisation opérationnelle)
- INTERVENTIONS (maintenance/réparations)
- FORMATIONS (compétences personnel)
- LICENCES (autorisations réglementaires)
- BUDGETS (investissements/coûts)
```


### 2. **Champs Obligatoires par Table**

**EQUIPEMENTS :**

- ID_Equipement (PK), Numero, Description, Marque_Type, Serie, N_Inventaire
- Utilisateur, Service, Localisation, Etat, Annee_Acquisition
- Statut_Metrologique, Date_Derniere_Verification, Prochaine_Verification

**METROLOGIE :**

- ID_Controle (PK), FK_Equipement, Type_Controle, Date_Verification
- Resultat, Prestataire, Cout, Prochaine_Echeance, Certificat


## **FONCTIONNALITÉS MODERNES À IMPLÉMENTER**

### 1. **Dashboard Interactif**

- **KPI en temps réel** : Taux de conformité métrologique, équipements en retard
- **Alertes automatiques** : Échéances d'étalonnage, maintenances préventives
- **Cartes de localisation** : Répartition géographique des équipements


### 2. **Graphiques et Visualisations**

```
GRAPHIQUES REQUIS :
□ Répartition des équipements par service (camembert)
□ Évolution des coûts d'étalonnage (courbe temporelle)
□ Taux d'utilisation par projet (barres horizontales)
□ État du parc matériel (gauge/jauge)
□ Planning métrologique (diagramme de Gantt)
□ Analyse des pannes (heatmap)
□ Budget vs réalisé (graphique combiné)
```


### 3. **Formats de Données Standardisés**

- **Dates** : ISO 8601 (YYYY-MM-DD)
- **États** : Énumération contrôlée (OK, EN_PANNE, REBUT, REFORME)
- **Services** : Code normalisé (CTS, CEM, DSC, INT)
- **Coûts** : Format monétaire avec devise (DA)


## **INTERFACE UTILISATEUR MODERNE**

### 1. **Tableaux de Bord par Rôle**

- **Chef de Service** : Vue stratégique et budgétaire
- **Technicien** : Planification et suivi opérationnel
- **Métrologue** : Calendrier et conformité


### 2. **Fonctions de Recherche Avancée**

- Filtres multicritères
- Recherche full-text
- Tri dynamique
- Export vers Excel/PDF


## **TECHNOLOGIES RECOMMANDÉES**

### Base de Données

- **PostgreSQL** ou **SQL Server** (robustesse entreprise)
- Index optimisés sur champs recherchés
- Contraintes d'intégrité référentielle


### Interface Web

- **Framework moderne** : React.js, Vue.js ou Angular
- **Bibliothèques graphiques** : Chart.js, D3.js ou Plotly
- **Design responsive** : Compatible mobile/tablette


### API et Intégration

- **API REST** pour intégration système
- **Authentification** : JWT ou OAuth2
- **Logs d'audit** : Traçabilité complète


## **LIVRABLES ATTENDUS**

### 1. **Schéma de Base de Données**

- Diagramme entité-relation complet
- Scripts SQL de création
- Jeu de données de test


### 2. **Application Web**

- Interface d'administration
- Tableaux de bord interactifs
- Module de reporting


### 3. **Documentation**

- Guide utilisateur
- Manuel d'administration
- Procédures de sauvegarde


## **CRITÈRES DE PERFORMANCE**

### Technique

- **Temps de réponse** < 2 secondes
- **Disponibilité** > 99.5%
- **Sauvegarde automatique** quotidienne


### Fonctionnel

- **Conformité normative** ISO 9001 et 10012
- **Alertes automatiques** 30 jours avant échéance
- **Historique complet** avec horodatage


## **CONTRAINTES SPÉCIFIQUES**

### Données Métrologiques

- Respect des échéances réglementaires
- Traçabilité des certificats d'étalonnage
- Calcul automatique des prochaines vérifications


### Gestion Budgétaire

- Suivi des coûts par équipement
- Planification des investissements
- Alertes dépassement budget


## **VALIDATION ET TESTS**

### Tests de Performance

- Charge 1000 utilisateurs simultanés
- Import/export fichiers volumineux
- Génération rapports complexes


### Tests Fonctionnels

- Parcours utilisateur complet
- Intégrité des calculs
- Cohérence des données

***

**RÉSULTAT ATTENDU** : Une base de données moderne, intuitive et performante qui transforme la gestion papier actuelle en système digital professionnel, avec analytics avancés et interface utilisateur de niveau entreprise.

<div style="text-align: center">⁂</div>

[^1]: BDD-INST-2025.xlsx

