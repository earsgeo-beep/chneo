Analyse
=======

Modules actifs
--------------

``hrneowave.gui.views.analysis_view``
   Vue Qt chargee de selectionner un fichier d'entree, de lancer le traitement et d'afficher un resume des resultats.

``hrneowave.core.post_processor``
   Moteur de post-traitement capable de lire ``csv``, ``json`` et ``hdf5`` puis de calculer statistiques, spectres et metriques de type Goda.

Formats supportes
-----------------

- entree: ``csv``, ``json``, ``h5``, ``hdf5``
- sortie: ``csv``, ``json``, ``hdf5``, ``txt``

Dependances
-----------

- ``numpy`` pour les calculs
- ``pandas`` pour CSV
- ``h5py`` pour HDF5
