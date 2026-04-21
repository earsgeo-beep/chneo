# CHNeoWave

CHNeoWave est une application desktop Qt pour l'acquisition, le traitement et l'export de donnees maritimes en laboratoire de modele reduit. Le depot a ete nettoye pour ne decrire que le flux actif valide dans le code.

Le runtime principal est un client Python/Qt lance depuis `chneowave.py`, `main.py`, `python -m hrneowave` ou `CHNeoWave.bat`.

## Flux actuellement branche

1. creation d'un projet
2. acquisition ou simulation multi-canaux
3. export des donnees brutes
4. analyse post-acquisition
5. generation de rapport

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
pip install PySide6 numpy pandas h5py
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

## Limites connues

- la vue d'acquisition expose encore des boutons de chargement/sauvegarde de configuration non implementes
- le mode HDF5 depend de `h5py`
- le support MCC depend des DLLs Measurement Computing et du materiel cible
- plusieurs modules secondaires restent presents dans `src/hrneowave`, mais la documentation ne couvre que le flux actif valide

## Documentation

- [INSTALL.md](INSTALL.md)
- [docs/index.rst](docs/index.rst)
- [docs/user_guide.rst](docs/user_guide.rst)
- [docs/technical_guide.rst](docs/technical_guide.rst)
