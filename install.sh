#!/bin/bash
# install.sh - Installer for Founder Note Toolkit (FNT)
# Verifies Python, FFmpeg, and sets up virtualenv with dependencies.

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}===============================================${NC}"
echo -e "${BLUE}     Founder Note Toolkit (FNT) Installer     ${NC}"
echo -e "${BLUE}===============================================${NC}"

# 1. Verify Python Version (>= 3.12)
echo -e "\n🔍 Checking Python version..."
if command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
elif command -v python &>/dev/null; then
    PYTHON_CMD="python"
else
    echo -e "${RED}Error: Python is not installed. Please install Python 3.12+ and try again.${NC}"
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$MAJOR" -lt 3 ] || { [ "$MAJOR" -eq 3 ] && [ "$MINOR" -lt 12 ]; }; then
    echo -e "${RED}Error: FNT requires Python 3.12 or newer. Detected version: $PYTHON_VERSION${NC}"
    exit 1
else
    echo -e "${GREEN}✓ Python version $PYTHON_VERSION detected.${NC}"
fi

# 2. Verify FFmpeg
echo -e "\n🔍 Checking FFmpeg installation..."
if command -v ffmpeg &>/dev/null && command -v ffprobe &>/dev/null; then
    FFMPEG_VER=$(ffmpeg -version | head -n1)
    echo -e "${GREEN}✓ FFmpeg detected: $FFMPEG_VER${NC}"
else
    echo -e "${YELLOW}Warning: FFmpeg or FFprobe was not found in your PATH.${NC}"
    echo -e "FNT requires FFmpeg to convert AV1 streams, burn captions, and extract codecs."
    echo -e "Please install FFmpeg (e.g., 'brew install ffmpeg' or 'sudo apt install ffmpeg') to utilize these features."
fi

# 3. Create/Use Virtual Environment
echo -e "\n📦 Setting up virtual environment..."
VENV_DIR=".venv"
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment in $VENV_DIR..."
    $PYTHON_CMD -m venv "$VENV_DIR"
fi

# Activate virtualenv
source "$VENV_DIR/bin/activate"
echo -e "${GREEN}✓ Activated virtual environment.${NC}"

# 4. Install Dependencies
echo -e "\n⚙️ Updating packaging tools and dependencies..."
pip install --upgrade pip setuptools wheel
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo -e "${GREEN}✓ Dependencies installed from requirements.txt.${NC}"
else
    echo -e "${YELLOW}Warning: requirements.txt not found. Installing from setup config...${NC}"
fi

# 5. Install package in editable mode
echo -e "\n🚀 Installing FNT CLI..."
pip install -e .
echo -e "${GREEN}✓ FNT installed in editable mode.${NC}"

# 6. Verify CLI Installation
if command -v fnt &>/dev/null; then
    echo -e "${GREEN}✓ CLI command 'fnt' is active!${NC}"
else
    # Link local installation
    echo -e "${YELLOW}Notice: 'fnt' command not directly in PATH.${NC}"
    echo -e "You can run FNT by activating the virtualenv first:"
    echo -e "  source .venv/bin/activate && fnt --help"
    echo -e "Or alias it directly:"
    echo -e "  alias fnt='$(pwd)/.venv/bin/fnt'"
fi

echo -e "\n${GREEN}===============================================${NC}"
echo -e "${GREEN}      Installation Completed Successfully!      ${NC}"
echo -e "${GREEN}===============================================${NC}"
echo -e "Run 'fnt --help' or activate the venv to get started."
