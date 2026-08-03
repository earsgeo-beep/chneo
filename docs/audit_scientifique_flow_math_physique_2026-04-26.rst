Audit scientifique: flow, mathematiques et physique
====================================================

Date: 2026-04-26

Objectif
--------

Ce document audite CHNeoWave comme logiciel professionnel d'acquisition de
donnees maritimes en modele reduit. Le but n'est pas encore de refondre le
code, mais de separer:

* ce qui est correct et peut rester une base de travail;
* ce qui est techniquement fonctionnel mais scientifiquement fragile;
* ce qui est mathematiquement faux ou trompeur et doit etre corrige avant
  d'utiliser le logiciel pour des essais de laboratoire.

Le perimetre audite couvre le flux actif:

1. configuration des capteurs;
2. acquisition ou simulation;
3. conversion tension -> grandeur physique;
4. export CSV, JSON et HDF5;
5. chargement post-traitement;
6. statistiques, spectre, metriques de vagues;
7. rapport utilisateur.

Verdict court
-------------

La base logicielle peut devenir un outil d'acquisition maritime serieux, mais
le coeur scientifique n'est pas encore fiable pour produire des resultats de
laboratoire. Les exports ont ete renforces par la presence explicite de la
frequence d'echantillonnage et par la separation brut/physique, mais les
algorithmes d'analyse de vagues et de spectre contiennent encore des erreurs
fondamentales.

Les points critiques sont:

* les metriques dites "Goda" dans ``PostProcessor`` ne sont pas une methode
  Goda de separation incident/reflechi; ce sont des metriques zero-crossing
  simplifiees et actuellement fausses sur des cas simples;
* l'analyse spectrale calcule une energie de FFT brute, pas une densite
  spectrale physique normalisee;
* l'analyseur Goda optimise contient une erreur d'algebre complexe dans la
  pseudo-inverse SVD;
* la calibration exposee a l'utilisateur n'est pas appliquee comme une chaine
  metrologique validee;
* plusieurs reglages visibles dans l'interface donnent l'impression d'etre
  appliques, alors qu'ils ne pilotent pas le calcul actif.

Etat correctif du 2026-04-26
----------------------------

Les corrections P0 initiales ont ete appliquees apres cet audit:

* ``zero_crossing_metrics`` est maintenant le nom canonique des metriques de
  vagues par zero-upcrossing; ``goda_metrics`` reste seulement un alias de
  compatibilite avec warning scientifique.
* L'extracteur zero-crossing retire le niveau moyen, detecte les up-crossings,
  evite les artefacts de ``sign(0)`` et mesure des vagues completes.
* Le spectre actif produit maintenant une PSD one-sided normalisee, les moments
  ``m0``, ``m1``, ``m2`` et ``Hm0``.
* La pseudo-inverse complexe de l'analyseur Goda optimise utilise
  ``conj().T``.
* La simulation pression utilise une pression relative compatible avec la plage
  DAQ par defaut.
* La calibration ne retourne plus de faux coefficients aleatoires ni de faux
  statut ``ok``. Tant qu'une vraie procedure materielle n'est pas implementee,
  elle retourne un contrat ``not_performed`` avec formule, coefficients actifs,
  unites et warnings.

Tests de non-regression ajoutes:

.. code-block:: powershell

   $env:PYTHONPATH='src'; python -m unittest discover -s tests

Le travail restant pour la calibration est une vraie procedure metrologique
avec mesures de reference, incertitudes, operateur, date, certificat et
application controlee des coefficients.

Invariants scientifiques a imposer
----------------------------------

Ces invariants doivent devenir des tests automatiques.

* Une grandeur stockee doit toujours avoir une unite, une frequence
  d'echantillonnage, un domaine de temps et une provenance de calibration.
* Le temps d'acquisition doit etre explicite: temps synthetique base sur Fs,
  horloge materielle, ou horloge systeme. Ces domaines ne doivent pas etre
  melanges.
* Une tension brute ``V_raw`` ne doit etre convertie en grandeur physique que
  par une loi calibree et documentee. Les unites de l'offset et du gain doivent
  etre non ambigues.
* Tout calcul spectral doit produire soit une amplitude FFT sans interpretation
  energetique, soit une PSD normalisee avec correction de fenetre.
* Toute hauteur de vague doit preciser sa methode: zero-upcrossing,
  zero-downcrossing, spectrale ``Hm0`` ou separation incident/reflechi.
* Toute methode de houle en canal doit distinguer au minimum: houle incidente,
  houle reflechie, coefficient de reflexion, profondeur d'eau, positions des
  sondes et relation de dispersion.
* Une interface ne doit jamais presenter un parametre scientifique comme actif
  si ce parametre n'est pas connecte au pipeline de calcul.

Carte du flow reel
------------------

Flux actif dans l'application:

.. code-block:: text

   Projet Qt
      -> AcquisitionConfigView
      -> AcquisitionController
      -> raw_data [volts]
      -> _convert_to_physical_units()
      -> processed_data [unites physiques]
      -> export CSV/JSON/HDF5
      -> AnalysisView
      -> PostProcessor.load_data_file()
      -> PostProcessor.run_analysis()
      -> basic_stats + spectral_analysis + zero_crossing_metrics
      -> ReportView / exports d'analyse

Points solides:

* les fichiers exportes peuvent maintenant porter explicitement
  ``sample_rate_hz``;
* CSV, JSON et HDF5 peuvent separer donnees physiques et donnees brutes;
* le post-traitement refuse maintenant les donnees sans Fs ni axe temps
  inferable;
* le format HDF5 devient une bonne base pour une chaine metrologique.

Points faibles du flow:

* l'acquisition garde surtout un timestamp de chunk, pas un timestamp materiel
  par echantillon;
* la simulation produit un axe temps coherent en echantillons, mais son debit
  mural n'est pas aligne sur ``sampling_rate``;
* les parametres avances de l'interface ne sont pas une source unique de verite;
* les rapports ne portent pas encore les hypotheses, les unites, la calibration
  et les avertissements scientifiques.

Preuves locales executees
-------------------------

Les tests ci-dessous ont ete executes localement avec ``PYTHONPATH=src``.

1. Zero-crossing sur sinusoide propre

   Signal: ``eta(t) = sin(2*pi*1*t)``, Fs = 100 Hz, duree = 10 s.

   Resultat observe:

   .. code-block:: text

      sine_zero_mean n_heights=10 Hs=1.0 Tp=1.0 Tm=1.0

   Probleme: pour une sinusoide d'amplitude 1, la hauteur vague crete-creux
   attendue est proche de 2. Le code mesure une demi-vague, donc sous-estime la
   hauteur par facteur 2 dans ce cas simple.

2. Zero-crossing avec offset positif

   Signal: ``eta(t) = 1.2 + sin(2*pi*1*t)``.

   Resultat observe:

   .. code-block:: text

      sine_positive_offset n_heights=0 Hs=None Tp=1.0 Tm=0.0

   Probleme: un signal avec niveau moyen non nul ne traverse plus zero. Le code
   ne retire pas le niveau moyen d'eau et declare donc aucune vague.

3. Zero-crossing avec valeurs quantifiees contenant des zeros

   Resultat observe:

   .. code-block:: text

      sine_with_zeros_quantized n_heights=19 Hs=1.0 Tp=1.0 Tm=0.5

   Probleme: ``np.sign(0)`` cree des transitions artificielles. La periode
   moyenne tombe a 0.5 s au lieu de 1.0 s.

4. Energie spectrale

   Signal: sinusoide 2 Hz, amplitude constante, Fs = 100 Hz.

   Resultat observe:

   .. code-block:: text

      duration_s=4  total_energy=38304.0
      duration_s=8  total_energy=76704.0
      duration_s=16 total_energy=127647.0

   Probleme: la quantite ``total_energy`` depend fortement de la duree et du
   ``n_fft``. Ce n'est pas une energie physique ni une PSD exploitable pour
   calculer des moments spectraux.

5. Goda optimise avec mesures complexes exactes

   Cas synthetique: matrice de propagation exacte, amplitudes incidentes et
   reflechies connues.

   Resultat observe:

   .. code-block:: text

      true_incident_abs=1.0440 estimated_abs=0.3202
      true_reflected_abs=0.3202 estimated_abs=1.0440
      reflection_true=0.3067 reflection_est=3.2610
      wrong_error_norm=1.2748
      right_error_norm=4.0e-16

   Probleme: la pseudo-inverse SVD utilise une transpose simple au lieu de la
   transpose conjuguee. Le calcul inverse incident/reflechi sur ce cas.

6. Simulation pression

   Configuration par defaut: pression en ``hPa``, sensibilite ``0.01 V/hPa``,
   plage ``BIP5VOLTS``.

   Resultat observe:

   .. code-block:: text

      pressure_raw_min=10.1419
      pressure_raw_max=10.1819
      daq_range_name=BIP5VOLTS
      pressure_exceeds_pm5=True

   Probleme: le simulateur genere une pression absolue proche de 1013 hPa,
   soit environ 10.13 V. Cela depasse une entree +/-5 V. Pour un laboratoire de
   canal a houle, il faut probablement une pression relative/gauge ou une
   calibration avec offset capteur explicite.

Findings prioritaires
---------------------

P0-1 - La hauteur de vague zero-crossing est mathematiquement fausse
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Evidence code:

* ``src/hrneowave/core/post_processor.py:396`` calcule les metriques dites
  Goda.
* ``src/hrneowave/core/post_processor.py:425`` extrait les hauteurs par
  passages a zero.
* ``src/hrneowave/core/post_processor.py:448`` calcule la periode moyenne par
  difference entre tous les changements de signe.

Probleme:

Le code prend les passages a zero de ``values`` directement, sans retirer le
niveau moyen, sans choisir up-crossing ou down-crossing, sans interpolation et
sans traiter les zeros exacts. Ensuite il groupe les croisements deux par deux,
ce qui segmente souvent des demi-vagues.

Impact:

``Hs``, ``H_mean``, ``H_max`` et ``Tm`` peuvent etre faux meme sur une sinusoide
parfaite. Ce resultat ne doit pas etre utilise pour un rapport de laboratoire.

Correction attendue:

* retirer ou estimer le niveau moyen d'eau;
* detecter uniquement les up-crossings ou uniquement les down-crossings;
* interpoler le temps exact de croisement;
* definir chaque vague entre deux crossings successifs du meme type;
* calculer ``H = max(eta_segment) - min(eta_segment)`` sur une vague complete;
* ajouter des seuils de periode et d'amplitude pour rejeter le bruit.

P0-2 - L'analyse spectrale n'est pas une PSD physique
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Evidence code:

* ``src/hrneowave/core/post_processor.py:378`` calcule le spectre.
* ``src/hrneowave/core/post_processor.py:383`` applique une fenetre de Hanning
  sans correction d'energie.
* ``src/hrneowave/core/post_processor.py:386`` calcule
  ``abs(FFT)**2`` et nomme la somme ``total_energy``.

Probleme:

Le code ne detrend pas le signal, ne normalise pas par ``Fs`` ni par l'energie
de fenetre, ne fait pas de correction one-sided coherente et tronque ou
zero-pad selon ``n_fft`` sans statut clair.

Impact:

Le pic frequentiel peut etre approximativement utile, mais l'energie, les
moments spectraux et toute hauteur ``Hm0`` derivee seraient invalides.

Correction attendue:

Implementer une PSD one-sided documentee:

.. code-block:: text

   eta0 = eta - mean(eta)
   xw = eta0 * window
   S_eta(f) = |FFT(xw)|^2 / (Fs * sum(window^2))
   doubler les bins one-sided hors DC et hors Nyquist
   m0 = integral S_eta(f) df
   Hm0 = 4 * sqrt(m0)
   Tp = 1 / fp

Les parametres de fenetre, recouvrement et bande frequentielle doivent etre
stockes dans les resultats.

P0-3 - Le "Goda" actif n'est pas une methode Goda
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Evidence code:

* ``src/hrneowave/core/post_processor.py:396`` expose ``_compute_goda_metrics``.
* ``src/hrneowave/core/optimized_goda_analyzer.py:201`` contient un vrai solveur
  de composantes incidentes/reflechies par SVD, mais ce solveur n'est pas le
  chemin actif de ``PostProcessor.run_analysis``.

Probleme:

Le nom ``goda_metrics`` laisse croire a une analyse de Goda pour canal a houle,
mais le code actif calcule seulement des statistiques de vagues par
zero-crossing sur chaque canal independamment. Aucune position de sonde, aucune
profondeur, aucune relation de dispersion et aucune separation
incident/reflechi ne sont utilisees.

Impact:

Un utilisateur peut interpreter ``Hs`` et ``Tp`` comme une analyse maritime
avancee alors que la methode n'a pas les hypotheses necessaires.

Correction attendue:

Renommer temporairement le resultat actif en ``zero_crossing_metrics`` et
reserver ``goda`` a une vraie analyse multi-sondes:

* positions des sondes;
* profondeur d'eau;
* spectres complexes par sonde;
* resolution de dispersion;
* separation ``Ai`` / ``Ar``;
* coefficient de reflexion ``Kr = |Ar| / |Ai|``;
* indicateur de conditionnement et validite frequentielle.

P0-4 - Erreur d'algebre complexe dans l'analyseur Goda optimise
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Evidence code:

* ``src/hrneowave/core/optimized_goda_analyzer.py:216`` utilise
  ``Vt.T @ diag(1/s) @ U.T``.

Probleme:

Pour une SVD complexe ``A = U S Vh``, la pseudo-inverse est:

.. code-block:: text

   A+ = Vh.conj().T @ diag(1/s) @ U.conj().T

La transpose simple est correcte seulement en reel. Les matrices de propagation
``exp(+/- i k x)`` sont complexes, donc la formule actuelle est fausse.

Impact:

Le test synthetique exact inverse l'amplitude incidente et reflechie et donne un
coefficient de reflexion 3.261 au lieu de 0.307.

Correction attendue:

Remplacer la pseudo-inverse par la version conjuguee et ajouter un test
automatique avec solution analytique.

P0-5 - Calibration non metrologique
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Evidence code:

* ``src/hrneowave/acquisition/acquisition_controller.py:390`` convertit la
  tension brute en unite physique avec offset, gain et sensibilite.
* ``src/hrneowave/acquisition/acquisition_controller.py:810`` expose
  ``calibrate_system``.
* ``src/hrneowave/acquisition/acquisition_controller.py:833`` genere des
  corrections aleatoires.

Probleme:

La loi actuelle ressemble a:

.. code-block:: text

   physical = ((raw + calibration_offset) * calibration_scale) / sensitivity

Mais les unites de ``calibration_offset`` et ``calibration_scale`` ne sont pas
formalisees, et ``calibrate_system`` ne modifie pas la configuration active. Les
corrections aleatoires ne constituent pas une calibration.

Impact:

La chaine tension -> unite physique n'est pas defendable en metrologie.

Correction attendue:

Definir un modele unique, par exemple:

.. code-block:: text

   physical = gain_phys * (raw_voltage - zero_voltage) / sensitivity_v_per_unit + offset_phys

Chaque coefficient doit avoir une unite, une incertitude, une date, une methode
et une provenance.

P0-6 - Simulation pression hors plage DAQ
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Evidence code:

* ``src/hrneowave/acquisition/acquisition_controller.py:430`` fixe
  ``base_pressure = 1013.25`` hPa.
* ``src/hrneowave/acquisition/acquisition_controller.py:893`` fixe la
  sensibilite pression a ``0.01 V/hPa`` sur une plage ``BIP5VOLTS``.

Probleme:

``1013.25 hPa * 0.01 V/hPa = 10.1325 V``. La simulation depasse donc une plage
de +/-5 V.

Impact:

Les tests et demos donnent une situation impossible pour la configuration par
defaut. Cela peut masquer de vrais problemes de saturation et de calibration.

Correction attendue:

Utiliser une pression relative au niveau de reference, ou simuler la tension
capteur autour d'un offset explicite compatible avec la plage DAQ.

P1-1 - Les reglages de l'interface ne pilotent pas le calcul
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Evidence code:

* ``src/hrneowave/gui/views/project_settings_view.py:241`` expose un facteur de
  calibration.
* ``src/hrneowave/gui/views/project_settings_view.py:275`` expose le filtrage.
* ``src/hrneowave/gui/views/project_settings_view.py:303`` expose la taille de
  fenetre FFT.
* ``src/hrneowave/gui/views/analysis_view.py:256`` recoit ``analysis_type`` et
  ``params``.
* ``src/hrneowave/gui/views/analysis_view.py:264`` appelle
  ``PostProcessor.run_analysis()`` sans transmettre ces choix au moteur.

Probleme:

L'utilisateur peut croire que les filtres, fenetres, recouvrements et offsets
sont appliques. Dans le flux actif, ces parametres ne pilotent pas encore les
algorithmes.

Impact:

Risque fort de rapport faux par illusion d'interface.

Correction attendue:

Creer un ``ProcessingConfig`` unique, valide, injecte dans l'acquisition, le
post-traitement, les exports et les rapports.

P1-2 - Convention de forme des donnees incoherente
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Evidence code:

* ``src/hrneowave/hardware/base.py:52`` documente ``(n_channels, n_samples)``.
* ``src/hrneowave/hardware/backends/demo.py:87`` genere
  ``(n_channels, n_samples)``.
* le flux ``AcquisitionController`` manipule et exporte des matrices
  ``[samples, channels]``.

Probleme:

Deux conventions coexistent. Une integration materielle directe peut transposer
les canaux et echantillons sans erreur immediate.

Impact:

Risque de melange de canaux, de mauvais Fs apparent ou de mauvais calculs par
canal.

Correction attendue:

Choisir une convention interne canonique, idealement ``[samples, channels]`` ou
``[channels, samples]``, puis ajouter des validateurs de shape a chaque frontiere
DAQ/export/post-traitement.

P1-3 - Temps et simulation temps reel
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Evidence code:

* ``src/hrneowave/acquisition/acquisition_controller.py:401`` genere toujours
  100 echantillons par chunk.
* ``src/hrneowave/acquisition/acquisition_controller.py:564`` genere des
  timestamps recents en ordre decroissant par rapport a des donnees remises en
  ordre chronologique.

Probleme:

Le simulateur peut produire des echantillons avec un axe temps coherent, mais
pas forcement au rythme mural attendu. ``get_recent_data`` associe des donnees
chronologiques a des timestamps decroissants.

Impact:

Les courbes live, statistiques de debit et diagnostics temporels peuvent etre
faux.

Correction attendue:

Utiliser un index echantillon global et produire des timestamps monotones. Pour
la simulation temps reel, dormir ``num_samples / sampling_rate`` sauf mode
accelerated explicitement marque.

P1-4 - Exports d'analyse incomplets
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Evidence code:

* ``src/hrneowave/core/post_processor.py:338`` lance l'analyse complete.
* les exports CSV/HDF5 d'analyse ne portent pas tout le contenu spectral avec
  metadonnees de methode.

Probleme:

JSON contient plus d'information que CSV/HDF5. Les parametres scientifiques ne
sont pas encore complets.

Impact:

Perte de tracabilite et impossibilite de reproduire un rapport.

Correction attendue:

Standardiser le schema d'analyse:

* signal source;
* unite;
* Fs;
* methode;
* parametres;
* resultats;
* warnings;
* version d'algorithme.

P1-5 - Dependances scientifiques non formalisees
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Evidence code:

* ``src/hrneowave/core/optimized_goda_analyzer.py`` importe SciPy.
* ``requirements.txt`` ne liste pas SciPy.
* ``pyfftw`` est absent localement, donc le FFT optimise retombe sur NumPy.

Probleme:

Un module scientifique peut echouer a l'import dans une installation propre si
SciPy n'est pas declare.

Impact:

Les fonctions avancees peuvent etre non reproductibles selon la machine.

Correction attendue:

Declarer les extras:

.. code-block:: text

   requirements.txt          -> runtime actif minimal
   requirements-science.txt  -> scipy, pyfftw optionnel, tests numeriques
   requirements-dev.txt      -> pytest, sphinx, outils qualite

Roadmap de correction
---------------------

Phase P0 - Verrou scientifique minimal
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Renommer ``goda_metrics`` actif en ``zero_crossing_metrics`` pour stopper la
   confusion.
2. Corriger la pseudo-inverse complexe de ``OptimizedGodaAnalyzer``.
3. Refaire l'extracteur zero-crossing avec niveau moyen, up-crossing,
   interpolation et tests analytiques.
4. Remplacer ``total_energy`` par une PSD normalisee et des moments spectraux
   explicites.
5. Formaliser la loi de calibration tension -> unite physique.
6. Corriger la simulation pression pour rester dans la plage DAQ.

Phase P1 - Chaine metrologique
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Introduire ``ProcessingConfig`` et ``SensorCalibration`` comme contrats
   uniques.
2. Injecter ces contrats dans acquisition, post-traitement, exports et rapports.
3. Ajouter les warnings scientifiques dans les resultats: Fs absent, aliasing,
   saturation, capteur non calibre, mauvaise geometrie, signal non stationnaire.
4. Standardiser les shapes de matrices.
5. Ajouter des tests de non-regression numeriques.

Phase P2 - Vraie analyse maritime modele reduit
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Implementer Goda multi-sondes comme analyse separee, pas comme metrique
   zero-crossing.
2. Ajouter la relation de similitude de Froude pour modele reduit:

   .. code-block:: text

      lambda_L = L_prototype / L_modele
      lambda_T = sqrt(lambda_L)
      f_modele = f_prototype * sqrt(lambda_L)
      H_modele = H_prototype / lambda_L

3. Stocker la geometrie du bassin: profondeur, echelle, positions sondes,
   origine, orientation.
4. Preparer le futur generateur de vagues seulement apres validation du pipeline
   d'acquisition: consigne, mesure, boucle de correction, limites mecaniques.

Definition de "pret pour vraie acquisition"
--------------------------------------------

Le logiciel pourra etre considere pret pour les essais serieux quand ces tests
passeront:

* sinusoide amplitude 1 -> hauteur zero-crossing proche de 2;
* sinusoide avec offset -> meme hauteur apres retrait du niveau moyen;
* PSD d'une sinusoide -> pic a la bonne frequence et variance coherente avec
  ``m0``;
* Goda synthetique -> ``Ai`` et ``Ar`` retrouves avec erreur relative faible;
* pression par defaut -> tension brute dans la plage DAQ;
* tout export -> contient Fs, unite, calibration, methode et warnings;
* tout rapport -> indique explicitement si les resultats sont valides,
  experimentaux ou non calibres.

Decision de travail
-------------------

Avant de developper de nouvelles fonctions ou un generateur de vagues, il faut
corriger P0. Sinon on risque d'ajouter des fonctionnalites sur une base de
mesure qui donne des resultats scientifiquement faux.

Le prochain chantier recommande est donc:

1. corriger les erreurs mathematiques prouvees;
2. ajouter les tests analytiques;
3. connecter la configuration scientifique au moteur;
4. seulement ensuite enrichir l'interface et les rapports.
