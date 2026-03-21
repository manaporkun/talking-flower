#!/usr/bin/env bash
# Start the Talking Flower voice assistant
# Optionally starts PicoClaw gateway first if not already running
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
PICOCLAW_BIN="${PICOCLAW_BIN:-/home/plue/picoclaw}"

# Start gateway if not running
if ! pgrep -f "picoclaw gateway" > /dev/null 2>&1; then
    echo "Starting PicoClaw gateway..."
    nohup "$PICOCLAW_BIN" gateway > /tmp/picoclaw-gw.log 2>&1 &
    sleep 2
    echo "Gateway started (PID: $(pgrep -f 'picoclaw gateway'))"
else
    echo "PicoClaw gateway already running."
fi

# Start voice assistant
cd "$PROJECT_DIR/voice-assistant"
exec .venv/bin/python3 voice_assistant.py
