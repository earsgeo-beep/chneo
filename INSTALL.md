# Installation

Ce guide correspond au depot actuel, pas a un ancien executable autonome.

## Plateforme cible

- Windows 10/11
- Python 3.10 ou plus recent recommande
- environnement de bureau avec Qt

## Installation rapide

```powershell
git clone https://github.com/Gameminde/Chneowave.git
cd Chneowave

python -m venv .venv
.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
pip install PySide6 numpy pandas h5py
```

## Dependances optionnelles

- `reportlab` : utile pour certaines briques PDF annexes hors flux GUI principal
- DLLs Measurement Computing : requises uniquement pour l'acquisition MCC reelle

## Verification minimale

```powershell
python chneowave.py --version
python -m compileall src\hrneowave
python chneowave.py
```

## Points d'entree disponibles

```powershell
python chneowave.py
python main.py
python -m hrneowave
CHNeoWave.bat
```

## Support MCC

Le depot conserve le dossier `Measurement Computing` parce que le wrapper MCC le recherche encore. Sans carte ou sans DLLs compatibles:

- l'application peut demarrer
- l'acquisition reelle n'est pas disponible
- le controleur bascule en mode simulation

## Stockage des projets

Les projets sont crees par defaut dans:

```text
%USERPROFILE%\CHNeoWave_Projects
```

Chaque projet contient:

```text
data/
sessions/
exports/
analysis/
calibration/
project_metadata.json
```

## Probleme frequents

### `PySide6 n'est pas installe`

```powershell
pip install PySide6
```

### `No module named pandas`

```powershell
pip install pandas
```

### Export HDF5 indisponible

```powershell
pip install h5py
```

### Acquisition MCC non detectee

Verifier:

- la presence des DLLs Measurement Computing
- l'installation pilote MCC
- la detection de la carte sur la machine cible

Sans cela, utiliser le mode simulation pour le developpement et les tests GUI.
