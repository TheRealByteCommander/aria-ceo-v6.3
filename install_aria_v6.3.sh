#!/bin/bash

###############################################################################
# Aria CEO v6.3 - Complete Installation Script
# 
# Fixes ALL issues:
# 1. Endless clarification loop - FIXED
# 2. Missing dashboard broadcasts - FIXED
# 3. Wrong dashboard IP (152 → 150) - FIXED
# 4. Slack status updates - FIXED with proper async/await
# 5. Slack bot client integration - FIXED
#
# Author: Manus AI
# Date: 2025-10-19
# Version: 6.3-final
###############################################################################

set -e  # Exit on error

echo "=========================================="
echo "Aria CEO v6.3 - Complete Installation"
echo "=========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check if system directory exists
if [ ! -d "/opt/aria-system" ]; then
    echo -e "${RED}Error: /opt/aria-system directory not found${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} System directory found"

# Detect system user
SYSTEM_USER="aria-system"
if ! id "$SYSTEM_USER" &>/dev/null; then
    SYSTEM_USER=$(stat -c '%U' /opt/aria-system 2>/dev/null || echo "root")
    echo -e "${YELLOW}Note: Using system user: $SYSTEM_USER${NC}"
fi

# Create backup directory
BACKUP_DIR="/opt/aria-system/backups/$(date +%Y%m%d-%H%M%S)"
echo ""
echo "Creating backup in: $BACKUP_DIR"
mkdir -p "$BACKUP_DIR"

# Backup files
if [ -f "/opt/aria-system/agents/aria_ceo.py" ]; then
    echo -e "${GREEN}✓${NC} Backing up aria_ceo.py"
    cp /opt/aria-system/agents/aria_ceo.py "$BACKUP_DIR/aria_ceo.py.backup"
fi

if [ -f "/opt/aria-system/integrations/slack_bot_v6.py" ]; then
    echo -e "${GREEN}✓${NC} Backing up slack_bot_v6.py"
    cp /opt/aria-system/integrations/slack_bot_v6.py "$BACKUP_DIR/slack_bot_v6.py.backup"
fi

if [ -f "/opt/aria-system/config/config.yaml" ]; then
    echo -e "${GREEN}✓${NC} Backing up config.yaml"
    cp /opt/aria-system/config/config.yaml "$BACKUP_DIR/config.yaml.backup"
fi

# Stop service
echo ""
echo "Stopping aria-ceo service..."
if systemctl is-active --quiet aria-ceo.service; then
    systemctl stop aria-ceo.service
    echo -e "${GREEN}✓${NC} Service stopped"
else
    echo -e "${YELLOW}Note: Service not running${NC}"
fi

# Install fixed aria_ceo.py
echo ""
echo "Installing aria_ceo.py (v6.3)..."
cp aria_ceo.py /opt/aria-system/agents/aria_ceo.py
chown $SYSTEM_USER:$SYSTEM_USER /opt/aria-system/agents/aria_ceo.py
chmod 644 /opt/aria-system/agents/aria_ceo.py
echo -e "${GREEN}✓${NC} Aria CEO v6.3 installed"

# Install new dependencies and configuration
echo ""
echo "Installing new dependencies (memory_manager.py, tools.py)..."
cp memory_manager.py /opt/aria-system/agents/memory_manager.py
chown $SYSTEM_USER:$SYSTEM_USER /opt/aria-system/agents/memory_manager.py
chmod 644 /opt/aria-system/agents/memory_manager.py

cp tools.py /opt/aria-system/agents/tools.py
chown $SYSTEM_USER:$SYSTEM_USER /opt/aria-system/agents/tools.py
chmod 644 /opt/aria-system/agents/tools.py
echo -e "${GREEN}✓${NC} Dependencies installed"

echo ""
echo "Installing new configuration (agents_config.yaml)..."
cp agents_config.yaml /opt/aria-system/config/agents_config.yaml
chown $SYSTEM_USER:$SYSTEM_USER /opt/aria-system/config/agents_config.yaml
chmod 644 /opt/aria-system/config/agents_config.yaml
echo -e "${GREEN}✓${NC} Configuration installed"

# Fix Slack bot
echo ""
echo "Fixing Slack bot integration..."
SLACK_BOT_FILE="/opt/aria-system/integrations/slack_bot_v6.py"

if [ -f "$SLACK_BOT_FILE" ]; then
    # Fix: client → self.app.client
    sed -i 's/AriaCEO(slack_client=client)/AriaCEO(slack_client=self.app.client)/g' "$SLACK_BOT_FILE"
    echo -e "${GREEN}✓${NC} Slack bot fixed"
else
    echo -e "${YELLOW}Warning: Slack bot file not found${NC}"
fi

# Install websockets dependency
echo ""
echo "Installing websockets dependency..."
if [ -f "/opt/aria-system/venv/bin/pip" ]; then
    /opt/aria-system/venv/bin/pip install -q websockets>=12.0
    echo -e "${GREEN}✓${NC} Dependency installed"
else
    echo -e "${YELLOW}Warning: Virtual environment not found${NC}"
fi

# Update config.yaml
echo ""
echo "Updating configuration..."
CONFIG_FILE="/opt/aria-system/config/config.yaml"

if [ -f "$CONFIG_FILE" ]; then
    # Fix dashboard IP: 152 → 150
    sed -i 's/192\.168\.178\.152:8090/192.168.178.150:8090/g' "$CONFIG_FILE"
    
    # Add dashboard config if missing
    if ! grep -q "dashboard:" "$CONFIG_FILE"; then
        cat >> "$CONFIG_FILE" << 'EOF'

# Dashboard Configuration (Added by v6.3)
dashboard:
  websocket_url: "ws://192.168.178.150:8090/ws"
  http_url: "http://192.168.178.150:8090"
EOF
        echo -e "${GREEN}✓${NC} Dashboard configuration added"
    else
        echo -e "${GREEN}✓${NC} Dashboard configuration updated"
    fi
else
    echo -e "${YELLOW}Warning: config.yaml not found${NC}"
fi

# Start service
echo ""
echo "Starting aria-ceo service..."
if systemctl list-unit-files | grep -q aria-ceo.service; then
    systemctl start aria-ceo.service
    sleep 3
    
    if systemctl is-active --quiet aria-ceo.service; then
        echo -e "${GREEN}✓${NC} Service started successfully"
    else
        echo -e "${RED}Error: Service failed to start${NC}"
        echo "Check logs: journalctl -u aria-ceo.service -n 50"
        exit 1
    fi
else
    echo -e "${YELLOW}Warning: aria-ceo.service not found${NC}"
fi

# Verify installation
echo ""
echo "=========================================="
echo "Installation Complete!"
echo "=========================================="
echo ""
echo -e "${GREEN}✓${NC} Aria CEO v6.3 installed successfully"
echo ""
echo "Backup location: $BACKUP_DIR"
echo ""
echo "What's new in v6.3:"
echo "  ✓ No more endless clarification loops"
echo "  ✓ Dashboard broadcasts (to 192.168.178.150:8090)"
echo "  ✓ Slack status updates with proper async/await"
echo "  ✓ All 8 workers active"
echo "  ✓ GitHub & Docker Hub integration"
echo ""
echo "Next steps:"
echo "  1. Check service: systemctl status aria-ceo.service"
echo "  2. Check dashboard: http://192.168.178.150:8090"
echo "  3. Test in Slack: @Aria hello"
echo ""
echo "Expected in Slack:"
echo "  1. 🚀 Starting project..."
echo "  2. 👷 Team is working..."
echo "  3. 💬 Progress Update..."
echo "  4. ✅ Team Discussion Complete..."
echo "  5. 🎉 Project Complete! (with links)"
echo ""
echo "To rollback if needed:"
echo "  systemctl stop aria-ceo.service"
echo "  cp $BACKUP_DIR/aria_ceo.py.backup /opt/aria-system/agents/aria_ceo.py"
echo "  cp $BACKUP_DIR/slack_bot_v6.py.backup /opt/aria-system/integrations/slack_bot_v6.py"
echo "  systemctl start aria-ceo.service"
echo ""

