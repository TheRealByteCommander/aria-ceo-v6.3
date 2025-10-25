# Aria CEO v6.1 - Quick Reference Guide

## Installation (3 Steps)

```bash
# 1. Copy to server
scp aria_bugfix_v7.tar.gz aria-system@192.168.178.150:~

# 2. Extract and enter directory
ssh aria-system@192.168.178.150
tar -xzf aria_bugfix_v7.tar.gz && cd aria_bugfix_v7

# 3. Run installation script
./apply_bugfix.sh
```

---

## What Was Fixed

| Bug | Status | Description |
|-----|--------|-------------|
| Endless clarification loop | ✅ FIXED | Clarification questions completely disabled |
| Missing dashboard broadcasts | ✅ FIXED | Real-time WebSocket updates enabled |

---

## Testing Commands

### Check Service Status
```bash
sudo systemctl status aria-ceo.service
```

### View Live Logs
```bash
sudo journalctl -u aria-ceo.service -f
```

### Test in Slack
```
@Aria Erstelle eine einfache Hello World API mit FastAPI und SQLite
```

### Check Dashboard
```
http://192.168.178.152:8090
```

### Test WebSocket Connection
```bash
curl -i -N -H "Connection: Upgrade" -H "Upgrade: websocket" \
     -H "Sec-WebSocket-Version: 13" -H "Sec-WebSocket-Key: test" \
     http://192.168.178.152:8090/ws
```

---

## Rollback (If Needed)

```bash
# Find latest backup
BACKUP_DIR=$(ls -t /opt/aria-system/backups/ | head -1)

# Restore
sudo systemctl stop aria-ceo.service
sudo cp /opt/aria-system/backups/$BACKUP_DIR/aria_ceo.py.backup \
       /opt/aria-system/agents/aria_ceo.py
sudo systemctl start aria-ceo.service
```

---

## Troubleshooting

### Service Won't Start

```bash
# Check logs
sudo journalctl -u aria-ceo.service -n 100 --no-pager

# Check Python syntax
sudo -u aria-system /opt/aria-system/venv/bin/python -m py_compile \
     /opt/aria-system/agents/aria_ceo.py

# Check dependencies
sudo -u aria-system /opt/aria-system/venv/bin/pip list | grep websockets
```

### Dashboard Not Showing Messages

```bash
# Check config
grep -A 2 "dashboard:" /opt/aria-system/config/config.yaml

# Check dashboard service
sudo systemctl status aria-dashboard.service

# Check WebSocket logs
sudo journalctl -u aria-ceo.service | grep -i websocket
```

### Clarifications Still Appearing

```bash
# Verify correct version
grep "BUGFIX #1" /opt/aria-system/agents/aria_ceo.py

# Force restart
sudo systemctl stop aria-ceo.service
sleep 5
sudo systemctl start aria-ceo.service
```

---

## Key Files

| File | Location | Purpose |
|------|----------|---------|
| Main agent | `/opt/aria-system/agents/aria_ceo.py` | Fixed version |
| Configuration | `/opt/aria-system/config/config.yaml` | System config |
| Service | `/etc/systemd/system/aria-ceo.service` | Systemd service |
| Backups | `/opt/aria-system/backups/` | Automatic backups |
| Logs | `journalctl -u aria-ceo.service` | Service logs |

---

## Configuration

Add to `/opt/aria-system/config/config.yaml`:

```yaml
dashboard:
  websocket_url: "ws://192.168.178.152:8090/ws"
```

---

## Expected Behavior

### Before Fix
- ❌ Endless clarification questions
- ❌ Dashboard shows nothing
- ❌ Projects get stuck

### After Fix
- ✅ Projects start immediately
- ✅ Dashboard shows real-time chat
- ✅ Projects complete successfully

---

## Support Checklist

- [ ] Service is running: `sudo systemctl status aria-ceo.service`
- [ ] No errors in logs: `sudo journalctl -u aria-ceo.service -n 50`
- [ ] Dashboard is accessible: `http://192.168.178.152:8090`
- [ ] WebSocket connects: Check browser console (F12)
- [ ] Slack bot responds: `@Aria hello`
- [ ] LLM servers online: Check dashboard "LLM Status"

---

## Version Info

```
Aria CEO: 6.1-bugfix-edition
Date: 2025-10-19
Python: 3.10+
Autogen: 0.4.x
WebSockets: 12.0+
```

---

## Quick Test Sequence

```bash
# 1. Check service
sudo systemctl status aria-ceo.service

# 2. Watch logs
sudo journalctl -u aria-ceo.service -f &

# 3. Open dashboard
firefox http://192.168.178.152:8090 &

# 4. Test in Slack
# Send: @Aria Erstelle eine einfache Hello World API

# 5. Verify:
# - No clarification questions in Slack
# - Messages appear in dashboard
# - Project completes successfully
```

---

## Emergency Contacts

- **Logs:** `sudo journalctl -u aria-ceo.service -f`
- **Status:** `sudo systemctl status aria-ceo.service`
- **Restart:** `sudo systemctl restart aria-ceo.service`
- **Rollback:** See "Rollback" section above

---

## Success Indicators

✅ Service shows "active (running)"  
✅ No error messages in logs  
✅ Slack bot responds to @mentions  
✅ Dashboard shows live chat messages  
✅ Projects complete without clarification loops  
✅ All 8 workers participate in projects  
✅ GitHub/Docker Hub integrations work  

---

## Common Issues

| Issue | Solution |
|-------|----------|
| Service failed | Check logs: `journalctl -u aria-ceo.service -n 100` |
| Dashboard empty | Verify WebSocket URL in config.yaml |
| Still asking questions | Verify correct file: `grep BUGFIX /opt/aria-system/agents/aria_ceo.py` |
| WebSocket errors | Check dashboard service is running |

---

## Next Steps After Installation

1. ✅ Test with simple project in Slack
2. ✅ Verify dashboard shows messages
3. ✅ Check GitHub integration works
4. ✅ Check Docker Hub integration works
5. ✅ Monitor for 24 hours
6. ✅ Document any issues

---

## Backup Information

Backups are automatically created in:
```
/opt/aria-system/backups/YYYYMMDD-HHMMSS/
```

Each backup contains:
- `aria_ceo.py.backup` - Previous version of the main agent file

Backups are kept indefinitely. Clean up manually if needed:
```bash
# List backups
ls -lh /opt/aria-system/backups/

# Remove old backups (keep last 5)
cd /opt/aria-system/backups/
ls -t | tail -n +6 | xargs -I {} sudo rm -rf {}
```

