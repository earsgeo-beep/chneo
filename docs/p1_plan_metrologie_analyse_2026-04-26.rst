Plan P1: metrologie, analyse PSD et validation terrain
======================================================

Date: 2026-04-26

Statut d'entree
---------------

Le bloc P0 est accepte provisoirement:

* zero-crossing corrige et teste;
* PSD one-sided normalisee et testee contre variance temporelle;
* ``zero_crossing_metrics`` separe du vrai Goda;
* pseudo-inverse complexe corrigee;
* simulation pression compatible avec la plage DAQ;
* contrat de temps et metadonnees renforce;
* NaN/Inf refuses explicitement.

La calibration reste volontairement en etat ``not_performed``. C'est correct
pour la securite scientifique, mais ce n'est pas encore une calibration
metrologique exploitable.

Objectif P1
-----------

Transformer CHNeoWave d'un pipeline mathematiquement securise en une chaine
metrologique utilisable en laboratoire de modele reduit.

P1 ne doit pas ajouter d'effets visuels ou de fonctions nouvelles non
mesurables. Chaque ajout doit renforcer la tracabilite, la reproductibilite ou
la validite scientifique.

Decoupage sans carte MCC
------------------------

La carte MCC n'est pas disponible au moment de l'ouverture P1. Cela ne bloque
pas le travail scientifique, mais impose une separation stricte:

P1-A - software-only, executable maintenant:

* noyau ``CalibrationRecord`` et ``CalibrationPoint``;
* ajustement lineaire reproductible;
* calcul ``offset_volts``, ``scale``, ``sensitivity_v_per_unit``,
  ``r_squared``, residus et incertitude;
* refus des calibrations invalides;
* application ``raw_voltage -> physical_value``;
* export/import du record;
* schema session strict JSON/HDF5/CSV sidecar;
* clarification periodogramme vs Welch;
* tests unitaires analytiques et signaux simules;
* preparation d'une couche ``DaqBackend`` simulation/replay.

P1-B - hardware MCC, a faire plus tard avec la carte:

* verification InstaCal / Universal Library;
* acquisition reelle courte;
* verification du ``sample_rate`` reel;
* verification de la shape ``[samples, channels]``;
* saturation tension;
* mapping canal-capteur;
* pertes d'echantillons;
* bruit reel de la carte;
* export/reload HDF5 depuis acquisition reelle.

Statut obligatoire tant que la carte n'est pas disponible:

.. code-block:: text

   MCC hardware validation: pending_hardware

Les exports, rapports et metadonnees doivent conserver
``hardware_validation_status = pending_hardware`` tant que P1-B n'a pas ete
execute avec une carte reelle.

Priorite 1 - Calibration metrologique reelle
--------------------------------------------

Objectif:

* remplacer le statut ``not_performed`` par une procedure capable de produire
  un ``CalibrationRecord`` valide;
* conserver date, operateur, reference, methode, incertitude, unite, capteur,
  canal et revision;
* appliquer uniquement des coefficients valides et tracables.

Contrat minimal d'un enregistrement de calibration:

.. code-block:: text

   calibration_id
   sensor_id
   channel
   sensor_type
   date_utc
   operator
   method
   reference_equipment
   reference_values_physical
   measured_values_volts
   offset_volts
   scale
   sensitivity_v_per_unit
   uncertainty
   r_squared
   residuals
   validity_status
   validity_reason

Tests requis:

* ajustement lineaire sur points de reference connus;
* refus si moins de deux points;
* refus si reference non monotone ou plage invalide;
* refus si ``r_squared`` trop faible;
* application predictable de la calibration a une tension brute;
* export/import du record sans perte.

Critere de sortie:

* un canal actif peut passer de ``unverified`` a ``valid`` uniquement via un
  record reproductible;
* les exports portent le ``calibration_id`` valide;
* les rapports affichent explicitement le statut de calibration.

Priorite 2 - Periodogramme vs Welch
-----------------------------------

Etat actuel:

* le calcul PSD actif est un periodogramme global one-sided;
* la configuration contient encore ``overlap``;
* ``overlap`` ne doit pas donner l'impression qu'une methode Welch est active.

Decision a prendre:

Option A:

* garder le periodogramme global;
* documenter ``psd_method = one_sided_periodogram``;
* ignorer ou masquer ``overlap`` dans l'interface.

Option B:

* implementer Welch reel;
* segmenter le signal;
* appliquer fenetre par segment;
* utiliser recouvrement;
* moyenner les PSD;
* exporter ``segment_length``, ``overlap``, ``window`` et ``n_segments``.

Critere de sortie:

* aucun champ ``overlap`` ne doit apparaitre comme applique si la methode n'est
  pas Welch;
* les resultats spectraux doivent porter ``psd_method`` et ses parametres.

Priorite 3 - Validation des raw_channels
----------------------------------------

Objectif:

* verifier la presence, la forme et la coherence de ``raw_channels`` quand le
  fichier pretend contenir des donnees brutes;
* garantir que ``raw`` et ``physical`` ont meme nombre d'echantillons et memes
  canaux;
* verifier que la reconversion raw -> physical est possible avec la calibration
  declaree.

Tests requis:

* HDF5 avec raw et physical coherents accepte;
* HDF5 avec longueur raw differente refuse;
* JSON avec canal brut manquant signale un warning;
* donnees physiques sans raw restent acceptables mais marquees comme derivees.

Priorite 4 - Schema formel
--------------------------

Objectif:

* definir un schema de session pour JSON/HDF5/CSV sidecar;
* rendre obligatoires les champs critiques;
* centraliser la validation avant analyse.

Champs obligatoires:

.. code-block:: text

   schema_version
   sample_rate_hz
   dt_seconds
   n_samples
   duration_s
   time_start
   time_end
   clock_domain
   data_kind
   channels
   channel_metadata
   sensor_id
   physical_units
   calibration_status
   calibration_coefficients
   conversion_formula
   warnings

Critere de sortie:

* un fichier incomplet echoue avant analyse;
* un fichier degrade peut etre charge seulement avec warning explicite;
* HDF5 reste le format canonique.

Priorite 5 - Tests terrain MCC/DAQ
----------------------------------

Objectif:

* verifier le comportement avec la carte reelle ou un dump MCC representatif;
* tester shape, saturation, cadence, timestamps et pertes de donnees.

Tests requis:

* acquisition courte avec Fs cible;
* verification ``samples_acquired / duration``;
* detection de saturation tension;
* verification shape ``[samples, channels]``;
* export/reload HDF5 sans perte critique.

Decision immediate
------------------

La premiere implementation P1 doit commencer par le noyau calibration, pas par
l'interface:

1. creer les structures ``CalibrationRecord`` et ``CalibrationPoint``;
2. implementer un ajustement lineaire reproductible;
3. calculer residus, ``r_squared`` et incertitude simple;
4. ajouter tests unitaires;
5. seulement ensuite brancher l'interface.

Etat P1-A apres demarrage
-------------------------

P1-A.1 a P1-A.2 sont engages:

* ``CalibrationPoint`` et ``CalibrationRecord`` existent dans le noyau;
* l'ajustement lineaire refuse les donnees insuffisantes, non finies, non
  monotones ou avec ``r_squared`` trop faible;
* la conversion appliquee reste explicite:
  ``physical = ((raw_voltage + offset_volts) * scale) / sensitivity_v_per_unit``;
* un canal ne peut passer a ``valid`` que via un ``CalibrationRecord`` valide;
* les metadonnees conservent ``hardware_validation_status = pending_hardware``
  sans carte MCC.

P1-A.5 est engage:

* ``DaqBackend`` definit le contrat commun;
* ``SimulatedDaqBackend`` produit des tensions brutes a partir de signaux
  analytiques;
* ``FileReplayBackend`` rejoue un fichier deja valide sans perdre ``time`` ni
  ``sample_rate_hz``;
* ``MccDaqBackend`` reste un adaptateur, avec validation terrain non terminee;
* la detection de risque de saturation de tension est disponible, sans
  remplacer la validation hardware P1-B.
