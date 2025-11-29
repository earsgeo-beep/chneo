<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# Résumé: comment l’acquisition et la calibration doivent fonctionner dans CHNeoWave

## 1) Acquisition: fiabilité temps réel, simplicité opérateur

- Objectif: capturer des signaux de houle depuis plusieurs capteurs, visualiser en temps réel, enregistrer proprement, sans surcharge cognitive.
- Workflow opérateur:
    - Configuration rapide: choisir la source (capteur/sonde), fréquence d’échantillonnage, durée/session, nom du projet/série.
    - Lancer/Pause/Stop: contrôles centraux clairs, retour d’état immédiat.
    - Visualisation:
        - 2 graphes individuels assignables par l’utilisateur à deux capteurs au choix (comparaison fine).
        - 1 graphe combiné superposant plusieurs capteurs pour cohérence inter-capteurs.
        - Interactions basiques: zoom, pan, curseur de lecture, légende activable.
    - Indicateurs essentiels:
        - Qualité signal (SNR simple, saturation détectée, présence de trous).
        - Compteur d’échantillons, durée écoulée/restante.
        - Marqueurs d’événements (start, pause, notes opérateur).
    - Enregistrement:
        - Sauvegarde structurée par projet/session.
        - Formats d’export standard (CSV/Parquet/NetCDF/Mat).
    - Performance:
        - Rendu fluide (objectif 60fps).
        - Pipelines FFT/spectres optimisés (ex: backend pyFFTW/FFTW avec “wisdom” et cache de plans pour signaux longs).
- Bonnes pratiques d’UX:
    - Layout 3 zones (contrôles, graphes, infos essentielles).
    - Éléments cliquables ≥44px, lisibilité élevée (laboratoire).
    - Thèmes cohérents (clair/sombre), contraste élevé, persistants.


## 2) Calibration: précision scientifique, guidage pas-à-pas

- Objectif: garantir que chaque capteur mesure avec sensibilité correcte, biais minimal et linéarité acceptable.
- Workflow guidé (assistant en 5 étapes):

1. Préparation: sélection du capteur, conditions, consignes (zéro, référence).
2. Acquisition de points de calibration: mesures à niveaux/états étalons (N points).
3. Modélisation: calcul de la droite de régression y = m x + b (pente m, intercept b), R², erreurs.
4. Validation: critères seuils (tolérances sur m, b, R², résidus), alertes si hors plage.
5. Certification: génération d’un certificat (PDF) et archivage historique.
- Visualisations essentielles:
    - Scatter X (référence) vs Y (mesuré) avec droite de régression.
    - Résidus vs X pour détecter non-linéarités.
    - Évolution dans le temps de m/b (stabilité).
- Indicateurs clés affichés:
    - Pente (sensibilité), Intercept (biais), R² (qualité d’ajustement).
    - Erreurs standard, seuils de tolérance, verdict (OK/À recalibrer).
- Bonnes pratiques d’UX:
    - Étapes claires, possibilité de revenir sans perdre les données.
    - Boutons Start/Measure/Validate larges, feedback immédiat.
    - Messages d’aide et d’alertes explicites.


## 3) Articulation Acquisition ↔ Calibration

- La calibration précède et fiabilise l’acquisition: les coefficients (m, b) validés sont appliqués en temps réel pour corriger les mesures (affichage et enregistrement).
- Sur l’acquisition, afficher un badge “Calibré (date)” par capteur; avertir si calibration absente/obsolète.
- Possibilité de lancer une mini-vérification (quick check) depuis l’acquisition pour détecter une dérive et recommander une recalibration.


## 4) Architecture et qualité

- État global unifié: thème, configuration active, capteurs sélectionnés, persistés (localStorage) et diffusés via contexte/Store (p.ex. Zustand/Redux/Context API).
- Performance signal: utiliser des traitements FFT optimisés pour spectres/indicateurs (ex: pyFFTW avec plans et “wisdom”), batchs pour réduire la charge, pas d’allocation répétée.
- Robustesse: gestion des erreurs capteur (déconnexion, saturation), reprise propre, logs et traçabilité.


## 5) Critères de validation

- Acquisition: latence faible, rendu fluide, pas de pertes de données, export fidèle.
- Calibration: tolérances respectées (m proche attendu, |b| faible, R² élevé), résidus sans tendance.
- UX: changements de thème cohérents, lisibilité, parcours clair; tests en conditions simulées avant intégration finale.

Ce cadre assure une interface d’acquisition efficace pour l’opérateur et une calibration scientifiquement solide, avec une expérience fluide, professionnelle et adaptée au laboratoire.

<div style="text-align: center">⁂</div>

[^1]: acqui.md

