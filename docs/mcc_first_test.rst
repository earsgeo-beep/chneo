Premier test MCC USB-1608FS
===========================

Objectif
--------

Ce protocole valide uniquement la detection, les plages analogiques, le rythme
d'acquisition et l'ordre des canaux. Il ne constitue pas encore la validation
d'une campagne de deux heures.

Preparation
-----------

1. Installer le pilote Measurement Computing et l'Universal Library.
2. Verifier la detection USB directe avec le diagnostic CHNeoWave ci-dessous.
3. En cas d'echec uniquement, utiliser InstaCal comme diagnostic constructeur.
4. Relier les entrees inutilisees a ``AGND`` conformement au manuel MCC.
5. Ne pas connecter les capteurs de campagne pendant le premier diagnostic.
6. Installer CHNeoWave et ``mcculw`` avec le kit hors ligne decrit dans
   ``INSTALL.md``.

Diagnostic non destructif
-------------------------

.. code-block:: powershell

   python scripts\mcc_hardware_probe.py

Le resultat attendu contient au minimum:

.. code-block:: json

   {
     "expected_device": "USB-1608FS",
     "boards": [0],
     "devices": [
       {"board_num": 0, "board_name": "USB-1608FS"}
     ],
     "ok": true
   }

Validation progressive
----------------------

Effectuer les essais dans cet ordre:

1. un canal, plage ``+/-10 V``, 100 Hz, 60 secondes;
2. deux canaux avec deux plages differentes, 100 Hz, 60 secondes;
3. huit canaux, 100 Hz, 10 minutes;
4. recommencer aux frequences reellement utilisees au laboratoire.

Pour chaque essai, conserver:

- le journal CHNeoWave;
- la frequence demandee et la frequence effective;
- le nombre d'echantillons attendu et enregistre;
- le compteur de debordements;
- le fichier HDF5 cree automatiquement dans ``<projet>/data``;
- un export CSV seulement pour les essais courts qui doivent etre relus dans
  un tableur;
- le rapport du diagnostic USB direct CHNeoWave.

Enregistrement continu
----------------------

Le fichier HDF5 est ouvert avant le lancement du thread d'acquisition, puis
alimente bloc par bloc. Il contient:

- ``acquisition_data/time`` et les valeurs converties en unites physiques;
- ``raw_voltage`` avec les tensions mesurees avant conversion capteur;
- la frequence effective, la configuration des canaux et les coefficients de
  calibration;
- ``recording_status`` avec la valeur ``recording``, ``complete`` ou ``error``.

Une fermeture normale doit produire ``recording_status = complete``. Apres
une coupure de courant ou une erreur disque, conserver le fichier partiel pour
diagnostic mais ne pas le presenter comme une session valide. L'ecriture est
videe vers le systeme de fichiers au maximum toutes les secondes et lors de
l'arret normal.

Verifier chaque fichier sans charger tous les signaux en memoire:

.. code-block:: powershell

   python scripts\inspect_mcc_session.py "C:\chemin\session.h5"

Le code de sortie est zero uniquement si la session est complete, si toutes
les longueurs de canaux correspondent, et si les compteurs ``errors`` et
``buffer_overruns`` sont nuls.

Particularite du USB-1608FS classique
-------------------------------------

Le modele ``USB-1608FS`` classique impose une file de gains comprenant les
huit canaux CH0 a CH7 dans l'ordre, contrairement au ``USB-1608FS-Plus``. Le
backend acquiert donc toujours les huit entrees, applique la plage configuree
aux canaux actifs et ``+/-10 V`` aux autres, puis ne transmet a l'application
que les canaux selectionnes. Les entrees inutilisees doivent rester reliees a
``AGND`` pendant les essais.

Le debit maximal du modele classique est de 100 kS/s agreges. Comme les huit
canaux sont scannes, CHNeoWave limite la frequence a 12 500 echantillons par
seconde et par canal. Commencer les validations a 100 Hz, puis augmenter
progressivement jusqu'a la frequence reellement necessaire au laboratoire.

Criteres d'arret
----------------

Arreter le test et ne pas utiliser les donnees si l'un des cas suivants se
produit:

- ``buffer_overruns`` est superieur a zero;
- la frequence effective est absente;
- des blocs sont repetes ou desordonnes;
- le nombre de colonnes ne correspond pas aux canaux choisis;
- la valeur mesuree ne respecte pas la plage configuree;
- l'application ou l'interface se bloque.

Limite actuelle
---------------

Le stockage HDF5 continu est integre et valide par des doubles de banc dans la
suite automatisee. Ne pas encore lancer de campagne de deux heures: il reste a
valider sur le PC Windows
du laboratoire les paliers de 60 secondes, 10 minutes puis 60 minutes, avec
``recording_status = complete``, le compte exact d'echantillons et zero
``buffer_overruns``. La campagne longue sera autorisee apres ces trois paliers.
