GUI
===

Fenetre principale
------------------

``hrneowave.gui.main_window``
   Orchestration principale de l'application, cablage des vues et propagation du contexte projet.

Gestionnaire de vues
--------------------

``hrneowave.gui.view_manager``
   Enregistrement des widgets, navigation et notifications de base.

Vues actives
------------

``hrneowave.gui.views.welcome_view``
   Ecran d'accueil et creation de projet.

``hrneowave.gui.views.dashboard_view``
   Tableau de bord synthetique.

``hrneowave.gui.views.calibration_view``
   Ecran de calibration.

``hrneowave.gui.views.acquisition_config_view``
   Configuration, acquisition et export des donnees.

``hrneowave.gui.views.analysis_view``
   Chargement de fichier et analyse.

``hrneowave.gui.views.report_view``
   Construction et export du rapport.

``hrneowave.gui.views.project_settings_view``
   Parametres projet.

Theme
-----

``hrneowave.gui.styles.theme_manager``
   Charge la feuille de style active. Ce module impose actuellement ``PySide6``.
