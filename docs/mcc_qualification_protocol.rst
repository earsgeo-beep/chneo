Qualification de la chaine d'acquisition MCC
=============================================

:Statut: protocole logiciel livre, execution sur USB-1608FS reelle requise
:Materiel vise: MCC USB-1608FS classique

But et limite
-------------

Ce protocole decide si une session de diagnostic est techniquement recevable.
Il ne constitue ni un etalonnage du constructeur, ni une certification
normative, ni la validation des capteurs. Les seuils electriques du profil
``grounded`` sont des seuils d'ingenierie preliminaires; le responsable du
laboratoire doit les confirmer avec les exigences metrologiques et le montage
reel.

Le moteur reste independant du constructeur. Il travaille uniquement sur le
fichier HDF5 maitre termine et ne lit jamais le tampon d'apercu de l'interface.
Il ne modifie pas ce fichier.

Poste de qualification dans l'application
------------------------------------------

Apres connexion de la carte, ouvrir l'onglet ``Qualification``. Le logiciel:

* selectionne le protocole correspondant au pilote et au modele detectes;
* impose l'ordre Q0, Q1, Q2, Q3 puis Q4;
* exige la checklist operateur avant chaque lancement;
* controle le nombre de voies, les plages et la frequence du palier;
* affiche uniquement l'historique de la carte connectee;
* ne debloque jamais un palier sur la base d'un rapport refuse ou illisible.

La carte est identifiee par l'identifiant USB renvoye par Universal Library,
et non par le seul numero logique ``board 0``. La checklist horodatee, le
protocole et le palier sont archives dans le HDF5 maitre avant le demarrage de
l'acquisition, puis recopies dans les rapports de qualification.

Le bouton ``Essai qualifie`` ouvre ce poste sur Q0. Il ne lance plus une
acquisition avant que l'operateur ait valide la checklist physique.

Profils automatiques
--------------------

``quick_functional``
~~~~~~~~~~~~~~~~~~~~

L'essai court controle:

* l'integrite et le statut ``complete`` du HDF5 maitre;
* l'identite du pilote et du modele;
* la duree et le nombre exact d'echantillons;
* l'ecart entre frequence demandee et frequence effective, limite a 1 %;
* la cadence observee par l'horloge monotone, limitee a 10 % d'ecart;
* la continuite de l'axe temps fourni bloc par bloc par le pilote;
* l'absence de debordement, erreur d'ecriture ou discontinuite;
* l'absence de valeur non finie et de saturation sur chaque voie.

``grounded_inputs``
~~~~~~~~~~~~~~~~~~~

Ce profil ajoute, pour chaque entree reliee a ``AGND``:

* ``abs(moyenne) <= 0,5 %`` de la valeur absolue de pleine echelle;
* ``bruit RMS <= 0,1 %`` de la pleine echelle;
* ``crete-a-crete <= 1 %`` de la pleine echelle;
* ecart de cadence monotone limite a 5 %.

Avec une plage ``+/-10 V``, ces limites preliminaires valent respectivement
``50 mV``, ``10 mV RMS`` et ``100 mV crete-a-crete``. Elles sont exprimees en
fraction de plage afin de rester applicables aux autres equipements et plages.

Execution hors ligne
---------------------

Depuis PowerShell, dans l'environnement CHNeoWave:

.. code-block:: powershell

   python scripts\qualify_hardware_session.py "C:\chemin\session_Q0.h5" --stage Q0

Pour l'essai avec les entrees reliees a ``AGND``:

.. code-block:: powershell

   python scripts\qualify_hardware_session.py "C:\chemin\session_Q1.h5" --stage Q1

L'option ``--stage`` applique sans modification possible la duree, le profil,
le nombre de voies et les plages du palier. Les options ``--profile`` et
``--minimum-duration`` restent disponibles pour un diagnostic hors protocole,
mais leur rapport ne valide aucun palier Q0-Q4.

Un palier formel doit avoir ete lance depuis l'onglet ``Qualification``: la
commande hors ligne reverifie l'attestation et la checklist deja presentes
dans le fichier maitre. ``--ignore-wall-clock`` est reserve aux diagnostics
hors protocole et ne peut pas affaiblir un palier Q0-Q4.

Le code de sortie est ``0`` pour ``accepted``, ``2`` pour ``refused`` et ``1``
si aucun rapport fiable ne peut etre produit. Un refus est un resultat de
qualification valide: il faut lire la liste ``failed_checks`` et corriger la
cause avant de recommencer.

Les rapports JSON et HDF5 autonomes sont ecrits dans
``qualification_reports``. Ils contiennent le SHA-256 du fichier maitre,
l'identite materielle, les criteres exacts, les mesures par voie et le verdict.

Sequence de qualification sur le banc
--------------------------------------

Executer les paliers dans cet ordre et conserver chaque fichier maitre et ses
deux rapports:

.. list-table:: Paliers obligatoires
   :header-rows: 1
   :widths: 12 18 18 22 30

   * - Palier
     - Voies
     - Duree
     - Profil
     - Porte de sortie
   * - Q0
     - 1
     - 3 s
     - quick
     - essai court accepte
   * - Q1
     - 1
     - 60 s
     - grounded
     - bruit, offset et cadence acceptes
   * - Q2
     - 2, plages mixtes
     - 60 s
     - grounded
     - deux voies acceptees
   * - Q3
     - 8
     - 10 min
     - grounded, incluant tous les controles quick
     - zero perte et zero saturation
   * - Q4
     - 8
     - 60 min
     - quick
     - compte exact, zero erreur

Recommencer Q3 et Q4 aux frequences et plages reellement utilisees pendant les
campagnes. La campagne de longue duree reste interdite tant que Q4 n'est pas
accepte sur le PC Windows, le cable USB, le disque et la carte qui seront
utilises au laboratoire.

Incidents a tester separement
-----------------------------

Les essais de defaillance ne doivent jamais etre marques ``accepted``:

* deconnexion USB pendant l'acquisition;
* arret manuel avant le nombre d'echantillons attendu;
* support d'enregistrement plein ou indisponible;
* entree volontairement proche de la pleine echelle;
* redemarrage de l'application apres un fichier laisse partiel.

Conserver les fichiers ``error`` pour l'audit, mais ne pas les exporter ou les
analyser comme des donnees scientifiques valides.
