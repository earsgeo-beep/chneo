Analyse
=======

Modules actifs
--------------

``hrneowave.gui.views.analysis_view``
   Vue Qt chargee de selectionner un fichier d'entree, de lancer le traitement et d'afficher un resume des resultats.

``hrneowave.core.post_processor``
   Orchestrateur capable de lire ``csv``, ``json`` et ``hdf5`` sans charger en
   bloc les longues sessions, puis d'exporter les resultats.

``hrneowave.core.wave_analysis``
   Moteur scientifique pour Welch, moments spectraux, parametres ITTC,
   zero-upcrossing, coherence, phase et indicateurs de qualite.

Formats supportes
-----------------

- entree: ``csv``, ``json``, ``h5``, ``hdf5``
- sortie: ``csv``, ``json``, ``hdf5``, ``txt``

Dependances
-----------

- ``numpy`` pour les calculs
- ``pandas`` pour CSV
- ``h5py`` pour HDF5
