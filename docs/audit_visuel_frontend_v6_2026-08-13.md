# Audit visuel exhaustif et refonte frontend v6

**Produit :** CHNeoWave  
**Dépôt audité :** `earsgeo-beep/chneo`  
**Base de l’audit :** `main` au commit `1eb340b`  
**Date :** 13 août 2026  
**Contexte de validation :** poste de travail 1440 × 900, thèmes clair et sombre, fichier réel « Copie de extension port de djendjen nord 35° calibration.raw » (9 voies, 32 Hz, 69 120 échantillons par voie, 2 160 s).

## 1. Conclusion exécutive

Le défaut principal ne venait pas d’un manque de décoration. Il venait d’une architecture visuelle qui attribuait la même importance à presque tous les éléments. Le menu, la navigation, la source, les commandes de voies, les statuts, deux graphes simultanés, les métriques et l’inspecteur étaient empilés en permanence. Le signal scientifique devenait une zone parmi d’autres alors qu’il doit être la scène principale.

Une seconde cause était directement présente dans la feuille de style : la règle globale appliquait la couleur de fond à **tous** les `QWidget`. Comme `QLabel`, `QCheckBox` et de nombreux conteneurs héritent de `QWidget`, les textes apparaissaient sur des rectangles gris séparés. Cela donnait l’impression de « boutons sur des boutons » et de colonnes imbriquées, même quand le layout Qt était correct.

La refonte v6 remplace cette logique par un poste scientifique continu :

- une barre native compacte et une navigation horizontale de 48 px ;
- deux lignes compactes pour la source et les voies ;
- **un seul graphe principal**, commutable entre signal temporel et spectre PSD ;
- un inspecteur Welch repliable ;
- une seule palette sémantique, partagée par toutes les vues ;
- des graphes de calibration réellement clairs en thème clair et sombres en thème sombre ;
- des noms de sondes courts `S01` à `S09` dans l’espace graphique ;
- aucune décision automatique de rejet : le diagnostic reste séparé de la décision ingénieur.

## 2. Méthode d’audit

L’audit ne repose pas uniquement sur la lecture du code. Les six espaces de travail ont été instanciés avec le moteur Qt réel en mode hors écran, à leur résolution de production. La vue Analyse a été alimentée avec le RAW Djendjen, puis le calcul temporel, la PSD de Welch, les métriques et le rapport ont été exécutés avant capture.

Les contrôles ont porté sur :

1. la hiérarchie visuelle et la surface réellement donnée au travail scientifique ;
2. la cohérence des couleurs, des états et des contrastes ;
3. la densité d’information et la répétition des libellés ;
4. la continuité entre Projet, Calibration, Acquisition, Analyse et Rapport ;
5. la lisibilité à 1440 × 900, sans zoom artificiel ;
6. le comportement clair/sombre ;
7. la capacité à comparer les neuf voies sans limiter l’analyse à `channel_00`.

## 3. Mesures objectives avant refonte

| Indicateur | Valeur observée | Conséquence |
|---|---:|---|
| Occurrences de couleurs hexadécimales dans le frontend | 374 | Les couleurs sont répétées et difficiles à gouverner. |
| Couleurs hexadécimales distinctes | 205 | Plusieurs systèmes visuels coexistent. |
| Appels `setStyleSheet(...)` dans le code Python | 68 | Les styles locaux peuvent contredire le thème global. |
| Dimensions fixes/min/max | 74 | L’interface résiste mal aux résolutions et DPI différents. |
| Gradients ou rayons décoratifs hérités | 54 | Présence résiduelle d’un ancien langage « application générique ». |
| Hauteur de l’ancienne navigation principale | 58 px | Surface verticale consommée avant le travail. |
| Disposition Analyse | 2 graphes empilés | Chaque graphe recevait une hauteur insuffisante. |
| Bande source/voies | 3 rangées | Répétition de commandes et d’aide textuelle. |
| Taille d’une voie dans le ruban | 154 × 42 px | Neuf sondes occupaient une largeur excessive. |

## 4. Défauts par espace de travail

### 4.1 Shell global — sévérité critique

**Défauts :** barre supérieure trop haute, marque sur deux lignes, projet/source/matériel sur deux lignes, navigation et contexte en concurrence, rectangles de fond derrière presque chaque libellé.

**Correction :** marque sur une ligne, navigation de 48 px, contexte projet et matériel sur une ligne, source retirée du shell global car elle appartient à l’analyse, fond transparent par défaut pour les widgets enfants.

### 4.2 Projet — sévérité moyenne

**Défauts :** les labels ressemblaient à des bandeaux indépendants ; les cartes de droite et le formulaire utilisaient trop de traits gris ; le texte d’aide participait à la hiérarchie au même niveau que les champs.

**Correction :** surfaces blanches continues, labels sans fond, bordures faibles, texte secondaire désaturé, action principale conservée en bas à droite.

### 4.3 Calibration — sévérité élevée

**Défauts :** graphe systématiquement sombre dans le thème clair ; rupture brutale avec le reste de l’application ; trop de noir attirant l’œil avant même qu’un signal existe.

**Correction :** palette Matplotlib synchronisée avec le thème global. Le signal, les axes, la grille, les points et la droite `m×x+b` utilisent désormais les rôles `mesure`, `référence`, `grille` et `texte`, sans valeurs décoratives indépendantes.

### 4.4 Acquisition — sévérité élevée

**Défauts :** titres et valeurs affichés sur des bandes alternées ; sensation de tableur administratif ; état vide très étendu ; nombreuses bordures d’égale intensité.

**Correction :** groupes Qt rendus comme surfaces continues, titres de groupe discrets, actions primaires/secondaires homogènes, disparition des fonds derrière les libellés. La prochaine itération pourra employer l’espace vide pour une topologie matérielle temps réel lorsque plusieurs familles de cartes seront intégrées.

### 4.5 Analyse — sévérité critique

**Défauts :** deux graphes permanents, trois rangées de commandes, légendes longues `channel_00`, panneau Welch permanent, sept blocs métriques et plusieurs statuts concurrents. Le contenu scientifique était visible, mais sa lecture était fatigante.

**Correction :** scène unique `QStackedWidget`, boutons `SIGNAL TEMPOREL` et `SPECTRE PSD`, passage automatique au spectre après le calcul, retour instantané au temporel, inspecteur `PARAMÈTRES` repliable, ruban des voies sur la même ligne que les commandes, légendes `S01` à `S09`.

### 4.6 Rapport — sévérité moyenne

**Défauts :** la configuration prenait visuellement autant d’importance que le livrable ; l’aperçu vide accentuait le sentiment de logiciel administratif.

**Correction :** aperçu conservé comme surface principale ; configuration réunie dans un dock latéral cohérent ; une fois l’analyse chargée, les tableaux statistiques et spectraux occupent immédiatement la page. Les décisions ingénieur restent visibles dans le rapport.

### 4.7 Préférences — sévérité élevée

**Défauts :** l’utilisateur pouvait choisir trois couleurs personnalisées héritées d’un ancien thème Material, alors que l’application exige une signification stable des états.

**Correction :** seulement deux thèmes de production, clair et sombre. La palette sémantique est verrouillée : pétrole pour les actions, cyan pour la mesure, ambre pour l’attention, rouge pour le danger et vert pour la connexion/validation explicite.

## 5. Nouveau modèle d’information

```text
Menu natif
└── Navigation laboratoire + projet + matériel
    └── Source et options de lecture
        └── Ruban compact des sondes
            └── Scène scientifique unique
                ├── Signal temporel
                └── Spectre PSD
            ├── Inspecteur repliable
            └── Rail de métriques
```

La profondeur visuelle maximale est volontairement limitée. Une commande peut appartenir au shell, à la scène ou à l’inspecteur, mais elle ne doit pas être enfermée dans plusieurs cartes successives.

## 6. Système de couleurs v6

| Rôle | Clair | Sombre | Utilisation autorisée |
|---|---|---|---|
| Fond application | `#F3F5F6` | `#08141B` | Espaces entre surfaces |
| Surface | `#FFFFFF` | `#0F2029` | Panneaux de travail |
| Canvas scientifique | `#FCFDFD` | `#071820` | Graphes uniquement |
| Texte principal | `#263840` | `#CDD7DB` | Libellés et valeurs courantes |
| Texte fort | `#102B35` | `#F1F5F6` | Titres et résultats |
| Action primaire | `#087F99` | `#32AEC5` | Action active, sélection, focus |
| Mesure active | `#25B3CD` | `#35BCD5` | Signal actif et repères de mesure |
| Succès | `#1B7B5E` | `#4BC39B` | Connexion ou validation explicite |
| Attention | `#A66B16` | `#E0A044` | Alerte à examiner |
| Danger | `#A9434D` | `#E16670` | Erreur ou décision de rejet explicite |

Contrastes mesurés : texte principal clair 11,15:1 ; texte secondaire clair 4,67:1 ; texte principal sombre 12,73:1 ; texte secondaire sombre 6,23:1 ; chrome 13,55:1. Les couples principaux dépassent les niveaux AA attendus pour du texte normal.

## 7. Comparaison géométrique

| Élément | Avant | v6 |
|---|---:|---:|
| Navigation principale | 58 px | 48 px |
| Bande source/voies | 3 rangées | 2 rangées |
| Graphes visibles simultanément | 2 | 1 |
| Représentations accessibles | Temporel + PSD empilés | Temporel / PSD commutables |
| Tuile de voie | 154 × 42 px | 122 × 32 px |
| Légende | `channel_00…08` | `S01…S09` |
| Inspecteur | Toujours présent | Repliable |
| Calibration en thème clair | Canvas sombre | Canvas clair synchronisé |

## 8. Mockups de direction

Les mockups servent de référence de composition, pas de copie littérale. Ils fixent la hiérarchie : un graphe, un inspecteur, un rail de mesures et aucune carte marketing.

- [Concept clair](mockups/chneowave-v6-light-concept.png)
- [Concept sombre](mockups/chneowave-v6-dark-concept.png)

## 9. Captures réelles après implémentation

- [Comparaison Analyse avant / après](screenshots/v6/comparison-analysis-before-after.png)
- [Projet — clair](screenshots/v6/after/01-welcome-light.png)
- [Calibration — clair](screenshots/v6/after/02-calibration-light.png)
- [Acquisition — clair](screenshots/v6/after/03-acquisition-light.png)
- [Analyse spectrale — clair](screenshots/v6/after/04-analysis-spectrum-light.png)
- [Analyse temporelle — clair](screenshots/v6/after/05-analysis-time-light.png)
- [Rapport scientifique alimenté](screenshots/v6/after/08-report-populated-light.png)
- [Analyse spectrale — sombre](screenshots/v6/after/07-analysis-spectrum-dark.png)

Les captures antérieures sont conservées dans `docs/screenshots/v6/before/` pour rendre l’évolution vérifiable.

## 10. Règles obligatoires pour les futures vues

1. Une vue scientifique possède une seule scène dominante.
2. Une couleur ne peut pas être choisie localement si un rôle sémantique existe.
3. Les emojis, gradients décoratifs et cartes de marketing sont exclus.
4. Les valeurs numériques utilisent une police monospace ; les libellés utilisent la police UI.
5. Une alerte automatique ne devient jamais une décision d’acceptation ou de rejet.
6. Les options rares vont dans l’inspecteur ou les préférences, jamais dans un nouveau bandeau permanent.
7. Tout nouvel écran doit être capturé en clair et sombre à 1440 × 900 avant validation.
8. Les neuf voies doivent rester sélectionnables ; aucune vue ne doit être implicitement limitée à la voie 0.

## 11. Dette restante et prochaine étape recommandée

Le nouveau shell et les vues actives sont unifiés, mais le dépôt contient encore des composants Material et des helpers d’anciens thèmes qui ne pilotent plus la fenêtre principale. Ils doivent être retirés progressivement après une cartographie d’imports, afin de ne pas casser les dialogues secondaires. La prochaine étape frontend utile n’est pas une nouvelle palette : c’est un composant de **topologie matérielle** partagé par Acquisition et Calibration, affichant carte, canaux, capteurs, unités, calibration et état live dans un modèle unique.
