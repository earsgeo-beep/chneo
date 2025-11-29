<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# Prompt ultra-précis pour intégrer l’interface au logiciel CHNeoWave (adaptation interface → logiciel et logiciel → interface)

Objectif: intégrer l’interface prototype (Lovable/isolée) dans le logiciel CHNeoWave existant sans casser l’architecture, en adaptant l’interface aux contraintes et fonctionnalités réelles du logiciel, et en alignant le logiciel sur les éléments UI indispensables quand ils sont manquants. L’intégration doit être bidirectionnelle mais pilotée par le logiciel: priorité à la vérité métier et aux modules core existants.

Instructions à donner à l’agent:

Contexte et principes

- Base de code: CHNeoWave (Python backend + frontend React/Tailwind ou équivalent).
- Interface à intégrer: prototype UI (Lovable/isolée) validée visuellement.
- Principe directeur: adapter l’interface au logiciel, pas l’inverse, sauf lorsque des éléments UI révèlent un besoin fonctionnel évident et déjà présent implicitement dans le logiciel (ex: actions, états, feedbacks non exposés).
- Aucune régression fonctionnelle. Respect strict des modules existants, des conventions de code, des contrats d’API et des formats de données.

Étapes d’intégration (phase par phase)

Phase 0 — Cartographie et alignement

1) Inventaire exhaustif

- Lister toutes les fonctionnalités existantes du logiciel (modules, endpoints, événements, états, flux de données, formats d’export, gestion capteurs, acquisition, calibration, analyse, configuration).
- Lister toutes les fonctionnalités de l’interface prototype (écrans, composants, contrôles, tableaux de bord, graphes, thèmes, accessibilité).
- Produire une table de correspondance “Fonctionnalité logiciel ↔ Élément UI” avec 4 catégories:
A. Existe dans les deux: intégrer tel quel.
B. Existe dans le logiciel mais pas dans l’UI: ajouter/compenser dans l’UI.
C. Existe dans l’UI mais pas dans le logiciel: adapter ou retirer, ou créer le point d’extension minimal si la fonctionnalité est requise par l’opérationnel.
D. Divergences (noms, flux, états): normaliser côté UI sans casser les APIs.

2) Contrats techniques

- Documenter les contrats d’API et modèles de données (schemas JSON, nomenclatures, unités, métadonnées).
- Définir les adaptateurs nécessaires (mappers) si l’UI attend un format différent.

Livrables: matrice de mapping, liste des gaps, plan de correction, schémas de données.

Phase 1 — Intégration structurelle
3) Architecture UI

- Insérer l’UI dans la structure du frontend existant (routing, providers, stores).
- Unifier le système de thème global (ThemeProvider + persistance), supprimer tous états locaux de thème restants, garantir propagation instantanée.
- Unifier la gestion d’état (Redux/Zustand/Context): une seule source de vérité pour capteurs, sessions, thèmes, préférences, configuration acquisition/calibration.

4) Points d’ancrage fonctionnels

- Relier les actions UI aux services existants:
    - Acquisition: start/pause/stop, sélection capteurs, fréquence, buffers, événements.
    - Calibration: étapes guidées, calculs, stockage certificats, historique.
    - Analyse: stats/spectres, exports.
    - Configuration: profils, projets/sessions.
- Introduire des adaptateurs si nécessaire (convertisseurs d’unités, renommages de champs, validation).

Livrables: code intégré, hooks/services unifiés, plan de tests smoke.

Phase 2 — Parité fonctionnelle et corrections
5) Couverture complète

- Pour chaque élément de la matrice:
    - Catégorie A: valider l’intégration et la parité des comportements.
    - Catégorie B: ajouter les écrans/contrôles manquants à l’UI en s’alignant sur les APIs existantes (pas de sur-spécification).
    - Catégorie C: si l’UI introduit une fonction absente mais nécessaire, proposer un point d’extension minimal backend (facultatif) OU rétrofiter l’UI pour masquer/adapter sans tromper l’utilisateur.
    - Catégorie D: normaliser les noms/états/erreurs côté UI pour coller au logiciel.
- Nettoyage Tailwind et thèmes:
    - Supprimer le “prototype tailwind”, centraliser les tokens (couleurs, espacements, typographies), palettes Light/Dark/Solarized corrigées, contrastes ≥7:1, cohérence globale.
    - Remplacer toute classe conditionnelle ad hoc par des utilitaires/variants normalisés.

Livrables: parité validée, backlog des écarts restants avec recommandations.

Phase 3 — Qualité, accessibilité, performance
6) Qualité et normes

- Accessibilité: focus trap, rôles ARIA, navigation clavier, tailles cibles ≥44px, messages d’erreur descriptifs, états chargement/désactivé, contrastes vérifiés.
- Performance: éviter re-renders inutiles, mémoïsation sur graphes/long lists, cadence 60fps, usage workers si FFT lourdes côté UI.
- Résilience: gestion erreurs réseau/capteurs, retries, messages utilisateurs, logs.

7) Tests et validation

- Tests unitaires et d’intégration UI pour flux critiques (acquisition, calibration, analyse, export).
- Tests E2E (scénarios opérateur).
- Scénarios thème: bascule instantanée, persistance, toutes pages.
- Scénarios dégradés: capteur déconnecté, données manquantes, formats inattendus.

Livrables: rapports de tests, checklist d’acceptation, vidéos/gifs courtes de démonstration.

Règles d’adaptation (claires et strictes)

- Toujours prioriser la vérité du logiciel: l’UI s’aligne sur les contrats d’API et les données réelles.
- Ne jamais masquer une fonctionnalité logicielle essentielle: si elle n’est pas visible dans l’UI, l’ajouter de manière cohérente et non intrusive.
- Éviter les “features fantômes” en UI: si le logiciel ne les supporte pas, les retirer ou griser avec message explicite et plan d’évolution.
- Respecter la terminologie métier existante (capteurs, sessions, projets, normes).
- Ne jamais casser un endpoint ou changer un modèle de données sans adapter tous les consommateurs et ajouter migration/compat.

Livrables attendus finaux

- Interface intégrée et fonctionnelle, alignée au logiciel (acquisition, calibration, analyse, configuration, export).
- Thèmes synchronisés globalement, propres, contrastés, persistants.
- Code propre: conventions, dossiers standardisés, composants réutilisables, hooks/services centralisés, commentaires/doc.
- Documentation: “Guide d’intégration UI CHNeoWave” + “Catalogue composants” + “Schémas API” + “Matrice de correspondance”.
- Rapport de non-régression et plan de maintenance.

Checklists de validation

- Fonctionnelle: toutes les actions du logiciel sont accessibles dans l’UI, sans pertes ni divergences.
- Thème: bascule instantanée, cohérence sur toutes les pages/composants, Solarized corrigé, couleurs de texte lisibles.
- Accessibilité: navigation clavier complète, ARIA, contrastes ≥7:1, tailles cibles OK.
- Performance: UI fluide, chargement raisonnable, graphes sans saccades.
- Résilience: gestion propres des erreurs/états limites.

Contraintes

- Ne pas introduire de dettes supplémentaires: tout code nouveau doit être testé, typé, et documenté.
- Zéro régression: exécuter une batterie de tests sur les modules critiques après chaque lot.
- Revue obligatoire: PRs petites et atomiques, diff clair, plan de rollback.

Format de sortie demandé

- Plan d’intégration détaillé (par étapes, fichiers impactés, estimations).
- Liste des composants modifiés/ajoutés/supprimés.
- Mappages de données et adaptateurs créés.
- Rapport d’écarts restants et recommandations.
- Scripts de test et résultats.

Note à l’agent

- Travailler en itérations courtes (PR atomiques).
- Commencer par la mise en place des providers globaux (thème/état), puis raccorder acquisition → calibration → analyse → configuration → export.
- Toujours fournir un aperçu visuel (captures ou storybook) avant fusion.
- S’arrêter avant toute modification de contrat backend sans approbation explicite.

