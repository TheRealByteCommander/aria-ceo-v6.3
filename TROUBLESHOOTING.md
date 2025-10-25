# Aria CEO v6.3 - Troubleshooting Guide

Lösungen für häufige Probleme

---

## 🔍 Diagnose-Tools

### Service-Status prüfen

```bash
systemctl status aria-ceo.service
```

**Gesund:**
```
Active: active (running)
Main PID: 12345 (python3)
```

**Problematisch:**
```
Active: failed
Active: activating (auto-restart)
```

### Logs anschauen

```bash
# Letzte 50 Zeilen
journalctl -u aria-ceo.service -n 50 --no-pager

# Live-Logs
journalctl -u aria-ceo.service -f

# Seit bestimmter Zeit
journalctl -u aria-ceo.service --since "10 minutes ago"

# Nach Fehler suchen
journalctl -u aria-ceo.service | grep -i error
```

### Konfiguration prüfen

```bash
# Config anzeigen
cat /opt/aria-system/config/config.yaml

# Dashboard-Config
grep -A 3 "dashboard:" /opt/aria-system/config/config.yaml

# LLM-Server-Config
grep -A 10 "llm_servers:" /opt/aria-system/config/config.yaml
```

---

## ❌ Problem: Service startet nicht

### Symptom

```bash
$ systemctl status aria-ceo.service
Active: failed (Result: exit-code)
Main PID: 12345 (code=exited, status=1/FAILURE)
```

### Diagnose

```bash
# Fehler in Logs finden
journalctl -u aria-ceo.service -n 30 --no-pager
```

### Häufige Ursachen

#### 1. Python Syntax-Fehler

**Log:**
```
SyntaxError: invalid syntax
  File "/opt/aria-system/agents/aria_ceo.py", line 28
```

**Lösung:**
```bash
# Datei neu installieren
cd ~/aria_v6.3_FINAL
cp aria_ceo_fixed.py /opt/aria-system/agents/aria_ceo.py
systemctl restart aria-ceo.service
```

#### 2. Import-Fehler

**Log:**
```
ModuleNotFoundError: No module named 'websockets'
ImportError: cannot import name 'AriaCEO'
```

**Lösung:**
```bash
# Dependency installieren
/opt/aria-system/venv/bin/pip install websockets

# Oder komplett neu installieren
cd ~/aria_v6.3_FINAL
./install_aria_v6.3.sh
```

#### 3. Permission-Fehler

**Log:**
```
PermissionError: [Errno 13] Permission denied: '/opt/aria-system/...'
```

**Lösung:**
```bash
# Ownership korrigieren
chown -R aria-system:aria-system /opt/aria-system
chmod 755 /opt/aria-system/agents
chmod 644 /opt/aria-system/agents/aria_ceo.py
```

#### 4. NameError: 'client' not defined

**Log:**
```
NameError: name 'client' is not defined
  File "/opt/aria-system/integrations/slack_bot_v6.py", line 28
```

**Lösung:**
```bash
# Slack bot fixen
sed -i 's/AriaCEO(slack_client=client)/AriaCEO(slack_client=self.app.client)/' \
   /opt/aria-system/integrations/slack_bot_v6.py
systemctl restart aria-ceo.service
```

---

## ❌ Problem: Dashboard zeigt nichts

### Symptom

- Dashboard-Webseite lädt
- Aber keine Live-Updates
- Keine Chat-Nachrichten

### Diagnose

```bash
# 1. Dashboard erreichbar?
curl http://192.168.178.150:8090

# 2. WebSocket-Verbindung in Logs?
journalctl -u aria-ceo.service | grep -i "dashboard"
```

### Häufige Ursachen

#### 1. Dashboard läuft nicht

**Log:**
```
Could not connect to dashboard: [Errno 111] Connection refused
```

**Lösung:**
```bash
# Dashboard-Service starten (auf CT150)
systemctl start aria-dashboard.service

# Oder Dashboard manuell starten
cd /opt/aria-dashboard
python3 dashboard.py
```

#### 2. Falsche Dashboard-IP

**Log:**
```
Could not connect to dashboard: [Errno 111] Connect call failed ('192.168.178.152', 8090)
```

**Lösung:**
```bash
# IP in Config korrigieren
sed -i 's/192\.168\.178\.152:8090/192.168.178.150:8090/g' \
   /opt/aria-system/config/config.yaml

# Service neu starten
systemctl restart aria-ceo.service
```

#### 3. WebSocket-Port blockiert

**Diagnose:**
```bash
# Port 8090 prüfen
ss -tlnp | grep 8090
netstat -tlnp | grep 8090
```

**Lösung:**
```bash
# Firewall-Regel hinzufügen
ufw allow 8090/tcp

# Oder Firewall temporär deaktivieren (zum Testen)
ufw disable
```

---

## ❌ Problem: Keine Slack Updates

### Symptom

- Nur "Starting project..." Nachricht
- Keine weiteren Updates
- Projekt läuft aber (sichtbar in Logs)

### Diagnose

```bash
# Nach Slack-Updates suchen
journalctl -u aria-ceo.service | grep -i "slack update"

# Nach RuntimeWarning suchen
journalctl -u aria-ceo.service | grep -i "runtimewarning"
```

### Häufige Ursachen

#### 1. RuntimeWarning: coroutine not awaited

**Log:**
```
RuntimeWarning: coroutine 'AsyncWebClient.chat_postMessage' was never awaited
```

**Lösung:**
```bash
# aria_ceo.py Zeile ~571 prüfen
grep -A 5 "_send_slack_update" /opt/aria-system/agents/aria_ceo.py

# Sollte sein:
# await self.slack_client.chat_postMessage(...)

# Wenn nicht, neu installieren:
cd ~/aria_v6.3_FINAL
cp aria_ceo_fixed.py /opt/aria-system/agents/aria_ceo.py
systemctl restart aria-ceo.service
```

#### 2. Slack Client nicht übergeben

**Log:**
```
DEBUG | Slack client or channel not available for updates
```

**Lösung:**
```bash
# Slack bot prüfen
grep "AriaCEO" /opt/aria-system/integrations/slack_bot_v6.py

# Sollte sein:
# self.aria_ceo = AriaCEO(slack_client=self.app.client)

# Wenn nicht:
sed -i 's/AriaCEO()/AriaCEO(slack_client=self.app.client)/' \
   /opt/aria-system/integrations/slack_bot_v6.py
systemctl restart aria-ceo.service
```

#### 3. Channel nicht gespeichert

**Diagnose:**
```bash
# Code prüfen
grep "self.current_channel" /opt/aria-system/agents/aria_ceo.py
```

**Lösung:**
```bash
# Sollte in handle_project() gesetzt werden:
# self.current_channel = channel

# Wenn nicht, neu installieren:
cd ~/aria_v6.3_FINAL
./install_aria_v6.3.sh
```

---

## ❌ Problem: LLM Server nicht erreichbar

### Symptom

**Log:**
```
WARNING | LLM server offline: Mac Mini (192.168.178.159)
ERROR | Could not connect to LLM server
```

### Diagnose

```bash
# LLM Server direkt testen
curl http://192.168.178.159:11434/api/tags
curl http://192.168.178.155:11434/api/tags
```

### Lösung

```bash
# Auf Mac Mini / GMKtec
systemctl status ollama.service
systemctl start ollama.service

# Oder Ollama manuell starten
ollama serve
```

---

## ❌ Problem: GitHub Integration funktioniert nicht

### Symptom

**Log:**
```
ERROR | GitHub push failed
WARNING | GitHub integration disabled
```

### Diagnose

```bash
# GitHub-Token prüfen
grep "GITHUB_TOKEN" /opt/aria-system/.env

# Git-Config prüfen
git config --global user.name
git config --global user.email
```

### Lösung

```bash
# Token setzen
echo "GITHUB_TOKEN=ghp_..." >> /opt/aria-system/.env

# Git-Config setzen
git config --global user.name "Aria CEO"
git config --global user.email "aria@example.com"

# Service neu starten
systemctl restart aria-ceo.service
```

---

## ❌ Problem: Docker Hub Integration funktioniert nicht

### Symptom

**Log:**
```
ERROR | Docker login failed
WARNING | Docker Hub integration disabled
```

### Diagnose

```bash
# Docker läuft?
systemctl status docker

# Docker Hub Login?
docker info | grep Username
```

### Lösung

```bash
# Docker starten
systemctl start docker

# Docker Hub Login
docker login -u USERNAME -p PASSWORD

# Service neu starten
systemctl restart aria-ceo.service
```

---

## ❌ Problem: Clarification Loop (sollte nicht mehr vorkommen)

### Symptom

- Aria fragt endlos nach Klarstellungen
- Projekt startet nie

### Diagnose

```bash
# Prüfe ob v6.3 installiert ist
grep "6.3-final" /opt/aria-system/agents/aria_ceo.py

# Prüfe _needs_clarification Methode
grep -A 5 "_needs_clarification" /opt/aria-system/agents/aria_ceo.py
```

### Lösung

```bash
# v6.3 neu installieren
cd ~/aria_v6.3_FINAL
./install_aria_v6.3.sh

# Verifizieren
journalctl -u aria-ceo.service -n 20 | grep "Clarification"
# Sollte zeigen: "❌ Clarification Questions (DISABLED)"
```

---

## 🔄 Rollback

### Zu letztem Backup

```bash
# 1. Letztes Backup finden
BACKUP_DIR=$(ls -t /opt/aria-system/backups/ | head -1)
echo "Rolling back to: $BACKUP_DIR"

# 2. Service stoppen
systemctl stop aria-ceo.service

# 3. Dateien wiederherstellen
cp /opt/aria-system/backups/$BACKUP_DIR/aria_ceo.py.backup \
   /opt/aria-system/agents/aria_ceo.py
cp /opt/aria-system/backups/$BACKUP_DIR/slack_bot_v6.py.backup \
   /opt/aria-system/integrations/slack_bot_v6.py
cp /opt/aria-system/backups/$BACKUP_DIR/config.yaml.backup \
   /opt/aria-system/config/config.yaml

# 4. Service starten
systemctl start aria-ceo.service

# 5. Verifizieren
systemctl status aria-ceo.service
```

### Zu v6.0 (Original)

```bash
# Nur wenn vollständiges Backup existiert
cp -r /opt/aria-system.backup.v6.0/* /opt/aria-system/
systemctl restart aria-ceo.service
```

---

## 🧪 Testing Checklist

Nach jeder Änderung:

### 1. Service läuft

```bash
systemctl status aria-ceo.service
# Erwartung: active (running)
```

### 2. Keine Fehler in Logs

```bash
journalctl -u aria-ceo.service -n 30 | grep -i error
# Erwartung: Keine kritischen Fehler
```

### 3. Dashboard verbindet

```bash
journalctl -u aria-ceo.service | grep -i "dashboard"
# Erwartung: "Connected to dashboard WebSocket"
# NICHT: "Could not connect to dashboard"
```

### 4. Slack funktioniert

**In Slack:**
```
@Aria hello
```

**Erwartung:**
- 🚀 Starting project...
- 👷 Team is working...
- 💬 Progress Update...
- ✅ Team Discussion Complete...
- 🎉 Project Complete!

### 5. Dashboard zeigt Updates

**Browser:** http://192.168.178.150:8090

**Erwartung:**
- Live Chat-Nachrichten
- Agent-Namen sichtbar
- Timestamps aktualisieren

---

## 📞 Support

### Logs sammeln

```bash
# Alle relevanten Logs
journalctl -u aria-ceo.service -n 200 > aria_logs.txt
systemctl status aria-ceo.service > aria_status.txt
cat /opt/aria-system/config/config.yaml > aria_config.txt

# Als Archiv
tar -czf aria_debug_$(date +%Y%m%d-%H%M%S).tar.gz \
    aria_logs.txt aria_status.txt aria_config.txt
```

### System-Info

```bash
# System
uname -a
cat /etc/os-release

# Python
python3 --version
/opt/aria-system/venv/bin/python3 --version

# Packages
/opt/aria-system/venv/bin/pip list

# Services
systemctl list-units --type=service | grep -E "aria|ollama|docker"
```

### Häufige Fragen

**Q: Wie lange dauert ein Projekt?**  
A: 1-5 Minuten, abhängig von Komplexität

**Q: Kann ich mehrere Projekte parallel laufen lassen?**  
A: Nein, aktuell nur sequentiell

**Q: Wo werden Projekte gespeichert?**  
A: `/opt/aria-system/projects/project-YYYYMMDD-HHMMSS/`

**Q: Wie kann ich ein Projekt abbrechen?**  
A: `systemctl restart aria-ceo.service` (stoppt aktuelles Projekt)

**Q: Werden alte Projekte gelöscht?**  
A: Nein, bleiben in `/opt/aria-system/projects/`

---

**Last Updated:** 2025-10-19  
**Version:** 6.3-final  
**Status:** ✅ Aktuell

