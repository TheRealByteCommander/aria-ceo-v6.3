# Aria CEO v6.1 - Complete Installation Guide

**Version:** 6.1-bugfix-edition  
**Target System:** VM at 192.168.178.150 (CT150 or VM1)  
**Estimated Time:** 5 minutes  
**Difficulty:** Easy (automated script)

---

## 📋 Pre-Installation Checklist

Before starting, verify these conditions:

### System Status
```bash
# Check if Aria system exists
ssh aria-system@192.168.178.150 "ls -la /opt/aria-system"
```
✅ Should show the aria-system directory

### Service Status
```bash
# Check if service is running
ssh aria-system@192.168.178.150 "sudo systemctl status aria-ceo.service"
```
✅ Should show "active (running)" or "active (failed)"

### Dashboard Status
```bash
# Check if dashboard is accessible
curl -I http://192.168.178.152:8090
```
✅ Should return HTTP 200 OK

### Network Access
```bash
# Verify you can SSH to the server
ssh aria-system@192.168.178.150 "hostname"
```
✅ Should show the hostname

---

## 🚀 Installation Steps

### Step 1: Download the Package

If you're reading this, you already have the package! The file is:
```
aria_bugfix_v7.tar.gz
```

### Step 2: Copy to Server

From your local machine (Windows PowerShell, Mac Terminal, or Linux):

```bash
scp aria_bugfix_v7.tar.gz aria-system@192.168.178.150:~
```

**Expected output:**
```
aria_bugfix_v7.tar.gz                100%   15KB   1.5MB/s   00:00
```

### Step 3: Connect to Server

```bash
ssh aria-system@192.168.178.150
```

You should now be logged into the server.

### Step 4: Extract the Package

```bash
tar -xzf aria_bugfix_v7.tar.gz
cd aria_bugfix_v7
```

**Verify extraction:**
```bash
ls -la
```

**Expected output:**
```
total XX
drwxrwxr-x 2 aria-system aria-system 4096 Oct 19 10:30 .
drwxr-xr-x 8 aria-system aria-system 4096 Oct 19 10:30 ..
-rw-rw-r-- 1 aria-system aria-system XXXX Oct 19 10:30 aria_ceo_fixed.py
-rwxrwxr-x 1 aria-system aria-system XXXX Oct 19 10:30 apply_bugfix.sh
-rw-rw-r-- 1 aria-system aria-system XXXX Oct 19 10:30 BUGFIX_DOCUMENTATION.md
-rw-rw-r-- 1 aria-system aria-system XXXX Oct 19 10:30 QUICK_REFERENCE.md
-rw-rw-r-- 1 aria-system aria-system XXXX Oct 19 10:30 README.md
```

### Step 5: Run Installation Script

```bash
./apply_bugfix.sh
```

**What the script does:**

1. ✅ Verifies system directory exists
2. ✅ Creates automatic backup
3. ✅ Stops aria-ceo service
4. ✅ Installs fixed aria_ceo.py
5. ✅ Installs websockets dependency
6. ✅ Updates configuration
7. ✅ Starts aria-ceo service
8. ✅ Verifies service is running
9. ✅ Shows recent logs

**Expected output:**
```
==========================================
Aria CEO v6.1 - Bugfix Installation
==========================================

✓ System directory found

Creating backup in: /opt/aria-system/backups/20251019-103000
Backing up current aria_ceo.py...
✓ Backup created

Stopping aria-ceo service...
✓ Service stopped

Installing fixed aria_ceo.py...
✓ Fixed file installed

Checking Python dependencies...
✓ websockets already installed

Checking configuration...
✓ Dashboard config already present

Starting aria-ceo service...
✓ Service is running

Recent logs:
----------------------------------------
Oct 19 10:30:15 vm1 systemd[1]: Started Aria Virtual CEO System.
Oct 19 10:30:16 vm1 python[12345]: Initializing Aria CEO - Version 6.1-bugfix-edition
Oct 19 10:30:16 vm1 python[12345]: ✨ Features enabled:
Oct 19 10:30:16 vm1 python[12345]:   ✅ GitHub Integration
Oct 19 10:30:16 vm1 python[12345]:   ✅ Docker Hub Integration
Oct 19 10:30:16 vm1 python[12345]:   ✅ Free Worker Communication
Oct 19 10:30:16 vm1 python[12345]:   ✅ LLM Monitoring
Oct 19 10:30:16 vm1 python[12345]:   ✅ Dashboard Broadcasts
Oct 19 10:30:16 vm1 python[12345]:   ❌ Clarification Questions (DISABLED)
Oct 19 10:30:17 vm1 python[12345]: Aria CEO v6.1 (Bugfix Edition) ready!
----------------------------------------

==========================================
Bugfix Installation Complete!
==========================================

Changes applied:
  ✅ Clarification questions: DISABLED
  ✅ Dashboard broadcasts: ENABLED

Backup location: /opt/aria-system/backups/20251019-103000

Next steps:
  1. Test in Slack: @Aria Erstelle eine einfache Hello World API
  2. Check dashboard: http://192.168.178.152:8090
  3. Monitor logs: sudo journalctl -u aria-ceo.service -f
```

---

## ✅ Post-Installation Verification

### Verify 1: Service Status

```bash
sudo systemctl status aria-ceo.service
```

**Expected:**
```
● aria-ceo.service - Aria Virtual CEO System
   Loaded: loaded (/etc/systemd/system/aria-ceo.service; enabled; vendor preset: enabled)
   Active: active (running) since Sat 2025-10-19 10:30:15 CEST; 2min ago
```

✅ Status should be "active (running)"

### Verify 2: Check Logs

```bash
sudo journalctl -u aria-ceo.service -n 50 --no-pager
```

**Look for:**
- ✅ "Initializing Aria CEO - Version 6.1-bugfix-edition"
- ✅ "✅ Dashboard Broadcasts"
- ✅ "❌ Clarification Questions (DISABLED)"
- ✅ "Aria CEO v6.1 (Bugfix Edition) ready!"
- ❌ No error messages

### Verify 3: Check Version

```bash
grep "version = " /opt/aria-system/agents/aria_ceo.py
```

**Expected:**
```python
self.version = "6.1-bugfix-edition"
```

### Verify 4: Check Bugfix Markers

```bash
grep "BUGFIX" /opt/aria-system/agents/aria_ceo.py
```

**Expected:**
```python
BUGFIX #1: Completely disabled clarification questions
BUGFIX #2: Broadcast events to dashboard via WebSocket
BUGFIX #2: Now broadcasts all chat messages to the dashboard
```

### Verify 5: Check Configuration

```bash
grep -A 2 "dashboard:" /opt/aria-system/config/config.yaml
```

**Expected:**
```yaml
dashboard:
  websocket_url: "ws://192.168.178.152:8090/ws"
```

---

## 🧪 Testing

### Test 1: Slack Integration

1. Open Slack
2. Go to the channel where Aria is installed
3. Send message:
   ```
   @Aria hello
   ```

**Expected:** Aria responds with a greeting

### Test 2: Simple Project (No Clarifications)

Send in Slack:
```
@Aria Erstelle eine einfache Hello World API mit FastAPI und SQLite
```

**Expected:**
- ✅ Aria starts working immediately
- ❌ NO clarification questions asked
- ✅ Team members start discussing the project
- ✅ Project completes successfully

**Watch logs in real-time:**
```bash
sudo journalctl -u aria-ceo.service -f
```

### Test 3: Dashboard Updates

1. Open dashboard in browser:
   ```
   http://192.168.178.152:8090
   ```

2. Open browser console (F12)

3. Send a project request in Slack (see Test 2)

4. Watch the dashboard

**Expected:**
- ✅ Dashboard shows "Project Started"
- ✅ Chat messages appear in real-time
- ✅ Each agent's messages are displayed
- ✅ Browser console shows WebSocket messages like:
  ```json
  {
    "type": "project_start",
    "timestamp": "2025-10-19T10:35:00",
    "data": { "project_id": "project-20251019-103500", ... }
  }
  {
    "type": "chat_message",
    "timestamp": "2025-10-19T10:35:15",
    "data": { "agent": "Sam", "content": "I'll create the FastAPI backend...", ... }
  }
  ```

### Test 4: LLM Monitoring

Check dashboard LLM status section:

**Expected:**
- ✅ Mac Mini (192.168.178.159): Online
- ✅ GMKtec (192.168.178.155): Online (if available)

### Test 5: GitHub Integration

After a project completes, check if it was pushed to GitHub:

```bash
# Check logs for GitHub push
sudo journalctl -u aria-ceo.service | grep -i github
```

**Expected:**
```
GitHub repository created: https://github.com/[username]/project-20251019-103500
```

### Test 6: Docker Hub Integration

After a project completes, check if image was pushed:

```bash
# Check logs for Docker Hub push
sudo journalctl -u aria-ceo.service | grep -i docker
```

**Expected:**
```
Docker image pushed: [username]/project-20251019-103500:latest
```

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
     websocket_url: "ws://192.168.178.152:8090/ws"
   ```

2. Check dashboard service:
   ```bash
   sudo systemctl status aria-dashboard.service
   ```

3. Test WebSocket connection:
   ```bash
   curl -i -N -H "Connection: Upgrade" -H "Upgrade: websocket" \
        -H "Sec-WebSocket-Version: 13" -H "Sec-WebSocket-Key: test" \
        http://192.168.178.152:8090/ws
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
   Should show "6.1-bugfix-edition"

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

### Manual Rollback (Specific Backup)

```bash
# List all backups
ls -lh /opt/aria-system/backups/

# Choose a specific backup
BACKUP_DIR="20251019-103000"  # Replace with your backup

# Stop service
sudo systemctl stop aria-ceo.service

# Restore
sudo cp /opt/aria-system/backups/$BACKUP_DIR/aria_ceo.py.backup \
       /opt/aria-system/agents/aria_ceo.py

# Start service
sudo systemctl start aria-ceo.service

# Verify
sudo systemctl status aria-ceo.service
```

---

## 📊 Success Indicators

After installation, you should see:

| Check | Command | Expected Result |
|-------|---------|-----------------|
| Service running | `sudo systemctl status aria-ceo.service` | "active (running)" |
| Correct version | `grep "version = " /opt/aria-system/agents/aria_ceo.py` | "6.1-bugfix-edition" |
| No errors | `sudo journalctl -u aria-ceo.service -n 50` | No error messages |
| Clarifications disabled | `grep "BUGFIX #1" /opt/aria-system/agents/aria_ceo.py` | Found |
| Broadcasts enabled | `grep "BUGFIX #2" /opt/aria-system/agents/aria_ceo.py` | Found |
| Config updated | `grep "dashboard:" /opt/aria-system/config/config.yaml` | Found |
| Slack responds | `@Aria hello` in Slack | Aria responds |
| Dashboard accessible | Open http://192.168.178.152:8090 | Dashboard loads |

---

## 🎯 Next Steps

After successful installation:

1. **Test thoroughly** - Run several test projects to ensure everything works

2. **Monitor for 24 hours** - Watch logs for any unexpected behavior:
   ```bash
   sudo journalctl -u aria-ceo.service -f
   ```

3. **Document any issues** - If you encounter problems, note them down

4. **Clean up** - Remove the installation files:
   ```bash
   cd ~
   rm -rf aria_bugfix_v7/
   rm aria_bugfix_v7.tar.gz
   ```

5. **Update documentation** - If you made any changes, document them

---

## 📞 Support Commands

### View Logs
```bash
# Live logs
sudo journalctl -u aria-ceo.service -f

# Last 100 lines
sudo journalctl -u aria-ceo.service -n 100 --no-pager

# Since specific time
sudo journalctl -u aria-ceo.service --since "1 hour ago"

# Errors only
sudo journalctl -u aria-ceo.service -p err
```

### Service Management
```bash
# Status
sudo systemctl status aria-ceo.service

# Start
sudo systemctl start aria-ceo.service

# Stop
sudo systemctl stop aria-ceo.service

# Restart
sudo systemctl restart aria-ceo.service

# Enable (start on boot)
sudo systemctl enable aria-ceo.service

# Disable (don't start on boot)
sudo systemctl disable aria-ceo.service
```

### File Locations
```bash
# Main agent file
/opt/aria-system/agents/aria_ceo.py

# Configuration
/opt/aria-system/config/config.yaml

# Service file
/etc/systemd/system/aria-ceo.service

# Backups
/opt/aria-system/backups/

# Projects
/opt/aria-system/projects/

# Logs
journalctl -u aria-ceo.service
```

---

## 🎓 Additional Resources

- **README.md** - Overview and quick start
- **QUICK_REFERENCE.md** - Quick commands and troubleshooting
- **BUGFIX_DOCUMENTATION.md** - Detailed technical documentation

---

## ✅ Installation Complete!

If you've reached this point and all tests pass, congratulations! 🎉

Your Aria CEO system is now running version 6.1 with:
- ✅ No more endless clarification loops
- ✅ Real-time dashboard broadcasts
- ✅ All features fully functional

**Enjoy your improved Aria CEO system!**

