@echo off
setlocal

set EXE_NAME=MaritimeDBServerFinal.exe
set EXE_PATH=%~dp0%EXE_NAME%

if not exist "%EXE_PATH%" (
  echo ERROR: %EXE_NAME% not found!
  pause
  exit /b 1
)

echo Starting Final Maritime Database Server...
start "Final Maritime DB Server" "%EXE_PATH%"

echo Waiting 3 seconds for server to initialize...
timeout /t 3 >nul

echo Opening interface in your browser at http://127.0.0.1:8000/
start "" "http://127.0.0.1:8000/"

endlocal
