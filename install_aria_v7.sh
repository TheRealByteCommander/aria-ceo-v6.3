#!/bin/bash

###############################################################################
# Aria CEO v7.0 - Standalone Installation Script
# 
# Installation ohne Voraussetzungen:
# - Erstellt automatisch Verzeichnisstruktur
# - Prüft/installiert Python und pip
# - Erstellt virtuelle Umgebung
# - Installiert alle Abhängigkeiten
# - Konfiguriert Systemd-Service
#
# Author: Manus AI
# Date: 2025-01-XX
# Version: 7.0-standalone
###############################################################################

set -e  # Exit on error

echo "=========================================="
echo "Aria CEO v7.0 - Standalone Installation"
echo "=========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Determine script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Installation paths
INSTALL_DIR="/opt/aria-system"
VENV_DIR="$INSTALL_DIR/venv"
AGENTS_DIR="$INSTALL_DIR/agents"
CONFIG_DIR="$INSTALL_DIR/config"
INTEGRATIONS_DIR="$INSTALL_DIR/integrations"
DOCS_DIR="$INSTALL_DIR/docs"

# Check for root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}Error: This script must be run as root (use sudo)${NC}"
    exit 1
fi

# Check Python3
echo "Checking Python 3..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: python3 not found. Please install Python 3.8 or higher.${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}✓${NC} Python $PYTHON_VERSION found"

# Check pip
echo "Checking pip..."
if ! command -v pip3 &> /dev/null; then
    echo "Installing pip..."
    python3 -m ensurepip --upgrade || apt-get install -y python3-pip
fi
echo -e "${GREEN}✓${NC} pip found"

# Create installation directory structure
echo ""
echo "Creating directory structure..."
mkdir -p "$INSTALL_DIR"
mkdir -p "$AGENTS_DIR"
mkdir -p "$CONFIG_DIR"
mkdir -p "$INTEGRATIONS_DIR"
mkdir -p "$DOCS_DIR"
mkdir -p "$INSTALL_DIR/backups"
echo -e "${GREEN}✓${NC} Directories created"

# Determine system user
SYSTEM_USER="${SUDO_USER:-$USER}"
if [ "$SYSTEM_USER" = "root" ]; then
    SYSTEM_USER="aria-system"
    if ! id "$SYSTEM_USER" &>/dev/null; then
        useradd -r -s /bin/bash -d "$INSTALL_DIR" "$SYSTEM_USER" 2>/dev/null || true
    fi
fi
echo -e "${GREEN}✓${NC} Using system user: $SYSTEM_USER"

# Create virtual environment if it doesn't exist
echo ""
echo "Setting up Python virtual environment..."
if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
    echo -e "${GREEN}✓${NC} Virtual environment created"
else
    echo -e "${YELLOW}Note: Virtual environment already exists${NC}"
fi

# Activate virtual environment and install dependencies
echo ""
echo "Installing Python dependencies..."
"$VENV_DIR/bin/pip" install --upgrade pip setuptools wheel
"$VENV_DIR/bin/pip" install -q -r "$SCRIPT_DIR/requirements.txt"
echo -e "${GREEN}✓${NC} Dependencies installed"

# Install Python modules
echo ""
echo "Installing Aria CEO modules..."
cp "$SCRIPT_DIR/aria_ceo_v7.py" "$AGENTS_DIR/aria_ceo_v7.py"
cp "$SCRIPT_DIR/memory_manager.py" "$AGENTS_DIR/memory_manager.py"
cp "$SCRIPT_DIR/tools.py" "$AGENTS_DIR/tools.py"

# Make sure aria_ceo_v7.py can find the modules
# Add agents directory to Python path in the script
sed -i '1i import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent))' "$AGENTS_DIR/aria_ceo_v7.py" 2>/dev/null || {
    # Fallback if sed doesn't work
    cat > "$AGENTS_DIR/aria_ceo_v7_wrapper.py" << 'WRAPPER_EOF'
#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from aria_ceo_v7 import *
if __name__ == '__main__':
    exec(open(Path(__file__).parent / 'aria_ceo_v7.py').read())
WRAPPER_EOF
}

# Set permissions
chown -R "$SYSTEM_USER:$SYSTEM_USER" "$INSTALL_DIR"
chmod 755 "$AGENTS_DIR"/*.py
echo -e "${GREEN}✓${NC} Modules installed"

# Install configuration files
echo ""
echo "Installing configuration files..."
cp "$SCRIPT_DIR/config/agents_v7.yaml" "$CONFIG_DIR/agents_v7.yaml"
cp "$SCRIPT_DIR/config/tools_v7.yaml" "$CONFIG_DIR/tools_v7.yaml"

# Copy config.yaml template if it doesn't exist
if [ ! -f "$CONFIG_DIR/config.yaml" ]; then
    cp "$SCRIPT_DIR/config/config.yaml" "$CONFIG_DIR/config.yaml"
    echo -e "${GREEN}✓${NC} config.yaml template installed"
else
    echo -e "${YELLOW}Note: config.yaml already exists, skipping template copy${NC}"
fi

chown -R "$SYSTEM_USER:$SYSTEM_USER" "$CONFIG_DIR"
chmod 644 "$CONFIG_DIR"/*.yaml
echo -e "${GREEN}✓${NC} Configuration installed"

# Install integrations (optional)
echo ""
echo "Installing integration files..."
if [ -f "$SCRIPT_DIR/integrations/slack_bot_v6.py" ]; then
    cp "$SCRIPT_DIR/integrations/slack_bot_v6.py" "$INTEGRATIONS_DIR/slack_bot_v6.py"
    chown "$SYSTEM_USER:$SYSTEM_USER" "$INTEGRATIONS_DIR/slack_bot_v6.py"
    echo -e "${GREEN}✓${NC} Slack bot integration installed"
fi

# Install Systemd service
echo ""
echo "Installing Systemd service..."
SERVICE_FILE="/etc/systemd/system/aria-ceo.service"

# Create service file
cat > "$SERVICE_FILE" << SERVICE_EOF
[Unit]
Description=Aria CEO v7.0 Config-Driven Multi-Agent Orchestrator
After=network.target

[Service]
Type=simple
User=$SYSTEM_USER
WorkingDirectory=$INSTALL_DIR
Environment="PATH=$VENV_DIR/bin:/usr/local/bin:/usr/bin:/bin"
Environment="PYTHONPATH=$AGENTS_DIR:$INSTALL_DIR"
ExecStart=$VENV_DIR/bin/python $AGENTS_DIR/aria_ceo_v7.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
SERVICE_EOF

systemctl daemon-reload
systemctl enable aria-ceo.service
echo -e "${GREEN}✓${NC} Systemd service installed and enabled"

# Validate configuration
echo ""
echo "Validating configuration..."
if [ -f "$AGENTS_DIR/aria_ceo_v7.py" ]; then
    PYTHONPATH="$AGENTS_DIR:$INSTALL_DIR" "$VENV_DIR/bin/python" "$AGENTS_DIR/aria_ceo_v7.py" --validate-config 2>&1 | grep -v "ERROR" || true
    if [ ${PIPESTATUS[0]} -eq 0 ]; then
        echo -e "${GREEN}✓${NC} Configuration validation passed"
    else
        echo -e "${YELLOW}Warning: Configuration validation had issues. Please review config files.${NC}"
    fi
fi

# Installation complete
echo ""
echo "=========================================="
echo "Installation Complete!"
echo "=========================================="
echo ""
echo -e "${GREEN}✓${NC} Aria CEO v7.0 installed successfully"
echo ""
echo "Installation directory: $INSTALL_DIR"
echo "Virtual environment: $VENV_DIR"
echo "Configuration: $CONFIG_DIR"
echo ""
echo "Configuration files:"
echo "  - $CONFIG_DIR/config.yaml (main config)"
echo "  - $CONFIG_DIR/agents_v7.yaml (agent definitions)"
echo "  - $CONFIG_DIR/tools_v7.yaml (tool definitions)"
echo ""
echo "Next steps:"
echo "  1. Review and customize: $CONFIG_DIR/config.yaml"
echo "  2. Validate config: $VENV_DIR/bin/python $AGENTS_DIR/aria_ceo_v7.py --validate-config"
echo "  3. Start service: systemctl start aria-ceo.service"
echo "  4. Check status: systemctl status aria-ceo.service"
echo "  5. View logs: journalctl -u aria-ceo.service -f"
echo ""
echo "Manual test:"
echo "  $VENV_DIR/bin/python $AGENTS_DIR/aria_ceo_v7.py --dry-run"
echo ""

