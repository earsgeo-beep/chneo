Guide utilisateur
=================

Vue d'ensemble
--------------

L'application active suit un enchainement simple:

1. creer un projet
2. parametrer une acquisition
3. exporter les donnees de session
4. charger un fichier dans l'analyse
5. produire un rapport exportable

Creation de projet
------------------

Depuis l'ecran d'accueil, la creation de projet alimente ``ProjectManager``. Le projet est stocke sous ``~/CHNeoWave_Projects`` avec un ``project_metadata.json`` et les sous-repertoires standards:

- ``data/``
- ``sessions/``
- ``exports/``
- ``analysis/``
- ``calibration/``

Acquisition
-----------

La vue active est ``AcquisitionConfigView``.

Fonctions actuellement branchees:

- demarrage et arret d'acquisition
- calibration et signal de fin de calibration
- export ``csv``, ``json`` et ``hdf5``
- emission automatique du fichier exporte vers la vue d'analyse

Quand aucun materiel MCC n'est detecte, le controleur peut fonctionner en mode simulation.

Limite actuelle:

- les boutons de chargement et sauvegarde de configuration affichent encore un message ``non implemente``

Analyse
-------

La vue active est ``AnalysisView``. Elle peut charger:

- ``.csv``
- ``.json``
- ``.h5``
- ``.hdf5``

Les analyses exposees dans l'interface sont:

- ``statistics``
- ``spectral``
- ``temporal``
- ``correlation``

Le traitement est delegue a ``PostProcessor`` qui produit un resume et des resultats exportables.

Rapports
--------

La vue active est ``ReportView``. Elle recoit le contexte projet et les resultats d'analyse puis permet l'export:

- ``html``
- ``txt``
- ``json``
- ``pdf``

Par defaut, les rapports sont sauvegardes dans ``<projet>/exports`` lorsque le contexte projet existe.

Lancement
---------

Les points d'entree valides sont:

- ``python chneowave.py``
- ``python main.py``
- ``python -m hrneowave``
- ``CHNeoWave.bat``

Dependances utiles
------------------

- ``PySide6`` pour la GUI
- ``numpy`` pour le calcul numerique
- ``pandas`` pour certains chargements/export CSV
- ``h5py`` pour HDF5
