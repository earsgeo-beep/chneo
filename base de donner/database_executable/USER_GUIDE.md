# Guide Utilisateur - Système de Gestion d'Instrumentation Maritime

## Introduction

Le Système de Gestion d'Instrumentation Maritime est une solution moderne et professionnelle développée pour le Laboratoire d'Études Maritimes (LEM). Cette application permet la gestion complète des équipements d'instrumentation scientifique et maritime, incluant le suivi métrologique, la maintenance, et la gestion des projets.

## Fonctionnalités Principales

### 📊 Dashboard Interactif
- **Statistiques en temps réel** : Vue d'ensemble des équipements, pannes, et conformité métrologique
- **Alertes automatiques** : Notifications pour les échéances d'étalonnage et maintenances
- **Graphiques dynamiques** : Répartition par service, état des équipements, évolution des coûts
- **KPI par service** : Taux de disponibilité, nombre d'interventions, budget consommé

### 🔧 Gestion des Équipements
- **Inventaire complet** : 230+ équipements répartis sur 4 services (CTS, CEM, DSC, INT)
- **Recherche avancée** : Filtrage par service, état, type, localisation
- **Fiche détaillée** : Informations techniques, historique, documentation
- **Traçabilité complète** : Suivi des modifications, utilisateurs, dates

### 📏 Métrologie et Conformité
- **Planning métrologique** : Calendrier des vérifications et étalonnages
- **Gestion des certificats** : Stockage et suivi des documents de conformité
- **Alertes d'échéance** : Notifications 30 et 60 jours avant expiration
- **Conformité normative** : Respect des exigences ISO 9001 et ISO 10012

### 🔨 Maintenance et Interventions
- **Planification préventive** : Programmation des maintenances selon la criticité
- **Suivi des interventions** : Historique complet, coûts, pièces changées
- **Gestion des fournisseurs** : Contacts, garanties, contrats de maintenance
- **Analyse des pannes** : Statistiques et tendances pour optimiser la maintenance

## Interface Utilisateur

### Navigation Principale

L'interface est organisée en sections accessibles via le menu latéral :

1. **Dashboard** 📊 : Vue d'ensemble et statistiques
2. **Équipements** 🔧 : Gestion de l'inventaire
3. **Métrologie** 📏 : Suivi des vérifications
4. **Projets** 📋 : Gestion des projets techniques
5. **Maintenance** 🔨 : Interventions et réparations
6. **Rapports** 📈 : Analyses et exports

### Dashboard - Vue d'Ensemble

#### Statistiques Principales
- **Total Équipements** : Nombre total d'équipements actifs
- **Opérationnels** : Équipements en état de fonctionnement
- **En Panne** : Équipements nécessitant une réparation
- **Vérifications Expirées** : Équipements non conformes métrologiquement

#### Graphiques Interactifs
- **Répartition par Service** : Camembert montrant la distribution des équipements
- **État des Équipements** : Graphique en barres des différents états
- **Évolution des Coûts** : Courbe temporelle des dépenses de maintenance

#### Alertes Métrologiques
Tableau des équipements nécessitant une attention particulière :
- 🔴 **EXPIRE** : Vérification dépassée
- 🟡 **ALERTE** : Échéance dans les 30 jours
- 🟠 **ATTENTION** : Échéance dans les 60 jours

### Gestion des Équipements

#### Recherche et Filtrage
- **Barre de recherche** : Recherche textuelle dans les descriptions, numéros, marques
- **Filtre par service** : CTS, CEM, DSC, INT
- **Filtre par état** : OK, En Panne, Maintenance, Rebut, Réformé
- **Reset des filtres** : Bouton pour effacer tous les filtres

#### Actions Disponibles
- 👁️ **Voir** : Consulter les détails complets
- ✏️ **Modifier** : Éditer les informations
- 📋 **Historique** : Consulter l'historique des interventions
- 📅 **Planifier** : Programmer une vérification ou maintenance

#### Informations Affichées
- **Numéro d'équipement** : Identifiant unique
- **Description** : Nom et fonction de l'équipement
- **Marque/Type** : Fabricant et modèle
- **Service** : Service propriétaire
- **État actuel** : Statut opérationnel
- **Statut métrologique** : Conformité des vérifications

### Métrologie

#### Planning des Vérifications
- **Vue calendaire** : Visualisation mensuelle et annuelle
- **Priorités** : Classification par criticité (1-5)
- **Prestataires** : Gestion des organismes d'étalonnage
- **Coûts** : Suivi budgétaire des vérifications

#### Gestion des Certificats
- **Stockage numérique** : Upload et archivage des certificats
- **Numérotation** : Système de référencement unique
- **Validité** : Calcul automatique des échéances
- **Recherche** : Localisation rapide des documents

## Utilisation Quotidienne

### Démarrage de Session

1. **Accès à l'application** : Ouvrir le navigateur sur `http://localhost:8080`
2. **Authentification** : Saisir les identifiants (à implémenter)
3. **Dashboard** : Consultation des alertes et statistiques du jour

### Tâches Courantes

#### Vérification des Alertes (Quotidien)
1. Consulter le dashboard
2. Examiner les alertes métrologiques
3. Planifier les vérifications urgentes
4. Contacter les prestataires si nécessaire

#### Mise à Jour d'un Équipement
1. Aller dans "Équipements"
2. Rechercher l'équipement concerné
3. Cliquer sur "Modifier" ✏️
4. Mettre à jour les informations
5. Sauvegarder les modifications

#### Enregistrement d'une Intervention
1. Sélectionner l'équipement
2. Cliquer sur "Historique" 📋
3. Ajouter une nouvelle intervention
4. Renseigner : date, type, technicien, coût, description
5. Joindre les documents si nécessaire

#### Planification d'une Vérification
1. Identifier l'équipement dans les alertes
2. Cliquer sur "Planifier" 📅
3. Choisir le prestataire
4. Définir la date souhaitée
5. Valider la planification

### Rapports et Exports

#### Types de Rapports Disponibles
- **Inventaire complet** : Liste exhaustive des équipements
- **État métrologique** : Conformité par service
- **Coûts de maintenance** : Analyse financière
- **Taux de disponibilité** : Performance opérationnelle

#### Formats d'Export
- **Excel (.xlsx)** : Pour analyse et archivage
- **PDF** : Pour impression et diffusion
- **JSON** : Pour intégration avec d'autres systèmes

## Bonnes Pratiques

### Saisie des Données

#### Équipements
- **Numérotation cohérente** : Respecter le format EQ-XXX
- **Descriptions précises** : Inclure la fonction et les caractéristiques
- **Localisation détaillée** : Bâtiment, étage, laboratoire
- **Mise à jour régulière** : Actualiser lors des changements

#### Métrologie
- **Respect des échéances** : Programmer les vérifications à l'avance
- **Documentation complète** : Archiver tous les certificats
- **Suivi des coûts** : Enregistrer les factures et devis
- **Traçabilité** : Maintenir l'historique des vérifications

### Maintenance Préventive

#### Planification
- **Criticité** : Prioriser selon l'impact opérationnel
- **Fréquence** : Adapter selon l'utilisation et l'environnement
- **Ressources** : Planifier les interventions selon les disponibilités
- **Budget** : Anticiper les coûts et négocier les contrats

#### Suivi
- **Indicateurs** : Surveiller les taux de panne et disponibilité
- **Analyse des tendances** : Identifier les équipements problématiques
- **Amélioration continue** : Ajuster les stratégies de maintenance
- **Formation** : Maintenir les compétences techniques

## Dépannage Utilisateur

### Problèmes Courants

#### L'application ne se charge pas
1. Vérifier la connexion Internet
2. Contrôler que le serveur backend est démarré
3. Essayer de rafraîchir la page (F5)
4. Vider le cache du navigateur

#### Données non mises à jour
1. Cliquer sur "Actualiser" dans le dashboard
2. Vérifier la connexion à la base de données
3. Consulter les logs d'erreur
4. Contacter l'administrateur si le problème persiste

#### Recherche ne fonctionne pas
1. Vérifier l'orthographe des termes de recherche
2. Essayer des mots-clés plus courts
3. Utiliser les filtres en complément
4. Réinitialiser les filtres avec "Reset"

#### Export impossible
1. Vérifier les autorisations du navigateur
2. Désactiver temporairement le bloqueur de pop-up
3. Essayer un autre format d'export
4. Contacter le support technique

### Support Technique

#### Contacts
- **Administrateur système** : admin@lem.dz
- **Support utilisateur** : support@lem.dz
- **Documentation** : Consulter ce guide et l'aide en ligne

#### Informations à Fournir
- **Navigateur utilisé** : Chrome, Firefox, Edge, Safari
- **Message d'erreur** : Copie exacte du message
- **Actions effectuées** : Étapes qui ont mené au problème
- **Capture d'écran** : Si possible, joindre une image

## Évolutions Futures

### Fonctionnalités Prévues
- **Application mobile** : Accès depuis tablettes et smartphones
- **Notifications push** : Alertes en temps réel
- **Intelligence artificielle** : Prédiction des pannes
- **Intégration IoT** : Capteurs de surveillance automatique

### Améliorations Continues
- **Interface utilisateur** : Optimisation de l'ergonomie
- **Performances** : Accélération des temps de réponse
- **Sécurité** : Renforcement de la protection des données
- **Conformité** : Mise à jour selon les nouvelles normes

---

**Version** : 1.0.0  
**Date de publication** : 2025-08-12  
**Prochaine mise à jour** : 2025-09-12  

Pour toute question ou suggestion d'amélioration, n'hésitez pas à contacter l'équipe de développement.
