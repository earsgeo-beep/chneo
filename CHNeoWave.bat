@echo off
REM =====================================================
REM CHNeoWave - Lanceur Windows
REM Laboratoire Maritime - Interface de Houle
REM =====================================================

echo.
echo ========================================
echo    CHNeoWave - Laboratoire Maritime
echo ========================================
echo.

set PYTHONUTF8=1

REM Utiliser Python 3.13 si disponible, sinon le Python du PATH
py -3.13 --version >nul 2>&1
if errorlevel 1 (
    python --version >nul 2>&1
    if errorlevel 1 (
        echo ERREUR: Python n'est pas installe ou pas dans le PATH
        echo Veuillez installer Python 3.8+ depuis python.org
        pause
        exit /b 1
    )
    set PY_CMD=python
) else (
    set PY_CMD=py -3.13
)

REM Aller dans le répertoire du script
cd /d "%~dp0"

REM Vérifier si le fichier principal existe
if not exist "chneowave.py" (
    echo ERREUR: Fichier chneowave.py introuvable
    echo Verifiez que vous etes dans le bon repertoire
    pause
    exit /b 1
)

echo Lancement de CHNeoWave...
echo.

REM Lancer CHNeoWave avec diagnostic des erreurs natives (DLL MCC)
%PY_CMD% -X faulthandler chneowave.py --gui

REM Vérifier le code de sortie
if errorlevel 1 (
    echo.
    echo ERREUR: CHNeoWave s'est ferme avec une erreur
    echo Consultez chneowave_debug.log et chneowave_crash.log
    pause
) else (
    echo.
    echo CHNeoWave s'est ferme normalement
)

echo.
echo Appuyez sur une touche pour fermer...
pause >nul
