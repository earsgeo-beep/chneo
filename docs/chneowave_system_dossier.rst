Dossier Systeme CHNeoWave
=========================

Objectif du document
--------------------

Ce document sert de reference complete sur le logiciel CHNeoWave dans son etat courant au 26 avril 2026. Il a deux objectifs:

1. expliquer clairement ce que le logiciel est, ce qu'il fait et comment il fonctionne reellement
2. servir de base de deep research pour corriger les problemes physiques, mathematiques et logiciels deja prouves

Ce document ne decrit pas un produit marketing idealise. Il decrit le depot reel, le runtime reel et les ecarts reels.

Resume executif
---------------

CHNeoWave est un logiciel desktop Python/Qt destine a un laboratoire d'etudes maritimes en modele reduit. Son intention metier est de couvrir toute la chaine d'un essai:

- creation d'un projet
- acquisition des mesures
- conversion vers des unites physiques
- analyse statistique et spectrale
- generation de rapport

Dans le depot actuel, cette chaine existe bien, mais elle n'est pas encore assez rigoureuse pour etre consideree comme une chaine scientifique fiable de niveau laboratoire. Le logiciel est aujourd'hui plus proche d'une base de travail technique et d'une IHM de demonstration avancee que d'un systeme metrologique totalement valide.

But metier du logiciel
----------------------

Le but de CHNeoWave est de centraliser la conduite d'essais maritimes sur modele reduit. Le logiciel est pense pour des campagnes experimentales en bassin, canal ou autre installation hydrodynamique.

Les usages cibles visibles dans le code sont:

- acquisition multi-canaux de capteurs de houle
- prise en charge de capteurs de pression, acceleration et temperature
- gestion de projets et de sessions d'essai
- export des donnees brutes et des resultats d'analyse
- production de rapports techniques

Ce que le logiciel n'est pas, dans l'etat actuel:

- ce n'est pas une application web active
- ce n'est pas une chaine de calibration tracee de bout en bout
- ce n'est pas encore un environnement de post-traitement scientifiquement verrouille

Ce qu'est le runtime actif
--------------------------

Le runtime reel du depot est une application desktop Qt lancee par:

- ``chneowave.py``
- ``main.py``
- ``python -m hrneowave``
- ``CHNeoWave.bat``

Le bootstrap principal passe par:

- ``src/hrneowave/cli.py``
- ``src/hrneowave/gui/main_window.py``
- ``src/hrneowave/gui/views/__init__.py``

Le code montre que la logique active suit ce cablage:

1. ``WelcomeView`` cree un projet
2. ``MainWindow`` charge le projet via ``ProjectManager``
3. le contexte projet est pousse vers acquisition, analyse et rapport
4. ``AcquisitionConfigView`` exporte un fichier
5. ``AnalysisView`` charge ce fichier et declenche ``PostProcessor``
6. ``ReportView`` recupere les resultats et genere les sorties finales

Architecture fonctionnelle actuelle
-----------------------------------

Gestion de projet
~~~~~~~~~~~~~~~~~

La couche projet est geree par ``src/hrneowave/core/project_manager.py``.

Le gestionnaire cree un espace de travail local sous ``~/CHNeoWave_Projects``. Chaque projet contient:

- ``data/``
- ``sessions/``
- ``exports/``
- ``analysis/``
- ``calibration/``
- ``project_metadata.json``

Le modele ``ProjectMetadata`` inclut deja des champs a valeur physique ou experimentale:

- ``basin_type``
- ``water_depth``
- ``wave_conditions``

Important: ces champs existent mais ils sont encore tres peu operes par la chaine active.

Acquisition
~~~~~~~~~~~

La couche active d'acquisition est porte par:

- ``src/hrneowave/gui/views/acquisition_config_view.py``
- ``src/hrneowave/acquisition/acquisition_controller.py``
- ``src/hrneowave/acquisition/mcc_daq_wrapper.py``

La vue acquisition permet:

- de choisir des canaux actifs
- d'associer un type de capteur, une plage de tension et une sensibilite
- de lancer et arreter l'acquisition
- d'exporter les donnees en ``csv``, ``json`` et ``hdf5``

Le controleur gere:

- la creation de session
- le mode materiel MCC
- le mode simulation
- la conversion tension -> unite physique
- l'export des donnees

Calibration
~~~~~~~~~~~

Une vue de calibration existe dans ``src/hrneowave/gui/views/calibration_view.py``. Elle est visuellement riche et structuree comme un module important de l'application.

Mais du point de vue de la chaine physique active:

- la calibration bas niveau MCC n'est pas implementee
- les corrections produites par ``calibrate_system()`` ne sont pas reinjectees dans les coefficients utilises pendant la conversion
- plusieurs indicateurs dans la vue sont encore decoratifs ou statiques

En consequence, la calibration existe dans l'IHM et dans le vocabulaire logiciel, mais pas encore comme une chaine metrologique fermee.

Analyse
~~~~~~~

La couche active d'analyse passe par:

- ``src/hrneowave/gui/views/analysis_view.py``
- ``src/hrneowave/core/post_processor.py``

``AnalysisView`` instancie directement ``PostProcessor`` et l'utilise comme moteur reel. Les modules ``optimized_fft_processor.py`` et ``optimized_goda_analyzer.py`` existent, mais ils ne sont pas relies au flux GUI actif.

La vue d'analyse charge:

- ``csv``
- ``json``
- ``h5``
- ``hdf5``

Le moteur calcule:

- statistiques descriptives
- analyse spectrale simple
- metriques de type Goda basees sur passages par zero et frequence de pic

Rapport et export
~~~~~~~~~~~~~~~~~

La couche rapport passe par ``src/hrneowave/gui/views/report_view.py``.

Le rapport GUI peut sortir:

- ``html``
- ``txt``
- ``json``
- ``pdf``

Le PDF GUI est genere avec ``QTextDocument`` et ``QPrinter``. Ce n'est pas le meme chemin que les utilitaires PDF annexes bases sur ``reportlab``.

Frameworks et dependances
-------------------------

Pile principale active
~~~~~~~~~~~~~~~~~~~~~~

- ``Python`` pour l'ensemble du logiciel
- ``PySide6`` pour la GUI active
- ``NumPy`` pour le calcul numerique
- ``pandas`` pour certains flux CSV dans l'analyse
- ``h5py`` pour le chargement/export HDF5
- ``ctypes`` pour l'appel aux DLL Measurement Computing

Pile optionnelle ou secondaire
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- ``PyQt6``: le bootstrap CLI essaie de le charger en secours, mais ``ThemeManager`` impose en pratique ``PySide6``
- ``SciPy``: utilise dans ``optimized_goda_analyzer.py`` mais pas dans le flux actif de la GUI
- ``pyFFTW``: optimisation FFT optionnelle non branchee au flux principal
- ``reportlab``: present dans ``utils/calib_pdf.py`` pour des sorties PDF annexes
- ``matplotlib``: utilise avec ``calib_pdf.py`` pour des graphiques hors flux actif principal
- ``Sphinx``: documentation technique du depot

Residus techniques et historiques
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Le depot garde encore des traces d'anciennes directions de projet:

- ``env.example`` contient une configuration orientee Vite / backend bridge web
- certains modules avances existent mais ne sont pas relies au runtime principal
- la vue calibration est plus mature visuellement que scientifiquement

Deep research signifie ici: separer strictement ce qui est actif, ce qui est optionnel, ce qui est historique et ce qui doit etre supprime.

Modele de donnees et contrats d'echange
---------------------------------------

Formats actifs
~~~~~~~~~~~~~~

- acquisition -> export: ``csv``, ``json``, ``hdf5``
- analyse -> export resultats: ``csv``, ``json``, ``hdf5``, ``txt``
- rapport -> export presentation: ``html``, ``txt``, ``json``, ``pdf``

Contrat CSV actif
~~~~~~~~~~~~~~~~~

Le flux actif exporte un CSV avec:

- une colonne ``time``
- des colonnes ``channel_XX``

Probleme prouve:

- la frequence d'echantillonnage de session n'est pas ecrite dans le CSV actif
- ``PostProcessor`` ne lit ``sample_rate`` que si cette colonne existe
- si elle manque, le moteur reste a ``32.0 Hz`` par defaut

Contrat JSON actif
~~~~~~~~~~~~~~~~~~

Le JSON exporte embarque davantage de metadonnees:

- ``sample_rate``
- ``sampling_rate``
- identifiant de session
- nom de projet
- labels et unites
- statistiques d'acquisition

Le JSON est aujourd'hui le format le plus proche d'un contrat exploitable et reversible dans la chaine active.

Contrat HDF5
~~~~~~~~~~~~

Le depot contient au moins deux logiques HDF5:

1. le contrat utilise par ``ExportManager`` et le flux acquisition actif
2. le contrat historique/annexe de ``utils/hdf_writer.py``

Probleme prouve:

- ces contrats ne sont pas unifies
- ``PostProcessor`` ne relit pas correctement tous les fichiers que le depot sait ecrire
- ``utils/hdf_writer.py`` est lui-meme partiellement casse

Chaine physique du logiciel
---------------------------

Intention physique
~~~~~~~~~~~~~~~~~~

Le logiciel veut transformer des tensions de capteurs en grandeurs experimentales:

- elevation de surface libre
- pression
- acceleration
- temperature

Le modele implicite est affine:

1. correction d'offset
2. application d'une echelle
3. division par une sensibilite capteur

Ce modele est visible dans ``AcquisitionController._convert_to_physical_units()``.

Limites physiques prouvees
~~~~~~~~~~~~~~~~~~~~~~~~~~

1. le mode simulation genere deja des grandeurs physiques, puis les repasse dans la conversion capteur
2. la calibration n'est pas reinjectee dans les coefficients utilises pendant la conversion
3. la base de temps affichee n'est pas une base de temps de mesure reconstruite depuis le buffer materiel
4. la plausibilite physique de la frequence d'echantillonnage n'est presque pas controlee
5. les metadata de type ``water_depth`` et ``wave_conditions`` ne pilotent pas encore la logique de mesure ou d'analyse

Consequence:

le logiciel possede une sémantique de laboratoire de modele reduit, mais pas encore une chaine metrologique suffisamment verrouillee.

Chaine mathematique du logiciel
-------------------------------

Statistiques descriptives
~~~~~~~~~~~~~~~~~~~~~~~~~

Le moteur calcule:

- moyenne
- ecart-type
- min
- max
- RMS
- skewness
- kurtosis

Ces calculs sont descriptifs, mais pas encore presentes comme estimateurs corriges pour petit echantillon.

Analyse spectrale
~~~~~~~~~~~~~~~~~

Le moteur actif:

- prend une taille de fenetre fixe
- peut appliquer une fenetre de Hann
- calcule une FFT
- derive un spectre en ``|FFT|^2``
- en deduit une frequence de pic

Problemes prouves:

- pas de normalisation PSD robuste dans le flux actif
- pas de correction energetique de fenetre
- les parametres ``detrend`` et ``overlap`` de la config ne sont pas vraiment utilises
- le module FFT optimise suit une autre definition mathematique que le moteur actif

Metriques de type Goda
~~~~~~~~~~~~~~~~~~~~~~

Le moteur actif derive:

- ``Hs``
- ``H_max``
- ``H_mean``
- ``H_rms``
- ``Tp``
- ``Tm``

Mais il le fait surtout a partir:

- de passages par zero du signal brut
- d'une frequence de pic issue d'une FFT simple

Problemes prouves:

- sensibilite forte aux offsets et derives
- hypothese de stationnarite implicite et non verifiee
- ecart entre les modules optimises du depot et la chaine active de la GUI

Problemes prouves a traiter
---------------------------

Bloc A - Critique
~~~~~~~~~~~~~~~~~

- perte de ``sample_rate`` dans le flux CSV actif
- biais physique du mode simulation
- calibration non injectee dans la conversion
- incoherence multi-plages MCC en acquisition scan
- non-unification et instabilite du contrat HDF5

Bloc B - Majeur
~~~~~~~~~~~~~~~

- base de temps de mesure non fiable
- chaine spectrale non normalisee de facon scientifique
- choix d'analyse GUI cosmétique
- non-usage des metadata physiques de projet
- export des resultats incomplet par rapport a ce qui est calcule

Bloc C - Structurel
~~~~~~~~~~~~~~~~~~~

- coexistence de modules optimises non relies au flux actif
- coexistence de restes web/hybrides dans le depot
- documentation a maintenir strictement alignee sur le runtime reel

Programme de deep research
--------------------------

Objectif global
~~~~~~~~~~~~~~~

Transformer CHNeoWave d'une base fonctionnelle de demonstration avancee en une chaine experimentale defensible du point de vue:

- physique
- mathematique
- logiciel
- reproductibilite

Lot 1 - Audit metrologique
~~~~~~~~~~~~~~~~~~~~~~~~~~

Questions a traiter:

- quels sont les capteurs reels cibles et leurs sensibilites exactes
- quelles unites physiques doivent etre considerees comme verite de reference
- quelle calibration est attendue en laboratoire: offset, pente, linearite, hysteresis, bruit, derive
- comment stocker une calibration de facon persistante et traçable
- comment reconstruire une base de temps fiable depuis le materiel

Livrables attendus:

- specification capteurs/unites/sensibilites
- contrat de calibration persistant
- mode simulation physiquement coherent
- politique d'horodatage experimentale

Lot 2 - Audit mathematique et signal
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Questions a traiter:

- quelle definition de PSD doit etre adoptee par le produit
- quelles fenetres, tailles de blocs et overlaps sont retenus
- comment traiter les offsets, derives et segments non stationnaires
- quelle definition officielle des indicateurs ``Hs``, ``Tp``, ``Tm`` doit etre retenue
- faut-il brancher les modules optimises existants ou les remplacer

Livrables attendus:

- specification mathematique officielle
- jeux de tests numeriques de reference
- alignement entre moteur actif et moteurs optimises
- export reversible des resultats spectraux et statistiques

Lot 3 - Contrats de donnees
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Questions a traiter:

- quel format canonique retenir entre CSV, JSON et HDF5
- quelles metadonnees sont obligatoires
- comment assurer la reversibilite acquisition -> analyse -> export
- comment versionner les schémas de donnees

Livrables attendus:

- contrat de donnees unique
- tables de compatibilite
- fichiers de test de reference
- validation automatique des exports

Lot 4 - Nettoyage d'architecture
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Questions a traiter:

- quels modules sont actifs
- quels modules sont optionnels
- quels modules historiques doivent etre supprimes
- quelles vues GUI sont fiables et lesquelles sont decoratives

Livrables attendus:

- carte d'architecture definitive
- suppression du code mort restant
- reduction du nombre de chemins alternatifs

Lot 5 - Validation scientifique et logicielle
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Questions a traiter:

- quels cas de test representent un essai reel de bassin
- quels signaux synthetiques permettent de verifier l'analyse
- quelles tolerances numeriques sont acceptables
- quels tests de non-regression doivent tourner en continu

Livrables attendus:

- suite de tests physiques et mathematiques
- datasets de reference
- smoke tests GUI minimaux
- criteres d'acceptation avant usage experimental

Roadmap de correction recommandee
---------------------------------

Phase 1 - Verrouiller les contrats
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- fixer le contrat CSV
- unifier le contrat HDF5
- figer les metadonnees obligatoires
- supprimer les chemins d'export cassés

Phase 2 - Corriger la chaine acquisition
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- separer clairement tension brute, grandeur simulee et grandeur physique convertie
- rendre la simulation dimensionalement correcte
- persister et reappliquer les vraies calibrations
- revoir l'acquisition MCC multi-plages et la base de temps

Phase 3 - Corriger la chaine d'analyse
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- normaliser la definition PSD
- traiter detrend, fenetrage et overlap proprement
- clarifier les definitions ``Hs``/``Tp``/``Tm``
- brancher ou supprimer les modules optimises selon decision claire

Phase 4 - Rendre la GUI honnête
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- faire correspondre les boutons a de vraies actions
- enlever les controles cosmetiques
- exposer clairement les hypotheses physiques et mathematiques
- afficher les limites et avertissements quand les conditions ne sont pas reunies

Phase 5 - Validation finale
~~~~~~~~~~~~~~~~~~~~~~~~~~~

- tests unitaires
- tests de contrats de donnees
- tests numeriques de reference
- verification GUI headless
- revue scientifique des formules et des conversions

Criteres de sortie
------------------

Le logiciel pourra etre considere comme scientifiquement defensible quand les conditions suivantes seront remplies:

- une calibration persistante et reappliquee existe
- le mode simulation suit la meme discipline dimensionnelle que le mode reel
- les frequences d'echantillonnage sont traçables dans toute la chaine
- les exports sont reversibles et versionnes
- les definitions mathematiques des indicateurs sont ecrites et testees
- la GUI n'expose plus de faux controles ni de faux statuts

Conclusion
----------

CHNeoWave a une vraie base fonctionnelle et un vrai domaine cible. Le depot n'est pas vide de substance. Il possede deja:

- une vraie logique de projet
- une vraie chaine acquisition -> analyse -> rapport
- une integration materielle MCC
- une base de post-traitement

Mais la transition entre prototype avance et outil de laboratoire n'est pas encore terminee. La deep research a lancer maintenant ne doit pas etre une exploration vague. Elle doit etre un programme de correction fonde sur les preuves deja extraites du code:

- physique de mesure
- contrats de donnees
- mathematiques du signal
- honnetete de la GUI

Priorite immediate
------------------

La priorite absolue est:

1. corriger les contrats de donnees et le ``sample_rate``
2. corriger la simulation et la calibration
3. reecrire la chaine spectrale sur une base mathematique unique

Tant que ces trois blocs ne sont pas traites, toute interpretation experimentale forte restera fragile.

Complement apres deep research du 26 avril 2026
-----------------------------------------------

Le rapport externe de deep research confirme que la cible produit principale doit rester l'acquisition de donnees pour essais maritimes en modele reduit.

La conclusion d'architecture retenue est la suivante:

- garder la GUI Qt comme interface operateur
- sortir progressivement la responsabilite de mesure vers un service d'acquisition
- utiliser HDF5 comme stockage canonique
- conserver JSON comme manifeste/metadonnees
- limiter CSV a un export derive
- traiter NMEA, Modbus, CAN et IEC comme extensions futures, pas comme capacites actuelles

Le rapport ouvre aussi une extension possible de generation de houle. Cette extension est valide comme direction future, mais elle doit rester separee de l'acquisition. Le generateur de houle doit commander un actionneur; l'acquisition doit rester la source de verite experimentale. La commande de batteur ne doit donc venir qu'apres verrouillage de la chaine acquisition, calibration, temps et analyse.

Le plan operationnel associe est formalise dans ``development_master_plan.rst``.
