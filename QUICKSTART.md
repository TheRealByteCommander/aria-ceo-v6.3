# Aria CEO v6.3 - Quick Start Guide

Schnellste Methode um Aria CEO v6.3 zu installieren und zu testen.

---

## ⚡ 3-Minuten Installation

### Schritt 1: Paket hochladen (30 Sekunden)

```bash
# Von deinem lokalen Rechner
scp aria_v6.3_FINAL.tar.gz root@192.168.178.150:~
```

### Schritt 2: Installation (1 Minute)

```bash
# Auf CT150 (SSH)
cd ~
tar -xzf aria_v6.3_FINAL.tar.gz
cd aria_v6.3_FINAL
./install_aria_v6.3.sh
```

### Schritt 3: Testen (1 Minute)

**In Slack:**
```
@Aria hello
```

**Erwartung:**
1. 🚀 "Starting project: hello"
2. 👷 "Team is working..."
3. 💬 "Progress Update..."
4. ✅ "Team Discussion Complete..."
5. 🎉 "Project Complete!"

**Fertig!** 🎉

---

## 🔍 Verifizierung

### Service läuft?

```bash
systemctl status aria-ceo.service
```

**Erwartung:**
```
● aria-ceo.service - Aria CEO v6.0 with Slack Bot - Complete Edition
   Active: active (running)
```

### Dashboard erreichbar?

**Browser:** http://192.168.178.150:8090

**Erwartung:**
- Dashboard lädt
- WebSocket verbunden
- Live-Updates sichtbar

### Logs OK?

```bash
journalctl -u aria-ceo.service -n 20
```

**Erwartung:**
```
✓ Aria CEO v6.3 initialized
✓ Dashboard Broadcasts
✓ Slack Status Updates
❌ Clarification Questions (DISABLED)
⚡️ Bolt app is running!
```

---

## 🎯 Erstes Projekt

### Einfaches Projekt

```
@Aria erstelle eine Hello World API mit FastAPI
```

**Dauer:** ~2 Minuten

**Ergebnis:**
- ✅ FastAPI Backend
- ✅ Dockerfile
- ✅ docker-compose.yml
- ✅ README.md
- ✅ Tests
- ✅ GitHub Repository (optional)
- ✅ Docker Hub Image (optional)

### Komplexes Projekt

```
@Aria erstelle einen PDF Reader mit:
- Backend: FastAPI
- Frontend: React
- Features: PDF Upload, Text Extraktion, Suche
- Deployment: Docker
```

**Dauer:** ~5 Minuten

**Ergebnis:**
- ✅ Vollständige Anwendung
- ✅ Frontend + Backend
- ✅ Docker Setup
- ✅ Dokumentation
- ✅ Tests

---

## 📊 Dashboard nutzen

### Dashboard öffnen

**URL:** http://192.168.178.150:8090

### Features

1. **Live Chat**
   - Alle Agent-Nachrichten in Echtzeit
   - Wer spricht mit wem
   - Vollständige Konversation

2. **Projekt-Status**
   - Aktuelles Projekt
   - Fortschritt
   - Geschätzte Restzeit

3. **LLM Monitoring**
   - Welcher LLM Server antwortet
   - Response-Zeiten
   - Token-Nutzung

---

## 🔧 Häufige Befehle

### Service Management

```bash
# Status prüfen
systemctl status aria-ceo.service

# Neu starten
systemctl restart aria-ceo.service

# Logs anschauen
journalctl -u aria-ceo.service -f

# Service stoppen
systemctl stop aria-ceo.service

# Service starten
systemctl start aria-ceo.service
```

### Projekt-Verwaltung

```bash
# Alle Projekte anzeigen
ls -la /opt/aria-system/projects/

# Letztes Projekt öffnen
cd /opt/aria-system/projects/$(ls -t /opt/aria-system/projects/ | head -1)

# Projekt-Dateien anzeigen
tree /opt/aria-system/projects/project-20251019-123456/
```

### Logs durchsuchen

```bash
# Nach Fehler suchen
journalctl -u aria-ceo.service | grep -i error

# Slack-Updates finden
journalctl -u aria-ceo.service | grep -i "slack update"

# Dashboard-Verbindung prüfen
journalctl -u aria-ceo.service | grep -i dashboard

# LLM-Server Status
journalctl -u aria-ceo.service | grep -i "llm server"
```

---

## ⚠️ Troubleshooting

### Problem: Service startet nicht

```bash
# Logs prüfen
journalctl -u aria-ceo.service -n 50

# Häufigste Ursachen:
# 1. Python-Fehler → Datei neu installieren
# 2. Import-Fehler → Dependencies installieren
# 3. Permission-Fehler → Ownership prüfen
```

**Schnelle Lösung:**
```bash
cd ~/aria_v6.3_FINAL
./install_aria_v6.3.sh  # Einfach nochmal ausführen
```

### Problem: Keine Slack Updates

```bash
# Prüfe Logs
journalctl -u aria-ceo.service | grep -i "slack update"

# Sollte zeigen:
# "Slack update sent: ..."

# Wenn nicht:
cd ~/aria_v6.3_FINAL
./install_aria_v6.3.sh
```

### Problem: Dashboard zeigt nichts

```bash
# Dashboard erreichbar?
curl http://192.168.178.150:8090

# Wenn nicht:
systemctl start aria-dashboard.service

# Oder Dashboard manuell starten
cd /opt/aria-dashboard
python3 dashboard.py
```

**Mehr Lösungen:** Siehe TROUBLESHOOTING.md

---

## 🎓 Tipps & Tricks

### 1. Klare Projekt-Beschreibungen

**Gut:**
```
@Aria erstelle eine REST API mit:
- FastAPI Backend
- PostgreSQL Datenbank
- User Authentication (JWT)
- CRUD für Produkte
- Docker Setup
```

**Weniger gut:**
```
@Aria mach mir eine API
```

### 2. Dashboard während Projekt-Ausführung offen lassen

- Siehst du was die Agents diskutieren
- Verstehst du Entscheidungen
- Kannst du Probleme früh erkennen

### 3. Projekte in Slack-Thread diskutieren

- Nutze Threads für Rückfragen
- Halte Haupt-Channel sauber
- Bessere Übersicht

### 4. Regelmäßig Backups prüfen

```bash
# Backups anzeigen
ls -la /opt/aria-system/backups/

# Alte Backups löschen (älter als 30 Tage)
find /opt/aria-system/backups/ -type d -mtime +30 -exec rm -rf {} \;
```

### 5. Logs rotieren

```bash
# Logs älter als 7 Tage löschen
journalctl --vacuum-time=7d

# Logs größer als 100MB löschen
journalctl --vacuum-size=100M
```

---

## 📚 Weitere Dokumentation

- **README.md** - Vollständige Übersicht
- **CHANGELOG.md** - Versions-Historie
- **TROUBLESHOOTING.md** - Detaillierte Problemlösungen
- **ARCHITECTURE.md** - System-Architektur (wenn vorhanden)

---

## 🎯 Nächste Schritte

Nach erfolgreicher Installation:

1. ✅ **Teste verschiedene Projekt-Typen**
   - Web-Anwendungen
   - APIs
   - CLI-Tools
   - Data Processing

2. ✅ **Erkunde das Dashboard**
   - Beobachte Agent-Kommunikation
   - Verstehe Entscheidungsprozesse
   - Nutze Monitoring-Features

3. ✅ **Integriere mit deinen Tools**
   - GitHub für Code-Verwaltung
   - Docker Hub für Images
   - Slack für Kommunikation

4. ✅ **Optimiere deine Workflows**
   - Erstelle Projekt-Templates
   - Definiere Best Practices
   - Automatisiere wiederkehrende Tasks

---

## 🏆 Erfolgs-Kriterien

Du weißt dass Aria CEO v6.3 korrekt läuft wenn:

- ✅ Service ist "active (running)"
- ✅ Slack zeigt 5 Nachrichten pro Projekt
- ✅ Dashboard zeigt Live-Updates
- ✅ Projekte werden erfolgreich abgeschlossen
- ✅ GitHub/Docker Hub Integration funktioniert
- ✅ Keine Fehler in Logs

**Wenn alle Punkte ✅ sind: Perfekt! 🎉**

---

## 💡 Pro-Tipps

### Parallele Entwicklung

Während Aria an einem Projekt arbeitet:
- Kannst du im Dashboard zuschauen
- Kannst du Logs beobachten
- Kannst du bereits nächstes Projekt planen

### Projekt-Qualität

Aria erstellt immer:
- ✅ Funktionierende Code-Basis
- ✅ Grundlegende Tests
- ✅ Docker Setup
- ✅ README mit Anleitung

Du solltest noch hinzufügen:
- 🔧 Erweiterte Tests
- 🔧 CI/CD Pipeline
- 🔧 Monitoring
- 🔧 Security Hardening

### Team-Nutzung

Wenn mehrere Personen Aria nutzen:
- Nutzt Slack-Threads
- Koordiniert Projekt-Timing
- Teilt Dashboard-Zugriff
- Dokumentiert Best Practices

---

**Viel Erfolg mit Aria CEO v6.3!** 🚀

---

**Version:** 6.3-final  
**Datum:** 2025-10-19  
**Status:** ✅ Produktionsbereit

