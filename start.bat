@echo off
echo ================================================
echo Axxon One Referenzbild-Exporter V2.0
echo ================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo FEHLER: Python ist nicht installiert!
    echo Bitte installieren Sie Python 3.8 oder hoeher von https://www.python.org/
    pause
    exit /b 1
)

echo Python gefunden!
echo.

REM Check if dependencies are installed
echo Pruefe Abhaengigkeiten...
python -c "import flet" >nul 2>&1
if errorlevel 1 (
    echo Flet nicht gefunden. Installiere Abhaengigkeiten...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo FEHLER: Installation fehlgeschlagen!
        pause
        exit /b 1
    )
)

echo.
echo Starte Anwendung...
echo.

REM Start the application
python main.py

if errorlevel 1 (
    echo.
    echo FEHLER: Die Anwendung wurde mit einem Fehler beendet.
    pause
)
