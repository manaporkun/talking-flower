#!/usr/bin/env bash
# Cleanup script — rotate logs, clean old sessions and temp audio files
# Run via cron: 0 4 * * * /home/plue/talking-flower/scripts/cleanup.sh

WORKSPACE="/home/plue/.picoclaw/workspace"
VOICE_DIR="$WORKSPACE/voice-assistant"
LOG="/tmp/talking-flower-cleanup.log"

echo "$(date): Running cleanup..." >> "$LOG"

# Clean temp audio files
find "$VOICE_DIR" -name "response_*.mp3" -mmin +60 -delete 2>/dev/null
find "$VOICE_DIR" -name "speak_tmp.mp3" -mmin +60 -delete 2>/dev/null
find "$VOICE_DIR" -name "*.wav" -mmin +60 -delete 2>/dev/null

# Rotate gateway log if over 10MB
GW_LOG="/tmp/picoclaw-gw.log"
if [ -f "$GW_LOG" ] && [ "$(stat -f%z "$GW_LOG" 2>/dev/null || stat -c%s "$GW_LOG" 2>/dev/null)" -gt 10485760 ]; then
    mv "$GW_LOG" "${GW_LOG}.old"
    echo "$(date): Rotated gateway log." >> "$LOG"
fi

# Clean old voice sessions (keep last 5)
SESSION_DIR="$WORKSPACE/sessions"
if [ -d "$SESSION_DIR" ]; then
    ls -t "$SESSION_DIR"/voice*.jsonl 2>/dev/null | tail -n +6 | while read f; do
        rm -f "$f" "${f%.jsonl}.meta.json"
        echo "$(date): Cleaned old session: $f" >> "$LOG"
    done
fi

echo "$(date): Cleanup done." >> "$LOG"
