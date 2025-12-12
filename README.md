# Axxon One Referenzbild-Exporter V2.0

Moderne Desktop-Anwendung zum Export von Referenzbildern aus Axxon One VMS in professionelle PDF-Reports.

## Features

- ✅ **Moderne GUI** mit Flet (Flutter-basiert, Material Design)
- ✅ **Live-Snapshots** von allen Kameras
- ✅ **Archiv-Snapshots** von einem beliebigen Zeitpunkt (optional)
- ✅ **Mehrere Auflösungen** (Original, Full HD, 4K, HD)
- ✅ **Projektdetails** (Name, Standort, Techniker, Firma)
- ✅ **Logo-Integration** in PDF-Reports
- ✅ **Manuelle Kameraauswahl** mit Suchfunktion
- ✅ **Professionelle PDF-Reports** mit ReportLab
- ✅ **Deutsche Benutzeroberfläche**

## Installation

### Voraussetzungen

- Python 3.8 oder höher
- Zugriff auf einen Axxon One Server

### Schritt 1: Abhängigkeiten installieren

```bash
pip install -r requirements.txt
```

## Verwendung

### Anwendung starten

```bash
python main.py
```

### Workflow

1. **Verbindung einrichten** (Tab 1)
   - Server IP-Adresse eingeben
   - Port eingeben (Standard: 8000 für Linux, 80 für Windows)
   - Benutzername und Passwort eingeben
   - "Verbindung testen" klicken
   - Bei erfolgreicher Verbindung wird automatisch gespeichert

2. **Kameras auswählen** (Tab 2)
   - "Kameras laden" klicken
   - Gewünschte Kameras mit Checkboxen auswählen
   - Optional: Suchfunktion verwenden
   - "Alle auswählen" / "Alle abwählen" Buttons nutzen

3. **Projektdetails eingeben** (Tab 3)
   - Projektname eingeben
   - Standort/Adresse eingeben
   - Techniker-Name eingeben
   - Firma/Unternehmen eingeben
   - Optional: Logo auswählen (PNG, JPG)
   - "Speichern" klicken

4. **Export durchführen** (Tab 4)
   - Optional: "Archivbilder hinzufügen" aktivieren
   - Bei Archivbildern: Datum und Uhrzeit einstellen
   - Auflösung auswählen
   - Speicherort für PDF wählen
   - "PDF exportieren" klicken

## Projektstruktur

```
Axxon Exporter V2.0/
├── main.py                 # Hauptanwendung
├── api_client.py           # Axxon One API-Client
├── config_manager.py       # Konfigurationsverwaltung
├── pdf_generator.py        # PDF-Generierung
├── requirements.txt        # Python-Abhängigkeiten
├── views/                  # UI-Views
│   ├── __init__.py
│   ├── connection_view.py  # Verbindungseinstellungen
│   ├── camera_view.py      # Kameraauswahl
│   ├── project_view.py     # Projektdetails
│   └── export_view.py      # Export-Einstellungen
└── axxon_config.json       # Konfigurationsdatei (wird automatisch erstellt)
```

## Konfiguration

Die Anwendung speichert Einstellungen automatisch in `axxon_config.json`:

- Verbindungsdaten (Server, Port, Benutzername, Passwort)
- Export-Einstellungen (Auflösung, Archiv-Optionen)
- Projektdetails (Name, Standort, Techniker, Firma, Logo-Pfad)

## Axxon One API

Die Anwendung verwendet die Axxon One REST API:

- **Kameraliste**: `GET /camera/list`
- **Live-Snapshot**: `GET /live/media/snapshot/{VIDEOSOURCEID}?w=X&h=Y`
- **Archiv-Snapshot**: `GET /archive/media/{VIDEOSOURCEID}/{TIMESTAMP}?format=mjpeg&w=X&h=Y`

### Authentifizierung

Die API verwendet HTTP Basic Authentication. Standardmäßig:
- Benutzername: `root`
- Passwort: `root` (muss beim ersten Login geändert werden)

## Fehlerbehebung

### Verbindung schlägt fehl

- Prüfen Sie, ob der Axxon One Server erreichbar ist
- Überprüfen Sie IP-Adresse und Port
- Stellen Sie sicher, dass Benutzername und Passwort korrekt sind
- Prüfen Sie die Firewall-Einstellungen

### Keine Kameras gefunden

- Stellen Sie sicher, dass Kameras im Axxon One konfiguriert sind
- Überprüfen Sie die Benutzerberechtigungen

### Archivbilder nicht verfügbar

- Prüfen Sie, ob für den gewählten Zeitpunkt Aufnahmen vorhanden sind
- Stellen Sie sicher, dass die Archive korrekt konfiguriert sind
- Verwenden Sie UTC+0 Zeitzone

### PDF-Export schlägt fehl

- Stellen Sie sicher, dass mindestens eine Kamera ausgewählt ist
- Überprüfen Sie den Speicherort und Schreibrechte
- Prüfen Sie, ob genügend Speicherplatz verfügbar ist

## Systemanforderungen

- **Betriebssystem**: Windows 10/11, Linux, macOS
- **Python**: 3.8 oder höher
- **RAM**: Mindestens 4 GB (empfohlen 8 GB für viele Kameras)
- **Speicherplatz**: 100 MB + Platz für PDF-Exports
- **Netzwerk**: Zugriff auf Axxon One Server

## Lizenz

Copyright © 2024. Alle Rechte vorbehalten.

## Support

Bei Fragen oder Problemen wenden Sie sich bitte an Ihren Administrator.

## Version

**Version 2.0** - Moderne Flet-basierte GUI mit verbesserter Benutzerfreundlichkeit
