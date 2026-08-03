# Installation

Ce guide correspond au depot actuel, pas a un ancien executable autonome.

## Plateforme cible

- Windows 10/11
- Python 3.10 ou plus recent recommande
- environnement de bureau avec Qt

## Installation rapide

```powershell
git clone https://github.com/earsgeo-beep/chneo.git
cd chneo

python -m venv .venv
.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
pip install -e ".[mcc]"
```

## Installation hors ligne au laboratoire

CHNeoWave n'a besoin d'aucune connexion internet pendant l'acquisition. Sur un
poste connecte servant uniquement a preparer l'installation:

```powershell
python -m pip download ".[mcc]" --dest wheelhouse
```

Copier ensuite le depot et le dossier ``wheelhouse`` sur le poste du laboratoire:

```powershell
python -m pip install --no-index --find-links wheelhouse -e ".[mcc]"
```

Le pilote MCC Universal Library et InstaCal doivent etre installes localement.
Le paquet Python ``mcculw`` utilise cette installation locale; aucune connexion
internet n'est requise a l'execution.

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
