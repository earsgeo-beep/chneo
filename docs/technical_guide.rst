Guide technique
===============

Architecture utile
------------------

Le depot a ete reduit autour d'une chaine principale:

- ``chneowave.py`` et ``main.py`` pour le lancement
- ``src/hrneowave/cli.py`` pour l'initialisation Qt
- ``src/hrneowave/gui/main_window.py`` pour l'orchestration GUI
- ``src/hrneowave/gui/views/`` pour les ecrans actifs
- ``src/hrneowave/core/project_manager.py`` pour la persistence projet
- ``src/hrneowave/acquisition/acquisition_controller.py`` pour l'acquisition
- ``src/hrneowave/core/post_processor.py`` pour le post-traitement
- ``src/hrneowave/gui/views/report_view.py`` pour la sortie rapport

Flux runtime
------------

Le cablage actif dans ``MainWindow`` relie:

1. creation de projet depuis ``WelcomeView``
2. propagation du contexte projet aux vues qui exposent ``set_project_context``
3. export acquisition via ``data_exported``
4. chargement du fichier dans ``AnalysisView``
5. emission ``analysis_completed``
6. alimentation de ``ReportView`` via ``set_analysis_context``

Persistence projet
------------------

``ProjectManager`` cree les projets sous ``Path.home() / "CHNeoWave_Projects"``.

Metadonnees persistantes:

- ``project_metadata.json``
- structure de repertoires standard ``data``, ``sessions``, ``exports``, ``analysis``, ``calibration``

Contraintes techniques reelles
------------------------------

- ``ThemeManager`` importe directement ``PySide6``: dans l'etat actuel, ``PyQt6`` n'est pas un runtime garanti
- ``PostProcessor`` charge ``pandas`` pour CSV et ``h5py`` pour HDF5
- ``ReportView`` genere les PDF via ``QTextDocument`` et ``QPrinter``
- le backend MCC charge ``mcculw`` localement, au-dessus de l'Universal
  Library installee avec InstaCal

Stockage pendant l'acquisition MCC
----------------------------------

``ContinuousHDF5Recorder`` est branche directement au controleur MCC. Chaque
bloc est ecrit dans deux groupes extensibles: ``raw_voltage`` pour la mesure en
volts et ``acquisition_data`` pour la valeur physique calibree. Le tampon du
controleur sert uniquement a l'affichage recent et ne constitue pas le stockage
de reference.

Une erreur HDF5 interrompt l'acquisition et incremente ``recording_errors``.
Une session terminee normalement est marquee ``recording_status = complete``;
un fichier interrompu reste marque ``recording`` ou ``error`` afin d'eviter de
le confondre avec une acquisition valide.

Modules secondaires
-------------------

Le depot conserve encore des packages secondaires ``hardware``, ``tools`` et ``utils``. Ils sont documentes comme modules presents, pas comme flux principal garanti.

Limites ouvertes
----------------

- boutons de configuration acquisition encore non implementes
- couverture de tests automatisee encore minimale
- plusieurs modules secondaires n'ont pas encore ete reduits au strict necessaire
