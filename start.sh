#!/bin/bash

echo "================================================"
echo "Axxon One Referenzbild-Exporter V2.0"
echo "================================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "FEHLER: Python 3 ist nicht installiert!"
    echo "Bitte installieren Sie Python 3.8 oder höher"
    exit 1
fi

echo "Python gefunden: $(python3 --version)"
echo ""

# Check if dependencies are installed
echo "Prüfe Abhängigkeiten..."
if ! python3 -c "import flet" &> /dev/null; then
    echo "Flet nicht gefunden. Installiere Abhängigkeiten..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "FEHLER: Installation fehlgeschlagen!"
        exit 1
    fi
fi

echo ""
echo "Starte Anwendung..."
echo ""

# Start the application
python3 main.py

if [ $? -ne 0 ]; then
    echo ""
    echo "FEHLER: Die Anwendung wurde mit einem Fehler beendet."
    read -p "Drücken Sie Enter zum Beenden..."
fi
