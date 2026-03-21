#!/usr/bin/env bash
# Talking Flower — setup script for Raspberry Pi Zero 2 WH
set -e

echo "=== Talking Flower Setup ==="

# Install system dependencies
echo "[1/4] Installing system packages..."
sudo apt-get update -qq
sudo apt-get install -y -qq python3 python3-venv python3-pip \
    portaudio19-dev libsndfile1 ffmpeg mpg123 alsa-utils

# Create venv and install Python deps
echo "[2/4] Setting up Python environment..."
cd "$(dirname "$0")/../voice-assistant"
python3 -m venv .venv
.venv/bin/pip install -q -r requirements.txt

# Copy .env if not present
echo "[3/4] Checking config..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "  Created .env from template — edit it with your API keys!"
else
    echo "  .env already exists, skipping."
fi

# Check audio devices
echo "[4/4] Checking audio devices..."
echo "  Playback devices:"
aplay -l 2>/dev/null | grep "^card" || echo "  (none found)"
echo "  Capture devices:"
arecord -l 2>/dev/null | grep "^card" || echo "  (none found)"

echo ""
echo "=== Setup complete! ==="
echo "Next steps:"
echo "  1. Edit voice-assistant/.env with your API keys"
echo "  2. Install PicoClaw: https://github.com/sipeed/picoclaw"
echo "  3. Run: cd voice-assistant && .venv/bin/python3 voice_assistant.py"
