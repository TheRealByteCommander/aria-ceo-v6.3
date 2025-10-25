# Aria System - Korrekte IP-Adressen

**Version:** 6.1-bugfix-edition  
**Datum:** 2025-10-19  
**Status:** ✅ Korrigiert

---

## 🌐 Netzwerk-Übersicht

### Korrekte IP-Adressen

| System | IP-Adresse | Funktion | Port |
|--------|------------|----------|------|
| **CT150** | 192.168.178.150 | CEO System (Aria + Agents) | - |
| **CT151** | 192.168.178.151 | Data Services (MongoDB, Redis, ChromaDB) | - |
| **CT152** | 192.168.178.152 | Dashboard & Monitoring | 8090 |
| **Mac Mini** | 192.168.178.159 | Ollama LLM Server | 11434 |
| **GMKtec** | 192.168.178.155 | Ollama LLM Server | 11434 |

---

## 📍 Detaillierte Zuordnung

### CT150 - CEO System
**IP:** 192.168.178.150  
**Hostname:** aria-ceo oder ct150  
**Funktion:**
- Aria CEO Agent
- 8 Worker Agents (Riley, Sam, Jordan, Taylor, Morgan, Alex, Casey + optional Audio)
- Slack Bot Integration
- GitHub Integration
- Docker Hub Integration
- Code File Generator

**Services:**
- aria-ceo.service (systemd)
- Slack Socket Mode Connection

**Verzeichnisse:**
- `/opt/aria-system/` - Hauptverzeichnis
- `/opt/aria-system/agents/` - Agent Code
- `/opt/aria-system/config/` - Konfiguration
- `/opt/aria-system/projects/` - Generierte Projekte
- `/opt/aria-system/backups/` - Automatische Backups

---

### CT151 - Data Services
**IP:** 192.168.178.151  
**Hostname:** data-services oder ct151  
**Funktion:**
- MongoDB (Projektdaten, Logs)
- Redis (Caching, Session Management)
- ChromaDB (Vector Database für RAG)

**Ports:**
- MongoDB: 27017
- Redis: 6379
- ChromaDB: 8000

---

### CT152 - Dashboard & Monitoring
**IP:** 192.168.178.152  
**Hostname:** dashboard oder ct152  
**Funktion:**
- Real-time WebSocket Dashboard
- LLM Monitoring
- System Metrics
- Project Tracking

**Ports:**
- Dashboard: 8090 (HTTP + WebSocket)
- WebSocket: ws://192.168.178.152:8090/ws

**URL:**
- Dashboard: http://192.168.178.152:8090

---

### Mac Mini - LLM Server
**IP:** 192.168.178.159  
**Hostname:** mac-mini  
**Funktion:**
- Ollama LLM Server
- Hauptsächlich für Aria (CEO) und Riley (Research)

**Modelle:**
- llama3.1:8b (für Aria CEO)
- llama3.1:8b (für Riley Research)

**Port:**
- Ollama API: 11434
- OpenAI-kompatible API: http://192.168.178.159:11434/v1

**Hardware:**
- 16GB RAM
- Apple Silicon M1/M2

---

### GMKtec - LLM Server
**IP:** 192.168.178.155  
**Hostname:** gmktec  
**Funktion:**
- Ollama LLM Server
- Hauptsächlich für Worker Agents (Sam, Jordan, etc.)

**Modelle:**
- llama3.2:3b (für Worker Agents)
- qwen2.5-coder:32b (für Sam Backend Developer)
- Weitere spezialisierte Modelle

**Port:**
- Ollama API: 11434
- OpenAI-kompatible API: http://192.168.178.155:11434/v1

**Hardware:**
- 32GB RAM (oder mehr)
- Dedizierte GPU

---

## 🔧 Konfiguration

### config.yaml (auf CT150)

```yaml
# LLM Configuration
llm:
  mac_mini:
    host: "192.168.178.159"
    port: 11434
    models:
      aria: "llama3.1:8b"
      riley: "llama3.1:8b"
  
  gmktec:
    host: "192.168.178.155"
    port: 11434
    models:
      sam: "qwen2.5-coder:32b"
      jordan: "llama3.2:3b"
      taylor: "llama3.2:3b"
      morgan: "llama3.2:3b"
      alex: "llama3.2:3b"
      casey: "llama3.2:3b"

# Dashboard Configuration
dashboard:
  websocket_url: "ws://192.168.178.152:8090/ws"
  http_url: "http://192.168.178.152:8090"

# Data Services Configuration
database:
  mongodb:
    host: "192.168.178.151"
    port: 27017
    database: "aria_system"
  
  redis:
    host: "192.168.178.151"
    port: 6379
  
  chromadb:
    host: "192.168.178.151"
    port: 8000

# GitHub Integration
github:
  enabled: true
  token: "${GITHUB_TOKEN}"
  organization: "your-org"

# Docker Hub Integration
docker_hub:
  enabled: true
  username: "${DOCKERHUB_USERNAME}"
  password: "${DOCKERHUB_PASSWORD}"
```

---

## 🚀 Deployment

### SSH Zugriff

```bash
# CT150 - CEO System
ssh aria-system@192.168.178.150

# CT151 - Data Services
ssh root@192.168.178.151

# CT152 - Dashboard
ssh root@192.168.178.152
```

### SCP Dateitransfer

```bash
# Zum CEO System (CT150)
scp file.tar.gz aria-system@192.168.178.150:~

# Zum Dashboard (CT152)
scp file.tar.gz root@192.168.178.152:~
```

---

## 🧪 Testing

### LLM Server Tests

```bash
# Mac Mini
curl http://192.168.178.159:11434/api/tags

# GMKtec
curl http://192.168.178.155:11434/api/tags
```

### Dashboard Test

```bash
# HTTP
curl http://192.168.178.152:8090

# WebSocket (mit wscat)
wscat -c ws://192.168.178.152:8090/ws
```

### Data Services Tests

```bash
# MongoDB
mongosh mongodb://192.168.178.151:27017

# Redis
redis-cli -h 192.168.178.151 -p 6379 ping

# ChromaDB
curl http://192.168.178.151:8000/api/v1/heartbeat
```

---

## 📊 Worker Agents & LLM Zuordnung

### Aria (CEO)
- **LLM:** Mac Mini (192.168.178.159)
- **Modell:** llama3.1:8b
- **Funktion:** Projektkoordination, Teamleitung

### Riley (Communication/Research)
- **LLM:** Mac Mini (192.168.178.159)
- **Modell:** llama3.1:8b
- **Funktion:** Slack-Kommunikation, Research, Best Practices

### Sam (Backend Developer)
- **LLM:** GMKtec (192.168.178.155)
- **Modell:** qwen2.5-coder:32b
- **Funktion:** Backend-Entwicklung (Python, Node.js, APIs)

### Jordan (Frontend Developer)
- **LLM:** GMKtec (192.168.178.155)
- **Modell:** llama3.2:3b
- **Funktion:** Frontend-Entwicklung (React, Vue, Next.js)

### Taylor (QA Engineer)
- **LLM:** GMKtec (192.168.178.155)
- **Modell:** llama3.2:3b
- **Funktion:** Testing, Quality Assurance

### Morgan (DevOps Engineer)
- **LLM:** GMKtec (192.168.178.155)
- **Modell:** llama3.2:3b
- **Funktion:** Docker, CI/CD, Deployment

### Alex (Project Manager)
- **LLM:** GMKtec (192.168.178.155)
- **Modell:** llama3.2:3b
- **Funktion:** Dokumentation, README, Technical Writing

### Casey (Audio/Video Specialist)
- **LLM:** GMKtec (192.168.178.155)
- **Modell:** llama3.2:3b
- **Funktion:** Audio/Video Processing (optional)

---

## ✅ Features

### Alle Features auf CT150

- ✅ **8 Worker Agents** - Aria, Riley, Sam, Jordan, Taylor, Morgan, Alex, Casey
- ✅ **Free Worker Communication** - Agents können direkt miteinander sprechen
- ✅ **GitHub Integration** - Automatisches Pushen von Projekten
- ✅ **Docker Hub Integration** - Automatisches Bauen und Pushen von Images
- ✅ **LLM Monitoring** - Überwachung von Mac Mini + GMKtec
- ✅ **Slack Integration** - @mentions, DMs, Slash Commands
- ✅ **Dashboard Broadcasts** - Real-time WebSocket Updates
- ✅ **Code Extraction** - Automatische Datei-Generierung
- ✅ **Project Management** - Vollständiger Workflow
- ❌ **Clarification Questions** - DEAKTIVIERT (Bugfix)

---

## 🔄 Netzwerk-Fluss

```
Slack User
    ↓
CT150 (Aria CEO)
    ↓
    ├─→ Mac Mini (192.168.178.159) - Aria & Riley LLMs
    ├─→ GMKtec (192.168.178.155) - Worker LLMs
    ├─→ CT151 (192.168.178.151) - Data Services
    └─→ CT152 (192.168.178.152) - Dashboard WebSocket
```

---

## 📝 Wichtige Hinweise

### Bugfix v6.1

1. **Dashboard WebSocket URL:** `ws://192.168.178.152:8090/ws`
2. **CEO System:** Läuft auf CT150 (192.168.178.150)
3. **Clarification Questions:** Komplett deaktiviert
4. **Dashboard Broadcasts:** Vollständig implementiert

### Deployment-Ziel

- **Haupt-System:** CT150 (192.168.178.150)
- **User:** aria-system
- **Verzeichnis:** /opt/aria-system

### Backup-Speicherort

- **Pfad:** /opt/aria-system/backups/
- **Format:** YYYYMMDD-HHMMSS/
- **Inhalt:** aria_ceo.py.backup

---

## 🎯 Zusammenfassung

| Komponente | IP | Port | Funktion |
|------------|----|----- |----------|
| CEO System | 192.168.178.150 | - | Aria + 8 Workers |
| Data Services | 192.168.178.151 | 27017, 6379, 8000 | MongoDB, Redis, ChromaDB |
| Dashboard | 192.168.178.152 | 8090 | WebSocket Dashboard |
| Mac Mini LLM | 192.168.178.159 | 11434 | Aria & Riley |
| GMKtec LLM | 192.168.178.155 | 11434 | Sam, Jordan, Taylor, Morgan, Alex, Casey |

---

**Status:** ✅ Alle IP-Adressen korrigiert  
**Version:** 6.1-bugfix-edition  
**Datum:** 2025-10-19

