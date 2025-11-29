@echo off
setlocal

rem The executable is in the same directory as this script
set EXE=%~dp0MaritimeDBServerConsole.exe

if not exist "%EXE%" (
  echo ERROR: Executable not found.
  echo It should be in the same folder as this script.
  pause
  exit /b 1
)

echo Starting Maritime Database Server...
start "Maritime DB Server" "%EXE%"

echo Waiting 3 seconds for server to initialize...
timeout /t 3 >nul

echo Opening interface in your browser at http://127.0.0.1:8000/
start "" "http://127.0.0.1:8000/"

endlocal
