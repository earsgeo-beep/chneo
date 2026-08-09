Architecture de la plateforme de laboratoire
=============================================

:Date: 9 aout 2026
:Statut: architecture cible et plan d'execution

Vision
------

CHNeoWave doit devenir le poste de travail numerique du laboratoire maritime,
et non l'interface d'une carte particuliere. Une campagne doit rester
exploitable si le materiel d'acquisition change. Les projets, capteurs,
calibrations, controles qualite, traitements et rapports appartiennent donc au
noyau du laboratoire; les details MCC, IOtech, Keithley ou Amplicon restent
dans des pilotes isoles.

Regles non negociables
----------------------

1. Une acquisition de production exige un equipement physique detecte,
   connecte et valide par son pilote.
2. Aucune source artificielle n'est disponible dans le runtime de production.
   Les doubles deterministes restent confines a la suite de tests.
3. Le fichier HDF5 maitre est ouvert avant la lecture de la premiere mesure et
   alimente en continu. Le tampon memoire sert uniquement a l'affichage.
4. Une erreur d'acquisition, un debordement ou une erreur disque interdit le
   statut ``complete`` et bloque les exports presentes comme valides.
5. La tension brute, la grandeur physique, la calibration appliquee, la base
   de temps et l'identite du materiel restent tracables ensemble.
6. Un constructeur n'est annonce comme supporte qu'apres essais sur le
   materiel reel et validation d'un protocole reproductible.

Architecture cible
------------------

La plateforme est organisee en sept domaines.

.. list-table:: Domaines du laboratoire
   :header-rows: 1
   :widths: 21 34 45

   * - Domaine
     - Responsabilite
     - Objets principaux
   * - Campagnes
     - Decrire l'essai et son contexte
     - projet, bassin, maquette, eau, operateur, protocole
   * - Metrologie
     - Administrer les chaines de mesure
     - capteur, certificat, points, incertitude, validite
   * - Materiel
     - Decouvrir et piloter les equipements
     - registre, pilote, peripherique, capacites, diagnostic
   * - Acquisition
     - Orchestrer la mesure et l'enregistrement
     - session, canaux, horloge, declenchement, HDF5 maitre
   * - Qualite
     - Decider si les donnees sont recevables
     - saturation, lacunes, derive, bruit, debordements, integrite
   * - Science
     - Produire des resultats mathematiques explicites
     - spectres, vagues, coherence, reflexion, statistiques
   * - Rapports
     - Restituer et auditer une campagne
     - methode, resultats, graphiques, avertissements, provenance

Contrat des pilotes materiels
-----------------------------

Chaque pilote doit publier une identite de peripherique et des capacites
generiques: nombre de voies, plages electriques, frequences, debit agrege,
mode continu, horloge externe, declenchement et type d'entrees. Il doit ensuite
fournir les operations ``discover``, ``open/connect``, ``start``, ``read``,
``status``, ``stop`` et ``close``.

Le controleur scientifique ne connait que ce contrat. Il valide la
configuration avec les capacites publiees avant de demarrer. La calibration
adapte automatiquement son nombre de canaux au materiel selectionne.

Etat des familles de cartes
---------------------------

.. list-table:: Etat reel au 9 aout 2026
   :header-rows: 1
   :widths: 20 22 28 30

   * - Famille
     - Etat logiciel
     - Validation requise
     - Decision
   * - MCC USB-1608FS
     - pilote physique actif
     - 1 min, 10 min, 60 min puis essai long
     - premier pilote de reference
   * - IOtech
     - non livre
     - modele exact, SDK, horloge et essai reel
     - prochain pilote si necessaire aux 16 voies
   * - Keithley
     - non livre
     - modele, type de mesures et SDK
     - ajouter seulement pour un besoin defini
   * - Amplicon
     - non livre
     - modele, bus, pilote et synchronisation
     - ajouter seulement apres fiche materielle

La detection MCC utilise l'Universal Library et cree directement le
peripherique USB. Elle ne depend pas d'une configuration ``cb.cfg``. InstaCal
reste un outil constructeur optionnel pour diagnostiquer le pilote, le
firmware ou le cablage.

Synchronisation multi-cartes
-----------------------------

Additionner simplement 8 et 16 voies ne garantit pas une mesure scientifique
de 24 voies. Il faut etablir une base de temps commune. L'integration
multi-cartes devra choisir et documenter l'une des strategies suivantes:

* horloge echantillon externe partagee, solution privilegiee;
* declenchement commun avec horloges independantes, puis mesure et correction
  de derive si les SDK le permettent;
* acquisition non synchronisee, autorisee uniquement pour des grandeurs qui
  ne seront jamais comparees en phase.

Une session multi-cartes devra enregistrer pour chaque bloc l'identite de
l'equipement, son compteur materiel, sa frequence effective et tout evenement
de perte de synchronisation. Les analyses de coherence, phase et reflexion
seront bloquees si la synchronisation n'est pas attestee.

Modele de donnees recommande
----------------------------

Le fichier maitre doit evoluer sans casser les lecteurs existants:

* ``metadata/session``: campagne, operateur, versions et base de temps;
* ``metadata/devices``: pilotes, numeros de serie, firmwares et diagnostics;
* ``metadata/channels``: correspondance voie-capteur, unite et position;
* ``metadata/calibration``: certificat, coefficients, incertitude et validite;
* ``raw_voltage``: valeurs electriques originales, jamais remplacees;
* ``acquisition_data``: valeurs physiques issues de la calibration declaree;
* ``quality``: saturations, lacunes, derive, debordements et decisions;
* ``processing``: parametres, version d'algorithme et resultats scientifiques.

Le HDF5 reste le format d'archive et d'analyse prioritaire. CSV convient aux
extraits courts. JSON est utile pour l'interoperabilite, mais n'est pas
recommande pour les campagnes longues en raison de sa taille et de son cout
memoire a la relecture.

Laboratoire complet: modules a construire
-----------------------------------------

Priorite 1 - fiabilite de la mesure
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* terminer les essais MCC sur le PC Windows reel;
* executer et archiver les rapports de qualification automatique avant chaque campagne;
* mesurer le taux reel, les pertes, le bruit a entree court-circuitee et la
  saturation pour chaque plage;
* tester l'arret, la deconnexion USB et le disque plein sans presenter le
  fichier partiel comme valide;
* construire un paquet d'installation hors ligne signe et reproductible.

Priorite 2 - metrologie des capteurs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* catalogue des capteurs avec numero de serie et historique;
* certificats versionnes, dates de validite et reference metrologique;
* regression lineaire, non-lineaire ou polynomiale selon la famille;
* incertitude, residus, hysteresis et seuils d'acceptation;
* verrouillage d'une campagne si un certificat obligatoire est expire;
* association explicite ``equipement / voie / capteur / position``.

Priorite 3 - campagnes et protocoles
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* modeles de campagne reutilisables;
* checklist avant essai: cablage, zero, profondeur, geometrie, operateur;
* journal chronologique des actions et incidents;
* annotations pendant l'acquisition: changement de regime, evenement, arret;
* comparaison entre essais d'une meme campagne.

Priorite 4 - science modulaire
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* statistiques et detection robuste de valeurs aberrantes;
* Welch avec controle des segments, fenetre, recouvrement et resolution;
* vagues par passages au zero et comparaison spectral/temporel;
* coherence, phase et fonctions de transfert;
* separation incident/reflechi avec geometrie et qualite du systeme;
* analyse directionnelle seulement avec geometrie et synchronisation valides;
* filtres documentes, sans modifier silencieusement les donnees originales;
* propagation des incertitudes jusqu'aux resultats publies.

Priorite 5 - qualite, audit et rapports
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* tableau de recevabilite par canal et par session;
* hash du fichier maitre et manifeste des exports;
* version de CHNeoWave, des pilotes et des algorithmes dans chaque resultat;
* rapport automatique distinguant mesure, methode, resultat et avertissement;
* profils operateur, responsable et administrateur, sans revendiquer une
  conformite normative avant audit formel;
* sauvegarde locale et strategie de copie vers le stockage du laboratoire.

Plan d'execution
----------------

.. list-table:: Phases et portes de sortie
   :header-rows: 1
   :widths: 13 32 32 23

   * - Phase
     - Livraison
     - Porte de sortie
     - Risque principal
   * - 0 - socle
     - registre multi-pilotes, acquisition physique, HDF5 maitre, exports complets
     - tests automatises verts
     - regressions de l'ancien prototype
   * - 1 - MCC
     - moteur de qualification, rapports lies au maitre par hash et protocole terrain
     - 60 min, compte exact, zero perte
     - pilote Windows/USB
   * - 2 - metrologie
     - catalogue et certificats
     - chaine etalonnee et auditable
     - qualite des references
   * - 3 - multi-cartes
     - orchestrateur de peripheriques et horloge commune
     - derive mesuree sous le seuil fixe
     - synchronisation physique
   * - 4 - science
     - modules versionnes et jeux de reference
     - erreurs numeriques sous tolerances
     - interpretation incorrecte
   * - 5 - laboratoire
     - protocoles, audit, rapports et paquet hors ligne
     - campagne complete reproductible
     - exploitation et maintenance

Decision de version
-------------------

La version actuelle est un socle professionnel en refonte, pas encore un
logiciel qualifie pour une campagne critique de longue duree. La premiere
version exploitable au laboratoire doit etre declaree seulement apres la porte
MCC de 60 minutes, la verification des fichiers HDF5 et un essai de reprise
apres incident. Le support de 24 capteurs viendra ensuite avec la
synchronisation multi-cartes; il ne doit pas etre obtenu en empilant des
pilotes sans preuve de la base de temps commune.
