# CHNeoWave

CHNeoWave est une plateforme desktop Qt de laboratoire pour l'acquisition,
la metrologie, le traitement scientifique et la tracabilite de donnees
maritimes. Le noyau ne depend d'aucun constructeur: chaque famille de cartes
est integree par un pilote qui publie ses capacites au registre materiel.

Le runtime principal est un client Python/Qt lance depuis `chneowave.py`, `main.py`, `python -m hrneowave` ou `CHNeoWave.bat`.

## Flux actuellement branche

1. creation d'un projet
2. detection et validation d'un equipement physique
3. calibration des chaines capteur
4. acquisition multi-canaux avec enregistrement HDF5 continu
5. analyse scientifique et controle qualite
6. export et rapport tracable

L'interface utilise une navigation horizontale et une barre de menus desktop.
Le poste de traitement affiche simultanement les signaux et les PSD de toutes
les voies choisies. Une alerte numerique reste un diagnostic automatique;
seul l'ingenieur peut accepter ou rejeter une voie dans le dossier scientifique.

Il n'existe aucun repli automatique vers des donnees artificielles. Sans
equipement physique connecte, l'acquisition reste verrouillee.

## Structure utile du depot

```text
.
├── src/hrneowave/
│   ├── acquisition/
│   ├── core/
│   ├── gui/
│   ├── hardware/
│   ├── tools/
│   └── utils/
├── docs/
├── scripts/
├── Measurement Computing/
├── chneowave.py
├── main.py
└── CHNeoWave.bat
```

## Lancement

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install PySide6 numpy pandas h5py scipy matplotlib pyqtgraph reportlab
python chneowave.py
```

Autres points d'entree:

```powershell
python main.py
python -m hrneowave
CHNeoWave.bat
```

## Dependances reelles

- `PySide6` : requis dans l'etat actuel du theme manager et de la GUI
- `PyQtGraph` : tracés temporels et spectraux interactifs du poste scientifique
- `SciPy` : estimation spectrale Welch et traitements numériques
- `Matplotlib` : figures intégrées aux rapports scientifiques PDF/HTML
- `numpy` : calculs numeriques
- `pandas` : lecture/ecriture CSV cote analyse
- `h5py` : support HDF5
- `reportlab` : seulement pour certaines briques PDF annexes, pas pour le rapport GUI principal

## Arborescence projet generee

Par defaut, les projets sont crees dans `~/CHNeoWave_Projects` avec la structure:

```text
<projet>/
├── data/
├── sessions/
├── exports/
├── analysis/
├── calibration/
└── project_metadata.json
```

## Materiel

Le premier pilote livre est celui de la MCC USB-1608FS. Il utilise l'Universal
Library en mode de detection USB directe et ne depend pas d'une configuration
``cb.cfg`` creee par InstaCal. L'application InstaCal reste utile pour un
diagnostic constructeur, mais elle n'est pas necessaire au lancement de
CHNeoWave. Les pilotes IOtech, Keithley et Amplicon seront ajoutes au meme
registre apres validation sur les materiels reels.

## Limites connues

- le mode HDF5 depend de `h5py`
- le pilote MCC depend des DLLs Measurement Computing installees localement
- la MCC doit encore franchir les paliers de validation 1 min, 10 min et 60 min
  sur le PC Windows du laboratoire
- les autres familles de cartes ne sont pas encore livrees comme pilotes actifs
- plusieurs modules secondaires restent presents dans `src/hrneowave`, mais la documentation ne couvre que le flux actif valide

## Documentation

- [INSTALL.md](INSTALL.md)
- [docs/index.rst](docs/index.rst)
- [docs/user_guide.rst](docs/user_guide.rst)
- [docs/technical_guide.rst](docs/technical_guide.rst)
- [docs/laboratory_platform_architecture_2026-08-09.rst](docs/laboratory_platform_architecture_2026-08-09.rst)
