# Aria CEO v7.0 - Installation ohne Voraussetzungen

## Übersicht

Version 7.0 kann **ohne Vorinstallation** auf einem frischen Linux-System installiert werden. Der Installer `install_aria_v7.sh` automatisiert alles:

- ✅ Prüft Python 3.8+
- ✅ Installiert pip falls nötig
- ✅ Erstellt virtuelle Umgebung
- ✅ Installiert alle Python-Dependencies
- ✅ Legt Verzeichnisstruktur an
- ✅ Kopiert alle Dateien
- ✅ Konfiguriert Systemd-Service
- ✅ Validiert Konfiguration

## Voraussetzungen

Minimal:
- Linux-System (Ubuntu/Debian empfohlen)
- Root-Zugriff (sudo)
- Internet-Verbindung für pip-Pakete

## Installation

```bash
# Repository klonen oder entpacken
cd aria-ceo-v6.3

# Installer ausführbar machen
chmod +x install_aria_v7.sh

# Installation starten (als root/sudo)
sudo ./install_aria_v7.sh
```

## Was wird installiert?

```
/opt/aria-system/
├── venv/                    # Python Virtual Environment
├── agents/
│   ├── aria_ceo_v7.py      # Hauptskript
│   ├── memory_manager.py
│   └── tools.py
├── config/
│   ├── config.yaml         # Hauptkonfiguration (LLM, DB, etc.)
│   ├── agents_v7.yaml      # Agent-Definitionen
│   └── tools_v7.yaml       # Tool-Konfiguration
├── integrations/
│   └── slack_bot_v6.py     # Optional: Slack-Integration
└── docs/                    # Dokumentation

/etc/systemd/system/aria-ceo.service  # Systemd Service
```

## Nach der Installation

### 1. Konfiguration anpassen

Bearbeite `/opt/aria-system/config/config.yaml`:
- LLM-Endpoints (Ollama)
- Datenbank-Verbind-Stepungen
- Dashboard-URL
- GitHub/Docker Hub (optional)

### 2. Konfiguration validieren

```bash
/opt/aria-system/venv/bin/python /opt/aria-system/agents/aria_ceo_v7.py --validate-config
```

### 3. Service starten

```bash
sudo systemctl start aria-ceo.service
sudo systemctl status aria-ceo.service
```

### 4. Logs ansehen

```bash
journalctl -u aria-ceo.service -f
```

## Manuelle Nutzung (ohne Service)

```bash
# Dry-Run (nur Initialisierung)
/opt/aria-system/venv/bin/python /opt/aria-system/agents/aria_ceo_v7.py --dry-run

# Projekt starten
/opt/aria-system/venv/bin/python /opt/aria-system/agents/aria_ceo_v7.py --project "Baue eine REST API"
```

## Troubleshooting

### Python nicht gefunden
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install python3 python3-pip python3-venv
```

### Service startet nicht
```bash
# Logs prüfen
journalctl -u aria-ceo.service -n 50

# Konfiguration prüfen
/opt/aria-system/venv/bin/python /opt/aria-system/agents/aria_ceo_v7.py --validate-config

# Manuell starten (zum Testen)
cd /opt/aria-system
/opt/aria-system/venv/bin/python agents/aria_ceo_v7.py --dry-run
```

### Module nicht gefunden
- Prüfe, ob alle Dateien in `/opt/aria-system/agents/` vorhanden sind
- Prüfe Permissions: `ls -la /opt/aria-system/agents/`

## Upgrade von v6.3

Wenn bereits v6.3 installiert ist:

```bash
# Backup erstellen
sudo systemctl stop aria-ceo.service
sudo cp -r /opt/aria-system /opt/aria-system.backup

# v7 installieren (überschreibt v6.3)
sudo ./install_aria_v7.sh

# Konfiguration migrieren (falls nötig)
# Bearbeite /opt/aria-system/config/config.yaml
```

## Deinstallation

```bash
sudo systemctl stop aria-ceo.service
sudo systemctl disable aria-ceo.service
sudo rm /etc/systemd/system/aria-ceo.service
sudo systemctl daemon-reload
sudo rm -rf /opt/aria-system
```

