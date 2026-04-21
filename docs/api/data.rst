Donnees
=======

Organisation des projets
------------------------

Chaque projet gere par ``ProjectManager`` est structure comme suit:

.. code-block:: text

   <projet>/
   ├── data/
   ├── sessions/
   ├── exports/
   ├── analysis/
   ├── calibration/
   └── project_metadata.json

Formats d'echange
-----------------

``CSV``
   Format simple pour export et relecture dans l'analyse.

``JSON``
   Format de session et de resultats facilement inspectable.

``HDF5``
   Format de stockage riche active quand ``h5py`` est disponible.

Metadonnees
-----------

Le fichier ``project_metadata.json`` contient au minimum l'identite du projet et les informations saisies a la creation.

Emplacement par defaut
----------------------

Les projets sont stockes sous ``~/CHNeoWave_Projects``.
