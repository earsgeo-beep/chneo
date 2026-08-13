Documentation CHNeoWave
=======================

Cette documentation couvre le flux de laboratoire actif au 9 aout 2026:

- creation de projet
- detection d'un equipement physique par un pilote interchangeable
- calibration des chaines capteur
- acquisition physique avec HDF5 maitre obligatoire
- export des donnees
- analyse post-acquisition
- generation de rapport

Le depot ne doit plus etre lu comme un prototype web ni comme une release autonome prepackagee.

.. toctree::
   :maxdepth: 2
   :caption: Guides

   user_guide
   technical_guide
   mcc_first_test
   mcc_qualification_protocol
   data_analysis
   scientific_processing_v2
   scientific_analysis_workspace
   interface_design
   laboratory_platform_architecture_2026-08-09

.. toctree::
   :maxdepth: 2
   :caption: Reference

   api/analysis
   api/core
   api/data
   api/gui
   api/utils

Demarrage rapide
----------------

.. code-block:: powershell

   python -m venv .venv
   .venv\Scripts\Activate.ps1
   pip install -e ".[mcc]"
   python chneowave.py

Points a retenir
----------------

- ``PySide6`` est requis dans l'etat actuel du depot
- ``pandas`` est necessaire pour certains flux CSV
- ``h5py`` est necessaire pour le support HDF5
- le premier pilote livre cible la MCC USB-1608FS
- le noyau metier ne depend pas de MCC et accepte de futurs pilotes
- sans materiel physique connecte, l'acquisition est verrouillee
