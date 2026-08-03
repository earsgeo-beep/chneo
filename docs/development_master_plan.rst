Plan Directeur de Developpement
===============================

Origine
-------

Ce plan reprend les conclusions du rapport de deep research fourni dans ``C:\Users\youcef cheriet\Downloads\deep-research-report.md`` et les aligne avec le code actif du depot CHNeoWave.

Le besoin produit est maintenant fixe:

- logiciel principal: acquisition de donnees pour laboratoire maritime en modele reduit
- priorite: chaine metrologique fiable, tracable et rejouable
- extension future possible: commande/generation de houle

Positionnement Produit
----------------------

CHNeoWave doit d'abord devenir un logiciel d'acquisition scientifique local pour essais en bassin ou canal de modele reduit.

Le logiciel doit permettre:

- creation et suivi d'un projet d'essai
- configuration des capteurs
- acquisition multi-canaux
- conversion tension -> unite physique via calibration
- stockage brut et converti avec metadonnees
- analyse post-acquisition
- rapport technique exploitable

Le logiciel ne doit pas encore chercher a etre:

- une plateforme navire complete
- une pile NMEA/Modbus/CAN generaliste
- un produit certifie maritime
- un controleur de batteur de houle

Ces directions peuvent etre preparees, mais elles ne doivent pas diluer la premiere cible: acquisition fiable.

Decision d'Architecture
-----------------------

La GUI Qt doit rester l'interface operateur, mais elle ne doit pas etre proprietaire de la mesure.

Architecture cible:

1. ``UI Qt``: navigation, supervision, configuration, visualisation
2. ``Acquisition Service``: acquisition, buffers, horodatage, etat runtime
3. ``Metrology Layer``: capteurs, unites, calibrations, conversions
4. ``Storage Layer``: HDF5 canonique, manifeste JSON, exports derives
5. ``Analysis Layer``: statistiques, spectres, indicateurs de houle
6. ``Report Layer``: HTML, TXT, JSON, PDF

Le developpement doit reduire les couplages implicites par fichiers et introduire progressivement des contrats internes explicites.

Portee V1
---------

La V1 doit etre limitee volontairement.

Objectif V1:

- acquisition locale fiable
- support MCC ou simulation coherente
- stockage canonique
- calibration persistante
- analyse reproductible
- rapport honnete

Hors scope V1:

- NMEA 0183
- NMEA 2000
- Modbus
- IEC 61162-450/460
- controle de batteur de houle
- synchronisation PTP multi-systemes
- certification CE, NMEA ou classification maritime

Ces sujets restent dans la feuille de route, mais ils ne doivent pas bloquer le durcissement de la chaine d'acquisition.

Backlog Prioritaire
-------------------

P0 - Contrats de donnees
~~~~~~~~~~~~~~~~~~~~~~~~

Probleme a corriger:

- ``sample_rate`` peut disparaitre dans le flux CSV
- plusieurs contrats HDF5 coexistent
- l'analyse accepte des donnees ambigues

Travail a faire:

- definir un schema de session obligatoire
- rendre ``sample_rate_hz`` obligatoire
- rendre ``clock_domain`` obligatoire
- separer ``raw``, ``physical`` et ``analysis``
- unifier le writer et le reader HDF5
- rendre le CSV export derive, pas format de verite
- ajouter un validateur de schema avant toute analyse

Critere de sortie:

- une session exportee puis rechargee conserve la meme frequence, les memes canaux, les memes unites et la meme calibration

P0 - Metrologie Acquisition
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Probleme a corriger:

- le mode simulation produit des grandeurs physiques puis les reconvertit
- la calibration retourne des corrections sans les appliquer
- les unites et sensibilites ne sont pas suffisamment validees

Travail a faire:

- definir une structure ``SensorConfig``
- definir une structure ``CalibrationRecord``
- stocker calibration par capteur/canal avec revision
- appliquer la calibration dans la conversion runtime
- separer simulation tension brute et simulation grandeur physique
- refuser une acquisition si un canal actif n'a pas d'unite et de calibration coherentes

Critere de sortie:

- modifier une calibration modifie le resultat converti de facon previsible et testee

P0 - Base de Temps
~~~~~~~~~~~~~~~~~~

Probleme a corriger:

- la base de temps actuelle est reconstruite de facon trop artificielle
- l'horodatage d'affichage peut etre confondu avec l'horodatage de mesure

Travail a faire:

- introduire un temps monotone interne
- enregistrer ``t0_monotonic_ns``
- enregistrer ``t0_utc`` si disponible
- stocker la qualite de synchronisation
- detecter trous, inversions et gigue excessive

Critere de sortie:

- chaque session a une base de temps reproductible et auditable

P0 - Analyse Scientifique
~~~~~~~~~~~~~~~~~~~~~~~~~

Probleme a corriger:

- PSD non normalisee dans le flux actif
- ``detrend`` et ``overlap`` existent mais ne pilotent pas encore vraiment le calcul
- definitions ``Hs``, ``Tp`` et ``Tm`` insuffisamment verrouillees

Travail a faire:

- definir une PSD officielle
- appliquer detrend, fenetrage et overlap de facon explicite
- documenter la correction d'energie de fenetre
- separer analyse temporelle et analyse spectrale
- ajouter datasets synthetiques de reference
- exporter aussi les resultats spectraux

Critere de sortie:

- un signal synthetique connu donne les memes resultats a chaque execution dans une tolerance documentee

P1 - UI Honnete
~~~~~~~~~~~~~~~

Probleme a corriger:

- certains boutons ou indicateurs sont cosmetiques
- le choix du type d'analyse ne change pas encore le pipeline
- la calibration semble plus reelle qu'elle ne l'est

Travail a faire:

- griser les actions non implementees
- afficher l'etat reel des calibrations
- relier le type d'analyse au moteur
- afficher les warnings de metadonnees manquantes
- afficher la qualite de session: OK, degradee, invalide

Critere de sortie:

- aucun controle visible ne doit promettre une action inexistante

P1 - Tests et Validation
~~~~~~~~~~~~~~~~~~~~~~~~

Travail a faire:

- tests round-trip CSV/JSON/HDF5
- tests de schema obligatoire
- tests de calibration
- tests de simulation
- tests FFT/PSD
- tests Hs/Tp/Tm
- tests d'erreurs: disque plein, canal sature, donnees manquantes

Critere de sortie:

- toute correction scientifique importante possede un test de non-regression

Future Extension - Generation de Houle
--------------------------------------

La generation de houle est une extension possible, mais elle doit etre separee de l'acquisition.

Principe:

- l'acquisition mesure la verite experimentale
- le generateur de houle commande un actionneur
- l'analyse compare commande, consigne et mesure

Architecture future:

1. ``WaveCommandService``: profils de consigne
2. ``WaveGeneratorAdapter``: driver du batteur ou generateur
3. ``SafetyInterlock``: limites, arret, verrouillage
4. ``FeedbackLoop``: optionnel, seulement apres validation acquisition
5. ``ExperimentRecipe``: scenario d'essai versionne

Types de consignes a prevoir:

- houle reguliere
- houle irreguliere
- rampe de frequence
- spectre cible
- sequence de calibration du batteur

Ce module ne doit pas etre construit avant que la chaine acquisition soit fiable, parce qu'une boucle de controle basee sur une mesure incertaine amplifie les erreurs au lieu de les corriger.

Phasage Recommande
------------------

Phase 1 - Fondations scientifiques
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- corriger ``sample_rate``
- unifier HDF5
- definir le schema de session
- ajouter validation de schema

Phase 2 - Acquisition metrologique
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- refondre simulation
- introduire calibration persistante
- ajouter base de temps monotone
- ajouter quality flags par canal

Phase 3 - Analyse fiable
~~~~~~~~~~~~~~~~~~~~~~~~

- refondre PSD
- clarifier Hs/Tp/Tm
- brancher les types d'analyse
- exporter tous les resultats utiles

Phase 4 - Service d'acquisition
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- sortir progressivement l'acquisition du couplage GUI
- creer interfaces propres pour drivers
- preparer replay deterministe

Phase 5 - Extension protocoles
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- ajouter NMEA/Modbus/CAN seulement si le besoin materiel est confirme
- les traiter comme sources auxiliaires, pas comme transport de waveform brut

Phase 6 - Generation de houle
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- ajouter commande de batteur
- ajouter recettes d'essai
- ajouter securites
- ajouter feedback uniquement apres validation acquisition

Definition de Reussite
----------------------

CHNeoWave sera pret pour un usage serieux en laboratoire quand:

- une acquisition ne peut pas demarrer avec des metadonnees critiques manquantes
- chaque canal a une unite, une plage, une sensibilite et une calibration tracables
- les donnees brutes et converties sont separees
- la frequence d'echantillonnage est conservee dans tous les formats
- HDF5 est le format canonique de session
- CSV est seulement un export derive
- l'analyse est reproductible sur datasets de reference
- la GUI montre l'etat reel du systeme
- les erreurs de capteur, saturation, disque et temps sont detectees

Decision Immediate
------------------

Le prochain travail de developpement doit commencer par le bloc P0:

1. schema de session
2. correction du ``sample_rate``
3. unification HDF5
4. separation brut / physique / analyse

Tout ajout fonctionnel avant ces corrections augmenterait la dette scientifique du logiciel.
