Traitement et analyse de la houle
=================================

Objectif scientifique
---------------------

La chaine active analyse toute la serie temporelle, canal par canal. Une longue
session HDF5 n'est pas chargee entierement en memoire: chaque canal est lu,
traite puis libere. Le premier canal du fichier sert de reference pour les
analyses croisees avec les autres capteurs.

Avant toute interpretation en hauteur de houle, le canal doit representer une
elevation de surface calibree. Sur un canal de pression ou d'acceleration,
``Hm0`` et ``H1/3`` restent des amplitudes exprimees dans l'unite du capteur;
elles ne deviennent pas des metres de houle sans une loi de conversion physique
validee.

Preparation du signal
---------------------

Le moteur refuse:

- les valeurs ``NaN`` ou infinies;
- les series de moins de 32 echantillons;
- une frequence d'echantillonnage absente, variable ou non positive;
- une session HDF5 dont ``recording_status`` n'est pas ``complete``;
- une session contenant des erreurs, des debordements ou des longueurs de
  canaux incoherentes.

La moyenne et, par defaut, la derive lineaire sont retirees avant l'analyse de
houle. Les donnees originales restent utilisees pour les statistiques
descriptives.

Analyse spectrale
-----------------

La densite spectrale de variance est estimee par la methode de Welch avec une
fenetre de Hann et 50 % de recouvrement par defaut. L'interface permet de regler
la longueur de segment, le recouvrement et la bande frequentielle. Le zero
padding n'est pas presente comme une amelioration de la resolution physique.

Pour une densite ``S(f)``, les moments sont calcules par integration numerique:

.. math::

   m_n = \int f^n S(f)\,df

Les parametres exportes sont:

.. math::

   H_{m0}=4\sqrt{m_0}, \qquad
   T_{m01}=\frac{m_0}{m_1}, \qquad
   T_{m02}=\sqrt{\frac{m_0}{m_2}}

``Tp`` est l'inverse de la frequence du maximum spectral, avec interpolation
parabolique locale. ``Te`` est calcule par ``m-1 / m0``. Les resultats incluent
la resolution frequentielle, le nombre de segments Welch et les unites de la
densite spectrale.

Analyse temporelle
------------------

Les vagues individuelles sont delimitees par deux passages ascendants
successifs du niveau moyen, avec interpolation lineaire de l'instant de
passage. La hauteur de chaque vague est la difference entre le maximum et le
minimum de ce segment.

Le moteur fournit notamment:

- ``H1_3``: moyenne du tiers des vagues les plus hautes;
- ``H1_10``: moyenne du dixieme des vagues les plus hautes;
- ``H_max``, ``H_mean`` et ``H_rms``;
- ``T_mean`` et la periode moyenne associee au tiers superieur;
- le nombre de vagues effectivement detectees.

Analyse multi-capteurs
----------------------

Pour chaque canal, la coherence et la phase sont calculees par rapport au
premier canal. Le resultat fournit la coherence et la phase au pic spectral de
la reference, ainsi que les courbes completes. Cette etape sert a controler la
propagation d'une onde entre sondes, un retard ou un capteur incoherent.

Execution hors interface
------------------------

Une session peut etre analysee directement en ligne de commande:

.. code-block:: powershell

   python scripts\analyze_wave_session.py "C:\donnees\session.h5" `
     --output "C:\donnees\analyse.json" `
     --segment-length 2048 --overlap 0.5

Le programme retourne un code non nul si le chargement, l'analyse ou l'export
echoue. La sortie JSON complete conserve les courbes spectrales, les moments,
les parametres de vagues, les analyses croisees et les avertissements.

Indicateurs de qualite
----------------------

Chaque canal contient une liste d'avertissements et les indicateurs suivants:

- rapport entre variance spectrale et variance temporelle;
- nombre de segments Welch;
- variation de la variance entre blocs;
- derive lineaire par seconde;
- duree et nombre d'echantillons;
- validite de l'interpretation en hauteur de houle selon le type de capteur.

Un avertissement ne modifie jamais silencieusement les donnees. Il apparait
dans l'interface, les exports et le rapport.

Validation numerique automatisee
--------------------------------

Les tests de reference verifient:

- la frequence, la periode, ``Hm0`` et ``H1/3`` d'une sinusoide connue;
- l'egalite entre variance temporelle et integrale de la densite spectrale;
- la coherence et le dephasage de deux signaux synthetiques;
- le rejet des valeurs non finies et des sessions HDF5 incompletes;
- le traitement paresseux d'un fichier HDF5 multi-canaux.

References methodologiques
--------------------------

- ITTC, ``Symbols and Terminology List``, section Environmental Mechanics -
  Waves, version 2024;
- ITTC Specialist Committee on Waves;
- NOAA/NDBC, ``Nondirectional and Directional Wave Data Analysis Procedures``;
- SciPy, implementation documentee de ``signal.welch``, ``signal.csd`` et
  ``signal.coherence``.
