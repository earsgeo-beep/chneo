Contrat scientifique du traitement V2
======================================

Objet
-----

Ce document fixe les equations, conventions et limites du calcul actif. Les
resultats ne doivent etre utilises dans un rapport de laboratoire que si les
metadonnees de calibration, la frequence d'echantillonnage et les indicateurs
de qualite sont conserves avec les donnees.

Calibration tension--grandeur physique
--------------------------------------

La regression est realisee dans le sens tension mesuree en fonction de la
reference physique:

.. math::

   V = S X + b

La conversion appliquee pendant l'acquisition est donc:

.. math::

   X = \frac{V-b}{S}

``S`` est exprime en V/unite physique et peut etre positif ou negatif selon la
polarite electrique du capteur. Une sensibilite nulle est interdite.

Deux points definissent une fonction de transfert, mais ne permettent pas
d'evaluer la linearite. Dans ce cas, le logiciel conserve la conversion mais
affiche explicitement ``Non evaluable (2 points)`` pour R2. Trois points ou plus
sont necessaires pour une evaluation de linearite.

La valeur ``uncertainty`` actuellement exportee est l'ecart-type residuel de la
regression dans l'unite physique. Elle ne constitue pas, seule, un budget
d'incertitude metrologique complet. Un certificat final devra aussi inclure les
incertitudes des references, la repetabilite, la resolution DAQ, la derive et
les conditions environnementales.

Spectre de houle
----------------

Le spectre actif est une densite spectrale de variance unilaterale obtenue par
Welch. Pour une fenetre ``w`` et une frequence d'echantillonnage ``Fs``, la
normalisation utilise:

.. math::

   S(f) = \frac{|FFT(x w)|^2}{F_s \sum w^2}

avec doublement des raies positives hors DC et Nyquist. Les moments spectraux
sont:

.. math::

   m_n = \int f^n S(f)\,df

Les parametres principaux sont:

.. math::

   H_{m0}=4\sqrt{m_0},\qquad
   T_p=\frac{1}{f_p},\qquad
   T_{m01}=\frac{m_0}{m_1},\qquad
   T_{m02}=\sqrt{\frac{m_0}{m_2}}

Le moteur exporte aussi un intervalle de confiance PSD approximatif a 95 %. Il
utilise ``2K`` degres de liberte pour ``K`` segments Welch. Cette approximation
ne corrige pas la correlation introduite par le recouvrement et est donc
identifiee comme telle dans les resultats. Elle est affichee uniquement pour
l'agregation Welch par moyenne; le logiciel ne pretend pas appliquer ce modele
du khi-deux a l'agregation robuste par mediane.

La resolution de Rayleigh exportee vaut ``Fs / nperseg``. L'espacement de la
grille FFT vaut ``Fs / nfft``. Un ``nfft`` plus grand par zero-padding fournit
plus de points d'affichage mais ne cree pas de resolution physique nouvelle.

Conditionnement optionnel
-------------------------

Le detrendage est explicite: aucun, retrait de moyenne, ou retrait d'une derive
lineaire. Les filtres optionnels sont des Butterworth passe-bas, passe-haut,
passe-bande ou coupe-bande d'ordre 1 a 10. Ils sont calcules en sections du
second ordre puis appliques aller-retour avec ``sosfiltfilt``. Le filtrage est
donc sans dephasage dans ce traitement hors ligne. Le type, les coupures,
l'ordre et l'implementation sont exportes avec chaque resultat.

Le spectrogramme de la voie active utilise ``scipy.signal.ShortTimeFFT`` quand
la version installee le fournit, avec fenetres completement incluses dans
l'intervalle selectionne. Une voie de compatibilite SciPy 1.10/1.11 reste
disponible. La carte montre une PSD unilaterale en dB et conserve dans les
resultats la resolution de Rayleigh et l'espacement FFT distincts.

Analyse croisee
---------------

La phase est calculee avec la convention:

.. math::

   \phi = \arg\left(\overline{X_{ref}} X_{comp}\right)

Une phase positive signifie que le signal compare est en avance. Le retard
temporel exporte est positif lorsque le signal compare arrive plus tard:

.. math::

   \tau = -\frac{\phi}{2\pi f}

Geometrie de campagne et reproductibilite
------------------------------------------

La profondeur d'eau est saisie en metres lors de la creation du projet ou dans
les parametres d'acquisition. La position longitudinale de chaque sonde de
houle est saisie dans la colonne ``Position x (m)`` de la table des canaux. Le
repere peut avoir une origine arbitraire et accepter des abscisses negatives,
mais toutes les positions doivent etre finies, distinctes et exprimees dans le
meme repere.

La commande de sauvegarde de configuration produit un JSON versionne contenant
la frequence d'echantillonnage, la duree, la profondeur, les huit canaux, leurs
positions et leurs certificats de calibration. Le chargement valide le document
complet avant de modifier l'interface; une configuration partiellement invalide
est donc refusee sans changement partiel de la campagne active.

Pendant l'acquisition, ``water_depth_m`` est fige dans les metadonnees de
session et ``probe_position_m`` dans les metadonnees de chaque canal. Ces champs
sont conserves en JSON et HDF5 ainsi que dans le sidecar metrologique d'un export
CSV. Les champs canoniques de temps (frequence, pas, nombre d'echantillons et
duree) ne peuvent pas etre remplaces par une metadonnee libre de projet.

Separation incidente--reflechie multi-sondes
---------------------------------------------

La separation devient active uniquement si au moins trois canaux de type
``wave_height`` portent une position ``probe_position_m`` et si la session
contient ``water_depth_m``.

Pour chaque frequence et chaque segment Welch, le modele resolu est:

.. math::

   \eta_j(f)=A_i(f)e^{+ikx_j}+A_r(f)e^{-ikx_j}

Le nombre d'onde est la racine positive de la relation de dispersion lineaire:

.. math::

   \omega^2=gk\tanh(kh)

La solution complexe est obtenue par moindres carres SVD. Les frequences dont le
nombre de condition depasse 100 sont refusees. Les PSD incidente et reflechie
sont moyennees sur les segments avec la meme normalisation que Welch. Le
coefficient de reflexion energetique est:

.. math::

   K_r=\sqrt{\frac{m_{0,r}}{m_{0,i}}}

Hypotheses et limites
---------------------

La separation suppose une houle lineaire bidimensionnelle, des sondes
synchronisees et calibrees, une profondeur constante, des positions connues
dans le meme repere et une serie suffisamment stationnaire. Elle ne corrige pas
les effets non lineaires, la houle oblique, les modes evanescents, les erreurs de
position ou les decalages d'horloge entre cartes.

Controles automatiques
----------------------

Le pipeline refuse les NaN/Inf, les longueurs de canaux differentes, les axes
temps non monotones ou incompatibles avec ``sample_rate_hz`` et les sessions
HDF5 incompletes. Il signale notamment:

* moins de quatre segments Welch;
* moins de dix periodes de pic enregistrees;
* moins de dix echantillons par periode de pic;
* divergence entre variance temporelle et spectrale;
* variance non stationnaire entre blocs;
* portion plate prolongee pouvant indiquer capteur, cable ou saturation;
* calibration absente ou type de capteur incompatible avec une interpretation
  en hauteur de houle.

Validation numerique
--------------------

Les tests synthetiques couvrent une sinusoide analytique, la conservation de
variance de la PSD, la phase et le retard entre canaux, les polarites de
calibration, la relation de dispersion et une combinaison incidente/reflechie
connue. Pour le cas ``Ai=0.30 m`` et ``Ar=0.09 m``, le moteur retrouve
``Kr=0.3008`` avec les reglages de test, pour une valeur analytique de ``0.3000``.
