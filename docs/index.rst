Documentation CHNeoWave
=======================

Cette documentation couvre le depot actif nettoye au 21 avril 2026. Elle decrit uniquement le flux reel aujourd'hui branche dans l'application desktop Qt:

- creation de projet
- acquisition ou simulation
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
   data_analysis

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
- le support MCC reste optionnel et depend du materiel cible
