Système d'interface
===================

Objectif
--------

L'interface CHNeoWave doit présenter une chaîne de mesure fiable, pas une
collection de composants décoratifs. La hiérarchie visuelle suit le travail du
laboratoire : projet, calibration, acquisition, analyse et rapport.

Source unique
-------------

La feuille ``gui/styles/maritime_modern.qss`` est l'unique source du thème de
production. ``ThemeManager`` conserve les anciens noms de thèmes uniquement
comme alias de compatibilité. Une vue ne doit pas définir sa propre palette avec
``setStyleSheet``.

Hiérarchie
----------

* La barre latérale assure seule la navigation entre les sections.
* L'en-tête indique le contexte, l'étape et l'objectif de la page.
* Une page possède une seule action principale visible.
* Les actions secondaires utilisent la propriété ``kind=secondary``.
* Les états utilisent ``state=success``, ``warning``, ``danger`` ou ``neutral``.
* Les mesures réelles sont distinguées des états système et des textes d'aide.
* Aucune valeur simulée ne doit apparaître comme un résultat expérimental.

Densité et surfaces
-------------------

Les espacements de référence sont 8, 12, 16 et 24 pixels. Les surfaces servent
à regrouper une décision ou un ensemble de données ; elles ne doivent pas être
imbriquées sans nécessité. Les bordures sont discrètes et les ombres sont
évitées afin de préserver la lisibilité sur les postes du laboratoire.

Composants communs
------------------

Les noms d'objet suivants sont réservés au système visuel :

``applicationHeader``
    Contexte stable de la page.

``surface`` et ``quietSurface``
    Conteneur principal et conteneur secondaire.

``sectionTitle`` et ``mutedText``
    Titre fonctionnel et information complémentaire.

``metricCard``, ``metricLabel`` et ``metricValue``
    Résumé d'une mesure ou d'un indicateur de qualité.

``state`` et ``kind``
    Propriétés dynamiques pour les badges et les boutons. Après modification
    dynamique, le widget doit être repoli avec ``style().unpolish`` puis
    ``style().polish``.

Règles scientifiques
--------------------

L'interface ne fusionne jamais ``H1/3`` temporel et ``Hm0`` spectral. Les unités,
la fréquence d'échantillonnage, la source et les alertes qualité restent visibles
à proximité des résultats. Un résultat issu d'un capteur non converti conserve
l'unité du capteur et ne doit pas être présenté comme une hauteur de vague.
