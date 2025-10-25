# Troubleshooting - Aria CEO v6.3 (Optimized Edition)

This document contains solutions to common issues encountered during and after the installation of the Aria CEO system.

---

## 🐛 Troubleshooting

### Issue 1: Service Failed to Start

**Symptoms:**
```bash
sudo systemctl status aria-ceo.service
# Shows: failed (Result: exit-code)
```

**Solution:**

1. Check logs for errors:
   ```bash
   sudo journalctl -u aria-ceo.service -n 100 --no-pager
   ```

2. Check Python syntax:
   ```bash
   sudo -u aria-system /opt/aria-system/venv/bin/python -m py_compile /opt/aria-system/agents/aria_ceo.py
   ```

3. If syntax error, restore backup:
   ```bash
   BACKUP_DIR=$(ls -t /opt/aria-system/backups/ | head -1)
   sudo cp /opt/aria-system/backups/$BACKUP_DIR/aria_ceo.py.backup \
          /opt/aria-system/agents/aria_ceo.py
   sudo systemctl restart aria-ceo.service
   ```

### Issue 2: Dashboard Not Showing Messages

**Symptoms:**
- Service runs fine
- Projects complete
- Dashboard remains empty

**Solution:**

1. Check WebSocket URL in config:
   ```bash
   grep -A 2 "dashboard:" /opt/aria-system/config/config.yaml
   ```
   Should show:
   ```yaml
   dashboard:
     websocket_url: "ws://192.168.178.150:8090/ws"
   ```

2. Check dashboard service:
   ```bash
   sudo systemctl status aria-dashboard.service
   ```

3. Test WebSocket connection:
   ```bash
   curl -i -N -H "Connection: Upgrade" -H "Upgrade: websocket" \
        -H "Sec-WebSocket-Version: 13" -H "Sec-WebSocket-Key: test" \
        http://192.168.178.150:8090/ws
   ```

4. Check for WebSocket errors in logs:
   ```bash
   sudo journalctl -u aria-ceo.service | grep -i websocket
   ```

### Issue 3: Still Asking Clarification Questions

**Symptoms:**
- Aria still asks clarification questions
- Old behavior persists

**Solution:**

1. Verify correct file is installed:
   ```bash
   grep "BUGFIX #1" /opt/aria-system/agents/aria_ceo.py
   ```
   Should show the bugfix comment.

2. Check version:
   ```bash
   grep "version = " /opt/aria-system/agents/aria_ceo.py
   ```
   Should show "6.3-optimized-edition"

3. Force restart:
   ```bash
   sudo systemctl stop aria-ceo.service
   sleep 5
   sudo systemctl start aria-ceo.service
   ```

4. Check for old processes:
   ```bash
   ps aux | grep aria
   # Kill any old processes
   sudo pkill -f aria_ceo
   sudo systemctl start aria-ceo.service
   ```

### Issue 4: Import Error (websockets)

**Symptoms:**
```
ModuleNotFoundError: No module named 'websockets'
```

**Solution:**

```bash
sudo -u aria-system /opt/aria-system/venv/bin/pip install websockets
sudo systemctl restart aria-ceo.service
```

### Issue 5: Permission Denied

**Symptoms:**
```
Permission denied: '/opt/aria-system/agents/aria_ceo.py'
```

**Solution:**

```bash
sudo chown aria-system:aria-system /opt/aria-system/agents/aria_ceo.py
sudo chmod 644 /opt/aria-system/agents/aria_ceo.py
sudo systemctl restart aria-ceo.service
```

---

## 🔄 Rollback Procedure

If you need to revert to the previous version:

### Quick Rollback

```bash
# Find latest backup
BACKUP_DIR=$(ls -t /opt/aria-system/backups/ | head -1)
echo "Restoring from: $BACKUP_DIR"

# Stop service
sudo systemctl stop aria-ceo.service

# Restore backup
sudo cp /opt/aria-system/backups/$BACKUP_DIR/aria_ceo.py.backup \
       /opt/aria-system/agents/aria_ceo.py

# Start service
sudo systemctl start aria-ceo.service

# Verify
sudo systemctl status aria-ceo.service
```
